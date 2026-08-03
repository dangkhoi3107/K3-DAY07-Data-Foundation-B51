# Checklist Lab 07 — K3 (Dịch vụ / Quy định Đại học) — Nhóm 5 người

> File này chỉ để nhóm theo dõi tiến độ. Không phải file nộp bắt buộc, nhưng nên cập nhật liên tục trong buổi lab.

## 0. Tình trạng repo hiện tại (cập nhật 2026-08-03: đã kiểm tra trực tiếp cả 5 nhánh trên remote — xem mục 10)

- [ ] **Python 3.11 đúng chuẩn lab** — máy này vẫn chỉ có Python 3.14.6, chưa cài 3.11 (`py -3.11 --version` báo lỗi "No runtime installed"). Code chỉ dùng thư viện chuẩn (không có gì riêng cho 3.11) nên **đã chạy thử và pass 42/42 trên 3.14** — không chặn tiến độ, nhưng nên cài 3.11 + tạo `.venv` đúng chuẩn trước khi nộp để khớp môi trường cả nhóm.
- [ ] **`.venv` riêng cho repo** — hiện đang chạy bằng Python global + `pip install` global (`python-dotenv`), chưa có `.venv/`. Nên tạo `.venv` sạch trước khi nộp (xem mục 2).
- [x] **`src/chunking.py`, `src/store.py`, `src/agent.py` đã code xong cho repo này (Phạm Nguyễn Đăng Khôi)** — `python -m pytest tests -v` → **42 passed**. Chi tiết logic từng Task xem `docs/HUONG_DAN_IMPLEMENTATION.md`.
- [x] **Corpus 8 tài liệu nguồn thật đã lưu vào repo này** (`data/k3_university/*.md` + `sources.csv`, xem mục 3b) — đã chạy script kiểm CP2: 8/8 file OK, csv khớp, `audience` có 3 giá trị (student/faculty/staff).
- [x] **`main.py` chạy end-to-end được** trên repo này (đã thử với câu hỏi thư viện, xem log ở cuối mục 1b phần Khôi). Trên Windows nếu gặp `UnicodeEncodeError` khi in tiếng Việt, set `PYTHONIOENCODING=utf-8` trước khi chạy — không phải lỗi code.
- [x] **`report/REPORT_CANHAN.md` và `report/REPORT_NHOM.md` của Khôi đã điền nội dung thật** — gồm cả bảng so sánh 5 người ở `REPORT_NHOM.md` (mục 2–4), gom từ dữ liệu thật đọc trực tiếp trên 4 nhánh còn lại. Kết quả: Hiển và Trung xong (code sạch, test 42/42); Đức và Sơn còn lỗi chặn (code thật nằm sai thư mục nên test gốc vẫn fail) — chi tiết ở mục 10 bên dưới và trong `REPORT_NHOM.md`.
- [x] **`docs/HUONG_DAN_IMPLEMENTATION.md` đã tạo** — hướng dẫn chi tiết Task 1–6 (không phải code hoàn chỉnh) để 4 bạn Hiển/Đức/Sơn/Trung tự code.
- [ ] `.env` chưa tồn tại (không bắt buộc trừ khi dùng local/openai embedding).

---

## 1. Phân vai trong nhóm (5 người)

Lưu ý quan trọng: **mỗi người vẫn phải tự code đủ Task 1–6 và tự đạt 42/42 test trong repo riêng của mình** (`DAY07-MSSV-HoVaTen`). Vai trò dưới đây chỉ là **trách nhiệm điều phối thêm** cho phần nộp chung của nhóm (corpus, 5 query, `REPORT_NHOM.md`) — không ai code hộ ai.

| Vai trò | Người phụ trách | MSSV | Việc điều phối chính |
|---|---|---|---|
| Data curator | Vi Minh Hiển | 2A202601743 | Chốt phạm vi cụ thể, tìm đủ 5–10 nguồn công khai thật, giữ `sources.csv` và front matter khớp 1–1 |
| Benchmark owner | Nguyễn Đăng Đức | 2A202601787 | Soạn 5 query + gold answer trích từ corpus, không đổi query sau khi đã thấy kết quả |
| Demo coordinator | Phạm Nguyễn Đăng Khôi | 2A202601243 | Gom bảng so sánh 5 strategy, điều phối kịch bản demo 6–8 phút, canh giờ từng phần |
| Strategy owner ×5 | Cả 5 người | — | Mỗi người 1 strategy chunking khác nhau, xem bảng mục 6 |

Đỗ Tuấn Sơn (2A202601051) và Trần Đức Bảo Trung (2A202601269) không giữ vai điều phối riêng — tập trung vào core coding cá nhân và strategy được phân công, đồng thời hỗ trợ Data curator/Benchmark owner khi cần (đọc nguồn, kiểm gold answer chéo).

---

## 1b. Chi tiết công việc từng người

Mỗi người **đều làm chung 4 việc cốt lõi** (Setup → Task 1–6 → 42/42 → `REPORT_CANHAN.md`) trong repo riêng của mình, cộng thêm phần điều phối/strategy riêng dưới đây.

⚠️ **Vì sao 4 bạn dưới đây không có sẵn code, chỉ có hướng dẫn:** phần `src/` chấm điểm cá nhân theo từng repo — nếu 5 repo có code giống hệt nhau sẽ bị nghi đạo bài, và report cá nhân hỏi bạn tự giải thích logic (không tự viết thì không trả lời được thật). Tôi đã soạn `docs/HUONG_DAN_IMPLEMENTATION.md` — hướng dẫn từng bước chi tiết hơn hẳn README gốc — để 4 bạn code nhanh mà vẫn tự tay làm. File này chỉ có ở repo của Khôi; **hãy gửi nội dung file đó cho 4 bạn** (copy nguyên văn qua Zalo/Messenger/Drive) vì mỗi người code trong repo riêng.

### Phạm Nguyễn Đăng Khôi — 2A202601243 — Demo coordinator
- [x] Core coding cá nhân: Task 1–6 đã code xong, `python -m pytest tests -v` → **42 passed**. `main.py "Chunking là gì?"` chạy được (Windows cần `PYTHONIOENCODING=utf-8`).
- [ ] `report/REPORT_CANHAN.md` — vẫn là khung, chưa điền (warm-up, hướng tiếp cận, output pytest, 5 kết quả retrieval riêng)
- [x] Đã copy 8 file corpus + `sources.csv` vào `data/k3_university/` của repo này
- [ ] Strategy riêng cho `bench.py`: **`FixedSizeChunker`** với `chunk_size`/`overlap` tự chọn — **`bench.py` chưa viết**
- [ ] Sau CHECKPOINT 6: gom bảng so sánh 5 strategy từ 4 bạn còn lại vào `REPORT_NHOM.md`
- [ ] Soạn kịch bản demo 6–8 phút, chia thời lượng cho từng phần (mục 8), canh giờ khi luyện tập demo thử
- [ ] Repo nộp: `DAY07-2A202601243-PhamNguyenDangKhoi` (repo hiện tại — kiểm lại tên trên GitHub đã đổi khớp)
- [ ] `.venv` + Python 3.11 đúng chuẩn (hiện đang chạy bằng Python 3.14 global, xem mục 0)

### Vi Minh Hiển — 2A202601743 — Data curator
- [ ] Core coding cá nhân: Setup → tự code Task 1–6 theo `docs/HUONG_DAN_IMPLEMENTATION.md` → 42/42 → `REPORT_CANHAN.md`
- [x] Phạm vi + nguồn đã chốt sẵn (mục 3b) — chỉ cần copy 8 file + `sources.csv` vào `data/k3_university/` trong repo riêng
- [ ] Kiểm tra lại các `source_url` còn truy cập được không trước khi nộp (nội dung đã paraphrase, không copy nguyên văn)
- [ ] Strategy riêng cho `bench.py`: **`SentenceChunker`**
- [ ] Repo nộp: `DAY07-2A202601743-ViMinhHien`

### Nguyễn Đăng Đức — 2A202601787 — Benchmark owner
- [ ] Core coding cá nhân: Setup → tự code Task 1–6 theo `docs/HUONG_DAN_IMPLEMENTATION.md` → 42/42 → `REPORT_CANHAN.md`
- [x] 5 query + gold answer đã soạn sẵn (mục 3b) — dán vào `REPORT_NHOM.md`, có sẵn 1 query bắt buộc filter `audience=student`
- [ ] Rà lại 5 query 1 lần cho chắc gold answer đúng ý nhóm; nếu cả nhóm đồng ý thì **không sửa lại** sau khi ai đó đã chạy benchmark
- [ ] Strategy riêng cho `bench.py`: **`RecursiveChunker`** với separator mặc định (đoạn → dòng → câu → từ → ký tự)
- [ ] Repo nộp: `DAY07-2A202601787-NguyenDangDuc`

### Đỗ Tuấn Sơn — 2A202601051
- [ ] Core coding cá nhân: Setup → tự code Task 1–6 theo `docs/HUONG_DAN_IMPLEMENTATION.md` → 42/42 → `REPORT_CANHAN.md`
- [ ] Strategy riêng cho `bench.py`: **chunker theo heading/section (tự viết thêm, không có trong `docs/HUONG_DAN_IMPLEMENTATION.md`)** — đây là chunker **bắt buộc** theo `K3_VARIANT.md`, tách trước tại mỗi heading, section nào dài quá ngưỡng thì hạ xuống `RecursiveChunker`; nhớ gắn lại tiêu đề vào từng mảnh con khi cắt nhỏ một section dài (dữ liệu mục 3b đã có heading `##` sẵn trong mỗi file, phù hợp để test chunker này)
- [ ] Hỗ trợ Vi Minh Hiển: kiểm tra lại nguồn trước khi nộp
- [ ] Repo nộp: `DAY07-2A202601051-DoTuanSon`

### Trần Đức Bảo Trung — 2A202601269
- [ ] Core coding cá nhân: Setup → tự code Task 1–6 theo `docs/HUONG_DAN_IMPLEMENTATION.md` → 42/42 → `REPORT_CANHAN.md`
- [ ] Strategy riêng cho `bench.py`: **`RecursiveChunker`** nhưng khác hẳn tham số của Nguyễn Đăng Đức — ví dụ `chunk_size` nhỏ hơn/lớn hơn rõ rệt, hoặc đổi thứ tự/tập separator — để hai kết quả Recursive thực sự so sánh được điều gì đó khác nhau
- [ ] Hỗ trợ Nguyễn Đăng Đức: kiểm tra chéo gold answer có thực sự chỉ trích được từ corpus (không suy đoán ngoài tài liệu)
- [ ] Repo nộp: `DAY07-2A202601269-TranDucBaoTrung`

---

## 2. Setup môi trường (mỗi người tự làm)

- [ ] Kiểm tra `py -3.11 --version` chạy được (cài Python 3.11 nếu chưa có)
- [ ] Tạo venv: `py -3.11 -m venv .venv`
- [ ] Kích hoạt: `.venv\Scripts\Activate.ps1` (nếu PowerShell chặn: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` chạy 1 lần)
- [ ] `python -m pip install -r requirements.txt`
- [ ] `python -m pytest tests -v` → phải ra **31 failed, 11 passed**
- [ ] ✅ CHECKPOINT 1 đạt

---

## 3. Chuẩn bị dữ liệu (nhóm — Data curator điều phối)

- [ ] Đọc `docs/DATA_COLLECTION.md` và `K3_VARIANT.md`
- [ ] Domain: **Dịch vụ/quy định đại học** (đăng ký môn, học phí, học bổng, thư viện, ký túc xá, ...) — chọn phạm vi cụ thể trong đó
- [ ] Thu thập **5–10 tài liệu công khai thật** (thay 2 file mẫu hiện có + thêm mới), lưu vào `data/k3_university/*.md`
- [ ] Mỗi file có front matter đủ: `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `audience` (student/faculty/staff/all), + ít nhất 1 metadata khác (category, department, effective_date...)
- [ ] `audience` phải có **ít nhất 2 giá trị khác nhau** trong corpus (không thì filter vô dụng)
- [ ] Cập nhật `data/k3_university/sources.csv` khớp 1–1 với các file `.md` (bỏ URL/license placeholder `example.edu` / `example-template-replace-me`)
- [ ] Làm sạch nội dung crawl thô (bỏ menu/footer/tin không liên quan) trước khi lưu
- [ ] (Tuỳ chọn) Dùng `scripts/fetch_public_pages.py` nếu crawl — có kiểm `robots.txt` sẵn
- [ ] Chạy script kiểm checklist mục 6 của `docs/DATA_COLLECTION.md` (đoạn Python kiểm metadata) → mọi dòng phải "OK"
- [ ] Điền bảng **Data Inventory** + **Metadata Schema** vào `report/REPORT_NHOM.md`
- [ ] ✅ CHECKPOINT 2 đạt

---

## 3b. Corpus đã chọn sẵn — 8 tài liệu nguồn thật (chỉ cần lưu & dán)

**Chủ đề đã chốt:** Dịch vụ & quy định đại học cho nhiều đối tượng — đăng ký học phần, học bổng, học phí, ký túc xá, thư viện, chế độ làm việc giảng viên, văn hóa công sở cán bộ. Lấy từ 6 trường thật (UEH, HaUI, TDTU, HUIT, VNU, HVNH), toàn bộ là trang công khai, không cần đăng nhập, đã kiểm tra truy cập được lúc thu thập (2026-08-03).

⚠️ **QUAN TRỌNG — áp dụng cho cả 5 repo:** đây là corpus dùng chung của nhóm. **Mỗi người trong 5 người đều phải tự copy 8 file bên dưới + `sources.csv` vào đúng `data/k3_university/` trong repo riêng của mình** (không chỉ riêng repo này), vì mỗi người nộp bài độc lập nhưng dùng chung dữ liệu để benchmark so sánh công bằng được.

Trước khi nộp, nếu còn thời gian, **mở lại từng `source_url` một lần** để chắc trang chưa bị gỡ/đổi — nội dung bên dưới đã được rút gọn/diễn đạt lại (paraphrase) từ trang gốc, không copy nguyên văn.

### Bảng tổng quan 8 tài liệu

| # | doc_id | Tên file (lưu vào `data/k3_university/`) | audience | Nguồn (trường) |
|---|--------|---|---|---|
| 1 | `course-registration` | `course-registration.md` | student | UEH |
| 2 | `scholarship-incentive` | `scholarship-incentive.md` | student | UEH |
| 3 | `dormitory-rules` | `dormitory-rules.md` | student | HaUI |
| 4 | `tuition-exemption` | `tuition-exemption.md` | student | TDTU |
| 5 | `library-services-student` | `library-services-student.md` | student | HUIT |
| 6 | `library-services-faculty` | `library-services-faculty.md` | faculty | HUIT (cùng trang, khác đối tượng) |
| 7 | `faculty-workload` | `faculty-workload.md` | faculty | VNU (ĐHQGHN) |
| 8 | `staff-workplace-culture` | `staff-workplace-culture.md` | staff | HVNH |

File #5 và #6 **cùng một trang nguồn** nhưng tách theo đối tượng vì hai đối tượng có quy định mượn sách khác hẳn nhau (10 ngày vs 180 ngày) — đây chính là cặp tài liệu dùng cho câu hỏi bắt buộc filter ở mục 6. Ba tài liệu còn lại (`tuition-exemption`, `faculty-workload`, `staff-workplace-culture`) không nằm trong 5 câu hỏi benchmark chính — chúng đóng vai trò tài liệu "nhiễu" hợp lệ, giúp phần phân tích ở CP6 thực chất hơn (nếu retrieval lẫn sang các tài liệu này ở câu hỏi khác thì đó là bằng chứng tốt để phân tích).

> ⚠️ File `course-registration.md` và `library-services-student.md` (đổi tên từ `library-services.md`) hiện đã có sẵn trong repo này nhưng nội dung là **placeholder mẫu** (`source_url: example.edu`) — cần **ghi đè toàn bộ nội dung** bằng bản dưới đây, xoá dòng chú thích "dữ liệu khởi động" cũ.

---

#### 1. `data/k3_university/course-registration.md`

```markdown
---
doc_id: course-registration
title: Đăng ký và hủy học phần
audience: student
department: academic-affairs
category: registration
source_url: https://daotao.ueh.edu.vn/quy-dinh-dang-ky-va-huy-hoc-phan-da-dang-ky-cua-sinh-vien-dai-hoc-chinh-quy-trong-dao-tao-theo-he-thong-tin-chi-tai-truong-dai-hoc-kinh-te-tp-ho-chi-minh/
retrieved_at: 2026-08-03
document_version: "not-stated"
---

# Đăng ký và hủy học phần

## Thời gian đăng ký
Sinh viên đăng ký học phần theo lịch được thông báo riêng cho từng học kỳ và từng khóa. Đăng ký bổ sung phải hoàn tất trước ngày công bố thời khóa biểu chính thức 10 ngày. Việc hủy học phần chưa đóng học phí, hoặc đã đóng nhưng xin rút học phí, cũng phải thực hiện trước mốc 10 ngày này. Nếu học phần đã đóng học phí và không rút, sinh viên chỉ được hủy trước ngày thi kết thúc học phần 10 ngày.

## Điều kiện đăng ký
Sinh viên phải còn trong thời gian đào tạo được phép, thỏa mãn điều kiện học phần tiên quyết, học trước hoặc song hành, và lớp học phần phải còn chỉ tiêu tiếp nhận. Học phần đang có điểm X (chưa nhận điểm thi) thì sinh viên không được đăng ký lại. Số tín chỉ đăng ký mỗi học kỳ phải nằm trong khung tối thiểu – tối đa do trường quy định, áp dụng cho cả học kỳ chính và học kỳ phụ.

## Quy trình hủy học phần
Sinh viên nộp Phiếu đề nghị hủy học phần tại Phòng Quản lý đào tạo trong đúng thời hạn quy định; yêu cầu nộp ngoài thời hạn sẽ không được giải quyết. Phòng Tài chính hoàn trả học phí theo danh sách đã được xác nhận hủy.

## Đóng học phí
Học phí phải được đóng trong thời gian quy định của học kỳ. Sau hạn chót, trường tự động hủy các học phần chưa đóng học phí; học phần đăng ký bổ sung phải đóng học phí ngay sau khi đăng ký.
```

#### 2. `data/k3_university/scholarship-incentive.md`

```markdown
---
doc_id: scholarship-incentive
title: Học bổng khuyến khích học tập
audience: student
department: academic-affairs
category: scholarship
source_url: https://daotao.ueh.edu.vn/quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap-cho-sinh-vien-dai-hoc-chinh-quy/
retrieved_at: 2026-08-03
document_version: "not-stated"
---

# Học bổng khuyến khích học tập

## Điều kiện xét
Sinh viên đang trong 8 học kỳ chính của khóa học, có kết quả học tập và rèn luyện từ loại khá trở lên, không bị kỷ luật từ mức khiển trách trở lên, đạt điểm 5/10 trở lên ở tất cả học phần trong học kỳ xét, và có số tín chỉ đăng ký bằng hoặc lớn hơn kế hoạch đào tạo mới đủ điều kiện tham gia xét học bổng khuyến khích học tập.

## Mức học bổng
Sinh viên đạt loại khá (điểm trung bình tích lũy khá, điểm rèn luyện khá) nhận 1 lần mức học phí theo tín chỉ kế hoạch. Sinh viên đạt loại giỏi (điểm trung bình tích lũy giỏi, điểm rèn luyện tốt) nhận 1,2 lần mức khá. Sinh viên đạt loại xuất sắc ở cả hai tiêu chí nhận 1,5 lần mức khá.

## Quy trình xét
Hội đồng xét học bổng họp ngay sau khi có điểm học kỳ. Phòng Quản lý Đào tạo công bố danh sách và tiếp nhận khiếu nại. Phòng Tài chính thông báo thời gian, địa điểm nhận học bổng cho sinh viên đủ điều kiện.
```

#### 3. `data/k3_university/dormitory-rules.md`

```markdown
---
doc_id: dormitory-rules
title: Nội quy ký túc xá
audience: student
department: student-affairs
category: housing
source_url: https://ktx.haui.edu.vn/vn/html/noi-quy
retrieved_at: 2026-08-03
document_version: "not-stated"
---

# Nội quy ký túc xá

## Giờ giấc và khách
Sinh viên nội trú không được thức khuya quá 23h30. Không được tiếp khách trong phòng riêng; bạn bè đến thăm phải gặp tại khu vực chỉ định. Khách muốn ở lại qua đêm phải đăng ký và làm đơn bảo lãnh trước.

## Hành vi bị cấm
Ký túc xá cấm uống rượu, bia; tàng trữ vũ khí, hung khí, chất nổ, ma túy; nấu ăn hoặc tổ chức sinh nhật trong phòng; đánh bài, cờ bạc; gây gổ, tụ tập bè phái; và vượt rào, trèo tường.

## Xử lý vi phạm
Tùy theo mức độ, sinh viên vi phạm bị phê bình, khiển trách, cảnh cáo, hủy hợp đồng thuê nhà ở nội trú, buộc thôi học, hoặc bị đề nghị truy tố trước pháp luật nếu vi phạm nghiêm trọng.

## Quy định khác
Sinh viên có trách nhiệm bảo vệ tài sản chung và bồi thường nếu gây thiệt hại, duy trì vệ sinh và trật tự chung, đồng thời tuân thủ quy định sử dụng điện, nước, internet trong ký túc xá.
```

#### 4. `data/k3_university/tuition-exemption.md`

```markdown
---
doc_id: tuition-exemption
title: Chính sách miễn, giảm học phí
audience: student
department: finance
category: tuition
source_url: https://student.tdtu.edu.vn/chinh-sach/mien-giam-hoc-phi
retrieved_at: 2026-08-03
document_version: "NĐ-238/2025"
---

# Chính sách miễn, giảm học phí

Chính sách được xây dựng căn cứ Nghị định số 238/2025/NĐ-CP ngày 03/9/2025 của Chính phủ.

## Đối tượng miễn 100% học phí
Người có công với cách mạng (Anh hùng, thương binh, bệnh binh), con liệt sỹ, con của anh hùng lao động thời kháng chiến, sinh viên khuyết tật, sinh viên mồ côi không có nguồn nuôi dưỡng từ 16 đến 22 tuổi, dân tộc thiểu số rất ít người ở vùng khó khăn đặc biệt, và dân tộc thiểu số thuộc hộ nghèo/cận nghèo (có cha, mẹ hoặc ông bà thuộc diện này).

## Đối tượng giảm 70% học phí
Sinh viên dân tộc thiểu số ở thôn/bản đặc biệt khó khăn, xã khu vực III vùng dân tộc và miền núi.

## Đối tượng giảm 50% học phí
Con của cán bộ, công chức mà cha hoặc mẹ bị tai nạn lao động hoặc mắc bệnh nghề nghiệp đang hưởng trợ cấp.

## Hồ sơ cần nộp
Đơn đề nghị theo mẫu quy định, giấy xác nhận hoặc chứng thực từ cơ quan có thẩm quyền, và bản sao giấy khai sinh khi cần thiết.
```

#### 5. `data/k3_university/library-services-student.md`

```markdown
---
doc_id: library-services-student
title: Quy định mượn tài liệu thư viện — dành cho sinh viên
audience: student
department: library
category: borrowing-policy
source_url: https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien
retrieved_at: 2026-08-03
document_version: "not-stated"
---

# Quy định mượn tài liệu thư viện — dành cho sinh viên

## Số lượng và thời hạn mượn
Sinh viên được mượn tối đa 3 tài liệu trong thời hạn 10 ngày.

## Gia hạn
Mỗi tài liệu được gia hạn tối đa 1 lần, thêm 10 ngày.

## Xử lý trễ hạn
Sinh viên trả trễ hạn phải chịu khoản tiền phạt theo quy định, nộp trực tiếp tại quầy thông tin hoặc trừ vào tài khoản ký quỹ thư viện. Nếu tài liệu quá hạn trên 30 ngày, khoản phạt có thể bị trừ vào học bổng của sinh viên.
```

#### 6. `data/k3_university/library-services-faculty.md`

```markdown
---
doc_id: library-services-faculty
title: Quy định mượn tài liệu thư viện — dành cho giảng viên/cán bộ
audience: faculty
department: library
category: borrowing-policy
source_url: https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien
retrieved_at: 2026-08-03
document_version: "not-stated"
---

# Quy định mượn tài liệu thư viện — dành cho giảng viên/cán bộ

## Số lượng và thời hạn mượn
Giảng viên và cán bộ được mượn tối đa 3 tài liệu trong thời hạn 180 ngày.

## Gia hạn
Không áp dụng gia hạn cho tài liệu mượn theo diện giảng viên/cán bộ; tài liệu phải được thu hồi đúng đợt vào ngày 25/6 và 25/12 hằng năm.

## Xử lý trễ hạn
Giảng viên/cán bộ trả trễ hạn phải chịu khoản tiền phạt theo quy định; khoản phạt được chuyển đến Phòng Kế hoạch — Tài chính và trừ vào lương hằng tháng.
```

#### 7. `data/k3_university/faculty-workload.md`

```markdown
---
doc_id: faculty-workload
title: Chế độ làm việc của giảng viên
audience: faculty
department: academic-affairs
category: workload
source_url: https://vnu.edu.vn/quy-dinh-ve-che-do-lam-viec-doi-voi-giang-vien-tai-dhqghn-post30072.html
retrieved_at: 2026-08-03
document_version: "not-stated"
---

# Chế độ làm việc của giảng viên

## Định mức giờ chuẩn giảng dạy
Giảng viên không giữ chức vụ lãnh đạo có định mức giờ chuẩn giảng dạy từ 200 đến 350 giờ mỗi năm học, tương đương 600–1.050 giờ hành chính. Giảng viên giữ chức vụ lãnh đạo/quản lý áp dụng định mức 270 giờ chuẩn/năm. Giờ giảng dạy trực tiếp trên lớp hoặc trực tuyến thực tế phải đạt tối thiểu 50% tổng định mức.

## Nhiệm vụ ngoài giảng dạy
Giảng viên phải dành tối thiểu 600 giờ mỗi năm cho nghiên cứu khoa học. Thời gian còn lại sau khi hoàn thành giảng dạy và nghiên cứu khoa học được dùng cho phục vụ cộng đồng.

## Tổng thời gian làm việc
Tổng thời gian làm việc của giảng viên là 44 tuần mỗi năm học, tương đương 1.760 giờ hành chính.
```

#### 8. `data/k3_university/staff-workplace-culture.md`

```markdown
---
doc_id: staff-workplace-culture
title: Quy chế văn hóa công sở
audience: staff
department: administration
category: workplace-conduct
source_url: https://hvnh.edu.vn/tccb/vi/danh-gia-xep-loai-ccvc/quy-che-van-hoa-cong-so-20.html
retrieved_at: 2026-08-03
document_version: "QĐ-40/2008"
---

# Quy chế văn hóa công sở

Quy chế được ban hành theo Quyết định số 40/QĐ-HVNH ngày 12/3/2008, áp dụng cho cán bộ, công chức, viên chức.

## Trang phục
Trang phục phải gọn gàng, lịch sự khi làm việc. Nam mặc áo sơ mi, quần âu, đi giày hoặc dép có quai hậu. Nữ mặc áo sơ mi, quần âu, hoặc áo dài truyền thống. Cấm mặc quần jean, quần soóc, áo pull, hoặc váy quá ngắn.

## Tác phong giao tiếp
Cán bộ, viên chức phải có thái độ lịch sự, tôn trọng khi giao tiếp; ngôn ngữ rõ ràng, mạch lạc. Với đồng nghiệp cần trung thực, thân thiện, hợp tác. Điện thoại di động phải tắt trong hội nghị, cuộc họp và giờ lên lớp.

## Ứng xử nơi làm việc
Quy chế cấm hút thuốc trong phòng làm việc/họp, uống rượu bia (trừ khi tiếp khách), quảng cáo thương mại, đánh bài, chơi game, thắp hương, và các hành động thiếu văn hóa khác tại nơi làm việc.
```

---

#### `data/k3_university/sources.csv` (thay thế toàn bộ nội dung file cũ)

```csv
doc_id,file_path,title,source_url,retrieved_at,document_version,license_or_permission
course-registration,data/k3_university/course-registration.md,Đăng ký và hủy học phần,https://daotao.ueh.edu.vn/quy-dinh-dang-ky-va-huy-hoc-phan-da-dang-ky-cua-sinh-vien-dai-hoc-chinh-quy-trong-dao-tao-theo-he-thong-tin-chi-tai-truong-dai-hoc-kinh-te-tp-ho-chi-minh/,2026-08-03,not-stated,public-page-no-login-required
scholarship-incentive,data/k3_university/scholarship-incentive.md,Học bổng khuyến khích học tập,https://daotao.ueh.edu.vn/quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap-cho-sinh-vien-dai-hoc-chinh-quy/,2026-08-03,not-stated,public-page-no-login-required
dormitory-rules,data/k3_university/dormitory-rules.md,Nội quy ký túc xá,https://ktx.haui.edu.vn/vn/html/noi-quy,2026-08-03,not-stated,public-page-no-login-required
tuition-exemption,data/k3_university/tuition-exemption.md,Chính sách miễn giảm học phí,https://student.tdtu.edu.vn/chinh-sach/mien-giam-hoc-phi,2026-08-03,NĐ-238/2025,public-page-no-login-required
library-services-student,data/k3_university/library-services-student.md,Quy định mượn tài liệu thư viện - sinh viên,https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien,2026-08-03,not-stated,public-page-no-login-required
library-services-faculty,data/k3_university/library-services-faculty.md,Quy định mượn tài liệu thư viện - giảng viên/cán bộ,https://thuvien.huit.edu.vn/Page/quy-dinh-su-dung-thu-vien,2026-08-03,not-stated,public-page-no-login-required
faculty-workload,data/k3_university/faculty-workload.md,Chế độ làm việc của giảng viên,https://vnu.edu.vn/quy-dinh-ve-che-do-lam-viec-doi-voi-giang-vien-tai-dhqghn-post30072.html,2026-08-03,not-stated,public-page-no-login-required
staff-workplace-culture,data/k3_university/staff-workplace-culture.md,Quy chế văn hóa công sở,https://hvnh.edu.vn/tccb/vi/danh-gia-xep-loai-ccvc/quy-che-van-hoa-cong-so-20.html,2026-08-03,QĐ-40/2008,public-page-no-login-required
```

*(Xoá 2 dòng cũ trỏ tới `example.edu` trong `sources.csv` — thay hẳn bằng bảng trên.)*

---

#### Dán vào `report/REPORT_NHOM.md` — bảng "Danh sách tài liệu (Data Inventory)"

```markdown
| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đăng ký và hủy học phần | daotao.ueh.edu.vn | 2026-08-03 / not-stated | ~950 | audience=student, department=academic-affairs, category=registration |
| 2 | Học bổng khuyến khích học tập | daotao.ueh.edu.vn | 2026-08-03 / not-stated | ~750 | audience=student, department=academic-affairs, category=scholarship |
| 3 | Nội quy ký túc xá | ktx.haui.edu.vn | 2026-08-03 / not-stated | ~700 | audience=student, department=student-affairs, category=housing |
| 4 | Chính sách miễn, giảm học phí | student.tdtu.edu.vn | 2026-08-03 / NĐ-238/2025 | ~700 | audience=student, department=finance, category=tuition |
| 5 | Quy định thư viện — sinh viên | thuvien.huit.edu.vn | 2026-08-03 / not-stated | ~350 | audience=student, department=library, category=borrowing-policy |
| 6 | Quy định thư viện — giảng viên/cán bộ | thuvien.huit.edu.vn | 2026-08-03 / not-stated | ~350 | audience=faculty, department=library, category=borrowing-policy |
| 7 | Chế độ làm việc của giảng viên | vnu.edu.vn | 2026-08-03 / not-stated | ~600 | audience=faculty, department=academic-affairs, category=workload |
| 8 | Quy chế văn hóa công sở | hvnh.edu.vn | 2026-08-03 / QĐ-40/2008 | ~700 | audience=staff, department=administration, category=workplace-conduct |
```

(Số ký tự là ước lượng — chạy `len()` thật trên file đã lưu rồi cập nhật lại số chính xác.)

#### Dán vào `report/REPORT_NHOM.md` — bảng "Cấu trúc Metadata (Metadata Schema)"

```markdown
| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `audience` | string (bắt buộc K3) | `student` / `faculty` / `staff` | Lọc trước khi rank — tránh trộn quy định của hai đối tượng khác nhau cho cùng chủ đề (VD: mượn sách thư viện) |
| `department` | string | `library`, `finance`, `academic-affairs` | Thu hẹp theo phòng ban phụ trách khi câu hỏi nêu rõ đơn vị |
| `category` | string | `tuition`, `housing`, `scholarship` | Phân nhóm chủ đề, hỗ trợ lọc thô trước khi so embedding |
| `source_url` / `retrieved_at` / `document_version` | string | — | Truy vết nguồn, không dùng để lọc retrieval nhưng bắt buộc cho minh bạch |
```

#### Dán vào `report/REPORT_NHOM.md` — bảng "5 câu hỏi đánh giá"

```markdown
| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu thư viện và trong bao lâu? *(bắt buộc `metadata_filter={"audience":"student"}`, nếu không sẽ dễ lẫn với đáp án 180 ngày của giảng viên)* | Tối đa 3 tài liệu, thời hạn 10 ngày, gia hạn thêm được 1 lần 10 ngày | `library-services-student` |
| 2 | Sinh viên cần đạt điều kiện gì để được xét học bổng khuyến khích học tập loại khá? | Đang trong 8 học kỳ chính; học tập và rèn luyện từ loại khá trở lên; không kỷ luật từ mức khiển trách trở lên; đạt ≥5/10 mọi học phần; tín chỉ đăng ký ≥ kế hoạch đào tạo | `scholarship-incentive` |
| 3 | Quy trình hủy một học phần đã đăng ký gồm những bước nào? | Nộp Phiếu đề nghị hủy học phần tại Phòng Quản lý đào tạo trong thời hạn quy định; Phòng Tài chính hoàn học phí theo danh sách đã xác nhận hủy | `course-registration` |
| 4 | Ký túc xá cấm những hành vi nào? | Uống rượu bia; tàng trữ vũ khí/hung khí/chất nổ/ma túy; nấu ăn/tổ chức sinh nhật trong phòng; đánh bài cờ bạc; gây gổ tụ tập bè phái; vượt rào trèo tường | `dormitory-rules` |
| 5 | Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không? *(câu hỏi ngoại lệ — đối lập với câu 1)* | Không — không áp dụng gia hạn, tài liệu phải trả đúng đợt thu hồi 25/6 và 25/12 hằng năm (khác với sinh viên được gia hạn 1 lần) | `library-services-faculty` |
```

- [ ] Cả 5 người đã copy 8 file + `sources.csv` vào repo riêng của mình
- [ ] Cả 5 người đã dán 3 bảng trên vào `report/REPORT_NHOM.md` của mình (nội dung giống nhau vì là phần chung của nhóm)
- [ ] (Vi Minh Hiển) đã điền câu "Phạm vi cụ thể nhóm tập trung" trong `REPORT_NHOM.md` — gợi ý: *"Dịch vụ và quy định dành cho sinh viên, giảng viên và cán bộ tại nhiều trường đại học Việt Nam, tập trung vào các thủ tục học vụ (đăng ký học phần, học bổng, học phí), đời sống sinh viên (ký túc xá, thư viện) và nghĩa vụ công tác (chế độ làm việc giảng viên, văn hóa công sở cán bộ)."*

---

## 4. Task 1–3: `src/chunking.py` (mỗi người tự code)

- [ ] Đọc trước: `src/models.py` (Document), `src/embeddings.py` (`_mock_embed`), `FixedSizeChunker.chunk()` đã có sẵn làm mẫu
- [ ] Trả lời warm-up trong `REPORT_CANHAN.md` **trước khi code** (cosine similarity nghĩa là gì; công thức số chunk `ceil((length-overlap)/(chunk_size-overlap))`)
- [ ] **Task 1** — `SentenceChunker.chunk`: tách câu bằng regex, gộp theo `max_sentences_per_chunk`
  - [ ] `python -m pytest tests/test_solution.py -k SentenceChunker -v` pass
- [ ] **Task 2** — `RecursiveChunker.chunk` + `_split`: đệ quy theo separator ưu tiên (đoạn → dòng → câu → từ → ký tự)
  - [ ] `python -m pytest tests/test_solution.py -k RecursiveChunker -v` pass
- [ ] **Task 3** — `compute_similarity` (cosine) + `ChunkingStrategyComparator.compare` (3 key: `fixed_size`, `by_sentences`, `recursive`)
  - [ ] `python -m pytest tests/test_solution.py -k "ComputeSimilarity or CompareChunkingStrategies" -v` pass
- [ ] ✅ CHECKPOINT 3: `python -m pytest tests -k "Chunker or Similarity or Compare" -v` → **23 passed**

---

## 5. Task 4–6: `src/store.py` + `src/agent.py` (mỗi người tự code)

- [ ] **Task 4** — `EmbeddingStore`: `_make_record` (copy metadata, giữ `doc_id`, id chunk duy nhất) → `add_documents` → `get_collection_size` → `search`/`_search_records` (dot product, sort giảm dần, cắt top_k)
- [ ] **Task 5** — `search_with_filter` (lọc theo metadata **trước**, rank **sau**, dùng chung `_search_records`) + `delete_document` (trả True/False dựa trên `metadata['doc_id']`)
  - [ ] `python -m pytest tests -k "EmbeddingStore or SearchWithFilter or DeleteDocument" -v` pass toàn bộ
- [ ] **Task 6** — `KnowledgeBaseAgent`: lưu `store`/`llm_fn` trong `__init__`, `answer()` gọi `store.search`, ghép context có đánh số `[1] [2]`, prompt yêu cầu chỉ dùng context, gọi `llm_fn(prompt)`
  - [ ] `python -m pytest tests/test_solution.py -k KnowledgeBaseAgent -v` pass
- [ ] ✅ CHECKPOINT 4: `python -m pytest tests -v` → **42 passed** + `python main.py "Chunking là gì?"` chạy được
- [ ] Dán output pytest (42 passed) vào `REPORT_CANHAN.md`

---

## 6. Strategy riêng + benchmark (Benchmark owner chốt query, mỗi người code `bench.py`)

| Người | Strategy trong `bench.py` |
|---|---|
| Phạm Nguyễn Đăng Khôi | `FixedSizeChunker` (overlap/chunk_size tự chọn) |
| Vi Minh Hiển | `SentenceChunker` |
| Nguyễn Đăng Đức | `RecursiveChunker` (separator mặc định) |
| Đỗ Tuấn Sơn | Chunker theo heading/section (tự viết, bắt buộc theo K3) |
| Trần Đức Bảo Trung | `RecursiveChunker` (tham số khác hẳn Đăng Đức) |

- [ ] Nhóm chốt **đúng 5 query** (đa dạng: số liệu, điều kiện, quy trình, liệt kê, ngoại lệ), kèm gold answer trích trực tiếp từ corpus
- [ ] Ít nhất 1 query **bắt buộc dùng** `metadata_filter={"audience": "student"}`
- [ ] Chạy `ChunkingStrategyComparator().compare()` trên 2–3 tài liệu (bỏ front matter trước khi so sánh) → điền bảng baseline vào `REPORT_NHOM.md`
- [ ] Mỗi người viết `bench.py` riêng, chỉ khác **1 dòng chọn chunker** (theo bảng trên), dùng chung `build_knowledge_base()` từ `ingest.py`
- [ ] `bench.py` in: strategy + tham số, số chunk đã nạp, top-3 (score, doc_id, preview) và câu trả lời agent cho cả 5 query
- [ ] ✅ CHECKPOINT 5: `bench.py` chạy được cho mọi người, 5 query đã chốt

---

## 7. Chạy benchmark & phân tích failure (mỗi người + tổng hợp nhóm)

- [ ] (Tuỳ chọn nhưng khuyến nghị) Cài `requirements-local.txt` để dùng embedding thật thay vì mock — chỉ làm **sau khi** đạt CP4
- [ ] Chấm theo **chunk trong top-3**, không chỉ theo `doc_id` (2đ/1đ/0đ theo `docs/EVALUATION.md`)
- [ ] Chạy A/B: có filter `audience` vs không filter, ghi nhận khác biệt (hoặc ghi nhận nếu không khác)
- [ ] Ghi top-3 chunk + score + đánh giá liên quan + câu trả lời agent cho từng query
- [ ] Viết **ít nhất 1 failure case** có bằng chứng cụ thể từ top-k (không chỉ ghi "model sai")
- [ ] ✅ CHECKPOINT 6: có bảng so sánh chung giữa 5 người + mỗi người có nhận xét riêng

---

## 8. Report & Demo

- [ ] Hoàn thiện `report/REPORT_CANHAN.md` (mỗi người): warm-up, hướng code, output pytest, dự đoán similarity, 5 kết quả retrieval riêng
- [ ] Hoàn thiện `report/REPORT_NHOM.md` (nhóm): corpus + metadata schema, baseline, 5 strategy của 5 người, 5 query + gold answer, so sánh, demo
- [ ] Chuẩn bị demo 6–8 phút: phạm vi/nguồn (1p) → mỗi người giải thích strategy (2p, ~24s/người với 5 người — cân nhắc rút gọn) → so sánh + A/B filter + failure case (3p) → chạy 1 query live (1–2p)

---

## 9. Nộp bài

- [ ] `python -m pytest tests -v` → 42 passed (chạy lại lần cuối)
- [ ] `git status` — đảm bảo **không** có `.venv/`, `.env`, database local
- [ ] Kiểm tra tên repo GitHub đúng quy ước `DAY07-MSSV-HoVaTen` (repo hiện tại: xác nhận lại tên đã đổi đúng chuẩn)
- [ ] `git add`, `git commit`, `git push`
- [ ] Nộp link GitHub (không nộp zip) lên vlearn
- [ ] Rà lại checklist ✅ CHECKPOINT 7 (10 mục) trong tài liệu lab gốc trước khi nộp

---

## Việc cần nhóm quyết định / xác nhận (hỏi lại tôi khi cần code cụ thể)

- [x] Tên 5 thành viên + phân công vai trò/strategy — đã điền ở mục 1 và 1b
- [x] Phạm vi cụ thể + nguồn thật cho 8 tài liệu + 5 câu hỏi benchmark — đã chọn sẵn ở mục 3b, chỉ cần lưu & dán
- [ ] Có dùng local embedding (`requirements-local.txt`) hay giữ mock cho toàn bộ benchmark?

---

## 10. Tổng hợp file theo từng người (đọc mục này trước khi bắt tay vào việc)

**Nguyên tắc:** file trong cột "Chung cả nhóm" phải **giống hệt nhau** ở cả 5 repo (copy từ mục 3b). File trong cột "Tự viết riêng" **phải khác nhau** — không copy của nhau, kể cả khi cùng loại strategy (VD 2 người cùng chọn `RecursiveChunker` vẫn phải tự gõ code, chỉ tham số khác).

| Người | MSSV | Repo GitHub | File chung cả nhóm (copy y hệt từ mục 3b) | File tự viết riêng (không copy) | Trạng thái hiện tại |
|---|---|---|---|---|---|
| Phạm Nguyễn Đăng Khôi | 2A202601243 | `DAY07-2A202601243-PhamNguyenDangKhoi` (repo này) | ✅ `data/k3_university/*.md` (8 file) + `sources.csv` — đã có | `src/chunking.py`, `src/store.py`, `src/agent.py` ✅ 42/42 pass · `bench.py` ✅ đã chạy · `report/REPORT_CANHAN.md` ✅ đã điền | ✅ Xong toàn bộ, kể cả `REPORT_NHOM.md` (bảng so sánh 5 người) |
| Vi Minh Hiển | 2A202601743 | `DAY07-2A202601743-ViMinhHien` (nhánh `hien`) | ✅ đã có | `src/chunking.py`, `src/store.py`, `src/agent.py` ✅ 42/42 pass · `bench.py` ✅ (`SentenceChunker` + tự viết `TfidfEmbedder`) · `report/REPORT_CANHAN.md` ✅ | ✅ Xong, chỉ cần chạy lại `bench.py` với đúng 5 câu hỏi chung của nhóm (hiện dùng bộ câu hỏi khác) |
| Nguyễn Đăng Đức | 2A202601787 | `DAY07-2A202601787-NguyenDangDuc` (nhánh `dangduc`) | ✅ đã có | `src/NguyenDangDuc/*.py` đã code nhưng **sai vị trí** — 3 file gốc `src/chunking.py`/`store.py`/`agent.py` vẫn còn 13 `NotImplementedError` → `pytest` thật vẫn 31 failed/11 passed · `bench.py` ⬜ chưa có · `report/REPORT_CANHAN.md` đã viết nhưng số liệu không khớp code/corpus | ⚠️ **Chặn** — cần copy đè code lên 3 file gốc, viết `bench.py`, chạy lại report mục 3–5 |
| Đỗ Tuấn Sơn | 2A202601051 | `DAY07-2A202601051-DoTuanSon` (nhánh `son`) | ✅ đã có (8/8 file đúng) | `src/01051-DoTuanSon/*.py` đã code + `HeadingChunker` tự viết tốt, nhưng **sai vị trí** giống Đức (3 file gốc còn 13 `NotImplementedError`) · `bench.py` ⬜ chưa có · `report/REPORT_CANHAN.md` ✅ đã viết chi tiết | ⚠️ **Chặn** — xem `THAM_KHAO_Son.md`; cần copy đè code lên 3 file gốc + viết `bench.py` |
| Trần Đức Bảo Trung | 2A202601269 | `DAY07-2A202601269-TranDucBaoTrung` | ✅ đã có | `src/chunking.py`, `src/store.py`, `src/agent.py` ✅ 42/42 pass (sửa thẳng file gốc) · `bench.py` ✅ (`RecursiveChunker(420)` + tự viết `LightweightVietnameseEmbedder`) · `report/REPORT_CANHAN.md` ✅ | ✅ Xong, điểm truy xuất cao nhất nhóm (5/5 đúng top-3) |

**File dùng chung ở mức nhóm (chỉ cần 1 bản, không nhân bản theo người):**
- `report/REPORT_NHOM.md` — mỗi repo vẫn cần có file này (vì nộp qua repo cá nhân) nhưng **nội dung giống hệt nhau** ở cả 5 repo; bản đầy đủ (đã gồm bảng so sánh 5 người) hiện có ở repo của Khôi — 4 bạn còn lại copy nguyên file này vào repo riêng trước khi nộp (sau khi Đức/Sơn/Hiển cập nhật xong phần của mình thì đồng bộ lại 1 lần nữa).
- `docs/HUONG_DAN_IMPLEMENTATION.md` — tài liệu hướng dẫn (không phải bài nộp), chỉ cần có ở máy/repo của người đang code, không bắt buộc phải nằm trong repo nộp cuối cùng.
- `CHECKLIST.md` (file này) — công cụ theo dõi tiến độ nội bộ, không phải bài nộp.

**Việc còn lại trước khi nộp (ưu tiên theo thứ tự):** (1) Đức + Sơn sửa lỗi vị trí code và viết `bench.py` — nếu không sửa, `pytest` sẽ fail ngay khi giảng viên clone repo dù report ghi "42 passed"; (2) Hiển chạy lại `bench.py` bằng đúng 5 câu hỏi chung; (3) cả 4 bạn copy bản `REPORT_NHOM.md` mới nhất (đã có bảng so sánh) vào repo riêng; (4) luyện demo 6–8 phút.
