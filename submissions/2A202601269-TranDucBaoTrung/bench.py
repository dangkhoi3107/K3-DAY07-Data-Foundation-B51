"""Benchmark cá nhân của Trần Đức Bảo Trung (2A202601269).

Chiến lược được phân công: RecursiveChunker với tham số khác Nguyễn Đăng Đức.
Chạy nhanh: ``python bench.py``.
"""
from __future__ import annotations

from sklearn.feature_extraction.text import HashingVectorizer

from ingest import build_knowledge_base
from src import KnowledgeBaseAgent, RecursiveChunker, compute_similarity

DATA_DIR = "data/k3_university"
CHUNKER = RecursiveChunker(
    chunk_size=420,
    separators=[". ", "; ", "\n\n", "\n", " ", ""],
)

QUERIES = [
    {
        "question": "Sinh viên được mượn tối đa bao nhiêu tài liệu thư viện và trong bao lâu?",
        "metadata_filter": {"audience": "student"},
        "gold_doc_id": "library-services-student",
    },
    {
        "question": "Sinh viên cần đạt điều kiện gì để được xét học bổng khuyến khích học tập loại khá?",
        "metadata_filter": None,
        "gold_doc_id": "scholarship-incentive",
    },
    {
        "question": "Quy trình hủy một học phần đã đăng ký gồm những bước nào?",
        "metadata_filter": None,
        "gold_doc_id": "course-registration",
    },
    {
        "question": "Ký túc xá cấm những hành vi nào?",
        "metadata_filter": None,
        "gold_doc_id": "dormitory-rules",
    },
    {
        "question": "Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không?",
        "metadata_filter": None,
        "gold_doc_id": "library-services-faculty",
    },
]

SIMILARITY_PAIRS = [
    (
        "Sinh viên được gia hạn tài liệu thư viện một lần.",
        "Người học có thể gia hạn sách đã mượn thêm một lần.",
        "cao",
    ),
    (
        "Điều kiện xét học bổng khuyến khích học tập.",
        "Các hành vi bị cấm trong ký túc xá.",
        "thấp",
    ),
    (
        "Thủ tục hủy học phần đã đăng ký.",
        "Quy trình xóa môn học khỏi danh sách đăng ký.",
        "cao",
    ),
    (
        "Giảng viên phải trả tài liệu vào đợt thu hồi.",
        "Sinh viên được miễn giảm học phí theo chính sách.",
        "thấp",
    ),
    (
        "Sinh viên được mượn tối đa ba tài liệu trong mười ngày.",
        "Thời hạn mượn sách của người học là 10 ngày, tối đa 3 cuốn.",
        "cao",
    ),
]


class LightweightVietnameseEmbedder:
    """Embedding n-gram cục bộ, nhẹ và có vector chuẩn hóa để benchmark nhanh."""

    def __init__(self) -> None:
        self._backend_name = "local char-ngram hashing (4096 dimensions)"
        self._vectorizer = HashingVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            n_features=4096,
            alternate_sign=False,
            norm="l2",
            lowercase=True,
        )

    def __call__(self, text: str) -> list[float]:
        return self._vectorizer.transform([text]).toarray()[0].tolist()


def extractive_llm(prompt: str) -> str:
    """LLM giả lập: trả về phần đầu context để kiểm tra luồng RAG không cần API."""
    context = prompt.split("NGỮ CẢNH:\n", 1)[-1].split("\n\nCÂU HỎI:", 1)[0]
    return context[:500].replace("\n", " ")


def main() -> int:
    embedder = LightweightVietnameseEmbedder()
    store = build_knowledge_base(DATA_DIR, embedder, chunker=CHUNKER)
    agent = KnowledgeBaseAgent(store, extractive_llm)

    print("=== BENCHMARK CÁ NHÂN: TRẦN ĐỨC BẢO TRUNG (2A202601269) ===")
    print(f"Backend: {embedder._backend_name}")
    print(f"Strategy: RecursiveChunker(chunk_size={CHUNKER.chunk_size}, separators={CHUNKER.separators})")
    print(f"Số chunk: {store.get_collection_size()}\n")

    hits = 0
    for number, item in enumerate(QUERIES, start=1):
        if item["metadata_filter"]:
            results = store.search_with_filter(
                item["question"], top_k=3, metadata_filter=item["metadata_filter"]
            )
        else:
            results = store.search(item["question"], top_k=3)

        found = any(result["metadata"].get("doc_id") == item["gold_doc_id"] for result in results)
        hits += int(found)
        print(f"Q{number}: {item['question']}")
        for rank, result in enumerate(results, start=1):
            doc_id = result["metadata"].get("doc_id", "?")
            marker = "[GOLD]" if doc_id == item["gold_doc_id"] else ""
            preview = " ".join(result["content"].split())[:180]
            print(f"  top-{rank}: {result['score']:.4f} {doc_id} {marker} | {preview}")
        print(f"  agent: {agent.answer(item['question'], top_k=3)[:220]}\n")

    print(f"TOP-3 HIT: {hits}/{len(QUERIES)}\n")
    print("SIMILARITY PAIRS")
    for number, (left, right, prediction) in enumerate(SIMILARITY_PAIRS, start=1):
        score = compute_similarity(embedder(left), embedder(right))
        print(f"  P{number}: prediction={prediction}, score={score:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
