"""Benchmark ca nhan cua Nguyen Dang Duc (2A202601787).

Chien luoc duoc phan cong: RecursiveChunker voi separator mac dinh
(doan -> dong -> cau -> tu -> ky tu).
Chay: ``python bench.py``.
"""
from __future__ import annotations

import math
import re
from collections import Counter

from ingest import build_knowledge_base
from src import KnowledgeBaseAgent, RecursiveChunker, compute_similarity

DATA_DIR = "data/k3_university"
CHUNKER = RecursiveChunker()  # separators mac dinh, chunk_size=500

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
        "Sinh viên đăng ký học phần theo thời khóa biểu từng học kỳ.",
        "Việc đăng ký môn học của sinh viên thực hiện theo lịch mỗi kỳ.",
        "cao",
    ),
    (
        "Học bổng loại giỏi bằng 1,2 lần mức khá.",
        "Mức học bổng loại giỏi cao hơn loại khá 1,2 lần.",
        "cao",
    ),
    (
        "Ký túc xá cấm sinh viên đánh bài, cờ bạc.",
        "Giảng viên phải dành 600 giờ mỗi năm cho nghiên cứu khoa học.",
        "thấp",
    ),
    (
        "Hồ sơ miễn giảm học phí cần đơn đề nghị và giấy xác nhận.",
        "Trang phục công sở phải gọn gàng, lịch sự.",
        "thấp",
    ),
    (
        "Tài liệu thư viện của giảng viên phải trả đúng đợt thu hồi.",
        "Giảng viên, cán bộ không được gia hạn tài liệu đã mượn.",
        "cao",
    ),
]


class SimpleTfidfEmbedder:
    """TF-IDF thuần Python, không cần cài thêm thư viện, dùng để benchmark có ngữ nghĩa thật thay vì MockEmbedder."""

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
    """LLM giả lập: trả về đoạn context đầu tiên để kiểm tra luồng RAG không cần gọi API."""
    context = prompt.split("Context:\n", 1)[-1].split("\n\nQuestion:", 1)[0]
    first_chunk = context.split("\n---\n", 1)[0]
    return first_chunk[:220].replace("\n", " ")


def main() -> int:
    from ingest import load_documents

    corpus_texts = [doc.content for doc in load_documents(DATA_DIR)]
    embedder = SimpleTfidfEmbedder(corpus_texts)
    store = build_knowledge_base(DATA_DIR, embedder, chunker=CHUNKER)
    agent = KnowledgeBaseAgent(store, extractive_llm)

    print("=== BENCHMARK CÁ NHÂN: NGUYỄN ĐĂNG ĐỨC (2A202601787) ===")
    print(f"Backend: {embedder._backend_name}")
    print(f"Strategy: RecursiveChunker(separators={CHUNKER.separators}, chunk_size={CHUNKER.chunk_size})")
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
