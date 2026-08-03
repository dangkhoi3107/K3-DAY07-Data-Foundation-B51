# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Nguyễn Đăng Khôi
**MSSV:** 2A202601243
**Nhóm:** K3 — Dịch vụ/quy định đại học (cùng Vi Minh Hiển, Nguyễn Đăng Đức, Đỗ Tuấn Sơn, Trần Đức Bảo Trung)
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding có góc giữa chúng gần 0°, tức là hướng biểu diễn gần giống nhau — không phụ thuộc độ dài (magnitude) của vector. Giá trị càng gần 1 thì mô hình càng coi hai đoạn text là "nói về cùng một điều".

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên đăng ký học phần theo lịch của từng học kỳ."
- Câu B: "Sinh viên đăng ký môn học theo thời khóa biểu mỗi kỳ."
- Tại sao tương đồng: cùng diễn đạt một ý (đăng ký môn học theo lịch mỗi kỳ), chỉ khác từ vựng bề mặt ("học phần"/"môn học", "lịch"/"thời khóa biểu").

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên được mượn tối đa 3 tài liệu trong 10 ngày."
- Câu B: "Hôm nay trời Hà Nội nhiều mây, có mưa rào."
- Tại sao khác: hai câu không cùng chủ đề, không chia sẻ khái niệm nào.

**Tại sao độ tương tự cosine được ưu tiên hơn khoảng cách Euclid cho text embeddings?**
> Cosine chỉ đo GÓC (hướng) giữa hai vector, không bị ảnh hưởng bởi ĐỘ DÀI vector. Với text embedding, độ dài vector phần lớn phản ánh độ dài/tần suất của văn bản (câu dài, câu ngắn) chứ không phải ý nghĩa; hai đoạn text cùng nghĩa nhưng độ dài khác nhau vẫn nên được coi là giống nhau. Euclidean distance bị "phạt" hai vector có magnitude khác nhau dù hướng giống hệt, nên dễ đánh giá sai các cặp câu cùng nghĩa nhưng khác độ dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: `ceil((length - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`
> Đáp án: **23 chunk.** Đã verify lại bằng code thật: `FixedSizeChunker(chunk_size=500, overlap=50).chunk("a"*10000)` → `len(...) == 23`.

**Nếu overlap tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Số chunk **tăng** lên 25 (verify bằng code: `FixedSizeChunker(chunk_size=500, overlap=100)` → 25 chunk). Lý do: bước nhảy mỗi lần (`step = chunk_size - overlap`) giảm từ 450 xuống 400 ký tự, nên cần nhiều bước hơn để duyệt hết văn bản. Overlap nhiều hơn giúp thông tin nằm ở ranh giới giữa 2 chunk không bị cắt cụt mất ngữ cảnh (nhiều khả năng xuất hiện trọn vẹn trong ít nhất 1 chunk), đổi lại tốn thêm dung lượng lưu trữ, thời gian embed, và có thể làm loãng kết quả retrieval vì nhiều chunk trùng nội dung nhau.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng `re.split` với pattern lookbehind `(?<=[.!?])\s+` để tách câu: chỉ tách tại khoảng trắng NGAY SAU dấu `.`/`!`/`?`, nhờ lookbehind nên dấu câu vẫn ở lại cuối câu trước thay vì bị mất. Edge case xử lý: text rỗng trả `[]` ngay; sau khi split thì `strip()` từng phần và loại bỏ chuỗi rỗng (do khoảng trắng thừa ở cuối văn bản mẫu sinh ra phần tử rỗng cuối cùng).

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Đệ quy thử lần lượt từng separator theo thứ tự ưu tiên (đoạn `\n\n` → dòng `\n` → câu `. ` → từ ` ` → ký tự `""`). Base case 1: text đã ngắn hơn `chunk_size` thì dừng, trả nguyên `[text]`. Base case 2: hết separator hoặc separator hiện tại là chuỗi rỗng thì cắt cứng theo `chunk_size`. Nếu separator hiện tại không xuất hiện trong text, gọi đệ quy tiếp với phần separator còn lại (giữ nguyên text) — bước này bắt buộc để đệ quy luôn tiến gần điều kiện dừng, tránh treo vòng lặp. Nếu separator có xuất hiện, split rồi gộp các phần liền kề tới sát `chunk_size`; phần nào tự nó đã dài hơn `chunk_size` thì đệ quy tiếp bằng separator ưu tiên thấp hơn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `_make_record` copy `dict(doc.metadata)` (không sửa object gốc của người gọi), đảm bảo có khóa `doc_id` (fallback về `doc.id` nếu metadata không có sẵn), sinh id record duy nhất bằng `f"{doc.id}::{self._next_index}"`. `add_documents` lặp qua từng doc, tạo record rồi mới tăng `_next_index`. `search` tính embedding của query một lần (`self._embedding_fn(query)`), rồi dùng dot product (`_dot`) so với embedding từng record trong helper dùng chung `_search_records` — vì `_mock_embed` đã chuẩn hoá vector về norm 1 nên dot product ở đây tương đương cosine similarity.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc metadata **trước**, rank **sau**: giữ lại record nào khớp MỌI cặp key/value trong `metadata_filter`, rồi mới gọi `_search_records` trên tập đã lọc. Làm ngược lại (rank top-k rồi mới lọc) có thể làm mất tài liệu đúng dù nó vẫn còn trong store. `search()` và `search_with_filter(metadata_filter=None)` dùng chung `_search_records` nên hai hàm cho kết quả khớp nhau khi không lọc. `delete_document` giữ lại mọi record có `metadata['doc_id'] != doc_id`, trả `True` nếu kích thước store giảm sau khi lọc.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Kiểm tra store rỗng trước để trả thông báo rõ ràng thay vì gọi LLM vô ích. Lấy `top_k` kết quả từ `store.search`, ghép nội dung thành context có **đánh số `[1] [2] ...`** kèm `doc_id` để truy vết nguồn khi debug. Prompt gồm 4 phần theo thứ tự: câu hướng dẫn chỉ dùng context (và nói rõ khi không đủ dữ liệu), khối `Context:`, `Question:`, và nhãn `Answer:` để LLM tiếp tục sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\CODE\MAIN\K3-DAY07-2A202601243-PhamNguyenDangKhoi-
plugins: anyio-4.14.2
collecting ... collected 42 items

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

============================= 42 passed in 0.06s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Dùng `_mock_embed` (MockEmbedder có sẵn trong repo) + `compute_similarity` đã implement, tính trên 5 cặp câu lấy từ corpus `data/k3_university/`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Sinh viên đăng ký học phần theo lịch của từng học kỳ." | "Sinh viên đăng ký môn học theo thời khóa biểu mỗi kỳ." (paraphrase) | cao | +0.1022 | Sai — thấp hơn nhiều so với kỳ vọng |
| 2 | "Ký túc xá cấm sinh viên uống rượu bia." | "Sinh viên không được uống rượu bia trong ký túc xá." (paraphrase) | cao | +0.0989 | Sai — thấp hơn nhiều so với kỳ vọng |
| 3 | "Sinh viên được mượn tối đa 3 tài liệu trong 10 ngày." | "Hôm nay trời Hà Nội nhiều mây, có mưa rào." (không liên quan) | thấp | −0.0765 | Đúng — thấp/âm như dự đoán |
| 4 | "Giảng viên có định mức giờ chuẩn giảng dạy 200-350 giờ mỗi năm." | "Cán bộ, viên chức phải mặc trang phục lịch sự khi làm việc." (cùng domain, khác chủ đề) | thấp | +0.2002 | Sai — cao hơn cả 2 cặp paraphrase ở trên |
| 5 | "Học bổng khuyến khích học tập xét theo điểm trung bình tích lũy." | (chính nó, lặp lại y hệt) | cao (=1) | +1.0000 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp 4: hai câu hoàn toàn khác chủ đề (giờ giảng dạy vs trang phục công sở, chỉ chung domain "quy định đại học") lại có điểm cao hơn cả hai cặp paraphrase thật sự cùng nghĩa (cặp 1, 2). Điều này cho thấy `_mock_embed` chỉ hash MD5 nội dung rồi sinh vector giả ngẫu nhiên theo seed đó — nó **không biểu diễn ngữ nghĩa thật**, độ tương đồng chỉ phản ánh sự trùng lặp ngẫu nhiên của hash chứ không phải ý nghĩa câu. Điểm số chỉ thật sự đáng tin khi hai chuỗi giống hệt nhau về mặt ký tự (dot product = 1, cặp 5). Đây đúng là giới hạn đề bài đã cảnh báo trước — muốn benchmark có ý nghĩa ngữ nghĩa thật cần chuyển sang `EMBEDDING_PROVIDER=local`.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy 5 câu hỏi đánh giá của nhóm bằng `bench.py` (strategy `FixedSizeChunker(chunk_size=300, overlap=60)`, backend `_mock_embed`, 29 chunk nạp vào store từ 8 tài liệu).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Score | Có liên quan không? | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên mượn tối đa bao nhiêu tài liệu thư viện, trong bao lâu? *(có filter `audience=student`)* | `scholarship-incentive` — sai tài liệu (gold: `library-services-student`) | 0.279 | Không (kể cả top-3) | Agent trả lời dựa trên context sai, không khớp gold answer |
| 2 | Điều kiện xét học bổng loại khá? | `library-services-student` — sai tài liệu (gold: `scholarship-incentive`) | 0.183 | Không (kể cả top-3) | Context sai chủ đề |
| 3 | Quy trình hủy học phần gồm bước nào? | `library-services-faculty` — sai (gold: `course-registration`), nhưng gold lọt **top-2** (score 0.148) | 0.191 (top-1) | **Có**, ở top-2 | Context top-1 sai, nhưng top-2 đúng vẫn nằm trong 3 chunk gửi cho LLM |
| 4 | Ký túc xá cấm hành vi nào? | `library-services-faculty` — sai tài liệu (gold: `dormitory-rules`) | 0.194 | Không (kể cả top-3) | Context sai chủ đề |
| 5 | Giảng viên/cán bộ có được gia hạn mượn sách không? | `course-registration` — sai (gold: `library-services-faculty`), nhưng gold lọt **top-3** (score 0.245) | 0.322 (top-1) | **Có**, ở top-3 | Context top-1/top-2 sai, top-3 đúng vẫn được đưa vào |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 2 / 5 (câu 3 và câu 5 — cả hai đều đúng ở vị trí top-2/top-3, không câu nào đúng ngay top-1).

**Ghi chú riêng:** câu 1 có dùng `metadata_filter={"audience": "student"}` — filter hoạt động đúng chức năng của nó (loại bỏ đúng 3 tài liệu `audience=faculty/staff`: `library-services-faculty`, `faculty-workload`, `staff-workplace-culture` khỏi tập ứng viên), nhưng trong 5 tài liệu `audience=student` còn lại, việc XẾP HẠNG bằng mock embedding vẫn vô nghĩa nên vẫn chọn sai top-1. Điều này minh hoạ đúng thông điệp của đề: **metadata filter và chất lượng embedding là hai việc độc lập** — filter đúng không đảm bảo rank đúng nếu embedding không mang ngữ nghĩa thật.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Điền sau khi nhóm demo và so sánh 5 strategy (CHECKPOINT 6) — chưa có dữ liệu tại thời điểm viết báo cáo này.*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
