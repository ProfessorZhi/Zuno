import re
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, create_model
from langchain_core.tools import BaseTool, StructuredTool

from agentchat.database import ToolTable
from agentchat.tools.cli_tool.adapter import CLIToolAdapter
from agentchat.tools.openapi_tool.adapter import OpenAPIToolAdapter


def get_user_defined_runtime_type(db_tool: ToolTable) -> str:
    auth_config = db_tool.auth_config or {}
    runtime_type = (auth_config.get("mode") or "remote_api").strip()
    return runtime_type if runtime_type in {"remote_api", "cli"} else "remote_api"


def normalize_remote_api_auth_config(auth_config: Optional[dict]) -> dict:
    if not auth_config:
        return {}

    if auth_config.get("auth_type"):
        return auth_config

    auth_type = (auth_config.get("type") or "").strip().lower()
    token = auth_config.get("token")
    if auth_type == "bearer" and token:
        return {"auth_type": "Bearer", "data": token}
    if auth_type == "basic" and token:
        return {"auth_type": "Basic", "data": token}
    return auth_config


def get_cli_config_from_auth_config(auth_config: Optional[dict]) -> dict:
    auth_config = auth_config or {}
    return auth_config.get("cli_config") or {}


def build_stored_tool_auth_config(
    runtime_type: str,
    auth_config: Optional[dict],
    cli_config: Optional[dict],
) -> dict:
    if runtime_type == "cli":
        return {
            "mode": "cli",
            "cli_config": cli_config or {},
        }

    normalized = normalize_remote_api_auth_config(auth_config)
    if not normalized:
        return {"mode": "remote_api"}
    return {
        "mode": "remote_api",
        **normalized,
    }


def build_user_defined_langchain_tools(
    db_tool: ToolTable,
    tool_metadata_map: Optional[Dict[str, Dict[str, str]]] = None,
) -> List[BaseTool]:
    runtime_type = get_user_defined_runtime_type(db_tool)
    if runtime_type == "cli":
        cli_adapter = CLIToolAdapter(
            tool_id=db_tool.tool_id,
            display_name=db_tool.display_name,
            description=db_tool.description,
            cli_config=get_cli_config_from_auth_config(db_tool.auth_config),
        )
        cli_schema = cli_adapter.tool_schema["function"]
        cli_tool = StructuredTool(
            name=cli_schema["name"],
            description=cli_schema["description"],
            coroutine=cli_adapter.execute,
            args_schema=_build_args_model(cli_schema["name"], cli_schema["parameters"]),
        )
        if tool_metadata_map is not None:
            tool_metadata_map[cli_tool.name] = {
                "name": db_tool.display_name,
                "type": "工具",
            }
        return [cli_tool]

    tool_adapter = OpenAPIToolAdapter(
        auth_config=normalize_remote_api_auth_config(db_tool.auth_config),
        openapi_schema=db_tool.openapi_schema,
    )

    tools: List[BaseTool] = []
    for openapi_tool in tool_adapter.tools:
        function_schema = openapi_tool["function"]
        tool_name = function_schema.get("name", "")
        tools.append(
            StructuredTool(
                name=tool_name,
                description=function_schema.get("description", ""),
                coroutine=_create_openapi_executor(tool_adapter, tool_name),
                args_schema=_build_args_model(tool_name, function_schema.get("parameters", {})),
            )
        )
        if tool_metadata_map is not None:
            tool_metadata_map[tool_name] = {
                "name": db_tool.display_name,
                "type": "工具",
            }
    return tools


def build_user_defined_openai_tools(
    db_tool: ToolTable,
) -> Tuple[List[dict], Dict[str, Callable[..., Awaitable[Any]]]]:
    runtime_type = get_user_defined_runtime_type(db_tool)
    if runtime_type == "cli":
        cli_adapter = CLIToolAdapter(
            tool_id=db_tool.tool_id,
            display_name=db_tool.display_name,
            description=db_tool.description,
            cli_config=get_cli_config_from_auth_config(db_tool.auth_config),
        )
        return [cli_adapter.tool_schema], {cli_adapter.tool_name: cli_adapter.execute}

    tool_adapter = OpenAPIToolAdapter(
        auth_config=normalize_remote_api_auth_config(db_tool.auth_config),
        openapi_schema=db_tool.openapi_schema,
    )
    executors = {
        tool_schema["function"]["name"]: _create_openapi_executor(
            tool_adapter,
            tool_schema["function"]["name"],
        )
        for tool_schema in tool_adapter.tools
    }
    return tool_adapter.tools, executors


def _create_openapi_executor(
    tool_adapter: OpenAPIToolAdapter,
    tool_name: str,
) -> Callable[..., Awaitable[Any]]:
    async def _execute_wrapper(**kwargs):
        return await tool_adapter.execute(_tool_name=tool_name, **kwargs)

    return _execute_wrapper


def _build_args_model(tool_name: str, parameters_schema: dict) -> type[BaseModel]:
    properties = parameters_schema.get("properties") or {}
    required = set(parameters_schema.get("required") or [])
    fields = {}
    for field_name, schema in properties.items():
        fields[field_name] = _build_field_definition(schema, field_name in required)

    model_name = _sanitize_model_name(tool_name)
    return create_model(model_name, **fields)


def _build_field_definition(schema: dict, required: bool):
    python_type = _json_schema_to_python_type(schema)
    description = schema.get("description")
    default = ... if required else None
    annotated_type = python_type if required else Optional[python_type]
    return (
        annotated_type,
        Field(default=default, description=description),
    )


def _json_schema_to_python_type(schema: dict):
    schema_type = schema.get("type", "string")
    if schema_type == "integer":
        return int
    if schema_type == "number":
        return float
    if schema_type == "boolean":
        return bool
    if schema_type == "array":
        return list[Any]
    if schema_type == "object":
        return dict[str, Any]
    return str


def _sanitize_model_name(tool_name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", tool_name).strip("_")
    if not cleaned:
        cleaned = "UserDefinedTool"
    if cleaned[0].isdigit():
        cleaned = f"Tool_{cleaned}"
    return cleaned
