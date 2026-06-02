"""MeetMind Evaluation Harness — CLI entry point.

Usage (run from backend/ so .env is loaded):
    python ../evaluation/run_eval.py              # all files in input folders
    python ../evaluation/run_eval.py --file lec1  # single case by stem

Input folders (relative to evaluation/):
    audios/                   *.mp3, *.mp4 (audio-only)
    slides/                   *.pdf
    transcripts_ground_truth/ *.txt  (optional, enables WER)
    ground_truth_analysis/    *.json (optional, enables P/R/F1)

Output (evaluation/results/):
    {name}.metrics.json    per-case raw metrics
    aggregate.json         averaged KPIs
    evaluation_report.md   Vietnamese human-readable report
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap: must happen before any backend imports
# ---------------------------------------------------------------------------
_eval_dir = Path(__file__).resolve().parent
_backend_dir = _eval_dir.parent / "backend"
sys.path.insert(0, str(_backend_dir))
os.chdir(_backend_dir)

from app.core.config import settings  # noqa: E402

if not settings.GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not set in backend/.env")
    sys.exit(1)

from app.workers.transcribe import _get_model          # noqa: E402
from app.workers.slides import extract_slides, pages_as_prompt  # noqa: E402
from app.workers.analyze import analyze_meeting         # noqa: E402

from case_discovery import discover_cases, Scenario    # noqa: E402
from metrics_asr import calculate_wer                  # noqa: E402
from metrics_quantitative import (                     # noqa: E402
    flatten_tasks, match_tasks, task_prf,
    assignment_accuracy, slide_attr_accuracy,
    slide_extract_coverage,
)
from llm_judge import evaluate_analysis_with_llm, evaluate_summary_kp_coverage  # noqa: E402
from results_logger import write_case_metrics, write_aggregate  # noqa: E402
from report_writer import write_report                 # noqa: E402


# ---------------------------------------------------------------------------
# Ground-truth loader
# ---------------------------------------------------------------------------

def _load_gt_analysis(path) -> dict | None:
    """Load ground-truth analysis JSON; return None on error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  ⚠  Could not load GT analysis {path.name}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Per-case evaluation
# ---------------------------------------------------------------------------

def _run_case(case, results_dir: Path) -> dict:
    print(f"\n▶  {case.name}  [{case.scenario.value}]")

    metrics: dict = {
        "name": case.name,
        "scenario": case.scenario.value,
        "has_gt_transcript": case.has_gt_transcript,
        "has_gt_analysis": case.has_gt_analysis,
        # timing
        "transcribe_time": 0.0, "duration": 0.0, "extract_time": 0.0,
        "analyze_time": 0.0, "pipeline_total_time": 0.0,
        # ASR
        "rtf": None, "wer": None,
        # slides
        "page_count": None, "slide_extract_coverage": None,
        # task quant
        "task_tp": None, "task_fp": None, "task_fn": None,
        "task_precision": None, "task_recall": None, "task_f1": None,
        "assignment_accuracy": None, "slide_attr_accuracy": None,
        # summary quant
        "summary_kp_coverage": None,
        # qualitative
        "judge_scores": None,
        "error": None,
    }

    try:
        # --- [1] Transcription ---
        if case.has_audio:
            print("  [1/4] Transcribing…")
            t0 = time.time()
            model = _get_model()
            segs_gen, info = model.transcribe(
                str(case.audio_path), beam_size=5, vad_filter=True
            )
            segments = [
                {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
                for s in segs_gen
            ]
            transcript = {"segments": segments, "language": info.language}
            t_tx = time.time() - t0
            metrics["transcribe_time"] = t_tx
            metrics["duration"] = info.duration
            metrics["rtf"] = t_tx / max(0.1, info.duration)
            raw_text = "\n".join(s["text"] for s in segments)
            print(f"      RTF={metrics['rtf']:.3f}  dur={info.duration/60:.1f}m  tx={t_tx:.1f}s")

            if case.has_gt_transcript:
                gt_text = case.gt_transcript_path.read_text(encoding="utf-8")
                metrics["wer"] = calculate_wer(gt_text, raw_text)
                print(f"      WER={metrics['wer']*100:.2f}%")
        else:
            print("  [1/4] Transcription: skipped (PDF-only)")
            transcript = {"segments": [], "language": "en"}
            raw_text = ""

        # --- [2] Slide extraction ---
        slides_prompt = ""
        if case.has_slides:
            print("  [2/4] Extracting slides…")
            t0 = time.time()
            slides_data = extract_slides(case.pdf_path.read_bytes())
            pages = slides_data["pages"]
            slides_prompt = pages_as_prompt(pages)
            t_ex = time.time() - t0
            metrics["extract_time"] = t_ex
            metrics["page_count"] = slides_data["page_count"]
            metrics["slide_extract_coverage"] = slide_extract_coverage(pages)
            print(f"      pages={slides_data['page_count']}  cov={metrics['slide_extract_coverage']:.0%}  t={t_ex:.1f}s")
        else:
            print("  [2/4] Slide extraction: skipped (audio-only)")

        # --- [3] Gemini analysis ---
        print("  [3/4] Analyzing with Gemini…")
        t0 = time.time()
        analysis = analyze_meeting(transcript, slides_prompt)
        t_an = time.time() - t0
        metrics["analyze_time"] = t_an
        metrics["pipeline_total_time"] = (
            metrics["transcribe_time"] + metrics["extract_time"] + t_an
        )
        print(f"      t={t_an:.1f}s")

        # --- [3b] Quantitative GT metrics ---
        if case.has_gt_analysis:
            gt = _load_gt_analysis(case.gt_analysis_path)
            if gt:
                gen_tasks = flatten_tasks(analysis)
                gt_tasks = gt.get("tasks", [])
                match = match_tasks(gen_tasks, gt_tasks)
                prf = task_prf(match["tp"], match["fp"], match["fn"])
                metrics.update({
                    "task_tp": match["tp"],
                    "task_fp": match["fp"],
                    "task_fn": match["fn"],
                    "task_precision": prf["precision"],
                    "task_recall": prf["recall"],
                    "task_f1": prf["f1"],
                    "assignment_accuracy": assignment_accuracy(
                        match["pairs"], gen_tasks, gt_tasks
                    ),
                    "slide_attr_accuracy": slide_attr_accuracy(
                        match["pairs"], gen_tasks, gt_tasks
                    ),
                })
                kps = gt.get("summary_key_points", [])
                if kps:
                    metrics["summary_kp_coverage"] = evaluate_summary_kp_coverage(
                        analysis.get("summary", ""), kps,
                        settings.GEMINI_API_KEY, settings.GEMINI_MODEL,
                    )
                print(f"      P={metrics['task_precision']}  R={metrics['task_recall']}  F1={metrics['task_f1']}")

        # --- [4] LLM judge ---
        print("  [4/4] LLM Judge…")
        metrics["judge_scores"] = evaluate_analysis_with_llm(
            raw_text, slides_prompt, analysis,
            case.scenario.value,
            settings.GEMINI_API_KEY, settings.GEMINI_MODEL,
        )
        js = metrics["judge_scores"]
        def _sc(k):
            c = js.get(k)
            return f"{c['score']}" if c and c.get("score") is not None else "N/A"
        print(
            f"      SComp={_sc('summary_completeness')}  SAcc={_sc('summary_accuracy')}  "
            f"TComp={_sc('task_completeness')}  TAssign={_sc('task_assignment_accuracy')}  "
            f"TQuote={_sc('task_quote_accuracy')}"
        )

    except Exception as exc:
        print(f"  ❌ Error: {exc}")
        metrics["error"] = str(exc)

    return metrics


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="MeetMind evaluation harness.")
    ap.add_argument("--file", help="Stem of a single test case (e.g. lec1)")
    args = ap.parse_args()

    results_dir = _eval_dir / "results"

    print("=" * 60)
    print("MEETMIND EVALUATION HARNESS")
    print("=" * 60)

    cases = discover_cases(_eval_dir, file_filter=args.file)
    if not cases:
        print("No test cases found. Drop .mp3/.mp4 into audios/ or .pdf into slides/.")
        return

    print(f"Found {len(cases)} case(s): {', '.join(c.name for c in cases)}\n")

    all_results: list[dict] = []
    for case in cases:
        metrics = _run_case(case, results_dir)
        all_results.append(metrics)
        # Write outputs after every case (live progress)
        write_case_metrics(metrics, results_dir)
        write_aggregate(all_results, results_dir)
        write_report(all_results, results_dir / "evaluation_report.md")
        print(f"  📝 results/{case.name}.metrics.json updated")

    print("\n" + "=" * 60)
    print("DONE")
    print(f"  Report:    evaluation/results/evaluation_report.md")
    print(f"  Aggregate: evaluation/results/aggregate.json")
    print("=" * 60)


if __name__ == "__main__":
    # Import local eval modules relative to evaluation/
    sys.path.insert(0, str(_eval_dir))
    main()
