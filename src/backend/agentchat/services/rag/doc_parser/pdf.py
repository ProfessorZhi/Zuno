import os
import pathlib
import re
import tempfile

import aiofiles
import pymupdf
import pymupdf4llm
from loguru import logger

from agentchat.schema.chunk import ChunkModel
from agentchat.settings import app_settings
from agentchat.services.rag.doc_parser.image import build_image_chunk
from agentchat.services.rag.doc_parser.markdown import markdown_parser
from agentchat.services.rag.doc_parser.text import text_parser
from agentchat.services.rewrite.markdown_rewrite import markdown_rewriter
from agentchat.services.storage import storage_client
from agentchat.utils.file_utils import (
    generate_unique_filename,
    get_convert_markdown_images_dir,
    get_object_storage_base_path,
)


class PDFParser:
    MIN_TEXT_CHARS_FOR_IMAGE_CHUNKS = 400

    def __init__(self):
        pass

    async def convert_markdown(self, file_path: str):
        markdown_dir, images_dir = get_convert_markdown_images_dir()
        md_text_words = pymupdf4llm.to_markdown(
            doc=file_path,
            write_images=True,
            image_path=images_dir,
            image_format="png",
            dpi=300,
        )
        markdown_output_path = os.path.join(markdown_dir, generate_unique_filename(file_path, "md"))
        output_markdown_file = pathlib.Path(markdown_output_path)
        output_markdown_file.write_bytes(md_text_words.encode())
        logger.info(f"PDF Convert MarkDown Successful, MarkDown Path: {output_markdown_file}")

        file_upload_url_map = await self.upload_folder_to_oss(images_dir)
        image_desc_dict = await markdown_rewriter.get_image_description(
            await markdown_rewriter._get_image_dict(markdown_output_path)
        )
        new_markdown_text = await markdown_rewriter.process_markdown(
            await markdown_rewriter._read_markdown(markdown_output_path),
            file_upload_url_map,
            image_desc_dict,
        )
        with open(markdown_output_path, "w", encoding="utf-8") as file:
            file.write(new_markdown_text)

        await self.upload_file_to_oss(markdown_output_path)
        return markdown_output_path, file_upload_url_map, image_desc_dict

    def _strip_markdown_images(self, markdown_text: str) -> str:
        cleaned = re.sub(r"!\[[^\]]*]\([^)]+\)", "", markdown_text)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def _extract_plain_text(self, file_path: str) -> str:
        doc = pymupdf.open(file_path)
        try:
            pages = [page.get_text() for page in doc]
        finally:
            doc.close()
        plain_text = "\n".join(pages)
        plain_text = re.sub(r"\n{3,}", "\n\n", plain_text)
        return plain_text.strip()

    async def _build_text_focused_markdown(self, markdown_file: str) -> str:
        async with aiofiles.open(markdown_file, "r", encoding="utf-8") as file:
            original_text = await file.read()
        cleaned_text = self._strip_markdown_images(original_text)
        if cleaned_text == original_text.strip():
            return markdown_file

        temp_markdown = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8")
        try:
            temp_markdown.write(cleaned_text)
            return temp_markdown.name
        finally:
            temp_markdown.close()

    async def _build_plain_text_fallback_file(self, file_path: str) -> str | None:
        plain_text = self._extract_plain_text(file_path)
        if len(plain_text) < self.MIN_TEXT_CHARS_FOR_IMAGE_CHUNKS:
            return None
        temp_text = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
        try:
            temp_text.write(plain_text)
            return temp_text.name
        finally:
            temp_text.close()

    async def parse_into_chunks(self, file_id, file_path, knowledge_id, markdown_parser_instance=None, image_mode: str = "dual"):
        markdown_file, image_url_map, image_desc_dict = await self.convert_markdown(file_path)
        parser = markdown_parser_instance or markdown_parser
        text_markdown_file = await self._build_text_focused_markdown(markdown_file)
        text_chunks = await parser.parse_into_chunks(file_id, text_markdown_file, knowledge_id)
        if not text_chunks:
            fallback_text_file = await self._build_plain_text_fallback_file(file_path)
            if fallback_text_file:
                logger.info(
                    "Fallback to raw PDF text extraction because markdown conversion produced no text chunks",
                    file_path=file_path,
                )
                text_chunks = await text_parser.parse_into_chunks(file_id, fallback_text_file, knowledge_id)
        image_chunks = []
        if image_mode == "text_only":
            return text_chunks
        total_text_chars = sum(len(chunk.content or "") for chunk in text_chunks)
        if total_text_chars >= self.MIN_TEXT_CHARS_FOR_IMAGE_CHUNKS:
            logger.info(
                "Skip standalone PDF image chunks because extracted text is already rich enough",
                total_text_chars=total_text_chars,
                file_path=file_path,
            )
            return text_chunks
        for image_name, source_url in image_url_map.items():
            description = image_desc_dict.get(image_name, "").strip()
            if not description:
                continue
            image_chunks.append(
                build_image_chunk(
                    file_id=file_id,
                    file_name=os.path.basename(file_path),
                    knowledge_id=knowledge_id,
                    source_url=source_url,
                    image_name=image_name,
                    description=description,
                )
            )
        return text_chunks + image_chunks

    async def upload_file_to_oss(self, file_path):
        async with aiofiles.open(file_path, "rb") as file:
            file_content = await file.read()
            oss_object_name = get_object_storage_base_path(os.path.basename(file_path))
            sign_url = f"{app_settings.storage.active.base_url.rstrip('/')}/{oss_object_name.lstrip('/')}"

            storage_client.sign_url_for_get(sign_url)
            storage_client.upload_file(oss_object_name, file_content)
            return sign_url

    async def upload_folder_to_oss(self, file_dir):
        file_upload_url_map = {}
        if not os.path.exists(file_dir):
            return file_upload_url_map

        for file_name in os.listdir(file_dir):
            file_path = os.path.join(file_dir, file_name)
            if not os.path.isfile(file_path):
                continue
            file_upload_url_map[file_name] = await self.upload_file_to_oss(file_path)
            logger.info(f"文件 {file_name} 上传成功")

        return file_upload_url_map


pdf_parser = PDFParser()
