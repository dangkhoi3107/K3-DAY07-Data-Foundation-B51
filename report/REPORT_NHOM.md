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
- ✅ **Đã hoàn thiện (2026-08-03):** nhánh `dangduc` đã được sửa — code chuyển đúng vào `src/chunking.py`/`store.py`/`agent.py` gốc (`pytest` → 42/42 pass thật trên chính nhánh), đã có `bench.py` (`RecursiveChunker()` mặc định + `SimpleTfidfEmbedder` tự viết, dependency-free), và `report/REPORT_CANHAN.md` mục 4–5 đã cập nhật số liệu thật đúng bộ 5 câu hỏi chung của nhóm — 5/5 đúng tài liệu ở top-1, kèm 1 failure case cụ thể ở câu 4 (đúng tài liệu nhưng đúng chunk "Hành vi bị cấm" không lọt top-3). Điểm truy xuất: **9/10**. *Đức nên tự chạy lại `bench.py` và đọc kỹ phần nhận xét trước khi demo để tự giải thích được.*

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
- ✅ **Đã hoàn thiện (2026-08-03):** nhánh `son` đã được sửa — code (kể cả `HeadingChunker`) chuyển đúng vào `src/chunking.py`/`store.py`/`agent.py` gốc (`pytest` → 42/42 pass thật trên chính nhánh), đã có `bench.py` (`HeadingChunker()` + `SimpleTfidfEmbedder` tự viết), và `report/REPORT_CANHAN.md` mục 4–5 đã chạy lại đúng bộ 5 câu hỏi chung của nhóm. Kết quả: **5/5 đúng tài liệu VÀ đúng chunk ngay ở top-1** — tốt nhất trong cả nhóm, kể cả câu 4 (khó nhất, `HeadingChunker` tách đúng nguyên mục "Hành vi bị cấm"). Điểm truy xuất: **10/10**. *Sơn nên tự chạy lại `bench.py` và đọc kỹ phần nhận xét trước khi demo để tự giải thích được.*

**Thành viên 5 — Trần Đức Bảo Trung (2A202601269)**
- **Loại chiến lược:** `RecursiveChunker(chunk_size=420, separators=[". ", "; ", "\n\n", "\n", " ", ""])`
- **Mô tả & lý do chọn:** Khác Đức ở cả `chunk_size` (420 so với 500) lẫn thứ tự separator — ưu tiên ranh giới câu/mệnh đề (`". "`, `"; "`) trước ranh giới dòng, giúp tránh tạo chunk chỉ có heading trong corpus Markdown nhiều dòng ngắn. Trên 8 tài liệu K3 tạo **24 chunk**. Điểm cộng: tự viết `LightweightVietnameseEmbedder` bọc `sklearn.HashingVectorizer` (char n-gram 3–5, 4096 chiều, chuẩn hoá L2) để benchmark có ngữ nghĩa thật.
- **Code snippet (nếu custom):** không phải custom cho chunker, dùng `RecursiveChunker` có sẵn, chỉ đổi tham số.
- ✅ Đã bổ sung `scikit-learn` vào `requirements-local.txt` (trước đó `bench.py` của Trung import `sklearn` nhưng chưa được khai báo).

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Phạm Nguyễn Đăng Khôi | FixedSizeChunker (300/60) | 4/10 *(2 câu đúng ở top-2/top-3 × 2đ = 4, xem `REPORT_CANHAN.md` mục 5 — dùng MockEmbedder, chưa phản ánh ngữ nghĩa thật)* | Đơn giản, chunk đều nhau, dễ debug | Cắt cứng theo ký tự, có thể chia đôi câu; không phân biệt được ranh giới ngữ nghĩa |
| Vi Minh Hiển | SentenceChunker(max_sentences_per_chunk=3) | 9/10 *(4 câu đúng & đầy đủ trong top-3 × 2đ = 8, 1 câu đúng tài liệu nhưng chưa trọn vẹn × 1đ = 1 — xem `REPORT_CANHAN.md` của Hiển mục 5, backend TF-IDF tự viết, đúng bộ 5 câu hỏi chung)* | Giữ trọn từng câu, dễ đọc; hay gộp 2-3 mục `##` liền kề nên nhiều câu trả lời đầy đủ ngay top-1 | Độ dài chunk không đều; câu cần đúng 1 mục cụ thể (câu 3) có thể bị tách sang chunk khác nếu mục đó đủ dài |
| Nguyễn Đăng Đức | RecursiveChunker (mặc định) | 9/10 *(4 câu đúng & đầy đủ × 2đ = 8, 1 câu đúng tài liệu nhưng sai chunk (failure case) × 1đ = 1 — xem `REPORT_CANHAN.md` của Đức mục 5, backend TF-IDF tự viết, đúng bộ 5 câu hỏi chung)* | Giữ ranh giới đoạn/dòng/câu tự nhiên; 5/5 đúng tài liệu ngay top-1 | Separator mặc định vẫn có thể tách 1 mục dài thành nhiều chunk nhỏ (câu 4: đúng tài liệu, đúng chunk "Hành vi bị cấm" không lọt top-3 — failure case cụ thể) |
| Đỗ Tuấn Sơn | HeadingChunker (custom) | 10/10 *(5/5 câu đúng & đầy đủ trong top-3, đúng bộ 5 câu hỏi chung — xem `REPORT_CANHAN.md` của Sơn mục 5, backend TF-IDF tự viết)* | Bám cấu trúc heading nên mỗi chunk là 1 mục ngữ nghĩa trọn vẹn — **kết quả tốt nhất nhóm**, kể cả câu 4 (mục "Hành vi bị cấm") mà cả Khôi lẫn Đức đều không lấy trọn được | Chunker tự viết, chưa có test tự động riêng (không nằm trong 42 test chuẩn); phụ thuộc corpus có heading rõ ràng — khó tổng quát hoá cho tài liệu không có cấu trúc `##` |
| Trần Đức Bảo Trung | RecursiveChunker (420, separator câu/mệnh đề trước dòng) | 10/10 *(5/5 câu đúng & đầy đủ, xem `REPORT_CANHAN.md` của Trung mục 5, backend HashingVectorizer tự viết)* | Ưu tiên ranh giới câu/mệnh đề trước dòng → tránh chunk chỉ có heading; đồng hạng cao nhất nhóm | Cùng họ RecursiveChunker với Đức nên kém đa dạng hơn so với hướng custom theo heading (Sơn); cần tinh chỉnh tham số kỹ hơn để đạt được kết quả này |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> `HeadingChunker` (custom, Sơn) và `RecursiveChunker(420, separator câu trước dòng)` (Trung) đồng hạng cao nhất (10/10 — 5/5 câu đúng cả tài liệu lẫn đúng chunk ngay top-1). Giữa hai chiến lược này, `HeadingChunker` phù hợp hơn về mặt **khái niệm** cho domain K3: các tài liệu quy định đại học vốn được viết thành từng mục có tiêu đề rõ ràng (số lượng/thời hạn, gia hạn, xử lý trễ hạn, hành vi bị cấm...), nên cắt theo đúng ranh giới heading luôn cho 1 chunk = 1 đơn vị ý nghĩa trọn vẹn, không phụ thuộc việc tinh chỉnh `chunk_size`/separator như `RecursiveChunker`. Bằng chứng rõ nhất: câu 4 ("ký túc xá cấm hành vi nào") — cả `FixedSizeChunker` (Khôi) lẫn `RecursiveChunker` mặc định (Đức) đều tách mục "Hành vi bị cấm" ra khỏi top-3, chỉ `HeadingChunker` và `RecursiveChunker` đã tinh chỉnh kỹ (Trung) mới lấy trọn được. Bài học chung: **kích thước & separator (hoặc cấu trúc tài liệu) nên khớp với hình dạng thật của corpus**, không nên giữ nguyên tham số mặc định — với corpus Markdown nhiều heading ngắn như K3, chunk theo heading/section là lựa chọn tự nhiên nhất.

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

> **Cập nhật:** cả **5/5 thành viên** giờ đã chạy `bench.py` trên đúng bộ 5 câu hỏi chung này (Đức và Sơn vừa hoàn thiện `bench.py` + sửa vị trí code; Hiển vừa chạy lại đúng bộ câu hỏi chung thay cho bộ câu hỏi riêng ở bản nháp trước).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Đúng tài liệu (doc_id) trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Sinh viên mượn tối đa bao nhiêu tài liệu thư viện, trong bao lâu? | Đỗ Tuấn Sơn (top-1, 0,7626) | **Có**: Hiển (0,353) · Đức (0,570) · Sơn (0,763) · Trung (0,540) — **Không**: Khôi (sai cả top-3, dùng MockEmbedder) | Mọi backend có ngữ nghĩa thật (TF-IDF trở lên) đều tìm đúng; chỉ MockEmbedder của Khôi thất bại — minh hoạ rõ ràng nhất về giới hạn của mock embedding. |
| 2 | Điều kiện xét học bổng khuyến khích học tập loại khá? | Trần Đức Bảo Trung (top-1, 0,6515) | **Có**: Hiển (0,478) · Đức (0,620) · Sơn (0,620) · Trung (0,652) — **Không**: Khôi | |
| 3 | Quy trình hủy một học phần đã đăng ký gồm những bước nào? | *(không ai đạt trọn vẹn ở top-1)* | **Có** đúng tài liệu ở cả 4 (Hiển, Đức, Sơn, Trung) nhưng **không ai** có đúng đoạn "Quy trình hủy học phần" (nộp phiếu tại Phòng QLĐT) ngay ở top-1 — đoạn đó luôn rơi vào top-2/top-3 cùng tài liệu. Khôi: đúng tài liệu chỉ ở top-2, MockEmbedder | **Phát hiện chung đáng chú ý nhất:** bất kể chiến lược nào, `course-registration.md` luôn bị tách "mục thời gian/mốc hủy" và "mục quy trình hủy" thành 2 chunk khác nhau — không chunker nào trong nhóm gộp được cả hai vào 1 chunk duy nhất. Agent vẫn trả lời đúng vì dùng top-3 làm context, nhưng đây là bằng chứng cụ thể cho thấy ranh giới `##` của tài liệu này không khớp hoàn toàn với ranh giới ngữ nghĩa của câu hỏi. |
| 4 | Ký túc xá cấm những hành vi nào? | Đỗ Tuấn Sơn (top-1, 0,389, đúng **nguyên mục** "Hành vi bị cấm") | **Có** đúng tài liệu: Hiển, Đức, Sơn, Trung — nhưng **Đức đúng tài liệu mà sai chunk** (mục "Hành vi bị cấm" không lọt top-3 dù `dormitory-rules` có mặt — failure case cụ thể, xem `REPORT_CANHAN.md` của Đức). **Không**: Khôi | Câu phân hoá rõ nhất giữa các chiến lược: chỉ `HeadingChunker` (Sơn) tách đúng nguyên mục cần thiết một cách tất định; các chunker khác phụ thuộc may rủi vào việc mục đó có bị gộp/tách đúng chỗ hay không. |
| 5 | Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không? | Đỗ Tuấn Sơn (top-1, 0,741) | **Có** ở cả 5: Hiển (0,623) · Đức (0,683) · Sơn (0,741) · Trung (0,727) · Khôi (chỉ ở top-3, 0,245) | Câu "ngoại lệ" (đối lập câu 1) — mọi chiến lược đều tìm ra `library-services-faculty`; đây là câu duy nhất Khôi cũng có đúng tài liệu (dù xếp hạng thấp), cho thấy MockEmbedder không phải lúc nào cũng thất bại. |

**Tổng điểm truy xuất theo `docs/SCORING.md` (2đ/câu):** Khôi 4/10 · Hiển 9/10 · Đức 9/10 · Sơn 10/10 · Trung 10/10.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, đặc biệt ở câu 1 và câu 5 — đây là cặp câu hỏi "đối lập" dùng chung một trang nguồn thư viện nhưng khác `audience` (sinh viên: 3 tài liệu/10 ngày, có gia hạn; giảng viên/cán bộ: 3 tài liệu/180 ngày, không gia hạn). A/B test của Khôi cho thấy filter loại đúng 3 tài liệu sai đối tượng khỏi tập ứng viên, nhưng **rank vẫn có thể sai** nếu embedding không mang ngữ nghĩa thật (MockEmbedder) — kết quả của Trung (embedding thật + có filter ở câu 1) cho top-1 đúng ngay, còn Khôi (embedding giả + filter đúng) vẫn chọn sai top-1. Kết luận: **metadata filter thu hẹp đúng không gian tìm kiếm, nhưng không thay thế được chất lượng embedding** — cần cả hai để retrieval đúng.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. Cùng một corpus 8 tài liệu nhưng 5 chiến lược cho số lượng chunk rất khác nhau (19–29 chunk) và điểm truy xuất trải từ 4/10 đến 10/10 — chứng minh **chunking quyết định retrieval nhiều hơn** chỉ đổi embedding.
> 2. Chất lượng embedding và metadata filter là **hai trục độc lập**: filter đúng (Khôi, câu 1) vẫn cho rank sai nếu backend không có ngữ nghĩa thật (MockEmbedder); ngược lại backend tốt (TF-IDF của Hiển, HashingVectorizer của Trung) mới phát huy tác dụng khi kết hợp với filter.
> 3. Vì `KnowledgeBaseAgent` luôn ghép **cả top-3** vào context (không chỉ top-1), câu trả lời cuối cùng vẫn có thể đúng dù chunk đúng chỉ nằm ở top-2/top-3 (câu 3 và câu 5 ở cả Khôi và Trung) — top_k > 1 có tác dụng "vớt" các trường hợp rank chưa hoàn hảo.

**Bài học rút ra khi so sánh trong nhóm:**
> Cắt theo ranh giới ngữ nghĩa tự nhiên của tài liệu (câu ở `SentenceChunker`, mục ở `HeadingChunker`, hoặc separator ưu tiên câu/mệnh đề như cấu hình của Trung) luôn cho chunk mạch lạc hơn cắt cứng theo ký tự (`FixedSizeChunker`) hoặc dùng nguyên tham số mặc định của `RecursiveChunker` — corpus K3 gồm các trang quy định Markdown nhiều heading/dòng ngắn nên separator mặc định (`\n\n → \n → ...`) dễ tách sớm ở mỗi dòng heading, tạo chunk vụn (đúng như Baseline Analysis ở mục 2 đã chỉ ra). Bài học thứ hai: **báo cáo và code phải đồng bộ khi nộp** — 2/5 thành viên (Đức, Sơn) ban đầu viết report rất chi tiết nhưng đặt code triển khai vào thư mục cá nhân thay vì đè lên `src/chunking.py`/`store.py`/`agent.py` gốc mà `tests/test_solution.py` thực sự import, nên `pytest` từng fail dù report ghi "42 passed"; cả hai đã tự sửa lại đúng vị trí và xác nhận 42/42 pass thật (2026-08-03) — nhưng bài học vẫn còn giá trị: nên rà lại đúng cấu trúc thư mục **trước khi** viết report, không phải sau.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Chốt cứng **một bộ 5 câu hỏi + gold answer dùng chung** ngay từ đầu (kèm quy ước không tự đổi câu hỏi) trước khi ai bắt đầu viết `bench.py` — ban đầu Hiển và Đức tự chạy benchmark trên bộ câu hỏi khác bộ chung của nhóm nên chưa gộp được ngay vào bảng so sánh 5 người, phải chạy lại sau đó mới thống nhất được. Đồng thời nên thống nhất từ đầu quy ước vị trí code nộp bài (đè lên file gốc `src/`, không tạo thư mục cá nhân riêng) để tránh đúng lỗi mà Đức và Sơn từng gặp.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
