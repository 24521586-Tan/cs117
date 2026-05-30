"""Transcript + slides -> structured meeting analysis via Google Gemini.

Enforces a JSON schema so the model returns summary + per-person tasks with
deadline, verbatim quote, and source slide. Prompt forbids inventing content.
"""

import json

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.core.config import settings


class Task(BaseModel):
    task: str
    deadline: str | None = None  # natural-language date/time as stated, else null
    quote: str  # verbatim sentence from the transcript that assigns this task
    slide: int | None = None  # source slide number if related to a slide, else null


class PersonTasks(BaseModel):
    person: str
    tasks: list[Task]


class MeetingAnalysis(BaseModel):
    title: str
    summary: str
    attendees: list[str]
    tasks_by_person: list[PersonTasks]


SYSTEM_INSTRUCTION = (
    "You are a meeting assistant. Analyze the meeting transcript and slide text and "
    "produce a concise summary plus the list of action items.\n"
    "STRICT RULES:\n"
    "1. Use ONLY information present in the transcript and slides. Never invent tasks, "
    "names, deadlines, or facts.\n"
    "2. Group every action item under the person it is assigned to. If the assignee is "
    "unclear, use 'Unassigned'.\n"
    "3. For each task, set 'quote' to the exact verbatim sentence from the transcript "
    "that states the task. Do not paraphrase.\n"
    "4. Set 'deadline' to the date/time exactly as mentioned (e.g. 'by Friday', 'next "
    "Monday'); use null if none was stated.\n"
    "5. Set 'slide' to the source slide number when the task references slide content, "
    "else null.\n"
    "6. Write the summary and all output in English.\n"
)


def _transcript_text(transcript: dict) -> str:
    segs = transcript.get("segments", [])
    return "\n".join(s.get("text", "") for s in segs).strip()


def analyze_meeting(transcript: dict, slides_text: str) -> dict:
    """Return MeetingAnalysis as a plain dict."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set — cannot run meeting analysis.")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = (
        f"=== MEETING TRANSCRIPT ===\n{_transcript_text(transcript)}\n\n"
        f"=== SLIDE TEXT (by slide number) ===\n{slides_text or '(no slides provided)'}"
    )

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=MeetingAnalysis,
            temperature=0.2,
        ),
    )

    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, MeetingAnalysis):
        return parsed.model_dump()
    # Fallback: schema-constrained text is still valid JSON.
    return MeetingAnalysis(**json.loads(response.text)).model_dump()
