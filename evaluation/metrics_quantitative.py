"""Quantitative metrics for task extraction and slide coverage.

Pure math — no backend imports. Safe to run standalone.

Task Matching (token-set Jaccard, threshold tau=0.5):
    1. Normalize both task strings (lowercase, strip punctuation).
    2. Compute Jaccard similarity on token sets: |A & B| / |A | B|.
       Fallback to SequenceMatcher.ratio() for very short strings (< 4 tokens).
    3. Greedy assignment: repeatedly pick the highest-similarity pair >= tau,
       consume both. Unmatched generated = FP, unmatched GT = FN.

Task Precision / Recall / F1:
    Precision = TP / (TP + FP)   -- of tasks generated, how many are real?
    Recall    = TP / (TP + FN)   -- of GT tasks, how many were found?
    F1        = 2 * P * R / (P + R)
    Division-by-zero rules:
      - Both generated and GT empty -> all None (N/A).
      - GT empty but generated non-empty -> P=0, R=None, F1=0.
      - Generated empty but GT non-empty -> P=None, R=0, F1=0.
    Aggregate across cases: micro-average (sum tp/fp/fn, then compute).
"""

import difflib
import re
import unicodedata
from typing import Optional


TAU = 0.5  # default matching threshold


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _jaccard(a: str, b: str) -> float:
    """Token-set Jaccard similarity between two normalized strings."""
    sa = set(a.split())
    sb = set(b.split())
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _similarity(a: str, b: str) -> float:
    """Jaccard for longer strings; SequenceMatcher for short ones."""
    na, nb = _normalize(a), _normalize(b)
    if len(na.split()) < 4 or len(nb.split()) < 4:
        return difflib.SequenceMatcher(None, na, nb).ratio()
    return _jaccard(na, nb)


# ---------------------------------------------------------------------------
# Task flattening
# ---------------------------------------------------------------------------

def flatten_tasks(analysis: dict) -> list[dict]:
    """Convert MeetingAnalysis dict to a flat list of task dicts.

    Each item: {task, assignee, deadline, quote, slide}
    (assignee comes from the parent PersonTasks.person field)
    """
    flat = []
    for person_block in analysis.get("tasks_by_person", []):
        person = person_block.get("person", "Unassigned")
        for t in person_block.get("tasks", []):
            flat.append(
                {
                    "task": t.get("task", ""),
                    "assignee": person,
                    "deadline": t.get("deadline"),
                    "quote": t.get("quote", ""),
                    "slide": t.get("slide"),
                }
            )
    return flat


# ---------------------------------------------------------------------------
# Task matching
# ---------------------------------------------------------------------------

def match_tasks(generated: list[dict], gt: list[dict], tau: float = TAU) -> dict:
    """Greedy highest-similarity matching between generated and GT tasks.

    Returns:
        {
          "pairs": [(gen_idx, gt_idx, similarity), ...],
          "tp": int,
          "fp": int,   # unmatched generated
          "fn": int,   # unmatched GT
        }
    """
    if not generated and not gt:
        return {"pairs": [], "tp": 0, "fp": 0, "fn": 0}

    # Build similarity matrix
    sims: list[tuple[float, int, int]] = []
    for gi, g in enumerate(generated):
        for gti, gt_t in enumerate(gt):
            s = _similarity(g["task"], gt_t["task"])
            if s >= tau:
                sims.append((s, gi, gti))

    sims.sort(key=lambda x: -x[0])  # highest first

    used_gen: set[int] = set()
    used_gt: set[int] = set()
    pairs: list[tuple[int, int, float]] = []

    for sim, gi, gti in sims:
        if gi in used_gen or gti in used_gt:
            continue
        pairs.append((gi, gti, sim))
        used_gen.add(gi)
        used_gt.add(gti)

    tp = len(pairs)
    fp = len(generated) - tp
    fn = len(gt) - tp
    return {"pairs": pairs, "tp": tp, "fp": fp, "fn": fn}


# ---------------------------------------------------------------------------
# P / R / F1
# ---------------------------------------------------------------------------

def task_prf(tp: int, fp: int, fn: int) -> dict:
    """Compute Precision, Recall, F1 from tp/fp/fn counts.

    Returns dict with keys: precision, recall, f1 (each float or None).
    """
    total_gen = tp + fp
    total_gt = tp + fn

    # Both sides empty -> N/A
    if total_gen == 0 and total_gt == 0:
        return {"precision": None, "recall": None, "f1": None}

    precision = (tp / total_gen) if total_gen > 0 else None
    recall = (tp / total_gt) if total_gt > 0 else None

    if precision is not None and recall is not None:
        denom = precision + recall
        f1 = (2 * precision * recall / denom) if denom > 0 else 0.0
    else:
        f1 = 0.0

    return {"precision": precision, "recall": recall, "f1": f1}


def micro_average_prf(
    tp_sum: int, fp_sum: int, fn_sum: int
) -> dict:
    """Micro-average P/R/F1 from summed tp/fp/fn across all cases."""
    return task_prf(tp_sum, fp_sum, fn_sum)


# ---------------------------------------------------------------------------
# Per-pair accuracy metrics
# ---------------------------------------------------------------------------

def assignment_accuracy(
    pairs: list[tuple[int, int, float]],
    generated: list[dict],
    gt: list[dict],
) -> Optional[float]:
    """Fraction of matched pairs where assignee matches (case-insensitive).

    Returns None if no matched pairs.
    """
    if not pairs:
        return None
    correct = sum(
        1
        for gi, gti, _ in pairs
        if _normalize(generated[gi]["assignee"]) == _normalize(gt[gti]["assignee"])
    )
    return correct / len(pairs)


def slide_attr_accuracy(
    pairs: list[tuple[int, int, float]],
    generated: list[dict],
    gt: list[dict],
) -> Optional[float]:
    """Fraction of matched pairs (where GT slide is set) with correct slide number.

    Returns None if no eligible pairs.
    """
    eligible = [
        (gi, gti, s) for gi, gti, s in pairs if gt[gti].get("slide") is not None
    ]
    if not eligible:
        return None
    correct = sum(
        1 for gi, gti, _ in eligible
        if generated[gi].get("slide") == gt[gti]["slide"]
    )
    return correct / len(eligible)


# ---------------------------------------------------------------------------
# Slide extraction coverage
# ---------------------------------------------------------------------------

def slide_extract_coverage(pages: list[dict]) -> Optional[float]:
    """Fraction of PDF pages with non-empty extracted text.

    Args:
        pages: list of {page: int, text: str} from extract_slides()["pages"].

    Returns None if no pages (PDF had 0 pages).
    Target per poster: >= 0.95 (95%).
    """
    if not pages:
        return None
    non_empty = sum(1 for p in pages if p.get("text", "").strip())
    return non_empty / len(pages)
