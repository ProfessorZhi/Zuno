import hashlib
import os
from typing import Any, Iterable

from agentchat.settings import app_settings
from agentchat.utils.contexts import get_trace_id_context


class RedisKeys:
    @staticmethod
    def auth_session(user_id: str) -> str:
        return f"auth:user:{user_id}:session"

    @staticmethod
    def captcha(captcha_key: str) -> str:
        return f"captcha:{captcha_key}"

    @staticmethod
    def rsa_private_key() -> str:
        return "security:rsa:private_key"

    @staticmethod
    def stream_latest(session_id: str) -> str:
        return f"stream:{session_id}:latest"

    @staticmethod
    def task_progress(task_id: str) -> str:
        return f"task_progress:{task_id}"

    @staticmethod
    def wechat_reply(user_id: str, content: str) -> str:
        content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
        return f"wechat:{user_id}:reply:{content_hash}"


def get_active_trace_id(default: str = "") -> str:
    try:
        return get_trace_id_context()
    except ValueError:
        return default


def configure_langsmith() -> bool:
    config = getattr(app_settings, "langsmith", {}) or {}
    if not config.get("enabled"):
        return False

    env_mapping = {
        "LANGCHAIN_API_KEY": config.get("api_key", ""),
        "LANGCHAIN_ENDPOINT": config.get("endpoint", ""),
        "LANGCHAIN_PROJECT": config.get("project", ""),
    }
    for env_name, env_value in env_mapping.items():
        if env_value and not os.getenv(env_name):
            os.environ[env_name] = str(env_value)

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    return True


def build_langsmith_metadata(**kwargs: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for key, value in kwargs.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, (list, tuple, set, dict)) and not value:
            continue
        metadata[key] = list(value) if isinstance(value, set) else value
    return metadata


def build_langchain_run_config(
    *,
    callbacks: list[Any] | None = None,
    run_name: str | None = None,
    tags: Iterable[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config: dict[str, Any] = {
        "callbacks": list(callbacks or []),
    }

    if run_name:
        config["run_name"] = run_name

    tag_list = [tag for tag in (tags or []) if tag]
    if tag_list:
        config["tags"] = tag_list

    filtered_metadata = build_langsmith_metadata(**(metadata or {}))
    if filtered_metadata:
        config["metadata"] = filtered_metadata

    return config
