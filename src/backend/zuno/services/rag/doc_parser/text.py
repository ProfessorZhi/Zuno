import os
from datetime import datetime, timedelta

from zuno.schema.chunk import ChunkModel
from zuno.services.rag.doc_parser.chunk_ids import build_chunk_id, build_source_chunk_id
from zuno.settings import app_settings


class TextParser:
    def __init__(self):
        self.chunk_size = app_settings.rag.split.get("chunk_size")
        self.overlap_size = app_settings.rag.split.get("overlap_size")

    async def split_text_into_chunks_by_lines(self, text):
        lines = text.splitlines()
        chunks = []
        current_chunk = []
        current_length = 0

        for line in lines:
            line_length = len(line)

            if current_length + line_length > self.chunk_size:
                if current_chunk:
                    chunk = "\n".join(current_chunk)
                    chunks.append(chunk)
                    overlap = chunk[-self.overlap_size:] if self.overlap_size > 0 else ""
                    current_chunk = [overlap] if overlap else []
                    current_length = len(overlap)

            current_chunk.append(line)
            current_length += line_length

        if current_chunk:
            chunk = "\n".join(current_chunk)
            chunks.append(chunk)

        return chunks

    async def parse_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text

    async def parse_into_chunks(self, file_id, file_path, knowledge_id):
        file_content = await self.parse_file(file_path)
        contents = await self.split_text_into_chunks_by_lines(file_content)
        chunks = []
        update_time = datetime.utcnow() + timedelta(hours=8)
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


text_parser = TextParser()


__all__ = ["TextParser", "text_parser"]
