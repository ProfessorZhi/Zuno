import asyncio
import os
from datetime import datetime, timedelta
from uuid import uuid4

from agentchat.core.models.manager import ModelManager
from agentchat.schema.chunk import ChunkModel
from agentchat.services.rag.doc_parser.docx import docx_parser
from agentchat.services.rag.doc_parser.excel import excel_to_txt
from agentchat.services.rag.doc_parser.image import build_image_chunk, describe_image
from agentchat.services.rag.doc_parser.markdown import markdown_parser
from agentchat.services.rag.doc_parser.other_file import other_file_to_txt
from agentchat.services.rag.doc_parser.pdf import pdf_parser
from agentchat.services.rag.doc_parser.pptx import pptx_parser
from agentchat.services.rag.doc_parser.text import text_parser
from agentchat.settings import app_settings

IMAGE_SUFFIXES = {"jpg", "jpeg", "png", "bmp", "webp", "tiff"}
TEXT_LIKE_SUFFIXES = {"txt", "json", "html", "htm", "csv"}
EXCEL_SUFFIXES = {"xls", "xlsx"}


class DocParser:
    @staticmethod
    def _build_markdown_parser(config: dict | None):
        index_settings = (config or {}).get("index_settings", {})
        chunk_size = index_settings.get("chunk_size", 1024)
        overlap = index_settings.get("overlap", 128)
        min_chunk_size = min(256, chunk_size)
        return markdown_parser.__class__(
            min_chunk_size=min_chunk_size,
            max_chunk_size=chunk_size,
            overlap_size=overlap,
        )

    @staticmethod
    def _build_text_parser(config: dict | None):
        index_settings = (config or {}).get("index_settings", {})
        parser = text_parser.__class__()
        parser.chunk_size = index_settings.get("chunk_size", parser.chunk_size)
        parser.overlap_size = index_settings.get("overlap", parser.overlap_size)
        return parser

    @classmethod
    async def parse_doc_into_chunks(
        cls,
        file_id,
        file_path,
        knowledge_id,
        max_concurrent_tasks=5,
        source_url: str | None = None,
        knowledge_config: dict | None = None,
    ):
        file_suffix = file_path.split(".")[-1].lower()
        chunks = []
        index_settings = (knowledge_config or {}).get("index_settings", {})
        image_mode = index_settings.get("image_indexing_mode", "dual")
        markdown_parser_instance = cls._build_markdown_parser(knowledge_config)
        text_parser_instance = cls._build_text_parser(knowledge_config)
        if file_suffix == "md":
            chunks = await markdown_parser_instance.parse_into_chunks(file_id, file_path, knowledge_id)
        elif file_suffix == "txt":
            chunks = await text_parser_instance.parse_into_chunks(file_id, file_path, knowledge_id)
        elif file_suffix == "docx":
            chunks = await docx_parser.parse_into_chunks(file_id, file_path, knowledge_id)
        elif file_suffix == "pdf":
            chunks = await pdf_parser.parse_into_chunks(
                file_id,
                file_path,
                knowledge_id,
                markdown_parser_instance=markdown_parser_instance,
                image_mode=image_mode,
            )
        elif file_suffix == "pptx":
            chunks = await pptx_parser.parse_into_chunks(file_id, file_path, knowledge_id)
        elif file_suffix in IMAGE_SUFFIXES:
            description = describe_image(file_path)
            if image_mode == "text_only":
                chunk_id = f"{os.path.basename(file_path).split('_')[0]}_{uuid4().hex}"
                update_time = datetime.utcnow() + timedelta(hours=8)
                chunks = [
                    ChunkModel(
                        chunk_id=chunk_id[:128] if len(chunk_id) > 128 else chunk_id,
                        content=description,
                        file_id=file_id,
                        file_name=os.path.basename(file_path),
                        knowledge_id=knowledge_id,
                        update_time=update_time.isoformat(),
                    )
                ]
            else:
                chunks = [
                    build_image_chunk(
                        file_id=file_id,
                        file_name=os.path.basename(file_path),
                        knowledge_id=knowledge_id,
                        source_url=source_url or "",
                        image_name=os.path.basename(file_path),
                        description=description,
                    )
                ]
        elif file_suffix in EXCEL_SUFFIXES:
            new_file_path = excel_to_txt(file_path)
            chunks = await text_parser_instance.parse_into_chunks(file_id, new_file_path, knowledge_id)
        elif file_suffix in TEXT_LIKE_SUFFIXES:
            new_file_path = other_file_to_txt(file_path)
            chunks = await text_parser_instance.parse_into_chunks(file_id, new_file_path, knowledge_id)

        if app_settings.rag.enable_summary:
            semaphore = asyncio.Semaphore(max_concurrent_tasks)
            tasks = [asyncio.create_task(cls.generate_summary(chunk, semaphore)) for chunk in chunks if chunk.modality == "text"]
            summarized_chunks = await asyncio.gather(*tasks)
            text_index = 0
            for index, chunk in enumerate(chunks):
                if chunk.modality == "text":
                    chunks[index] = summarized_chunks[text_index]
                    text_index += 1

        return chunks

    @classmethod
    async def generate_summary(cls, chunk: ChunkModel, semaphore):
        async_client = ModelManager.get_conversation_model()

        async with semaphore:
            prompt = f"""
                你是一个专业的摘要生成助手，请根据以下要求为文本生成一段摘要：
                ## 需要总结的文本：
                {chunk.content}
                ## 要求：
                1. 摘要字数控制在 100 字左右。
                2. 摘要中仅包含文字和字母，不得出现链接或其他特殊符号。
                3. 只输出摘要部分，不准输出 “以下是文本的摘要” 等字样。
            """
            response = await async_client.ainvoke(prompt)
            chunk.summary = response.content
            return chunk


doc_parser = DocParser()
