# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đăng Đức  
**MSSV:** 2A202601787  
**Nhóm:** K3 — Dịch vụ/quy định đại học (cùng Vi Minh Hiển, Phạm Nguyễn Đăng Khôi, Đỗ Tuấn Sơn, Trần Đức Bảo Trung)  
**Ngày:** 03-08-2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

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
| 1 | Quy định nộp học phí trực tuyến | Hướng dẫn thanh toán tiền học qua ngân hàng | cao | 0.85 | Đúng |
| 2 | Quy định đăng ký môn học | Lịch thi kết thúc học phần | thấp | 0.32 | Đúng |
| 3 | Thủ tục xin cấp lại thẻ sinh viên | Hướng dẫn làm lại thẻ sinh viên bị mất | cao | 0.91 | Đúng |
| 4 | Điều kiện xét học bổng khuyến khích | Quy định về ký túc xá sinh viên | thấp | 0.18 | Đúng |
| 5 | Đăng ký phòng ở ký túc xá | Nộp tiền ở nội trú trường | cao | 0.78 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 1 và 5 cho thấy embedding phản ánh tốt ngữ nghĩa tương đồng mặc dù hai câu dùng từ ngữ khác nhau ("thanh toán tiền học qua ngân hàng" vs "nộp học phí trực tuyến"). Điều này khẳng định embeddings học biểu diễn không gian khái niệm thay vì chỉ khớp từ khóa đơn thuần.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Hạn nộp học phí học kỳ 1 khi nào? | Quy định học phí: Hạn chót đóng tiền là ngày 15/10. | 0.88 | Có | Hạn nộp học phí học kỳ 1 là ngày 15/10. |
| 2 | Điều kiện xin học bổng khuyến khích học tập? | Học bổng: Điểm Rèn luyện >= 80 và ĐTB học tập >= 3.2. | 0.84 | Có | Sinh viên cần có ĐTB >= 3.2 và ĐRL >= 80. |
| 3 | Thủ tục đăng ký ký túc xá như thế nào? | Ký túc xá: Đăng ký trực tuyến trên portal từ 01/08. | 0.81 | Có | Sinh viên đăng ký online qua portal từ ngày 01/08. |
| 4 | Thời gian mượn sách thư viện tối đa bao lâu? | Thư viện: Sinh viên được mượn tối đa 3 cuốn trong 14 ngày. | 0.86 | Có | Thời gian mượn tối đa là 14 ngày đối với 3 cuốn sách. |
| 5 | Làm sao để hủy môn học đã đăng ký? | Đăng ký môn: Hủy môn học trong 2 tuần đầu học kỳ. | 0.79 | Có | Sinh viên thực hiện hủy môn trên hệ thống trong 2 tuần đầu. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5** / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Việc kết hợp chiến lược chia nhỏ linh hoạt (RecursiveChunker) kết hợp với lọc Metadata (pre-filtering) giúp tăng rõ rệt độ chính xác khi truy xuất tài liệu trong các bài toán quy định phức tạp.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
