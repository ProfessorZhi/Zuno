from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICE_API_V1_ROOT = REPO_ROOT / "services/api/src/zuno/api/v1"


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_api_v1_routes_no_longer_directly_import_runtime_layers() -> None:
    direct_import_lines: list[str] = []

    for path in sorted(SERVICE_API_V1_ROOT.glob("*.py")):
        content = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            if (
                stripped.startswith("from zuno.services.")
                or stripped.startswith("import zuno.services.")
                or stripped.startswith("from zuno.core.")
                or stripped.startswith("import zuno.core.")
                or stripped.startswith("from zuno.tools.")
                or stripped.startswith("import zuno.tools.")
            ):
                direct_import_lines.append(f"{path}:{line_number}:{stripped}")

    assert direct_import_lines == []


def test_user_controller_avoids_direct_dao_and_redis_imports() -> None:
    content = _read("services/api/src/zuno/api/v1/user.py")

    assert "from zuno.api.services.user import UserService, get_user_jwt" in content
    assert "from zuno.database.dao.user import UserDao" not in content
    assert "from zuno.services.redis import redis_client" not in content
    assert "from zuno.utils.JWT import ACCESS_TOKEN_EXPIRE_TIME" not in content


def test_knowledge_controller_routes_search_through_service_layer() -> None:
    controller = _read("services/api/src/zuno/api/v1/knowledge.py")
    service = _read("services/api/src/zuno/api/services/knowledge.py")

    assert "from zuno.services.rag.handler import RagHandler" not in controller
    assert "await KnowledgeService.search_knowledge(" in controller
    assert "from zuno.services.rag.handler import RagHandler" in service


def test_knowledge_file_controller_avoids_direct_storage_imports() -> None:
    controller = _read("services/api/src/zuno/api/v1/knowledge_file.py")
    service = _read("services/api/src/zuno/api/services/knowledge_file.py")

    assert "from zuno.services.storage import storage_client" not in controller
    assert "from zuno.utils.file_utils import get_object_key_from_public_url, get_save_tempfile" not in controller
    assert "KnowledgeFileService.prepare_uploaded_file(file_url)" in controller
    assert "from zuno.services.storage import storage_client" in service
    assert "from zuno.utils.file_utils import get_object_key_from_public_url, get_save_tempfile" in service


def test_upload_controller_routes_storage_through_service_layer() -> None:
    controller = _read("services/api/src/zuno/api/v1/upload.py")
    service = _read("services/api/src/zuno/api/services/upload.py")

    assert "from zuno.api.services.upload import UploadService" in controller
    assert "from zuno.services.storage import storage_client" not in controller
    assert "from zuno.settings import app_settings" not in controller
    assert "from zuno.services.storage import storage_client" in service


def test_completion_controller_avoids_direct_agent_and_memory_imports() -> None:
    controller = _read("services/api/src/zuno/api/v1/completion.py")
    service = _read("services/api/src/zuno/api/services/completion.py")

    assert "from zuno.api.services.completion import CompletionService" in controller
    assert "from zuno.core.agents.general_agent import AgentConfig, GeneralAgent" not in controller
    assert "from zuno.services.memory.client import memory_client" not in controller
    assert "from zuno.core.agents.general_agent import AgentConfig, GeneralAgent" in service


def test_wechat_controller_avoids_direct_redis_and_agent_imports() -> None:
    controller = _read("services/api/src/zuno/api/v1/wechat.py")
    service = _read("services/api/src/zuno/api/services/wechat.py")

    assert "from zuno.services.redis import redis_client" not in controller
    assert "from zuno.services.workspace.wechat_agent import WeChatAgent" not in controller
    assert "from zuno.api.services.workspace_session import WorkSpaceSessionService" not in controller
    assert "from zuno.services.redis import redis_client" in service
    assert "from zuno.api.services.workspace_session import WorkSpaceSessionService" in service


def test_mcp_server_controller_avoids_direct_runtime_and_mcp_manager_imports() -> None:
    controller = _read("services/api/src/zuno/api/v1/mcp_server.py")
    service = _read("services/api/src/zuno/api/services/mcp_server.py")

    assert "from zuno.core.agents.structured_response_agent import StructuredResponseAgent" not in controller
    assert "from zuno.services.mcp.manager import MCPManager" not in controller
    assert "from zuno.utils.convert import convert_mcp_config" not in controller
    assert "from zuno.utils.helpers import parse_imported_config" not in controller
    assert "from zuno.core.agents.structured_response_agent import StructuredResponseAgent" in service
    assert "from zuno.services.mcp.manager import MCPManager" in service


def test_workspace_controller_routes_runtime_orchestration_through_service_layer() -> None:
    controller = _read("services/api/src/zuno/api/v1/workspace.py")
    service = _read("services/api/src/zuno/api/services/workspace.py")

    assert "from zuno.api.services.workspace import WorkspaceService" in controller
    assert "from zuno.services.execution_policy import (" not in controller
    assert "from zuno.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent" not in controller
    assert "from zuno.services.workspace.attachment_service import (" not in controller
    assert "from zuno.utils.helpers import parse_imported_config" not in controller
    assert "from zuno.services.execution_policy import (" in service
    assert "from zuno.services.workspace.attachment_service import (" in service
    assert 'from zuno.services.workspace.simple_agent import MCPConfig' in service or 'from zuno.services.workspace.simple_agent import WorkSpaceSimpleAgent' in service


def test_capability_controller_routes_registry_search_through_service_layer() -> None:
    controller = _read("services/api/src/zuno/api/v1/capability.py")
    service = _read("services/api/src/zuno/api/services/capability.py")

    assert "from zuno.api.services.capability import CapabilityService" in controller
    assert "from zuno.services.capability_registry import CapabilityRegistryService" not in controller
    assert "await CapabilityService.search_capabilities(" in controller
    assert "from zuno.services.capability_registry import CapabilityRegistryService" in service


def test_tool_controller_routes_runtime_validation_and_connectivity_through_service_layer() -> None:
    controller = _read("services/api/src/zuno/api/v1/tool.py")
    service = _read("services/api/src/zuno/api/services/tool.py")

    assert "from zuno.api.services.tool import ToolRuntimeService, ToolService" in controller
    assert "from zuno.services.cli_tool_discovery import CliToolDiscoveryService" not in controller
    assert "from zuno.services.simple_api_tool import (" not in controller
    assert "from zuno.services.tool_connectivity_service import ToolConnectivityService" not in controller
    assert "from zuno.services.tool_creation_service import ToolCreationService" not in controller
    assert "from zuno.services.user_defined_tool_runtime import build_stored_tool_auth_config" not in controller
    assert "from zuno.tools.cli_tool.adapter import CLIToolAdapter" not in controller
    assert "from zuno.tools.openapi_tool.adapter import OpenAPIToolAdapter" not in controller
    assert "await ToolRuntimeService.create_user_defined_tool(" in controller
    assert "ToolRuntimeService.preview_cli_tool_directory(req)" in controller
    assert "await ToolRuntimeService.assist_remote_api_tool(req)" in controller
    assert "await ToolRuntimeService.test_tool_connectivity(req)" in controller
    assert "await ToolRuntimeService.test_system_tool_connectivity(tool_name)" in controller
    assert "await ToolRuntimeService.test_saved_tool_connectivity(tool)" in controller
    assert "ToolRuntimeService.build_update_payload(req)" in controller
    assert "from zuno.services.cli_tool_discovery import CliToolDiscoveryService" in service
    assert "from zuno.services.simple_api_tool import (" in service
    assert "from zuno.services.tool_connectivity_service import ToolConnectivityService" in service
    assert "from zuno.services.tool_creation_service import ToolCreationService" in service
    assert "from zuno.services.user_defined_tool_runtime import build_stored_tool_auth_config" in service
