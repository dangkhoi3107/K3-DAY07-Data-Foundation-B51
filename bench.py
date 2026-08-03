"""bench.py — benchmark chiến lược chunking cho corpus data/k3_university.

Chiến lược của Phạm Nguyễn Đăng Khôi (2A202601243): FixedSizeChunker(chunk_size=300, overlap=60)
— khác tham số mặc định (chunk_size=500, overlap=50) của FixedSizeChunker mẫu trong src/chunking.py.

Chạy: python bench.py
(Windows: nếu lỗi encoding tiếng Việt, chạy trước $env:PYTHONIOENCODING="utf-8")
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

from ingest import build_knowledge_base
from src.agent import KnowledgeBaseAgent
from src.chunking import FixedSizeChunker
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)

DATA_DIR = "data/k3_university"

CHUNKER = FixedSizeChunker(chunk_size=300, overlap=60)

# 5 câu hỏi chung của nhóm (xem report/REPORT_NHOM.md và CHECKLIST.md mục 3b).
QUERIES = [
    {
        "question": "Sinh viên được mượn tối đa bao nhiêu tài liệu thư viện và trong bao lâu?",
        "metadata_filter": {"audience": "student"},
        "gold_answer": "Tối đa 3 tài liệu, thời hạn 10 ngày, gia hạn thêm được 1 lần 10 ngày.",
        "gold_doc_id": "library-services-student",
    },
    {
        "question": "Sinh viên cần đạt điều kiện gì để được xét học bổng khuyến khích học tập loại khá?",
        "metadata_filter": None,
        "gold_answer": (
            "Đang trong 8 học kỳ chính; học tập và rèn luyện từ loại khá trở lên; "
            "không kỷ luật từ mức khiển trách trở lên; đạt từ 5/10 trở lên mọi học phần; "
            "tín chỉ đăng ký lớn hơn hoặc bằng kế hoạch đào tạo."
        ),
        "gold_doc_id": "scholarship-incentive",
    },
    {
        "question": "Quy trình hủy một học phần đã đăng ký gồm những bước nào?",
        "metadata_filter": None,
        "gold_answer": (
            "Nộp Phiếu đề nghị hủy học phần tại Phòng Quản lý đào tạo trong thời hạn quy định; "
            "Phòng Tài chính hoàn học phí theo danh sách đã xác nhận hủy."
        ),
        "gold_doc_id": "course-registration",
    },
    {
        "question": "Ký túc xá cấm những hành vi nào?",
        "metadata_filter": None,
        "gold_answer": (
            "Uống rượu bia; tàng trữ vũ khí/hung khí/chất nổ/ma túy; nấu ăn/tổ chức sinh nhật "
            "trong phòng; đánh bài cờ bạc; gây gổ tụ tập bè phái; vượt rào trèo tường."
        ),
        "gold_doc_id": "dormitory-rules",
    },
    {
        "question": "Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không?",
        "metadata_filter": None,
        "gold_answer": (
            "Không — không áp dụng gia hạn, tài liệu phải trả đúng đợt thu hồi 25/6 và 25/12 "
            "hằng năm (khác với sinh viên được gia hạn 1 lần)."
        ),
        "gold_doc_id": "library-services-faculty",
    },
]


def _select_embedder():
    """Giống main.py: chọn backend theo biến môi trường EMBEDDING_PROVIDER (mock | local | openai)."""
    load_dotenv(override=False)
    provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
    if provider == "local":
        try:
            return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
        except Exception:
            print("Local embedder không sẵn sàng; tạm dùng mock.")
            return _mock_embed
    if provider == "openai":
        try:
            return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
        except Exception:
            print("OpenAI embedder không sẵn sàng; tạm dùng mock.")
            return _mock_embed
    return _mock_embed


def bench_llm(prompt: str) -> str:
    """LLM giả lập cho benchmark — không cần API key."""
    preview = prompt[:300].replace("\n", " ")
    return f"[BENCH LLM] {preview}..."


def main() -> int:
    embedder = _select_embedder()
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)

    print(f"=== Strategy: FixedSizeChunker(chunk_size={CHUNKER.chunk_size}, overlap={CHUNKER.overlap}) ===")
    print(f"Backend nhúng: {backend}")
    if backend == "mock embeddings fallback":
        print("Lưu ý: mock không phản ánh ngữ nghĩa thật — chỉ dùng để kiểm luồng kỹ thuật.\n")

    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=CHUNKER)
    print(f"Đã nạp {store.get_collection_size()} chunk vào EmbeddingStore\n")

    agent = KnowledgeBaseAgent(store=store, llm_fn=bench_llm)
    hits = 0

    for index, item in enumerate(QUERIES, start=1):
        print(f"--- Query {index}: {item['question']} ---")
        print(f"Gold answer : {item['gold_answer']}")
        print(f"Gold doc_id : {item['gold_doc_id']}")

        if item["metadata_filter"]:
            results = store.search_with_filter(
                item["question"], top_k=3, metadata_filter=item["metadata_filter"]
            )
            print(f"(metadata_filter={item['metadata_filter']})")
        else:
            results = store.search(item["question"], top_k=3)

        found = False
        for rank, result in enumerate(results, start=1):
            doc_id = result["metadata"].get("doc_id", "?")
            preview = result["content"][:100].replace("\n", " ")
            is_gold = doc_id == item["gold_doc_id"]
            found = found or is_gold
            marker = "[OK]" if is_gold else "    "
            print(f"  top-{rank} {marker} score={result['score']:.3f} doc_id={doc_id} | {preview}...")
        hits += int(found)

        answer = agent.answer(item["question"], top_k=3)
        print(f"Agent answer: {answer[:200]}...")
        print()

    print(f"=== Tổng kết: {hits}/{len(QUERIES)} query có gold doc_id nằm trong top-3 ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
