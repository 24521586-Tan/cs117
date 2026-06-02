# Báo Cáo Đánh Giá Hiệu Năng — MeetMind (CS117)
*Ngày đánh giá: 2026-06-02 10:38:32 | Tổng mẫu: 1*

## 1. Bảng Tổng Hợp (Summary Table)

| Mẫu | Kịch bản | Audio | RTF | WER | Slide Cov | Task P/R/F1 | Assign | KP Cov | Trạng thái |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| lec1 | 🎤+📄 Both | 25.4m | 0.203 | 30.8% | 100.0% | N/A | N/A | N/A | ✅ |

## 2. Tiêu Chí Định Lượng (Quantitative Metrics)

- **Tỷ lệ thành công (Success Rate):** 1/1 (100.0%)

### 2.1 Nhận dạng giọng nói (ASR)
- **Avg RTF:** 0.203 (ví dụ: 1 phút audio mất 0.2 phút xử lý)
- **Avg WER:** 30.8% (mục tiêu ≤ 15%)
- **Tốc độ pipeline (60 phút audio):** ❌ FAIL (12.2 phút / 60 phút audio) (mục tiêu ≤ 10 phút)

### 2.2 Trích xuất slide
- **Avg Slide Extraction Coverage:** 100.0% (mục tiêu ≥ 95%)

### 2.3 Trích xuất và giao việc (Task Extraction)
- **Micro-Precision:** N/A
- **Micro-Recall:** N/A (mục tiêu ≥ 80%)
- **Micro-F1:** N/A
- **Avg Assignment Accuracy:** N/A
- **Avg Slide Attribution Accuracy:** N/A

### 2.4 Tóm tắt (Summary)
- **Avg KP Coverage:** N/A

## 3. Tiêu Chí Định Tính — LLM Judge (Qualitative Metrics)

*(Gemini đóng vai trọng tài, chấm điểm 1.0–5.0)*

- **Summary Completeness (Độ đầy đủ tóm tắt):** 5.00 / 5.0
- **Summary Accuracy (Độ chính xác tóm tắt):** 5.00 / 5.0
- **Task Completeness (Độ đầy đủ giao việc):** 4.00 / 5.0
- **Task Assignment Accuracy (Đúng vai):** 5.00 / 5.0
- **Task Quote Accuracy (Trích dẫn):** 5.00 / 5.0 *(N/A cho PDF-only)*

- **📊 Điểm Tóm Tắt Tổng Hợp:** 1.00 / 1.00
- **📊 Điểm Giao Việc Tổng Hợp:** 0.93 / 1.00

## 4. Phân Tích Theo Kịch Bản (Per-Scenario Breakdown)

### 🎤+📄 Both (1 mẫu)
- Avg RTF: 0.203 | Avg WER: 30.8% | Avg Task F1: N/A


## 5. Chi Tiết Từng Mẫu Thử (Per-Case Detail)

### lec1 — 🎤+📄 Both
- Thời lượng: 25.4 phút | ASR: 309.7s | Slides: 0.0s | Gemini: 35.1s
- WER: 30.79%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 5.0/5 — Bản tóm tắt đã nắm bắt đầy đủ tất cả các điểm chính của cuộc họp, bao gồm việc xem xét biên bản cuộc họp trước, trình bày nguyên mẫu, quá trình đánh giá dựa trên các tiêu chí, kết quả đánh giá, thảo luận về ngân sách và việc điều chỉnh thiết kế để phù hợp với ngân sách, cũng như đánh giá quy trình dự án và các bước kết thúc.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong bản tóm tắt đều chính xác và được hỗ trợ bởi nội dung cuộc họp. Không có thông tin nào bịa đặt hay sai lệch so với bản ghi gốc.
- **Task Completeness:** 4.0/5 — Bản phân tích đã trích xuất được 2 trong số 3 nhiệm vụ chính được đề cập trong cuộc họp. Nhiệm vụ "check with the main boss whether we can, what goes on after that" (kiểm tra với sếp chính về các bước tiếp theo) đã bị bỏ sót.
- **Task Assignment:** 5.0/5 — Các nhiệm vụ được trích xuất đều được gán chính xác cho "Meeting Lead", người đã đề cập đến các nhiệm vụ này trong cuộc họp.
- **Task Quote:** 5.0/5 — Các trích dẫn cho nhiệm vụ hoàn toàn khớp với lời nói trong bản ghi cuộc họp.

> Bản phân tích cuộc họp có chất lượng rất tốt. Phần tóm tắt và độ chính xác của thông tin là hoàn hảo. Tuy nhiên, có một nhiệm vụ quan trọng đã bị bỏ lỡ trong phần giao việc. Cần cải thiện khả năng trích xuất tất cả các nhiệm vụ được đề cập để đảm bảo tính đầy đủ.

---

