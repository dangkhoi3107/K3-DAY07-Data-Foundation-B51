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
        retrieved_chunks = self.store.search(question, top_k=top_k)
        context = "\n\n".join(
            f"[Đoạn {index}]\n{result['content']}"
            for index, result in enumerate(retrieved_chunks, start=1)
        )

        if not context:
            context = "Không tìm thấy ngữ cảnh liên quan."

        prompt = (
            "Hãy trả lời câu hỏi chỉ dựa trên ngữ cảnh được cung cấp. "
            "Nếu ngữ cảnh không đủ thông tin, hãy nói rằng bạn không biết.\n\n"
            f"NGỮ CẢNH:\n{context}\n\n"
            f"CÂU HỎI:\n{question}\n\n"
            "TRẢ LỜI:"
        )
        return self.llm_fn(prompt)
