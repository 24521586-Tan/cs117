# Research Report: Real Meeting Audio + Slide PDF for MeetMind Testing

_Conducted: 2026-05-31. Sources: 5 WebSearch queries (Gemini disabled)._

## Goal

Find 1 real meeting-style audio recording + matching slide PDF to test the MeetMind pipeline end-to-end (WhisperX → Gemini → Notion).

## Constraints (from README)

- Audio: **English**, `.mp3/.m4a/.wav`, **≤ 60 min**, low background noise.
- Slides: **text-based** `.pdf` (NOT scanned/image-only), **≤ 50 pages**.
- Audio + slides must be about the same content (else Gemini cross-referencing is meaningless).

## Recommendation (ranked)

### 1. MIT OpenCourseWare — paired "Lecture Audio and Slides" pages ⭐ BEST
Some OCW courses publish a lecture's **MP3 audio + slide PDF together on one page**, e.g.
`2.997 Direct Solar/Thermal to Electrical Energy Conversion` → page literally named **"Lecture Audio and Slides"**.
- ✅ Free, direct download, no login. English, academic, low noise. Slides are clean text-based PDFs.
- ✅ Audio + slides guaranteed about the same topic.
- ⚠️ Lectures can be > 60 min — pick a shorter session or trim with ffmpeg.
- Link: https://ocw.mit.edu/courses/2-997-direct-solar-thermal-to-electrical-energy-conversion-technologies-fall-2009/pages/audio-lectures/
- OCW home: https://ocw.mit.edu/

### 2. Earnings call (Apple / NVIDIA) — most "meeting"-like
Quarterly earnings call = a real business meeting; companies also publish an **investor presentation slide deck (PDF)**.
- ✅ Realistic meeting tone, English, ~45–60 min, professional/low noise.
- ✅ Slide deck PDF available on IR site.
- ⚠️ Audio often **streamed/webcast or podcast** (Apple Podcasts gives `.m4a` — works), not always a clean direct MP3. Slides grabbed separately from IR page.
- Apple earnings: https://www.apple.com/investor/earnings-call/ · podcast (m4a): https://podcasts.apple.com/us/podcast/apple-quarterly-earnings-call/id74942331
- NVIDIA IR presentations: https://investor.nvidia.com/events-and-presentations/presentations/default.aspx
- Aggregator (audio + slides together): Seeking Alpha https://seekingalpha.com/earnings/earnings-call-transcripts · Quartr API https://quartr.com/products/quartr-api

### 3. AMI Meeting Corpus — academic, real multi-person meetings
100h of staged meetings w/ audio + slide-projector output, CC BY 4.0.
- ✅ Genuine multi-speaker meeting audio, free.
- ⚠️ Slide output is **projector capture/whiteboard**, not a clean text PDF → likely fails MeetMind's "text-based PDF" requirement. Use only if you build a matching PDF yourself.
- https://groups.inf.ed.ac.uk/ami/corpus/ · https://groups.inf.ed.ac.uk/ami/download/ · HF: https://huggingface.co/datasets/edinburghcstr/ami

## Quick Start (pick #1)

1. Open the OCW "Lecture Audio and Slides" page, download one lecture's **MP3** + its **slides PDF**.
2. If audio > 60 min, trim:
   ```powershell
   ffmpeg -i lecture.mp3 -t 00:30:00 -c copy meeting.mp3
   ```
3. CLI test (fastest, no UI/auth):
   ```powershell
   cd backend
   .venv\Scripts\python.exe scripts\run_pipeline_local.py --audio meeting.mp3 --pdf slides.pdf
   ```
4. For real WhisperX: set `COLAB_WHISPER_URL` in `backend/.env`. Empty = mock transcript (tests Gemini+Notion only).

## Common Pitfalls

- Image-only/scanned PDF → "Slides text empty". Verify PDF has selectable text first.
- Audio + slides mismatched topic → Gemini to-do/quote linking is garbage.
- Earnings call audio that's stream-only → use the Apple Podcasts `.m4a` or a Quartr/Seeking Alpha download.

## Unresolved Questions

- Need a single OCW lecture confirmed **≤ 60 min** with **≤ 50-page** PDF — not verified per-lecture; pick at download time.
- Does `run_pipeline_local.py` accept `.m4a` directly, or only `.mp3`? (Apple Podcasts gives `.m4a`.) Check before using source #2.
