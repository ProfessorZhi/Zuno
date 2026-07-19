import asyncio
from typing import List, Union

from zuno.database import SystemUser, ToolTable
from zuno.database.dao.tool import ToolDao
from zuno.database.models.user import AdminUser
from zuno.api.services.security_admin_actions import require_admin_action_authorized
from zuno.schema.tool import (
    CLIToolPreviewReq,
    RemoteApiAssistReq,
    ToolConnectivityReq,
    ToolCreateReq,
    ToolUpdateReq,
)
from zuno.services.user_defined_tool_runtime import get_user_defined_runtime_type

HIDDEN_SYSTEM_TOOL_NAMES = {"tavily_search", "bocha_search", "text_to_image"}


class ToolService:
    @staticmethod
    def _serialize_tool(tool: ToolTable | dict):
        payload = tool.to_dict() if hasattr(tool, "to_dict") else dict(tool)
        if payload.get("is_user_defined"):
            auth_config = payload.get("auth_config") or {}
            payload["runtime_type"] = get_user_defined_runtime_type(
                ToolTable(**{**payload, "auth_config": auth_config})
            )
        return payload

    @classmethod
    def _serialize_tools(cls, tools: list[ToolTable | dict]):
        return [cls._serialize_tool(tool) for tool in tools]

    @staticmethod
    def _dedupe_tools(tools: list[dict]):
        deduped = []
        seen = set()
        for tool in tools:
            if tool.get("user_id") != SystemUser:
                deduped.append(tool)
                continue
            key = (tool.get("user_id"), tool.get("name"))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(tool)
        return deduped

    @staticmethod
    def _filter_hidden_system_tools(tools: list[dict]):
        return [
            tool for tool in tools
            if not (
                tool.get("user_id") == SystemUser
                and tool.get("name") in HIDDEN_SYSTEM_TOOL_NAMES
            )
        ]

    @classmethod
    async def create_default_tool(cls, default_tool: ToolTable):
        return await ToolDao.create_default_tool(default_tool)

    @classmethod
    async def create_user_defined_tool(cls, tool: ToolTable):
        return await ToolDao.create_user_defined_tool(tool)

    @classmethod
    async def delete_user_defined_tool(cls, tool_id: str):
        await ToolDao.delete_user_defined_tool(tool_id=tool_id)

    @classmethod
    async def verify_user_permission(cls, tool_id: str, user_id: str, action: str = "access"):
        authorized_user_id = await cls._get_user_by_tool_id(tool_id)
        if user_id == AdminUser:
            if authorized_user_id != AdminUser:
                require_admin_action_authorized(
                    principal_id=user_id,
                    action=f"admin.tool.{action}",
                    resource_ref=f"tool:{tool_id}",
                )
            return
        if user_id != authorized_user_id:
            raise ValueError("没有权限访问该资源")

    @classmethod
    async def get_personal_tool_by_user(cls, user_id: str):
        try:
            personal_results = await ToolDao.get_tool_by_user_id(user_id=user_id)
            return cls._filter_hidden_system_tools(
                cls._dedupe_tools(cls._serialize_tools(personal_results))
            )
        except Exception as err:
            raise ValueError(f"Get Tool By User Id Appear Error: {err}")

    @classmethod
    async def get_visible_tool_by_user(cls, user_id: str):
        try:
            personal_results = await ToolDao.get_tool_by_user_id(user_id=user_id)
            system_results = await ToolDao.get_tool_by_user_id(user_id=SystemUser)
            return cls._filter_hidden_system_tools(
                cls._dedupe_tools(cls._serialize_tools(personal_results + system_results))
            )
        except Exception as err:
            raise ValueError(f"Get All Tool By User Appear Error: {err}")

    @classmethod
    async def get_all_tools(cls, user_id: str) -> list[dict]:
        if user_id == SystemUser:
            tools = await ToolDao.get_all_tools(SystemUser)
            return cls._filter_hidden_system_tools(
                cls._dedupe_tools(cls._serialize_tools(tools))
            )
        tools, default_tools = await asyncio.gather(
            ToolDao.get_all_tools(user_id),
            ToolDao.get_all_tools(SystemUser),
        )
        return cls._filter_hidden_system_tools(
            cls._dedupe_tools(cls._serialize_tools([*tools, *default_tools]))
        )

    @classmethod
    async def get_tool_name_by_id(cls, tool_id: Union[List[str], str]):
        try:
            tool_ids = [tool_id] if isinstance(tool_id, str) else tool_id
            tools = await ToolDao.get_tool_name_by_id(tool_id=tool_ids)
            return [tool.name for tool in tools]
        except Exception as err:
            raise ValueError(f"Get Tool name by Id appear Err: {err}")

    @classmethod
    async def get_tools_from_id(cls, tool_ids: Union[List[str], str]) -> List[ToolTable]:
        tool_ids = [tool_ids] if isinstance(tool_ids, str) else tool_ids
        return await ToolDao.get_tool_name_by_id(tool_id=tool_ids)

    @classmethod
    async def _get_user_by_tool_id(cls, tool_id: str):
        try:
            tool = await ToolDao.get_tool_by_id(tool_id=tool_id)
            return tool.user_id
        except Exception as err:
            raise ValueError(f"Get user by tool Id appear Error: {err}")

    @classmethod
    async def get_tools_data(cls):
        try:
            tools = await ToolDao.get_all_tools(SystemUser)
            return cls._filter_hidden_system_tools(
                cls._dedupe_tools(cls._serialize_tools(tools))
            )
        except Exception as err:
            raise ValueError(f"Get tools data appear Error: {err}")

    @classmethod
    async def get_id_by_tool_name(cls, tool_name: str, user_id: str):
        try:
            tool = await ToolDao.get_id_by_tool_name(tool_name, user_id)
            return tool.tool_id
        except Exception as err:
            raise ValueError(f"Get Id by tool name appear Error: {err}")

    @classmethod
    async def get_tool_ids_from_name(cls, tool_names: List[str], user_id):
        try:
            tools = await ToolDao.get_tool_ids_from_name(tool_names, user_id)
            tools.extend(await ToolDao.get_tool_ids_from_name(tool_names, SystemUser))
            return [tool.tool_id for tool in tools]
        except Exception as err:
            raise ValueError(f"Get Tool ID tool name appear Error: {err}")

    @classmethod
    async def get_user_defined_tools(cls, user_id):
        tools = await ToolDao.get_user_defined_tools(user_id)
        return cls._serialize_tools(tools)

    @classmethod
    async def update_user_defined_tool(cls, tool_id, update_values):
        await ToolDao.update_user_defined_tool(tool_id, update_values)

    @classmethod
    async def get_tool_by_name_and_user_id(cls, name: str, user_id: str):
        tools = await ToolDao.get_tool_by_name_and_user_id(name, user_id)
        return [tool.to_dict() for tool in tools]

    @classmethod
    async def get_tool_by_id(cls, tool_id: str):
        return await ToolDao.get_tool_by_id(tool_id)

    @classmethod
    async def delete_tool_by_id(cls, tool_id: str):
        await ToolDao.delete_tool_by_id(tool_id)


class ToolRuntimeService:
    @staticmethod
    async def create_user_defined_tool(req: ToolCreateReq, *, user_id: str) -> dict:
        from zuno.services.tool_creation_service import ToolCreationService

        return await ToolCreationService.create_user_defined_tool(
            display_name=req.display_name,
            description=req.description,
            logo_url=req.logo_url,
            runtime_type=req.runtime_type or "remote_api",
            user_id=user_id,
            auth_config=req.auth_config,
            cli_config=req.cli_config,
            openapi_schema=req.openapi_schema,
            simple_api_config=req.simple_api_config,
            source_metadata=req.source_metadata,
        )

    @staticmethod
    def preview_cli_tool_directory(req: CLIToolPreviewReq):
        from zuno.services.cli_tool_discovery import CliToolDiscoveryService

        return CliToolDiscoveryService.preview(req)

    @staticmethod
    async def assist_remote_api_tool(req: RemoteApiAssistReq):
        from zuno.services.simple_api_tool import (
            build_openapi_schema_from_simple_config,
            build_remote_api_assist_draft_agentic,
        )

        _ = build_openapi_schema_from_simple_config
        return await build_remote_api_assist_draft_agentic(req)

    @staticmethod
    async def test_tool_connectivity(req: ToolConnectivityReq):
        from zuno.services.tool_connectivity_service import ToolConnectivityService

        return await ToolConnectivityService.test(req)

    @staticmethod
    async def test_system_tool_connectivity(tool_name: str):
        from zuno.services.tool_connectivity_service import ToolConnectivityService

        return await ToolConnectivityService.test_system_tool(tool_name)

    @staticmethod
    async def test_saved_tool_connectivity(tool: ToolTable | dict):
        from zuno.services.tool_connectivity_service import ToolConnectivityService

        return await ToolConnectivityService.test_saved_tool(tool)

    @staticmethod
    def build_runtime_update_values(req: ToolUpdateReq) -> dict:
        from zuno.services.tool_creation_service import ToolCreationService
        from zuno.services.user_defined_tool_runtime import build_stored_tool_auth_config

        _ = build_stored_tool_auth_config
        runtime_type, resolved_schema, stored_auth = ToolCreationService.validate_and_resolve(
            runtime_type=req.runtime_type,
            auth_config=req.auth_config,
            cli_config=req.cli_config,
            openapi_schema=req.openapi_schema,
            simple_api_config=req.simple_api_config,
            source_metadata=req.source_metadata,
        )
        return {
            "display_name": req.display_name,
            "description": req.description,
            "logo_url": req.logo_url,
            "openapi_schema": resolved_schema if runtime_type == "remote_api" else None,
            "auth_config": stored_auth,
        }

    @staticmethod
    def build_update_payload(req: ToolUpdateReq) -> dict:
        return ToolRuntimeService.build_runtime_update_values(req)

    @staticmethod
    def to_runtime_status(result):
        from zuno.services.tool_connectivity_service import ToolConnectivityService

        return ToolConnectivityService.to_runtime_status(result)


__all__ = ["HIDDEN_SYSTEM_TOOL_NAMES", "ToolRuntimeService", "ToolService"]
