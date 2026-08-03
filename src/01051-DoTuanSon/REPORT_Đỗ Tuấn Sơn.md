# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đỗ Tuấn Sơn
**MSSV:** 2A202601051
**Nhóm:** K3 — B51 (repo: `DAY07-2A202601051-DoTuanSon`)
**Vai trò:** Chiến lược chunking heading/section (tự viết) · Hỗ trợ kiểm tra nguồn dữ liệu
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

> **Ghi chú kỹ thuật:** phần Dự đoán độ tương tự (mục 4) và Kết quả truy xuất (mục 5) được chạy với backend nhúng **local** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (`EMBEDDING_PROVIDER=local`) vì mock embeddings chỉ là hash md5, không phản ánh ngữ nghĩa. Toàn bộ 42 unit test (mục 3) vẫn chạy bằng mock như yêu cầu.

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding gần như cùng hướng trong không gian nhiều chiều (góc giữa chúng nhỏ, cosine gần 1). Về mặt ý nghĩa, hai đoạn văn bản nói về cùng chủ đề / cùng nội dung, dù dùng từ ngữ khác nhau.

**Ví dụ có độ tương tự CAO:** (đo thực tế = **0.694**)
- Câu A: "Sinh viên được mượn tối đa 3 tài liệu trong 10 ngày."
- Câu B: "Thời hạn mượn sách của sinh viên trong thư viện là bao lâu?"
- Tại sao tương đồng: cùng nói về việc mượn tài liệu thư viện của sinh viên (số lượng + thời hạn); embedding bắt được quan hệ hỏi–đáp dù câu B không lặp lại con số "3" hay "10 ngày".

**Ví dụ có độ tương tự THẤP:** (đo thực tế = **0.092**)
- Câu A: "Nội quy ký túc xá cấm sinh viên uống rượu, bia."
- Câu B: "Định mức giờ chuẩn giảng dạy của giảng viên mỗi năm."
- Tại sao khác: khác hẳn chủ đề (kỷ luật nội trú của sinh viên vs. khối lượng công việc giảng viên), gần như không chia sẻ khái niệm nào → vector gần vuông góc.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ quan tâm **hướng** của vector (ý nghĩa) chứ không quan tâm **độ dài** (magnitude), nên một câu ngắn và một đoạn dài cùng chủ đề vẫn được xem là giống nhau; ngoài ra embedding thường đã được chuẩn hóa L2 nên cosine tương đương tích vô hướng — tính nhanh và ổn định trong không gian nhiều chiều, nơi khoảng cách Euclid dễ bị "phình" và mất ý nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* mỗi chunk mới tiến thêm `step = chunk_size − overlap = 500 − 50 = 450` ký tự.
> Số chunk = `⌈(10000 − overlap) / step⌉ = ⌈(10000 − 50) / 450⌉ = ⌈9950 / 450⌉ = ⌈22.11⌉ = 23`.
> (Kiểm chứng theo code `FixedSizeChunker`: các vị trí bắt đầu 0, 450, 900, …, 9900 → đúng 23 chunk; chunk cuối `text[9900:10000]`.)
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> `step = 500 − 100 = 400` → số chunk = `⌈(10000 − 100)/400⌉ = ⌈9900/400⌉ = ⌈24.75⌉ = 25` chunks (nhiều hơn). Tăng overlap giúp giữ ngữ cảnh liền mạch qua ranh giới chunk: một câu/ý nằm vắt ngang hai chunk sẽ không bị cắt cụt, nên câu trả lời cho truy vấn ít bị mất thông tin — đổi lại tốn thêm bộ nhớ và số lần embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `re.split(r"(?<=[.!?])\s+", text)` — lookbehind để cắt **sau** dấu kết câu `.`, `!`, `?` khi theo sau là khoảng trắng, nên bao trọn cả `". "`, `"! "`, `"? "` và `".\n"` mà vẫn giữ dấu câu ở cuối câu. Edge case: text rỗng/chỉ có khoảng trắng → trả `[]`; các phần rỗng sau khi strip bị loại; `max_sentences_per_chunk` được ép `max(1, …)` để không bao giờ chia cho 0. Sau đó gom mỗi `max_sentences_per_chunk` câu thành một chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Đệ quy theo danh sách separator ưu tiên `["\n\n", "\n", ". ", " ", ""]` (đoạn văn → dòng → câu → từ → ký tự). `_split` cắt text theo separator hiện tại rồi **gộp tham lam** (greedy) các phần liền nhau lại tới sát `chunk_size`; phần nào vẫn quá dài thì đệ quy xuống separator kế tiếp. **Base case:** `len(text) <= chunk_size` → trả `[text]` (bỏ nếu rỗng); khi hết separator hoặc gặp `""` → cắt cứng theo kích thước. Cách này giữ ranh giới tự nhiên của văn bản càng lâu càng tốt.

**`HeadingChunker.chunk` — chiến lược tự viết (vai trò K3 của tôi):**
> Tài liệu quy định đại học được viết thành từng mục có tiêu đề Markdown (`#`, `##`, `###`). Tôi quét từng dòng, mở một section mới mỗi khi gặp dòng heading (regex `^#{1,3}\s+\S`), nên mỗi chunk là **một mục ngữ nghĩa trọn vẹn** (ví dụ toàn bộ mục "Số lượng và thời hạn mượn" hay "Xử lý trễ hạn") thay vì bị cắt giữa câu như FixedSize. Hai xử lý quan trọng: (1) section "chỉ có tiêu đề, không có nội dung" — như dòng `# Học bổng…` đứng ngay trước `## Điều kiện xét` — được **gộp vào section kế tiếp** để tránh sinh ra chunk rỗng nghĩa chỉ chứa vài từ khóa của tiêu đề (đây là lỗi tôi phát hiện khi chạy thử, xem mục 5); (2) section dài hơn `max_chunk_size` được đệ quy tách nhỏ tiếp bằng `RecursiveChunker` để không tạo chunk quá lớn. Trên bộ 8 tài liệu K3, chiến lược này tạo **29 chunk**.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents`: với mỗi `Document`, tạo record gồm `id`, `content`, `metadata` (tự thêm `doc_id` nếu thiếu) và `embedding = embedding_fn(content)`, rồi lưu vào list `self._store` (đồng thời nạp vào ChromaDB nếu môi trường có sẵn — có fallback in-memory nên test không cần cài Chroma). `search`: embed câu truy vấn rồi tính **tích vô hướng** giữa vector truy vấn và từng vector đã lưu (embedding đã chuẩn hóa nên tích vô hướng ≈ cosine), sắp xếp giảm dần theo `score` và trả `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` **lọc metadata trước, rồi mới tính tương tự** (pre-filter): chỉ giữ các record có metadata khớp *tất cả* cặp key–value trong `metadata_filter`, sau đó chạy đúng hàm chấm điểm như `search` trên tập con → đảm bảo top_k luôn nằm trong phạm vi đã lọc (ví dụ chỉ tài liệu `audience=student`). `delete_document` giữ lại các record có `metadata["doc_id"] != doc_id`, trả `True` nếu kích thước store thay đổi (tức có xóa), `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Theo mẫu RAG 3 bước: (1) `store.search(question, top_k)` lấy các chunk liên quan; (2) ghép chúng thành context đánh số `[1] … [2] …`; (3) dựng prompt yêu cầu **chỉ trả lời dựa trên context, nếu context không có thì nói không biết** (chống bịa), gắn context + câu hỏi rồi gọi `llm_fn`. Việc inject context dạng đánh số giúp câu trả lời có thể trích dẫn nguồn và dễ kiểm chứng.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

Lệnh chạy (trỏ bộ test vào package lời giải của tôi):

```
$ pytest tests/ -v            # trong repo cá nhân, package tên "src"

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED
... (42 items)
============================== 42 passed in 0.02s ==============================
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Đo bằng `compute_similarity` + backend `paraphrase-multilingual-MiniLM-L12-v2`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên được mượn tối đa 3 tài liệu trong 10 ngày. | Thời hạn mượn sách của sinh viên trong thư viện là bao lâu? | cao | **0.694** | ✅ |
| 2 | Nội quy ký túc xá cấm sinh viên uống rượu, bia. | Định mức giờ chuẩn giảng dạy của giảng viên mỗi năm. | thấp | **0.092** | ✅ |
| 3 | Con liệt sỹ được miễn 100% học phí. | Chính sách miễn, giảm học phí cho người có công với cách mạng. | cao | **0.117** | ❌ |
| 4 | Điều kiện xét học bổng khuyến khích học tập. | Sinh viên cần đạt loại khá trở lên để được cấp học bổng. | cao | **0.793** | ✅ |
| 5 | Trang phục công sở của cán bộ phải gọn gàng, lịch sự. | Sinh viên được gia hạn tài liệu thư viện thêm 10 ngày. | thấp | **0.068** | ✅ |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 3 gây bất ngờ nhất: tôi nghĩ "con liệt sỹ được miễn 100% học phí" và "chính sách miễn giảm học phí cho người có công" rất liên quan (một là trường hợp cụ thể của cái kia), nhưng điểm chỉ **0.117** — coi như thấp. Lý do: hai câu gần như **không trùng từ khóa bề mặt** ("con liệt sỹ" vs "người có công với cách mạng"), câu A rất ngắn và cụ thể còn câu B trừu tượng ở mức chính sách. Điều này cho thấy embedding vẫn chịu ảnh hưởng mạnh của từ vựng/độ dài câu, chưa suy luận được quan hệ "trường hợp con ⊂ nhóm cha"; do đó trong RAG nên chia câu hỏi rõ ràng và dựa vào top-k + metadata thay vì tin tuyệt đối vào một điểm số.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân (chiến lược `HeadingChunker`, backend local, `top_k=3`). Câu 1 dùng `search_with_filter(audience="student")` vì tài liệu thư viện có 2 phiên bản sinh viên/giảng viên với số liệu khác nhau — đây là câu **cần lọc metadata**.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu, trong bao lâu? | `library-services-student` → "Số lượng và thời hạn mượn: … tối đa 3 tài liệu trong 10 ngày" | 0.832 | ✅ (top-1) | 3 tài liệu, thời hạn 10 ngày |
| 2 | Hủy học phần đã đóng học phí nhưng không rút thì hủy trước khi nào? | `course-registration` → "Đóng học phí…" (đúng tài liệu); clause chính xác "trước ngày thi 10 ngày" ở chunk "Thời gian đăng ký" (top-3, 0.691) | 0.720 | ✅ (top-3) | Phải hủy trước ngày thi kết thúc học phần 10 ngày |
| 3 | Điều kiện xét học bổng khuyến khích học tập là gì? | `scholarship-incentive` → "Điều kiện xét: … 8 học kỳ chính, khá trở lên, không kỷ luật, ≥5/10, tín chỉ ≥ kế hoạch" | 0.785 | ✅ (top-1) | Nêu đủ 5 điều kiện xét học bổng |
| 4 | Những đối tượng nào được miễn 100% học phí? | `tuition-exemption` → "Đối tượng miễn 100% học phí: người có công, con liệt sỹ, SV khuyết tật, mồ côi…" | 0.454 | ✅ (top-1) | Liệt kê các nhóm được miễn 100% |
| 5 | Ký túc xá quy định không được thức khuya quá mấy giờ? | `dormitory-rules` → "Giờ giấc và khách: … không được thức khuya quá 23h30" | 0.807 | ✅ (top-1) | Không thức khuya quá 23h30 |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5** (top-1 chính xác ở 4/5; riêng câu 2, top-1 đúng tài liệu còn mệnh đề mốc "10 ngày trước ngày thi" nằm ở chunk xếp hạng 3).

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Cùng một bộ tài liệu nhưng mỗi chiến lược chunking cho chất lượng truy xuất rất khác nhau: `FixedSizeChunker` của Khôi cắt đều nên ổn định về kích thước nhưng hay cắt giữa mục, còn `HeadingChunker` của tôi bám cấu trúc tiêu đề nên top-1 thường là đúng nguyên mục cần tìm. Bài học lớn nhất là **chunk quá nhỏ / chỉ chứa tiêu đề sẽ khớp từ khóa nhưng rỗng nội dung** — chính lỗi này khiến tôi phải sửa chunker để gộp section "chỉ có tiêu đề" vào mục sau, và điểm truy xuất câu 3 mới lên đúng.

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
