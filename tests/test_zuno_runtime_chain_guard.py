from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


CRITICAL_RUNTIME_FILES = [
    "src/backend/zuno/main.py",
    "src/backend/zuno/api/router.py",
    "src/backend/zuno/api/v1/__init__.py",
    "src/backend/zuno/api/v1/workspace.py",
    "src/backend/zuno/database/init_data.py",
    "src/backend/zuno/services/__init__.py",
    "src/backend/zuno/services/queue/runner.py",
    "src/backend/zuno/services/queue/workers.py",
    "src/backend/zuno/services/queue/client.py",
    "src/backend/zuno/services/queue/messages.py",
    "src/backend/zuno/services/pipeline/manager.py",
    "src/backend/zuno/services/storage/__init__.py",
    "src/backend/zuno/services/rag/vector_db/__init__.py",
]


def test_critical_zuno_runtime_chain_does_not_directly_import_agentchat():
    for relative_path in CRITICAL_RUNTIME_FILES:
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "from agentchat" not in content, relative_path
        assert "import agentchat" not in content, relative_path


def test_workspace_route_now_delegates_runtime_orchestration_to_service_layer():
    relative_path = "src/backend/zuno/api/v1/workspace.py"
    content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
    service_content = (
        REPO_ROOT / "src/backend/zuno/api/services/workspace.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.api.services.workspace import WorkspaceService" in content
    assert "from zuno.api.services.llm import LLMService" not in content
    assert "from zuno.api.services.mcp_server import MCPService" not in content
    assert "from zuno.api.services.agent import AgentService" not in content
    assert "from zuno.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent" not in content
    assert "from zuno.api.services.llm import LLMService" in service_content
    assert "from zuno.api.services.mcp_server import MCPService" in service_content
    assert "from zuno.api.services.agent import AgentService" in service_content
    assert "from agentchat.api.v1.workspace import *" not in content
