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

**Backend:** normalized TF-IDF

**Corpus:** 8 tài liệu, 19 chunks

| # | Query | Top-1 chunk | Score | Relevant | Câu trả lời Agent tóm tắt |
|---|---|---|---:|---|---|
| 1 | Hủy học phần đã đóng học phí để rút học phí trước khi nào? | `course-registration`: phần đóng học phí | 0.4669 | Có | Đúng tài liệu nhưng top-1 chưa nêu mốc 10 ngày; thông tin đúng có trong top-3. |
| 2 | Học bổng xuất sắc bằng bao nhiêu lần mức khá? | `scholarship-incentive`: điều kiện và mức học bổng | 0.3954 | Có | Đúng tài liệu nhưng top-1 mới nêu mức khá/giỏi; mức 1,5 lần có trong top-3. |
| 3 | Sinh viên mượn bao nhiêu tài liệu, bao lâu và gia hạn thế nào? | `library-services-student`: số lượng, thời hạn và gia hạn | 0.3908 | Có | Tối đa 3 tài liệu trong 10 ngày, gia hạn một lần thêm 10 ngày. |
| 4 | Đối tượng nào được giảm 70% học phí? | `tuition-exemption`: đối tượng giảm 70% | 0.2555 | Có | Sinh viên dân tộc thiểu số tại địa bàn đặc biệt khó khăn/khu vực III. |
| 5 | Khách ở lại qua đêm trong ký túc xá phải làm gì? | `dormitory-rules`: giờ giấc và khách | 0.4917 | Có | Khách phải đăng ký và làm đơn bảo lãnh trước. |

**Số query có tài liệu liên quan trong top-3:** 5 / 5.

Qua phân công chiến lược, mình nhận thấy SentenceChunker giữ câu trọn vẹn và dễ đọc, trong khi chunking theo heading có thể giữ cấu trúc mục tốt hơn đối với quy chế dài.

## Tự đánh giá

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận | 10 / 10 |
| Hoàn thiện code | 30 / 30 |
| Dự đoán similarity | 4 / 5 |
| Kết quả truy xuất | 8 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |
