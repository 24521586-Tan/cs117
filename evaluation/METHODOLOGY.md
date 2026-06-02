# Phương Pháp Đánh Giá Giải Pháp MeetMind

**Môn học:** CS117 — Tư duy tính toán  
**GVHD:** NGÔ ĐỨC THÀNH  
**Nhóm:** Nguyễn Trọng Nghĩa, Nguyễn Thiện Nhân, Nguyễn Đăng Ân Phước, Văn Đức Tân, Tú Lê Tuấn Anh

---

## 1. Mục tiêu giải pháp (Objectives)

MeetMind giải quyết bài toán: *người dùng không ghi lại được đầy đủ nội dung cuộc họp,
dẫn đến bỏ sót deadline và nhiệm vụ cá nhân.* Hệ thống nhận audio + slide PDF đầu vào
và tự động tạo trang Notion gồm **Meeting Summary** và **To-do List** có checkbox,
deadline, trích dẫn verbatim và số slide nguồn.

**Mục tiêu kỹ thuật cụ thể (từ poster):**
1. Transcript WER ≤ 15% (tiếng Anh, môi trường ít nhiễu).
2. Trích xuất ≥ 95% nội dung từ slide PDF text-based.
3. Trích xuất ≥ 80% task và deadline từ cuộc họp.
4. Mỗi task phải đúng nguồn slide + trích dẫn verbatim.
5. Không thêm thông tin ngoài transcript/slide (không hallucination).
6. Pipeline ≤ 10 phút cho audio 60 phút.
7. Đầu ra là 1 trang Notion hoàn chỉnh.

---

## 2. Xác định tiêu chí đánh giá (Metric Identification)

Theo quy trình 5 bước của thầy (slide 13):

| Bước | Hành động |
|:---|:---|
| 1. Xác định mục tiêu | 7 mục tiêu kỹ thuật nêu trên |
| 2. Liệt kê nhu cầu | Người dùng cần: tóm tắt đầy đủ, task đúng người, deadline rõ, không sai thông tin |
| 3. Chọn tiêu chí | Mapping bên dưới (§3) |
| 4. Xác định đo lường | Công thức và phương pháp (§4, §5) |
| 5. Kiểm chứng và tinh chỉnh | Chạy thử, kiểm tra τ=0.5, điều chỉnh ngưỡng nếu cần |

---

## 3. Mapping Yêu Cầu → Tiêu Chí (Requirements ↔ Metrics)

*(Mối quan hệ nhiều–nhiều theo slide 18–19)*

| # | Yêu cầu / Mong đợi | Tiêu chí đánh giá | Loại |
|:---:|:---|:---|:---:|
| R1 | Transcript chính xác | **WER** (Word Error Rate) | Định lượng |
| R2 | Hệ thống xử lý đủ nhanh | **RTF** + Speed Target PASS/FAIL | Định lượng |
| R3 | Trích xuất đủ nội dung slide | **Slide Extraction Coverage** | Định lượng |
| R4 | Không bỏ sót task | **Task Recall** (và F1) | Định lượng |
| R4 | Không bỏ sót task | **Task Completeness** (LLM judge) | Định tính |
| R5 | Task giao đúng người | **Assignment Accuracy** | Định lượng |
| R5 | Task giao đúng người | **Task Assignment Accuracy** (LLM judge) | Định tính |
| R6 | Task đúng nguồn slide | **Slide Attribution Accuracy** | Định lượng |
| R7 | Trích dẫn verbatim chính xác | **Task Quote Accuracy** (LLM judge) | Định tính |
| R8 | Summary đầy đủ | **Summary KP Coverage** | Định lượng |
| R8 | Summary đầy đủ | **Summary Completeness** (LLM judge) | Định tính |
| R9 | Không hallucination | **Summary Accuracy** (LLM judge) | Định tính |
| R10 | Hệ thống ổn định | **Success Rate** | Định lượng |

**Nhận xét mapping:** R4, R5, R8 mỗi mong đợi cần **nhiều tiêu chí** (1-many) để phản ánh
đầy đủ cả góc khách quan (định lượng) lẫn chủ quan (LLM judge). Đây là ví dụ điển hình
của quan hệ nhiều–nhiều (many-to-many) theo lý thuyết slide 18.

---

## 4. Phân Loại Tiêu Chí

### 4.1 Định lượng (Quantitative Metrics)

*Khách quan, có công thức rõ ràng, tái lập được, dễ so sánh.*

| Metric | Công thức tóm tắt | Phạm vi | Mục tiêu |
|:---|:---|:---:|:---:|
| WER | edit_distance(words) / len(ref) | [0, ∞) | ≤ 0.15 |
| RTF | tx_time / audio_duration | [0, ∞) | ≤ 0.167 |
| Speed Target | RTF × 60 ≤ 10 phút | PASS/FAIL | PASS |
| Slide Coverage | non_empty_pages / total_pages | [0, 1] | ≥ 0.95 |
| Task Precision | TP / (TP+FP) | [0, 1] | — |
| Task Recall | TP / (TP+FN) | [0, 1] | ≥ 0.80 |
| Task F1 | 2PR/(P+R) | [0, 1] | cao nhất có thể |
| Assignment Accuracy | matched_correct / matched_total | [0, 1] | cao nhất có thể |
| Slide Attribution | correct_slide / eligible_pairs | [0, 1] | cao nhất có thể |
| Summary KP Coverage | covered_kp / total_kp | [0, 1] | cao nhất có thể |
| Success Rate | success / total_cases | [0, 1] | 1.0 |

### 4.2 Định tính (Qualitative Metrics)

*Phản ánh trải nghiệm và cảm nhận, bổ sung cho định lượng.*

LLM-as-a-Judge: Gemini đóng vai trọng tài độc lập, chấm điểm 1.0–5.0:

| Tiêu chí | Câu hỏi cốt lõi |
|:---|:---|
| Summary Completeness | Summary có bao phủ tất cả chủ đề và quyết định chính? |
| Summary Accuracy | Summary có chứa thông tin sai/bịa đặt so với nguồn? |
| Task Completeness | Có bỏ sót action item nào không? |
| Task Assignment Accuracy | Task có giao đúng người không? |
| Task Quote Accuracy | Trích dẫn có khớp lời nói thật sự? *(N/A với PDF-only)* |

**Hạn chế của định tính:** Kết quả phụ thuộc vào LLM trọng tài (non-deterministic),
có thể không hoàn toàn tái lập. Đây là lý do cần kết hợp với định lượng.

---

## 5. Kiểm tra SMART

| Metric | S — Cụ thể | M — Đo được | A — Khả thi | R — Liên quan | T — Giới hạn |
|:---|:---:|:---:|:---:|:---:|:---:|
| WER | ✅ công thức rõ | ✅ tính được | ✅ cần GT transcript | ✅ R1 | Đo trước khi deploy |
| RTF | ✅ | ✅ | ✅ đo tự động | ✅ R2 | Mỗi lần chạy |
| Slide Coverage | ✅ | ✅ | ✅ đo tự động | ✅ R3 | Mỗi lần chạy |
| Task Recall | ✅ | ✅ | ⚠️ cần GT JSON | ✅ R4 | Đo trước khi deploy |
| LLM Judge | ✅ rubric rõ | ⚠️ phụ thuộc LLM | ✅ | ✅ R4–R9 | Mỗi lần chạy |
| Success Rate | ✅ | ✅ | ✅ | ✅ R10 | Mỗi lần chạy |

---

## 6. Phân Tích Trade-off

### 6.1 Tốc độ vs Độ chính xác ASR
- Mô hình `large-v2` cho WER thấp hơn nhưng RTF cao hơn `small`.
- Trade-off: chấp nhận RTF cao hơn để đạt WER mục tiêu ≤ 15%.
- Trên GPU (NVIDIA), `large-v2` vẫn đáp ứng được Speed Target.

### 6.2 Định lượng vs Định tính (Task Accuracy)
- **Task Recall** (định lượng): khách quan, tái lập, nhưng phụ thuộc vào chất lượng nhãn GT
  và ngưỡng ghép τ=0.5. Nếu paraphrase quá xa, Jaccard < 0.5 → bị tính là FN sai.
- **LLM Judge Task Completeness** (định tính): xử lý được paraphrase, nhưng không deterministic
  và có thể bị bias bởi LLM tạo ra analysis.

**Giải pháp:** Dùng cả hai. Nếu định lượng và định tính mâu thuẫn, ưu tiên định lượng
(có ground-truth) và ghi chú lý do trong báo cáo.

### 6.3 LLM Matcher vs Deterministic Matcher
- **Deterministic (Jaccard, mặc định):** tái lập, không tốn API call, không bị bias vòng tròn.
  Hạn chế: brittle với paraphrase ("email report" vs "send document" → Jaccard ≈ 0).
- **LLM Matcher (tuỳ chọn):** xử lý ngữ nghĩa tốt hơn, nhưng:
  - Không deterministic (kết quả có thể khác mỗi lần)
  - Circular bias: cùng LLM tạo analysis và đánh giá matching
  - Tốn thêm API calls

**Quyết định:** Mặc định dùng Jaccard (τ=0.5). Có thể điều chỉnh `TAU` trong
`metrics_quantitative.py` nếu cần.

### 6.4 Bảo mật và Quyền riêng tư
- Audio và PDF cuộc họp có thể chứa thông tin nhạy cảm.
- Giải pháp: tự động xoá file audio/PDF khỏi Supabase Storage sau khi tạo trang Notion.
- File ground-truth `.txt` và `.json` không được commit vào GitHub public repo.

---

## 7. Phương Pháp Gán Nhãn Ground-Truth

### 7.1 Transcript (`transcripts_ground_truth/{name}.txt`)
- Nghe lại audio, viết transcript theo từng câu.
- Dùng ngôn ngữ gốc của audio (thường là tiếng Anh).
- Không cần timestamp, chỉ cần nội dung đúng.

### 7.2 Task analysis (`ground_truth_analysis/{name}.json`)
- Nghe lại audio và/hoặc đọc slide, liệt kê tất cả action items.
- Điền đúng `assignee` (dùng `"Unassigned"` nếu không rõ).
- Điền `slide` chỉ khi task **thực sự liên quan** đến nội dung slide đó.
- `quote` là câu verbatim từ transcript (để tham khảo, không dùng trong tính metric).

### 7.3 Nguyên tắc nhãn
- Nhất quán: cùng quy tắc đặt tên `assignee` cho tất cả file.
- Bảo thủ: chỉ đánh dấu `covered: true` nếu ý tứ rõ ràng có trong summary/transcript.
- Độc lập: người gán nhãn không xem output của hệ thống trước khi gán nhãn.

---

## 8. Các Kịch Bản Đánh Giá

| Kịch bản | Input | WER | Task P/R/F1 | Quote Accuracy |
|:---|:---:|:---:|:---:|:---:|
| `both` — đầy đủ | audio + PDF | ✅ | ✅ | ✅ |
| `audio_only` — chỉ audio | audio | ✅ | ✅ | ✅ |
| `pdf_only` — chỉ slide | PDF | N/A | ✅ (nếu có GT) | N/A |

Đánh giá trên cả 3 kịch bản giúp phát hiện:
- Hệ thống hoạt động tốt hơn khi có cả hai nguồn thông tin không?
- Slide có thực sự cải thiện chất lượng task extraction không?
- Pipeline có ổn định khi thiếu một trong hai nguồn không?
