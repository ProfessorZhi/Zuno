import base64
import time
from pathlib import Path

import requests
from langchain.tools import tool

from agentchat.settings import app_settings

DEFAULT_MINIMAX_API_HOST = "https://api.minimaxi.com"


def _normalize_minimax_api_host(base_url: str) -> str:
    normalized = (base_url or "").strip().rstrip("/")
    if not normalized:
        return DEFAULT_MINIMAX_API_HOST

    if normalized.endswith("/v1"):
        normalized = normalized[:-3].rstrip("/")

    return normalized or DEFAULT_MINIMAX_API_HOST


def _resolve_minimax_vision_config() -> tuple[str, str]:
    vision_config = app_settings.multi_models.qwen_vl
    conversation_config = app_settings.multi_models.conversation_model

    api_key = (vision_config.api_key or conversation_config.api_key or "").strip()
    base_url = (vision_config.base_url or conversation_config.base_url or "").strip()

    if not api_key:
        raise ValueError("MiniMax vision is not configured with a usable API key.")

    return api_key, _normalize_minimax_api_host(base_url)


def _build_data_url(image_path: str) -> str:
    image_bytes = Path(image_path).read_bytes()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    suffix = Path(image_path).suffix.lower()
    media_type = "image/jpeg"
    if suffix == ".png":
        media_type = "image/png"
    elif suffix == ".webp":
        media_type = "image/webp"

    return f"data:{media_type};base64,{image_base64}"


@tool
def image_to_text(image_path: str):
    """
    Understand an image and return a dense, grounded description.
    Args:
        image_path (str): Local path to the image.
    Returns:
        str: Dense image understanding result.
    """
    return _image_to_text(image_path)


def _image_to_text(image_path: str) -> str:
    api_key, api_host = _resolve_minimax_vision_config()
    endpoint = f"{api_host}/v1/coding_plan/vlm"
    payload = {
        "prompt": (
            "Understand the image and report only what is truly visible. "
            "Use Chinese in the final answer. "
            "Keep the result information-dense, concrete, and grounded. "
            "Output in this structure: "
            "1. 一句话总结; "
            "2. 图片类型; "
            "3. 主要主体; "
            "4. 可见文字; "
            "5. 关键区域/按钮/元素; "
            "6. 配色与布局; "
            "7. 可复用的视觉特征（方便后续重生成）. "
            "If something is unclear, say it is unclear. "
            "Do not invent git diff, source websites, file names, or hidden context."
        ),
        "image_url": _build_data_url(image_path),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "MM-API-Source": "Minimax-MCP",
        "Content-Type": "application/json",
    }

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            data = response.json() or {}
            message = str(data.get("content", "")).strip()
            if message:
                return message
            raise ValueError(f"MiniMax vision returned empty content: {data}")
        except Exception as err:
            last_error = err
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise

    raise ValueError(str(last_error) if last_error else "MiniMax vision failed unexpectedly.")
