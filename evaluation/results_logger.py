"""Write per-case and aggregate metric files to results/ folder.

Outputs:
  results/{name}.metrics.json   -- all raw values for one test case
  results/aggregate.json        -- micro-averaged KPIs across all cases
"""

import json
import time
from pathlib import Path
from typing import Optional


def _safe(value):
    """Convert non-JSON-serialisable values to None."""
    if isinstance(value, float) and (value != value):  # NaN guard
        return None
    return value


def write_case_metrics(metrics: dict, results_dir: Path) -> None:
    """Persist one test case's raw metric dict to results/{name}.metrics.json."""
    results_dir.mkdir(parents=True, exist_ok=True)
    out = {k: _safe(v) for k, v in metrics.items()}
    path = results_dir / f"{metrics['name']}.metrics.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")


def write_aggregate(results: list[dict], results_dir: Path) -> None:
    """Compute and persist aggregate.json from all completed cases."""
    results_dir.mkdir(parents=True, exist_ok=True)

    successful = [r for r in results if not r.get("error")]
    audio_cases = [r for r in successful if r.get("scenario") in ("audio_only", "both")]

    # --- ASR / speed ---
    total_dur = sum(r.get("duration", 0) for r in audio_cases)
    total_tx = sum(r.get("transcribe_time", 0) for r in audio_cases)
    avg_rtf = (total_tx / total_dur) if total_dur > 0 else None

    wer_vals = [r["wer"] for r in audio_cases if r.get("wer") is not None]
    avg_wer = (sum(wer_vals) / len(wer_vals)) if wer_vals else None

    # Pipeline speed check: RTF * 60 <= 10 min
    speed_pass: Optional[bool] = None
    projected_10min: Optional[float] = None
    if avg_rtf is not None:
        projected_10min = round(avg_rtf * 60, 2)
        speed_pass = projected_10min <= 10.0

    # --- Task P/R/F1 micro-average ---
    tp_sum = sum(r.get("task_tp", 0) or 0 for r in successful)
    fp_sum = sum(r.get("task_fp", 0) or 0 for r in successful)
    fn_sum = sum(r.get("task_fn", 0) or 0 for r in successful)
    total_gen = tp_sum + fp_sum
    total_gt = tp_sum + fn_sum

    micro_p = (tp_sum / total_gen) if total_gen > 0 else None
    micro_r = (tp_sum / total_gt) if total_gt > 0 else None
    if micro_p is not None and micro_r is not None:
        denom = micro_p + micro_r
        micro_f1 = (2 * micro_p * micro_r / denom) if denom > 0 else 0.0
    else:
        micro_f1 = None

    # --- Assignment / slide-attr / KP coverage ---
    def _avg_optional(key: str) -> Optional[float]:
        vals = [r[key] for r in successful if r.get(key) is not None]
        return (sum(vals) / len(vals)) if vals else None

    avg_assign = _avg_optional("assignment_accuracy")
    avg_slide_attr = _avg_optional("slide_attr_accuracy")
    avg_kp = _avg_optional("summary_kp_coverage")
    avg_slide_cov = _avg_optional("slide_extract_coverage")

    # --- LLM judge averages (skip None) ---
    def _avg_judge(key: str) -> Optional[float]:
        vals = []
        for r in successful:
            js = r.get("judge_scores") or {}
            crit = js.get(key)
            if crit and crit.get("score") is not None:
                vals.append(crit["score"])
        return (sum(vals) / len(vals)) if vals else None

    # --- Per-scenario counts ---
    by_scenario: dict[str, int] = {}
    for r in results:
        s = r.get("scenario", "unknown")
        by_scenario[s] = by_scenario.get(s, 0) + 1

    aggregate = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_cases": len(results),
        "successful_cases": len(successful),
        "success_rate": len(successful) / len(results) if results else 0.0,
        "by_scenario": by_scenario,
        "asr": {
            "avg_rtf": avg_rtf,
            "avg_wer": avg_wer,
            "projected_60min_pipeline_minutes": projected_10min,
            "speed_target_pass": speed_pass,
        },
        "slide": {
            "avg_extract_coverage": avg_slide_cov,
        },
        "task_quantitative": {
            "micro_precision": micro_p,
            "micro_recall": micro_r,
            "micro_f1": micro_f1,
            "avg_assignment_accuracy": avg_assign,
            "avg_slide_attr_accuracy": avg_slide_attr,
        },
        "summary_quantitative": {
            "avg_kp_coverage": avg_kp,
        },
        "llm_judge": {
            "avg_summary_completeness": _avg_judge("summary_completeness"),
            "avg_summary_accuracy": _avg_judge("summary_accuracy"),
            "avg_task_completeness": _avg_judge("task_completeness"),
            "avg_task_assignment_accuracy": _avg_judge("task_assignment_accuracy"),
            "avg_task_quote_accuracy": _avg_judge("task_quote_accuracy"),
        },
    }

    path = results_dir / "aggregate.json"
    path.write_text(json.dumps(aggregate, indent=2, ensure_ascii=False), encoding="utf-8")
