from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        if self.store.get_collection_size() == 0:
            return "Knowledge base đang rỗng — chưa có tài liệu nào để trả lời câu hỏi này."

        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy đoạn tài liệu nào liên quan để trả lời câu hỏi này."

        context = "\n".join(
            f"[{index}] ({result['metadata'].get('doc_id', result['id'])}) {result['content']}"
            for index, result in enumerate(results, start=1)
        )

        prompt = (
            "Chỉ dùng thông tin trong Context dưới đây để trả lời. "
            "Nếu context không đủ để trả lời chắc chắn, hãy nói rõ là không đủ dữ liệu.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        )
        return self.llm_fn(prompt)
