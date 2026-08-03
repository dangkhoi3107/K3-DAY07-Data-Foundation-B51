# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Vi Minh Hiển

**MSSV:** 2A202601743

**Nhóm:** K3-B51

**Ngày:** 2026-08-03

## 1. Khởi động

### Độ tương tự cosine

Cosine similarity cao nghĩa là hai vector embedding có hướng gần nhau, thường cho thấy hai đoạn văn có nội dung hoặc ngữ nghĩa tương đồng.

- Ví dụ cao: “Sinh viên được mượn sách trong 10 ngày.” và “Thời hạn mượn tài liệu của sinh viên là 10 ngày.” Hai câu cùng nói về thời hạn mượn tài liệu.
- Ví dụ thấp: “Sinh viên đăng ký học phần trực tuyến.” và “Giảng viên dành 600 giờ cho nghiên cứu.” Hai câu thuộc hai chủ đề khác nhau.

Cosine similarity phù hợp với text embedding vì tập trung vào hướng của vector thay vì độ lớn; khoảng cách Euclid có thể bị ảnh hưởng bởi độ lớn vector dù nội dung vẫn tương tự.

### Bài toán chunking

Với `chunk_size=500`, `overlap=50`:

`ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23 chunks`.

Nếu tăng overlap lên 100:

`ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks`.

Overlap lớn hơn tạo nhiều chunk hơn nhưng giúp giữ ngữ cảnh ở ranh giới giữa hai chunk.

## 2. Hướng tiếp cận của tôi

### Chunking

`SentenceChunker` dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng sau dấu kết thúc câu, loại bỏ khoảng trắng thừa rồi nhóm tối đa ba câu. Chuỗi rỗng trả về danh sách rỗng.

`RecursiveChunker` thử lần lượt các separator ưu tiên. Đoạn đã đủ ngắn là base case; đoạn quá dài tiếp tục được chia bằng separator kế tiếp, cuối cùng cắt cứng theo `chunk_size`.

### EmbeddingStore

`add_documents` tạo embedding, metadata chuẩn hóa và ID lưu trữ duy nhất. `search` nhúng truy vấn, tính dot product với từng record, sắp xếp score giảm dần và lấy top-k.

`search_with_filter` lọc metadata trước khi xếp hạng. `delete_document` xóa tất cả record có cùng `metadata['doc_id']` và trả về trạng thái thành công.

### KnowledgeBaseAgent

Agent truy xuất top-k chunk, ghép chúng vào phần ngữ cảnh của prompt, thêm câu hỏi và yêu cầu chỉ trả lời dựa trên ngữ cảnh trước khi gọi `llm_fn`.

## 3. Hoàn thiện code

```text
.......................................... [100%]
42 passed, 1 warning in 0.11s
```

**Số lượng test vượt qua:** 42 / 42

## 4. Dự đoán độ tương tự

Lần chạy này dùng backend TF-IDF chuẩn hóa, tái lập được và không dùng mock ngẫu nhiên.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Sinh viên được mượn tối đa 3 tài liệu trong 10 ngày. | Thời hạn mượn sách của sinh viên là 10 ngày, tối đa 3 tài liệu. | Cao | 0.7400 | Có |
| 2 | Sinh viên xuất sắc nhận học bổng bằng 1,5 lần mức khá. | Mức học bổng loại xuất sắc cao gấp 1,5 lần loại khá. | Cao | 0.6091 | Có |
| 3 | Ký túc xá cấm sinh viên uống rượu bia trong phòng. | Sinh viên nội trú không được sử dụng đồ uống có cồn. | Cao | 0.1470 | Không |
| 4 | Sinh viên phải đăng ký học phần đúng thời hạn. | Giảng viên dành tối thiểu 600 giờ mỗi năm cho nghiên cứu khoa học. | Thấp | 0.0512 | Có |
| 5 | Sinh viên thuộc diện chính sách có thể được miễn học phí. | Điện thoại di động phải tắt trong cuộc họp. | Thấp | 0.0000 | Có |

Cặp 3 bất ngờ nhất vì hai câu gần nghĩa nhưng dùng ít từ giống nhau. Điều này cho thấy TF-IDF nắm bắt từ vựng tốt nhưng kém hơn embedding ngữ nghĩa khi gặp diễn đạt đồng nghĩa.

## 5. Kết quả truy xuất của tôi

**Strategy:** `SentenceChunker(max_sentences_per_chunk=3)`

**Backend:** normalized TF-IDF (tự viết, dependency-free)

**Corpus:** 8 tài liệu, 19 chunks

> Cập nhật: chạy lại bằng đúng **5 câu hỏi chung của nhóm** (`report/REPORT_NHOM.md` mục 3) thay cho bộ câu hỏi riêng ở bản nháp trước, để so sánh trực tiếp được với các thành viên khác trong bảng tổng hợp của nhóm.

| # | Query | Top-1 chunk | Score | Relevant | Câu trả lời Agent tóm tắt |
|---|---|---|---:|---|---|
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu thư viện và trong bao lâu? *(filter `audience=student`)* | `library-services-student`: số lượng, thời hạn, gia hạn, xử lý trễ hạn (gộp cả 3 mục vào 1 chunk) | 0.3531 | Có (top-1, đầy đủ) | Tối đa 3 tài liệu trong 10 ngày, gia hạn 1 lần thêm 10 ngày. |
| 2 | Sinh viên cần đạt điều kiện gì để được xét học bổng khuyến khích học tập loại khá? | `scholarship-incentive`: điều kiện xét + mức học bổng | 0.4777 | Có (top-1, đầy đủ) | Nêu đủ 5 điều kiện (8 học kỳ, khá trở lên, không kỷ luật, ≥5/10, tín chỉ ≥ kế hoạch). |
| 3 | Quy trình hủy một học phần đã đăng ký gồm những bước nào? | `course-registration`: mục "Thời gian đăng ký" (đúng tài liệu, nhưng chưa phải đoạn "Quy trình hủy học phần" chứa bước nộp phiếu) | 0.2781 | Có (top-1 đúng tài liệu; cả top-3 đều là `course-registration` nên đoạn quy trình chi tiết nằm trong top-3) | Agent (dựa top-1) trả lời về mốc thời gian, chưa nêu bước "nộp Phiếu đề nghị tại Phòng Quản lý đào tạo" |
| 4 | Ký túc xá cấm những hành vi nào? | `dormitory-rules`: mục "Hành vi bị cấm" + "Xử lý vi phạm" + "Quy định khác" (gộp 3 mục, 3 câu/chunk) | 0.2945 | Có (top-1, đầy đủ) | Liệt kê đúng và đủ toàn bộ hành vi bị cấm. |
| 5 | Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không? | `library-services-faculty`: số lượng/thời hạn + gia hạn + xử lý trễ hạn | 0.6231 | Có (top-1, đầy đủ) | Không được gia hạn; phải trả đúng đợt thu hồi 25/6 và 25/12. |

**Số query có tài liệu liên quan trong top-3:** 5 / 5. **Điểm truy xuất theo `docs/SCORING.md`:** 2+2+1+2+2 = **9/10** (chỉ câu 3 chưa trọn vẹn — đúng tài liệu ở top-1 nhưng chưa phải đúng đoạn quy trình).

**Nhận xét:** `SentenceChunker(max_sentences_per_chunk=3)` có xu hướng gộp 2-3 mục `##` liền kề vào 1 chunk (vì mỗi mục thường chỉ 1-2 câu) — đây là lý do câu 1, 4, 5 có câu trả lời đầy đủ ngay top-1 dù câu hỏi cần thông tin từ nhiều mục con. Ngược lại câu 3 bị tách vì "Thời gian đăng ký" và "Quy trình hủy học phần" đủ dài để thành 2 chunk riêng. Qua phân công chiến lược, mình nhận thấy SentenceChunker giữ câu trọn vẹn và dễ đọc, trong khi chunking theo heading (như Đỗ Tuấn Sơn) giữ đúng ranh giới mục hơn nên ít bị hiện tượng "gộp may rủi" như trên.

## Tự đánh giá

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận | 10 / 10 |
| Hoàn thiện code | 30 / 30 |
| Dự đoán similarity | 4 / 5 |
| Kết quả truy xuất | 9 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
