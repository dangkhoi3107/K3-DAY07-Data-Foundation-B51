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
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** *(Hiển tự điền sau khi chạy `bench.py`)*
- **Code snippet (nếu custom):** không cần, dùng `SentenceChunker` có sẵn.

**Thành viên 3 — Nguyễn Đăng Đức (2A202601787)**
- **Loại chiến lược:** RecursiveChunker (separator mặc định: đoạn → dòng → câu → từ → ký tự)
- **Mô tả & lý do chọn:** *(Đức tự điền sau khi chạy `bench.py`)*
- **Code snippet (nếu custom):** không cần, dùng `RecursiveChunker` có sẵn với separator mặc định.

**Thành viên 4 — Đỗ Tuấn Sơn (2A202601051)**
- **Loại chiến lược:** custom — chunker theo heading/section (bắt buộc theo `K3_VARIANT.md`)
- **Mô tả & lý do chọn:** *(Sơn tự điền — nên so sánh trực tiếp với nhận xét "chunk vụn" của `RecursiveChunker` ở phần Baseline phía trên, vì đây chính là vấn đề chunker heading/section được kỳ vọng khắc phục)*
- **Code snippet (nếu custom):**
```python
# Sơn dán code chunker heading/section của mình vào đây
```

**Thành viên 5 — Trần Đức Bảo Trung (2A202601269)**
- **Loại chiến lược:** RecursiveChunker (tham số khác Nguyễn Đăng Đức)
- **Mô tả & lý do chọn:** *(Trung tự điền, nêu rõ khác Đức ở tham số nào — chunk_size, separator...)*
- **Code snippet (nếu custom):** không cần, dùng `RecursiveChunker` có sẵn với tham số khác.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Phạm Nguyễn Đăng Khôi | FixedSizeChunker (300/60) | 4/10 *(2 câu đúng ở top-2/top-3 × 2đ = 4, xem `REPORT_CANHAN.md` mục 5 — dùng MockEmbedder, chưa phản ánh ngữ nghĩa thật)* | Đơn giản, chunk đều nhau, dễ debug | Cắt cứng theo ký tự, có thể chia đôi câu; không phân biệt được ranh giới ngữ nghĩa |
| Vi Minh Hiển | SentenceChunker | *(chờ Hiển)* | | |
| Nguyễn Đăng Đức | RecursiveChunker (mặc định) | *(chờ Đức)* | | |
| Đỗ Tuấn Sơn | Chunker heading/section | *(chờ Sơn)* | | |
| Trần Đức Bảo Trung | RecursiveChunker (tham số khác) | *(chờ Trung)* | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

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
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

> Bảng này cần kết quả từ **cả 5 người** mới điền được (phải so sánh chiến lược nào thắng ở từng câu). Dữ liệu thô của Phạm Nguyễn Đăng Khôi (top-3 từng câu, score, agent answer) đã có sẵn ở `REPORT_CANHAN.md` mục 5 — 4 bạn còn lại gửi phần tương ứng của mình theo đúng form đó rồi điền tiếp bảng trên.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu — nên tổng hợp từ A/B test (có filter vs không filter) của từng người ở câu hỏi 1.*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
