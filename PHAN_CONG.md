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

## Trạng thái hiện tại (repo Khôi)

Data ✅ đã push lên `main` · Code Task 1–6 ✅ 42/42 pass · `bench.py` ⬜ đã viết, chưa chạy/xác nhận · `REPORT_CANHAN.md` / `REPORT_NHOM.md` ⬜ chưa điền. 4 người còn lại: chưa bắt đầu.
