# Tham khảo cho Nguyễn Đăng Đức — dựa trên code thật trên nhánh `origin/dangduc` (kiểm tra 2026-08-03)

> File này **không push lên nhánh của Khôi**, chỉ để Khôi tham khảo rồi trao đổi với Đức. Không phải bản nháp để Đức copy-paste — phần kết quả (test/retrieval) Đức phải tự chạy lại trên code của chính mình sau khi sửa vấn đề bên dưới, vì hiện tại nhánh `dangduc` **chưa thể ra 42/42** (xem mục 1).

## 1. Vấn đề quan trọng nhất: code nằm sai chỗ, test sẽ vẫn fail

Đức đã viết implementation Task 1–6 trong thư mục con `src/NguyenDangDuc/` (`agent.py`, `chunking.py`, `store.py`, `__init__.py`), nhưng `tests/test_solution.py` import qua `src/__init__.py`, và `src/__init__.py` chỉ đọc từ **`src/chunking.py`, `src/store.py`, `src/agent.py` ở gốc** — 3 file này trên nhánh `dangduc` **vẫn còn nguyên `NotImplementedError`** (đã kiểm tra: 5 chỗ trong `chunking.py`, 7 chỗ trong `store.py`, 1 chỗ trong `agent.py` — y hệt lúc chưa code gì).

→ Nếu Đức chạy `python -m pytest tests -v` ngay bây giờ, kết quả vẫn là **31 failed, 11 passed**, dù code thật đã viết xong trong `src/NguyenDangDuc/`. Đây là **đúng lỗi mà Đỗ Tuấn Sơn cũng gặp** — có thể cả nhóm đã hiểu nhầm quy ước cùng một hướng khi tự làm theo mẫu của nhau (tạo thư mục con theo tên mình), nên nên nhắc chung cho cả nhóm.

**Cách sửa (khuyến nghị, giống cách Vi Minh Hiển và Trần Đức Bảo Trung đã làm và đã pass 42/42):** copy nguyên nội dung 3 file từ `src/NguyenDangDuc/{chunking,store,agent}.py` đè lên `src/chunking.py`, `src/store.py`, `src/agent.py` ở gốc repo.

## 2. Vấn đề thứ hai: `REPORT_CANHAN.md` đã viết đầy đủ, nhưng số liệu không khớp code hiện tại lẫn corpus thật

`report/REPORT_CANHAN.md` trên nhánh `dangduc` đã điền rất đầy đủ (warm-up, hướng tiếp cận, "42 passed", similarity, 5 kết quả retrieval, tự chấm 60/60) — nhưng vì root code vẫn `NotImplementedError` (mục 1), các con số này **không thể tái lập được bằng cách chạy lại trên đúng code đã push**. Ngoài ra, một số chi tiết trong mục 5 (5 kết quả retrieval) không khớp với 8 tài liệu thật trong `data/k3_university/` của nhóm:

- Report ghi "Thời gian mượn sách thư viện tối đa bao lâu? → tối đa 3 cuốn trong **14 ngày**" — nhưng `library-services-student.md` của nhóm ghi rõ **10 ngày** (giống hệt bên `library-services-faculty.md` ghi 180 ngày cho giảng viên/cán bộ, không phải 14).
- Report ghi mốc "hạn nộp học phí học kỳ 1 là **15/10**", điều kiện học bổng "**ĐTB ≥ 3.2, điểm rèn luyện ≥ 80**", đăng ký ký túc xá "**trên portal từ 01/08**", hủy môn "**trong 2 tuần đầu học kỳ**" — không có mốc/số liệu nào trong 4 câu này khớp với nội dung 8 tài liệu thật ở `data/k3_university/` (`tuition-exemption.md`, `scholarship-incentive.md`, `dormitory-rules.md`, `course-registration.md` dùng tiêu chí hoàn toàn khác, xem `report/REPORT_NHOM.md` mục 3 để đối chiếu gold answer đúng).
- 5 câu hỏi dùng trong report cũng không trùng bộ 5 câu hỏi chung đã chốt ở `CHECKLIST.md` mục 3b.

Nhiều khả năng phần này được soạn dựa trên một corpus/đề bài khác (hoặc soạn trước khi chốt corpus 8 tài liệu K3), rồi chưa cập nhật lại. Cần Đức tự chạy `bench.py` (chưa có, cần viết) trên đúng corpus + đúng 5 câu hỏi chung rồi điền lại mục 3–5 bằng số liệu thật.

## 3. Việc phụ: chưa có `bench.py`

Nhánh `dangduc` chưa có file `bench.py` nào được commit, dù strategy được phân công (`RecursiveChunker` separator mặc định) đã có mô tả hướng tiếp cận trong report mục 2. Có thể tham khảo cấu trúc `bench.py` của Khôi/Hiển/Trung.

---

**Tóm lại:** Đức cần làm theo thứ tự — (1) copy code từ `src/NguyenDangDuc/` lên gốc `src/`, (2) chạy `python -m pytest tests -v` xác nhận đúng 42/42, (3) viết `bench.py` với `RecursiveChunker` mặc định, (4) chạy đúng 5 câu hỏi chung ở `report/REPORT_NHOM.md` mục 3 (không phải 5 câu tự chọn), (5) viết lại mục 3–5 của `REPORT_CANHAN.md` bằng số liệu thật khớp corpus, (6) copy bản `report/REPORT_NHOM.md` mới nhất (đã có bảng so sánh 5 người) từ repo Khôi vào repo của Đức.
