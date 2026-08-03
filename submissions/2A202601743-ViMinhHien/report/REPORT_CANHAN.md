# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:*

**Ví dụ có độ tương tự CAO:**
- Câu A:
- Câu B:
- Tại sao tương đồng:

**Ví dụ có độ tương tự THẤP:**
- Câu A:
- Câu B:
- Tại sao khác:

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:*

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:*

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Dán kết quả (output) của: pytest tests/ -v
```

**Số lượng bài test vượt qua (pass):** __ / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

<<<<<<< HEAD
Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).
=======
**Backend:** normalized TF-IDF (tự viết, dependency-free)
>>>>>>> origin/hien

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

<<<<<<< HEAD
**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---
=======
> Cập nhật: chạy lại bằng đúng **5 câu hỏi chung của nhóm** (`report/REPORT_NHOM.md` mục 3) thay cho bộ câu hỏi riêng ở bản nháp trước, để so sánh trực tiếp được với các thành viên khác trong bảng tổng hợp của nhóm.

| # | Query | Top-1 chunk | Score | Relevant | Câu trả lời Agent tóm tắt |
|---|---|---|---:|---|---|
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu thư viện và trong bao lâu? *(filter `audience=student`)* | `library-services-student`: số lượng, thời hạn, gia hạn, xử lý trễ hạn (gộp cả 3 mục vào 1 chunk) | 0.3531 | Có (top-1, đầy đủ) | Tối đa 3 tài liệu trong 10 ngày, gia hạn 1 lần thêm 10 ngày. |
| 2 | Sinh viên cần đạt điều kiện gì để được xét học bổng khuyến khích học tập loại khá? | `scholarship-incentive`: điều kiện xét + mức học bổng | 0.4777 | Có (top-1, đầy đủ) | Nêu đủ 5 điều kiện (8 học kỳ, khá trở lên, không kỷ luật, ≥5/10, tín chỉ ≥ kế hoạch). |
| 3 | Quy trình hủy một học phần đã đăng ký gồm những bước nào? | `course-registration`: mục "Thời gian đăng ký" (đúng tài liệu, nhưng chưa phải đoạn "Quy trình hủy học phần" chứa bước nộp phiếu) | 0.2781 | Có (top-1 đúng tài liệu; cả top-3 đều là `course-registration` nên đoạn quy trình chi tiết nằm trong top-3) | Agent (dựa top-1) trả lời về mốc thời gian, chưa nêu bước "nộp Phiếu đề nghị tại Phòng Quản lý đào tạo" |
| 4 | Ký túc xá cấm những hành vi nào? | `dormitory-rules`: mục "Hành vi bị cấm" + "Xử lý vi phạm" + "Quy định khác" (gộp 3 mục, 3 câu/chunk) | 0.2945 | Có (top-1, đầy đủ) | Liệt kê đúng và đủ toàn bộ hành vi bị cấm. |
| 5 | Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không? | `library-services-faculty`: số lượng/thời hạn + gia hạn + xử lý trễ hạn | 0.6231 | Có (top-1, đầy đủ) | Không được gia hạn; phải trả đúng đợt thu hồi 25/6 và 25/12. |

**Số query có tài liệu liên quan trong top-3:** 5 / 5. **Điểm truy xuất theo `docs/SCORING.md`:** 2+2+1+2+2 = **9/10** (chỉ câu 3 chưa trọn vẹn — đúng tài liệu ở top-1 nhưng chưa phải đúng đoạn quy trình).

**Nhận xét:** `SentenceChunker(max_sentences_per_chunk=3)` có xu hướng gộp 2-3 mục `##` liền kề vào 1 chunk (vì mỗi mục thường chỉ 1-2 câu) — đây là lý do câu 1, 4, 5 có câu trả lời đầy đủ ngay top-1 dù câu hỏi cần thông tin từ nhiều mục con. Ngược lại câu 3 bị tách vì "Thời gian đăng ký" và "Quy trình hủy học phần" đủ dài để thành 2 chunk riêng. Qua phân công chiến lược, mình nhận thấy SentenceChunker giữ câu trọn vẹn và dễ đọc, trong khi chunking theo heading (như Đỗ Tuấn Sơn) giữ đúng ranh giới mục hơn nên ít bị hiện tượng "gộp may rủi" như trên.
>>>>>>> origin/hien

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
<<<<<<< HEAD
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
=======
|---|---:|
| Khởi động | 5 / 5 |
| Hướng tiếp cận | 10 / 10 |
| Hoàn thiện code | 30 / 30 |
| Dự đoán similarity | 4 / 5 |
| Kết quả truy xuất | 9 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |
>>>>>>> origin/hien
