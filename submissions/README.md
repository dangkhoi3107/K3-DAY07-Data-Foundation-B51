# Submissions — Lab 7 (K3), nhóm 5 người

Thư mục này gộp **bài làm cá nhân thật** của cả 5 thành viên, tách theo từng người để không đè lên nhau (mỗi người có `src/` + `report/REPORT_CANHAN.md`, ai có `bench.py` thì kèm theo). `src/*.py`, `bench.py`, `report/REPORT_CANHAN.md` ở **gốc repo** vẫn giữ nguyên bản template rỗng cho lab — không đại diện cho ai trong nhóm. Báo cáo nhóm dùng chung nằm ở `report/REPORT_NHOM.md` (gốc repo).

## Trạng thái từng người (cập nhật 2026-08-03)

| Thư mục | Người | Test cá nhân | `bench.py` | Ghi chú |
|---|---|---|---|---|
| `2A202601243-PhamNguyenDangKhoi/` | Phạm Nguyễn Đăng Khôi | ✅ 42/42 | ✅ `FixedSizeChunker(300/60)` | Điểm truy xuất 4/10 — dùng MockEmbedder nên rank chưa phản ánh ngữ nghĩa thật (xem `report/REPORT_NHOM.md`) |
| `2A202601743-ViMinhHien/` | Vi Minh Hiển | ✅ 42/42 | ✅ `SentenceChunker` + tự viết `TfidfEmbedder` | Điểm truy xuất 8/10. Bộ 5 câu hỏi benchmark khác bộ chung của nhóm — cần chạy lại để so sánh trực tiếp |
| `2A202601787-NguyenDangDuc/` | Nguyễn Đăng Đức | ✅ 42/42 *(đã tự xác nhận: đặt tạm code này vào `src/` gốc và chạy `pytest` độc lập, logic đúng)* | ⬜ chưa có | Code đúng, nhưng trên **nhánh `dangduc` gốc** vẫn nằm sai vị trí nên `pytest` mặc định ở đó vẫn fail (chi tiết: `THAM_KHAO_Duc.md`). Số liệu retrieval trong report chưa khớp corpus — cần Đức tự chạy lại sau khi sửa vị trí + viết `bench.py` |
| `2A202601051-DoTuanSon/` | Đỗ Tuấn Sơn | ✅ 42/42 *(đã tự xác nhận tương tự)* | ⬜ chưa có | Có `HeadingChunker` tự viết đúng yêu cầu bắt buộc K3 (thiết kế tốt, không nằm trong 42 test chuẩn nhưng đã đọc code). Cùng lỗi vị trí code như Đức trên nhánh `son` gốc (chi tiết: `THAM_KHAO_Son.md`) |
| `2A202601269-TranDucBaoTrung/` | Trần Đức Bảo Trung | ✅ 42/42 | ✅ `RecursiveChunker(420)` + tự viết `LightweightVietnameseEmbedder` (sklearn `HashingVectorizer`) | Điểm truy xuất 10/10 — cao nhất nhóm. Thiếu `scikit-learn` trong `requirements*.txt` |

**Về cột "Test cá nhân":** kiểm tra bằng cách đặt tạm `agent.py`/`chunking.py`/`store.py` của từng người vào đúng vị trí `src/` gốc rồi chạy `pytest` — tất cả **5/5 người đều pass 42/42** khi code được đặt đúng chỗ. Tức là code của cả nhóm đều đúng logic; vấn đề còn lại của Đức và Sơn chỉ là *vị trí file trên nhánh riêng của họ* + thiếu `bench.py`, không phải lỗi implementation.

## Vì sao cấu trúc như thế này

Cả 5 người đều sửa cùng những file (`src/chunking.py`, `src/store.py`, `src/agent.py`, `report/REPORT_CANHAN.md`...) nhưng với nội dung khác nhau hoàn toàn — không có cách nào gộp 5 cách viết khác nhau của cùng một hàm thành 1 bản duy nhất mà không làm mất bài của ai đó. Giải pháp: giữ gốc repo là bản template (đúng như lúc chưa ai code), tách bài làm thật của từng người vào thư mục riêng ở đây. Muốn chạy thử code của một người cụ thể, trỏ `PYTHONPATH`/import vào đúng `submissions/<thư mục>/src/` thay vì `src/` gốc.

Muốn xem chi tiết từng lần merge, xem `git log --graph` trên `main` — mỗi người tương ứng 1 merge commit riêng.
