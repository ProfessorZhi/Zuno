import os
from pathlib import Path
from typing import Optional

import yaml
from loguru import logger
from pydantic.v1 import BaseSettings, Field

from zuno.schema.common import MultiModels, ModelConfig, Rag, StorageConfig, Tools


class Settings(BaseSettings):
    database: dict = {}
    redis: dict = {}
    rabbitmq: dict = {}
    neo4j: dict = {}
    mysql: dict = {}
    server: dict = {}
    langsmith: dict = {}
    langfuse: dict = {}
    whitelist_paths: list = []
    wechat_config: dict = {}
    default_config: dict = {}

    rag: Rag = Field(default_factory=Rag)
    tools: Tools = Field(default_factory=Tools)
    storage: Optional[StorageConfig] = None
    multi_models: MultiModels = Field(default_factory=MultiModels)


app_settings = Settings()


def resolve_app_config_path(file_path: str | None = None, *, writable: bool = False) -> Path:
    if file_path:
        return Path(file_path)

    env_path = os.getenv("ZUNO_CONFIG") or os.getenv("AGENTCHAT_CONFIG")
    if env_path:
        return Path(env_path)

    package_root = Path(__file__).resolve().parent
    repo_root = package_root.parents[2]
    candidates = [
        repo_root / ".local" / "config" / "agentchat" / "config.local.yaml",
        repo_root / ".local" / "config" / "agentchat" / "config.yaml",
        package_root / "config.local.yaml",
        package_root / "config.yaml",
        package_root / "config.example.yaml",
        Path("zuno/config.local.yaml"),
        Path("zuno/config.yaml"),
        Path("zuno/config.example.yaml"),
        Path("agentchat/config.local.yaml"),
        Path("agentchat/config.yaml"),
        Path("agentchat/config.example.yaml"),
        Path("/app/zuno/config.local.yaml"),
        Path("/app/zuno/config.yaml"),
        Path("/app/zuno/config.example.yaml"),
        Path("/app/agentchat/config.local.yaml"),
        Path("/app/agentchat/config.yaml"),
        Path("/app/agentchat/config.example.yaml"),
    ]
    if writable:
        writable_candidates = [
            repo_root / ".local" / "config" / "agentchat" / "config.local.yaml",
            package_root / "config.local.yaml",
            Path("zuno/config.local.yaml"),
            Path("/app/zuno/config.local.yaml"),
            Path("agentchat/config.local.yaml"),
            Path("/app/agentchat/config.local.yaml"),
        ]
        for candidate in writable_candidates:
            if candidate.exists():
                return candidate
        return writable_candidates[0]

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return package_root / "config.example.yaml"


async def initialize_app_settings(file_path: str = None):
    global app_settings

    config_path = resolve_app_config_path(file_path)
    try:
        with config_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            if data is None:
                logger.error("YAML 文件解析为空")
                return

            if "multi_models" in data:
                data["multi_models"] = MultiModels(**data["multi_models"])

            if "tools" in data:
                data["tools"] = Tools(**data["tools"])

            if "rag" in data:
                data["rag"] = Rag(**data["rag"])

            if "storage" in data:
                data["storage"] = StorageConfig(**data["storage"])

            if "database" not in data and "mysql" in data:
                mysql_config = data.get("mysql") or {}
                data["database"] = {
                    "sync_endpoint": mysql_config.get("endpoint", ""),
                    "async_endpoint": mysql_config.get("async_endpoint", ""),
                    "echo": False,
                    "pool_size": 10,
                    "max_overflow": 20,
                }

            for key, value in data.items():
                setattr(app_settings, key, value)
    except Exception as exc:
        logger.error(f"Yaml file loading error: {exc}")


__all__ = [
    "ModelConfig",
    "Settings",
    "app_settings",
    "initialize_app_settings",
    "resolve_app_config_path",
]
