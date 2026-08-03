# Phân công việc — Lab 07 (K3)

Tài liệu chi tiết hơn: `CHECKLIST.md` (đầy đủ từng bước), `docs/HUONG_DAN_IMPLEMENTATION.md` (hướng dẫn code Task 1–6). File này chỉ tóm tắt việc của từng người.

## Việc chung — ai cũng làm, trong repo riêng của mình

1. **Lấy data**: copy 8 file `.md` + `sources.csv` vào `data/k3_university/` — copy tay từ `CHECKLIST.md` mục 3b, hoặc `git checkout` thẳng từ repo Khôi (xem hướng dẫn 2 cách ở cuối `CHECKLIST.md` mục 3b).
2. **Code Task 1–6** trong `src/chunking.py`, `src/store.py`, `src/agent.py` theo `docs/HUONG_DAN_IMPLEMENTATION.md` → `python -m pytest tests -v` phải ra **42 passed**.
3. **Viết `bench.py`** với strategy được phân công (bảng dưới) — chỉ khác 1 dòng chọn chunker so với người khác.
4. **Điền `report/REPORT_CANHAN.md`**: warm-up, hướng tiếp cận code, output test, dự đoán similarity, 5 kết quả retrieval của riêng mình.
5. **Copy 3 bảng chung** (Data Inventory, Metadata Schema, 5 câu hỏi + gold answer) từ `CHECKLIST.md` mục 3b vào `report/REPORT_NHOM.md`.

## Việc riêng từng người

| Người | MSSV | Repo GitHub | Strategy `bench.py` | Vai trò thêm |
|---|---|---|---|---|
| Phạm Nguyễn Đăng Khôi | 2A202601243 | `DAY07-2A202601243-PhamNguyenDangKhoi` | `FixedSizeChunker(chunk_size=300, overlap=60)` | Demo coordinator — gom bảng so sánh 5 strategy, dẫn demo 6–8 phút |
| Vi Minh Hiển | 2A202601743 | `DAY07-2A202601743-ViMinhHien` | `SentenceChunker` | Data curator — kiểm lại các `source_url` còn truy cập được trước khi nộp |
| Nguyễn Đăng Đức | 2A202601787 | `DAY07-2A202601787-NguyenDangDuc` | `RecursiveChunker` (separator mặc định) | Benchmark owner — rà lại 5 query/gold answer cho khớp ý nhóm |
| Đỗ Tuấn Sơn | 2A202601051 | `DAY07-2A202601051-DoTuanSon` | Chunker heading/section (tự viết — bắt buộc theo K3) | Hỗ trợ kiểm tra nguồn dữ liệu |
| Trần Đức Bảo Trung | 2A202601269 | `DAY07-2A202601269-TranDucBaoTrung` | `RecursiveChunker` (tham số khác hẳn Đức) | Hỗ trợ kiểm chéo gold answer |

## Thứ tự nên làm

Lấy data → code Task 1–3 (chunking) → CP3 (23 passed) → code Task 4–6 (store + agent) → CP4 (42 passed) → viết `bench.py` → CP5 → điền `REPORT_CANHAN.md` → họp nhóm gom kết quả 5 strategy → điền `REPORT_NHOM.md` → luyện demo.

## Trạng thái hiện tại (cập nhật 2026-08-03, sau khi kiểm tra trực tiếp cả 5 nhánh trên remote)

**Phạm Nguyễn Đăng Khôi** — ✅ xong: data, Task 1–6 (42/42), `bench.py` đã chạy, `REPORT_CANHAN.md` + `REPORT_NHOM.md` đã điền (phần nhóm gồm cả bảng so sánh 5 người, xem bên dưới).

**Vi Minh Hiển (nhánh `hien`)** — ✅ xong: code gốc `src/*.py` sạch `NotImplementedError`, 42/42 pass. `bench.py` tự viết thêm `TfidfEmbedder` (TF-IDF thuần Python, không phụ thuộc thư viện ngoài). `REPORT_CANHAN.md` đã điền đầy đủ, 5/5 câu có chunk liên quan trong top-3. ⚠️ Có đóng góp vào `REPORT_NHOM.md` nhưng dùng **bộ 5 câu hỏi khác** bộ chung của nhóm — cần chạy lại đúng 5 câu ở `REPORT_NHOM.md` mục 3 để gộp vào bảng so sánh.

**Trần Đức Bảo Trung (nhánh `2A202601269-TranDucBaoTrung`)** — ✅ xong, kết quả tốt nhất nhóm: code gốc sạch, 42/42 pass. `bench.py` dùng đúng bộ 5 câu hỏi chung, tự viết `LightweightVietnameseEmbedder` (sklearn `HashingVectorizer`), đạt 5/5 câu đúng tài liệu trong top-3. `REPORT_CANHAN.md` đầy đủ. ⚠️ nhỏ: thiếu `scikit-learn` trong `requirements*.txt`.

**Nguyễn Đăng Đức (nhánh `dangduc`)** — ⚠️ **CHƯA XONG, cần Đức tự sửa:** code Task 1–6 chỉ nằm ở `src/NguyenDangDuc/` (bản sao), 3 file gốc `src/chunking.py`/`store.py`/`agent.py` vẫn còn nguyên `NotImplementedError` (13 chỗ) → `pytest` thực tế vẫn ra 31 failed/11 passed dù `REPORT_CANHAN.md` đã viết đầy đủ và ghi "42 passed". Chưa có `bench.py`. 5 câu hỏi trong report khác bộ chung của nhóm và một số gold answer không khớp corpus thật (vd. "mượn tối đa 3 cuốn trong 14 ngày" — corpus ghi 10 ngày). **Cách sửa:** copy đè 3 file từ `src/NguyenDangDuc/` lên `src/chunking.py`/`store.py`/`agent.py` gốc, viết `bench.py`, chạy lại report mục 3–5 bằng số liệu thật trên đúng 5 câu hỏi nhóm.

**Đỗ Tuấn Sơn (nhánh `son`)** — ⚠️ **CHƯA XONG, cần Sơn tự sửa:** cùng lỗi vị trí code như Đức (code + `HeadingChunker` tự viết chỉ nằm ở `src/01051-DoTuanSon/`, 3 file gốc vẫn còn 13 `NotImplementedError`). Đã fix xong phần data (8/8 file thật) và đã viết `HeadingChunker` + `REPORT_CANHAN.md` khá chi tiết, nhưng chưa có `bench.py` và 5 câu hỏi dùng trong report khác bộ chung của nhóm. Xem `THAM_KHAO_Son.md` để biết chi tiết cách sửa.

**Việc tiếp theo của Khôi:** nhắc Đức và Sơn sửa lỗi vị trí code + viết `bench.py` + chạy lại report đúng 5 câu hỏi chung, rồi bổ sung 2 dòng còn thiếu vào bảng so sánh ở `REPORT_NHOM.md`. Nhắc Hiển chạy lại `bench.py` bằng đúng 5 câu hỏi chung (hiện đang dùng bộ câu hỏi khác).
