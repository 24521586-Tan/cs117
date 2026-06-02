"""Generate the Vietnamese Markdown evaluation report.

Follows thay's framework (CS117-7.pdf):
  §1 Tong hop (summary table)
  §2 Dinh luong (quantitative KPIs)
  §3 Dinh tinh (qualitative LLM-judge)
  §4 Phan tich theo kich ban (per-scenario breakdown)
  §5 Chi tiet tung mau thu (per-case detail)
"""

import time
from pathlib import Path
from typing import Optional


SCENARIO_LABEL = {
    "audio_only": "🎤 Audio Only",
    "pdf_only":   "📄 PDF Only",
    "both":       "🎤+📄 Both",
}


def _fmt(v, fmt=".2f", suffix="", na="N/A") -> str:
    if v is None:
        return na
    return f"{v:{fmt}}{suffix}"


def _pct(v) -> str:
    return _fmt(v, ".1%") if v is not None else "N/A"


def _score(v) -> str:
    return _fmt(v, ".2f") if v is not None else "N/A"


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _summary_table(results: list[dict]) -> str:
    lines = [
        "## 1. Bảng Tổng Hợp (Summary Table)\n",
        "| Mẫu | Kịch bản | Audio | RTF | WER | Slide Cov | Task P/R/F1 | Assign | KP Cov | Trạng thái |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]
    for r in results:
        name = r["name"]
        scen = SCENARIO_LABEL.get(r.get("scenario", ""), r.get("scenario", "-"))
        dur = f"{r['duration']/60:.1f}m" if r.get("duration") else "-"
        rtf = _fmt(r.get("rtf"), ".3f")
        wer = _pct(r.get("wer"))
        cov = _pct(r.get("slide_extract_coverage"))
        p = _pct(r.get("task_precision"))
        rc = _pct(r.get("task_recall"))
        f1 = _pct(r.get("task_f1"))
        prf = f"{p}/{rc}/{f1}" if r.get("task_tp") is not None else "N/A"
        asgn = _pct(r.get("assignment_accuracy"))
        kp = _pct(r.get("summary_kp_coverage"))
        if r.get("error"):
            status = f"❌ {r['error'][:40]}"
        else:
            status = "✅"
        lines.append(f"| {name} | {scen} | {dur} | {rtf} | {wer} | {cov} | {prf} | {asgn} | {kp} | {status} |")
    return "\n".join(lines) + "\n"


def _quant_section(results: list[dict]) -> str:
    successful = [r for r in results if not r.get("error")]
    audio_cases = [r for r in successful if r.get("scenario") in ("audio_only", "both")]

    total_dur = sum(r.get("duration", 0) for r in audio_cases)
    total_tx = sum(r.get("transcribe_time", 0) for r in audio_cases)
    avg_rtf = (total_tx / total_dur) if total_dur > 0 else None
    projected = (avg_rtf * 60) if avg_rtf is not None else None
    speed_ok = projected is not None and projected <= 10.0
    speed_str = f"{'✅ PASS' if speed_ok else '❌ FAIL'} ({_fmt(projected, '.1f')} phút / 60 phút audio)" if projected else "N/A"

    wer_vals = [r["wer"] for r in audio_cases if r.get("wer") is not None]
    avg_wer = (sum(wer_vals) / len(wer_vals)) if wer_vals else None

    cov_vals = [r["slide_extract_coverage"] for r in successful if r.get("slide_extract_coverage") is not None]
    avg_cov = (sum(cov_vals) / len(cov_vals)) if cov_vals else None

    tp = sum(r.get("task_tp", 0) or 0 for r in successful)
    fp = sum(r.get("task_fp", 0) or 0 for r in successful)
    fn = sum(r.get("task_fn", 0) or 0 for r in successful)
    mp = (tp / (tp + fp)) if (tp + fp) > 0 else None
    mr = (tp / (tp + fn)) if (tp + fn) > 0 else None
    mf1 = (2 * mp * mr / (mp + mr)) if (mp and mr and (mp + mr) > 0) else None

    def _avg_opt(key):
        vals = [r[key] for r in successful if r.get(key) is not None]
        return (sum(vals) / len(vals)) if vals else None

    lines = [
        "## 2. Tiêu Chí Định Lượng (Quantitative Metrics)\n",
        f"- **Tỷ lệ thành công (Success Rate):** {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)" if results else "",
        "",
        "### 2.1 Nhận dạng giọng nói (ASR)",
        f"- **Avg RTF:** {_fmt(avg_rtf, '.3f')} (ví dụ: 1 phút audio mất {_fmt(avg_rtf, '.1f')} phút xử lý)" if avg_rtf else "- **Avg RTF:** N/A",
        f"- **Avg WER:** {_pct(avg_wer)} (mục tiêu ≤ 15%)",
        f"- **Tốc độ pipeline (60 phút audio):** {speed_str} (mục tiêu ≤ 10 phút)",
        "",
        "### 2.2 Trích xuất slide",
        f"- **Avg Slide Extraction Coverage:** {_pct(avg_cov)} (mục tiêu ≥ 95%)",
        "",
        "### 2.3 Trích xuất và giao việc (Task Extraction)",
        f"- **Micro-Precision:** {_pct(mp)}",
        f"- **Micro-Recall:** {_pct(mr)} (mục tiêu ≥ 80%)",
        f"- **Micro-F1:** {_pct(mf1)}",
        f"- **Avg Assignment Accuracy:** {_pct(_avg_opt('assignment_accuracy'))}",
        f"- **Avg Slide Attribution Accuracy:** {_pct(_avg_opt('slide_attr_accuracy'))}",
        "",
        "### 2.4 Tóm tắt (Summary)",
        f"- **Avg KP Coverage:** {_pct(_avg_opt('summary_kp_coverage'))}",
    ]
    return "\n".join(lines) + "\n"


def _qual_section(results: list[dict]) -> str:
    successful = [r for r in results if not r.get("error")]

    def _avg_judge(key):
        vals = []
        for r in successful:
            js = r.get("judge_scores") or {}
            crit = js.get(key)
            if crit and crit.get("score") is not None:
                vals.append(crit["score"])
        return (sum(vals) / len(vals)) if vals else None

    sc = _avg_judge("summary_completeness")
    sa = _avg_judge("summary_accuracy")
    tc = _avg_judge("task_completeness")
    ta = _avg_judge("task_assignment_accuracy")
    tq = _avg_judge("task_quote_accuracy")

    summary_agg = ((sc or 0) + (sa or 0)) / (10 if (sc and sa) else 5) if (sc or sa) else None
    task_agg = ((tc or 0) + (ta or 0) + (tq or 0)) / (15 if (tc and ta and tq) else (10 if (tc and ta) else 5)) if (tc or ta) else None

    lines = [
        "## 3. Tiêu Chí Định Tính — LLM Judge (Qualitative Metrics)\n",
        "*(Gemini đóng vai trọng tài, chấm điểm 1.0–5.0)*\n",
        f"- **Summary Completeness (Độ đầy đủ tóm tắt):** {_score(sc)} / 5.0",
        f"- **Summary Accuracy (Độ chính xác tóm tắt):** {_score(sa)} / 5.0",
        f"- **Task Completeness (Độ đầy đủ giao việc):** {_score(tc)} / 5.0",
        f"- **Task Assignment Accuracy (Đúng vai):** {_score(ta)} / 5.0",
        f"- **Task Quote Accuracy (Trích dẫn):** {_score(tq)} / 5.0 *(N/A cho PDF-only)*",
        "",
        f"- **📊 Điểm Tóm Tắt Tổng Hợp:** {_fmt(summary_agg)} / 1.00",
        f"- **📊 Điểm Giao Việc Tổng Hợp:** {_fmt(task_agg)} / 1.00",
    ]
    return "\n".join(lines) + "\n"


def _scenario_section(results: list[dict]) -> str:
    successful = [r for r in results if not r.get("error")]
    buckets: dict[str, list[dict]] = {}
    for r in successful:
        s = r.get("scenario", "unknown")
        buckets.setdefault(s, []).append(r)

    lines = ["## 4. Phân Tích Theo Kịch Bản (Per-Scenario Breakdown)\n"]
    for scen, cases in buckets.items():
        label = SCENARIO_LABEL.get(scen, scen)
        wer_vals = [r["wer"] for r in cases if r.get("wer") is not None]
        avg_wer = (sum(wer_vals) / len(wer_vals)) if wer_vals else None
        rtf_vals = [r["rtf"] for r in cases if r.get("rtf") is not None]
        avg_rtf = (sum(rtf_vals) / len(rtf_vals)) if rtf_vals else None
        f1_vals = [r["task_f1"] for r in cases if r.get("task_f1") is not None]
        avg_f1 = (sum(f1_vals) / len(f1_vals)) if f1_vals else None
        lines += [
            f"### {label} ({len(cases)} mẫu)",
            f"- Avg RTF: {_fmt(avg_rtf, '.3f')} | Avg WER: {_pct(avg_wer)} | Avg Task F1: {_pct(avg_f1)}",
            "",
        ]
    return "\n".join(lines) + "\n"


def _detail_section(results: list[dict]) -> str:
    lines = ["## 5. Chi Tiết Từng Mẫu Thử (Per-Case Detail)\n"]
    for r in results:
        if r.get("error"):
            lines += [f"### ❌ {r['name']}", f"> Lỗi: {r['error']}", "", "---", ""]
            continue

        scen = SCENARIO_LABEL.get(r.get("scenario", ""), "-")
        lines += [
            f"### {r['name']} — {scen}",
            f"- Thời lượng: {r.get('duration', 0)/60:.1f} phút | "
            f"ASR: {r.get('transcribe_time', 0):.1f}s | "
            f"Slides: {r.get('extract_time', 0):.1f}s | "
            f"Gemini: {r.get('analyze_time', 0):.1f}s",
        ]
        if r.get("wer") is not None:
            lines.append(f"- WER: {r['wer']*100:.2f}%")
        if r.get("slide_extract_coverage") is not None:
            lines.append(f"- Slide Coverage: {r['slide_extract_coverage']*100:.1f}% ({r.get('page_count','-')} trang)")

        # Quantitative task block
        if r.get("task_tp") is not None:
            lines += [
                "",
                "**📊 Định lượng (ground-truth):**",
                f"- Task Precision: {_pct(r.get('task_precision'))} | Recall: {_pct(r.get('task_recall'))} | F1: {_pct(r.get('task_f1'))}",
                f"- Assignment Accuracy: {_pct(r.get('assignment_accuracy'))}",
                f"- Slide Attribution: {_pct(r.get('slide_attr_accuracy'))}",
                f"- KP Coverage: {_pct(r.get('summary_kp_coverage'))}",
            ]
        else:
            lines.append("\n*Định lượng: N/A (không có ground-truth analysis)*")

        # LLM judge scores
        js = r.get("judge_scores") or {}
        if js:
            lines += ["", "**🤖 LLM Judge (Gemini):**"]
            for key, label in [
                ("summary_completeness", "Summary Completeness"),
                ("summary_accuracy", "Summary Accuracy"),
                ("task_completeness", "Task Completeness"),
                ("task_assignment_accuracy", "Task Assignment"),
                ("task_quote_accuracy", "Task Quote"),
            ]:
                crit = js.get(key)
                if crit is None or crit.get("score") is None:
                    lines.append(f"- **{label}:** N/A")
                else:
                    lines.append(f"- **{label}:** {crit['score']}/5 — {crit.get('explanation','')}")
            lines += ["", f"> {js.get('overall_comments', '')}"]

        lines += ["", "---", ""]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def write_report(results: list[dict], report_path: Path) -> None:
    """Write full Vietnamese evaluation report to report_path."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    parts = [
        "# Báo Cáo Đánh Giá Hiệu Năng — MeetMind (CS117)\n",
        f"*Ngày đánh giá: {time.strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Tổng mẫu: {len(results)}*\n\n",
        _summary_table(results),
        "\n",
        _quant_section(results),
        "\n",
        _qual_section(results),
        "\n",
        _scenario_section(results),
        "\n",
        _detail_section(results),
    ]
    report_path.write_text("".join(parts), encoding="utf-8")
