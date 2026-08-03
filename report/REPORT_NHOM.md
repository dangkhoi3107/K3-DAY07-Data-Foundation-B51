# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** K3 — Dịch vụ/quy định đại học
**Thành viên:** Phạm Nguyễn Đăng Khôi (2A202601243) · Vi Minh Hiển (2A202601743) · Nguyễn Đăng Đức (2A202601787) · Đỗ Tuấn Sơn (2A202601051) · Trần Đức Bảo Trung (2A202601269)
**Ngày:** 2026-08-03 (bản nháp — cập nhật lại ngày khi nộp chính thức)

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:** Dịch vụ và quy định dành cho sinh viên, giảng viên và cán bộ tại nhiều trường đại học Việt Nam, tập trung vào các thủ tục học vụ (đăng ký học phần, học bổng, học phí), đời sống sinh viên (ký túc xá, thư viện) và nghĩa vụ công tác (chế độ làm việc giảng viên, văn hóa công sở cán bộ).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đăng ký và hủy học phần | daotao.ueh.edu.vn | 2026-08-03 / not-stated | 1300 | audience=student, department=academic-affairs, category=registration |
| 2 | Học bổng khuyến khích học tập | daotao.ueh.edu.vn | 2026-08-03 / not-stated | 904 | audience=student, department=academic-affairs, category=scholarship |
| 3 | Nội quy ký túc xá | ktx.haui.edu.vn | 2026-08-03 / not-stated | 856 | audience=student, department=student-affairs, category=housing |
| 4 | Chính sách miễn, giảm học phí | student.tdtu.edu.vn | 2026-08-03 / NĐ-238/2025 | 914 | audience=student, department=finance, category=tuition |
| 5 | Quy định thư viện — sinh viên | thuvien.huit.edu.vn | 2026-08-03 / not-stated | 454 | audience=student, department=library, category=borrowing-policy |
| 6 | Quy định thư viện — giảng viên/cán bộ | thuvien.huit.edu.vn | 2026-08-03 / not-stated | 488 | audience=faculty, department=library, category=borrowing-policy |
| 7 | Chế độ làm việc của giảng viên | vnu.edu.vn | 2026-08-03 / not-stated | 705 | audience=faculty, department=academic-affairs, category=workload |
| 8 | Quy chế văn hóa công sở | hvnh.edu.vn | 2026-08-03 / QĐ-40/2008 | 825 | audience=staff, department=administration, category=workplace-conduct |

*(Số ký tự đo bằng `len(document.content)` sau khi đã tách front matter qua `ingest.load_documents()` — chỉ tính phần thân, không tính khối YAML.)*

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string (bắt buộc K3) | `student` / `faculty` / `staff` | Lọc trước khi rank — tránh trộn quy định của hai đối tượng khác nhau cho cùng chủ đề (VD: mượn sách thư viện) |
| `department` | string | `library`, `finance`, `academic-affairs` | Thu hẹp theo phòng ban phụ trách khi câu hỏi nêu rõ đơn vị |
| `category` | string | `tuition`, `housing`, `scholarship` | Phân nhóm chủ đề, hỗ trợ lọc thô trước khi so embedding |
| `source_url` / `retrieved_at` / `document_version` | string | — | Truy vết nguồn, không dùng để lọc retrieval nhưng bắt buộc cho minh bạch |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=200)` trên 3 tài liệu thật (đã bỏ front matter qua `ingest.load_documents()`):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| course-registration (1300 ký tự) | FixedSizeChunker (`fixed_size`) | 9 | 188.9 | Có thể cắt giữa câu vì cắt cứng theo ký tự |
| course-registration (1300 ký tự) | SentenceChunker (`by_sentences`) | 4 | 323.5 | Giữ nguyên câu, nhưng vượt hẳn chunk_size=200 (gộp tới 3 câu/chunk) |
| course-registration (1300 ký tự) | RecursiveChunker (`recursive`) | 14 | 91.3 | Chunk khá vụn — separator `\n` tách cả ở dòng heading `##` ngắn, tạo nhiều chunk nhỏ hơn cần thiết |
| dormitory-rules (856 ký tự) | FixedSizeChunker (`fixed_size`) | 6 | 184.3 | Có thể cắt giữa câu |
| dormitory-rules (856 ký tự) | SentenceChunker (`by_sentences`) | 2 | 426.0 | Giữ nguyên câu nhưng chunk quá dài so với chunk_size=200 |
| dormitory-rules (856 ký tự) | RecursiveChunker (`recursive`) | 10 | 84.2 | Vụn tương tự — nhiều dòng ngắn (heading, danh sách hành vi cấm) bị tách riêng |
| library-services-student (454 ký tự) | FixedSizeChunker (`fixed_size`) | 3 | 184.7 | Có thể cắt giữa câu, nhưng tài liệu ngắn nên ít ảnh hưởng |
| library-services-student (454 ký tự) | SentenceChunker (`by_sentences`) | 2 | 225.5 | Giữ nguyên câu, độ dài hợp lý nhất trong 3 tài liệu |
| library-services-student (454 ký tự) | RecursiveChunker (`recursive`) | 5 | 89.4 | Vụn — mỗi heading `##` thành 1 chunk riêng dù nội dung ngắn |

**Nhận xét baseline:** `RecursiveChunker` với separator mặc định (`\n\n → \n → . → " " → ""`) tạo chunk nhỏ hơn hẳn `chunk_size=200` mong muốn, vì các tài liệu K3 có nhiều dòng ngắn (heading `##`, mỗi ý một dòng) khiến separator `\n` kích hoạt sớm. Đây là lý do K3_VARIANT.md yêu cầu thử thêm chunker theo heading/section — Đỗ Tuấn Sơn sẽ so sánh trực tiếp với baseline này.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây. Nhóm có 5 người nên có 5 khối.

**Thành viên 1 — Phạm Nguyễn Đăng Khôi (2A202601243)**
- **Loại chiến lược:** FixedSizeChunker (`chunk_size=300, overlap=60`)
- **Mô tả & lý do chọn cho chủ đề này:** Chọn tham số khác mặc định (500/50) để tạo chunk nhỏ hơn, phù hợp với các đoạn quy định K3 vốn ngắn (mỗi tài liệu 450–1300 ký tự) — overlap 60 (20% chunk_size) đủ để câu điều kiện/ngoại lệ không bị cắt đứt ngay ranh giới chunk. Nhược điểm đã thấy: cắt cứng theo ký tự nên vẫn có thể chia đôi một câu.
- **Code snippet (nếu custom):** không phải custom, dùng nguyên `FixedSizeChunker` có sẵn trong `src/chunking.py`, chỉ đổi tham số trong `bench.py`.

**Thành viên 2 — Vi Minh Hiển (2A202601743)**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`
- **Mô tả & lý do chọn:** Tách theo ranh giới câu (regex `(?<=[.!?])\s+`) rồi gộp tối đa 3 câu/chunk — giữ trọn từng câu quy định, không cắt đứt điều kiện/mốc thời gian nằm giữa câu. Trên 8 tài liệu K3 tạo **19 chunk**. Điểm cộng: còn tự viết thêm `TfidfEmbedder` (TF-IDF chuẩn hoá, không phụ thuộc thư viện ngoài) trong `bench.py` để benchmark có ý nghĩa ngữ nghĩa thật thay vì chỉ dùng MockEmbedder.
- **Code snippet (nếu custom):** không cần cho chunker, dùng `SentenceChunker` có sẵn trong `src/chunking.py`.

**Thành viên 3 — Nguyễn Đăng Đức (2A202601787)**
- **Loại chiến lược:** RecursiveChunker (separator mặc định: đoạn → dòng → câu → từ → ký tự)
- **Mô tả & lý do chọn:** Đệ quy thử separator ưu tiên `["\n\n", "\n", ". ", " ", ""]`, gộp các phần liền kề tới sát `chunk_size=500`; phần nào vẫn dài thì đệ quy xuống separator kế tiếp — giữ ranh giới tự nhiên (đoạn/dòng/câu) của văn bản càng lâu càng tốt (mô tả lấy từ `REPORT_CANHAN.md` của Đức).
- **Code snippet (nếu custom):** không cần, dùng `RecursiveChunker` có sẵn với separator mặc định.
- ✅ **Cập nhật:** đã tự lấy đúng 3 file `agent.py`/`chunking.py`/`store.py` từ `src/NguyenDangDuc/`, đặt tạm vào đúng vị trí `src/` gốc và chạy `pytest` độc lập — **42/42 pass thật**, nghĩa là logic code của Đức đúng, không phải lỗi implementation.
- ⚠️ **Vẫn cần Đức tự sửa trước khi nộp:** trên chính nhánh `dangduc` hiện tại, code thật vẫn nằm ở `src/NguyenDangDuc/` (bản sao) trong khi 3 file gốc `src/chunking.py`/`store.py`/`agent.py` — nơi `tests/test_solution.py` thực sự import — vẫn còn nguyên `NotImplementedError`, nên nếu ai clone đúng nhánh `dangduc` và chạy `pytest` ngay sẽ vẫn ra **31 failed, 11 passed**, dù `REPORT_CANHAN.md` đã ghi "42 passed". Cách sửa: copy đè 3 file từ `src/NguyenDangDuc/` lên 3 file gốc cùng tên. Chưa có `bench.py` trong repo. 5 câu hỏi & gold answer ở mục 5 báo cáo cũng dùng một bộ câu hỏi khác hẳn bộ 5 câu chung của nhóm, và một vài con số không khớp corpus thật đang dùng (ví dụ ghi "mượn tối đa 3 cuốn trong 14 ngày" trong khi `library-services-student.md` ghi rõ 10 ngày) — cần rà lại các con số này sau khi sửa vị trí code.

**Thành viên 4 — Đỗ Tuấn Sơn (2A202601051)**
- **Loại chiến lược:** custom — `HeadingChunker` theo heading/section (bắt buộc theo `K3_VARIANT.md`)
- **Mô tả & lý do chọn:** Quét từng dòng, mở section mới mỗi khi gặp dòng heading Markdown (`#`/`##`/`###`) để mỗi chunk là **một mục ngữ nghĩa trọn vẹn**, đúng vấn đề "chunk vụn" đã nêu ở Baseline Analysis phía trên. Hai xử lý đáng chú ý: (1) section "chỉ có tiêu đề, không nội dung" được gộp vào section kế tiếp để tránh chunk rỗng nghĩa (lỗi Sơn tự phát hiện khi chạy thử); (2) section dài hơn `max_chunk_size` được hạ xuống `RecursiveChunker` để không tạo chunk quá lớn. Trên 8 tài liệu K3 tạo **29 chunk**.
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    """Chunk Markdown theo cấu trúc heading/section (chiến lược tự viết của K3)."""

    def __init__(self, max_heading_level: int = 3, max_chunk_size: int = 1000) -> None:
        self.max_heading_level = max_heading_level
        self.max_chunk_size = max_chunk_size
        self._heading_re = re.compile(rf"^#{{1,{max_heading_level}}}\s+\S")

    def _is_heading(self, line: str) -> bool:
        return bool(self._heading_re.match(line))

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        # Gom các dòng thành từng section, mở section mới mỗi khi gặp heading.
        sections: list[list[str]] = []
        current: list[str] = []
        for line in text.splitlines():
            if self._is_heading(line) and current:
                sections.append(current)
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append(current)

        # Gộp section "chỉ có tiêu đề" (không nội dung) vào section kế tiếp.
        merged: list[list[str]] = []
        carry: list[str] = []
        for section in sections:
            body = [ln for ln in section[1:] if ln.strip()]
            if not body:
                carry.extend(section)
            else:
                merged.append(carry + section)
                carry = []
        if carry:
            merged.append(carry)

        chunks: list[str] = []
        splitter = RecursiveChunker(chunk_size=self.max_chunk_size)
        for section in merged:
            block = "\n".join(section).strip()
            if not block:
                continue
            chunks.extend([block] if len(block) <= self.max_chunk_size else splitter.chunk(block))
        return chunks
```
  *(nguyên văn từ `src/01051-DoTuanSon/chunking.py` trên nhánh `son` — thiết kế đúng yêu cầu và đã đọc kỹ.)*
- ✅ **Cập nhật:** đã tự lấy đúng 3 file từ `src/01051-DoTuanSon/`, đặt tạm vào vị trí `src/` gốc và chạy `pytest` độc lập — **42/42 pass thật**, bao gồm cả 3 chunker chuẩn (`HeadingChunker` là custom nên không nằm trong 42 test, nhưng đã đọc code và xác nhận logic hợp lý — xem mục ghi chú thiết kế phía trên).
- ⚠️ **Vẫn cần Sơn tự sửa trước khi nộp:** cùng lỗi vị trí code như Đức — trên chính nhánh `son`, toàn bộ Task 1–6 (kể cả `HeadingChunker`) vẫn chỉ nằm ở `src/01051-DoTuanSon/`, còn 3 file gốc `src/chunking.py`/`store.py`/`agent.py` vẫn còn nguyên `NotImplementedError` nên `pytest` trên nhánh `son` hiện vẫn ra **31 failed, 11 passed**. Cách sửa đơn giản nhất: copy đè nội dung 3 file từ `src/01051-DoTuanSon/` lên 3 file gốc cùng tên (giống cách Hiển đã làm). Chưa có `bench.py` trong repo dù `REPORT_CANHAN.md` mô tả đã chạy benchmark với backend `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` — số liệu đó chưa có script để tái lập. 5 câu hỏi dùng trong báo cáo cũng khác bộ 5 câu chung của nhóm (2/5 câu là chủ đề khác hẳn, không có gold answer chung để đối chiếu).

**Thành viên 5 — Trần Đức Bảo Trung (2A202601269)**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=420, separators=[". ", "; ", "\n\n", "\n", " ", ""])`
- **Mô tả & lý do chọn:** Khác Đức ở cả `chunk_size` (420 so với 500) lẫn thứ tự separator — ưu tiên ranh giới câu/mệnh đề (`". "`, `"; "`) trước ranh giới dòng, giúp tránh tạo chunk chỉ có heading trong corpus Markdown nhiều dòng ngắn. Trên 8 tài liệu K3 tạo **24 chunk**. Điểm cộng: tự viết `LightweightVietnameseEmbedder` bọc `sklearn.HashingVectorizer` (char n-gram 3–5, 4096 chiều, chuẩn hoá L2) để benchmark có ngữ nghĩa thật.
- **Code snippet (nếu custom):** không phải custom cho chunker, dùng `RecursiveChunker` có sẵn, chỉ đổi tham số.
- ℹ️ Lưu ý nhỏ: `bench.py` của Trung import `sklearn` nhưng `scikit-learn` chưa có trong `requirements.txt`/`requirements-local.txt` — nên thêm vào để người khác chạy lại được đúng hướng dẫn cài đặt.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Phạm Nguyễn Đăng Khôi | FixedSizeChunker (300/60) | 4/10 *(2 câu đúng ở top-2/top-3 × 2đ = 4, xem `REPORT_CANHAN.md` mục 5 — dùng MockEmbedder, chưa phản ánh ngữ nghĩa thật)* | Đơn giản, chunk đều nhau, dễ debug | Cắt cứng theo ký tự, có thể chia đôi câu; không phân biệt được ranh giới ngữ nghĩa |
| Vi Minh Hiển | SentenceChunker(max_sentences_per_chunk=3) | 8/10 *(3 câu đúng & đầy đủ trong top-3 × 2đ = 6, 2 câu đúng tài liệu nhưng top-1 thiếu chi tiết × 1đ = 2 — xem `REPORT_CANHAN.md` của Hiển mục 5, backend TF-IDF tự viết)* | Giữ trọn từng câu, dễ đọc, không cắt đứt điều kiện/mốc thời gian giữa câu | Độ dài chunk không đều; đôi khi mốc thời gian tách khỏi câu mô tả điều kiện nên top-1 đúng tài liệu nhưng thiếu chi tiết |
| Nguyễn Đăng Đức | RecursiveChunker (mặc định) | ⚠️ *code đúng (42/42 khi test độc lập), điểm truy xuất chưa đo được* | Logic 42/42 pass khi đặt đúng vị trí (đã tự kiểm tra); giữ ranh giới đoạn/dòng/câu tự nhiên | Trên nhánh `dangduc` code vẫn nằm sai thư mục nên `pytest` mặc định vẫn fail; chưa có `bench.py`; báo cáo dùng bộ câu hỏi khác nhóm và có số liệu không khớp corpus — xem cảnh báo ở khối chiến lược phía trên |
| Đỗ Tuấn Sơn | HeadingChunker (custom) | ⚠️ *code đúng (42/42 khi test độc lập), điểm truy xuất chưa đo được* | Logic 42/42 pass khi đặt đúng vị trí (đã tự kiểm tra); thiết kế đúng vấn đề "chunk vụn" của Baseline, xử lý tốt case section chỉ có tiêu đề | Trên nhánh `son` code vẫn nằm sai thư mục nên `pytest` mặc định vẫn fail; chưa có `bench.py`; bộ câu hỏi khác nhóm — xem cảnh báo ở khối chiến lược phía trên |
| Trần Đức Bảo Trung | RecursiveChunker (420, separator câu/mệnh đề trước dòng) | 10/10 *(5/5 câu đúng tài liệu trong top-3 + agent trả lời đầy đủ, xem `REPORT_CANHAN.md` của Trung mục 5, backend HashingVectorizer tự viết)* | Ưu tiên ranh giới câu/mệnh đề trước dòng → tránh chunk chỉ có heading; điểm truy xuất cao nhất nhóm | Cùng họ RecursiveChunker với Đức nên kém đa dạng hơn so với hướng custom theo heading (Sơn) |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Trong số kết quả **đã xác nhận chạy được thật** (Khôi, Hiển, Trung), `RecursiveChunker(chunk_size=420, separator ưu tiên câu/mệnh đề)` của Trung đạt điểm truy xuất cao nhất (10/10) vì corpus K3 là các trang quy định Markdown nhiều heading và dòng ngắn — ưu tiên cắt tại `". "`/`"; "` trước khi cắt tại `"\n"` tránh được đúng lỗi "chunk chỉ còn heading" mà Baseline Analysis đã chỉ ra ở `RecursiveChunker` mặc định. `SentenceChunker` của Hiển (8/10) cũng tốt vì giữ trọn câu. Về mặt **thiết kế** (chưa tính điểm vì code chưa chạy được), `HeadingChunker` của Sơn có lẽ là chiến lược phù hợp nhất về mặt khái niệm cho domain này — vì các tài liệu K3 vốn được viết theo mục có tiêu đề rõ ràng (số lượng/thời hạn, gia hạn, xử lý trễ hạn...) — nhưng cần chạy thật mới kết luận được có vượt qua kết quả của Trung hay không. Bài học chung: **kích thước & separator nên khớp với cấu trúc thật của tài liệu**, không nên giữ nguyên tham số mặc định.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu thư viện và trong bao lâu? *(bắt buộc `metadata_filter={"audience":"student"}`, nếu không sẽ dễ lẫn với đáp án 180 ngày của giảng viên)* | Tối đa 3 tài liệu, thời hạn 10 ngày, gia hạn thêm được 1 lần 10 ngày | `library-services-student` |
| 2 | Sinh viên cần đạt điều kiện gì để được xét học bổng khuyến khích học tập loại khá? | Đang trong 8 học kỳ chính; học tập và rèn luyện từ loại khá trở lên; không kỷ luật từ mức khiển trách trở lên; đạt ≥5/10 mọi học phần; tín chỉ đăng ký ≥ kế hoạch đào tạo | `scholarship-incentive` |
| 3 | Quy trình hủy một học phần đã đăng ký gồm những bước nào? | Nộp Phiếu đề nghị hủy học phần tại Phòng Quản lý đào tạo trong thời hạn quy định; Phòng Tài chính hoàn học phí theo danh sách đã xác nhận hủy | `course-registration` |
| 4 | Ký túc xá cấm những hành vi nào? | Uống rượu bia; tàng trữ vũ khí/hung khí/chất nổ/ma túy; nấu ăn/tổ chức sinh nhật trong phòng; đánh bài cờ bạc; gây gổ tụ tập bè phái; vượt rào trèo tường | `dormitory-rules` |
| 5 | Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không? *(câu hỏi ngoại lệ — đối lập với câu 1)* | Không — không áp dụng gia hạn, tài liệu phải trả đúng đợt thu hồi 25/6 và 25/12 hằng năm (khác với sinh viên được gia hạn 1 lần) | `library-services-faculty` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Sinh viên mượn tối đa bao nhiêu tài liệu thư viện, trong bao lâu? | Trần Đức Bảo Trung — RecursiveChunker(420) | **Có** ở Trung (top-1, score 0,5402) · **Không** ở Khôi (FixedSize+Mock, sai tài liệu cả top-3) | Cả hai đều dùng đúng `metadata_filter={"audience":"student"}`; chỉ khi embedding có ngữ nghĩa thật (Trung) thì rank mới đúng. |
| 2 | Điều kiện xét học bổng khuyến khích học tập loại khá? | Trần Đức Bảo Trung — RecursiveChunker(420) | **Có** ở Trung (top-1, score 0,6515) · **Không** ở Khôi | |
| 3 | Quy trình hủy một học phần đã đăng ký gồm những bước nào? | Trần Đức Bảo Trung — RecursiveChunker(420) | **Có** ở cả hai, nhưng không ở top-1: Trung top-2/3 (0,4737, agent vẫn trả lời đầy đủ) · Khôi top-2 (0,148, context top-1 sai) | Vì agent luôn ghép cả top-3 vào context nên câu trả lời cuối vẫn đúng dù chunk đúng không nằm ở top-1 — minh hoạ tác dụng của `top_k=3` thay vì chỉ lấy top-1. |
| 4 | Ký túc xá cấm những hành vi nào? | Trần Đức Bảo Trung — RecursiveChunker(420) | **Có** ở Trung (top-1, 0,3396) · **Không** ở Khôi | |
| 5 | Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không? | Trần Đức Bảo Trung — RecursiveChunker(420) | **Có** ở cả hai: Trung top-1 (0,7266) · Khôi top-3 (0,245) | Câu "ngoại lệ" (đối lập câu 1) — cả 2 chiến lược đều tìm ra tài liệu `library-services-faculty` dù dùng embedding khác hẳn nhau. |

> **Ghi chú phạm vi bảng trên:** chỉ Khôi và Trung dùng **đúng bộ 5 câu hỏi chung** này để chạy `bench.py`, nên chỉ 2 người có trong bảng so từng câu. Hiển và Đức đã chạy benchmark thật (Hiển 5/5 top-3; Đức tự báo 5/5 nhưng số liệu không khớp corpus — xem cảnh báo mục 2) nhưng trên **một bộ câu hỏi khác** bộ chung của nhóm (chủ đề trùng nhưng cách hỏi/gold answer khác) — cần Hiển và Đức chạy lại `bench.py` đúng 5 câu hỏi ở bảng mục 3 phía trên rồi bổ sung cột riêng vào bảng này. Sơn chưa có số liệu vì chưa viết `bench.py` (code chunker của Sơn đã xác nhận đúng — 42/42 khi test độc lập — chỉ là chưa có script benchmark để chạy 5 câu hỏi).

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, đặc biệt ở câu 1 và câu 5 — đây là cặp câu hỏi "đối lập" dùng chung một trang nguồn thư viện nhưng khác `audience` (sinh viên: 3 tài liệu/10 ngày, có gia hạn; giảng viên/cán bộ: 3 tài liệu/180 ngày, không gia hạn). A/B test của Khôi cho thấy filter loại đúng 3 tài liệu sai đối tượng khỏi tập ứng viên, nhưng **rank vẫn có thể sai** nếu embedding không mang ngữ nghĩa thật (MockEmbedder) — kết quả của Trung (embedding thật + có filter ở câu 1) cho top-1 đúng ngay, còn Khôi (embedding giả + filter đúng) vẫn chọn sai top-1. Kết luận: **metadata filter thu hẹp đúng không gian tìm kiếm, nhưng không thay thế được chất lượng embedding** — cần cả hai để retrieval đúng.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. Cùng một corpus 8 tài liệu nhưng 5 chiến lược cho số lượng chunk rất khác nhau (19–29 chunk) và điểm truy xuất trải từ 4/10 đến 10/10 — chứng minh **chunking quyết định retrieval nhiều hơn** chỉ đổi embedding.
> 2. Chất lượng embedding và metadata filter là **hai trục độc lập**: filter đúng (Khôi, câu 1) vẫn cho rank sai nếu backend không có ngữ nghĩa thật (MockEmbedder); ngược lại backend tốt (TF-IDF của Hiển, HashingVectorizer của Trung) mới phát huy tác dụng khi kết hợp với filter.
> 3. Vì `KnowledgeBaseAgent` luôn ghép **cả top-3** vào context (không chỉ top-1), câu trả lời cuối cùng vẫn có thể đúng dù chunk đúng chỉ nằm ở top-2/top-3 (câu 3 và câu 5 ở cả Khôi và Trung) — top_k > 1 có tác dụng "vớt" các trường hợp rank chưa hoàn hảo.

**Bài học rút ra khi so sánh trong nhóm:**
> Cắt theo ranh giới ngữ nghĩa tự nhiên của tài liệu (câu ở `SentenceChunker`, mục ở `HeadingChunker`, hoặc separator ưu tiên câu/mệnh đề như cấu hình của Trung) luôn cho chunk mạch lạc hơn cắt cứng theo ký tự (`FixedSizeChunker`) hoặc dùng nguyên tham số mặc định của `RecursiveChunker` — corpus K3 gồm các trang quy định Markdown nhiều heading/dòng ngắn nên separator mặc định (`\n\n → \n → ...`) dễ tách sớm ở mỗi dòng heading, tạo chunk vụn (đúng như Baseline Analysis ở mục 2 đã chỉ ra). Bài học thứ hai: **báo cáo và code phải đồng bộ khi nộp** — 2/5 thành viên (Đức, Sơn) viết report rất chi tiết nhưng đặt code triển khai vào thư mục cá nhân thay vì đè lên `src/chunking.py`/`store.py`/`agent.py` gốc mà `tests/test_solution.py` thực sự import, nên `pytest` hiện vẫn fail dù report ghi "42 passed" — cần rà lại đúng cấu trúc thư mục trước khi tính là "xong".

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Chốt cứng **một bộ 5 câu hỏi + gold answer dùng chung** ngay từ đầu (kèm quy ước không tự đổi câu hỏi) trước khi ai bắt đầu viết `bench.py` — hiện tại Hiển và Đức đã tự chạy benchmark trên bộ câu hỏi khác bộ chung của nhóm nên chưa gộp được vào bảng so sánh 5 người. Đồng thời nên thống nhất từ đầu quy ước vị trí code nộp bài (đè lên file gốc `src/`, không tạo thư mục cá nhân riêng) để tránh đúng lỗi mà Đức và Sơn đang gặp.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
