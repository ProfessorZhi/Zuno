import os.path
import re
from datetime import datetime, timedelta, timezone

from zuno.schema.chunk import ChunkModel
from zuno.services.rag.doc_parser.chunk_ids import build_chunk_id, build_source_chunk_id


class MarkdownParser:
    CHINA_TZ = timezone(timedelta(hours=8))

    def __init__(self, min_chunk_size=256, max_chunk_size=512, overlap_size=128):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.header_pattern = r"^(#{1,5})\s+(.+)$"
        self.link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        self.img_pattern = r"!\[([^\]]+)\]\(([^)]+)\)"

    def find_link_boundaries(self, text):
        boundaries = []
        for pattern in [self.link_pattern, self.img_pattern]:
            for match in re.finditer(pattern, text):
                boundaries.append((match.start(), match.end()))
        return boundaries

    def is_safe_cut_position(self, text, position, boundaries):
        for start, end in boundaries:
            if start < position < end:
                return False
        return True

    def find_best_cut_position(self, text, target_position, boundaries):
        if self.is_safe_cut_position(text, target_position, boundaries):
            for i in range(target_position, min(len(text), target_position + 50)):
                if text[i] in ".!?\n" and self.is_safe_cut_position(text, i + 1, boundaries):
                    return i + 1

        for i in range(target_position, max(0, target_position - 100), -1):
            if self.is_safe_cut_position(text, i, boundaries):
                for j in range(i, max(0, i - 50), -1):
                    if text[j] in ".!?\n" and self.is_safe_cut_position(text, j + 1, boundaries):
                        return j + 1
                return i

        return target_position

    async def split_text_with_headers(self, text, header_path):
        chunks = []
        header_overhead = len(header_path) + 4

        if header_overhead > 200:
            header_parts = header_path.split(" > ")
            while len(" > ".join(header_parts)) + 4 > 200 and len(header_parts) > 1:
                header_parts = header_parts[1:]
            header_path = " > ".join(header_parts)
            header_overhead = len(header_path) + 4

        paragraphs = text.split("\n\n")
        current_chunk_text = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            test_text = current_chunk_text + ("\n\n" if current_chunk_text else "") + paragraph
            full_test_chunk = f"{header_path}\n\n{test_text}"

            if len(full_test_chunk) <= 1024:
                current_chunk_text = test_text

                if len(full_test_chunk) >= self.min_chunk_size + header_overhead:
                    if len(full_test_chunk) > self.max_chunk_size + header_overhead:
                        prev_text = current_chunk_text.rsplit("\n\n" + paragraph, 1)[0] if "\n\n" + paragraph in current_chunk_text else ""
                        if prev_text:
                            full_chunk = f"{header_path}\n\n{prev_text}"
                            if len(full_chunk) >= self.min_chunk_size:
                                chunks.append(full_chunk)

                        current_chunk_text = paragraph
            else:
                if current_chunk_text:
                    full_chunk = f"{header_path}\n\n{current_chunk_text}"
                    if len(full_chunk) >= self.min_chunk_size:
                        chunks.append(full_chunk)

                current_chunk_text = paragraph
                full_chunk = f"{header_path}\n\n{current_chunk_text}"

                if len(full_chunk) > self.max_chunk_size + header_overhead:
                    chunks.extend(await self.split_long_paragraph(paragraph, header_path))
                    current_chunk_text = ""

        if current_chunk_text:
            full_chunk = f"{header_path}\n\n{current_chunk_text}"
            if len(full_chunk) >= self.min_chunk_size:
                chunks.append(full_chunk)
            elif chunks:
                last_chunk = chunks[-1]
                combined = last_chunk + "\n\n" + current_chunk_text
                if len(combined) <= 1024:
                    chunks[-1] = combined
                else:
                    chunks.append(full_chunk)
            else:
                chunks.append(full_chunk)

        return chunks

    async def split_long_paragraph(self, paragraph, header_path):
        chunks = []
        header_overhead = len(header_path) + 4
        max_text_size = self.max_chunk_size - header_overhead
        boundaries = self.find_link_boundaries(paragraph)

        start = 0
        while start < len(paragraph):
            end = start + max_text_size

            if end >= len(paragraph):
                chunk_text = paragraph[start:].strip()
                if chunk_text:
                    full_chunk = f"{header_path}\n\n{chunk_text}"
                    chunks.append(full_chunk)
                break

            end = self.find_best_cut_position(paragraph, end, boundaries)

            chunk_text = paragraph[start:end].strip()
            if chunk_text:
                full_chunk = f"{header_path}\n\n{chunk_text}"
                chunks.append(full_chunk)

            start = end - self.overlap_size if end > self.overlap_size else end

        return chunks

    async def parse_markdown_headers(self, text):
        current_headers = {i: "" for i in range(1, 6)}
        chunks = []
        current_text = []

        lines = text.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            header_match = re.match(self.header_pattern, line)

            if header_match:
                if current_text:
                    full_text = "\n".join(current_text)
                    header_path = " > ".join([h for h in current_headers.values() if h])
                    chunks.extend(await self.split_text_with_headers(full_text, header_path))
                    current_text = []

                level = len(header_match.group(1))
                header_text = header_match.group(2)
                current_headers[level] = header_text

                for nested_level in range(level + 1, 6):
                    current_headers[nested_level] = ""
            else:
                current_text.append(line)

            i += 1

        if current_text:
            full_text = "\n".join(current_text)
            header_path = " > ".join([h for h in current_headers.values() if h])
            chunks.extend(await self.split_text_with_headers(full_text, header_path))

        return chunks

    async def parse_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text

    async def parse_into_chunks(self, file_id: str, file_path: str, knowledge_id: str):
        text = await self.parse_file(file_path)
        contents = await self.parse_markdown_headers(text)
        chunks = []
        update_time = datetime.now(self.CHINA_TZ)
        for index, content in enumerate(contents):
            source_chunk_id = build_source_chunk_id(
                file_id=file_id,
                file_name=os.path.basename(file_path),
                index=index,
            )
            chunk_id = build_chunk_id(
                file_id=file_id,
                file_name=os.path.basename(file_path),
                content=content,
                index=index,
            )
            chunks.append(
                ChunkModel(
                    chunk_id=chunk_id,
                    content=content,
                    file_id=file_id,
                    file_name=os.path.basename(file_path),
                    knowledge_id=knowledge_id,
                    update_time=update_time.isoformat(),
                    source_chunk_id=source_chunk_id,
                )
            )

        return chunks


markdown_parser = MarkdownParser()


__all__ = ["MarkdownParser", "markdown_parser"]
