from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse
from uuid import uuid4

import requests

from agentchat.schema.workspace import WorkspaceAttachment
from agentchat.services.rag.parser import doc_parser
from agentchat.services.storage import storage_client
from agentchat.settings import app_settings
from agentchat.tools.image2text.action import _image_to_text

IMAGE_SUFFIXES = {"jpg", "jpeg", "png", "gif", "webp", "bmp", "tiff"}
DOCUMENT_SUFFIXES = {"pdf", "doc", "docx", "ppt", "pptx", "txt", "md", "csv", "xls", "xlsx"}
CHAT_IMAGE_MIME_PREFIX = "image/"
MAX_TOTAL_EXTRACTED_CHARS = 12000
MAX_SINGLE_ATTACHMENT_CHARS = 5000


def _get_extension(name: str, fallback_url: str = "") -> str:
    suffix = Path(name or "").suffix.lower().lstrip(".")
    if suffix:
        return suffix

    parsed = urlparse(fallback_url or "")
    return Path(parsed.path).suffix.lower().lstrip(".")


def classify_attachment(attachment: WorkspaceAttachment) -> str | None:
    mime_type = (attachment.mime_type or "").lower()
    if mime_type.startswith(CHAT_IMAGE_MIME_PREFIX):
        return "image"

    extension = _get_extension(attachment.name, attachment.url)
    if extension in IMAGE_SUFFIXES:
        return "image"
    if extension in DOCUMENT_SUFFIXES:
        return "document"
    return None


def validate_workspace_attachments(
    attachments: Iterable[WorkspaceAttachment],
    workspace_mode: str,
) -> None:
    for attachment in attachments:
        kind = classify_attachment(attachment)
        if kind is None:
            raise ValueError(
                f"附件 {attachment.name} 暂不支持。当前仅支持图片、PDF、Word、PPT、TXT、Markdown、Excel。"
            )
        if workspace_mode == "normal" and kind != "image":
            raise ValueError(
                f"聊天模式当前仅支持图片。附件 {attachment.name} 请切换到 Agent 模式后再分析。"
            )


def _try_download_from_storage(url: str, local_path: str) -> bool:
    if not app_settings.storage:
        return False

    base_url = (app_settings.storage.active.base_url or "").rstrip("/")
    normalized_url = (url or "").strip()
    if not base_url or not normalized_url.startswith(base_url):
        return False

    object_name = unquote(normalized_url[len(base_url):].lstrip("/"))
    if not object_name:
        return False

    try:
        storage_client.download_file(object_name, local_path)
        return os.path.exists(local_path) and os.path.getsize(local_path) > 0
    except Exception:
        return False


def _download_attachment(attachment: WorkspaceAttachment) -> str:
    extension = _get_extension(attachment.name, attachment.url)
    suffix = f".{extension}" if extension else ""
    fd, local_path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)

    if _try_download_from_storage(attachment.url, local_path):
        return local_path

    response = requests.get(attachment.url, timeout=60)
    response.raise_for_status()
    with open(local_path, "wb") as file:
        file.write(response.content)

    return local_path


async def _extract_attachment_text(attachment: WorkspaceAttachment, session_id: str) -> tuple[str, str]:
    kind = classify_attachment(attachment)
    local_path = _download_attachment(attachment)

    try:
        if kind == "image":
            return kind, await asyncio.to_thread(_image_to_text, local_path)

        chunks = await doc_parser.parse_doc_into_chunks(
            file_id=f"workspace_attachment_{uuid4().hex}",
            file_path=local_path,
            knowledge_id=session_id or "workspace_attachment",
        )
        content = "\n\n".join(chunk.content for chunk in chunks if chunk.content).strip()
        if not content:
            raise ValueError(f"附件 {attachment.name} 没有提取到可读内容。")
        return kind, content
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)


def _truncate_text(content: str, remaining_chars: int) -> str:
    excerpt = content[: min(remaining_chars, MAX_SINGLE_ATTACHMENT_CHARS)].strip()
    if len(content) > len(excerpt):
        excerpt += "\n[内容已截断]"
    return excerpt


def _build_attachment_block(
    attachment: WorkspaceAttachment,
    index: int,
    kind: str,
    excerpt: str,
) -> str:
    lines = [
        f"附件 {index}",
        f"名称: {attachment.name}",
        f"类型: {'图片' if kind == 'image' else '文档'}",
    ]

    if kind == "image" and attachment.url:
        lines.append(f"source_url: {attachment.url}")

    lines.extend(
        [
            "提取内容:",
            excerpt,
        ]
    )

    if kind == "image" and attachment.url:
        lines.append(
            "如果用户要求基于这张图重绘、换背景、改配色、做变体，请调用 text_to_image，并把 reference_image_url 设为上面的 source_url。"
        )

    return "\n".join(lines)


async def build_workspace_attachment_prompt(
    query: str,
    attachments: list[WorkspaceAttachment],
    workspace_mode: str,
    session_id: str,
) -> str:
    if not attachments:
        return query

    validate_workspace_attachments(attachments, workspace_mode)

    blocks: list[str] = []
    remaining_chars = MAX_TOTAL_EXTRACTED_CHARS

    for index, attachment in enumerate(attachments, start=1):
        if remaining_chars <= 0:
            break

        kind, extracted = await _extract_attachment_text(attachment, session_id)
        excerpt = _truncate_text(extracted, remaining_chars)
        remaining_chars -= len(excerpt)
        blocks.append(_build_attachment_block(attachment, index, kind, excerpt))

    if not blocks:
        return query

    attachment_prompt = "\n\n".join(blocks)
    return (
        f"{query}\n\n"
        "<uploaded_attachments>\n"
        f"{attachment_prompt}\n"
        "</uploaded_attachments>\n\n"
        "请结合用户问题和附件提取内容回答。"
        "如果用户要求基于上传图片生成新图、改背景、改配色、做海报或做变体，优先调用 text_to_image，"
        "并使用附件里的 source_url 作为 reference_image_url。"
        "回答时优先输出高信息密度结果，不要空泛概括。"
    )
