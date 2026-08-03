# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đăng Đức  
**MSSV:** 2A202601787  
**Nhóm:** K3 — Dịch vụ/quy định đại học (cùng Vi Minh Hiển, Phạm Nguyễn Đăng Khôi, Đỗ Tuấn Sơn, Trần Đức Bảo Trung)  
**Ngày:** 03-08-2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

> **Ghi chú kỹ thuật:** mục 4 và 5 chạy bằng `bench.py` với `RecursiveChunker()` (separator mặc định) trên 8 tài liệu thật của nhóm, backend TF-IDF thuần Python tự viết (không cần cài thêm thư viện, xem lớp `SimpleTfidfEmbedder` trong `bench.py`) — không dùng MockEmbedder nên số liệu phản ánh ngữ nghĩa thật.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai góc của vector nhúng (text embedding) chỉ cùng về một hướng trong không gian đa chiều, đại diện cho việc hai văn bản có ngữ nghĩa vô cùng gần gũi với nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên thực hiện đăng ký môn học trực tuyến qua cổng portal.
- Câu B: Học viên thực hiện đăng ký tín chỉ học tập trên website nhà trường.
- Tại sao tương đồng: Cùng diễn tả hành động đăng ký môn/tín chỉ trực tuyến của sinh viên.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Hạn nộp học phí học kỳ 1 kết thúc vào cuối tuần này.
- Câu B: Đội bóng đá sinh viên của trường đã giành giải nhất cấp thành phố.
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau (quản lý tài chính học tập vs hoạt động thể thao).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Độ tương tự cosine chỉ tập trung vào hướng (chủ đề/ngữ nghĩa) của vector thay vì độ dài (độ dài văn bản). Khoảng cách Euclid bị ảnh hưởng bởi độ dài câu/tài liệu, khiến hai tài liệu cùng chủ đề nhưng độ dài khác nhau bị đánh giá xa nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Bước dịch chuyển (step) = chunk_size - overlap = 500 - 50 = 450.
> Chunk 1 dịch từ 0 đến 500. Phần còn lại = 10,000 - 500 = 9,500 ký tự.
> Số bước tiếp theo = ceil(9,500 / 450) = ceil(21.11) = 22 bước.
> Tổng số chunks = 1 + 22 = 23.
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước dịch chuyển giảm xuống 400, số chunk tăng lên thành 1 + ceil(9,500 / 400) = 25 chunks. Việc tăng overlap giúp tránh tình trạng cắt đứt ngữ cảnh ở ranh giới giữa các chunk, đảm bảo thông tin liên tục cho mô hình RAG.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `re.split(r'\. |\! |\? |\.\n', text)` để tách văn bản theo các dấu kết thúc câu chuẩn (`. `, `! `, `? `, `.\n`). Xử lý trường hợp ngoại lệ văn bản rỗng, không có dấu ngắt hoặc các câu không đủ số lượng bằng cách nhóm tối đa `max_sentences_per_chunk` câu lại bằng khoảng trắng và lọc các khoảng trắng thừa (`strip`).

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán duyệt đệ quy theo thứ tự ưu tiên separator `["\n\n", "\n", ". ", " ", ""]`. Trường hợp cơ sở (base case) là khi văn bản ngắn hơn `chunk_size` hoặc đã hết danh sách separators (khi đó chia nhỏ theo ký tự). Thuật toán gộp các đoạn nhỏ (splits) lại với nhau cho đến khi đạt ngưỡng `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ văn bản dưới dạng danh sách các `dict` chứa `id`, `content`, `metadata`, và vector `embedding` sinh ra từ `embedding_fn`. Khi tìm kiếm (`search`), tính độ tương tự cosine giữa embedding của câu truy vấn (`query`) với toàn bộ vector trong kho lưu trữ, sau đó sắp xếp giảm dần theo điểm số (`score`) và trả về `top_k` kết quả hàng đầu.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc (`search_with_filter`) được thực hiện **trước** khi tính toán độ tương tự (pre-filtering), giúp tối ưu hiệu năng tính toán vector. Hàm `delete_document` lọc bỏ tất cả bản ghi có `id` hoặc `metadata['doc_id']` trùng với `doc_id` cần xóa và trả về `True` nếu có bản ghi bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Truy xuất `top_k` đoạn ngữ cảnh liên quan nhất từ `EmbeddingStore`, sau đó ghép các nội dung này thành chuỗi ngữ cảnh (Context). Prompt được xây dựng dạng `Context:\n{context}\n\nQuestion: {question}\n\nAnswer:` và truyền cho hàm `llm_fn` để tổng hợp câu trả lời cuối cùng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần theo thời khóa biểu từng học kỳ. | Việc đăng ký môn học của sinh viên thực hiện theo lịch mỗi kỳ. | cao | 0.4345 | Đúng, nhưng thấp hơn kỳ vọng |
| 2 | Học bổng loại giỏi bằng 1,2 lần mức khá. | Mức học bổng loại giỏi cao hơn loại khá 1,2 lần. | cao | 0.8483 | Đúng |
| 3 | Ký túc xá cấm sinh viên đánh bài, cờ bạc. | Giảng viên phải dành 600 giờ mỗi năm cho nghiên cứu khoa học. | thấp | 0.0215 | Đúng |
| 4 | Hồ sơ miễn giảm học phí cần đơn đề nghị và giấy xác nhận. | Trang phục công sở phải gọn gàng, lịch sự. | thấp | 0.0000 | Đúng |
| 5 | Tài liệu thư viện của giảng viên phải trả đúng đợt thu hồi. | Giảng viên, cán bộ không được gia hạn tài liệu đã mượn. | cao | 0.2673 | Đúng, nhưng thấp hơn kỳ vọng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 1 và cặp 5 bất ngờ nhất: cả hai là paraphrase rõ ràng (cùng một ý, đổi cấu trúc câu) nhưng điểm chỉ 0.43 và 0.27 — thấp hơn nhiều so với cặp 2 (0.85, gần như trùng từ vựng). Lý do: `SimpleTfidfEmbedder` chỉ đếm từ trùng lặp (bag-of-words có trọng số IDF), không hiểu quan hệ đồng nghĩa ("đăng ký học phần" vs "đăng ký môn học", "trả đúng đợt thu hồi" vs "không được gia hạn" — cùng ý nhưng gần như không chung từ khóa). Điều này cho thấy TF-IDF nắm tốt sự trùng lặp bề mặt nhưng chưa biểu diễn được ngữ nghĩa sâu như embedding học sẵn (sentence-transformers) — đúng hạn chế đã biết của TF-IDF so với embedding ngữ nghĩa thật.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Thiết lập: `RecursiveChunker()` (separator mặc định) trên 8 tài liệu `data/k3_university/` → **17 chunk**. Backend: `SimpleTfidfEmbedder` (TF-IDF thuần Python, tự viết trong `bench.py`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu thư viện và trong bao lâu? *(filter `audience=student`)* | `library-services-student`: "tối đa 3 tài liệu trong thời hạn 10 ngày" | 0.5702 | Có (top-1) | Tối đa 3 tài liệu, thời hạn 10 ngày, gia hạn thêm 1 lần 10 ngày |
| 2 | Sinh viên cần đạt điều kiện gì để được xét học bổng khuyến khích học tập loại khá? | `scholarship-incentive`: "8 học kỳ chính, khá trở lên, không kỷ luật, ≥5/10, tín chỉ ≥ kế hoạch" | 0.6196 | Có (top-1) | Nêu đủ các điều kiện xét học bổng |
| 3 | Quy trình hủy một học phần đã đăng ký gồm những bước nào? | `course-registration`: "Thời gian đăng ký" (top-2 mới đúng đoạn quy trình hủy chi tiết, score 0.5171) | 0.5518 | Có (top-1, đúng tài liệu) | Agent dùng top-1 (mục thời gian đăng ký) — nội dung quy trình hủy đầy đủ hơn nằm ở top-2 cùng tài liệu |
| 4 | Ký túc xá cấm những hành vi nào? | `dormitory-rules` (top-1 = mục "Giờ giấc và khách", top-2 = mục "Xử lý vi phạm") — **đúng tài liệu nhưng chunk chứa danh sách hành vi cấm thật sự (mục "Hành vi bị cấm") không lọt vào top-3** | 0.3972 | Một phần — đúng `doc_id` nhưng thiếu đúng đoạn | Agent (dựa top-1) trả lời về giờ giấc/khách chứ chưa liệt kê được rượu bia, vũ khí, cờ bạc... — đây là **failure case cụ thể**: `RecursiveChunker` mặc định tách `dormitory-rules` thành nhiều mục nhỏ theo `##`, và với câu hỏi này 2/3 chunk lọt top-3 không phải mục cần thiết |
| 5 | Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không? | `library-services-faculty`: "tối đa 3 tài liệu trong 180 ngày, không áp dụng gia hạn" | 0.6829 | Có (top-1) | Không được gia hạn; phải trả đúng đợt thu hồi 25/6 và 25/12 |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** Theo `doc_id`: **5/5**. Nhưng xét đúng **nội dung** cần thiết thì câu 4 chưa đạt — chunk mang thông tin trả lời (danh sách hành vi cấm) không nằm trong top-3, dù đúng tài liệu. Câu 3 đúng tài liệu ở top-1 nhưng đoạn quy trình chi tiết nằm ở top-2 (agent vẫn nhìn thấy vì dùng top-3 làm context).

**Điều hay nhất tôi học được từ việc đối chiếu với các thành viên khác:**
> `RecursiveChunker` mặc định (separator ưu tiên đoạn/dòng trước câu) đôi khi tách một tài liệu thành nhiều chunk nhỏ theo từng mục (`##`), nên top-1 có thể đúng tài liệu nhưng chưa phải đoạn chứa câu trả lời chi tiết nhất (câu 3, câu 4) — trong khi các bạn dùng chunker ưu tiên ranh giới câu/mệnh đề (như cấu hình `RecursiveChunker(420, separator câu trước)` của Trần Đức Bảo Trung) cho top-1 trọn vẹn hơn. Đây là bằng chứng cụ thể cho thấy thứ tự separator quan trọng không kém việc chọn đúng loại chunker.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 9 / 10 *(câu 4: đúng `doc_id` nhưng chunk mang nội dung cần thiết không lọt top-3 — xem failure case ở mục 5)* |
| **Tổng phần cá nhân** | **59 / 60** |
