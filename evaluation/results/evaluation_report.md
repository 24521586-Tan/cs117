# Báo Cáo Đánh Giá Hiệu Năng — MeetMind (CS117)
*Ngày đánh giá: 2026-06-02 20:56:49 | Tổng mẫu: 16*

## 1. Bảng Tổng Hợp (Summary Table)

| Mẫu | Kịch bản | Audio | RTF | WER | Slide Cov | Task P/R/F1 | Assign | KP Cov | Trạng thái |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| ES2013a | 🎤+📄 Both | 13.8m | 0.279 | 22.9% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2013b | 🎤+📄 Both | 35.5m | 2.496 | 28.2% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2013c | 🎤+📄 Both | 39.3m | 0.214 | 37.3% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2013d | 🎤+📄 Both | 31.6m | 0.209 | 28.6% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2014a | 🎤 Audio Only | 19.2m | 0.194 | 34.9% | N/A | N/A | N/A | N/A | ✅ |
| ES2014b | 🎤+📄 Both | 38.7m | 0.251 | 32.3% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2014c | 🎤+📄 Both | 37.9m | 0.257 | 30.6% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2014d | 🎤+📄 Both | 48.5m | 0.208 | 37.8% | 100.0% | N/A | N/A | N/A | ❌ 503 UNAVAILABLE. {'error': {'code': 503, |
| ES2015a | 🎤+📄 Both | 19.1m | 0.177 | 25.2% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2015b | 🎤+📄 Both | 38.2m | 0.204 | 31.0% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2015c | 🎤+📄 Both | 35.6m | 0.232 | 23.4% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2015d | 🎤+📄 Both | 32.2m | 0.275 | 34.3% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2016a | 🎤 Audio Only | 23.1m | 0.176 | 25.9% | N/A | N/A | N/A | N/A | ✅ |
| ES2016b | 🎤+📄 Both | 40.2m | 0.181 | 21.2% | 100.0% | N/A | N/A | N/A | ❌ 503 UNAVAILABLE. {'error': {'code': 503, |
| ES2016c | 🎤+📄 Both | 38.5m | 0.160 | 26.0% | 100.0% | N/A | N/A | N/A | ✅ |
| ES2016d | 🎤+📄 Both | 25.4m | 0.163 | 46.0% | 100.0% | N/A | N/A | N/A | ✅ |

## 2. Tiêu Chí Định Lượng (Quantitative Metrics)

- **Tỷ lệ thành công (Success Rate):** 14/16 (87.5%)

### 2.1 Nhận dạng giọng nói (ASR)
- **Avg RTF:** 0.405 (ví dụ: 1 phút audio mất 0.4 phút xử lý)
- **Avg WER:** 30.5% (mục tiêu ≤ 15%)
- **Tốc độ pipeline (60 phút audio):** ❌ FAIL (24.3 phút / 60 phút audio) (mục tiêu ≤ 10 phút)

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

- **Summary Completeness (Độ đầy đủ tóm tắt):** 4.64 / 5.0
- **Summary Accuracy (Độ chính xác tóm tắt):** 5.00 / 5.0
- **Task Completeness (Độ đầy đủ giao việc):** 4.82 / 5.0
- **Task Assignment Accuracy (Đúng vai):** 4.82 / 5.0
- **Task Quote Accuracy (Trích dẫn):** 4.89 / 5.0 *(N/A cho PDF-only)*

- **📊 Điểm Tóm Tắt Tổng Hợp:** 0.96 / 1.00
- **📊 Điểm Giao Việc Tổng Hợp:** 0.97 / 1.00

## 4. Phân Tích Theo Kịch Bản (Per-Scenario Breakdown)

### 🎤+📄 Both (12 mẫu)
- Avg RTF: 0.410 | Avg WER: 30.5% | Avg Task F1: N/A

### 🎤 Audio Only (2 mẫu)
- Avg RTF: 0.185 | Avg WER: 30.4% | Avg Task F1: N/A


## 5. Chi Tiết Từng Mẫu Thử (Per-Case Detail)

### ES2013a — 🎤+📄 Both
- Thời lượng: 13.8 phút | ASR: 229.9s | Slides: 0.0s | Gemini: 14.0s
- WER: 22.87%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 4.5/5 — Tóm tắt đã nắm bắt được hầu hết các quyết định và chủ đề chính của cuộc họp, bao gồm mục tiêu dự án, mục tiêu tài chính, buổi đào tạo công cụ và các ý tưởng ban đầu cho điều khiển từ xa. Tuy nhiên, nó bỏ qua một số chi tiết nhỏ hơn như các bước cụ thể trong phương pháp dự án (thiết kế chức năng, thiết kế ý tưởng, thiết kế chi tiết) và thời lượng cuộc họp (25 phút).
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong phần tóm tắt đều chính xác và được trích xuất trực tiếp từ bản ghi cuộc họp. Không có thông tin sai lệch hay bịa đặt nào.
- **Task Completeness:** 5.0/5 — Tất cả các mục hành động rõ ràng được đề cập trong bản ghi đã được trích xuất đầy đủ. Các hoạt động như thử nghiệm bảng trắng được coi là đào tạo công cụ chứ không phải nhiệm vụ dài hạn, và các mục tiêu chung của dự án không được coi là nhiệm vụ cá nhân, điều này là hợp lý.
- **Task Assignment:** 5.0/5 — Tất cả các nhiệm vụ đã được giao chính xác cho đúng người hoặc đúng bộ phận (ví dụ: 'Unassigned' cho nhiệm vụ tiếp thị khi không có tên cụ thể được đề cập).
- **Task Quote:** 5.0/5 — Các trích dẫn cho từng nhiệm vụ hoàn toàn khớp với lời nói thực tế trong bản ghi cuộc họp, không có bất kỳ sai lệch nào.

> Phân tích cuộc họp này có chất lượng rất cao. Phần tóm tắt cô đọng nhưng đầy đủ, nắm bắt được các điểm cốt lõi. Việc trích xuất và phân công nhiệm vụ là hoàn hảo, với các trích dẫn chính xác. Đây là một bản phân tích xuất sắc.

---

### ES2013b — 🎤+📄 Both
- Thời lượng: 35.5 phút | ASR: 5312.6s | Slides: 0.0s | Gemini: 5.7s
- WER: 28.16%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 4.0/5 — Tóm tắt đã nắm bắt được hầu hết các chủ đề chính và quyết định quan trọng của cuộc họp, bao gồm mục đích cuộc họp, các bài thuyết trình về nghiên cứu thị trường, chức năng kỹ thuật, thiết kế, các yêu cầu dự án mới và các nhiệm vụ được giao. Tuy nhiên, nó đã bỏ l lỡ một số chi tiết quan trọng như giới hạn chi phí 12.50 Euro cho thiết bị, thảo luận về việc sản xuất hàng loạt/dùng một lần so với khả năng sửa chữa, và cuộc thảo luận về nhóm đối tượng mục tiêu (người dùng sớm so với nhà sản xuất). Những chi tiết này có ảnh hưởng đáng kể đến thiết kế và chiến lược.
- **Summary Accuracy:** 5.0/5 — Tóm tắt hoàn toàn chính xác về mặt thông tin. Không có bất kỳ thông tin nào bịa đặt hoặc sai lệch so với bản ghi cuộc họp và văn bản slide.
- **Task Completeness:** 5.0/5 — Tất cả các mục hành động và nhiệm vụ được giao đã được trích xuất đầy đủ từ bản ghi và slide. Mặc dù có một nhiệm vụ bị gán sai người, nhưng bản thân nhiệm vụ đó vẫn được ghi nhận.
- **Task Assignment:** 4.0/5 — Hầu hết các nhiệm vụ đã được gán cho đúng người. Tuy nhiên, có một lỗi trong việc gán nhiệm vụ: nhiệm vụ "Do research on the cost of rechargeable internal batteries" (Nghiên cứu chi phí pin sạc bên trong) đã được Kate tự nguyện nhận làm, nhưng lại bị gán cho Florence trong bản phân tích. Các nhiệm vụ còn lại đều được gán chính xác.
- **Task Quote:** 5.0/5 — Tất cả các trích dẫn nguyên văn cho các nhiệm vụ đều khớp chính xác với lời nói trong bản ghi cuộc họp. Không có sự sai lệch nào.

> Bản phân tích cuộc họp có chất lượng tốt. Phần tóm tắt cung cấp một cái nhìn tổng quan toàn diện về các chủ đề chính và quyết định, mặc dù có thể cải thiện bằng cách bao gồm các ràng buộc về chi phí và các cuộc thảo luận chiến lược quan trọng khác. Việc trích xuất nhiệm vụ rất đầy đủ, nhưng cần chú ý hơn đến độ chính xác trong việc gán nhiệm vụ để tránh nhầm lẫn. Các trích dẫn nguyên văn là hoàn hảo.

---

### ES2013c — 🎤+📄 Both
- Thời lượng: 39.3 phút | ASR: 504.5s | Slides: 0.0s | Gemini: 15.1s
- WER: 37.28%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 4.5/5 — Tóm tắt đã nắm bắt hầu hết các quyết định chính và các chủ đề lớn của cuộc họp, bao gồm việc xem xét biên bản cuộc họp trước, các bài thuyết trình của Sarah, Kate, Steph và các quyết định cuối cùng về năng lượng, vỏ, giao diện. Tuy nhiên, một số chi tiết nhỏ từ cuộc họp trước như chi phí 12.5 pence cho thiết bị sản xuất hàng loạt đơn giản, yêu cầu "chỉ dành cho TV" và "khẩu hiệu/màu sắc của thiết kế công ty" đã không được nêu bật rõ ràng trong phần tóm tắt các điểm đã thống nhất từ cuộc họp trước.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin được trình bày trong phần tóm tắt đều chính xác và có thể tìm thấy trong bản ghi cuộc họp. Không có thông tin nào bịa đặt hoặc sai lệch.
- **Task Completeness:** 5.0/5 — Tất cả các mục hành động chính, cả từ cuộc họp trước được xem xét và các mục mới được giao ở cuối cuộc họp, đều đã được trích xuất đầy đủ. Bao gồm cả nhiệm vụ cần chuyển giao cho nhóm khác và nhiệm vụ của Kate về việc kiểm tra lại với nhà sản xuất.
- **Task Assignment:** 5.0/5 — Tất cả các nhiệm vụ đều được giao cho đúng người hoặc nhóm người chịu trách nhiệm, bao gồm cả nhiệm vụ được giao cho "Unassigned" (chuyển cho nhóm khác).
- **Task Quote:** 5.0/5 — Tất cả các trích dẫn cho các nhiệm vụ đều khớp chính xác với lời nói trong bản ghi cuộc họp.

> Bản phân tích cuộc họp này có chất lượng rất cao. Phần tóm tắt đầy đủ và chính xác, nắm bắt được các điểm thảo luận và quyết định quan trọng. Việc trích xuất và phân công nhiệm vụ được thực hiện một cách hoàn hảo, với độ chính xác cao về cả nội dung và người thực hiện, cũng như các trích dẫn nguyên văn. Đây là một bản phân tích rất hữu ích và đáng tin cậy.

---

### ES2013d — 🎤+📄 Both
- Thời lượng: 31.6 phút | ASR: 397.6s | Slides: 0.0s | Gemini: 21.6s
- WER: 28.63%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 5.0/5 — Tóm tắt đã nắm bắt đầy đủ tất cả các quyết định quan trọng và các chủ đề chính được thảo luận trong cuộc họp. Nó bao gồm việc xem xét biên bản cuộc họp trước, trình bày nguyên mẫu, tiêu chí đánh giá, khía cạnh tài chính và đánh giá quy trình dự án.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong phần tóm tắt đều chính xác 100% và được lấy trực tiếp từ bản ghi cuộc họp và văn bản slide. Không có thông tin nào bịa đặt hay sai lệch.
- **Task Completeness:** 4.5/5 — Hầu hết các mục hành động đã được trích xuất. Tuy nhiên, có một nhiệm vụ nhỏ ở cuối cuộc họp là 'save everything' (lưu mọi thứ) mà Florence đã đề cập, nhưng nó không được đưa vào danh sách nhiệm vụ. Đây là một thiếu sót nhỏ và không ảnh hưởng đáng kể đến chất lượng tổng thể.
- **Task Assignment:** 5.0/5 — Tất cả các nhiệm vụ đã được gán cho đúng người hoặc được đánh dấu là 'Unassigned' một cách chính xác khi không có người cụ thể nào được chỉ định trong bản ghi.
- **Task Quote:** 5.0/5 — Các trích dẫn nguyên văn cho từng nhiệm vụ hoàn toàn khớp với những lời nói thực tế trong bản ghi cuộc họp.

> Bản phân tích cuộc họp được tạo ra có chất lượng rất cao. Phần tóm tắt đầy đủ và chính xác, bao gồm tất cả các điểm thảo luận và quyết định quan trọng. Các nhiệm vụ được trích xuất tốt và được gán vai trò chính xác. Các trích dẫn cũng hoàn toàn khớp với bản ghi. Chỉ có một nhiệm vụ nhỏ bị bỏ sót, nhưng điều này không làm giảm đáng kể chất lượng tổng thể của phân tích.

---

### ES2014a — 🎤 Audio Only
- Thời lượng: 19.2 phút | ASR: 223.4s | Slides: 0.0s | Gemini: 11.2s
- WER: 34.90%

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 4.5/5 — Bản tóm tắt đã nắm bắt được hầu hết các quyết định và chủ đề chính của cuộc họp, bao gồm mục tiêu dự án, các giai đoạn thiết kế, mục tiêu tài chính (giá bán, chi phí sản xuất), các yêu cầu của người dùng đối với thiết bị điều khiển từ xa và quyết định ban đầu về việc tập trung vào điều khiển TV. Tuy nhiên, nó bỏ qua một hoạt động nhỏ là vẽ trên bảng trắng (whiteboard), vốn là một phần của việc làm quen và kiểm tra công cụ, mặc dù đây không phải là một quyết định cốt lõi của dự án.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong bản tóm tắt đều chính xác và được trích xuất trực tiếp từ bản ghi cuộc họp. Không có thông tin nào bị thêm vào hoặc bịa đặt.
- **Task Completeness:** 5.0/5 — Chỉ có một nhiệm vụ rõ ràng được giao trong cuộc họp là người quản lý sẽ chuẩn bị biên bản cuộc họp. Nhiệm vụ này đã được trích xuất đầy đủ và chính xác. Các hoạt động khác như 'thiết kế' là mô tả công việc chung chứ không phải nhiệm vụ cụ thể với người được giao.
- **Task Assignment:** 5.0/5 — Nhiệm vụ 'viết biên bản cuộc họp' đã được gán chính xác cho 'manager' (người quản lý), dựa trên lời nói của người nói trong bản ghi ('And I guess I'll try and write up some minutes of this meeting...').
- **Task Quote:** 5.0/5 — Trích dẫn cho nhiệm vụ ('And I guess I'll try and write up some minutes of this meeting to give it to you for the next meeting.') hoàn toàn khớp với lời nói trong bản ghi.

> Bản phân tích cuộc họp này có chất lượng rất tốt. Phần tóm tắt đầy đủ, chính xác và nắm bắt được các điểm mấu chốt của cuộc họp. Việc trích xuất và gán nhiệm vụ cũng hoàn hảo, với trích dẫn chính xác. Cần lưu ý rằng hoạt động vẽ trên bảng trắng có thể được bỏ qua trong tóm tắt vì nó không phải là một quyết định quan trọng của dự án.

---

### ES2014b — 🎤+📄 Both
- Thời lượng: 38.7 phút | ASR: 582.5s | Slides: 0.0s | Gemini: 15.5s
- WER: 32.30%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 4.5/5 — Tóm tắt đã nắm bắt được hầu hết các quyết định và chủ đề chính của cuộc họp, bao gồm các yêu cầu dự án mới, các bài thuyết trình về thiết kế và nghiên cứu thị trường, cũng như các quyết định quan trọng về chức năng điều khiển từ xa (bỏ nút teletext, 10 nút số, chức năng tìm điều khiển bị mất, các nút chức năng trước/sau). Tuy nhiên, nó thiếu một chi tiết nhỏ về việc cần có hướng dẫn sử dụng tốt hơn cho các chức năng menu.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong phần tóm tắt đều chính xác và được trích xuất trực tiếp từ bản ghi cuộc họp. Không có thông tin nào bịa đặt hay sai lệch.
- **Task Completeness:** 5.0/5 — Tất cả các mục hành động được đề cập trong bản ghi cuộc họp đều đã được trích xuất đầy đủ. Bao gồm việc ghi biên bản cuộc họp, lập danh sách các nút chức năng trước/sau, đảm bảo sự rõ ràng về nhiệm vụ cho cuộc họp tiếp theo và việc truyền đạt thông tin bổ sung qua email.
- **Task Assignment:** 5.0/5 — Các nhiệm vụ đã được phân công chính xác. Nhiệm vụ ghi biên bản được giao cho 'Project Manager' và các nhiệm vụ chung khác không được chỉ định cụ thể cho một cá nhân nào đã được gán cho 'Unassigned', điều này là hợp lý.
- **Task Quote:** 5.0/5 — Tất cả các trích dẫn nguyên văn cho các nhiệm vụ đều khớp hoàn hảo với lời nói thực tế trong bản ghi cuộc họp.

> Phân tích cuộc họp này có chất lượng rất cao. Phần tóm tắt đầy đủ và chính xác, nắm bắt được các điểm mấu chốt của cuộc thảo luận. Việc trích xuất nhiệm vụ hoàn chỉnh, phân công chính xác và các trích dẫn nguyên văn hoàn toàn khớp với bản ghi. Đây là một bản phân tích xuất sắc.

---

### ES2014c — 🎤+📄 Both
- Thời lượng: 37.9 phút | ASR: 585.0s | Slides: 0.0s | Gemini: 15.1s
- WER: 30.64%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 4.5/5 — Bản tóm tắt đã nắm bắt được hầu hết các quyết định chính và các chủ đề quan trọng được thảo luận trong cuộc họp. Nó bao gồm các quyết định về nguồn điện (động năng), nút bấm (cao su đơn giản), bảng mạch (đơn giản), chức năng nhận dạng giọng nói (chức năng tìm kiếm), thiết kế vỏ (cong đơn, cao su, cảm giác mềm mại), và nút chờ (hình quả táo). Tuy nhiên, nó không đề cập rõ ràng đến việc từ chối các nút cuộn và các trường hợp có thể thay đổi, mặc dù những điều này được ngụ ý trong các quyết định khác.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong bản tóm tắt đều chính xác và được lấy trực tiếp từ bản ghi cuộc họp. Không có thông tin nào bịa đặt hoặc không có trong nguồn.
- **Task Completeness:** 4.0/5 — Hầu hết các mục hành động đã được trích xuất. Các nhiệm vụ như tìm hiểu chi phí nhận dạng giọng nói, giữ cho các nút đơn giản, sắp xếp mọi thứ và thực hiện nhiệm vụ tạo mô hình bằng đất sét đều được ghi lại. Tuy nhiên, một nhiệm vụ cụ thể là 'tìm hiểu độ dẻo của đất sét' (find out how pliable is plasticine) đã bị bỏ sót, mặc dù nhiệm vụ chung về 'nhiệm vụ đất sét' đã được đề cập.
- **Task Assignment:** 5.0/5 — Tất cả các nhiệm vụ đều được gán chính xác cho 'Unassigned' (Chưa được gán) vì bản ghi cuộc họp không chỉ định tên cụ thể cho bất kỳ nhiệm vụ nào. Việc gán cho 'Unassigned' là phù hợp trong trường hợp này.
- **Task Quote:** 5.0/5 — Tất cả các trích dẫn được cung cấp cho các nhiệm vụ đều khớp chính xác với lời nói thực tế trong bản ghi cuộc họp.

> Bản phân tích cuộc họp này có chất lượng tốt. Phần tóm tắt rất toàn diện và chính xác, nắm bắt được các quyết định cốt lõi. Việc trích xuất nhiệm vụ cũng khá tốt, mặc dù có thể cải thiện một chút bằng cách nắm bắt các nhiệm vụ phụ hoặc nhiệm vụ tìm kiếm thông tin cụ thể hơn. Độ chính xác của việc gán nhiệm vụ và trích dẫn là hoàn hảo. Nhìn chung, đây là một bản phân tích hữu ích và đáng tin cậy.

---

### ❌ ES2014d
> Lỗi: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}

---

### ES2015a — 🎤+📄 Both
- Thời lượng: 19.1 phút | ASR: 203.0s | Slides: 0.0s | Gemini: 19.1s
- WER: 25.24%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 4.0/5 — Tóm tắt đã nắm bắt được hầu hết các quyết định chính và chủ đề lớn của cuộc họp, bao gồm giới thiệu nhóm, mục tiêu sản phẩm, phương pháp làm việc, buổi đào tạo công cụ và các ý tưởng ban đầu. Tuy nhiên, nó đã bỏ lỡ mục tiêu lợi nhuận cụ thể là 50 triệu euro và một số chi tiết cụ thể về tính thân thiện với người dùng (ví dụ: cho người khó nhìn số, thiết kế công thái học) cũng như nhấn mạnh vào 'phong cách mới' để thu hút thế hệ trẻ.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin được trình bày trong phần tóm tắt đều chính xác và có nguồn gốc trực tiếp từ bản ghi cuộc họp và văn bản slide. Không có thông tin nào bịa đặt hay sai lệch.
- **Task Completeness:** 4.5/5 — Phần lớn các mục hành động đã được trích xuất đầy đủ. Các nhiệm vụ cho Poppy, Tara, Genevieve và các nhiệm vụ chung ('Unassigned') đều được ghi lại. Các nhiệm vụ của Heather như ghi biên bản, lập kế hoạch dự án và thảo luận mục tiêu cũng được đề cập. Chỉ có một nhiệm vụ của Heather bị hiểu sai ngữ cảnh, nhưng không phải là bỏ sót hoàn toàn một nhiệm vụ.
- **Task Assignment:** 3.5/5 — Việc phân công nhiệm vụ cho Poppy, Tara, Genevieve và các nhiệm vụ chung là chính xác. Tuy nhiên, nhiệm vụ cuối cùng của Heather là 'Send specific instructions to you by your personal coach.' đã bị gán sai. Câu trích dẫn này từ slide là một hướng dẫn chung cho các thành viên trong nhóm (ID, UID, ME) rằng họ sẽ nhận được hướng dẫn từ huấn luyện viên cá nhân của họ, chứ không phải là nhiệm vụ mà Heather (Quản lý dự án) phải thực hiện hoặc gửi đi.
- **Task Quote:** 5.0/5 — Tất cả các trích dẫn được cung cấp cho các nhiệm vụ đều khớp chính xác từng từ với bản ghi cuộc họp hoặc văn bản slide. Ngay cả đối với nhiệm vụ bị gán sai cho Heather, câu trích dẫn vẫn đúng nguyên văn từ slide. Vấn đề nằm ở việc giải thích và gán nhiệm vụ, chứ không phải ở độ chính xác của câu trích dẫn.

> Bản phân tích cuộc họp có chất lượng tốt. Phần tóm tắt cung cấp cái nhìn tổng quan toàn diện và chính xác về cuộc họp, mặc dù có thể bổ sung thêm một vài chi tiết cụ thể. Việc trích xuất nhiệm vụ khá đầy đủ, nhưng có một lỗi đáng chú ý trong việc gán nhiệm vụ cho Heather, cho thấy sự hiểu sai ngữ cảnh của một hướng dẫn chung. Độ chính xác của các trích dẫn là hoàn hảo.

---

### ES2015b — 🎤+📄 Both
- Thời lượng: 38.2 phút | ASR: 467.5s | Slides: 0.0s | Gemini: 20.5s
- WER: 31.04%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 5.0/5 — Bản tóm tắt đã nắm bắt đầy đủ tất cả các điểm chính và quyết định quan trọng trong cuộc họp. Nó bao gồm các ý tưởng từ bài thuyết trình của Poppy (khả năng hiển thị trong bóng tối, hệ thống báo động, vật liệu thông minh), đề xuất của Tara về điều khiển từ xa một chức năng, kết quả nghiên cứu thị trường của Genevieve (thực trạng, mong muốn của người dùng, các tính năng tiềm năng như nhận dạng giọng nói và màn hình LCD), các quyết định từ ban quản lý (chỉ dành cho TV, loại bỏ Teletext, tích hợp logo/màu sắc công ty), và các quyết định cuối cùng của nhóm (loại bỏ LCD/nhận dạng giọng nói, triển khai hệ thống báo động, nút bấm phát sáng theo thời gian, số nổi, mặt nạ có thể thay đổi). Các điểm cần nghiên cứu thêm cũng được đề cập.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong bản tóm tắt đều chính xác và được rút ra trực tiếp từ bản ghi cuộc họp và văn bản slide. Không có thông tin nào bịa đặt hay sai lệch.
- **Task Completeness:** 5.0/5 — Bản phân tích đã trích xuất đầy đủ tất cả các mục hành động được đề cập trong cuộc họp. Cụ thể là hai nhiệm vụ cho Poppy và một nhiệm vụ cần được quyết định về logo/màu sắc của công ty.
- **Task Assignment:** 5.0/5 — Các nhiệm vụ đã được giao chính xác cho đúng người. Nhiệm vụ điều tra tài chính về hợp kim nhớ hình dạng và kết nối phổ quát cho thiết bị báo động được giao cho Poppy. Nhiệm vụ quyết định màu sắc và logo của công ty được đặt là 'Unassigned' (chưa được giao), điều này phản ánh đúng tình hình trong cuộc họp khi không có người cụ thể nào được chỉ định cho nhiệm vụ này.
- **Task Quote:** 5.0/5 — Các trích dẫn cho từng nhiệm vụ đều khớp chính xác với lời nói trong bản ghi cuộc họp. Không có sự thay đổi hay sai lệch nào trong các câu trích dẫn.

> Bản phân tích cuộc họp này có chất lượng rất cao. Tóm tắt đầy đủ, chính xác, nắm bắt được tất cả các điểm thảo luận và quyết định quan trọng. Các nhiệm vụ được trích xuất một cách toàn diện, phân công đúng người và các trích dẫn cũng hoàn toàn chính xác. Đây là một bản phân tích rất hữu ích và đáng tin cậy.

---

### ES2015c — 🎤+📄 Both
- Thời lượng: 35.6 phút | ASR: 494.6s | Slides: 0.0s | Gemini: 29.6s
- WER: 23.36%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 5.0/5 — Bản tóm tắt đã nắm bắt đầy đủ tất cả các quyết định chính và các chủ đề quan trọng được thảo luận trong cuộc họp, bao gồm các bài thuyết trình về linh kiện, giao diện người dùng, xu hướng thời trang, cũng như các quyết định về nguồn năng lượng, chip, vỏ điều khiển, giao diện và chủ đề thiết kế.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong bản tóm tắt đều chính xác và không có bất kỳ thông tin nào bịa đặt hoặc sai lệch so với bản ghi cuộc họp gốc.
- **Task Completeness:** 4.5/5 — Hầu hết các mục hành động đã được trích xuất. Các nhiệm vụ được giao cho Poppy và Tara, cũng như các nhiệm vụ chưa được giao (đánh giá sản phẩm, nhận hướng dẫn cụ thể, phát triển thiết kế chủ đề rau củ quả, đưa ra 5 ý tưởng vỏ điều khiển) đều được ghi nhận. Tuy nhiên, việc 'stick to the veggie theme' (tuân thủ chủ đề rau củ quả) là một quyết định/hướng dẫn thiết kế hơn là một nhiệm vụ riêng biệt, và việc 'reconvene in 30 minutes' (họp lại sau 30 phút) là một chi tiết hậu cần của cuộc họp chứ không phải một nhiệm vụ cụ thể cho cá nhân hay nhóm.
- **Task Assignment:** 5.0/5 — Các nhiệm vụ đã được phân công chính xác cho đúng người (Poppy, Tara) hoặc được đánh dấu là 'Unassigned' (chưa được giao) một cách phù hợp, vì bản ghi không chỉ định rõ người thực hiện cho các nhiệm vụ đó.
- **Task Quote:** 3.5/5 — Các trích dẫn lời nói khớp chính xác với bản ghi. Tuy nhiên, có 3 trong số 8 nhiệm vụ bị thiếu thông tin về slide liên quan (được đánh dấu là `null`), trong khi các slide tương ứng đang hiển thị trong bản ghi. Ngoài ra, một số trích dẫn không phải là câu lệnh giao việc trực tiếp mà là các câu hỏi hoặc tuyên bố đồng ý/quyết định, từ đó nhiệm vụ được suy ra. Điều này làm giảm tính chính xác của việc liên kết trực tiếp giữa trích dẫn và nhiệm vụ.

> Bản phân tích cuộc họp này có chất lượng tốt. Tóm tắt và phân công nhiệm vụ rất đầy đủ và chính xác. Điểm cần cải thiện là việc cung cấp số slide chính xác cho tất cả các trích dẫn nhiệm vụ và đảm bảo rằng các trích dẫn nhiệm vụ phản ánh trực tiếp hơn các chỉ thị hành động.

---

### ES2015d — 🎤+📄 Both
- Thời lượng: 32.2 phút | ASR: 530.4s | Slides: 0.0s | Gemini: 18.0s
- WER: 34.26%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 5.0/5 — Bản tóm tắt đã nắm bắt đầy đủ tất cả các điểm chính của cuộc họp, bao gồm phần trình bày nguyên mẫu, quá trình đánh giá với điểm số cụ thể (1.9/7), xác nhận ngân sách (trong giới hạn 1220 euro), và các điểm chính từ đánh giá dự án như sự hài lòng về lãnh đạo và làm việc nhóm, cũng như nhu cầu về vật liệu tạo mẫu.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong bản tóm tắt đều chính xác và được lấy trực tiếp từ bản ghi cuộc họp. Không có thông tin nào bịa đặt hay sai lệch.
- **Task Completeness:** 5.0/5 — Tất cả các mục hành động và đề xuất quan trọng được thảo luận trong cuộc họp đều đã được trích xuất một cách đầy đủ. Các nhiệm vụ liên quan đến hệ thống nút 'plus', nghiên cứu RSI, thảo luận về logo/màu sắc với quản lý, và nhu cầu vật liệu tạo mẫu đều được ghi nhận.
- **Task Assignment:** 5.0/5 — Việc phân công nhiệm vụ rất chính xác. Nhiệm vụ liên quan đến chiến lược tiếp thị được giao cho Genevieve, người đã tự nhận mình là chuyên gia tiếp thị trong cuộc họp. Các nhiệm vụ còn lại được giao cho 'Unassigned', điều này phù hợp vì chúng là các mục hành động chung của nhóm mà không có người cụ thể nào được chỉ định rõ ràng trong bản ghi.
- **Task Quote:** 5.0/5 — Tất cả các trích dẫn được sử dụng cho các nhiệm vụ đều khớp chính xác với lời nói trong bản ghi cuộc họp. Không có sự sai lệch nào.

> Bản phân tích cuộc họp này có chất lượng rất cao. Tóm tắt đầy đủ, chính xác, và các nhiệm vụ được trích xuất một cách toàn diện, phân công đúng người và trích dẫn chính xác. Đây là một bản phân tích xuất sắc.

---

### ES2016a — 🎤 Audio Only
- Thời lượng: 23.1 phút | ASR: 244.1s | Slides: 0.0s | Gemini: 2.8s
- WER: 25.92%

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 5.0/5 — Bản tóm tắt đã nắm bắt đầy đủ tất cả các điểm chính của cuộc họp, bao gồm mục tiêu dự án, giới thiệu vai trò của các thành viên, các tính năng mong muốn cho điều khiển từ xa mới (phổ quát, bền, dễ tìm, hiện đại, độc đáo), các ý tưởng thiết kế được thảo luận (hình cầu, bàn phím, hình chữ nhật), những thách thức tiềm ẩn (ổn định, bản lề, nút bấm), và kết luận cuộc họp không có quyết định cuối cùng cùng với các nhiệm vụ được giao.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong bản tóm tắt đều chính xác và được trích xuất trực tiếp từ bản ghi cuộc họp. Không có thông tin nào bị sai lệch hoặc bịa đặt.
- **Task Completeness:** 5.0/5 — Tất cả các nhiệm vụ được giao trong cuộc họp đều đã được trích xuất đầy đủ. Cụ thể là nhiệm vụ cho Corinne Whiting (marketing) và hai nhiệm vụ cho Nick DeBusk (quản lý dự án).
- **Task Assignment:** 5.0/5 — Mỗi nhiệm vụ đều được gán chính xác cho người chịu trách nhiệm. Nhiệm vụ nghiên cứu thị trường được giao cho Corinne Whiting (chuyên gia marketing) và các nhiệm vụ liên quan đến việc chuẩn bị cuộc họp tiếp theo được giao cho Nick DeBusk (quản lý dự án).
- **Task Quote:** 5.0/5 — Các trích dẫn cho từng nhiệm vụ hoàn toàn khớp với lời nói trong bản ghi cuộc họp, không có bất kỳ sự thay đổi nào.

> Bản phân tích cuộc họp này có chất lượng rất cao. Tóm tắt đầy đủ, chính xác và các nhiệm vụ được trích xuất, phân công và trích dẫn một cách hoàn hảo. Đây là một bản phân tích mẫu mực.

---

### ❌ ES2016b
> Lỗi: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}}

---

### ES2016c — 🎤+📄 Both
- Thời lượng: 38.5 phút | ASR: 370.1s | Slides: 0.0s | Gemini: 16.2s
- WER: 25.98%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 5.0/5 — Bản tóm tắt đã nắm bắt đầy đủ tất cả các điểm chính của cuộc họp, bao gồm việc xem xét biên bản cuộc họp trước, các bài thuyết trình từ bộ phận Marketing, thiết kế giao diện người dùng và thiết kế công nghiệp, cũng như các quyết định quan trọng về nguồn năng lượng, vật liệu vỏ, giao diện người dùng và chip. Không có thông tin quan trọng nào bị bỏ lỡ.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong bản tóm tắt đều chính xác và được trích xuất trực tiếp từ bản ghi cuộc họp. Không có bất kỳ thông tin nào bị thêm vào hoặc sai lệch so với nguồn.
- **Task Completeness:** 5.0/5 — Tất cả các mục hành động được giao vào cuối cuộc họp đều đã được trích xuất đầy đủ. Các nhiệm vụ cho Ryan, Manuel, Karen và nhiệm vụ chung của Ryan và Manuel đều được ghi lại.
- **Task Assignment:** 5.0/5 — Mỗi nhiệm vụ đều được gán chính xác cho người hoặc nhóm người chịu trách nhiệm, đúng như đã nêu trong bản ghi cuộc họp.
- **Task Quote:** 5.0/5 — Các trích dẫn cho mỗi nhiệm vụ hoàn toàn khớp với lời nói thực tế trong bản ghi cuộc họp, không có sự thay đổi nào.

> Bản phân tích cuộc họp này có chất lượng rất cao. Tóm tắt đầy đủ, chính xác và bao quát tất cả các điểm thảo luận và quyết định quan trọng. Các nhiệm vụ được trích xuất hoàn chỉnh, gán đúng người và trích dẫn chính xác. Đây là một bản phân tích xuất sắc.

---

### ES2016d — 🎤+📄 Both
- Thời lượng: 25.4 phút | ASR: 248.0s | Slides: 0.0s | Gemini: 18.6s
- WER: 45.97%
- Slide Coverage: 100.0% (None trang)

*Định lượng: N/A (không có ground-truth analysis)*

**🤖 LLM Judge (Gemini):**
- **Summary Completeness:** 4.5/5 — Bản tóm tắt đã nắm bắt được hầu hết các chủ đề chính và quyết định quan trọng của cuộc họp, bao gồm việc xem xét biên bản cuộc họp trước, trình bày nguyên mẫu, đánh giá dựa trên các tiêu chí, thảo luận về ngân sách và điều chỉnh thiết kế để phù hợp với ngân sách, cũng như đánh giá quy trình dự án. Tuy nhiên, nó có thể chi tiết hơn một chút về các tiêu chí đánh giá cụ thể (ví dụ: sự đổi mới công nghệ, thời trang trong điện tử) và quyết định không sử dụng nhận dạng giọng nói đã được đưa ra trong cuộc họp trước.
- **Summary Accuracy:** 5.0/5 — Tất cả thông tin trong bản tóm tắt đều chính xác và có thể được xác minh từ bản ghi cuộc họp. Không có thông tin sai lệch hay bịa đặt nào được tìm thấy.
- **Task Completeness:** 5.0/5 — Tất cả các mục hành động rõ ràng được đề cập trong bản ghi đã được trích xuất đầy đủ. Các nhiệm vụ như hoàn thành biên bản cuộc họp cuối cùng, chuẩn bị bảng câu hỏi tiếp theo và kiểm tra với sếp chính về các bước tiếp theo đều được ghi nhận.
- **Task Assignment:** 5.0/5 — Các nhiệm vụ được giao cho 'Secretary' (Thư ký) là hoàn toàn chính xác. Người nói trong cuộc họp tự nhận mình sẽ thực hiện các nhiệm vụ này, và vai trò thư ký là phù hợp để xử lý các công việc hành chính và theo dõi này.
- **Task Quote:** 5.0/5 — Các trích dẫn nguyên văn cho từng nhiệm vụ đều khớp chính xác với lời nói trong bản ghi cuộc họp. Không có sự sai lệch nào được tìm thấy.

> Bản phân tích cuộc họp này có chất lượng rất cao. Tóm tắt đầy đủ, chính xác và các nhiệm vụ được trích xuất, phân công và trích dẫn một cách hoàn hảo. Đây là một bản phân tích xuất sắc.

---

