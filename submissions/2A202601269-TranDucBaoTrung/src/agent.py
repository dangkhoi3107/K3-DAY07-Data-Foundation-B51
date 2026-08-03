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
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy ngữ cảnh phù hợp trong kho tri thức."

        context = "\n\n".join(
            (
                f"[{index}] Nguồn: "
                f"{result['metadata'].get('doc_id', result['id'])}\n"
                f"{result['content']}"
            )
            for index, result in enumerate(results, start=1)
        )
        prompt = (
            "Chỉ trả lời dựa trên ngữ cảnh được cung cấp. "
            "Nếu ngữ cảnh không đủ, hãy nói rõ là không đủ thông tin.\n\n"
            f"NGỮ CẢNH:\n{context}\n\n"
            f"CÂU HỎI: {question}\n"
            "TRẢ LỜI:"
        )
        return self.llm_fn(prompt)
