# Tham khảo cho Đỗ Tuấn Sơn — cập nhật 2026-08-03, dựa trên code thật mới nhất trên nhánh `origin/son`

> File này **không push lên nhánh của Khôi**, chỉ để Khôi tham khảo rồi trao đổi với Sơn. Không phải bản nháp để Sơn copy-paste nộp.

## 0. Tin tốt: 2 việc đã xong so với lần kiểm tra trước

- **Data đã đúng** — `data/k3_university/` trên nhánh `son` giờ đã có đủ 8 file thật + `sources.csv` khớp corpus chung của nhóm (không còn là bản 2 file cũ). Không cần làm gì thêm ở mục này.
- **`HeadingChunker` đã viết xong và viết tốt** — `src/01051-DoTuanSon/chunking.py` đã có class `HeadingChunker` đúng yêu cầu bắt buộc của K3: cắt theo heading Markdown (`#`/`##`/`###`), gộp section "chỉ có tiêu đề không nội dung" vào section kế tiếp (tránh chunk rỗng nghĩa — chi tiết này thể hiện Sơn hiểu bài, không phải chép), và hạ xuống `RecursiveChunker` khi section quá dài. `REPORT_Đỗ Tuấn Sơn.md` (trong `src/01051-DoTuanSon/`) cũng đã viết đầy đủ cả 5 mục, khá chi tiết và có phản ánh thật (vd. cặp similarity #3 "bất ngờ" được giải thích hợp lý). Nội dung này đã được trích dẫn nguyên văn vào `report/REPORT_NHOM.md` (khối "Thành viên 4") của Khôi làm code snippet mẫu.

## 1. Vấn đề còn lại (quan trọng nhất): code vẫn nằm sai chỗ, test vẫn sẽ fail

Đã kiểm tra lại nhánh `son` mới nhất (commit `2a3c12e`): 3 file gốc `src/chunking.py`, `src/store.py`, `src/agent.py` **vẫn còn nguyên `NotImplementedError`** (5 chỗ trong `chunking.py`, 7 chỗ trong `store.py`, 1 chỗ trong `agent.py` — đếm bằng `grep -c NotImplementedError`, giống hệt lúc chưa code gì). Lý do: `tests/test_solution.py` import qua `src/__init__.py`, và `src/__init__.py` chỉ đọc từ 3 file gốc này, không đọc từ `src/01051-DoTuanSon/`.

→ Nếu Sơn chạy `python -m pytest tests -v` ngay bây giờ, kết quả vẫn là **31 failed, 11 passed**, dù `HeadingChunker` và cả report đã viết xong trong `src/01051-DoTuanSon/`.

**Cách sửa (khuyến nghị, giống cách Vi Minh Hiển và Trần Đức Bảo Trung đã làm và đã pass 42/42):** copy nguyên nội dung 3 file từ `src/01051-DoTuanSon/{chunking,store,agent}.py` đè lên `src/chunking.py`, `src/store.py`, `src/agent.py` ở gốc repo. Đề bài cũng nêu đích danh 3 đường dẫn gốc này là "3 file cần sửa".

## 2. Vấn đề mới phát hiện: chưa có `bench.py`, và 5 câu hỏi trong report khác bộ chung của nhóm

- Nhánh `son` chưa có file `bench.py` nào được commit, dù `report/REPORT_CANHAN.md` (bản trong `src/01051-DoTuanSon/`) mô tả đã "chạy 5 câu hỏi đánh giá của nhóm" với `HeadingChunker` + backend local `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Cần viết `bench.py` thật (tham khảo cấu trúc `bench.py` của Khôi/Hiển/Trung) để số liệu có thể tái lập.
- 5 câu hỏi Sơn dùng trong report **không trùng** bộ 5 câu hỏi chung đã chốt ở `CHECKLIST.md` mục 3b / `report/REPORT_NHOM.md` mục 3: 2/5 câu hỏi của Sơn (mốc hủy học phần cụ thể, đối tượng miễn 100% học phí, giờ giới nghiêm ký túc xá) là chủ đề/gold answer khác hẳn bộ chung. Cần chạy lại đúng 5 câu hỏi chung để kết quả gộp được vào bảng so sánh nhóm ở `REPORT_NHOM.md`.

## 3. Thứ tự nên làm tiếp

(1) Copy đè 3 file từ `src/01051-DoTuanSon/` lên `src/chunking.py`/`store.py`/`agent.py` gốc → (2) chạy `python -m pytest tests -v` xác nhận đúng **42 passed** → (3) viết `bench.py` dùng `HeadingChunker`, chạy đúng 5 câu hỏi ở `report/REPORT_NHOM.md` mục 3 (không phải 5 câu tự chọn) → (4) cập nhật lại mục 3–5 của `report/REPORT_CANHAN.md` bằng số liệu thật từ `bench.py` mới → (5) copy bản `report/REPORT_NHOM.md` mới nhất (đã có bảng so sánh 5 người) từ repo Khôi vào repo của Sơn.
