import os
from pathlib import Path

import yaml
from typing import Literal, Optional
from loguru import logger
from types import SimpleNamespace
from pydantic.v1 import BaseSettings, Field

from agentchat.schema.common import MultiModels, ModelConfig, Tools, Rag, StorageConfig


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

    env_path = os.getenv("AGENTCHAT_CONFIG") or os.getenv("ZUNO_CONFIG")
    if env_path:
        return Path(env_path)

    package_root = Path(__file__).resolve().parent
    candidates = [
        package_root / "config.local.yaml",
        package_root / "config.yaml",
        package_root / "config.example.yaml",
        Path("agentchat/config.local.yaml"),
        Path("agentchat/config.yaml"),
        Path("agentchat/config.example.yaml"),
        Path("/app/agentchat/config.local.yaml"),
        Path("/app/agentchat/config.yaml"),
        Path("/app/agentchat/config.example.yaml"),
    ]
    if writable:
        writable_candidates = [
            package_root / "config.local.yaml",
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
        with config_path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data is None:
                logger.error("YAML 文件解析为空")
                return

            # 特殊处理multi_models配置
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
    except Exception as e:
        logger.error(f"Yaml file loading error: {e}")
