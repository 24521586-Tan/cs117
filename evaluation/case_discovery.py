"""Discover test cases from evaluation input folders.

Scans audios/ (*.mp3) and slides/ (*.pdf) for matching stems,
determines scenario per case (AUDIO_ONLY / PDF_ONLY / BOTH),
and attaches optional ground-truth paths.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


AUDIO_EXTS = (".mp3", ".mp4", ".wav")  # .mp4 used as audio-only; faster-whisper extracts the audio track
SLIDE_EXT = ".pdf"


class Scenario(str, Enum):
    AUDIO_ONLY = "audio_only"
    PDF_ONLY = "pdf_only"
    BOTH = "both"


@dataclass
class EvalCase:
    name: str
    audio_path: Optional[Path]
    pdf_path: Optional[Path]
    gt_transcript_path: Optional[Path]   # transcripts_ground_truth/{name}.txt
    gt_analysis_path: Optional[Path]     # ground_truth_analysis/{name}.json
    scenario: Scenario

    @property
    def has_audio(self) -> bool:
        return self.audio_path is not None and self.audio_path.is_file()

    @property
    def has_slides(self) -> bool:
        return self.pdf_path is not None and self.pdf_path.is_file()

    @property
    def has_gt_transcript(self) -> bool:
        return self.gt_transcript_path is not None and self.gt_transcript_path.is_file()

    @property
    def has_gt_analysis(self) -> bool:
        return self.gt_analysis_path is not None and self.gt_analysis_path.is_file()


def _stem_from_path(p: Path) -> str:
    """Return file stem (name without extension)."""
    return p.stem


def discover_cases(eval_dir: Path, file_filter: Optional[str] = None) -> list[EvalCase]:
    """Return sorted list of EvalCase objects from the evaluation input folders.

    Args:
        eval_dir: Root of the evaluation/ directory.
        file_filter: Optional stem filter (e.g. "lec1" matches lec1.mp3 / lec1.pdf).
                     Strips known extensions before matching.
    """
    audios_dir = eval_dir / "audios"
    slides_dir = eval_dir / "slides"
    gt_txt_dir = eval_dir / "transcripts_ground_truth"
    gt_json_dir = eval_dir / "ground_truth_analysis"

    # Build stem→path dicts for audio and slides
    audio_by_stem: dict[str, Path] = {}
    for ext in AUDIO_EXTS:
        for p in audios_dir.glob(f"*{ext}"):
            audio_by_stem[p.stem] = p

    pdf_by_stem: dict[str, Path] = {}
    for p in slides_dir.glob(f"*{SLIDE_EXT}"):
        pdf_by_stem[p.stem] = p

    # Union of stems = all test cases
    all_stems = sorted(set(audio_by_stem) | set(pdf_by_stem))

    # Apply file_filter if provided
    if file_filter:
        # Strip any known extension from the filter value
        filter_stem = file_filter
        for ext in list(AUDIO_EXTS) + [SLIDE_EXT]:
            if filter_stem.endswith(ext):
                filter_stem = filter_stem[: -len(ext)]
                break
        all_stems = [s for s in all_stems if s == filter_stem]

    cases: list[EvalCase] = []
    for stem in all_stems:
        audio_path = audio_by_stem.get(stem)
        pdf_path = pdf_by_stem.get(stem)

        if audio_path and pdf_path:
            scenario = Scenario.BOTH
        elif audio_path:
            scenario = Scenario.AUDIO_ONLY
        else:
            scenario = Scenario.PDF_ONLY

        gt_txt = gt_txt_dir / f"{stem}.txt"
        gt_json = gt_json_dir / f"{stem}.json"

        cases.append(
            EvalCase(
                name=stem,
                audio_path=audio_path,
                pdf_path=pdf_path,
                gt_transcript_path=gt_txt if gt_txt.exists() else None,
                gt_analysis_path=gt_json if gt_json.exists() else None,
                scenario=scenario,
            )
        )

    return cases
