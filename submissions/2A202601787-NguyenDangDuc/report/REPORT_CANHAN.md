# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

> **Ghi chú kỹ thuật:** mục 4 và 5 chạy bằng `bench.py` với `RecursiveChunker()` (separator mặc định) trên 8 tài liệu thật của nhóm, backend TF-IDF thuần Python tự viết (không cần cài thêm thư viện, xem lớp `SimpleTfidfEmbedder` trong `bench.py`) — không dùng MockEmbedder nên số liệu phản ánh ngữ nghĩa thật.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:*

**Ví dụ có độ tương tự CAO:**
- Câu A:
- Câu B:
- Tại sao tương đồng:

**Ví dụ có độ tương tự THẤP:**
- Câu A:
- Câu B:
- Tại sao khác:

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** __ / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
<<<<<<< HEAD
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*
=======
| 1 | Sinh viên đăng ký học phần theo thời khóa biểu từng học kỳ. | Việc đăng ký môn học của sinh viên thực hiện theo lịch mỗi kỳ. | cao | 0.4345 | Đúng, nhưng thấp hơn kỳ vọng |
| 2 | Học bổng loại giỏi bằng 1,2 lần mức khá. | Mức học bổng loại giỏi cao hơn loại khá 1,2 lần. | cao | 0.8483 | Đúng |
| 3 | Ký túc xá cấm sinh viên đánh bài, cờ bạc. | Giảng viên phải dành 600 giờ mỗi năm cho nghiên cứu khoa học. | thấp | 0.0215 | Đúng |
| 4 | Hồ sơ miễn giảm học phí cần đơn đề nghị và giấy xác nhận. | Trang phục công sở phải gọn gàng, lịch sự. | thấp | 0.0000 | Đúng |
| 5 | Tài liệu thư viện của giảng viên phải trả đúng đợt thu hồi. | Giảng viên, cán bộ không được gia hạn tài liệu đã mượn. | cao | 0.2673 | Đúng, nhưng thấp hơn kỳ vọng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 1 và cặp 5 bất ngờ nhất: cả hai là paraphrase rõ ràng (cùng một ý, đổi cấu trúc câu) nhưng điểm chỉ 0.43 và 0.27 — thấp hơn nhiều so với cặp 2 (0.85, gần như trùng từ vựng). Lý do: `SimpleTfidfEmbedder` chỉ đếm từ trùng lặp (bag-of-words có trọng số IDF), không hiểu quan hệ đồng nghĩa ("đăng ký học phần" vs "đăng ký môn học", "trả đúng đợt thu hồi" vs "không được gia hạn" — cùng ý nhưng gần như không chung từ khóa). Điều này cho thấy TF-IDF nắm tốt sự trùng lặp bề mặt nhưng chưa biểu diễn được ngữ nghĩa sâu như embedding học sẵn (sentence-transformers) — đúng hạn chế đã biết của TF-IDF so với embedding ngữ nghĩa thật.
>>>>>>> origin/dangduc

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Thiết lập: `RecursiveChunker()` (separator mặc định) trên 8 tài liệu `data/k3_university/` → **17 chunk**. Backend: `SimpleTfidfEmbedder` (TF-IDF thuần Python, tự viết trong `bench.py`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
<<<<<<< HEAD
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*
=======
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu thư viện và trong bao lâu? *(filter `audience=student`)* | `library-services-student`: "tối đa 3 tài liệu trong thời hạn 10 ngày" | 0.5702 | Có (top-1) | Tối đa 3 tài liệu, thời hạn 10 ngày, gia hạn thêm 1 lần 10 ngày |
| 2 | Sinh viên cần đạt điều kiện gì để được xét học bổng khuyến khích học tập loại khá? | `scholarship-incentive`: "8 học kỳ chính, khá trở lên, không kỷ luật, ≥5/10, tín chỉ ≥ kế hoạch" | 0.6196 | Có (top-1) | Nêu đủ các điều kiện xét học bổng |
| 3 | Quy trình hủy một học phần đã đăng ký gồm những bước nào? | `course-registration`: "Thời gian đăng ký" (top-2 mới đúng đoạn quy trình hủy chi tiết, score 0.5171) | 0.5518 | Có (top-1, đúng tài liệu) | Agent dùng top-1 (mục thời gian đăng ký) — nội dung quy trình hủy đầy đủ hơn nằm ở top-2 cùng tài liệu |
| 4 | Ký túc xá cấm những hành vi nào? | `dormitory-rules` (top-1 = mục "Giờ giấc và khách", top-2 = mục "Xử lý vi phạm") — **đúng tài liệu nhưng chunk chứa danh sách hành vi cấm thật sự (mục "Hành vi bị cấm") không lọt vào top-3** | 0.3972 | Một phần — đúng `doc_id` nhưng thiếu đúng đoạn | Agent (dựa top-1) trả lời về giờ giấc/khách chứ chưa liệt kê được rượu bia, vũ khí, cờ bạc... — đây là **failure case cụ thể**: `RecursiveChunker` mặc định tách `dormitory-rules` thành nhiều mục nhỏ theo `##`, và với câu hỏi này 2/3 chunk lọt top-3 không phải mục cần thiết |
| 5 | Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không? | `library-services-faculty`: "tối đa 3 tài liệu trong 180 ngày, không áp dụng gia hạn" | 0.6829 | Có (top-1) | Không được gia hạn; phải trả đúng đợt thu hồi 25/6 và 25/12 |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** Theo `doc_id`: **5/5**. Nhưng xét đúng **nội dung** cần thiết thì câu 4 chưa đạt — chunk mang thông tin trả lời (danh sách hành vi cấm) không nằm trong top-3, dù đúng tài liệu. Câu 3 đúng tài liệu ở top-1 nhưng đoạn quy trình chi tiết nằm ở top-2 (agent vẫn nhìn thấy vì dùng top-3 làm context).

**Điều hay nhất tôi học được từ việc đối chiếu với các thành viên khác:**
> `RecursiveChunker` mặc định (separator ưu tiên đoạn/dòng trước câu) đôi khi tách một tài liệu thành nhiều chunk nhỏ theo từng mục (`##`), nên top-1 có thể đúng tài liệu nhưng chưa phải đoạn chứa câu trả lời chi tiết nhất (câu 3, câu 4) — trong khi các bạn dùng chunker ưu tiên ranh giới câu/mệnh đề (như cấu hình `RecursiveChunker(420, separator câu trước)` của Trần Đức Bảo Trung) cho top-1 trọn vẹn hơn. Đây là bằng chứng cụ thể cho thấy thứ tự separator quan trọng không kém việc chọn đúng loại chunker.
>>>>>>> origin/dangduc

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
<<<<<<< HEAD
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
=======
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 *(câu 4: đúng `doc_id` nhưng chunk mang nội dung cần thiết không lọt top-3 — xem failure case ở mục 5)* |
| **Tổng phần cá nhân** | **59 / 60** |
>>>>>>> origin/dangduc
