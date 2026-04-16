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

async def initialize_app_settings(file_path: str = None):
    global app_settings

    file_path = file_path or "agentchat/config.yaml"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
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
