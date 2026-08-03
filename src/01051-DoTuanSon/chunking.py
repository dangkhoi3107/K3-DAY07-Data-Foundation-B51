from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Split after sentence-ending punctuation (. ! ?) followed by whitespace.
        # This covers ". ", "! ", "? " and ".\n".
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        sentences = [part.strip() for part in parts if part.strip()]

        chunks: list[str] = []
        for start in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[start : start + self.max_sentences_per_chunk]
            chunks.append(" ".join(group))
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Small enough already: keep as a single chunk.
        if len(current_text) <= self.chunk_size:
            return [current_text] if current_text.strip() else []

        # No separators left (or the "" separator): hard-split by size.
        if not remaining_separators or remaining_separators[0] == "":
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        separator = remaining_separators[0]
        rest = remaining_separators[1:]
        parts = current_text.split(separator)

        # Greedily merge neighbouring parts back together up to chunk_size,
        # recursing with the next separator on parts that are still too large.
        chunks: list[str] = []
        buffer = ""
        for part in parts:
            candidate = part if not buffer else buffer + separator + part
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue
            if buffer:
                chunks.append(buffer)
                buffer = ""
            if len(part) <= self.chunk_size:
                buffer = part
            else:
                chunks.extend(self._split(part, rest))
        if buffer:
            chunks.append(buffer)
        return chunks


class HeadingChunker:
    """
    Chunk Markdown theo cấu trúc heading/section (chiến lược tự viết của K3).

    Ý tưởng: các tài liệu quy định đại học được viết thành từng mục có tiêu đề
    (`# Tiêu đề`, `## Mục con`...). Cắt theo heading giữ nguyên một "đơn vị ý
    nghĩa" trọn vẹn trong mỗi chunk (ví dụ toàn bộ mục "Gia hạn" hay "Xử lý trễ
    hạn"), thay vì cắt cứng giữa câu như FixedSize.

    Quy tắc:
        - Mỗi chunk = dòng heading + toàn bộ nội dung tới heading kế tiếp.
        - Heading là dòng bắt đầu bằng 1..`max_heading_level` ký tự '#' rồi tới
          khoảng trắng (cú pháp ATX của Markdown).
        - Phần văn bản đứng trước heading đầu tiên (nếu có) thành một chunk riêng.
        - Section "chỉ có tiêu đề, không có nội dung" (ví dụ dòng `# Tiêu đề`
          đứng ngay trước một `## Mục con`) được GỘP vào section kế tiếp, tránh
          tạo chunk rỗng nghĩa chỉ chứa vài từ khóa của tiêu đề.
        - Nếu một section dài hơn `max_chunk_size`, tách nhỏ tiếp bằng
          RecursiveChunker để không tạo chunk quá lớn.
        - Bỏ qua các chunk rỗng/chỉ có khoảng trắng.
    """

    def __init__(self, max_heading_level: int = 3, max_chunk_size: int = 1000) -> None:
        self.max_heading_level = max_heading_level
        self.max_chunk_size = max_chunk_size
        self._heading_re = re.compile(rf"^#{{1,{max_heading_level}}}\s+\S")

    def _is_heading(self, line: str) -> bool:
        return bool(self._heading_re.match(line))

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Gom các dòng thành từng section, mở section mới mỗi khi gặp heading.
        sections: list[list[str]] = []
        current: list[str] = []
        for line in text.splitlines():
            if self._is_heading(line) and current:
                sections.append(current)
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append(current)

        # Gộp section "chỉ có tiêu đề" (không có dòng nội dung thực) vào section sau.
        merged: list[list[str]] = []
        carry: list[str] = []
        for section in sections:
            body = [ln for ln in section[1:] if ln.strip()]
            if not body:
                carry.extend(section)  # để dành, ghép vào section kế tiếp
            else:
                merged.append(carry + section)
                carry = []
        if carry:  # tiêu đề cuối cùng không có nội dung -> giữ riêng
            merged.append(carry)

        chunks: list[str] = []
        splitter = RecursiveChunker(chunk_size=self.max_chunk_size)
        for section in merged:
            block = "\n".join(section).strip()
            if not block:
                continue
            if len(block) <= self.max_chunk_size:
                chunks.append(block)
            else:
                chunks.extend(splitter.chunk(block))
        return chunks


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size),
            "by_sentences": SentenceChunker(),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        comparison: dict = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            count = len(chunks)
            avg_length = sum(len(c) for c in chunks) / count if count else 0.0
            comparison[name] = {
                "count": count,
                "avg_length": avg_length,
                "chunks": chunks,
            }
        return comparison
