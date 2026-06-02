# MeetMind — Evaluation Harness

Hướng dẫn chạy đánh giá và giải thích cách tính từng metric.

---

## Cách chạy (CLI)

### Bước 1 — Chuẩn bị file input

Thả file vào đúng thư mục. Tên file phải **khớp nhau** (cùng stem):

```
evaluation/
├── audios/                        ← *.mp3 hoặc *.mp4 (chỉ lấy audio)
│   └── lec1.mp3
├── slides/                        ← *.pdf
│   └── lec1.pdf
├── transcripts_ground_truth/      ← *.txt  (tuỳ chọn — để tính WER)
│   └── lec1.txt
└── ground_truth_analysis/         ← *.json (tuỳ chọn — để tính P/R/F1)
    └── lec1.json
```

**Kịch bản được hỗ trợ:**
| Có audio | Có PDF | Kịch bản |
|:---:|:---:|:---|
| ✅ | ✅ | `both` — đầy đủ |
| ✅ | ❌ | `audio_only` — không trích xuất slide |
| ❌ | ✅ | `pdf_only` — không có transcript, WER = N/A |

> **Lưu ý:** Để test cùng nội dung theo 2 kịch bản khác nhau, dùng stem khác nhau:
> `lec1_audio.mp3` (audio-only) và `lec1_pdf.pdf` (pdf-only).

---

### Bước 2 — Chạy lệnh

```bash
# Chạy từ thư mục backend/ để .env được load tự động
cd backend

# Tất cả file trong thư mục input
python ../evaluation/run_eval.py

# Chỉ một case cụ thể
python ../evaluation/run_eval.py --file lec1
```

---

### Bước 3 — Xem kết quả

Kết quả được ghi vào `evaluation/results/`:

| File | Nội dung |
|:---|:---|
| `lec1.metrics.json` | Tất cả số liệu thô của case `lec1` |
| `aggregate.json` | KPI tổng hợp (micro-avg, per-scenario) |
| `evaluation_report.md` | Báo cáo tiếng Việt (mở bằng VS Code/Obsidian) |

---

### Git workflow (cho cả nhóm)

```bash
# Commit input + kết quả để teammate reproduce được
git add evaluation/audios/ evaluation/slides/
git add evaluation/transcripts_ground_truth/ evaluation/ground_truth_analysis/
git add evaluation/results/
git commit -m "feat: add evaluation results for lec1"
git push

# Teammate pull về và chạy lại
git pull
cd backend
python ../evaluation/run_eval.py
```

---

## Cách tính từng metric

### 1. WER — Word Error Rate (Tỷ lệ lỗi từ)

**Nguồn:** `metrics_asr.py → calculate_wer()`

**Yêu cầu:** File `transcripts_ground_truth/{name}.txt` (transcript do người viết tay).

**Công thức:**
```
WER = (S + D + I) / N

S = số từ bị thay thế (substitution)
D = số từ bị xoá (deletion)
I = số từ bị thêm thừa (insertion)
N = số từ trong transcript chuẩn (reference)
```

**Cách tính:** Dynamic programming Levenshtein trên danh sách từ (không phải ký tự).
Văn bản được chuẩn hoá trước: lowercase, bỏ dấu câu, chuẩn hoá unicode.

**Phạm vi:** 0.0 (hoàn hảo) đến 1.0+ (nhiều lỗi hơn số từ gốc).

**Mục tiêu dự án:** ≤ 0.15 (15%).

**Ví dụ:**
```
Reference:  "please send the report by friday"   (6 từ)
Hypothesis: "please sent report by next friday"  (6 từ)
→ S=2 (send→sent, the→next), D=1 (the), I=1 (next)
→ WER = (2+1+1)/6 ≈ 0.67 — không tốt
```

---

### 2. RTF — Real-Time Factor (Hệ số thời gian thực)

**Nguồn:** `run_eval.py` (tính trong loop)

**Công thức:**
```
RTF = thời_gian_chạy_ASR (giây) / độ_dài_audio (giây)
```

**Phạm vi:** RTF < 1.0 = nhanh hơn thời gian thực.

**Mục tiêu dự án:** Pipeline ≤ 10 phút cho audio 60 phút → RTF ≤ 10/60 ≈ 0.167.

**Ví dụ:**
```
Audio: 60 phút = 3600 giây
Thời gian chạy ASR: 480 giây (8 phút)
→ RTF = 480/3600 = 0.133  ✅ PASS
```

---

### 3. Pipeline Speed Target (Mục tiêu tốc độ pipeline)

**Nguồn:** `metrics_asr.py → speed_target_pass()` / `results_logger.py`

**Kiểm tra:** `avg_RTF × 60 ≤ 10 phút`

Hiển thị **PASS / FAIL** trong report.

---

### 4. Slide Extraction Coverage (Độ bao phủ trích xuất slide)

**Nguồn:** `metrics_quantitative.py → slide_extract_coverage()`

**Công thức:**
```
Coverage = số_trang_có_text / tổng_số_trang
```

Một trang được coi là "có text" nếu sau khi strip() còn ít nhất 1 ký tự.

**Mục tiêu dự án:** ≥ 0.95 (95%).

**Lưu ý:** PDF scan dạng ảnh sẽ cho coverage = 0%. Chỉ hỗ trợ PDF text-based.

---

### 5. Task Matching — Token-set Jaccard (Ghép task)

**Nguồn:** `metrics_quantitative.py → match_tasks()`

Trước khi tính P/R/F1, cần xác định task nào là TP (ghép được giữa generated và ground-truth).

**Thuật toán:**
1. Chuẩn hoá cả 2 chuỗi task (lowercase, bỏ dấu câu).
2. Tính **Jaccard similarity** trên tập token:
   ```
   Jaccard(A, B) = |A ∩ B| / |A ∪ B|
   ```
   Nếu chuỗi ngắn (< 4 token): dùng `SequenceMatcher.ratio()` thay thế.
3. **Greedy matching:** lấy cặp (generated, GT) có similarity cao nhất ≥ τ=0.5,
   loại cả 2 khỏi pool, lặp lại cho đến khi không còn cặp nào đủ điều kiện.

**Ngưỡng τ=0.5:** Có thể điều chỉnh nếu cần (xem `TAU` trong `metrics_quantitative.py`).

**Ví dụ:**
```
Generated task: "prepare presentation slides"
GT task:        "prepare the slide deck for presentation"
Token sets: {"prepare","presentation","slides"} vs {"prepare","the","slide","deck","for","presentation"}
Intersection: {"prepare","presentation"} = 2
Union: 7 tokens
Jaccard = 2/7 ≈ 0.29 → KHÔNG ghép được (< 0.5)

Generated task: "set up CI pipeline on repo"
GT task:        "set up CI pipeline"
Jaccard = 3/5 = 0.6 → GhÉP được ✅
```

---

### 6. Task Precision / Recall / F1

**Nguồn:** `metrics_quantitative.py → task_prf()`

Sau khi ghép task:
```
TP = số task generated được ghép với GT
FP = số task generated KHÔNG ghép được (thêm thừa)
FN = số task GT KHÔNG được ghép (bỏ sót)

Precision = TP / (TP + FP)   — trong những task đưa ra, bao nhiêu % đúng?
Recall    = TP / (TP + FN)   — trong những task cần có, bao nhiêu % tìm được?
F1        = 2 × P × R / (P + R)
```

**Xử lý chia cho 0:**
| Tình huống | P | R | F1 |
|:---|:---:|:---:|:---:|
| Generated = 0, GT = 0 | N/A | N/A | N/A |
| Generated > 0, GT = 0 | 0.0 | N/A | 0.0 |
| Generated = 0, GT > 0 | N/A | 0.0 | 0.0 |

**Tổng hợp nhiều case:** Micro-average (cộng dồn TP/FP/FN rồi tính, không lấy trung bình P/R/F1).

**Mục tiêu dự án:** Recall ≥ 0.80 (80%).

---

### 7. Assignment Accuracy (Độ chính xác giao việc)

**Nguồn:** `metrics_quantitative.py → assignment_accuracy()`

**Công thức:**
```
Assignment Accuracy = số cặp TP có đúng assignee / tổng số cặp TP
```

So sánh `assignee` sau khi chuẩn hoá (lowercase). Dùng `"Unassigned"` cho task chưa rõ người.

**Trả về `None`** nếu không có cặp TP nào.

---

### 8. Slide Attribution Accuracy (Độ chính xác gán slide)

**Nguồn:** `metrics_quantitative.py → slide_attr_accuracy()`

**Công thức:**
```
Slide Attribution Accuracy =
    số cặp TP (có GT slide ≠ null) với slide number đúng /
    tổng số cặp TP có GT slide ≠ null
```

**Trả về `None`** nếu không có GT task nào có `slide` được đặt.

---

### 9. Summary KP Coverage (Độ bao phủ điểm chính)

**Nguồn:** `llm_judge.py → evaluate_summary_kp_coverage()`

**Yêu cầu:** Field `summary_key_points` trong `ground_truth_analysis/{name}.json`.

**Cách tính:** Gọi Gemini với danh sách key points + summary được tạo ra, hỏi
"key point nào được đề cập trong summary?". Mỗi key point trả về `covered: true/false`.

```
KP Coverage = số key points covered / tổng số key points
```

---

### 10. Success Rate (Tỷ lệ thành công)

```
Success Rate = số case chạy thành công / tổng số case
```

Case lỗi (exception) không được tính vào bất kỳ metric trung bình nào.

---

### 11. LLM Judge — 5 tiêu chí (1.0–5.0)

**Nguồn:** `llm_judge.py → evaluate_analysis_with_llm()`

Gemini đóng vai trọng tài, chấm điểm từ 1.0 đến 5.0:

| Tiêu chí | Mô tả | N/A khi |
|:---|:---|:---|
| Summary Completeness | Tóm tắt có đầy đủ các chủ đề và quyết định chính? | — |
| Summary Accuracy | Tóm tắt có thông tin ngoài transcript/slide không? | — |
| Task Completeness | Tất cả action items được trích xuất? | — |
| Task Assignment Accuracy | Task được giao đúng người? | — |
| Task Quote Accuracy | Trích dẫn verbatim có khớp transcript không? | pdf_only |

Điểm tổng hợp:
```
Summary Score = (Completeness + Accuracy) / 10.0    → [0.0, 1.0]
Task Score    = (Completeness + Assignment + Quote) / 15.0  → [0.0, 1.0]
```

---

## Cấu trúc file ground-truth

### `transcripts_ground_truth/{name}.txt`
Transcript do người viết tay (plain text, UTF-8).
Dùng để tính **WER**.

### `ground_truth_analysis/{name}.json`
```json
{
  "name": "lec1",
  "scenario": "both",
  "summary_key_points": [
    "Điểm chính 1 cần có trong summary",
    "Điểm chính 2..."
  ],
  "tasks": [
    {
      "task": "Mô tả task (dùng để ghép với output)",
      "assignee": "Tên người hoặc Unassigned",
      "deadline": "by Friday hoặc null",
      "slide": 3,
      "quote": "Câu verbatim từ transcript (để tham khảo)"
    }
  ]
}
```

> **Lưu ý:** Tất cả file ground-truth đều **tuỳ chọn**. Nếu thiếu, metric tương ứng
> hiển thị N/A và harness vẫn chạy bình thường với LLM-judge.

---

## Cấu trúc module

| File | Mục đích |
|:---|:---|
| `run_eval.py` | CLI entry point, orchestration loop |
| `case_discovery.py` | Scan input folders, detect scenarios |
| `metrics_asr.py` | WER, RTF (pure math, no backend) |
| `metrics_quantitative.py` | Task P/R/F1, coverage (pure math) |
| `llm_judge.py` | Gemini judge + KP coverage |
| `results_logger.py` | Write JSON metric files |
| `report_writer.py` | Write Vietnamese Markdown report |
