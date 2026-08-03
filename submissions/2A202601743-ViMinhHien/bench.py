from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Callable

from ingest import chunk_document, load_documents
from src import (
    Document,
    EmbeddingStore,
    KnowledgeBaseAgent,
    LocalEmbedder,
    SentenceChunker,
    compute_similarity,
    _mock_embed,
)


DATA_DIR = Path("data/k3_university")

BENCHMARKS = [
    # Bo 5 cau hoi CHUNG cua nhom (report/REPORT_NHOM.md muc 3) - thay cho
    # bo cau hoi rieng o ban nhap truoc de so sanh duoc voi cac thanh vien khac.
    {
        "query": "Sinh viên được mượn tối đa bao nhiêu tài liệu thư viện và trong bao lâu?",
        "expected_doc_id": "library-services-student",
        "metadata_filter": {"audience": "student"},
        "gold_answer": "Tối đa 3 tài liệu trong 10 ngày; gia hạn tối đa 1 lần, thêm 10 ngày.",
    },
    {
        "query": "Sinh viên cần đạt điều kiện gì để được xét học bổng khuyến khích học tập loại khá?",
        "expected_doc_id": "scholarship-incentive",
        "metadata_filter": None,
        "gold_answer": "Đang trong 8 học kỳ chính; học tập và rèn luyện từ loại khá trở lên; không kỷ luật từ mức khiển trách trở lên; đạt ≥5/10 mọi học phần; tín chỉ đăng ký ≥ kế hoạch đào tạo.",
    },
    {
        "query": "Quy trình hủy một học phần đã đăng ký gồm những bước nào?",
        "expected_doc_id": "course-registration",
        "metadata_filter": None,
        "gold_answer": "Nộp Phiếu đề nghị hủy học phần tại Phòng Quản lý đào tạo trong thời hạn quy định; Phòng Tài chính hoàn học phí theo danh sách đã xác nhận hủy.",
    },
    {
        "query": "Ký túc xá cấm những hành vi nào?",
        "expected_doc_id": "dormitory-rules",
        "metadata_filter": None,
        "gold_answer": "Uống rượu bia; tàng trữ vũ khí/hung khí/chất nổ/ma túy; nấu ăn/tổ chức sinh nhật trong phòng; đánh bài cờ bạc; gây gổ tụ tập bè phái; vượt rào trèo tường.",
    },
    {
        "query": "Giảng viên/cán bộ có được gia hạn tài liệu mượn từ thư viện không?",
        "expected_doc_id": "library-services-faculty",
        "metadata_filter": None,
        "gold_answer": "Không — không áp dụng gia hạn, tài liệu phải trả đúng đợt thu hồi 25/6 và 25/12 hằng năm.",
    },
]

SIMILARITY_PAIRS = [
    (
        "Sinh viên được mượn tối đa 3 tài liệu trong 10 ngày.",
        "Thời hạn mượn sách của sinh viên là 10 ngày, tối đa 3 tài liệu.",
        "cao",
    ),
    (
        "Sinh viên xuất sắc nhận học bổng bằng 1,5 lần mức khá.",
        "Mức học bổng loại xuất sắc cao gấp 1,5 lần loại khá.",
        "cao",
    ),
    (
        "Ký túc xá cấm sinh viên uống rượu bia trong phòng.",
        "Sinh viên nội trú không được sử dụng đồ uống có cồn.",
        "cao",
    ),
    (
        "Sinh viên phải đăng ký học phần đúng thời hạn.",
        "Giảng viên dành tối thiểu 600 giờ mỗi năm cho nghiên cứu khoa học.",
        "thấp",
    ),
    (
        "Sinh viên thuộc diện chính sách có thể được miễn học phí.",
        "Điện thoại di động phải tắt trong cuộc họp.",
        "thấp",
    ),
]


class TfidfEmbedder:
    """Small dependency-free lexical embedding for reproducible lab runs."""

    TOKEN_PATTERN = re.compile(r"\w+", flags=re.UNICODE)

    def __init__(self, texts: list[str]) -> None:
        tokenized = [self._tokenize(text) for text in texts]
        document_frequency: Counter[str] = Counter()
        for tokens in tokenized:
            document_frequency.update(set(tokens))

        self.vocabulary = {
            token: index
            for index, token in enumerate(sorted(document_frequency))
        }
        document_count = max(1, len(tokenized))
        self.idf = {
            token: math.log((1 + document_count) / (1 + frequency)) + 1.0
            for token, frequency in document_frequency.items()
        }
        self._backend_name = "normalized TF-IDF (dependency-free)"

    @classmethod
    def _tokenize(cls, text: str) -> list[str]:
        return cls.TOKEN_PATTERN.findall(text.lower())

    def __call__(self, text: str) -> list[float]:
        counts = Counter(self._tokenize(text))
        vector = [0.0] * len(self.vocabulary)
        for token, count in counts.items():
            index = self.vocabulary.get(token)
            if index is not None:
                vector[index] = count * self.idf[token]

        magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / magnitude for value in vector]


class FilteredStore:
    """Adapter that lets KnowledgeBaseAgent retrieve with one fixed filter."""

    def __init__(self, store: EmbeddingStore, metadata_filter: dict | None) -> None:
        self.store = store
        self.metadata_filter = metadata_filter

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        return self.store.search_with_filter(
            query,
            top_k=top_k,
            metadata_filter=self.metadata_filter,
        )


def extractive_llm(prompt: str) -> str:
    """Return the first retrieved passage as a deterministic grounded answer."""
    context = prompt.partition("NGỮ CẢNH:\n")[2].partition("\n\nCÂU HỎI:")[0]
    first_passage = context.split("\n\n[Đoạn 2]", 1)[0]
    return first_passage.partition("\n")[2].strip()


def prepare_documents(chunker: SentenceChunker) -> list[Document]:
    chunk_documents: list[Document] = []
    for document in load_documents(DATA_DIR):
        chunk_documents.extend(chunk_document(document, chunker))
    return chunk_documents


def select_embedder(provider: str, texts: list[str]) -> Callable[[str], list[float]]:
    if provider == "local":
        return LocalEmbedder()
    if provider == "mock":
        return _mock_embed
    return TfidfEmbedder(texts)


def run(provider: str = "lexical") -> dict:
    # Strategy assigned to Vi Minh Hiển in PHAN_CONG.md.
    chunker = SentenceChunker()
    chunk_documents = prepare_documents(chunker)

    embedding_corpus = [document.content for document in chunk_documents]
    embedding_corpus.extend(item["query"] for item in BENCHMARKS)
    for sentence_a, sentence_b, _ in SIMILARITY_PAIRS:
        embedding_corpus.extend([sentence_a, sentence_b])

    embedder = select_embedder(provider, embedding_corpus)
    store = EmbeddingStore(
        collection_name="vi_minh_hien_sentence_benchmark",
        embedding_fn=embedder,
    )
    store.add_documents(chunk_documents)

    retrieval_results = []
    for item in BENCHMARKS:
        results = store.search_with_filter(
            item["query"],
            top_k=3,
            metadata_filter=item["metadata_filter"],
        )
        retrieved_doc_ids = [
            result["metadata"].get("doc_id") for result in results
        ]
        agent = KnowledgeBaseAgent(
            store=FilteredStore(store, item["metadata_filter"]),
            llm_fn=extractive_llm,
        )
        retrieval_results.append(
            {
                **item,
                "top_1": results[0] if results else None,
                "top_3_doc_ids": retrieved_doc_ids,
                "relevant_in_top_3": item["expected_doc_id"] in retrieved_doc_ids,
                "agent_answer": agent.answer(item["query"], top_k=3),
            }
        )

    similarity_results = []
    for sentence_a, sentence_b, prediction in SIMILARITY_PAIRS:
        score = compute_similarity(embedder(sentence_a), embedder(sentence_b))
        similarity_results.append(
            {
                "sentence_a": sentence_a,
                "sentence_b": sentence_b,
                "prediction": prediction,
                "score": score,
            }
        )

    return {
        "student": "Vi Minh Hiển",
        "student_id": "2A202601743",
        "strategy": "SentenceChunker(max_sentences_per_chunk=3)",
        "embedding_backend": getattr(embedder, "_backend_name", type(embedder).__name__),
        "document_count": len(load_documents(DATA_DIR)),
        "chunk_count": len(chunk_documents),
        "retrieval": retrieval_results,
        "similarity": similarity_results,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider",
        choices=["lexical", "local", "mock"],
        default="lexical",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run(provider=args.provider)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\nSaved benchmark results to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
