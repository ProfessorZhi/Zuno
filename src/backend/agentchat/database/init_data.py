import json
import re
from collections import defaultdict

import httpx
from loguru import logger
from sqlalchemy import inspect, text
from sqlmodel import SQLModel

from agentchat.api.services.agent import AgentService
from agentchat.api.services.llm import LLMService
from agentchat.api.services.mcp_server import MCPService
from agentchat.api.services.tool import ToolService
from agentchat.database import AgentTable, SystemUser, ToolTable, engine, ensure_database
from agentchat.database.dao.agent import AgentDao
from agentchat.database.dao.dialog import DialogDao
from agentchat.database.dao.llm import LLMDao
from agentchat.database.models.user import AdminUser
from agentchat.services.mcp.manager import MCPManager
from agentchat.services.storage import storage_client
from agentchat.settings import app_settings
from agentchat.utils.convert import convert_mcp_config
from agentchat.utils.helpers import get_provider_from_model

HIDDEN_SYSTEM_TOOL_NAMES = {"tavily_search", "bocha_search", "text_to_image"}
HIDDEN_SYSTEM_AGENT_NAMES = {"联网搜索助手", "博查搜索助手", "文生图助手"}


async def init_database():
    try:
        ensure_database()
        SQLModel.metadata.create_all(engine)
        _ensure_knowledge_pipeline_schema()
        logger.success("PostgreSQL tables are ready")
    except Exception as err:
        logger.error(f"Create PostgreSQL Table Error: {err}")


def _ensure_knowledge_pipeline_schema():
    inspector = inspect(engine)
    if "knowledge_file" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("knowledge_file")}
    required_columns = {
        "parse_status": "ALTER TABLE knowledge_file ADD COLUMN parse_status VARCHAR DEFAULT 'pending'",
        "rag_index_status": "ALTER TABLE knowledge_file ADD COLUMN rag_index_status VARCHAR DEFAULT 'pending'",
        "graph_index_status": "ALTER TABLE knowledge_file ADD COLUMN graph_index_status VARCHAR DEFAULT 'pending'",
        "last_task_id": "ALTER TABLE knowledge_file ADD COLUMN last_task_id VARCHAR",
        "last_error": "ALTER TABLE knowledge_file ADD COLUMN last_error VARCHAR(2048)",
    }

    with engine.begin() as connection:
        for column_name, ddl in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(ddl))

    if "knowledge" in inspector.get_table_names():
        knowledge_columns = {column["name"] for column in inspector.get_columns("knowledge")}
        if "default_retrieval_mode" not in knowledge_columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE knowledge ADD COLUMN default_retrieval_mode VARCHAR DEFAULT 'rag'")
                )
        if "knowledge_config" not in knowledge_columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE knowledge ADD COLUMN knowledge_config JSON DEFAULT '{}'::json")
                )

    if "llm" in inspector.get_table_names():
        llm_columns = {column["name"] for column in inspector.get_columns("llm")}
        if "model_slot" not in llm_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE llm ADD COLUMN model_slot VARCHAR"))


async def init_default_agent():
    try:
        logger.info("Reconciling default tools in PostgreSQL")
        await cleanup_duplicate_system_data()
        await insert_tools_to_mysql()
        await insert_llm_to_mysql()
        logger.info("Skip default agent seeding; users create agents explicitly")
        logger.success("Default tools are ready")
    except Exception as err:
        logger.error(f"Failed to initialize default tools: {err}")


async def update_system_mcp_server():
    try:
        if not app_settings.multi_models.conversation_model.is_configured():
            logger.warning("Skip system MCP initialization because no conversation model is configured")
            return
        mcp_server = await MCPService.get_all_servers(SystemUser)
        if len(mcp_server):
            await update_mcp_server_into_mysql(True)
        else:
            await update_mcp_server_into_mysql(False)
    except Exception as err:
        logger.error(f"Failed to initialize system MCP server: {err}")


def _sort_records(records: list[dict], id_key: str):
    return sorted(
        records,
        key=lambda item: (
            item.get("create_time") or "",
            item.get(id_key) or "",
        ),
    )


async def cleanup_duplicate_system_data():
    await cleanup_hidden_system_data()
    await cleanup_legacy_seeded_system_agents()
    tool_id_map = await cleanup_duplicate_system_tools()
    await cleanup_duplicate_system_agents(tool_id_map)


async def cleanup_hidden_system_data():
    hidden_tool_ids = set()
    for tool_name in HIDDEN_SYSTEM_TOOL_NAMES:
        hidden_tools = await ToolService.get_tool_by_name_and_user_id(tool_name, SystemUser)
        for tool in hidden_tools:
            hidden_tool_ids.add(tool["tool_id"])

    if hidden_tool_ids:
        all_agents = await AgentService.get_agent()
        for agent in all_agents:
            original_tool_ids = agent.get("tool_ids") or []
            updated_tool_ids = [tool_id for tool_id in original_tool_ids if tool_id not in hidden_tool_ids]
            if updated_tool_ids != original_tool_ids:
                await AgentDao.update_agent_by_id(agent["id"], {"tool_ids": updated_tool_ids})

        for tool_id in hidden_tool_ids:
            await ToolService.delete_tool_by_id(tool_id)

    for agent_name in HIDDEN_SYSTEM_AGENT_NAMES:
        hidden_agents = await AgentService.get_agents_by_name_and_user_id(agent_name, SystemUser)
        for agent in hidden_agents:
            await AgentDao.delete_agent_by_id(agent["id"])


async def cleanup_duplicate_system_tools():
    system_tools = await ToolService.get_tools_data()
    grouped_tools = defaultdict(list)
    for tool in system_tools:
        grouped_tools[tool["name"]].append(tool)

    tool_id_map = {}
    for records in grouped_tools.values():
        ordered_records = _sort_records(records, "tool_id")
        canonical = ordered_records[0]
        for duplicate in ordered_records[1:]:
            tool_id_map[duplicate["tool_id"]] = canonical["tool_id"]

    if not tool_id_map:
        return {}

    all_agents = await AgentService.get_agent()
    for agent in all_agents:
        original_tool_ids = agent.get("tool_ids") or []
        if not original_tool_ids:
            continue

        updated_tool_ids = []
        for tool_id in original_tool_ids:
            normalized_tool_id = tool_id_map.get(tool_id, tool_id)
            if normalized_tool_id not in updated_tool_ids:
                updated_tool_ids.append(normalized_tool_id)

        if updated_tool_ids != original_tool_ids:
            await AgentDao.update_agent_by_id(agent["id"], {"tool_ids": updated_tool_ids})

    for duplicate_tool_id in tool_id_map:
        await ToolService.delete_tool_by_id(duplicate_tool_id)

    logger.warning(f"Removed {len(tool_id_map)} duplicate system tools")
    return tool_id_map


async def cleanup_duplicate_system_agents(tool_id_map: dict[str, str] | None = None):
    system_agents = await AgentService.get_personal_agent_by_user_id(SystemUser)
    grouped_agents = defaultdict(list)
    for agent in system_agents:
        grouped_agents[agent["name"]].append(agent)

    duplicate_count = 0
    for records in grouped_agents.values():
        ordered_records = _sort_records(records, "id")
        canonical = ordered_records[0]

        canonical_tool_ids = canonical.get("tool_ids") or []
        if tool_id_map:
            normalized_tool_ids = []
            for tool_id in canonical_tool_ids:
                normalized_tool_id = tool_id_map.get(tool_id, tool_id)
                if normalized_tool_id not in normalized_tool_ids:
                    normalized_tool_ids.append(normalized_tool_id)
            if normalized_tool_ids != canonical_tool_ids:
                await AgentDao.update_agent_by_id(canonical["id"], {"tool_ids": normalized_tool_ids})

        for duplicate in ordered_records[1:]:
            await DialogDao.reassign_agent_id(duplicate["id"], canonical["id"])
            await AgentDao.delete_agent_by_id(duplicate["id"])
            duplicate_count += 1

    if duplicate_count:
        logger.warning(f"Removed {duplicate_count} duplicate system agents")


async def cleanup_legacy_seeded_system_agents():
    system_agents = await AgentService.get_personal_agent_by_user_id(SystemUser)
    deleted_count = 0
    for agent in system_agents:
        if agent.get("is_custom") is False:
            await AgentDao.delete_agent_by_id(agent["id"])
            deleted_count += 1

    if deleted_count:
        logger.warning(f"Removed {deleted_count} legacy seeded system agents")
    return deleted_count


async def insert_agent_to_mysql():
    model_name = app_settings.multi_models.conversation_model.model_name
    llm_id = await LLMService.get_llm_id_from_name(model_name, SystemUser)
    if not llm_id:
        logger.warning("Skip default agent creation because system LLM is missing")
        return

    tools = await ToolService.get_tools_data()
    existing_agents = {
        agent["name"]
        for agent in await AgentService.get_personal_agent_by_user_id(SystemUser)
    }

    for tool in tools:
        agent_name = tool["display_name"] + "助手"
        if agent_name in existing_agents:
            continue

        tool["name"] = agent_name
        await AgentDao.create_agent(
            AgentTable(
                **ToolTable(**tool).model_dump(exclude={"user_id", "tool_id"}),
                tool_ids=[tool["tool_id"]],
                user_id=SystemUser,
                is_custom=False,
                llm_id=llm_id,
            )
        )
        existing_agents.add(agent_name)


async def insert_llm_to_mysql():
    model_specs = [
        ("LLM", "conversation_model", app_settings.multi_models.conversation_model),
        ("Embedding", "embedding", app_settings.multi_models.embedding),
        ("Embedding", "vl_embedding", app_settings.multi_models.vl_embedding),
        ("Rerank", "rerank", app_settings.multi_models.rerank),
    ]

    existing_system_llms = await LLMDao.get_llm_by_user(SystemUser)
    existing_by_key = {
        (LLMService.normalize_llm_type(llm.llm_type), llm.model): llm
        for llm in existing_system_llms
    }

    has_default_llm = False
    for llm_type, model_slot, config in model_specs:
        if not config.is_configured():
            continue

        provider = _resolve_provider_from_config(config.model_name, config.base_url)
        payload = {
            "model": config.model_name,
            "llm_type": llm_type,
            "api_key": config.api_key,
            "base_url": config.base_url,
            "provider": provider,
            "model_slot": model_slot,
        }

        existing_llm = existing_by_key.get((llm_type, config.model_name))
        if existing_llm:
            await LLMService.update_llm(llm_id=existing_llm.llm_id, **payload)
        else:
            await LLMService.create_llm(
                user_id=SystemUser,
                **payload,
            )
            existing_by_key[(llm_type, config.model_name)] = True

        if llm_type == "LLM":
            has_default_llm = True

    if not has_default_llm:
        logger.warning("No default conversation model configured, skipping default LLM initialization")
    return has_default_llm


def _resolve_provider_from_config(model_name: str, base_url: str) -> str:
    provider = get_provider_from_model(model_name)
    if provider != "未知服务商":
        return provider

    base_url_lower = (base_url or "").lower()
    if "dashscope.aliyuncs.com" in base_url_lower:
        return "通义千问"
    if "minimax" in base_url_lower:
        return "MiniMax"
    if "deepseek.com" in base_url_lower:
        return "深度求索"
    if "openai.com" in base_url_lower:
        return "OpenAI"
    return provider


async def insert_tools_to_mysql():
    tools = await load_default_tool()
    existing_tools = {
        tool["name"]
        for tool in await ToolService.get_tools_data()
    }

    for tool in tools:
        if tool["name"] in HIDDEN_SYSTEM_TOOL_NAMES:
            continue

        if tool["name"] in existing_tools:
            continue

        await ToolService.create_default_tool(
            ToolTable(
                **tool,
                user_id=SystemUser,
                is_user_defined=False,
            )
        )
        existing_tools.add(tool["name"])


async def update_mcp_server_into_mysql(has_mcp_server: bool):
    servers = await load_system_mcp_server()
    existing_system_servers = {
        server["server_name"]: server
        for server in await MCPService.get_all_servers(SystemUser)
        if server["user_id"] == SystemUser
    }

    if has_mcp_server and not await MCPService.mcp_server_need_update():
        logger.info("Reconciling system MCP definitions with config file")

    servers_info = [_build_runtime_server_info(server) for server in servers]
    mcp_manager = MCPManager([config for config in convert_mcp_config(servers_info) if config])
    servers_params = await mcp_manager.show_mcp_tools()

    async def get_tools_name_from_params(tools_params: dict):
        tools_name = []
        for tool in tools_params:
            tools_name.append(tool["name"])
        return tools_name

    for key, params in servers_params.items():
        server = next((item for item in servers if item["server_name"] == key), None)
        if not server:
            continue
        tools_name = await get_tools_name_from_params(params)
        imported_config = _build_imported_config(server)
        runtime_info = _build_runtime_server_info(server)

        if key in existing_system_servers:
            existing_server = existing_system_servers[key]
            mcp_as_tool_name = existing_server.get("mcp_as_tool_name") or _fallback_mcp_tool_name(key)
            description = existing_server.get("description") or _fallback_mcp_description(key, tools_name)
            update_values = {
                "server_name": key,
                "url": runtime_info.get("url", ""),
                "type": runtime_info["type"],
                "config": server["config"],
                "config_enabled": server["config_enabled"],
                "logo_url": server["logo_url"],
                "imported_config": imported_config,
                "tools": tools_name,
                "params": params,
                "mcp_as_tool_name": mcp_as_tool_name,
                "description": description,
            }
            await MCPService.update_mcp_server(
                server_id=existing_server["mcp_server_id"],
                update_data=update_values,
            )
        else:
            mcp_as_tool_name = _fallback_mcp_tool_name(key)
            description = _fallback_mcp_description(key, tools_name)
            await MCPService.create_mcp_server(
                server_name=key,
                user_id=SystemUser,
                user_name="Admin",
                url=runtime_info.get("url", ""),
                type=runtime_info["type"],
                config=server["config"],
                tools=tools_name,
                params=params,
                config_enabled=server["config_enabled"],
                logo_url=server["logo_url"],
                mcp_as_tool_name=mcp_as_tool_name,
                description=description,
                imported_config=imported_config,
            )


async def upload_user_avatars_storage():
    if not storage_client.list_files_in_folder("icons/user"):
        user_avatars = await load_user_avatars()
        for avatar_url in user_avatars["avatars"]:
            async with httpx.AsyncClient() as client:
                response = await client.get(avatar_url)
                image_data = response.content

            file_name = avatar_url.split("/")[-1]
            object_name = f"icons/user/{file_name}"
            storage_client.upload_file(object_name, image_data)


async def load_default_tool():
    with open("./agentchat/config/tool.json", "r", encoding="utf-8") as f:
        result = json.load(f)
    return result


async def load_system_mcp_server():
    with open("./agentchat/config/mcp_server.json", "r", encoding="utf-8") as f:
        result = json.load(f)
    return result


def _build_imported_config(server: dict) -> dict:
    imported_config = server.get("imported_config")
    if imported_config:
        return imported_config

    server_name = server["server_name"]
    info: dict[str, object] = {"type": server["type"]}
    for key in ("url", "headers", "command", "args", "env", "env_passthrough", "cwd"):
        value = server.get(key)
        if value not in (None, "", [], {}):
            info[key] = value
    return {"mcpServers": {server_name: info}}


def _build_runtime_server_info(server: dict) -> dict:
    imported_config = _build_imported_config(server)
    _, info = next(iter(imported_config["mcpServers"].items()))
    return {
        "server_name": server["server_name"],
        "type": info.get("type", server.get("type", "sse")),
        "url": info.get("url", server.get("url", "")),
        "headers": info.get("headers"),
        "command": info.get("command"),
        "args": info.get("args"),
        "env": info.get("env"),
        "env_passthrough": info.get("env_passthrough"),
        "cwd": info.get("cwd"),
    }


def _fallback_mcp_tool_name(server_name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "_", server_name.lower()).strip("_")
    return base or "mcp_server"


def _fallback_mcp_description(server_name: str, tools_name: list[str]) -> str:
    if tools_name:
        preview = "、".join(tools_name[:3])
        return f"{server_name} MCP 服务，当前提供 {len(tools_name)} 个工具，例如：{preview}。"
    return f"{server_name} MCP 服务。"


async def load_user_avatars():
    with open("./agentchat/config/avatars.json", "r", encoding="utf-8") as f:
        result = json.load(f)
    return result
