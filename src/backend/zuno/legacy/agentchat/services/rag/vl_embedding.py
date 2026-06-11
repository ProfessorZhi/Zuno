import base64
import mimetypes
from urllib.parse import urlparse

import aiohttp

from agentchat.core.models.manager import ModelManager
from agentchat.services.storage import storage_client
from agentchat.settings import app_settings
from agentchat.utils.file_utils import get_object_key_from_public_url

VL_EMBEDDING_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding"
VL_EMBEDDING_DIMENSION = 1024


def _normalize_model_config(config_override):
    if not config_override:
        return None
    if hasattr(config_override, "model_name"):
        return config_override
    return type("VLEmbeddingConfig", (), config_override)()


def _get_vl_config(config_override=None):
    return _normalize_model_config(config_override) or ModelManager.get_model_config("vl_embedding", "VL Embedding 模型")


def _get_vl_endpoint(base_url: str) -> str:
    normalized = (base_url or "").strip().rstrip("/")
    if normalized and "multimodal-embedding" in normalized:
        return normalized
    return VL_EMBEDDING_ENDPOINT


def _is_local_or_private_image_url(image_url: str) -> bool:
    if not image_url or image_url.startswith("data:"):
        return False
    parsed = urlparse(image_url)
    host = (parsed.hostname or "").lower()
    if host in {"127.0.0.1", "localhost", "host.docker.internal", "minio"}:
        return True
    storage_base_url = (app_settings.storage.active.base_url or "").strip().rstrip("/")
    return bool(storage_base_url and image_url.startswith(storage_base_url))


def _image_bytes_to_data_uri(image_bytes: bytes, object_name: str) -> str:
    mime_type = mimetypes.guess_type(object_name)[0] or "image/png"
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


async def _http_url_to_data_uri(image_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            response.raise_for_status()
            image_bytes = await response.read()
            content_type = response.headers.get("Content-Type") or mimetypes.guess_type(image_url)[0] or "image/png"
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{content_type};base64,{encoded}"


async def _normalize_image_input(image_url: str) -> str:
    if not image_url or image_url.startswith("data:"):
        return image_url
    is_local_or_private = _is_local_or_private_image_url(image_url)
    if not is_local_or_private:
        return image_url

    bucket_name = getattr(app_settings.storage.active, "bucket_name", "") or ""
    object_name = get_object_key_from_public_url(image_url, bucket_name=bucket_name)
    image_bytes = storage_client.get_file_bytes(object_name)
    if image_bytes:
        return _image_bytes_to_data_uri(image_bytes, object_name)

    return await _http_url_to_data_uri(image_url)


async def _request_vl_embedding(contents: list[dict], config_override=None) -> list[list[float]]:
    config = _get_vl_config(config_override)
    payload = {
        "model": config.model_name,
        "input": {
            "contents": contents,
        },
        "parameters": {
            "dimension": VL_EMBEDDING_DIMENSION,
        },
    }
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            _get_vl_endpoint(config.base_url),
            headers=headers,
            json=payload,
        ) as response:
            if response.status != 200:
                response.raise_for_status()
            data = await response.json()

    embeddings = []
    for item in data.get("output", {}).get("embeddings", []):
        if item.get("embedding"):
            embeddings.append(item["embedding"])
    return embeddings


async def get_vl_text_embedding(texts: list[str], config_override=None) -> list[list[float]]:
    contents = [{"text": text} for text in texts if str(text or "").strip()]
    if not contents:
        return []
    return await _request_vl_embedding(contents, config_override)


async def get_vl_image_embedding(image_urls: list[str], config_override=None) -> list[list[float]]:
    contents = []
    for image_url in image_urls:
        normalized = str(image_url or "").strip()
        if not normalized:
            continue
        contents.append({"image": await _normalize_image_input(normalized)})
    if not contents:
        return []
    return await _request_vl_embedding(contents, config_override)
