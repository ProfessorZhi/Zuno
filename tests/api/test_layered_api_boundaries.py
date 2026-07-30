from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICE_API_V1_ROOT = REPO_ROOT / "src/backend/zuno/api/v1"


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
                or stripped.startswith("from zuno.schema.")
                or stripped.startswith("import zuno.schema.")
                or stripped.startswith("from zuno.utils.contexts")
            ):
                direct_import_lines.append(f"{path}:{line_number}:{stripped}")

    assert direct_import_lines == []


def test_user_controller_avoids_direct_dao_and_redis_imports() -> None:
    content = _read("src/backend/zuno/api/v1/user.py")

    assert "from zuno.api.services.user import UserService, get_user_jwt" in content
    assert "from zuno.database.dao.user import UserDao" not in content
    assert "from zuno.services.redis import redis_client" not in content
    assert "from zuno.utils.JWT import ACCESS_TOKEN_EXPIRE_TIME" not in content


def test_knowledge_controller_routes_search_through_service_layer() -> None:
    controller = _read("src/backend/zuno/api/v1/knowledge.py")
    service = _read("src/backend/zuno/api/services/knowledge.py")

    assert "from zuno.services.rag.handler import RagHandler" not in controller
    assert "await KnowledgeService.search_knowledge(" in controller
    assert "from zuno.services.rag.handler import RagHandler" not in service
    assert "from zuno.platform.services.application.knowledge import KnowledgeQueryService" in service


def test_knowledge_file_controller_avoids_direct_storage_imports() -> None:
    controller = _read("src/backend/zuno/api/v1/knowledge_file.py")
    service = _read("src/backend/zuno/api/services/knowledge_file.py")

    assert "from zuno.services.storage import storage_client" not in controller
    assert "from zuno.utils.file_utils import get_object_key_from_public_url, get_save_tempfile" not in controller
    assert "KnowledgeFileService.prepare_uploaded_file(file_url)" in controller
    assert "from zuno.platform.services.storage import storage_client" in service
    assert "from zuno.platform.common.file_utils import get_object_key_from_public_url, get_save_tempfile" in service


def test_upload_controller_routes_storage_through_service_layer() -> None:
    controller = _read("src/backend/zuno/api/v1/upload.py")
    service = _read("src/backend/zuno/api/services/upload.py")

    assert "from zuno.api.services.upload import UploadService" in controller
    assert "from zuno.services.storage import storage_client" not in controller
    assert "from zuno.settings import app_settings" not in controller
    assert "from zuno.platform.services.storage import storage_client" in service


def test_completion_controller_avoids_direct_agent_and_memory_imports() -> None:
    controller = _read("src/backend/zuno/api/v1/completion.py")
    service = _read("src/backend/zuno/api/services/completion.py")

    assert "from zuno.api.services.completion import CompletionService" in controller
    assert "from zuno.core.agents.general_agent import AgentConfig, GeneralAgent" not in controller
    assert "from zuno.services.memory.client import memory_client" not in controller
    assert "from zuno.core.agents.general_agent import AgentConfig, GeneralAgent" in service


def test_wechat_controller_avoids_direct_redis_and_agent_imports() -> None:
    controller = _read("src/backend/zuno/api/v1/wechat.py")
    service = _read("src/backend/zuno/api/services/wechat.py")

    assert "from zuno.services.redis import redis_client" not in controller
    assert "from zuno.services.workspace.wechat_agent import WeChatAgent" not in controller
    assert "from zuno.api.services.workspace_session import WorkSpaceSessionService" not in controller
    assert "from zuno.services.redis import redis_client" in service
    assert "from zuno.api.services.workspace_session import WorkSpaceSessionService" in service


def test_mcp_server_controller_avoids_direct_runtime_and_mcp_manager_imports() -> None:
    controller = _read("src/backend/zuno/api/v1/mcp_server.py")
    service = _read("src/backend/zuno/api/services/mcp_server.py")

    assert "from zuno.core.agents.structured_response_agent import StructuredResponseAgent" not in controller
    assert "from zuno.services.mcp.manager import MCPManager" not in controller
    assert "from zuno.utils.convert import convert_mcp_config" not in controller
    assert "from zuno.utils.helpers import parse_imported_config" not in controller
    assert "from zuno.agent.core.agents.structured_response_agent import StructuredResponseAgent" in service
    assert "from zuno.platform.services.mcp.manager import MCPManager" in service


def test_workspace_controller_routes_runtime_orchestration_through_service_layer() -> None:
    controller = _read("src/backend/zuno/api/v1/workspace.py")
    service = _read("src/backend/zuno/api/services/workspace.py")

    assert "from zuno.api.services.workspace import WorkspaceService" in controller
    assert "from zuno.services.execution_policy import (" not in controller
    assert "from zuno.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent" not in controller
    assert "from zuno.services.workspace.attachment_service import (" not in controller
    assert "from zuno.utils.helpers import parse_imported_config" not in controller
    assert "from zuno.platform.services.execution_policy import (" in service
    assert "from zuno.platform.services.workspace.attachment_service import (" in service
    assert 'from zuno.platform.services.workspace.simple_agent import MCPConfig' in service or 'from zuno.platform.services.workspace.simple_agent import WorkSpaceSimpleAgent' in service


def test_capability_controller_routes_registry_search_through_service_layer() -> None:
    controller = _read("src/backend/zuno/api/v1/capability.py")
    service = _read("src/backend/zuno/api/services/capability.py")

    assert "from zuno.api.services.capability import CapabilityService" in controller
    assert "from zuno.services.capability_registry import CapabilityRegistryService" not in controller
    assert "await CapabilityService.search_capabilities(" in controller
    assert "from zuno.platform.services.capability_registry import CapabilityRegistryService" in service
    assert "from zuno.database import engine" not in service


def test_tool_controller_routes_runtime_validation_and_connectivity_through_service_layer() -> None:
    controller = _read("src/backend/zuno/api/v1/tool.py")
    service = _read("src/backend/zuno/api/services/tool.py")

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
    assert "from zuno.platform.services.cli_tool_discovery import CliToolDiscoveryService" in service
    assert "from zuno.platform.services.simple_api_tool import (" in service
    assert "from zuno.platform.services.tool_connectivity_service import ToolConnectivityService" in service


def test_capability_tool_actions_use_canonical_imports() -> None:
    convert_to_docx = _read("src/backend/zuno/capability/tools/convert_to_docx/action.py")
    convert_to_pdf = _read("src/backend/zuno/capability/tools/convert_to_pdf/action.py")
    get_weather = _read("src/backend/zuno/capability/tools/get_weather/action.py")
    delivery = _read("src/backend/zuno/capability/tools/delivery/action.py")

    assert "from zuno.platform.services.storage import storage_client" in convert_to_docx
    assert "from zuno.platform.common.file_utils import get_object_name_from_aliyun_url, get_save_tempfile" in convert_to_docx
    assert "from zuno.platform.common.helpers import get_now_beijing_time" in convert_to_docx
    assert "from zuno.platform.services.storage import storage_client" in convert_to_pdf
    assert "from zuno.platform.common.file_utils import get_object_name_from_aliyun_url, get_save_tempfile" in convert_to_pdf
    assert "from zuno.platform.common.helpers import get_now_beijing_time" in convert_to_pdf
    assert "from zuno.platform.resources.prompts.tool import MESSAGE_PROMPT, WEATHER_PROMPT" in get_weather
    assert "from zuno.platform.resources.prompts.tool import DELIVERY_PROMPT" in delivery

    for content in [convert_to_docx, convert_to_pdf, get_weather, delivery]:
        assert "from zuno.services." not in content
        assert "from zuno.resources." not in content
        assert "from zuno.utils." not in content


def test_api_service_layer_uses_canonical_platform_imports() -> None:
    upload = _read("src/backend/zuno/api/services/upload.py")
    knowledge_file = _read("src/backend/zuno/api/services/knowledge_file.py")
    workspace_session = _read("src/backend/zuno/api/services/workspace_session.py")
    user = _read("src/backend/zuno/api/services/user.py")
    tool = _read("src/backend/zuno/api/services/tool.py")
    knowledge = _read("src/backend/zuno/api/services/knowledge.py")
    agent = _read("src/backend/zuno/api/services/agent.py")
    history = _read("src/backend/zuno/api/services/history.py")
    llm = _read("src/backend/zuno/api/services/llm.py")
    mcp_server = _read("src/backend/zuno/api/services/mcp_server.py")
    message = _read("src/backend/zuno/api/services/message.py")
    dialog = _read("src/backend/zuno/api/services/dialog.py")
    message_events = _read("src/backend/zuno/api/services/message_events.py")
    mcp_user_config = _read("src/backend/zuno/api/services/mcp_user_config.py")
    mcp_stdio_server = _read("src/backend/zuno/api/services/mcp_stdio_server.py")
    usage_stats = _read("src/backend/zuno/api/services/usage_stats.py")
    mcp_agent = _read("src/backend/zuno/api/services/mcp_agent.py")
    capability = _read("src/backend/zuno/api/services/capability.py")
    agent_skill = _read("src/backend/zuno/api/services/agent_skill.py")

    assert "from zuno.platform.services.storage import storage_client" in upload
    assert "from zuno.platform.common.file_utils import get_object_storage_base_path" in upload
    assert "from zuno.platform.database.dao.knowledge_file import KnowledgeFileDao" in knowledge_file
    assert "from zuno.platform.database.dao.knowledge_task import KnowledgeTaskDao" in knowledge_file
    assert "from zuno.platform.services.pipeline.manager import KnowledgePipelineManager" in knowledge_file
    assert "from zuno.platform.services.queue.client import QueueClient, get_queue_names" in knowledge_file
    assert "from zuno.platform.services.rag.handler import RagHandler" in knowledge_file
    assert "from zuno.platform.services.storage import storage_client" in knowledge_file
    assert "from zuno.platform.common.runtime_observability import get_active_trace_id" in knowledge_file
    assert "from zuno.platform.database.dao.workspace_session import WorkSpaceSession, WorkSpaceSessionDao" in workspace_session
    assert "from zuno.platform.database.models.workspace_session import WorkSpaceSessionCreate" in workspace_session
    assert "from zuno.platform.common.model_output import strip_model_wrapper_from_user_input, strip_think_tags" in workspace_session
    assert "from zuno.platform.database.dao.user import UserDao" in user
    assert "from zuno.platform.database.dao.user_role import UserRoleDao" in user
    assert "from zuno.platform.database.models.role import AdminRole" in user
    assert "from zuno.platform.database.models.user import AdminUser, UserTable" in user
    assert "from zuno.platform.services.redis import redis_client" in user
    assert "from zuno.platform.services.storage import storage_client" in user
    assert "from zuno.api.dto.schemas import CreateUserReq" in user
    assert "from zuno.platform.common.JWT import ACCESS_TOKEN_EXPIRE_TIME" in user
    assert "from zuno.platform.common.constants import RSA_KEY" in user
    assert "from zuno.platform.common.hash import md5_hash" in user
    assert "from zuno.platform.common.runtime_observability import RedisKeys" in user
    assert "from zuno.platform.database import SystemUser, ToolTable" in tool
    assert "from zuno.api.dto.tool import (" in tool
    assert "from zuno.platform.database.dao.tool import ToolDao" in tool
    assert "from zuno.platform.database.models.user import AdminUser" in tool
    assert "from zuno.platform.services.cli_tool_discovery import CliToolDiscoveryService" in tool
    assert "from zuno.platform.services.simple_api_tool import (" in tool
    assert "from zuno.platform.services.tool_connectivity_service import ToolConnectivityService" in tool
    assert "from zuno.platform.services.tool_creation_service import ToolCreationService" in tool
    assert "from zuno.platform.services.user_defined_tool_runtime import (" in tool
    assert "from zuno.platform.common.file_utils import format_file_size" in knowledge
    assert "from zuno.platform.database import engine" in knowledge
    assert "from zuno.platform.database.dao.knowledge import KnowledgeDao" in knowledge
    assert "from zuno.platform.database.dao.knowledge_file import KnowledgeFileDao" in knowledge
    assert "from zuno.platform.database.dao.llm import LLMDao" in knowledge
    assert "from zuno.platform.database.models.user import AdminUser" in knowledge
    assert "from zuno.platform.services.runtime_registry import get_local_runtime_settings" in knowledge
    assert "from zuno.platform.services.graphrag.project.loader import GraphRAGProjectLoader" in knowledge
    assert "from zuno.platform.services.application.knowledge import KnowledgeQueryService" in knowledge
    assert "from zuno.api.dto.agent import AgentCreateReq" in agent
    assert "from zuno.platform.database import AgentTable" in agent
    assert "from zuno.platform.database.dao.agent import AgentDao" in agent
    assert "from zuno.platform.database.dao.dialog import DialogDao" in agent
    assert "from zuno.platform.database.models.user import AdminUser, SystemUser" in agent
    assert "from zuno.api.dto.chunk import ChunkModel" in history
    assert "from zuno.platform.common.helpers import get_now_beijing_time" in history
    assert "from zuno.platform.common.model_output import strip_model_wrapper_from_user_input" in history
    assert "from zuno.platform.database.dao.history import HistoryDao" in history
    assert "from zuno.platform.services.rag.es_client import client as es_client" in history
    assert "from zuno.platform.services.rag.vector_db import milvus_client" in history
    assert "from zuno.platform.common.model_output import normalize_model_id_for_provider" in llm
    assert "from zuno.platform.database.dao.llm import LLMDao" in llm
    assert "from zuno.platform.database.models.user import AdminUser, SystemUser" in llm
    assert "from zuno.api.dto.mcp import MCPResponseFormat" in mcp_server
    assert "from zuno.platform.common.convert import convert_mcp_config" in mcp_server
    assert "from zuno.platform.common.helpers import parse_imported_config" in mcp_server
    assert "from zuno.platform.database.dao.mcp_server import MCPServerDao" in mcp_server
    assert "from zuno.platform.database.models.user import AdminUser, SystemUser" in mcp_server
    assert "from zuno.platform.resources.prompts.mcp import McpAsToolPrompt" in mcp_server
    assert "from zuno.platform.services.mcp.manager import MCPManager" in mcp_server
    assert "from zuno.platform.database.dao.message import MessageDownDao, MessageLikeDao" in message
    assert "from zuno.platform.database.dao.dialog import DialogDao" in dialog
    assert "from zuno.platform.database.dao.history import HistoryDao" in dialog
    assert "from zuno.platform.database.models.user import AdminUser" in dialog
    assert "from zuno.platform.database.dao.message import MessageLikeDao" in message_events
    assert "from zuno.platform.database.dao.mcp_user_config import MCPUserConfigDao" in mcp_user_config
    assert "from zuno.platform.database.dao.mcp_stdio_server import MCPServerStdioDao" in mcp_stdio_server
    assert "from zuno.platform.database.models.user import AdminUser" in mcp_stdio_server
    assert "from zuno.platform.database.dao.usage_stats import UsageStats, UsageStatsDao" in usage_stats
    assert "from zuno.api.dto.schemas import resp_200, resp_500" in mcp_agent
    assert "from zuno.platform.database.dao.mcp_agent import MCPAgentDao" in mcp_agent
    assert "from zuno.platform.database.models.user import AdminUser, SystemUser" in mcp_agent
    assert "from zuno.platform.services.capability_registry import CapabilityRegistryService" in capability
    assert "from zuno.platform.database import engine" in capability
    assert "from zuno.agent.core.agents.structured_response_agent import StructuredResponseAgent" in agent_skill
    assert "from zuno.api.dto.agent_skill import (" in agent_skill
    assert "from zuno.platform.database.dao.agent_skill import AgentSkillDao" in agent_skill
    assert "from zuno.platform.database.models.agent_skill import AgentSkill" in agent_skill
    assert "from zuno.platform.resources.prompts.skill import AgentSkillAsToolPrompt" in agent_skill

    for content in [upload, knowledge_file, workspace_session, user, tool, knowledge, agent, history, llm, mcp_server, message, dialog, message_events, mcp_user_config, mcp_stdio_server, usage_stats, mcp_agent, capability, agent_skill]:
        assert "from zuno.services." not in content
        assert "from zuno.schema." not in content
        assert "from zuno.utils." not in content
        assert "from zuno.database" not in content
        assert "from zuno.core." not in content
        assert "from zuno.resources." not in content


def test_runtime_entrypoints_and_cross_module_dtos_use_canonical_imports() -> None:
    main = _read("src/backend/zuno/main.py")
    memory_feedback = _read("src/backend/zuno/memory/feedback_consumer.py")
    product_baseline = _read("src/backend/zuno/agent/product_baseline.py")
    workspace_task_runtime = _read("src/backend/zuno/api/services/workspace_task_runtime.py")
    knowledge_dto = _read("src/backend/zuno/api/dto/knowledge.py")

    assert "from zuno.platform.common.runtime_observability import configure_langsmith" in main
    assert "from zuno.platform.database.init_data import (" in main
    assert "from zuno.platform.database.models.memory_runtime import MemoryRawEventTable" in memory_feedback
    assert "from zuno.api.dto.workspace import WorkSpaceSimpleTask, WorkspaceOutputContract" in product_baseline
    assert "from zuno.api.dto.workspace import (" in workspace_task_runtime
    assert "from zuno.platform.services.graphrag.models import GraphRAGProjectContract" in knowledge_dto

    for content in [main, memory_feedback, product_baseline, workspace_task_runtime, knowledge_dto]:
        assert "from zuno.schema." not in content
        assert "from zuno.database." not in content
        assert "from zuno.services." not in content
        assert "from zuno.utils." not in content


def test_platform_tool_runtime_services_use_canonical_imports() -> None:
    cli_tool_discovery = _read("src/backend/zuno/platform/services/cli_tool_discovery.py")
    simple_api_tool = _read("src/backend/zuno/platform/services/simple_api_tool.py")
    tool_creation_service = _read("src/backend/zuno/platform/services/tool_creation_service.py")
    tool_connectivity_service = _read("src/backend/zuno/platform/services/tool_connectivity_service.py")
    user_defined_tool_runtime = _read("src/backend/zuno/platform/services/user_defined_tool_runtime.py")
    init_data = _read("src/backend/zuno/platform/database/init_data.py")
    mcp_manager = _read("src/backend/zuno/platform/services/mcp/manager.py")
    mcp_multi_client = _read("src/backend/zuno/platform/services/mcp/multi_client.py")
    mcp_load_tools = _read("src/backend/zuno/platform/services/mcp/load_mcp/tools.py")
    mcp_openai_manager = _read("src/backend/zuno/platform/services/mcp_openai/mcp_manager.py")
    mcp_openai_util = _read("src/backend/zuno/platform/services/mcp_openai/mcp_util.py")

    assert "from zuno.api.dto.tool import (" in cli_tool_discovery
    assert "from zuno.agent.core.models.manager import ModelManager" in simple_api_tool
    assert "from zuno.api.dto.tool import (" in simple_api_tool
    assert "from zuno.platform.common.model_output import normalize_messages_for_model, strip_think_tags" in simple_api_tool
    assert "from zuno.api.dto.tool import SimpleApiConfig" in tool_creation_service
    assert "from zuno.capability.tools.cli_tool.adapter import CLIToolAdapter" in tool_creation_service
    assert "from zuno.capability.tools.openapi_tool.adapter import OpenAPIToolAdapter" in tool_creation_service
    assert "from zuno.platform.database import ToolTable" in tool_creation_service
    assert "from zuno.platform.services.simple_api_tool import build_openapi_schema_from_simple_config" in tool_creation_service
    assert "from zuno.platform.services.user_defined_tool_runtime import build_stored_tool_auth_config" in tool_creation_service
    assert "from zuno.api.dto.tool import ToolConnectivityReq, ToolConnectivityResp" in tool_connectivity_service
    assert "from zuno.capability.tools.cli_tool.adapter import CLIToolAdapter" in tool_connectivity_service
    assert "from zuno.capability.tools.openapi_tool.adapter import OpenAPIToolAdapter" in tool_connectivity_service
    assert "from zuno.platform.database import ToolTable" in tool_connectivity_service
    assert "from zuno.platform.services.simple_api_tool import normalize_remote_api_auth_config" in tool_connectivity_service
    assert "from zuno.platform.services.tool_creation_service import ToolCreationService" in tool_connectivity_service
    assert "from zuno.platform.services.user_defined_tool_runtime import get_cli_config_from_auth_config, get_user_defined_runtime_type" in tool_connectivity_service
    assert "from zuno.platform.database import ToolTable" in user_defined_tool_runtime
    assert "from zuno.platform.services.simple_api_tool import normalize_remote_api_auth_config" in user_defined_tool_runtime
    assert "from zuno.capability.tools.cli_tool.adapter import CLIToolAdapter" in user_defined_tool_runtime
    assert "from zuno.capability.tools.openapi_tool.adapter import OpenAPIToolAdapter" in user_defined_tool_runtime
    assert "from zuno.platform.database import AgentTable, SystemUser, ToolTable, engine, ensure_database" in init_data
    assert "from zuno.platform.services.mcp.manager import MCPManager" in init_data
    assert "from zuno.platform.services.storage import storage_client" in init_data
    assert "from zuno.platform.common.convert import convert_mcp_config" in init_data
    assert "from zuno.platform.common.helpers import get_provider_from_model" in init_data
    assert "from zuno.platform.services.mcp.multi_client import MultiServerMCPClient" in mcp_manager
    assert "from zuno.api.dto.mcp import MCPBaseConfig" in mcp_manager
    assert "from zuno.platform.services.mcp.load_mcp.prompts import load_mcp_prompt" in mcp_multi_client
    assert "from zuno.platform.services.mcp.load_mcp.resources import load_mcp_resources" in mcp_multi_client
    assert "from zuno.platform.services.mcp.load_mcp.tools import load_mcp_tools" in mcp_multi_client
    assert "from zuno.platform.services.mcp.sessions import (" in mcp_multi_client
    assert "from zuno.platform.services.mcp.sessions import Connection, create_session" in mcp_load_tools
    assert "from zuno.platform.services.mcp_openai.mcp_client import MCPClient" in mcp_openai_manager
    assert "from zuno.platform.services.mcp_openai.mcp_util import MCPUtil" in mcp_openai_manager
    assert "from zuno.platform.services.mcp_openai.schema import FunctionTool" in mcp_openai_manager
    assert "from zuno.platform.services.mcp_openai.mcp_client import MCPClient" in mcp_openai_util
    assert "from zuno.platform.services.mcp_openai.schema import FunctionTool" in mcp_openai_util
    assert "from zuno.platform.services.mcp_openai.strict_schema import ensure_strict_json_schema" in mcp_openai_util

    for content in [cli_tool_discovery, simple_api_tool, tool_creation_service, tool_connectivity_service, user_defined_tool_runtime, init_data, mcp_manager, mcp_multi_client, mcp_load_tools, mcp_openai_manager, mcp_openai_util]:
        assert "from zuno.services." not in content
        assert "from zuno.schema." not in content
        assert "from zuno.utils." not in content
        assert "from zuno.database." not in content
        assert "from zuno.core." not in content
        assert "from zuno.tools." not in content


def test_agent_core_uses_canonical_imports() -> None:
    files = [
        "src/backend/zuno/agent/core/agents/codeact_agent.py",
        "src/backend/zuno/agent/core/agents/general_agent.py",
        "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
        "src/backend/zuno/agent/core/agents/react_agent.py",
        "src/backend/zuno/agent/core/agents/structured_response_agent.py",
        "src/backend/zuno/agent/core/callbacks/__init__.py",
        "src/backend/zuno/agent/core/callbacks/usage_metadata.py",
        "src/backend/zuno/agent/core/models/__init__.py",
        "src/backend/zuno/agent/core/models/manager.py",
        "src/backend/zuno/agent/core/models/usage_model.py",
    ]
    contents = {path: _read(path) for path in files}

    assert "from zuno.agent.core.models.manager import ModelManager" in contents["src/backend/zuno/agent/core/agents/codeact_agent.py"]
    assert "from zuno.platform.services.sandbox import PyodideSandbox" in contents["src/backend/zuno/agent/core/agents/codeact_agent.py"]
    assert "from zuno.agent.core.callbacks import usage_metadata_callback" in contents["src/backend/zuno/agent/core/agents/general_agent.py"]
    assert "from zuno.capability.tools import AgentToolsWithName" in contents["src/backend/zuno/agent/core/agents/general_agent.py"]
    assert "from zuno.platform.services.mcp.manager import MCPManager" in contents["src/backend/zuno/agent/core/agents/general_agent.py"]
    assert "from zuno.platform.services.user_defined_tool_runtime import build_user_defined_langchain_tools" in contents["src/backend/zuno/agent/core/agents/general_agent.py"]
    assert "from zuno.api.dto.completion import PlanToolFlow" in contents["src/backend/zuno/agent/core/agents/plan_execute_agent.py"]
    assert "from zuno.platform.resources.prompts.completion import DEFAULT_CALL_PROMPT" in contents["src/backend/zuno/agent/core/agents/react_agent.py"]
    assert "from zuno.agent.core.callbacks.usage_metadata import UsageMetadataCallbackHandler" in contents["src/backend/zuno/agent/core/callbacks/__init__.py"]
    assert "from zuno.platform.database import SystemUser" in contents["src/backend/zuno/agent/core/callbacks/usage_metadata.py"]
    assert "from zuno.agent.core.models.embedding import EmbeddingModel" in contents["src/backend/zuno/agent/core/models/__init__.py"]
    assert "from zuno.api.dto.common import ModelConfig" in contents["src/backend/zuno/agent/core/models/manager.py"]
    assert "from zuno.platform.database.dao.llm import LLMDao" in contents["src/backend/zuno/agent/core/models/manager.py"]
    assert "from zuno.platform.common.convert import convert_langchain_tool_calls" in contents["src/backend/zuno/agent/core/models/usage_model.py"]

    for content in contents.values():
        assert "from zuno.core." not in content
        assert "from zuno.services." not in content
        assert "from zuno.schema." not in content
        assert "from zuno.database" not in content
        assert "from zuno.resources." not in content
        assert "from zuno.utils." not in content
        assert "from zuno.tools" not in content
