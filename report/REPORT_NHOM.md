# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** K3-B51

**Thành viên:** Phạm Nguyễn Đăng Khôi, Vi Minh Hiển, Nguyễn Đăng Đức, Đỗ Tuấn Sơn, Trần Đức Bảo Trung

**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Quy định và dịch vụ đại học dành cho sinh viên, giảng viên và nhân viên: đăng ký học phần, học bổng, học phí, thư viện, ký túc xá và quy định nơi làm việc.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đăng ký và hủy học phần | [UEH](https://daotao.ueh.edu.vn/quy-dinh-dang-ky-va-huy-hoc-phan-da-dang-ky-cua-sinh-vien-dai-hoc-chinh-quy-trong-dao-tao-theo-he-thong-tin-chi-tai-truong-dai-hoc-kinh-te-tp-ho-chi-minh/) | 2026-08-03 / not-stated | 1.300 | `student`, `academic-affairs`, `registration` |
| 2 | Nội quy ký túc xá | [HaUI](https://ktx.haui.edu.vn/vn/html/noi-quy) | 2026-08-03 / not-stated | 856 | `student`, `student-affairs`, `housing` |
| 3 | Chế độ làm việc của giảng viên | [ĐHQGHN](https://vnu.edu.vn/quy-dinh-ve-che-do-lam-viec-doi-voi-giang-vien-tai-dhqghn-post30072.html) | 2026-08-03 / not-stated | 705 | `faculty`, `academic-affairs`, `workload` |
| 4 | Mượn tài liệu — giảng viên/cán bộ | [HUIT](https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien) | 2026-08-03 / not-stated | 488 | `faculty`, `library`, `borrowing-policy` |
| 5 | Mượn tài liệu — sinh viên | [HUIT](https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien) | 2026-08-03 / not-stated | 454 | `student`, `library`, `borrowing-policy` |
| 6 | Học bổng khuyến khích học tập | [UEH](https://daotao.ueh.edu.vn/quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap-cho-sinh-vien-dai-hoc-chinh-quy/) | 2026-08-03 / not-stated | 904 | `student`, `academic-affairs`, `scholarship` |
| 7 | Quy chế văn hóa công sở | [Học viện Ngân hàng](https://hvnh.edu.vn/tccb/vi/danh-gia-xep-loai-ccvc/quy-che-van-hoa-cong-so-20.html) | 2026-08-03 / QĐ-40/2008 | 825 | `staff`, `administration`, `workplace-conduct` |
| 8 | Chính sách miễn, giảm học phí | [TDTU](https://student.tdtu.edu.vn/chinh-sach/mien-giam-hoc-phi) | 2026-08-03 / NĐ-238/2025 | 914 | `student`, `finance`, `tuition` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Corpus chỉ chứa nguồn công khai, không yêu cầu đăng nhập và không chứa dữ liệu cá nhân hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` trong metadata; 7/7 URL duy nhất đã được kiểm tra truy cập ngày 2026-08-03.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `library-services-student` | Nhận diện tài liệu và hỗ trợ xóa/lọc chunk theo tài liệu. |
| `title` | string | `Quy định mượn tài liệu thư viện` | Hiển thị và truy vết kết quả. |
| `source_url` | string | URL trang chính thức | Kiểm chứng nguồn của câu trả lời. |
| `retrieved_at` | string | `2026-08-03` | Kiểm tra thời điểm thu thập. |
| `document_version` | string | `NĐ-238/2025` | Theo dõi phiên bản hoặc hiệu lực. |
| `audience` | string | `student` | Lọc đúng đối tượng sinh viên/giảng viên/nhân viên. |
| `department` | string | `library` | Thu hẹp theo đơn vị phụ trách. |
| `category` | string | `borrowing-policy` | Thu hẹp theo loại dịch vụ hoặc quy định. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — Vi Minh Hiển**
- **Loại chiến lược:** `SentenceChunker(max_sentences_per_chunk=3)`
- **Mô tả & lý do chọn:** Chia theo ranh giới câu giúp mỗi chunk giữ được câu hoàn chỉnh, phù hợp với các quy định ngắn và câu hỏi cần lấy điều kiện, thời hạn cụ thể.
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên đã đóng học phí và muốn hủy học phần để rút học phí phải nộp phiếu trước thời điểm nào? | Trước ngày thông báo thời khóa biểu chính thức 10 ngày. | `course-registration`, mục “Thời gian đăng ký/Quy trình hủy học phần” |
| 2 | Sinh viên đạt loại xuất sắc được nhận học bổng bằng bao nhiêu lần mức học bổng loại khá? | Bằng 1,5 lần mức học bổng loại khá. | `scholarship-incentive`, mục “Mức học bổng” |
| 3 | Sinh viên được mượn tối đa bao nhiêu tài liệu, trong bao lâu và được gia hạn thế nào? | Tối đa 3 tài liệu trong 10 ngày; gia hạn tối đa 1 lần, thêm 10 ngày. Dùng lọc `audience=student`, `department=library`. | `library-services-student`, mục “Số lượng và thời hạn mượn/Gia hạn” |
| 4 | Đối tượng sinh viên nào được giảm 70% học phí? | Sinh viên dân tộc thiểu số ở thôn/bản đặc biệt khó khăn hoặc xã khu vực III vùng dân tộc và miền núi. | `tuition-exemption`, mục “Đối tượng giảm 70% học phí” |
| 5 | Khách muốn ở lại qua đêm trong ký túc xá phải làm gì? | Phải đăng ký và làm đơn bảo lãnh trước. | `dormitory-rules`, mục “Giờ giấc và khách” |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

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
