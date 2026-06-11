import base64
import mimetypes
import os
import tempfile
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse

import requests
from langchain.tools import tool
from loguru import logger

from agentchat.services.storage import storage_client
from agentchat.settings import app_settings
from agentchat.tools.image2text.action import _image_to_text

DEFAULT_MINIMAX_BASE_URL = "https://api.minimaxi.com/v1"
DEFAULT_MINIMAX_IMAGE_MODEL = "image-01"


def _resolve_minimax_image_config() -> tuple[str, str, str]:
    text2image_config = app_settings.multi_models.text2image
    conversation_config = app_settings.multi_models.conversation_model

    api_key = (text2image_config.api_key or conversation_config.api_key or "").strip()
    base_url = (
        text2image_config.base_url
        or conversation_config.base_url
        or DEFAULT_MINIMAX_BASE_URL
    ).strip()
    model_name = (text2image_config.model_name or DEFAULT_MINIMAX_IMAGE_MODEL).strip()

    if not api_key:
        raise ValueError("MiniMax image generation is not configured with a usable API key.")

    return api_key, (base_url or DEFAULT_MINIMAX_BASE_URL).rstrip("/"), model_name


def _load_reference_image(reference_image_url: str) -> tuple[bytes, str]:
    image_bytes: bytes
    content_type = "image/png"
    base_url = (app_settings.storage.active.base_url or "").rstrip("/")
    normalized_url = reference_image_url.strip()

    if base_url and normalized_url.startswith(base_url):
        object_name = unquote(normalized_url[len(base_url):].lstrip("/"))
        suffix = PurePosixPath(object_name).suffix or ".png"
        fd, local_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        try:
            storage_client.download_file(object_name, local_path)
            with open(local_path, "rb") as file:
                image_bytes = file.read()
            guessed_content_type, _ = mimetypes.guess_type(object_name)
            if guessed_content_type:
                content_type = guessed_content_type
        finally:
            if os.path.exists(local_path):
                os.remove(local_path)
    else:
        response = requests.get(reference_image_url, timeout=120)
        response.raise_for_status()
        image_bytes = response.content
        content_type = response.headers.get("content-type", "image/png").split(";")[0].strip() or "image/png"

    return image_bytes, content_type


def _upload_generated_image(image_bytes: bytes, source_name: str) -> str:
    parsed = urlparse(source_name)
    file_name = PurePosixPath(unquote(parsed.path)).name if parsed.path else source_name
    file_name = file_name or f"generated_{PurePosixPath(source_name).name or 'image'}.png"
    if "." not in file_name:
        file_name = f"{file_name}.png"

    oss_object_name = f"text_to_image/{file_name}"
    storage_client.upload_file(oss_object_name, image_bytes, content_type="image/png")
    return f"{app_settings.storage.active.base_url.rstrip('/')}/{oss_object_name.lstrip('/')}"


def _build_reference_bundle(reference_image_url: str) -> tuple[str, str]:
    normalized_url = reference_image_url.strip()
    if not normalized_url:
        return "", ""

    local_path = None
    try:
        image_bytes, content_type = _load_reference_image(normalized_url)
        parsed = urlparse(normalized_url)
        suffix = PurePosixPath(unquote(parsed.path)).suffix or ".png"
        fd, local_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        with open(local_path, "wb") as file:
            file.write(image_bytes)
        reference_description = _image_to_text(local_path).strip()
    except Exception as err:
        logger.warning(f"Failed to extract reference image description: {err}")
        return "", ""
    finally:
        if local_path and os.path.exists(local_path):
            os.remove(local_path)

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{content_type};base64,{image_base64}"
    return data_url, reference_description


@tool
def text_to_image(user_prompt: str, reference_image_url: str = ""):
    """
    Generate an image from a text prompt, optionally using a reference image.
    Args:
        user_prompt (str): What to generate or how to transform the reference image.
        reference_image_url (str): Optional reference image URL for redraw or regeneration.
    Returns:
        str: Markdown image result.
    """
    return _text_to_image(user_prompt, reference_image_url)


def _text_to_image(user_prompt: str, reference_image_url: str = "") -> str:
    api_key, base_url, model_name = _resolve_minimax_image_config()
    endpoint = f"{base_url}/image_generation"
    reference_data_url = ""
    reference_description = ""
    if reference_image_url.strip():
        reference_data_url, reference_description = _build_reference_bundle(reference_image_url)

    final_prompt = user_prompt.strip()
    if reference_description:
        final_prompt = (
            f"{final_prompt}\n\n"
            "Reference image description:\n"
            f"{reference_description}\n\n"
            "Keep the important visible structure, subject, and layout from the reference image unless the user explicitly asks to change them. "
            "Apply the user's requested transformation directly. "
            "Do not explain what could be done; generate the transformed result."
        )

    payload = {
        "model": model_name,
        "prompt": final_prompt,
        "aspect_ratio": "1:1",
        "response_format": "base64",
        "prompt_optimizer": True,
    }

    if reference_data_url:
        payload["subject_reference"] = [
            {
                "type": "character",
                "image_file": reference_data_url,
            }
        ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    response = requests.post(endpoint, headers=headers, json=payload, timeout=300)
    response.raise_for_status()
    data = response.json() or {}

    image_items = ((data.get("data") or {}).get("image_base64")) or []
    if isinstance(image_items, str):
        image_items = [image_items]
    if not image_items:
        raise ValueError(f"MiniMax image generation returned empty data: {data}")

    image_bytes = base64.b64decode(image_items[0])
    file_name = "minimax_generated_from_prompt.png"
    if reference_image_url.strip():
        file_name = "minimax_regenerated_from_reference.png"

    image_url = _upload_generated_image(image_bytes, file_name)
    logger.info("MiniMax image generated and uploaded to storage")
    return f"图片已生成完成：![生成图片]({image_url})"
