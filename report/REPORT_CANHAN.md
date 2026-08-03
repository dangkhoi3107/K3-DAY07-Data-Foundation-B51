# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Đức Bảo Trung

**MSSV:** 2A202601269

**Nhóm:** K3 — Dịch vụ/quy định đại học

**Ngày:** 03-08-2026

> Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) được tổng hợp riêng trong `REPORT_NHOM.md`.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Bài tập 1.1)

**Độ tương tự cosine cao nghĩa là gì?**

Hai vector embedding có cosine similarity cao khi chúng hướng gần giống nhau trong không gian vector. Điều này thường cho thấy hai văn bản gần nhau về chủ đề hoặc ý nghĩa, dù không nhất thiết dùng đúng cùng từ.

**Ví dụ có độ tương tự CAO:**

- Câu A: “Sinh viên được gia hạn tài liệu thư viện một lần.”
- Câu B: “Người học có thể gia hạn sách đã mượn thêm một lần.”
- Tại sao tương đồng: Cả hai đều nói về quyền gia hạn tài liệu của sinh viên.

**Ví dụ có độ tương tự THẤP:**

- Câu A: “Điều kiện xét học bổng khuyến khích học tập.”
- Câu B: “Các hành vi bị cấm trong ký túc xá.”
- Tại sao khác: Một câu thuộc chính sách học bổng, câu còn lại thuộc nội quy nơi ở.

**Tại sao cosine similarity được ưu tiên hơn khoảng cách Euclid cho text embeddings?**

Cosine tập trung vào hướng của vector nên ít bị ảnh hưởng bởi độ lớn vector hoặc độ dài văn bản. Khoảng cách Euclid có thể đánh giá hai vector cùng hướng là xa nhau chỉ vì độ lớn khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`:**

- Bước dịch: `500 - 50 = 450` ký tự.
- Số chunk: `ceil((10.000 - 50) / 450) = ceil(22,11) = 23`.
- **Đáp án: 23 chunks.**

**Nếu tăng overlap lên 100:**

- Bước dịch còn `500 - 100 = 400` ký tự.
- Số chunk: `ceil((10.000 - 100) / 400) = ceil(24,75) = 25`.
- Số chunk tăng từ 23 lên 25. Overlap lớn hơn giúp giữ lại ngữ cảnh nằm sát biên chunk, đổi lại tốn thêm lưu trữ và phép tính embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ

**`SentenceChunker.chunk`:**

Dùng regex `(?<=[.!?])(?:[ \t]+|\n+)` để tách tại khoảng trắng hoặc xuống dòng ngay sau dấu kết thúc câu, nhờ đó dấu câu vẫn thuộc câu đứng trước. Văn bản rỗng được trả về danh sách rỗng; các câu được `strip` rồi gom tối đa theo `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`:**

Thuật toán thử separator theo thứ tự ưu tiên và gom các phần nhỏ cho đến gần `chunk_size`. Nếu một phần vẫn quá dài, hàm tiếp tục đệ quy với separator kế tiếp; base case là đoạn đã đủ ngắn hoặc hết separator, khi đó cắt cứng theo số ký tự. Separator được gắn lại để không làm mất dấu câu và cấu trúc Markdown.

Chiến lược cá nhân dùng trong `bench.py` là `RecursiveChunker(chunk_size=420, separators=[". ", "; ", "\n\n", "\n", " ", ""])`. Cấu hình này khác Đức (separator mặc định, `chunk_size=500`): ưu tiên ranh giới câu và mệnh đề trước ranh giới dòng, giúp tránh tạo chunk chỉ có heading trong corpus Markdown.

### Lớp `EmbeddingStore`

**`add_documents` + `search`:**

Mỗi bản ghi trong bộ nhớ lưu `id`, `content`, bản sao `metadata` và embedding. Khi tìm kiếm, câu hỏi được nhúng bằng cùng `embedding_fn`, tính cosine similarity với từng bản ghi, sắp xếp điểm giảm dần và trả về tối đa `top_k` kết quả.

**`search_with_filter` + `delete_document`:**

Metadata được lọc trước khi tính similarity để giảm tập ứng viên và tránh trộn quy định của các đối tượng khác nhau. `delete_document` loại toàn bộ chunk có `metadata["doc_id"]` trùng mã tài liệu và trả về trạng thái có xóa được bản ghi hay không.

### Tác tử `KnowledgeBaseAgent.answer`

Agent truy xuất các chunk liên quan, ghép nội dung kèm `doc_id` vào phần ngữ cảnh và yêu cầu LLM chỉ trả lời dựa trên ngữ cảnh đó. Khi không có kết quả, agent trả về thông báo thiếu ngữ cảnh thay vì gọi LLM với prompt rỗng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết quả kiểm thử

Lệnh chạy:

```text
python -m pytest tests -v
```

Kết quả:

```text
collected 42 items

TestProjectStructure                         2 passed
TestClassBasedInterfaces                    2 passed
TestFixedSizeChunker                        7 passed
TestSentenceChunker                         4 passed
TestRecursiveChunker                        4 passed
TestEmbeddingStore                          8 passed
TestKnowledgeBaseAgent                      2 passed
TestComputeSimilarity                       4 passed
TestCompareChunkingStrategies               3 passed
TestEmbeddingStoreSearchWithFilter          3 passed
TestEmbeddingStoreDeleteDocument            3 passed

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua:** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Backend đo thực tế: embedding local nhẹ `HashingVectorizer` theo character n-gram 3–5, 4.096 chiều, chuẩn hóa L2. Backend này được chọn để benchmark nhanh, có thể tái lập và không dùng điểm ngẫu nhiên từ mock embedder.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Sinh viên được gia hạn tài liệu thư viện một lần. | Người học có thể gia hạn sách đã mượn thêm một lần. | Cao | 0,3334 | Đúng |
| 2 | Điều kiện xét học bổng khuyến khích học tập. | Các hành vi bị cấm trong ký túc xá. | Thấp | 0,0140 | Đúng |
| 3 | Thủ tục hủy học phần đã đăng ký. | Quy trình xóa môn học khỏi danh sách đăng ký. | Cao | 0,3247 | Đúng |
| 4 | Giảng viên phải trả tài liệu vào đợt thu hồi. | Sinh viên được miễn giảm học phí theo chính sách. | Thấp | 0,1771 | Đúng |
| 5 | Sinh viên được mượn tối đa ba tài liệu trong mười ngày. | Thời hạn mượn sách của người học là 10 ngày, tối đa 3 cuốn. | Cao | 0,3085 | Đúng |

**Kết quả bất ngờ nhất:**

Cặp 4 vẫn đạt 0,1771 dù khác chủ đề vì cùng chứa các từ thuộc miền đại học như “giảng viên”, “sinh viên” và “tài liệu/chính sách”. Điều này cũng chỉ ra giới hạn của embedding character n-gram: nó phản ánh chồng lấp từ vựng tốt nhưng chưa hiểu quan hệ ngữ nghĩa sâu bằng mô hình transformer đa ngôn ngữ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Thiết lập benchmark:

- Dữ liệu: 8 tài liệu trong `data/k3_university/`.
- Chunker: `RecursiveChunker(chunk_size=420, separators=[". ", "; ", "\n\n", "\n", " ", ""])`.
- Tổng số chunk: 24.
- Backend: local character n-gram hashing 4.096 chiều.

| # | Câu hỏi | Top-1 chunk truy xuất được (tóm tắt) | Score | Liên quan? | Câu trả lời Agent (tóm tắt từ top-3) |
|---|---|---|---:|---|---|
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu thư viện và trong bao lâu? | Quy định sinh viên: tối đa 3 tài liệu, thời hạn 10 ngày, gia hạn một lần. | 0,5402 | Có | Tối đa 3 tài liệu trong 10 ngày; mỗi tài liệu được gia hạn một lần thêm 10 ngày. |
| 2 | Điều kiện xét học bổng khuyến khích học tập loại khá? | Điều kiện: trong 8 học kỳ chính, học tập/rèn luyện từ khá, không bị kỷ luật, các học phần đạt từ 5/10. | 0,6515 | Có | Đủ các điều kiện học kỳ, xếp loại, kỷ luật, điểm học phần và số tín chỉ theo kế hoạch. |
| 3 | Quy trình hủy một học phần đã đăng ký gồm những bước nào? | Tài liệu đăng ký/hủy học phần; chunk chi tiết quy trình nằm top-2 và top-3. | 0,4737 | Có (đúng tài liệu; chi tiết ở top-2/3) | Nộp Phiếu đề nghị hủy đúng hạn tại Phòng Quản lý đào tạo; Phòng Tài chính hoàn học phí theo danh sách xác nhận. |
| 4 | Ký túc xá cấm những hành vi nào? | Cấm rượu bia, vũ khí/chất nổ/ma túy, nấu ăn hoặc sinh nhật trong phòng, cờ bạc, gây gổ và vượt rào. | 0,3396 | Có | Agent liệt kê đúng nhóm hành vi bị cấm từ nội quy ký túc xá. |
| 5 | Giảng viên/cán bộ có được gia hạn tài liệu mượn không? | Quy định giảng viên/cán bộ: tối đa 3 tài liệu trong 180 ngày; không áp dụng gia hạn. | 0,7266 | Có | Không được gia hạn; phải trả đúng các đợt thu hồi 25/6 và 25/12. |

**Số câu hỏi có gold document trong top-3:** **5 / 5**

**Nhận xét:**

Metadata filter ở câu 1 giới hạn `audience=student`, tránh lẫn quy định mượn 180 ngày của giảng viên/cán bộ. Cấu hình ưu tiên dấu kết thúc câu giúp giữ nhiều điều kiện trong một chunk; hạn chế còn lại là câu 3 có đúng tài liệu ở top-1 nhưng chi tiết quy trình phân bố ở top-2 và top-3.

**Điều học được từ việc đối chiếu kết quả trong nhóm:**

Không chỉ `chunk_size`, thứ tự separator cũng ảnh hưởng lớn đến độ mạch lạc của chunk Markdown. Với dữ liệu quy định có nhiều heading và dòng ngắn, ưu tiên ranh giới câu trước xuống dòng giảm chunk vụn; metadata pre-filter đặc biệt hữu ích khi hai tài liệu cùng chủ đề nhưng áp dụng cho đối tượng khác nhau.

---

## Tự đánh giá (Phần cá nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận | 10 / 10 |
| Hoàn thiện code | 30 / 30 |
| Dự đoán độ tương tự | 5 / 5 |
| Kết quả truy xuất | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
