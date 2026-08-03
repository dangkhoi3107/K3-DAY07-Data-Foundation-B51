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
        # 1. Retrieve the most relevant chunks from the knowledge base.
        results = self.store.search(question, top_k=top_k)

        # 2. Build a prompt grounding the answer in the retrieved context.
        if results:
            context = "\n\n".join(
                f"[{i + 1}] {result['content']}" for i, result in enumerate(results)
            )
        else:
            context = "(no relevant context found)"

        prompt = (
            "Answer the question using only the context below. "
            "If the context does not contain the answer, say you don't know.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        # 3. Call the LLM to generate the final answer.
        return self.llm_fn(prompt)
