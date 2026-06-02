"""LLM-as-a-judge evaluation using Gemini.

Scenario-aware: AUDIO_ONLY / BOTH use a 5-criteria prompt; PDF_ONLY drops
the Task Quote Accuracy criterion (no transcript to quote against).

Summary key-point coverage is also computed here via a separate LLM call
when the GT analysis file contains summary_key_points.

Requires: google-genai, pydantic (same deps as backend/requirements.txt).
Backend settings (GEMINI_API_KEY, GEMINI_MODEL) must be loaded before import.
"""

import json
from typing import Optional

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Judge schemas
# ---------------------------------------------------------------------------

class CriterionScore(BaseModel):
    score: float = Field(description="Score from 1.0 to 5.0")
    explanation: str = Field(
        description="Detailed explanation in Vietnamese of why this score was given"
    )


class EvalResult(BaseModel):
    summary_completeness: CriterionScore = Field(
        description="Recall of main topics and key decisions in the summary"
    )
    summary_accuracy: CriterionScore = Field(
        description="Factual accuracy — no hallucinations vs transcript/slides"
    )
    task_completeness: CriterionScore = Field(
        description="All action items extracted; none missing"
    )
    task_assignment_accuracy: CriterionScore = Field(
        description="Tasks assigned to the correct person"
    )
    task_quote_accuracy: Optional[CriterionScore] = Field(
        default=None,
        description="Verbatim quotes match transcript (N/A for PDF-only)"
    )
    overall_comments: str = Field(
        description="Overall quality summary and recommendations in Vietnamese"
    )


# ---------------------------------------------------------------------------
# System instructions
# ---------------------------------------------------------------------------

_JUDGE_BASE = (
    "You are an objective AI evaluator. Rate the generated meeting analysis "
    "on the following criteria from 1.0 to 5.0 (5.0 = perfect):\n"
    "1. Summary Completeness (Độ đầy đủ tóm tắt): does the summary capture all "
    "   key decisions and major topics? (1=missed everything, 5=captured all)\n"
    "2. Summary Factual Accuracy (Độ chính xác tóm tắt): any info not in the "
    "   source? (1=completely hallucinated, 5=100% accurate)\n"
    "3. Task Completeness (Độ đầy đủ giao việc): all action items extracted? "
    "   (1=missed all, 5=captured all)\n"
    "4. Task Assignment Accuracy (Độ chính xác phân vai): tasks assigned to the "
    "   correct person? (1=all wrong, 5=perfectly assigned)\n"
)

JUDGE_SYSTEM_AUDIO = (
    _JUDGE_BASE
    + "5. Task Quote Accuracy (Độ chính xác trích dẫn): do verbatim quotes match "
    "   the actual spoken words? (1=made up, 5=perfect match)\n"
    "Provide detailed justification for each score in Vietnamese."
)

JUDGE_SYSTEM_PDF_ONLY = (
    _JUDGE_BASE
    + "NOTE: This is a PDF-only case — no audio transcript was provided. "
    "Evaluate criteria 1-4 against the slide text only. "
    "Do NOT score Task Quote Accuracy (set task_quote_accuracy to null).\n"
    "Provide detailed justification for each score in Vietnamese."
)

_KP_SYSTEM = (
    "You are an objective evaluator. Given a list of expected key points and a "
    "generated meeting summary, determine which key points are covered (even if "
    "paraphrased). Return a JSON array where each element has: "
    "'key_point' (string) and 'covered' (boolean). Be strict: only mark covered "
    "if the concept is clearly present in the summary."
)


# ---------------------------------------------------------------------------
# Judge call
# ---------------------------------------------------------------------------

def evaluate_analysis_with_llm(
    transcript_text: str,
    slides_text: str,
    analysis: dict,
    scenario: str,
    api_key: str,
    model: str,
) -> dict:
    """Call Gemini to judge the generated analysis.

    Returns EvalResult as a plain dict. task_quote_accuracy.score is None
    for pdf_only scenario.
    """
    client = genai.Client(api_key=api_key)
    analysis_str = json.dumps(analysis, indent=2, ensure_ascii=False)

    if scenario == "pdf_only":
        system_instruction = JUDGE_SYSTEM_PDF_ONLY
        prompt = (
            f"=== SLIDE TEXT ===\n{slides_text or '(no slides)'}\n\n"
            f"=== GENERATED MEETING ANALYSIS ===\n{analysis_str}\n\n"
            "Evaluate the GENERATED MEETING ANALYSIS against the SLIDE TEXT."
        )
    else:
        system_instruction = JUDGE_SYSTEM_AUDIO
        prompt = (
            f"=== RAW MEETING TRANSCRIPT ===\n{transcript_text}\n\n"
            f"=== SLIDE TEXT ===\n{slides_text or '(no slides)'}\n\n"
            f"=== GENERATED MEETING ANALYSIS ===\n{analysis_str}\n\n"
            "Evaluate the GENERATED MEETING ANALYSIS against the RAW TRANSCRIPT and SLIDE TEXT."
        )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=EvalResult,
            temperature=0.1,
        ),
    )

    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, EvalResult):
        result = parsed.model_dump()
    else:
        result = EvalResult(**json.loads(response.text)).model_dump()

    # Ensure pdf_only quote score is explicitly None
    if scenario == "pdf_only" and result.get("task_quote_accuracy") is not None:
        result["task_quote_accuracy"] = None

    return result


# ---------------------------------------------------------------------------
# Summary key-point coverage (LLM-assisted)
# ---------------------------------------------------------------------------

class _KpItem(BaseModel):
    key_point: str
    covered: bool


def evaluate_summary_kp_coverage(
    summary: str,
    key_points: list[str],
    api_key: str,
    model: str,
) -> Optional[float]:
    """Return fraction of GT key_points covered in summary (0.0-1.0) or None."""
    if not key_points or not summary:
        return None

    client = genai.Client(api_key=api_key)
    kp_list = "\n".join(f"- {kp}" for kp in key_points)
    prompt = (
        f"Expected key points:\n{kp_list}\n\n"
        f"Generated summary:\n{summary}\n\n"
        "For each key point, determine if it is covered in the summary."
    )

    class _KpList(BaseModel):
        items: list[_KpItem]

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_KP_SYSTEM,
            response_mime_type="application/json",
            response_schema=_KpList,
            temperature=0.0,
        ),
    )

    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, _KpList):
        items = parsed.items
    else:
        items = _KpList(**json.loads(response.text)).items

    if not items:
        return None
    return sum(1 for it in items if it.covered) / len(items)
