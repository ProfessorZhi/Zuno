from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any

from agentchat.database.dao.mcp_user_config import MCPUserConfigDao


class MCPUserConfigService:
    META_PREFIX = "__zuno_"
    META_STATUS_KEY = "__zuno_test_status"
    META_MESSAGE_KEY = "__zuno_test_message"
    META_TIME_KEY = "__zuno_test_time"
    META_TOOLS_KEY = "__zuno_test_tools"

    @classmethod
    def _split_public_and_meta(cls, config: Optional[List[dict]] = None) -> Tuple[List[dict], Dict[str, Any]]:
        public_items: List[dict] = []
        meta: Dict[str, Any] = {}
        for item in config or []:
            key = item.get("key")
            if isinstance(key, str) and key.startswith(cls.META_PREFIX):
                meta[key] = item.get("value")
            else:
                public_items.append(item)
        return public_items, meta

    @classmethod
    def _build_meta_items(cls, meta: Dict[str, Any]) -> List[dict]:
        return [{"key": key, "value": value} for key, value in meta.items()]

    @classmethod
    def _untested_meta(cls) -> Dict[str, Any]:
        return {
            cls.META_STATUS_KEY: "untested",
            cls.META_MESSAGE_KEY: "配置已保存，尚未执行测试。",
            cls.META_TIME_KEY: datetime.now().isoformat(timespec="seconds"),
            cls.META_TOOLS_KEY: [],
        }

    @classmethod
    def _build_test_status(cls, meta: Dict[str, Any]) -> Dict[str, Any]:
        if not meta:
            return {
                "code": "untested",
                "label": "未测试",
                "detail": "还没有做过连接测试。",
                "tools": [],
                "tested_at": None,
            }

        status_code = meta.get(cls.META_STATUS_KEY) or "untested"
        status_map = {
            "success": "测试通过",
            "failed": "测试失败",
            "untested": "未测试",
        }
        return {
            "code": status_code,
            "label": status_map.get(status_code, "未测试"),
            "detail": meta.get(cls.META_MESSAGE_KEY) or "还没有做过连接测试。",
            "tools": meta.get(cls.META_TOOLS_KEY) or [],
            "tested_at": meta.get(cls.META_TIME_KEY),
        }

    @classmethod
    async def create_mcp_user_config(cls, mcp_server_id: str, user_id: str, config: Optional[List[dict]] = None):
        try:
            public_config, _ = cls._split_public_and_meta(config)
            merged_config = public_config + cls._build_meta_items(cls._untested_meta())
            return await MCPUserConfigDao.create_mcp_user_config(mcp_server_id, user_id, merged_config)
        except Exception as err:
            raise ValueError(f"Create MCP User Config Error: {err}")

    @classmethod
    async def get_mcp_user_config_from_id(cls, config_id: str):
        try:
            results = await MCPUserConfigDao.get_mcp_user_config_from_id(config_id)
            return results.to_dict()
        except Exception as err:
            raise ValueError(f"Get MCP User Config From ID Error: {err}")

    @classmethod
    async def update_mcp_user_config(cls, mcp_server_id: str, user_id: str, config: Optional[List[dict]] = None):
        try:
            record = await MCPUserConfigDao.get_mcp_user_configs(user_id, mcp_server_id)
            public_config, _ = cls._split_public_and_meta(config)
            merged_config = public_config + cls._build_meta_items(cls._untested_meta())
            if not record:
                await MCPUserConfigDao.create_mcp_user_config(mcp_server_id, user_id, merged_config)
            else:
                await MCPUserConfigDao.update_mcp_user_config(mcp_server_id, user_id, merged_config)
        except Exception as err:
            raise ValueError(f"Update MCP User Config Error: {err}")

    @classmethod
    async def update_test_status(
        cls,
        mcp_server_id: str,
        user_id: str,
        *,
        success: bool,
        message: str,
        tools: Optional[List[str]] = None,
    ):
        record = await MCPUserConfigDao.get_mcp_user_configs(user_id, mcp_server_id)
        public_config, meta = cls._split_public_and_meta(record.config if record else [])
        meta.update(
            {
                cls.META_STATUS_KEY: "success" if success else "failed",
                cls.META_MESSAGE_KEY: message,
                cls.META_TIME_KEY: datetime.now().isoformat(timespec="seconds"),
                cls.META_TOOLS_KEY: tools or [],
            }
        )
        merged_config = public_config + cls._build_meta_items(meta)
        if not record:
            await MCPUserConfigDao.create_mcp_user_config(mcp_server_id, user_id, merged_config)
        else:
            await MCPUserConfigDao.update_mcp_user_config(mcp_server_id, user_id, merged_config)

    @classmethod
    async def delete_mcp_user_config(cls, config_id: str):
        try:
            return await MCPUserConfigDao.delete_mcp_user_config(config_id)
        except Exception as err:
            raise ValueError(f"Delete MCP User Config Error: {err}")

    @classmethod
    async def get_mcp_user_config(cls, user_id: str, mcp_server_id: str):
        try:
            result = await MCPUserConfigDao.get_mcp_user_configs(user_id, mcp_server_id)
            mcp_config = {}
            if result:
                public_config, _ = cls._split_public_and_meta(result.config)
                for res in public_config:
                    mcp_config[res["key"]] = res["value"]
            return mcp_config
        except Exception as err:
            raise ValueError(f"Get MCP User Configs Error: {err}")

    @classmethod
    async def show_mcp_user_config(cls, user_id: str, mcp_server_id: str):
        try:
            result = await MCPUserConfigDao.get_mcp_user_configs(user_id, mcp_server_id)
            if result:
                result_dict = result.to_dict()
                public_config, meta = cls._split_public_and_meta(result_dict.get("config"))
                result_dict["config"] = public_config
                result_dict["test_status"] = cls._build_test_status(meta)
                return result_dict
            return {
                "config": [],
                "test_status": cls._build_test_status({}),
            }
        except Exception as err:
            raise ValueError(f"Get MCP User Configs Error: {err}")
