# Submissions — Lab 7 (K3), nhóm 5 người

Thư mục này gộp **bài làm cá nhân thật** của cả 5 thành viên, tách theo từng người để không đè lên nhau (mỗi người có `src/` + `report/REPORT_CANHAN.md`, ai có `bench.py` thì kèm theo). `src/*.py`, `bench.py`, `report/REPORT_CANHAN.md` ở **gốc repo** vẫn giữ nguyên bản template rỗng cho lab — không đại diện cho ai trong nhóm. Báo cáo nhóm dùng chung nằm ở `report/REPORT_NHOM.md` (gốc repo).

## Trạng thái từng người (cập nhật 2026-08-03 — cả 5/5 đã hoàn thiện)

| Thư mục | Người | Test cá nhân | `bench.py` | Điểm truy xuất | Ghi chú |
|---|---|---|---|---|---|
| `2A202601243-PhamNguyenDangKhoi/` | Phạm Nguyễn Đăng Khôi | ✅ 42/42 | ✅ `FixedSizeChunker(300/60)` | 4/10 | Dùng MockEmbedder nên rank chưa phản ánh ngữ nghĩa thật — minh hoạ rõ "filter đúng ≠ rank đúng" (xem `report/REPORT_NHOM.md`) |
| `2A202601743-ViMinhHien/` | Vi Minh Hiển | ✅ 42/42 | ✅ `SentenceChunker` + tự viết `TfidfEmbedder` | 9/10 | Đã chạy lại đúng 5 câu hỏi chung của nhóm; 5/5 top-3, 4/5 đúng trọn vẹn ngay top-1 |
| `2A202601787-NguyenDangDuc/` | Nguyễn Đăng Đức | ✅ 42/42 | ✅ `RecursiveChunker()` mặc định + tự viết `SimpleTfidfEmbedder` | 9/10 | 5/5 đúng tài liệu ở top-1; câu 4 có 1 failure case cụ thể (đúng tài liệu, sai chunk — xem report mục 5) |
| `2A202601051-DoTuanSon/` | Đỗ Tuấn Sơn | ✅ 42/42 | ✅ `HeadingChunker()` (tự viết, đúng yêu cầu bắt buộc K3) + `SimpleTfidfEmbedder` | 10/10 | **Kết quả tốt nhất nhóm** — 5/5 đúng tài liệu VÀ đúng chunk ngay top-1, kể cả câu khó nhất (câu 4, tách đúng nguyên mục "Hành vi bị cấm") |
| `2A202601269-TranDucBaoTrung/` | Trần Đức Bảo Trung | ✅ 42/42 | ✅ `RecursiveChunker(420)` + tự viết `LightweightVietnameseEmbedder` (sklearn `HashingVectorizer`) | 10/10 | 5/5 đúng tài liệu VÀ đúng chunk ngay top-1 |

**Về cột "Test cá nhân":** kiểm tra bằng cách đặt `agent.py`/`chunking.py`/`store.py` của từng người vào đúng vị trí `src/` gốc rồi chạy `pytest` — **5/5 người đều pass 42/42**. Toàn bộ `bench.py` + số liệu "Điểm truy xuất" ở trên đều chạy thật (không bịa), dùng đúng **5 câu hỏi chung** đã chốt ở `report/REPORT_NHOM.md` mục 3, chấm theo `docs/SCORING.md` (2đ/câu nếu top-3 có chunk liên quan + agent trả lời đúng, 1đ nếu chunk đúng nhưng chưa trọn vẹn/không ở top-1, 0đ nếu không có trong top-3).

**Lưu ý minh bạch:** phần `bench.py` + số liệu retrieval + đoạn nhận xét/phản ánh của Đức, Sơn, và bản chạy lại của Hiển được một coordinator (Phạm Nguyễn Đăng Khôi, có AI hỗ trợ) dựng lại dựa trên đúng code + chiến lược đã phân công của từng người, sau khi xác nhận logic code của họ đúng. Số liệu là thật (chạy trực tiếp trên corpus của nhóm), nhưng **từng người nên tự chạy lại `bench.py` và đọc kỹ phần nhận xét trước khi nộp/demo**, vì report cá nhân yêu cầu tự giải thích được — không tự chạy thì sẽ khó trả lời sâu khi được hỏi trực tiếp.

## Vì sao cấu trúc như thế này

Cả 5 người đều sửa cùng những file (`src/chunking.py`, `src/store.py`, `src/agent.py`, `report/REPORT_CANHAN.md`...) nhưng với nội dung khác nhau hoàn toàn — không có cách nào gộp 5 cách viết khác nhau của cùng một hàm thành 1 bản duy nhất mà không làm mất bài của ai đó. Giải pháp: giữ gốc repo là bản template (đúng như lúc chưa ai code), tách bài làm thật của từng người vào thư mục riêng ở đây. Muốn chạy thử code của một người cụ thể, trỏ `PYTHONPATH`/import vào đúng `submissions/<thư mục>/src/` thay vì `src/` gốc.

Muốn xem chi tiết từng lần merge, xem `git log --graph` trên `main` — mỗi người tương ứng 1 merge commit riêng.
