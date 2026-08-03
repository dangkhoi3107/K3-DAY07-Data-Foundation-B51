# Hướng dẫn implementation Task 1–6 — dành cho Vi Minh Hiển, Nguyễn Đăng Đức, Đỗ Tuấn Sơn, Trần Đức Bảo Trung

> Đây **không phải code hoàn chỉnh để copy-paste**. Đây là hướng dẫn chi tiết hơn hẳn README gốc để bạn tự gõ nhanh và đúng. Lý do không có sẵn code: phần này chấm cá nhân (30đ + phần lớn 60đ report), và `REPORT_CANHAN.md` sẽ hỏi bạn giải thích logic — nếu không tự viết thì không trả lời thật được, dễ lộ khi demo/hỏi đáp. Repo tham khảo (`DAY07-2A202601243-PhamNguyenDangKhoi`) đã có 42/42 test pass — dùng để đối chiếu KẾT QUẢ (số test pass, số chunk...) chứ đừng chép nguyên code.

Trước khi bắt đầu, đọc `src/models.py` (class `Document`), `src/embeddings.py` (`_mock_embed` — trả 64 số cố định theo hash nội dung, KHÔNG mang nghĩa ngữ nghĩa thật), và đọc kỹ `FixedSizeChunker.chunk()` đã viết sẵn trong `src/chunking.py` — đó là chuẩn style cho cả bài (text rỗng → `[]`, text ngắn hơn chunk_size → `[text]`).

---

## Task 1 — `SentenceChunker.chunk` (`src/chunking.py`)

Mục tiêu: chia text thành câu, gộp tối đa `self.max_sentences_per_chunk` câu/chunk.

1. `text` rỗng → trả `[]` ngay.
2. Tách câu bằng `re.split` với pattern lookbehind `(?<=[.!?])\s+` — nghĩa là chỉ tách tại khoảng trắng NGAY SAU dấu `.`/`!`/`?`, dấu câu ở lại với câu đứng trước.
3. `strip()` từng phần, bỏ phần rỗng (`if s.strip()`).
4. Duyệt list câu theo bước nhảy `self.max_sentences_per_chunk`, mỗi nhóm nối lại bằng `" ".join(...)`.
5. Trả `list[str]`, không trả generator.

**Tự kiểm tra:** `SAMPLE_TEXT` trong test có đúng 5 câu. Với `max_sentences_per_chunk=2` → phải ra 3 chunk (2+2+1). Với `=1` → 5 chunk. Với `=3` → 2 chunk (3+2). Nếu số chunk bạn ra sai, `print(sentences)` để xem có bị dính câu hay tách nhầm không.

⚠️ Lỗi hay gặp: quên `strip()` → chunk cuối là chuỗi rỗng/toàn khoảng trắng vì text mẫu có khoảng trắng thừa ở cuối.

---

## Task 2 — `RecursiveChunker.chunk` + `_split` (`src/chunking.py`)

Mục tiêu: thử tách theo từng separator trong `self.separators` (mặc định: đoạn `\n\n` → dòng `\n` → câu `. ` → từ ` ` → ký tự `""`), ưu tiên ranh giới tự nhiên trước, phần nào vẫn dài thì hạ xuống separator ưu tiên thấp hơn.

**`chunk(text)`:** text rỗng → `[]`; gọi `self._split(text, self.separators)`; `strip()` + bỏ phần rỗng.

**`_split(current_text, remaining_separators)`** — phần khó nhất bài, làm đúng thứ tự:

1. **Base case 1:** `len(current_text) <= self.chunk_size` → trả `[current_text]` ngay.
2. **Base case 2:** hết separator (`remaining_separators` rỗng) HOẶC separator đầu là `""` → cắt cứng: chia `current_text` thành từng đoạn `chunk_size` ký tự liên tiếp bằng `range(0, len(current_text), self.chunk_size)`.
3. Lấy `separator = remaining_separators[0]`, `rest = remaining_separators[1:]`.
4. Separator **không** xuất hiện trong `current_text` → gọi đệ quy `self._split(current_text, rest)` (bỏ qua separator này). **Bắt buộc** — thiếu bước này đệ quy không tiến gần điều kiện dừng, sẽ treo/tràn stack.
5. Separator có xuất hiện → `current_text.split(separator)` ra các phần nhỏ. Gộp các phần liền kề (nối lại bằng chính `separator`) tới sát `chunk_size` thì chốt 1 chunk, sang phần tiếp.
6. Một phần đơn lẻ đã dài hơn `chunk_size` (không gộp được với ai) → xử lý tiếp bằng đệ quy `self._split(part, rest)`, nối kết quả vào danh sách chunk.

Sơ đồ tương đương đề bài: *Text dài hơn chunk_size? → còn separator? → separator có xuất hiện? → không thì thử separator kế; có thì gộp phần vừa kích thước, phần nào còn dài thì tách tiếp bằng separator kế.*

**Tự kiểm tra:** `RecursiveChunker(separators=[], chunk_size=100).chunk("no separators here")` (text ngắn hơn 100 ký tự) vẫn phải trả list không rỗng — vì rơi vào Base case 1 ngay, không cần đụng tới separator rỗng.

⚠️ Lỗi hay gặp nhất (đề bài cũng nhắc ở Phụ lục A): gọi lại đệ quy với **đúng nguyên** `current_text` và **đúng nguyên** `remaining_separators` — không bớt gì cả. Mỗi lần gọi lại phải hoặc bớt 1 separator, hoặc làm nhỏ `current_text` đi.

---

## Task 3 — `compute_similarity` + `ChunkingStrategyComparator.compare` (`src/chunking.py`)

**`compute_similarity(vec_a, vec_b)`:**
1. `norm_a = math.sqrt(_dot(vec_a, vec_a))`, tương tự `norm_b` (hàm `_dot` đã có sẵn trong file).
2. `norm_a == 0` hoặc `norm_b == 0` → trả `0.0` ngay (tránh chia 0).
3. Ngược lại trả `_dot(vec_a, vec_b) / (norm_a * norm_b)`.

Tự kiểm tra: vector giống hệt → `1.0`; vuông góc (`[1,0,0]` và `[0,1,0]`) → `0.0`; ngược hướng (`[1,0]` và `[-1,0]`) → `-1.0`.

**`ChunkingStrategyComparator.compare(text, chunk_size)`:**
1. Chạy `FixedSizeChunker(chunk_size=chunk_size)`, `SentenceChunker()`, `RecursiveChunker(chunk_size=chunk_size)` trên `text`.
2. Viết hàm phụ tính `count` (số chunk) + `avg_length` (trung bình `len()`) — `count == 0` thì `avg_length = 0.0` (tránh `ZeroDivisionError`).
3. Trả dict đúng 3 khóa: `fixed_size`, `by_sentences`, `recursive`, mỗi khóa có `count`, `avg_length`, `chunks`.

---

## Task 4 — `EmbeddingStore`: `_make_record`, `add_documents`, `search`, `get_collection_size` (`src/store.py`)

**`_make_record(doc)`:**
1. **Copy** metadata: `metadata = dict(doc.metadata)` — không dùng thẳng object gốc.
2. Đảm bảo có khóa `doc_id`: `metadata.setdefault("doc_id", doc.id)` (test hay truyền `metadata={}` rỗng, nên phải có fallback). `delete_document()` sẽ dựa vào khóa này.
3. Id record duy nhất: ghép `doc.id` với `self._next_index`, ví dụ `f"{doc.id}::{self._next_index}"`.
4. Trả dict có tối thiểu `id`, `content` (=`doc.content`), `metadata` (bản copy), `embedding` (=`self._embedding_fn(doc.content)`).

**`add_documents(docs)`:** với từng `doc`: tạo record (dùng `_next_index` hiện tại) → **tăng `self._next_index` lên 1** → append vào `self._store`. `docs` rỗng thì không làm gì, không lỗi.

**`get_collection_size()`:** `len(self._store)`.

**`_search_records(query, records, top_k)`** — helper dùng chung cho cả `search()` lẫn `search_with_filter()` (Task 5 bắt buộc dùng lại y hệt hàm này):
1. `query_vector = self._embedding_fn(query)` — tính **1 lần**, ngoài vòng lặp.
2. Với từng `record`: điểm = `_dot(query_vector, record["embedding"])` (import `_dot` từ `.chunking`, đã có sẵn trong file).
3. Kết quả có tối thiểu `id`, `content`, `metadata`, `score`.
4. `sort` giảm dần theo `score`, cắt `[:top_k]`.

**`search(query, top_k)`:** `return self._search_records(query, self._store, top_k)`.

⚠️ Lỗi hay gặp: gán `self._use_chroma = True` ngay sau `import chromadb` thành công nhưng chưa thật sự tạo client/collection → mọi method sau lỗi vì `self._collection` vẫn `None`. Nếu không định implement nhánh Chroma (không bắt buộc), cứ để `self._use_chroma = False` luôn — mọi method đi qua `self._store` in-memory, đúng như đề cho phép.

---

## Task 5 — `search_with_filter` + `delete_document` (`src/store.py`)

**`search_with_filter(query, top_k, metadata_filter)`:**
1. `metadata_filter` có giá trị → lọc `self._store`, chỉ giữ record mà **MỌI** cặp `key: value` trong `metadata_filter` khớp: `all(record["metadata"].get(k) == v for k, v in metadata_filter.items())`.
2. `metadata_filter` là `None` → tập ứng viên = toàn bộ `self._store`.
3. Gọi `self._search_records(query, candidates, top_k)` trên tập đã lọc.

**Bắt buộc filter TRƯỚC, rank SAU** — lấy top-k trước rồi mới lọc có thể ra 0 kết quả dù store còn tài liệu hợp lệ.

**`delete_document(doc_id)`:** lưu `size_before = len(self._store)` → gán lại `self._store` = list chỉ giữ record có `record["metadata"].get("doc_id") != doc_id` → trả `len(self._store) < size_before`.

---

## Task 6 — `KnowledgeBaseAgent` (`src/agent.py`)

**`__init__(self, store, llm_fn)`:** `self.store = store`; `self.llm_fn = llm_fn`.

**`answer(question, top_k)`:**
1. Store rỗng (`self.store.get_collection_size() == 0`) → trả thẳng câu thông báo, KHÔNG gọi `llm_fn`.
2. `results = self.store.search(question, top_k=top_k)`.
3. Ghép `result["content"]` thành context, **đánh số** `[1]`, `[2]`... kèm `doc_id` (từ `result["metadata"].get("doc_id", ...)`) để truy vết nguồn.
4. Prompt gồm 4 phần theo thứ tự: hướng dẫn "chỉ dùng context, không đủ thì nói rõ" → khối `Context:` → `Question: {question}` → nhãn `Answer:` ở cuối (không có nội dung sau).
5. `return self.llm_fn(prompt)`.

Đánh số `[1] [2]` ở bước 3 là phần đáng đầu tư nhất — đó là tiêu chí "grounding" mà `docs/EVALUATION.md` chấm.

---

## Sau khi xong cả 6 Task

```
python -m pytest tests -k "Chunker or Similarity or Compare" -v   # kỳ vọng 23 passed (CP3)
python -m pytest tests -v                                          # kỳ vọng 42 passed (CP4)
python main.py "Chunking là gì?"
```

Nếu Windows báo `UnicodeEncodeError` khi in tiếng Việt ra console — không phải lỗi code, do codepage mặc định của terminal. Chạy trước:
- PowerShell: `$env:PYTHONIOENCODING="utf-8"`
- cmd: `set PYTHONIOENCODING=utf-8`

rồi chạy lại lệnh `python main.py ...`.
