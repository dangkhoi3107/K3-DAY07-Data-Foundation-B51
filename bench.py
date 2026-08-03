"""Benchmark ca nhan cua Do Tuan Son (2A202601051).

Chien luoc duoc phan cong: HeadingChunker (tu viet, bat buoc theo K3_VARIANT.md)
- chunk theo heading/section Markdown.
Chay: ``python bench.py``.
"""
from __future__ import annotations

import math
import re
from collections import Counter

from ingest import build_knowledge_base, load_documents
from src import KnowledgeBaseAgent, compute_similarity
from src.chunking import HeadingChunker

DATA_DIR = "data/k3_university"
CHUNKER = HeadingChunker()  # max_heading_level=3, max_chunk_size=1000

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
        "Sinh viên được mượn tối đa 3 tài liệu trong 10 ngày.",
        "Thời hạn mượn sách của sinh viên trong thư viện là bao lâu?",
        "cao",
    ),
    (
        "Nội quy ký túc xá cấm sinh viên uống rượu, bia.",
        "Định mức giờ chuẩn giảng dạy của giảng viên mỗi năm.",
        "thấp",
    ),
    (
        "Con liệt sỹ được miễn 100% học phí.",
        "Chính sách miễn, giảm học phí cho người có công với cách mạng.",
        "cao",
    ),
    (
        "Điều kiện xét học bổng khuyến khích học tập.",
        "Sinh viên cần đạt loại khá trở lên để được cấp học bổng.",
        "cao",
    ),
    (
        "Trang phục công sở của cán bộ phải gọn gàng, lịch sự.",
        "Sinh viên được gia hạn tài liệu thư viện thêm 10 ngày.",
        "thấp",
    ),
]


class SimpleTfidfEmbedder:
    """TF-IDF thuần Python, không cần cài thêm thư viện (dùng thay sentence-transformers khi máy không có sẵn model)."""

    _TOKEN_RE = re.compile(r"\w+", flags=re.UNICODE)

    def __init__(self, corpus_texts: list[str]) -> None:
        docs_tokens = [self._tokenize(t) for t in corpus_texts]
        doc_freq: Counter[str] = Counter()
        for tokens in docs_tokens:
            doc_freq.update(set(tokens))
        self._vocab = {term: i for i, term in enumerate(sorted(doc_freq))}
        n_docs = max(1, len(docs_tokens))
        self._idf = {
            term: math.log((1 + n_docs) / (1 + freq)) + 1.0
            for term, freq in doc_freq.items()
        }
        self._backend_name = "TF-IDF thuần Python (dependency-free)"

    @classmethod
    def _tokenize(cls, text: str) -> list[str]:
        return cls._TOKEN_RE.findall(text.lower())

    def __call__(self, text: str) -> list[float]:
        counts = Counter(self._tokenize(text))
        vector = [0.0] * len(self._vocab)
        for term, count in counts.items():
            index = self._vocab.get(term)
            if index is not None:
                vector[index] = count * self._idf[term]
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


def extractive_llm(prompt: str) -> str:
    """LLM giả lập: trả về đoạn context đầu tiên (đánh số [1]) để kiểm tra luồng RAG không cần gọi API."""
    context = prompt.split("Context:\n", 1)[-1].split("\n\nQuestion:", 1)[0]
    first_chunk = context.split("[2]", 1)[0]
    return first_chunk[:220].replace("\n", " ")


def main() -> int:
    corpus_texts = [doc.content for doc in load_documents(DATA_DIR)]
    embedder = SimpleTfidfEmbedder(corpus_texts)
    store = build_knowledge_base(DATA_DIR, embedder, chunker=CHUNKER)
    agent = KnowledgeBaseAgent(store, extractive_llm)

    print("=== BENCHMARK CÁ NHÂN: ĐỖ TUẤN SƠN (2A202601051) ===")
    print(f"Backend: {embedder._backend_name}")
    print(f"Strategy: HeadingChunker(max_heading_level={CHUNKER.max_heading_level}, max_chunk_size={CHUNKER.max_chunk_size})")
    print(f"Số chunk: {store.get_collection_size()}\n")

    hits = 0
    for number, item in enumerate(QUERIES, start=1):
        if item["metadata_filter"]:
            results = store.search_with_filter(
                item["question"], top_k=3, metadata_filter=item["metadata_filter"]
            )
        else:
            results = store.search(item["question"], top_k=3)

        found = any(r["metadata"].get("doc_id") == item["gold_doc_id"] for r in results)
        hits += int(found)
        print(f"Q{number}: {item['question']}")
        for rank, r in enumerate(results, start=1):
            doc_id = r["metadata"].get("doc_id", "?")
            marker = "[GOLD]" if doc_id == item["gold_doc_id"] else ""
            preview = " ".join(r["content"].split())[:180]
            print(f"  top-{rank}: {r['score']:.4f} {doc_id} {marker} | {preview}")
        print(f"  agent: {agent.answer(item['question'], top_k=3)[:220]}\n")

    print(f"TOP-3 HIT: {hits}/{len(QUERIES)}\n")
    print("SIMILARITY PAIRS")
    for number, (left, right, prediction) in enumerate(SIMILARITY_PAIRS, start=1):
        score = compute_similarity(embedder(left), embedder(right))
        print(f"  P{number}: prediction={prediction}, score={score:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
