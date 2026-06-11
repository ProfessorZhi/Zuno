from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Literal

from agentchat.api.services.agent_skill import AgentSkillService
from agentchat.api.services.mcp_server import MCPService
from agentchat.api.services.tool import ToolService

CapabilityKind = Literal["tool", "skill", "mcp_server", "mcp_tool"]


class CapabilityRegistryService:
    """Unified searchable catalog for tools, skills, and MCP capabilities."""

    KIND_ALIASES: dict[str, set[str]] = {
        "tool": {"tool", "tools", "工具"},
        "skill": {"skill", "skills", "技能"},
        "mcp_server": {"mcp_server", "mcp", "server", "服务"},
        "mcp_tool": {"mcp_tool", "mcp", "工具"},
    }

    @classmethod
    async def search(
        cls,
        query: str,
        *,
        user_id: str,
        kind: str | None = None,
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        capabilities = await cls.list_capabilities(user_id)
        normalized_kind = cls._normalize_kind(kind)
        if normalized_kind:
            capabilities = [
                item for item in capabilities
                if item["kind"] == normalized_kind or (
                    normalized_kind == "mcp_server" and item["kind"] == "mcp_tool"
                )
            ]

        scored = []
        for item in capabilities:
            score = cls._score(query, item)
            if score <= 0 and query.strip():
                continue
            scored.append({**item, "score": score})

        scored.sort(
            key=lambda item: (
                item["score"],
                1 if item.get("status") == "ready" else 0,
                cls._source_priority(str(item.get("source") or "")),
            ),
            reverse=True,
        )
        return scored[: max(1, min(limit, 50))]

    @classmethod
    async def list_capabilities(cls, user_id: str) -> list[dict[str, Any]]:
        tools = await ToolService.get_visible_tool_by_user(user_id)
        skills = await AgentSkillService.get_agent_skills(user_id)
        mcp_servers = await MCPService.get_all_servers(user_id)

        capabilities: list[dict[str, Any]] = []
        for tool in tools:
            capabilities.append(cls._tool_capability(tool))
        for skill in skills:
            capabilities.append(cls._skill_capability(skill))
        for server in mcp_servers:
            capabilities.extend(cls._mcp_capabilities(server))
        return capabilities

    @classmethod
    def _tool_capability(cls, tool: dict[str, Any]) -> dict[str, Any]:
        runtime_type = str(tool.get("runtime_type") or ("remote_api" if tool.get("is_user_defined") else "system"))
        source = "user" if tool.get("is_user_defined") else "system"
        name = str(tool.get("name") or "")
        display_name = str(tool.get("display_name") or name)
        return cls._base_capability(
            id=f"tool:{tool.get('tool_id') or name}",
            kind="tool",
            name=name,
            display_name=display_name,
            description=str(tool.get("description") or ""),
            source=source,
            status="ready",
            status_message="",
            tags=[runtime_type, "api" if runtime_type == "remote_api" else runtime_type],
            aliases=[name, display_name],
            invoke_ref={"tool_id": tool.get("tool_id"), "tool_name": name},
            metadata={"runtime_type": runtime_type},
        )

    @classmethod
    def _skill_capability(cls, skill: dict[str, Any]) -> dict[str, Any]:
        skill_id = str(skill.get("id") or skill.get("agent_skill_id") or skill.get("name") or "")
        name = str(skill.get("name") or skill.get("as_tool_name") or skill_id)
        tool_name = str(skill.get("as_tool_name") or name)
        source = str(skill.get("source") or ("system" if skill.get("is_system") else "user"))
        return cls._base_capability(
            id=f"skill:{skill_id}",
            kind="skill",
            name=name,
            display_name=name,
            description=str(skill.get("description") or ""),
            source=source,
            status="ready",
            status_message="",
            tags=["skill", source],
            aliases=[name, tool_name],
            invoke_ref={"agent_skill_id": skill_id, "as_tool_name": tool_name},
            metadata={"readonly": bool(skill.get("is_readonly"))},
        )

    @classmethod
    def _mcp_capabilities(cls, server: dict[str, Any]) -> list[dict[str, Any]]:
        server_id = str(server.get("mcp_server_id") or server.get("server_id") or server.get("server_name") or "")
        server_name = str(server.get("server_name") or server.get("mcp_as_tool_name") or server_id)
        status, status_message = cls._mcp_status(server)
        source = "system" if str(server.get("user_id") or "") == "system" else "user"

        capabilities = [
            cls._base_capability(
                id=f"mcp_server:{server_id}",
                kind="mcp_server",
                name=server_name,
                display_name=server_name,
                description=str(server.get("description") or ""),
                source=source,
                status=status,
                status_message=status_message,
                tags=["mcp", str(server.get("type") or "")],
                aliases=[server_name, str(server.get("mcp_as_tool_name") or "")],
                invoke_ref={"mcp_server_id": server_id},
                metadata={"transport": server.get("type"), "tool_count": len(server.get("tools") or [])},
            )
        ]

        for tool_def in cls._iter_mcp_tool_defs(server):
            tool_name = str(tool_def.get("name") or "")
            if not tool_name:
                continue
            capabilities.append(
                cls._base_capability(
                    id=f"mcp_tool:{server_id}:{tool_name}",
                    kind="mcp_tool",
                    name=tool_name,
                    display_name=f"{server_name} / {tool_name}",
                    description=str(tool_def.get("description") or ""),
                    source=source,
                    status=status,
                    status_message=status_message,
                    tags=["mcp", str(server.get("type") or ""), server_name],
                    aliases=[server_name, tool_name, str(server.get("mcp_as_tool_name") or "")],
                    invoke_ref={"mcp_server_id": server_id, "mcp_tool_name": tool_name},
                    metadata={"transport": server.get("type")},
                )
            )
        return capabilities

    @staticmethod
    def _base_capability(
        *,
        id: str,
        kind: CapabilityKind,
        name: str,
        display_name: str,
        description: str,
        source: str,
        status: str,
        status_message: str,
        tags: list[str],
        aliases: list[str],
        invoke_ref: dict[str, Any],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "id": id,
            "kind": kind,
            "name": name,
            "display_name": display_name,
            "description": description,
            "source": source,
            "status": status,
            "status_message": status_message,
            "tags": [tag for tag in tags if tag],
            "aliases": [alias for alias in aliases if alias],
            "invoke_ref": invoke_ref,
            "metadata": metadata,
        }

    @staticmethod
    def _iter_mcp_tool_defs(server: dict[str, Any]) -> list[dict[str, Any]]:
        params = server.get("params") or []
        if isinstance(params, list) and params:
            return [item for item in params if isinstance(item, dict)]
        return [
            {"name": tool_name, "description": ""}
            for tool_name in (server.get("tools") or [])
            if tool_name
        ]

    @staticmethod
    def _mcp_status(server: dict[str, Any]) -> tuple[str, str]:
        status = server.get("test_status") or {}
        if status.get("success") is True:
            return "ready", str(status.get("message") or "")
        if status:
            return "needs_config", str(status.get("message") or "MCP 未通过连通性测试")
        if server.get("tools") or server.get("params"):
            return "ready", ""
        return "needs_config", "MCP 尚未测试或没有发现可用工具"

    @classmethod
    def _normalize_kind(cls, kind: str | None) -> str:
        raw = (kind or "").strip().lower()
        if not raw:
            return ""
        for normalized, aliases in cls.KIND_ALIASES.items():
            if raw == normalized or raw in aliases:
                return normalized
        return raw

    @classmethod
    def _score(cls, query: str, item: dict[str, Any]) -> float:
        normalized_query = cls._normalize_text(query)
        if not normalized_query:
            return 1.0

        haystack_parts = [
            item.get("name"),
            item.get("display_name"),
            item.get("description"),
            item.get("kind"),
            item.get("source"),
            " ".join(item.get("tags") or []),
            " ".join(item.get("aliases") or []),
        ]
        haystack = cls._normalize_text(" ".join(str(part or "") for part in haystack_parts))
        if not haystack:
            return 0

        score = 0.0
        query_tokens = cls._query_tokens(normalized_query)
        if normalized_query in haystack:
            score += 100
        for token in query_tokens:
            if token and token in haystack:
                score += 25 if len(token) > 1 else 8

        name_text = cls._normalize_text(f"{item.get('name', '')} {item.get('display_name', '')}")
        score += SequenceMatcher(None, normalized_query, name_text).ratio() * 20
        score += SequenceMatcher(None, normalized_query, haystack[: max(60, len(normalized_query))]).ratio() * 10
        return score

    @staticmethod
    def _normalize_text(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").strip().lower())

    @staticmethod
    def _query_tokens(query: str) -> list[str]:
        tokens = [token for token in re.split(r"[\s,，。；;:/\\|]+", query) if token]
        # Chinese queries often arrive without spaces; bi-grams catch fuzzy intent such as "飞书消息".
        compact = re.sub(r"\s+", "", query)
        if re.search(r"[\u4e00-\u9fff]", compact):
            tokens.extend(compact[index:index + 2] for index in range(max(0, len(compact) - 1)))
        return list(dict.fromkeys(tokens))

    @staticmethod
    def _source_priority(source: str) -> int:
        if source == "user":
            return 3
        if source == "host":
            return 2
        if source == "system":
            return 1
        return 0
