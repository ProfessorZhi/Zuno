from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_core_database_and_runtime_services_no_longer_import_api_services_directly() -> None:
    expected = {
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

    forbidden_phrase = "from zuno.api.services."
    for relative_path, required_phrases in expected.items():
        content = _read(relative_path)
        assert forbidden_phrase not in content, f"forbidden api.services dependency remains in {relative_path}"
        for phrase in required_phrases:
            assert phrase in content, f"missing application-layer import in {relative_path}: {phrase}"


def test_application_service_exports_exist_for_high_value_boundary_modules() -> None:
    expected = {
        "src/backend/zuno/services/application/agent.py": "from zuno.api.services.agent import AgentService, HIDDEN_SYSTEM_AGENT_NAMES",
        "src/backend/zuno/services/application/agent_skill.py": "from zuno.api.services.agent_skill import AgentSkillService, default_agent_skill_folder",
        "src/backend/zuno/services/application/knowledge.py": "from zuno.api.services.knowledge import DEFAULT_KNOWLEDGE_CONFIG, KnowledgeService",
        "src/backend/zuno/services/application/llm.py": "from zuno.api.services.llm import LLMService, LLM_Types, MODEL_SLOTS",
        "src/backend/zuno/services/application/mcp_server.py": "from zuno.api.services.mcp_server import MCPService",
        "src/backend/zuno/services/application/mcp_user_config.py": "from zuno.api.services.mcp_user_config import MCPUserConfigService",
        "src/backend/zuno/services/application/tool.py": "from zuno.api.services.tool import ToolRuntimeService, ToolService, HIDDEN_SYSTEM_TOOL_NAMES",
        "src/backend/zuno/services/application/usage_stats.py": "from zuno.api.services.usage_stats import UsageStatsService",
    }

    for relative_path, phrase in expected.items():
        content = _read(relative_path)
        assert phrase in content, f"missing application export in {relative_path}"


def test_backend_layering_verifier_knows_phase4_contract() -> None:
    verifier = _read("tools/scripts/verify_backend_layering.py")

    required_phrases = [
        "FORBIDDEN_IMPORTS",
        "REQUIRED_IMPORTS",
        "APPLICATION_EXPORTS",
        "Backend layering verification passed.",
        "src/backend/zuno/core/callbacks/usage_metadata.py",
        "src/backend/zuno/database/init_data.py",
    ]

    for phrase in required_phrases:
        assert phrase in verifier, f"missing verifier phrase: {phrase}"
