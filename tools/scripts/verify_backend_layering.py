from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_IMPORTS: dict[str, list[str]] = {
    "src/backend/zuno/core/callbacks/usage_metadata.py": [
        "from zuno.api.services.usage_stats import UsageStatsService",
    ],
    "src/backend/zuno/database/init_data.py": [
        "from zuno.api.services.agent import AgentService",
        "from zuno.api.services.llm import LLMService",
        "from zuno.api.services.mcp_server import MCPService",
        "from zuno.api.services.tool import ToolService",
    ],
    "src/backend/zuno/services/capability_registry.py": [
        "from zuno.api.services.agent_skill import AgentSkillService",
        "from zuno.api.services.mcp_server import MCPService",
        "from zuno.api.services.tool import ToolService",
    ],
    "src/backend/zuno/services/pipeline/manager.py": [
        "from zuno.api.services.knowledge import KnowledgeService",
    ],
    "src/backend/zuno/services/retrieval/retrievers.py": [
        "from zuno.api.services.knowledge import KnowledgeService",
    ],
    "src/backend/zuno/services/rag/handler.py": [
        "from zuno.api.services.knowledge import KnowledgeService",
    ],
    "src/backend/zuno/services/tool_creation_service.py": [
        "from zuno.api.services.tool import ToolService",
    ],
}

REQUIRED_IMPORTS: dict[str, list[str]] = {
    "src/backend/zuno/core/callbacks/usage_metadata.py": [
        "from zuno.services.application.usage_stats import UsageStatsService",
    ],
    "src/backend/zuno/database/init_data.py": [
        "from zuno.services.application.agent import AgentService",
        "from zuno.services.application.llm import LLMService",
        "from zuno.services.application.mcp_server import MCPService",
        "from zuno.services.application.tool import ToolService",
    ],
    "src/backend/zuno/services/capability_registry.py": [
        "from zuno.services.application.agent_skill import AgentSkillService",
        "from zuno.services.application.mcp_server import MCPService",
        "from zuno.services.application.tool import ToolService",
    ],
    "src/backend/zuno/services/pipeline/manager.py": [
        "from zuno.services.application.knowledge import KnowledgeService",
    ],
    "src/backend/zuno/services/retrieval/retrievers.py": [
        "from zuno.services.application.knowledge import KnowledgeService",
    ],
    "src/backend/zuno/services/rag/handler.py": [
        "from zuno.services.application.knowledge import KnowledgeService",
    ],
    "src/backend/zuno/services/tool_creation_service.py": [
        "from zuno.services.application.tool import ToolService",
    ],
}

APPLICATION_EXPORTS: dict[str, list[str]] = {
    "src/backend/zuno/services/application/usage_stats.py": [
        "from zuno.api.services.usage_stats import UsageStatsService",
    ],
    "src/backend/zuno/services/application/knowledge.py": [
        "from zuno.api.services.knowledge import DEFAULT_KNOWLEDGE_CONFIG, KnowledgeService",
    ],
    "src/backend/zuno/services/application/mcp_server.py": [
        "from zuno.api.services.mcp_server import MCPService",
    ],
}


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    for relative_path, phrases in FORBIDDEN_IMPORTS.items():
        content = _read_text(relative_path)
        for phrase in phrases:
            if phrase in content:
                errors.append(f"{relative_path} still contains forbidden import: {phrase}")

    for relative_path, phrases in REQUIRED_IMPORTS.items():
        content = _read_text(relative_path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{relative_path} missing required import: {phrase}")

    for relative_path, phrases in APPLICATION_EXPORTS.items():
        content = _read_text(relative_path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{relative_path} missing application export: {phrase}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Backend layering verification failed.")
        return 1

    print("Backend layering verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
