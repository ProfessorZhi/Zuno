import argparse
import json
import keyword
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[3]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from mcp.server.fastmcp import FastMCP

from agentchat.services.mcp.sessions import create_session


def _safe_identifier(name: str) -> str:
    candidate = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in name)
    if not candidate:
        candidate = "tool"
    if candidate[0].isdigit():
        candidate = f"tool_{candidate}"
    if keyword.iskeyword(candidate):
        candidate = f"{candidate}_tool"
    return candidate


def _schema_type_to_python(schema: dict[str, Any]) -> str:
    schema_type = schema.get("type")
    if schema_type == "string":
        return "str"
    if schema_type == "integer":
        return "int"
    if schema_type == "number":
        return "float"
    if schema_type == "boolean":
        return "bool"
    if schema_type == "array":
        return "list"
    if schema_type == "object":
        return "dict"
    return "Any"


def _result_to_text(result: Any) -> str:
    if getattr(result, "structuredContent", None) is not None:
        return json.dumps(result.structuredContent, ensure_ascii=False, indent=2)

    chunks: list[str] = []
    for content in getattr(result, "content", []) or []:
        if hasattr(content, "text"):
            chunks.append(content.text)
        elif hasattr(content, "model_dump"):
            chunks.append(json.dumps(content.model_dump(), ensure_ascii=False, indent=2))
        else:
            chunks.append(str(content))
    text = "\n".join(part for part in chunks if part)
    if getattr(result, "isError", False):
        raise RuntimeError(text or "Remote MCP tool call failed")
    return text or ""


def _build_proxy_connection(args: argparse.Namespace) -> dict[str, Any]:
    connection: dict[str, Any] = {
        "transport": args.target_transport,
        "url": args.target_url,
    }
    if args.headers_json:
        connection["headers"] = json.loads(args.headers_json)
    return connection


def _create_tool_function(
    mcp: FastMCP,
    remote_tool_name: str,
    description: str,
    input_schema: dict[str, Any],
    target_connection: dict[str, Any],
) -> None:
    properties = input_schema.get("properties") or {}
    required_fields = set(input_schema.get("required") or [])
    local_name_map = {key: _safe_identifier(key) for key in properties.keys()}

    namespace: dict[str, Any] = {
        "Any": Any,
        "_target_connection": target_connection,
        "_remote_tool_name": remote_tool_name,
        "_result_to_text": _result_to_text,
        "create_session": create_session,
    }

    signature_parts: list[str] = []
    body_lines = [
        "async def generated_tool(",
    ]
    # Placeholder to fill later
    ordered_items = sorted(
        properties.items(),
        key=lambda item: (item[0] not in required_fields, item[0]),
    )
    for key, schema in ordered_items:
        local_name = local_name_map[key]
        annotation = _schema_type_to_python(schema)
        if key in required_fields:
            signature_parts.append(f"{local_name}: {annotation}")
        else:
            signature_parts.append(f"{local_name}: {annotation} | None = None")

    body_lines[0] += ", ".join(signature_parts) + "):"
    body_lines.extend(
        [
            "    arguments = {}",
        ]
    )
    for original_key, local_name in local_name_map.items():
        if original_key in required_fields:
            body_lines.append(f"    arguments[{original_key!r}] = {local_name}")
        else:
            body_lines.append(f"    if {local_name} is not None:")
            body_lines.append(f"        arguments[{original_key!r}] = {local_name}")
    body_lines.extend(
        [
            "    async with create_session(_target_connection) as session:",
            "        await session.initialize()",
            "        result = await session.call_tool(_remote_tool_name, arguments)",
            "    return _result_to_text(result)",
        ]
    )

    exec("\n".join(body_lines), namespace)  # noqa: S102
    generated_tool = namespace["generated_tool"]
    generated_tool.__name__ = _safe_identifier(remote_tool_name)
    mcp.add_tool(generated_tool, name=remote_tool_name, description=description)


async def _register_proxy_tools(mcp: FastMCP, target_connection: dict[str, Any]) -> None:
    async with create_session(target_connection) as session:
        await session.initialize()
        result = await session.list_tools()
    for tool in result.tools:
        _create_tool_function(
            mcp=mcp,
            remote_tool_name=tool.name,
            description=tool.description or "",
            input_schema=tool.inputSchema or {"type": "object", "properties": {}},
            target_connection=target_connection,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Remote MCP proxy server")
    parser.add_argument("--server-name", required=True, help="Local MCP server display name")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "streamable-http"],
        help="Local proxy transport exposed to Zuno",
    )
    parser.add_argument(
        "--target-transport",
        default="sse",
        choices=["sse", "streamable_http"],
        help="Transport used to connect to the remote MCP server",
    )
    parser.add_argument("--target-url", required=True, help="Remote MCP URL")
    parser.add_argument("--headers-json", default="", help="Optional JSON headers for the remote MCP request")
    args = parser.parse_args()

    mcp = FastMCP(args.server_name)
    target_connection = _build_proxy_connection(args)

    import anyio

    anyio.run(lambda: _register_proxy_tools(mcp, target_connection))
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
