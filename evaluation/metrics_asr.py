"""ASR accuracy metrics: WER and RTF.

Pure math — no backend imports. Safe to run standalone.

WER (Word Error Rate):
    Levenshtein edit distance on word lists (not chars).
    WER = (S + D + I) / N  where N = number of reference words,
    S = substitutions, D = deletions, I = insertions.
    Range: 0.0 (perfect) to 1.0+ (more errors than words).
    Target per poster: WER <= 0.15 (15%).

RTF (Real-Time Factor):
    RTF = transcription_wall_time / audio_duration
    RTF < 1.0 means faster than real-time.
    Target per poster: pipeline <= 10 min for 60-min audio -> RTF <= 10/60 ~ 0.167.
"""

import re
import unicodedata


def normalize_text(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace for fair comparison."""
    text = text.lower()
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def calculate_wer(reference: str, hypothesis: str) -> float:
    """Word Error Rate via dynamic-programming Levenshtein on word lists.

    Args:
        reference: Ground-truth transcript (raw string).
        hypothesis: ASR output (raw string).

    Returns:
        WER as float >= 0.0. Returns 0.0 if both are empty.
        Can exceed 1.0 if many insertions.
    """
    ref_words = normalize_text(reference).split()
    hyp_words = normalize_text(hypothesis).split()

    if not ref_words:
        return 0.0 if not hyp_words else float(len(hyp_words))

    n_ref = len(ref_words)
    n_hyp = len(hyp_words)

    # dp[i][j] = edit distance between ref[:i] and hyp[:j]
    dp = [[0] * (n_hyp + 1) for _ in range(n_ref + 1)]
    for i in range(n_ref + 1):
        dp[i][0] = i
    for j in range(n_hyp + 1):
        dp[0][j] = j

    for i in range(1, n_ref + 1):
        for j in range(1, n_hyp + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j - 1],  # substitution
                    dp[i][j - 1],      # insertion
                    dp[i - 1][j],      # deletion
                )

    return dp[n_ref][n_hyp] / n_ref


def project_pipeline_minutes(avg_rtf: float, audio_minutes: float = 60.0) -> float:
    """Estimate pipeline wall-clock minutes for a given audio length at avg RTF."""
    return avg_rtf * audio_minutes


def speed_target_pass(
    avg_rtf: float, target_minutes: float = 10.0, audio_minutes: float = 60.0
) -> bool:
    """True if projected pipeline time <= target_minutes for audio_minutes of audio."""
    return project_pipeline_minutes(avg_rtf, audio_minutes) <= target_minutes
