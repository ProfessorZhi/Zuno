from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_public_backend_entrypoints_prefer_zuno():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    dockerfile = (REPO_ROOT / "infra/docker/Dockerfile").read_text(encoding="utf-8")
    start_script = (REPO_ROOT / "tools/scripts/start.py").read_text(encoding="utf-8")
    main_module = (
        REPO_ROOT / "src/backend/zuno/legacy/agentchat/main.py"
    ).read_text(encoding="utf-8")
    zuno_main = (REPO_ROOT / "src/backend/zuno/main.py").read_text(encoding="utf-8")

    assert "uvicorn zuno.main:app" in readme
    assert 'CMD ["uvicorn", "zuno.main:app"' in dockerfile
    assert '"zuno.main:app"' in start_script
    assert 'uvicorn.run("zuno.main:app"' in main_module
    assert "from zuno.api.router import router" in zuno_main
    assert "from zuno.api.JWT import Settings" in zuno_main
    assert "from zuno.middleware.trace_id_middleware import TraceIDMiddleware" in zuno_main
    assert "from agentchat.main import app" not in zuno_main


def test_core_runtime_and_agent_packages_prefer_local_zuno_exports():
    zuno_core_runtime_init = (
        REPO_ROOT / "src/backend/zuno/core/runtime/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_core_runtime = (
        REPO_ROOT / "src/backend/zuno/core/runtime/agent_runtime.py"
    ).read_text(encoding="utf-8")
    zuno_core_agents_init = (
        REPO_ROOT / "src/backend/zuno/core/agents/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_core_general_agent = (
        REPO_ROOT / "src/backend/zuno/core/agents/general_agent.py"
    ).read_text(encoding="utf-8")
    zuno_core_domain_graph = (
        REPO_ROOT / "src/backend/zuno/core/graphs/domain_qa_graph.py"
    ).read_text(encoding="utf-8")
    zuno_core_models_init = (
        REPO_ROOT / "src/backend/zuno/core/models/__init__.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.core.runtime.agent_runtime import AgentRuntime" in zuno_core_runtime_init
    assert "from zuno.core.graphs.domain_qa_graph import DomainQAGraph" in zuno_core_runtime
    assert "from zuno.core.graphs.multi_agent_supervisor_graph import MultiAgentSupervisorGraph" in zuno_core_runtime
    assert "from agentchat.core.runtime import *" not in zuno_core_runtime_init
    assert "from agentchat.core.runtime.agent_runtime import *" not in zuno_core_runtime

    assert "_EXPORT_TO_MODULE = {" in zuno_core_agents_init
    assert '"GeneralAgent": "general_agent"' in zuno_core_agents_init
    assert '"StructuredResponseAgent": "structured_response_agent"' in zuno_core_agents_init
    assert "from agentchat.core.agents import *" not in zuno_core_agents_init

    assert "from importlib import import_module" in zuno_core_general_agent
    assert '_AGENTCHAT_MODULE = "agentchat.core.agents.general_agent"' in zuno_core_general_agent
    assert "from agentchat.core.agents.general_agent import" not in zuno_core_general_agent

    assert "from zuno.core.graphs.states import DomainQAState" in zuno_core_domain_graph
    assert "from zuno.services.rag.handler import RagHandler" in zuno_core_domain_graph
    assert "class DomainQAGraph:" in zuno_core_domain_graph
    assert "from agentchat.core.graphs.domain_qa_graph import" not in zuno_core_domain_graph
    assert "from zuno.core.models.embedding import EmbeddingModel" in zuno_core_models_init
    assert "from zuno.core.models.manager import ModelManager" in zuno_core_models_init
    assert "from zuno.core.models.reason_model import ReasoningModel" in zuno_core_models_init
    assert "from agentchat.core.models import *" not in zuno_core_models_init


def test_top_level_zuno_packages_prefer_local_explicit_exports():
    zuno_root_init = (REPO_ROOT / "src/backend/zuno/__init__.py").read_text(encoding="utf-8")
    zuno_api_init = (REPO_ROOT / "src/backend/zuno/api/__init__.py").read_text(encoding="utf-8")
    zuno_core_init = (REPO_ROOT / "src/backend/zuno/core/__init__.py").read_text(encoding="utf-8")
    zuno_database_init = (REPO_ROOT / "src/backend/zuno/database/__init__.py").read_text(encoding="utf-8")

    assert "__all__: list[str] = []" in zuno_root_init
    assert "from agentchat import *" not in zuno_root_init

    assert "from zuno.api.JWT import Settings" in zuno_api_init
    assert "from zuno.api.router import router" in zuno_api_init
    assert "from agentchat.api import *" not in zuno_api_init

    assert "_EXPORT_TO_MODULE = {" in zuno_core_init
    assert '"GeneralAgent": ("agents", "GeneralAgent")' in zuno_core_init
    assert '"DomainQAGraph": ("graphs", "DomainQAGraph")' in zuno_core_init
    assert '"AgentRuntime": ("runtime", "AgentRuntime")' in zuno_core_init
    assert "from agentchat.core import *" not in zuno_core_init

    assert "from zuno.database.models.agent import AgentTable" in zuno_database_init
    assert "from zuno.database.models.user import SystemUser" in zuno_database_init
    assert "from zuno.database.models.tool import ToolTable" in zuno_database_init
    assert "from zuno.settings import app_settings" in zuno_database_init
    assert "from agentchat.database import *" not in zuno_database_init


def test_schema_utils_tools_and_support_packages_prefer_local_package_contracts():
    zuno_schema_init = (REPO_ROOT / "src/backend/zuno/schema/__init__.py").read_text(encoding="utf-8")
    zuno_utils_init = (REPO_ROOT / "src/backend/zuno/utils/__init__.py").read_text(encoding="utf-8")
    zuno_tools_init = (REPO_ROOT / "src/backend/zuno/tools/__init__.py").read_text(encoding="utf-8")
    zuno_cli_tool_init = (
        REPO_ROOT / "src/backend/zuno/tools/cli_tool/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_openapi_tool_init = (
        REPO_ROOT / "src/backend/zuno/tools/openapi_tool/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_send_email_tool_init = (
        REPO_ROOT / "src/backend/zuno/tools/send_email/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_image2text_tool_init = (
        REPO_ROOT / "src/backend/zuno/tools/image2text/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_text2image_tool_init = (
        REPO_ROOT / "src/backend/zuno/tools/text2image/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_text2image_tool_action = (
        REPO_ROOT / "src/backend/zuno/tools/text2image/action.py"
    ).read_text(encoding="utf-8")
    zuno_middleware_init = (
        REPO_ROOT / "src/backend/zuno/middleware/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_servers_init = (
        REPO_ROOT / "src/backend/zuno/mcp_servers/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_remote_proxy_init = (
        REPO_ROOT / "src/backend/zuno/mcp_servers/remote_proxy/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_prompts_init = (REPO_ROOT / "src/backend/zuno/prompts/__init__.py").read_text(encoding="utf-8")
    zuno_prompts_completion = (
        REPO_ROOT / "src/backend/zuno/prompts/completion.py"
    ).read_text(encoding="utf-8")
    zuno_prompts_mcp = (REPO_ROOT / "src/backend/zuno/prompts/mcp.py").read_text(encoding="utf-8")
    zuno_prompts_skill = (REPO_ROOT / "src/backend/zuno/prompts/skill.py").read_text(encoding="utf-8")
    zuno_utils_convert = (REPO_ROOT / "src/backend/zuno/utils/convert.py").read_text(encoding="utf-8")

    assert "from . import (" in zuno_schema_init
    assert "schemas" in zuno_schema_init
    assert "from agentchat.schema import *" not in zuno_schema_init

    assert "from . import (" in zuno_utils_init
    assert "runtime_observability" in zuno_utils_init
    assert "from agentchat.utils import *" not in zuno_utils_init

    assert "from . import cli_tool, image2text, openapi_tool, send_email, text2image" in zuno_tools_init
    assert "from agentchat.tools import *" not in zuno_tools_init

    assert "from . import adapter" in zuno_cli_tool_init
    assert "from agentchat.tools.cli_tool import *" not in zuno_cli_tool_init

    assert "from . import adapter" in zuno_openapi_tool_init
    assert "from agentchat.tools.openapi_tool import *" not in zuno_openapi_tool_init

    assert "from . import cli" in zuno_send_email_tool_init
    assert "from agentchat.tools.send_email import *" not in zuno_send_email_tool_init

    assert "from zuno.tools.image2text.action import _image_to_text, image_to_text" in zuno_image2text_tool_init
    assert "from agentchat.tools.image2text import *" not in zuno_image2text_tool_init

    assert "from zuno.tools.text2image.action import _text_to_image" in zuno_text2image_tool_init
    assert "from agentchat.tools.text2image import *" not in zuno_text2image_tool_init
    assert "from zuno.services.storage import storage_client" in zuno_text2image_tool_action
    assert "from zuno.settings import app_settings" in zuno_text2image_tool_action
    assert "from zuno.tools.image2text.action import _image_to_text" in zuno_text2image_tool_action
    assert "from agentchat.tools.text2image.action import" not in zuno_text2image_tool_action

    assert "from zuno.middleware.trace_id_middleware import TraceIDMiddleware" in zuno_middleware_init
    assert "from zuno.middleware.white_list_middleware import WhitelistMiddleware" in zuno_middleware_init
    assert "from agentchat.middleware import *" not in zuno_middleware_init

    assert "from . import remote_proxy" in zuno_mcp_servers_init
    assert "from agentchat.mcp_servers import *" not in zuno_mcp_servers_init

    assert "from . import main" in zuno_mcp_remote_proxy_init
    assert "from agentchat.mcp_servers.remote_proxy import *" not in zuno_mcp_remote_proxy_init

    assert "from . import completion, mcp, rewrite, skill" in zuno_prompts_init
    assert "from agentchat.prompts import *" not in zuno_prompts_init
    assert "GenerateTitlePrompt = " in zuno_prompts_completion
    assert "from agentchat.prompts.completion import" not in zuno_prompts_completion
    assert "McpAsToolPrompt = " in zuno_prompts_mcp
    assert "from agentchat.prompts.mcp import" not in zuno_prompts_mcp
    assert "AgentSkillAsToolPrompt = " in zuno_prompts_skill
    assert "from agentchat.prompts.skill import" not in zuno_prompts_skill
    assert "from zuno.schema.mcp import MCPSSEConfig, MCPWebsocketConfig, MCPStreamableHttpConfig, MCPStdioConfig" in zuno_utils_convert
    assert "def convert_mcp_config(" in zuno_utils_convert
    assert "from agentchat.utils.convert import" not in zuno_utils_convert


def test_services_packages_prefer_local_zuno_contracts():
    zuno_services_init = (REPO_ROOT / "src/backend/zuno/services/__init__.py").read_text(encoding="utf-8")
    zuno_memory_init = (REPO_ROOT / "src/backend/zuno/services/memory/__init__.py").read_text(encoding="utf-8")
    zuno_mcp_init = (REPO_ROOT / "src/backend/zuno/services/mcp/__init__.py").read_text(encoding="utf-8")
    zuno_mcp_multi_client = (
        REPO_ROOT / "src/backend/zuno/services/mcp/multi_client.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_sessions = (
        REPO_ROOT / "src/backend/zuno/services/mcp/sessions.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_load_tools = (
        REPO_ROOT / "src/backend/zuno/services/mcp/load_mcp/tools.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_openai_init = (
        REPO_ROOT / "src/backend/zuno/services/mcp_openai/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_workspace_init = (
        REPO_ROOT / "src/backend/zuno/services/workspace/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_queue_init = (REPO_ROOT / "src/backend/zuno/services/queue/__init__.py").read_text(encoding="utf-8")
    zuno_rag_init = (REPO_ROOT / "src/backend/zuno/services/rag/__init__.py").read_text(encoding="utf-8")
    zuno_retrieval_init = (
        REPO_ROOT / "src/backend/zuno/services/retrieval/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_graphrag_init = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/__init__.py"
    ).read_text(encoding="utf-8")

    assert "_SUBMODULES = {" in zuno_services_init
    assert '"workspace"' in zuno_services_init
    assert '"runtime_registry"' in zuno_services_init
    assert '"retrieval"' in zuno_services_init
    assert "def __getattr__(name: str):" in zuno_services_init
    assert "from agentchat.services import *" not in zuno_services_init

    assert "from . import client" in zuno_memory_init
    assert "from agentchat.services.memory import *" not in zuno_memory_init

    assert "from . import load_mcp, manager, multi_client, sessions" in zuno_mcp_init
    assert "from agentchat.services.mcp import *" not in zuno_mcp_init
    assert "from zuno.services.mcp.load_mcp.prompts import load_mcp_prompt" in zuno_mcp_multi_client
    assert "from zuno.services.mcp.load_mcp.resources import load_mcp_resources" in zuno_mcp_multi_client
    assert "from zuno.services.mcp.load_mcp.tools import load_mcp_tools" in zuno_mcp_multi_client
    assert "from zuno.services.mcp.sessions import (" in zuno_mcp_multi_client
    assert "from agentchat.services.mcp.multi_client import *" not in zuno_mcp_multi_client
    assert "from mcp import ClientSession, StdioServerParameters" in zuno_mcp_sessions
    assert "from agentchat.services.mcp.sessions import *" not in zuno_mcp_sessions
    assert "from zuno.services.mcp.sessions import Connection, create_session" in zuno_mcp_load_tools
    assert "from agentchat.services.mcp.load_mcp.tools import *" not in zuno_mcp_load_tools

    assert "from . import mcp_client, mcp_manager, mcp_util, schema, strict_schema" in zuno_mcp_openai_init
    assert "from agentchat.services.mcp_openai import *" not in zuno_mcp_openai_init

    assert "_MODULE_EXPORTS = {" in zuno_workspace_init
    assert '"attachment_service": "attachment_service"' in zuno_workspace_init
    assert '"simple_agent": "simple_agent"' in zuno_workspace_init
    assert '"wechat_agent": "wechat_agent"' in zuno_workspace_init
    assert "from agentchat.services.workspace import *" not in zuno_workspace_init

    assert "from . import client, messages, runner, workers" in zuno_queue_init
    assert "from agentchat.services.queue import *" not in zuno_queue_init

    assert "_SUBMODULES = {" in zuno_rag_init
    assert '"retrieval"' in zuno_rag_init
    assert "def __getattr__(name: str):" in zuno_rag_init
    assert "from agentchat.services.rag import *" not in zuno_rag_init
    assert "from zuno.services.retrieval.orchestrator import RetrievalOrchestrator" in zuno_retrieval_init
    assert "from agentchat.services.retrieval" not in zuno_retrieval_init
    assert "from zuno.services.graphrag.models import normalize_retrieval_mode" in zuno_graphrag_init
    assert "from agentchat.services.graphrag import *" not in zuno_graphrag_init


def test_high_value_service_modules_prefer_local_zuno_contracts():
    zuno_execution_policy = (
        REPO_ROOT / "src/backend/zuno/services/execution_policy.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_manager = (
        REPO_ROOT / "src/backend/zuno/services/mcp/manager.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_openai_manager = (
        REPO_ROOT / "src/backend/zuno/services/mcp_openai/mcp_manager.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_openai_client = (
        REPO_ROOT / "src/backend/zuno/services/mcp_openai/mcp_client.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_openai_util = (
        REPO_ROOT / "src/backend/zuno/services/mcp_openai/mcp_util.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_openai_schema = (
        REPO_ROOT / "src/backend/zuno/services/mcp_openai/schema.py"
    ).read_text(encoding="utf-8")
    zuno_mcp_openai_strict_schema = (
        REPO_ROOT / "src/backend/zuno/services/mcp_openai/strict_schema.py"
    ).read_text(encoding="utf-8")
    zuno_tool_creation_service = (
        REPO_ROOT / "src/backend/zuno/services/tool_creation_service.py"
    ).read_text(encoding="utf-8")
    zuno_tool_connectivity_service = (
        REPO_ROOT / "src/backend/zuno/services/tool_connectivity_service.py"
    ).read_text(encoding="utf-8")
    zuno_capability_registry = (
        REPO_ROOT / "src/backend/zuno/services/capability_registry.py"
    ).read_text(encoding="utf-8")
    zuno_rag_handler = (
        REPO_ROOT / "src/backend/zuno/services/rag/handler.py"
    ).read_text(encoding="utf-8")
    zuno_rag_rerank = (
        REPO_ROOT / "src/backend/zuno/services/rag/rerank.py"
    ).read_text(encoding="utf-8")
    zuno_model_manager = (
        REPO_ROOT / "src/backend/zuno/core/models/manager.py"
    ).read_text(encoding="utf-8")
    zuno_rag_retrieval = (
        REPO_ROOT / "src/backend/zuno/services/rag/retrieval.py"
    ).read_text(encoding="utf-8")
    zuno_retrieval_orchestrator = (
        REPO_ROOT / "src/backend/zuno/services/retrieval/orchestrator.py"
    ).read_text(encoding="utf-8")
    zuno_retrieval_planner = (
        REPO_ROOT / "src/backend/zuno/services/retrieval/planner.py"
    ).read_text(encoding="utf-8")
    zuno_retrieval_fusion = (
        REPO_ROOT / "src/backend/zuno/services/retrieval/fusion.py"
    ).read_text(encoding="utf-8")
    zuno_retrieval_retrievers = (
        REPO_ROOT / "src/backend/zuno/services/retrieval/retrievers.py"
    ).read_text(encoding="utf-8")
    zuno_rewrite_init = (
        REPO_ROOT / "src/backend/zuno/services/rewrite/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_rewrite_query_write = (
        REPO_ROOT / "src/backend/zuno/services/rewrite/query_write.py"
    ).read_text(encoding="utf-8")
    zuno_rewrite_markdown = (
        REPO_ROOT / "src/backend/zuno/services/rewrite/markdown_rewrite.py"
    ).read_text(encoding="utf-8")
    zuno_graphrag_models = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/models.py"
    ).read_text(encoding="utf-8")
    zuno_prompts_init = (
        REPO_ROOT / "src/backend/zuno/prompts/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_prompts_rewrite = (
        REPO_ROOT / "src/backend/zuno/prompts/rewrite.py"
    ).read_text(encoding="utf-8")

    assert "class ExecutionMode(str, Enum):" in zuno_execution_policy
    assert "class AccessScope(str, Enum):" in zuno_execution_policy
    assert "from agentchat.services.execution_policy import *" not in zuno_execution_policy

    assert "from zuno.schema.mcp import MCPBaseConfig" in zuno_mcp_manager
    assert "from zuno.services.mcp.multi_client import MultiServerMCPClient" in zuno_mcp_manager
    assert "class MCPManager:" in zuno_mcp_manager
    assert "from agentchat.services.mcp.manager import *" not in zuno_mcp_manager
    assert "from agentchat.services.mcp.multi_client import MultiServerMCPClient" not in zuno_mcp_manager

    assert "from zuno.core.models.anthropic import DeepAsyncAnthropic, DeepAnthropic" in zuno_mcp_openai_manager
    assert "from zuno.services.mcp_openai.mcp_client import MCPClient" in zuno_mcp_openai_manager
    assert "from zuno.services.mcp_openai.mcp_util import MCPUtil" in zuno_mcp_openai_manager
    assert "from zuno.services.mcp_openai.schema import FunctionTool" in zuno_mcp_openai_manager
    assert "class MCPManager:" in zuno_mcp_openai_manager
    assert "from agentchat.services.mcp_openai.mcp_manager import *" not in zuno_mcp_openai_manager
    assert "from agentchat.services.mcp_openai.mcp_client" not in zuno_mcp_openai_manager
    assert "from agentchat.services.mcp_openai.mcp_util" not in zuno_mcp_openai_manager
    assert "from agentchat.services.mcp_openai.schema" not in zuno_mcp_openai_manager
    assert "class MCPClient:" in zuno_mcp_openai_client
    assert "from zuno.services.mcp_openai.mcp_client import MCPClient" in zuno_mcp_openai_util
    assert "from zuno.services.mcp_openai.schema import FunctionTool" in zuno_mcp_openai_util
    assert "from zuno.services.mcp_openai.strict_schema import ensure_strict_json_schema" in zuno_mcp_openai_util
    assert "class MCPUtil:" in zuno_mcp_openai_util
    assert "class FunctionTool:" in zuno_mcp_openai_schema
    assert "def ensure_strict_json_schema(" in zuno_mcp_openai_strict_schema

    assert "from zuno.api.services.tool import ToolService" in zuno_tool_creation_service
    assert "from zuno.database import ToolTable" in zuno_tool_creation_service
    assert "from zuno.schema.tool import SimpleApiConfig" in zuno_tool_creation_service
    assert "from zuno.services.tool_creation_service import *" not in zuno_tool_creation_service

    assert "from zuno.database.models.tool import ToolTable" in zuno_tool_connectivity_service
    assert "from zuno.schema.tool import ToolConnectivityReq, ToolConnectivityResp" in zuno_tool_connectivity_service
    assert "from zuno.services.tool_creation_service import ToolCreationService" in zuno_tool_connectivity_service
    assert "from zuno.tools.cli_tool.adapter import CLIToolAdapter" in zuno_tool_connectivity_service
    assert "from zuno.tools.openapi_tool.adapter import OpenAPIToolAdapter" in zuno_tool_connectivity_service
    assert "from agentchat.services.tool_connectivity_service import *" not in zuno_tool_connectivity_service

    assert "from zuno.api.services.agent_skill import AgentSkillService" in zuno_capability_registry
    assert "from zuno.api.services.mcp_server import MCPService" in zuno_capability_registry
    assert "from zuno.api.services.tool import ToolService" in zuno_capability_registry
    assert "class CapabilityRegistryService:" in zuno_capability_registry
    assert "from agentchat.services.capability_registry" not in zuno_capability_registry
    assert "from zuno.services.graphrag.models import normalize_retrieval_mode" in zuno_rag_handler
    assert "from zuno.services.rag.rerank import Reranker" in zuno_rag_handler
    assert "from zuno.services.rag.retrieval import MixRetrival" in zuno_rag_handler
    assert "from zuno.services.rewrite.query_write import query_rewriter" in zuno_rag_handler
    assert "from zuno.services.retrieval.orchestrator import (" in zuno_rag_handler
    assert "RetrievalOrchestrator" in zuno_rag_handler
    assert "from agentchat.services.graphrag.models import normalize_retrieval_mode" not in zuno_rag_handler
    assert "from agentchat.services.rag.rerank import Reranker" not in zuno_rag_handler
    assert "from agentchat.services.rag.retrieval import MixRetrival" not in zuno_rag_handler
    assert "from agentchat.services.rewrite.query_write import query_rewriter" not in zuno_rag_handler
    assert "from agentchat.services.retrieval.orchestrator import RetrievalOrchestrator" not in zuno_rag_handler
    assert "from zuno.schema.rerank import RerankResultModel" in zuno_rag_rerank
    assert "from zuno.core.models.manager import ModelManager" in zuno_rag_rerank
    assert "from zuno.settings import app_settings, initialize_app_settings" in zuno_rag_rerank
    assert "from agentchat.services.rag.rerank import *" not in zuno_rag_rerank
    assert "from agentchat.core.models.manager import ModelManager" not in zuno_rag_rerank
    assert "from zuno.services.rag.es_client import client as es_client" in zuno_rag_retrieval
    assert "from zuno.services.rag.vector_db import milvus_client" in zuno_rag_retrieval
    assert "from agentchat.services.rag.retrieval import *" not in zuno_rag_retrieval
    assert "from zuno.services.graphrag.models import normalize_retrieval_mode" in zuno_retrieval_orchestrator
    assert "from zuno.services.retrieval.fusion import RetrievalFusion" in zuno_retrieval_orchestrator
    assert "from zuno.services.retrieval.planner import RetrievalPlanner" in zuno_retrieval_orchestrator
    assert "from zuno.services.retrieval.retrievers import (" in zuno_retrieval_orchestrator
    assert "from zuno.settings import app_settings" not in zuno_retrieval_orchestrator
    assert "from agentchat.services.retrieval.orchestrator import *" not in zuno_retrieval_orchestrator
    assert "from zuno.services.graphrag.models import normalize_retrieval_mode" in zuno_retrieval_planner
    assert "from zuno.services.retrieval.models import ProcessedQuery, RetrievalPlan, RetrievalRequest" in zuno_retrieval_planner
    assert "from zuno.services.retrieval.models import FusionResult, RetrievedDocument" in zuno_retrieval_fusion
    assert "from zuno.api.services.knowledge import KnowledgeService" in zuno_retrieval_retrievers
    assert "from zuno.services.graphrag.retriever import GraphRetriever" in zuno_retrieval_retrievers
    assert "from zuno.services.rag.retrieval import MixRetrival" in zuno_retrieval_retrievers
    assert "from zuno.settings import app_settings" in zuno_retrieval_retrievers
    assert "from zuno.services.rewrite.query_write import QueryRewrite, query_rewriter" in zuno_rewrite_init
    assert "from zuno.prompts.rewrite import system_query_rewrite, user_query_write" in zuno_rewrite_query_write
    assert "from zuno.core.models.manager import ModelManager" in zuno_rewrite_query_write
    assert "from agentchat.core.models.manager import ModelManager" not in zuno_rewrite_query_write
    assert "from zuno.core.models.manager import ModelManager" in zuno_rewrite_markdown
    assert "from agentchat.core.models.manager import ModelManager" not in zuno_rewrite_markdown
    assert "from . import completion, mcp, rewrite, skill" in zuno_prompts_init
    assert "user_query_write = " in zuno_prompts_rewrite
    assert "system_query_rewrite = " in zuno_prompts_rewrite
    assert 'RETRIEVAL_MODES = {"default", "rag", "graphrag", "hybrid", "rag_graph", "auto"}' in zuno_graphrag_models
    assert "def normalize_retrieval_mode(mode: str | None) -> str:" in zuno_graphrag_models

    zuno_memory_client = (
        REPO_ROOT / "src/backend/zuno/services/memory/client.py"
    ).read_text(encoding="utf-8")
    zuno_simple_api_tool = (
        REPO_ROOT / "src/backend/zuno/services/simple_api_tool.py"
    ).read_text(encoding="utf-8")
    zuno_user_defined_tool_runtime = (
        REPO_ROOT / "src/backend/zuno/services/user_defined_tool_runtime.py"
    ).read_text(encoding="utf-8")
    zuno_workspace_simple_agent = (
        REPO_ROOT / "src/backend/zuno/services/workspace/simple_agent.py"
    ).read_text(encoding="utf-8")
    zuno_workspace_attachment_service = (
        REPO_ROOT / "src/backend/zuno/services/workspace/attachment_service.py"
    ).read_text(encoding="utf-8")
    zuno_workspace_wechat_agent = (
        REPO_ROOT / "src/backend/zuno/services/workspace/wechat_agent.py"
    ).read_text(encoding="utf-8")
    zuno_cli_tool_discovery = (
        REPO_ROOT / "src/backend/zuno/services/cli_tool_discovery.py"
    ).read_text(encoding="utf-8")

    assert "from importlib import import_module" in zuno_memory_client
    assert '_AGENTCHAT_MODULE = "agentchat.services.memory.client"' in zuno_memory_client
    assert "memory_client" in zuno_memory_client
    assert "from agentchat.services.memory.client import" not in zuno_memory_client

    assert "from zuno.core.models.manager import ModelManager" in zuno_simple_api_tool
    assert "from zuno.schema.tool import (" in zuno_simple_api_tool
    assert "from zuno.utils.model_output import normalize_messages_for_model, strip_think_tags" in zuno_simple_api_tool
    assert "build_openapi_schema_from_simple_config" in zuno_simple_api_tool
    assert "build_remote_api_assist_draft_agentic" in zuno_simple_api_tool
    assert "from agentchat.services.simple_api_tool import *" not in zuno_simple_api_tool
    assert "from agentchat.services.simple_api_tool import (" not in zuno_simple_api_tool

    assert "from zuno.database import ToolTable" in zuno_user_defined_tool_runtime
    assert "from zuno.services.simple_api_tool import normalize_remote_api_auth_config" in zuno_user_defined_tool_runtime
    assert "from zuno.tools.cli_tool.adapter import CLIToolAdapter" in zuno_user_defined_tool_runtime
    assert "from zuno.tools.openapi_tool.adapter import OpenAPIToolAdapter" in zuno_user_defined_tool_runtime
    assert "def build_user_defined_langchain_tools(" in zuno_user_defined_tool_runtime
    assert "from agentchat.services.user_defined_tool_runtime" not in zuno_user_defined_tool_runtime

    assert "from importlib import import_module" in zuno_workspace_simple_agent
    assert '_AGENTCHAT_MODULE = "agentchat.services.workspace.simple_agent"' in zuno_workspace_simple_agent
    assert '__all__ = ["MCPConfig", "WorkSpaceSimpleAgent"]' in zuno_workspace_simple_agent
    assert "from agentchat.services.workspace.simple_agent import" not in zuno_workspace_simple_agent

    assert "from zuno.schema.workspace import WorkspaceAttachment" in zuno_workspace_attachment_service
    assert "from zuno.services.rag.parser import doc_parser" in zuno_workspace_attachment_service
    assert "from zuno.services.storage import storage_client" in zuno_workspace_attachment_service
    assert "from zuno.settings import app_settings" in zuno_workspace_attachment_service
    assert "from zuno.tools.image2text.action import _image_to_text" in zuno_workspace_attachment_service
    assert "build_workspace_attachment_prompt" in zuno_workspace_attachment_service
    assert "validate_workspace_attachments" in zuno_workspace_attachment_service
    assert "from agentchat.services.workspace.attachment_service import" not in zuno_workspace_attachment_service

    assert "from importlib import import_module" in zuno_workspace_wechat_agent
    assert '_AGENTCHAT_MODULE = "agentchat.services.workspace.wechat_agent"' in zuno_workspace_wechat_agent
    assert '__all__ = ["MCPConfig", "WeChatAgent"]' in zuno_workspace_wechat_agent
    assert "from agentchat.services.workspace.wechat_agent import" not in zuno_workspace_wechat_agent

    assert "from zuno.schema.tool import (" in zuno_cli_tool_discovery
    assert "class CliToolDiscoveryService:" in zuno_cli_tool_discovery
    assert "from agentchat.services.cli_tool_discovery import" not in zuno_cli_tool_discovery


def test_api_settings_and_schema_packages_prefer_local_zuno_contracts():
    zuno_jwt = (REPO_ROOT / "src/backend/zuno/api/JWT.py").read_text(encoding="utf-8")
    zuno_errcode_init = (
        REPO_ROOT / "src/backend/zuno/api/errcode/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_errcode_base = (
        REPO_ROOT / "src/backend/zuno/api/errcode/base.py"
    ).read_text(encoding="utf-8")
    zuno_errcode_user = (
        REPO_ROOT / "src/backend/zuno/api/errcode/user.py"
    ).read_text(encoding="utf-8")
    zuno_settings = (REPO_ROOT / "src/backend/zuno/settings.py").read_text(encoding="utf-8")
    zuno_schema_common = (
        REPO_ROOT / "src/backend/zuno/schema/common.py"
    ).read_text(encoding="utf-8")
    zuno_schema_schemas = (
        REPO_ROOT / "src/backend/zuno/schema/schemas.py"
    ).read_text(encoding="utf-8")

    assert "class Settings(BaseSettings):" in zuno_jwt
    assert "from agentchat.api.JWT import *" not in zuno_jwt

    assert "from zuno.api.errcode.base import BaseErrorCode, NotFoundError, UnAuthorizedError" in zuno_errcode_init
    assert "from zuno.api.errcode.user import (" in zuno_errcode_init
    assert "from agentchat.api.errcode import *" not in zuno_errcode_init

    assert "from zuno.schema.schemas import UnifiedResponseModel" in zuno_errcode_base
    assert "class BaseErrorCode:" in zuno_errcode_base
    assert "from agentchat.api.errcode.base import *" not in zuno_errcode_base

    assert "from zuno.api.errcode.base import BaseErrorCode" in zuno_errcode_user
    assert "class UserValidateError(BaseErrorCode):" in zuno_errcode_user
    assert "from agentchat.api.errcode.user import *" not in zuno_errcode_user

    assert "from zuno.schema.common import MultiModels, ModelConfig, Rag, StorageConfig, Tools" in zuno_settings
    assert "class Settings(BaseSettings):" in zuno_settings
    assert "resolve_app_config_path" in zuno_settings
    assert "from agentchat.settings import *" not in zuno_settings

    assert "class ModelConfig(BaseModel):" in zuno_schema_common
    assert "class StorageConfig(BaseModel):" in zuno_schema_common
    assert "from agentchat.schema.common import *" not in zuno_schema_common

    assert "class CreateUserReq(BaseModel):" in zuno_schema_schemas
    assert "class UnifiedResponseModel(BaseModel, Generic[DataT]):" in zuno_schema_schemas
    assert "def resp_200(" in zuno_schema_schemas
    assert "from agentchat.schema.schemas import *" not in zuno_schema_schemas


def test_high_value_schema_modules_prefer_local_zuno_contracts():
    zuno_schema_agent = (REPO_ROOT / "src/backend/zuno/schema/agent.py").read_text(encoding="utf-8")
    zuno_schema_agent_skill = (
        REPO_ROOT / "src/backend/zuno/schema/agent_skill.py"
    ).read_text(encoding="utf-8")
    zuno_schema_capability = (
        REPO_ROOT / "src/backend/zuno/schema/capability.py"
    ).read_text(encoding="utf-8")
    zuno_schema_chunk = (REPO_ROOT / "src/backend/zuno/schema/chunk.py").read_text(encoding="utf-8")
    zuno_schema_completion = (
        REPO_ROOT / "src/backend/zuno/schema/completion.py"
    ).read_text(encoding="utf-8")
    zuno_schema_dialog = (REPO_ROOT / "src/backend/zuno/schema/dialog.py").read_text(encoding="utf-8")
    zuno_schema_knowledge = (
        REPO_ROOT / "src/backend/zuno/schema/knowledge.py"
    ).read_text(encoding="utf-8")
    zuno_schema_llm = (REPO_ROOT / "src/backend/zuno/schema/llm.py").read_text(encoding="utf-8")
    zuno_schema_mcp = (REPO_ROOT / "src/backend/zuno/schema/mcp.py").read_text(encoding="utf-8")
    zuno_schema_mcp_user_config = (
        REPO_ROOT / "src/backend/zuno/schema/mcp_user_config.py"
    ).read_text(encoding="utf-8")
    zuno_schema_tool = (REPO_ROOT / "src/backend/zuno/schema/tool.py").read_text(encoding="utf-8")
    zuno_schema_usage_stats = (
        REPO_ROOT / "src/backend/zuno/schema/usage_stats.py"
    ).read_text(encoding="utf-8")
    zuno_schema_workspace = (
        REPO_ROOT / "src/backend/zuno/schema/workspace.py"
    ).read_text(encoding="utf-8")

    assert "class AgentCreateReq(BaseModel):" in zuno_schema_agent
    assert "from agentchat.schema.agent" not in zuno_schema_agent

    assert "class AgentSkillCreateReq(BaseModel):" in zuno_schema_agent_skill
    assert "from agentchat.schema.agent_skill" not in zuno_schema_agent_skill

    assert "class CapabilitySearchReq(BaseModel):" in zuno_schema_capability
    assert "from agentchat.schema.capability" not in zuno_schema_capability

    assert "class ChunkModel:" in zuno_schema_chunk
    assert "from agentchat.schema.chunk" not in zuno_schema_chunk

    assert "class CompletionReq(BaseModel):" in zuno_schema_completion
    assert "class PlanToolFlow(BaseModel):" in zuno_schema_completion
    assert "from agentchat.schema.completion" not in zuno_schema_completion

    assert "class DialogCreateRequest(BaseModel):" in zuno_schema_dialog
    assert "from agentchat.schema.dialog" not in zuno_schema_dialog

    assert "class KnowledgeConfig(BaseModel):" in zuno_schema_knowledge
    assert "class KnowledgeUpdateRequest(BaseModel):" in zuno_schema_knowledge
    assert "from agentchat.schema.knowledge" not in zuno_schema_knowledge

    assert "class LLMCreateReq(BaseModel):" in zuno_schema_llm
    assert "from agentchat.schema.llm" not in zuno_schema_llm

    assert "def _default_mcp_logo_url() -> str:" in zuno_schema_mcp
    assert "from zuno.settings import app_settings" in zuno_schema_mcp
    assert "class MCPServerImportedReq(BaseModel):" in zuno_schema_mcp
    assert "from agentchat.schema.mcp" not in zuno_schema_mcp

    assert "class MCPUserConfigCreateRequest(BaseModel):" in zuno_schema_mcp_user_config
    assert "from agentchat.schema.mcp_user_config" not in zuno_schema_mcp_user_config

    assert "class ToolCreateReq(BaseModel):" in zuno_schema_tool
    assert "class CLIToolPreviewResp(BaseModel):" in zuno_schema_tool
    assert "from agentchat.schema.tool" not in zuno_schema_tool

    assert "class UsageStatsRequest(BaseModel):" in zuno_schema_usage_stats
    assert "from agentchat.schema.usage_stats" not in zuno_schema_usage_stats

    assert "class WorkSpaceSimpleTask(BaseModel):" in zuno_schema_workspace
    assert "class WorkspaceAttachment(BaseModel):" in zuno_schema_workspace
    assert "from agentchat.schema.workspace" not in zuno_schema_workspace


def test_high_value_utils_modules_prefer_local_zuno_contracts():
    zuno_utils_init = (REPO_ROOT / "src/backend/zuno/utils/__init__.py").read_text(encoding="utf-8")
    zuno_utils_jwt = (REPO_ROOT / "src/backend/zuno/utils/JWT.py").read_text(encoding="utf-8")
    zuno_utils_constants = (
        REPO_ROOT / "src/backend/zuno/utils/constants.py"
    ).read_text(encoding="utf-8")
    zuno_utils_contexts = (
        REPO_ROOT / "src/backend/zuno/utils/contexts.py"
    ).read_text(encoding="utf-8")
    zuno_utils_date_utils = (
        REPO_ROOT / "src/backend/zuno/utils/date_utils.py"
    ).read_text(encoding="utf-8")
    zuno_utils_file_utils = (
        REPO_ROOT / "src/backend/zuno/utils/file_utils.py"
    ).read_text(encoding="utf-8")
    zuno_utils_hash = (REPO_ROOT / "src/backend/zuno/utils/hash.py").read_text(encoding="utf-8")
    zuno_utils_model_output = (
        REPO_ROOT / "src/backend/zuno/utils/model_output.py"
    ).read_text(encoding="utf-8")
    zuno_utils_runtime_observability = (
        REPO_ROOT / "src/backend/zuno/utils/runtime_observability.py"
    ).read_text(encoding="utf-8")

    assert "date_utils" in zuno_utils_init
    assert "from agentchat.utils import *" not in zuno_utils_init

    assert "ACCESS_TOKEN_EXPIRE_TIME = 86400" in zuno_utils_jwt
    assert "from agentchat.utils.JWT" not in zuno_utils_jwt

    assert 'RSA_KEY = "rsa_"' in zuno_utils_constants
    assert "from agentchat.utils.constants" not in zuno_utils_constants

    assert 'ContextVar("trace_id"' in zuno_utils_contexts
    assert "from agentchat.utils.contexts" not in zuno_utils_contexts

    assert 'pytz.timezone("Asia/Shanghai")' in zuno_utils_date_utils
    assert "from agentchat.utils.date_utils" not in zuno_utils_date_utils

    assert "from zuno.utils.date_utils import get_beijing_date_str" in zuno_utils_file_utils
    assert "def generate_unique_filename(file_name: str, file_suffix: str = None) -> str:" in zuno_utils_file_utils
    assert "from agentchat.utils.file_utils" not in zuno_utils_file_utils

    assert "def md5_hash(original_string: str):" in zuno_utils_hash
    assert "from agentchat.utils.hash" not in zuno_utils_hash

    assert "USER_INPUT_PATTERN = re.compile" in zuno_utils_model_output
    assert "def normalize_model_id_for_provider(" in zuno_utils_model_output
    assert "from agentchat.utils.model_output" not in zuno_utils_model_output

    assert "from zuno.settings import app_settings" in zuno_utils_runtime_observability
    assert "from zuno.utils.contexts import get_trace_id_context" in zuno_utils_runtime_observability
    assert "class RedisKeys:" in zuno_utils_runtime_observability
    assert "from agentchat.utils.runtime_observability" not in zuno_utils_runtime_observability


def test_database_session_and_metadata_prefer_local_zuno_contract():
    zuno_database_session = (
        REPO_ROOT / "src/backend/zuno/database/session.py"
    ).read_text(encoding="utf-8")
    zuno_database_metadata = (
        REPO_ROOT / "src/backend/zuno/database/metadata.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.database import async_engine, engine" in zuno_database_session
    assert "from agentchat.database.session import" not in zuno_database_session

    assert "from zuno.database import models as model_package" in zuno_database_metadata
    assert "metadata = SQLModel.metadata" in zuno_database_metadata
    assert "from agentchat.database.metadata import metadata" not in zuno_database_metadata


def test_database_models_package_prefers_explicit_zuno_bridge_exports():
    zuno_database_models_init = (
        REPO_ROOT / "src/backend/zuno/database/models/__init__.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.database.models.agent import AgentTable" in zuno_database_models_init
    assert "from zuno.database.models.base import SQLModelSerializable, orjson_dumps" in zuno_database_models_init
    assert "from zuno.database.models.user import AdminUser, SystemUser, UserTable" in zuno_database_models_init
    assert "from zuno.database.models.workspace_session import WorkSpaceSession, WorkSpaceSessionCreate" in zuno_database_models_init
    assert "from agentchat.database.models import *" not in zuno_database_models_init


def test_domain_pack_and_pipeline_packages_prefer_local_zuno_contract():
    zuno_domain_pack_init = (
        REPO_ROOT / "src/backend/zuno/services/domain_pack/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_domain_pack_loader = (
        REPO_ROOT / "src/backend/zuno/services/domain_pack/loader.py"
    ).read_text(encoding="utf-8")
    zuno_domain_pack_models = (
        REPO_ROOT / "src/backend/zuno/services/domain_pack/models.py"
    ).read_text(encoding="utf-8")
    zuno_domain_pack_registry = (
        REPO_ROOT / "src/backend/zuno/services/domain_pack/registry.py"
    ).read_text(encoding="utf-8")
    zuno_domain_pack_validators = (
        REPO_ROOT / "src/backend/zuno/services/domain_pack/validators.py"
    ).read_text(encoding="utf-8")
    zuno_pipeline_init = (
        REPO_ROOT / "src/backend/zuno/services/pipeline/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_pipeline_models = (
        REPO_ROOT / "src/backend/zuno/services/pipeline/models.py"
    ).read_text(encoding="utf-8")
    zuno_pipeline_stages = (
        REPO_ROOT / "src/backend/zuno/services/pipeline/stages.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.services.domain_pack.loader import DomainPackLoader" in zuno_domain_pack_init
    assert "from zuno.services.domain_pack.models import DomainPack" in zuno_domain_pack_init
    assert "from zuno.services.domain_pack.registry import DomainPackRegistry" in zuno_domain_pack_init
    assert "from zuno.services.domain_pack.validators import DomainPackValidator" in zuno_domain_pack_init
    assert "from agentchat.services.domain_pack import *" not in zuno_domain_pack_init

    assert "from zuno.services.domain_pack.models import DomainPack" in zuno_domain_pack_loader
    assert "from zuno.services.domain_pack.validators import DomainPackValidator" in zuno_domain_pack_loader
    assert "from agentchat.services.domain_pack.loader import *" not in zuno_domain_pack_loader

    assert "@dataclass(slots=True)" in zuno_domain_pack_models
    assert "class DomainPack:" in zuno_domain_pack_models
    assert "from agentchat.services.domain_pack.models import *" not in zuno_domain_pack_models

    assert "from zuno.services.domain_pack.loader import DomainPackLoader" in zuno_domain_pack_registry
    assert "from agentchat.services.domain_pack.registry import *" not in zuno_domain_pack_registry

    assert "from zuno.services.domain_pack.models import DomainPack" in zuno_domain_pack_validators
    assert "from agentchat.services.domain_pack.validators import *" not in zuno_domain_pack_validators

    assert "from zuno.services.pipeline.models import KnowledgeTaskStage, KnowledgeTaskStatus, PIPELINE_STAGES" in zuno_pipeline_init
    assert "from zuno.services.pipeline.stages import (" in zuno_pipeline_init
    assert "from agentchat.services.pipeline import *" not in zuno_pipeline_init

    assert "class KnowledgeTaskStatus:" in zuno_pipeline_models
    assert "class KnowledgeTaskStage:" in zuno_pipeline_models
    assert "from agentchat.services.pipeline.models import *" not in zuno_pipeline_models

    assert "from zuno.database.models.knowledge_file import Status as KnowledgeFileStatus" in zuno_pipeline_stages
    assert "from zuno.services.pipeline.models import KnowledgeTaskStage" in zuno_pipeline_stages
    assert "from agentchat.services.pipeline.stages import *" not in zuno_pipeline_stages


def test_graphrag_packages_prefer_local_zuno_contract():
    zuno_graphrag_init = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_graphrag_extractors_init = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/extractors/__init__.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.services.graphrag.client import Neo4jClient" in zuno_graphrag_init
    assert "from zuno.services.graphrag.graph_store.graph_writer import GraphWriter" in zuno_graphrag_init
    assert "from zuno.services.graphrag.retriever import GraphRetriever" in zuno_graphrag_init
    assert "from agentchat.services.graphrag import *" not in zuno_graphrag_init

    assert "from zuno.services.graphrag.extractors.cached_extractor import CachedGraphExtractor" in zuno_graphrag_extractors_init
    assert "from zuno.services.graphrag.extractors.structured_extractor import StructuredGraphExtractor" in zuno_graphrag_extractors_init
    assert "from agentchat.services.graphrag.extractors import *" not in zuno_graphrag_extractors_init


def test_small_bridge_modules_are_localized_under_zuno():
    small_bridge_modules = {
        "src/backend/zuno/api/services/mineru.py": [
            "def convert_pdf_to_markdown(",
            "from magic_pdf.tools.common import do_parse",
        ],
        "src/backend/zuno/tools/cli_tool/adapter.py": [
            "class CLIToolAdapter:",
        ],
        "src/backend/zuno/tools/openapi_tool/adapter.py": [
            "class OpenAPIToolAdapter:",
        ],
        "src/backend/zuno/tools/send_email/cli.py": [
            "from zuno.settings import initialize_app_settings, resolve_app_config_path",
            "from zuno.tools.send_email import action as email_action",
        ],
        "src/backend/zuno/utils/helpers.py": [
            "from zuno.settings import app_settings",
            "class ImportedConfigInfo(BaseModel):",
        ],
    }

    for relative_path, required_snippets in small_bridge_modules.items():
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "from agentchat" not in content, relative_path
        assert "import agentchat" not in content, relative_path
        for snippet in required_snippets:
            assert snippet in content, (relative_path, snippet)


def test_rag_vector_store_modules_are_localized_under_zuno():
    localized_modules = {
        "src/backend/zuno/services/rag/embedding.py": [
            "from zuno.core.models.manager import ModelManager",
            "async def get_embedding(",
        ],
        "src/backend/zuno/services/rag/vl_embedding.py": [
            "from zuno.core.models.manager import ModelManager",
            "from zuno.services.storage import storage_client",
            "async def get_vl_text_embedding(",
        ],
        "src/backend/zuno/services/rag/vector_db/chroma_client.py": [
            "from zuno.schema.search import SearchModel",
            "from zuno.services.rag.embedding import get_embedding",
        ],
        "src/backend/zuno/services/rag/vector_db/milvus_client.py": [
            "from zuno.services.rag.vector_db.milvus_lite_client import MilvusLiteClient",
        ],
        "src/backend/zuno/services/rag/vector_db/milvus_lite_client.py": [
            "from zuno.schema.search import SearchModel",
            "from zuno.services.rag.vl_embedding import get_vl_image_embedding, get_vl_text_embedding",
            "from zuno.settings import app_settings",
        ],
    }

    for relative_path, required_snippets in localized_modules.items():
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "from agentchat" not in content, relative_path
        assert "import agentchat" not in content, relative_path
        for snippet in required_snippets:
            assert snippet in content, (relative_path, snippet)


def test_optional_mineru_service_is_implemented_locally():
    zuno_mineru_service = (
        REPO_ROOT / "src/backend/zuno/api/services/mineru.py"
    ).read_text(encoding="utf-8")

    assert "from magic_pdf.tools.common import do_parse" in zuno_mineru_service
    assert "def convert_pdf_to_markdown(path, output_dir, method=\"auto\", lang=None, debug_able=False, start_page_id=0, end_page_id=None):" in zuno_mineru_service
    assert "from agentchat.api.services.mineru import *" not in zuno_mineru_service


def test_public_worker_entrypoints_and_manifest_prefer_zuno():
    compose = (REPO_ROOT / "infra/docker/docker-compose.yml").read_text(encoding="utf-8")
    compose_dev = (REPO_ROOT / "infra/docker/docker-compose.dev.yml").read_text(encoding="utf-8")
    docker_readme = (REPO_ROOT / "infra/docker/README.md").read_text(encoding="utf-8")
    mcp_config = (
        REPO_ROOT / "src/backend/zuno/legacy/agentchat/config/mcp_server.json"
    ).read_text(encoding="utf-8")
    manifest = (
        REPO_ROOT / "src/backend/zuno/legacy/agentchat/tools/send_email/manifest.yaml"
    ).read_text(encoding="utf-8")
    settings_py = (
        REPO_ROOT / "src/backend/zuno/legacy/agentchat/settings.py"
    ).read_text(encoding="utf-8")
    zuno_queue_runner = (REPO_ROOT / "src/backend/zuno/services/queue/runner.py").read_text(encoding="utf-8")
    zuno_queue_workers = (REPO_ROOT / "src/backend/zuno/services/queue/workers.py").read_text(encoding="utf-8")
    zuno_queue_client = (REPO_ROOT / "src/backend/zuno/services/queue/client.py").read_text(encoding="utf-8")
    zuno_queue_messages = (
        REPO_ROOT / "src/backend/zuno/services/queue/messages.py"
    ).read_text(encoding="utf-8")
    zuno_rag_handler = (
        REPO_ROOT / "src/backend/zuno/services/rag/handler.py"
    ).read_text(encoding="utf-8")
    zuno_model_manager = (
        REPO_ROOT / "src/backend/zuno/core/models/manager.py"
    ).read_text(encoding="utf-8")
    zuno_vector_db = (
        REPO_ROOT / "src/backend/zuno/services/rag/vector_db/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_graph_retriever = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/retriever.py"
    ).read_text(encoding="utf-8")
    zuno_graph_extractor = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/extractor.py"
    ).read_text(encoding="utf-8")
    zuno_structured_extractor = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/extractors/structured_extractor.py"
    ).read_text(encoding="utf-8")
    zuno_cached_extractor = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/extractors/cached_extractor.py"
    ).read_text(encoding="utf-8")
    zuno_graph_client = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/client.py"
    ).read_text(encoding="utf-8")
    zuno_graph_writer = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/graph_store/graph_writer.py"
    ).read_text(encoding="utf-8")
    zuno_rag_es_client = (
        REPO_ROOT / "src/backend/zuno/services/rag/es_client.py"
    ).read_text(encoding="utf-8")
    zuno_convert_files_init = (
        REPO_ROOT / "src/backend/zuno/services/convert_files/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_convert_pdf = (
        REPO_ROOT / "src/backend/zuno/services/convert_files/convert_pdf.py"
    ).read_text(encoding="utf-8")
    zuno_rag_docx_parser = (
        REPO_ROOT / "src/backend/zuno/services/rag/doc_parser/docx.py"
    ).read_text(encoding="utf-8")
    zuno_rag_pdf_parser = (
        REPO_ROOT / "src/backend/zuno/services/rag/doc_parser/pdf.py"
    ).read_text(encoding="utf-8")
    zuno_rag_pptx_parser = (
        REPO_ROOT / "src/backend/zuno/services/rag/doc_parser/pptx.py"
    ).read_text(encoding="utf-8")
    zuno_rag_image_parser = (
        REPO_ROOT / "src/backend/zuno/services/rag/doc_parser/image.py"
    ).read_text(encoding="utf-8")
    zuno_rag_parser = (
        REPO_ROOT / "src/backend/zuno/services/rag/parser.py"
    ).read_text(encoding="utf-8")
    zuno_rewrite_markdown = (
        REPO_ROOT / "src/backend/zuno/services/rewrite/markdown_rewrite.py"
    ).read_text(encoding="utf-8")
    zuno_redis = (REPO_ROOT / "src/backend/zuno/services/redis.py").read_text(encoding="utf-8")
    zuno_storage_init = (
        REPO_ROOT / "src/backend/zuno/services/storage/__init__.py"
    ).read_text(encoding="utf-8")
    zuno_storage_minio = (
        REPO_ROOT / "src/backend/zuno/services/storage/minio.py"
    ).read_text(encoding="utf-8")
    zuno_storage_oss = (
        REPO_ROOT / "src/backend/zuno/services/storage/oss.py"
    ).read_text(encoding="utf-8")
    zuno_pipeline_manager = (
        REPO_ROOT / "src/backend/zuno/services/pipeline/manager.py"
    ).read_text(encoding="utf-8")
    zuno_main = (REPO_ROOT / "src/backend/zuno/main.py").read_text(encoding="utf-8")

    assert 'command: ["python", "-m", "zuno.services.queue.runner"]' in compose
    assert "ZUNO_CONFIG: /app/zuno/config.yaml" in compose
    assert "ZUNO_CONFIG: /app/zuno/config.yaml" in compose_dev
    assert "ZUNO_CONFIG: /app/zuno/config.yaml" in docker_readme
    assert "module: zuno.tools.send_email.cli" in manifest
    assert 'os.getenv("ZUNO_CONFIG") or os.getenv("AGENTCHAT_CONFIG")' in settings_py
    assert 'Path("zuno/config.yaml")' in settings_py
    assert '"/app/zuno/config.yaml"' in settings_py
    assert "zuno/mcp_servers/remote_proxy/main.py" in mcp_config
    assert "from zuno.database.init_data import init_database" in zuno_queue_runner
    assert "from zuno.database.init_data import (" in zuno_main
    assert "from zuno.services.pipeline.manager import KnowledgePipelineManager" in zuno_queue_runner
    assert "from zuno.services.queue.client import QueueClient, get_queue_names" in zuno_queue_runner
    assert "from zuno.services.queue.workers import GraphWorker, IndexWorker, ParseWorker" in zuno_queue_runner
    assert "from zuno.services.pipeline.models import KnowledgeTaskStage" in zuno_queue_workers
    assert "from zuno.services.queue.client import get_queue_names" in zuno_queue_workers
    assert "from zuno.services.queue.messages import build_task_message" in zuno_queue_workers
    assert "from zuno.settings import app_settings" in zuno_queue_client
    assert "from zuno.services.pipeline.models import KnowledgeTaskStage" in zuno_queue_messages
    assert "from zuno.api.services.knowledge import KnowledgeService" in zuno_rag_handler
    assert "from zuno.settings import app_settings" in zuno_rag_handler
    assert "from zuno.services.rag.es_client import client as es_client" in zuno_rag_handler
    assert "from zuno.services.rag.vector_db import milvus_client" in zuno_rag_handler
    assert "class RagHandler:" in zuno_rag_handler
    assert "from agentchat.services.rag.handler import RagHandler" not in zuno_rag_handler
    assert "from zuno.core.models.embedding import EmbeddingModel" in zuno_model_manager
    assert "from zuno.core.models.reason_model import ReasoningModel" in zuno_model_manager
    assert "from zuno.database.dao.llm import LLMDao" in zuno_model_manager
    assert "from zuno.schema.common import ModelConfig" in zuno_model_manager
    assert "from zuno.settings import app_settings" in zuno_model_manager
    assert "from zuno.utils.model_output import normalize_model_id_for_provider" in zuno_model_manager
    assert "class ModelManager:" in zuno_model_manager
    assert "from agentchat.core.models.manager import *" not in zuno_model_manager
    assert "from zuno.services.convert_files.convert_pdf import convert_to_pdf, get_libreoffice_command" in zuno_convert_files_init
    assert "def convert_to_pdf(input_path):" in zuno_convert_pdf
    assert "def get_libreoffice_command():" in zuno_convert_pdf
    assert "from agentchat.services.convert_files.convert_pdf import *" not in zuno_convert_pdf
    assert "from zuno.config.es_index import ESIndex" in zuno_rag_es_client
    assert "from zuno.schema.chunk import ChunkModel" in zuno_rag_es_client
    assert "from zuno.schema.search import SearchModel" in zuno_rag_es_client
    assert "from zuno.settings import app_settings" in zuno_rag_es_client
    assert "class ESClient:" in zuno_rag_es_client
    assert "from agentchat.services.rag.es_client import client" not in zuno_rag_es_client
    assert "from zuno.settings import app_settings" in zuno_vector_db
    assert "LazyVectorStoreClient" in zuno_vector_db
    assert "from zuno.services.graphrag.client import Neo4jClient" in zuno_graph_retriever
    assert "from zuno.services.rag.vector_db import milvus_client" in zuno_graph_retriever
    assert "class GraphRetriever:" in zuno_graph_retriever
    assert "from agentchat.services.graphrag.retriever" not in zuno_graph_retriever
    assert "class GraphExtractor:" in zuno_graph_extractor
    assert "async def extract_from_chunk(self, chunk: dict, knowledge_id: str) -> dict:" in zuno_graph_extractor
    assert "from agentchat.services.graphrag.extractor import GraphExtractor" not in zuno_graph_extractor
    assert "from zuno.services.graphrag.extractor import GraphExtractor" in zuno_structured_extractor
    assert "class StructuredGraphExtractor(GraphExtractor):" in zuno_structured_extractor
    assert "from agentchat.services.graphrag.extractors.structured_extractor" not in zuno_structured_extractor
    assert "from zuno.services.graphrag.extractors.structured_extractor import StructuredGraphExtractor" in zuno_cached_extractor
    assert "class CachedGraphExtractor:" in zuno_cached_extractor
    assert "from agentchat.services.graphrag.extractors.cached_extractor" not in zuno_cached_extractor
    assert "from zuno.settings import app_settings" in zuno_graph_client
    assert "class Neo4jClient:" in zuno_graph_client
    assert "from agentchat.services.graphrag.client" not in zuno_graph_client
    assert "class GraphWriter:" in zuno_graph_writer
    assert "def build_entity_payload(" in zuno_graph_writer
    assert "from agentchat.services.graphrag.graph_store.graph_writer" not in zuno_graph_writer
    assert "class DocParser:" in zuno_rag_parser
    assert "doc_parser = DocParser()" in zuno_rag_parser
    assert "from zuno.services.rag.doc_parser.chunk_ids import build_chunk_id" in zuno_rag_parser
    assert "from zuno.services.rag.doc_parser.excel import excel_to_txt" in zuno_rag_parser
    assert "from zuno.services.rag.doc_parser.image import build_image_chunk, describe_image" in zuno_rag_parser
    assert "from zuno.services.rag.doc_parser.markdown import markdown_parser" in zuno_rag_parser
    assert "from zuno.services.rag.doc_parser.docx import docx_parser" in zuno_rag_parser
    assert "from zuno.services.rag.doc_parser.other_file import other_file_to_txt" in zuno_rag_parser
    assert "from zuno.services.rag.doc_parser.pdf import pdf_parser" in zuno_rag_parser
    assert "from zuno.services.rag.doc_parser.pptx import pptx_parser" in zuno_rag_parser
    assert "from zuno.services.rag.doc_parser.text import text_parser" in zuno_rag_parser
    assert "from zuno.core.models.manager import ModelManager" in zuno_rag_parser
    assert "from agentchat.services.rag.parser import DocParser" not in zuno_rag_parser
    assert "from agentchat.core.models.manager import ModelManager" not in zuno_rag_parser
    assert "from zuno.services.convert_files.convert_pdf import convert_to_pdf" in zuno_rag_docx_parser
    assert "from agentchat.services.convert_files.convert_pdf import convert_to_pdf" not in zuno_rag_docx_parser
    assert "from zuno.services.convert_files.convert_pdf import convert_to_pdf" in zuno_rag_pptx_parser
    assert "from agentchat.services.convert_files.convert_pdf import convert_to_pdf" not in zuno_rag_pptx_parser
    assert "from zuno.services.rag.doc_parser.image import build_image_chunk" in zuno_rag_pdf_parser
    assert "from zuno.services.rag.doc_parser.markdown import markdown_parser" in zuno_rag_pdf_parser
    assert "from zuno.services.rewrite.markdown_rewrite import markdown_rewriter" in zuno_rag_pdf_parser
    assert "from zuno.services.rag.doc_parser.text import text_parser" in zuno_rag_pdf_parser
    assert "from zuno.services.storage import storage_client" in zuno_rag_pdf_parser
    assert "from zuno.utils.file_utils import (" in zuno_rag_pdf_parser
    assert "class PDFParser:" in zuno_rag_pdf_parser
    assert "from agentchat.services.rag.doc_parser.pdf" not in zuno_rag_pdf_parser
    assert "from agentchat.services.rewrite.markdown_rewrite" not in zuno_rag_pdf_parser
    assert "from zuno.core.models.manager import ModelManager" in zuno_rag_image_parser
    assert "from agentchat.core.models.manager import ModelManager" not in zuno_rag_image_parser
    assert "class RedisClient:" in zuno_redis
    assert "from zuno.settings import app_settings" in zuno_redis
    assert "from agentchat.services.redis import RedisClient as AgentchatRedisClient" not in zuno_redis
    assert "from zuno.settings import app_settings" in zuno_storage_init
    assert "class MinioClient:" in zuno_storage_minio
    assert "from zuno.settings import app_settings" in zuno_storage_minio
    assert "from agentchat.services.storage.minio import MinioClient as AgentchatMinioClient" not in zuno_storage_minio
    assert "class OSSClient:" in zuno_storage_oss
    assert "from zuno.settings import app_settings" in zuno_storage_oss
    assert "from agentchat.services.storage.oss import OSSClient as AgentchatOSSClient" not in zuno_storage_oss
    assert "from zuno.api.services.knowledge import KnowledgeService" in zuno_pipeline_manager
    assert "from zuno.database.dao.knowledge_file import KnowledgeFileDao" in zuno_pipeline_manager
    assert "from zuno.database.dao.knowledge_task import KnowledgeTaskDao" in zuno_pipeline_manager
    assert "from zuno.services.rag.handler import RagHandler" in zuno_pipeline_manager
    assert "from zuno.services.storage import storage_client" in zuno_pipeline_manager
    assert "from zuno.services.graphrag.client import Neo4jClient" in zuno_pipeline_manager
    assert "from zuno.services.graphrag.extractors.cached_extractor import CachedGraphExtractor" in zuno_pipeline_manager
    assert "from zuno.services.graphrag.graph_store.graph_writer import GraphWriter" in zuno_pipeline_manager
    assert "from zuno.services.rag.parser import doc_parser" in zuno_pipeline_manager
    assert "from zuno.services.redis import redis_client" in zuno_pipeline_manager
    assert "from zuno.utils.file_utils import get_object_key_from_public_url, get_save_tempfile" in zuno_pipeline_manager
    assert "from zuno.utils.runtime_observability import RedisKeys" in zuno_pipeline_manager


def test_high_value_knowledge_api_prefers_zuno():
    zuno_api_service_knowledge = (
        REPO_ROOT / "src/backend/zuno/api/services/knowledge.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_knowledge = (
        REPO_ROOT / "src/backend/zuno/api/v1/knowledge.py"
    ).read_text(encoding="utf-8")
    zuno_dao_knowledge = (
        REPO_ROOT / "src/backend/zuno/database/dao/knowledge.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.database.dao.knowledge import KnowledgeDao" in zuno_api_service_knowledge
    assert "from zuno.database.dao.knowledge_file import KnowledgeFileDao" in zuno_api_service_knowledge
    assert "from zuno.database.dao.llm import LLMDao" in zuno_api_service_knowledge
    assert "from zuno.services.domain_pack.loader import DomainPackLoader" in zuno_api_service_knowledge
    assert "from zuno.services.rag.handler import RagHandler" in zuno_api_service_knowledge
    assert "from zuno.services.runtime_registry import get_local_runtime_settings" in zuno_api_service_knowledge
    assert "from zuno.utils.file_utils import format_file_size" in zuno_api_service_knowledge
    assert "class KnowledgeService:" in zuno_api_service_knowledge
    assert "from zuno.api.services.knowledge import KnowledgeService" in zuno_api_v1_knowledge
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_knowledge
    assert "from zuno.services.rag.handler import RagHandler" not in zuno_api_v1_knowledge
    assert "from agentchat.api.v1.knowledge import *" not in zuno_api_v1_knowledge
    assert "from zuno.database.models.knowledge import KnowledgeTable" in zuno_dao_knowledge
    assert "from zuno.database.session import session_getter" in zuno_dao_knowledge
    assert "from agentchat.database.dao.knowledge import *" not in zuno_dao_knowledge


def test_high_value_knowledge_file_api_prefers_zuno():
    zuno_api_service_knowledge_file = (
        REPO_ROOT / "src/backend/zuno/api/services/knowledge_file.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_knowledge_file = (
        REPO_ROOT / "src/backend/zuno/api/v1/knowledge_file.py"
    ).read_text(encoding="utf-8")
    zuno_dao_knowledge_file = (
        REPO_ROOT / "src/backend/zuno/database/dao/knowledge_file.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.api.services.knowledge import KnowledgeService" in zuno_api_service_knowledge_file
    assert "from zuno.database.dao.knowledge_file import KnowledgeFileDao" in zuno_api_service_knowledge_file
    assert "from zuno.database.dao.knowledge_task import KnowledgeTaskDao" in zuno_api_service_knowledge_file
    assert "from zuno.services.pipeline.manager import KnowledgePipelineManager" in zuno_api_service_knowledge_file
    assert "from zuno.services.queue.client import QueueClient, get_queue_names" in zuno_api_service_knowledge_file
    assert "from zuno.services.queue.messages import build_task_message" in zuno_api_service_knowledge_file
    assert "from zuno.services.storage import storage_client" in zuno_api_service_knowledge_file
    assert "from zuno.utils.file_utils import get_object_key_from_public_url, get_save_tempfile" in zuno_api_service_knowledge_file
    assert "class KnowledgeFileService:" in zuno_api_service_knowledge_file
    assert "from zuno.api.services.knowledge import KnowledgeService" in zuno_api_v1_knowledge_file
    assert "from zuno.api.services.knowledge_file import KnowledgeFileService" in zuno_api_v1_knowledge_file
    assert "from zuno.services.storage import storage_client" not in zuno_api_v1_knowledge_file
    assert "from zuno.utils.file_utils import get_object_key_from_public_url, get_save_tempfile" not in zuno_api_v1_knowledge_file
    assert "from agentchat.api.v1.knowledge_file import *" not in zuno_api_v1_knowledge_file
    assert "from zuno.database.models.knowledge_file import KnowledgeFileTable" in zuno_dao_knowledge_file
    assert "from zuno.database.session import session_getter" in zuno_dao_knowledge_file
    assert "from agentchat.database.dao.knowledge_file import *" not in zuno_dao_knowledge_file


def test_high_value_workspace_session_service_prefers_zuno():
    zuno_api_service_workspace_session = (
        REPO_ROOT / "src/backend/zuno/api/services/workspace_session.py"
    ).read_text(encoding="utf-8")
    zuno_dao_workspace_session = (
        REPO_ROOT / "src/backend/zuno/database/dao/workspace_session.py"
    ).read_text(encoding="utf-8")
    zuno_model_workspace_session = (
        REPO_ROOT / "src/backend/zuno/database/models/workspace_session.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.database.dao.workspace_session import WorkSpaceSession, WorkSpaceSessionDao" in zuno_api_service_workspace_session
    assert "from zuno.database.models.workspace_session import WorkSpaceSessionCreate" in zuno_api_service_workspace_session
    assert "from zuno.utils.model_output import strip_model_wrapper_from_user_input, strip_think_tags" in zuno_api_service_workspace_session
    assert "from zuno.database.models.workspace_session import WorkSpaceSession" in zuno_dao_workspace_session
    assert "from zuno.database.session import async_session_getter" in zuno_dao_workspace_session
    assert "from zuno.database.models.base import SQLModelSerializable" in zuno_model_workspace_session
    assert "class WorkSpaceSessionBase(SQLModelSerializable):" in zuno_model_workspace_session
    assert "class WorkSpaceSession(WorkSpaceSessionBase, table=True):" in zuno_model_workspace_session
    assert "from agentchat.database.models.workspace_session import" not in zuno_model_workspace_session


def test_high_value_user_api_prefers_zuno():
    zuno_api_service_user = (
        REPO_ROOT / "src/backend/zuno/api/services/user.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_user = (
        REPO_ROOT / "src/backend/zuno/api/v1/user.py"
    ).read_text(encoding="utf-8")
    zuno_dao_user = (
        REPO_ROOT / "src/backend/zuno/database/dao/user.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.services.storage import storage_client" in zuno_api_service_user
    assert "from zuno.services.redis import redis_client" in zuno_api_service_user
    assert "from zuno.database.models.user import AdminUser, UserTable" in zuno_api_service_user
    assert "from zuno.database.dao.user import UserDao" in zuno_api_service_user
    assert "from zuno.utils.JWT import ACCESS_TOKEN_EXPIRE_TIME" in zuno_api_service_user
    assert "from zuno.api.services.user import UserService, get_user_jwt" in zuno_api_v1_user
    assert "from zuno.database.dao.user import UserDao" not in zuno_api_v1_user
    assert "from zuno.services.redis import redis_client" not in zuno_api_v1_user
    assert "from zuno.utils.JWT import ACCESS_TOKEN_EXPIRE_TIME" not in zuno_api_v1_user
    assert "from agentchat.api.v1.user import *" not in zuno_api_v1_user
    assert "from zuno.database.models.user import UserTable" in zuno_dao_user
    assert "from zuno.database.session import session_getter" in zuno_dao_user
    assert "from agentchat.database.dao.user import *" not in zuno_dao_user


def test_high_value_knowledge_task_dao_prefers_zuno():
    zuno_dao_knowledge_task = (
        REPO_ROOT / "src/backend/zuno/database/dao/knowledge_task.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.database.models.knowledge_task import KnowledgeTaskEventTable, KnowledgeTaskTable" in zuno_dao_knowledge_task
    assert "from zuno.database.session import session_getter" in zuno_dao_knowledge_task
    assert "from agentchat.database.dao.knowledge_task import *" not in zuno_dao_knowledge_task


def test_high_value_dialog_api_prefers_zuno():
    zuno_api_service_dialog = (
        REPO_ROOT / "src/backend/zuno/api/services/dialog.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_dialog = (
        REPO_ROOT / "src/backend/zuno/api/v1/dialog.py"
    ).read_text(encoding="utf-8")
    zuno_dao_dialog = (
        REPO_ROOT / "src/backend/zuno/database/dao/dialog.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.api.services.agent import AgentService" in zuno_api_service_dialog
    assert "from zuno.database.dao.dialog import DialogDao" in zuno_api_service_dialog
    assert "from zuno.database.dao.history import HistoryDao" in zuno_api_service_dialog
    assert "class DialogService:" in zuno_api_service_dialog
    assert "from zuno.api.services.dialog import DialogService" in zuno_api_v1_dialog
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_dialog
    assert "from zuno.schema.dialog import DialogCreateRequest" in zuno_api_v1_dialog
    assert "from zuno.schema.schemas import UnifiedResponseModel, resp_200, resp_500" in zuno_api_v1_dialog
    assert "from agentchat.api.v1.dialog import *" not in zuno_api_v1_dialog
    assert "from zuno.database.models.dialog import DialogTable" in zuno_dao_dialog
    assert "from zuno.database.session import session_getter" in zuno_dao_dialog
    assert "from agentchat.database.dao.dialog import *" not in zuno_dao_dialog


def test_high_value_history_api_prefers_zuno():
    zuno_api_service_history = (
        REPO_ROOT / "src/backend/zuno/api/services/history.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_history = (
        REPO_ROOT / "src/backend/zuno/api/v1/history.py"
    ).read_text(encoding="utf-8")
    zuno_dao_history = (
        REPO_ROOT / "src/backend/zuno/database/dao/history.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.api.services.dialog import DialogService" in zuno_api_service_history
    assert "from zuno.database.dao.history import HistoryDao" in zuno_api_service_history
    assert "from zuno.services.rag.es_client import client as es_client" in zuno_api_service_history
    assert "from zuno.services.rag.vector_db import milvus_client" in zuno_api_service_history
    assert "class HistoryService:" in zuno_api_service_history
    assert "from zuno.api.services.history import HistoryService" in zuno_api_v1_history
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_history
    assert "from zuno.schema.schemas import UnifiedResponseModel, resp_200, resp_500" in zuno_api_v1_history
    assert "from agentchat.api.v1.history import *" not in zuno_api_v1_history
    assert "from zuno.database.models.history import HistoryTable" in zuno_dao_history
    assert "from zuno.database.session import session_getter" in zuno_dao_history
    assert "from agentchat.database.dao.history import *" not in zuno_dao_history


def test_high_value_usage_stats_api_prefers_zuno():
    zuno_api_service_usage = (
        REPO_ROOT / "src/backend/zuno/api/services/usage_stats.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_usage = (
        REPO_ROOT / "src/backend/zuno/api/v1/usage_stats.py"
    ).read_text(encoding="utf-8")
    zuno_dao_usage = (
        REPO_ROOT / "src/backend/zuno/database/dao/usage_stats.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.database.dao.usage_stats import UsageStats, UsageStatsDao" in zuno_api_service_usage
    assert "class UsageStatsService:" in zuno_api_service_usage
    assert "from zuno.api.services.usage_stats import UsageStatsService" in zuno_api_v1_usage
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_usage
    assert "from zuno.schema.usage_stats import UsageStatsRequest" in zuno_api_v1_usage
    assert "from agentchat.api.v1.usage_stats import *" not in zuno_api_v1_usage
    assert "from zuno.database.models.usage_stats import UsageStats" in zuno_dao_usage
    assert "from zuno.database.session import async_session_getter, session_getter" in zuno_dao_usage
    assert "from agentchat.database.dao.usage_stats import *" not in zuno_dao_usage


def test_high_value_message_api_prefers_zuno():
    zuno_api_service_message = (
        REPO_ROOT / "src/backend/zuno/api/services/message.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_message = (
        REPO_ROOT / "src/backend/zuno/api/v1/message.py"
    ).read_text(encoding="utf-8")
    zuno_dao_message = (
        REPO_ROOT / "src/backend/zuno/database/dao/message.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.database.dao.message import MessageDownDao, MessageLikeDao" in zuno_api_service_message
    assert "class MessageLikeService:" in zuno_api_service_message
    assert "class MessageDownService:" in zuno_api_service_message
    assert "from zuno.api.services.message import MessageDownService, MessageLikeService" in zuno_api_v1_message
    assert "from zuno.schema.schemas import resp_200" in zuno_api_v1_message
    assert "from agentchat.api.v1.message import *" not in zuno_api_v1_message
    assert "from zuno.database.models.message import MessageDownTable, MessageLikeTable" in zuno_dao_message
    assert "from zuno.database.session import session_getter" in zuno_dao_message
    assert "from agentchat.database.dao.message import *" not in zuno_dao_message


def test_workspace_prep_services_prefer_zuno_entrypoints():
    zuno_api_v1_agent = (
        REPO_ROOT / "src/backend/zuno/api/v1/agent.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_capability = (
        REPO_ROOT / "src/backend/zuno/api/v1/capability.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_completion = (
        REPO_ROOT / "src/backend/zuno/api/v1/completion.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_config = (
        REPO_ROOT / "src/backend/zuno/api/v1/config.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_mcp_chat = (
        REPO_ROOT / "src/backend/zuno/api/v1/mcp_chat.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_tool = (
        REPO_ROOT / "src/backend/zuno/api/v1/tool.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_upload = (
        REPO_ROOT / "src/backend/zuno/api/v1/upload.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_wechat = (
        REPO_ROOT / "src/backend/zuno/api/v1/wechat.py"
    ).read_text(encoding="utf-8")
    zuno_api_service_mcp_chat = (
        REPO_ROOT / "src/backend/zuno/api/services/mcp_chat.py"
    ).read_text(encoding="utf-8")
    zuno_api_service_wechat = (
        REPO_ROOT / "src/backend/zuno/api/services/wechat.py"
    ).read_text(encoding="utf-8")
    zuno_api_service_llm = (
        REPO_ROOT / "src/backend/zuno/api/services/llm.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_llm = (
        REPO_ROOT / "src/backend/zuno/api/v1/llm.py"
    ).read_text(encoding="utf-8")
    zuno_api_service_agent = (
        REPO_ROOT / "src/backend/zuno/api/services/agent.py"
    ).read_text(encoding="utf-8")
    zuno_api_service_tool = (
        REPO_ROOT / "src/backend/zuno/api/services/tool.py"
    ).read_text(encoding="utf-8")
    zuno_api_service_mcp_server = (
        REPO_ROOT / "src/backend/zuno/api/services/mcp_server.py"
    ).read_text(encoding="utf-8")
    zuno_dao_llm = (
        REPO_ROOT / "src/backend/zuno/database/dao/llm.py"
    ).read_text(encoding="utf-8")
    zuno_dao_agent = (
        REPO_ROOT / "src/backend/zuno/database/dao/agent.py"
    ).read_text(encoding="utf-8")
    zuno_dao_tool = (
        REPO_ROOT / "src/backend/zuno/database/dao/tool.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.api.services.agent import AgentService" in zuno_api_v1_agent
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_agent
    assert "from zuno.schema.agent import AgentCreateReq, AgentDeleteReq, AgentSearchReq, AgentUpdateReq" in zuno_api_v1_agent
    assert 'router = APIRouter(tags=["Agent"])' in zuno_api_v1_agent
    assert "from agentchat.api.v1.agent import *" not in zuno_api_v1_agent
    assert "from zuno.api.services.capability import CapabilityService" in zuno_api_v1_capability
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_capability
    assert "from zuno.schema.capability import CapabilitySearchReq" in zuno_api_v1_capability
    assert "from zuno.services.capability_registry import CapabilityRegistryService" not in zuno_api_v1_capability
    assert 'router = APIRouter(tags=["Capability"], prefix="/capability")' in zuno_api_v1_capability
    assert "from agentchat.api.v1.capability import *" not in zuno_api_v1_capability
    assert "from zuno.api.services.completion import CompletionService" in zuno_api_v1_completion
    assert "from zuno.api.services.history import HistoryService" in zuno_api_v1_completion
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_completion
    assert "from zuno.core.agents.general_agent import AgentConfig, GeneralAgent" not in zuno_api_v1_completion
    assert "from zuno.services.memory.client import memory_client" not in zuno_api_v1_completion
    assert 'router = APIRouter(tags=["Completion"])' in zuno_api_v1_completion
    assert "from agentchat.api.v1.completion import *" not in zuno_api_v1_completion
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_config
    assert "from zuno.settings import initialize_app_settings, resolve_app_config_path" in zuno_api_v1_config
    assert "SYSTEM_TOOL_CONFIG_META" in zuno_api_v1_config
    assert 'router = APIRouter(tags=["Config"])' in zuno_api_v1_config
    assert "from agentchat.api.v1.config import *" not in zuno_api_v1_config
    assert "from zuno.api.services.dialog import DialogService" in zuno_api_v1_mcp_chat
    assert "from zuno.api.services.history import HistoryService" in zuno_api_v1_mcp_chat
    assert "from zuno.api.services.mcp_chat import MCPChatAgent" in zuno_api_v1_mcp_chat
    assert 'router = APIRouter(tags=["MCP-Chat"])' in zuno_api_v1_mcp_chat
    assert "from agentchat.api.v1.mcp_chat import *" not in zuno_api_v1_mcp_chat
    assert "from zuno.api.services.tool import ToolRuntimeService, ToolService" in zuno_api_v1_tool
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_tool
    assert "from zuno.schema.tool import (" in zuno_api_v1_tool
    assert "from zuno.services.cli_tool_discovery import CliToolDiscoveryService" not in zuno_api_v1_tool
    assert "from zuno.services.simple_api_tool import (" not in zuno_api_v1_tool
    assert "from zuno.services.tool_connectivity_service import ToolConnectivityService" not in zuno_api_v1_tool
    assert "from zuno.services.tool_creation_service import ToolCreationService" not in zuno_api_v1_tool
    assert "from zuno.services.user_defined_tool_runtime import build_stored_tool_auth_config" not in zuno_api_v1_tool
    assert "from zuno.tools.cli_tool.adapter import CLIToolAdapter" not in zuno_api_v1_tool
    assert "from zuno.tools.openapi_tool.adapter import OpenAPIToolAdapter" not in zuno_api_v1_tool
    assert 'router = APIRouter(tags=["Tool"], prefix="/tool")' in zuno_api_v1_tool
    assert "from agentchat.api.v1.tool import *" not in zuno_api_v1_tool
    assert "from zuno.api.services.upload import UploadService" in zuno_api_v1_upload
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_upload
    assert "from zuno.services.storage import storage_client" not in zuno_api_v1_upload
    assert "from zuno.settings import app_settings" not in zuno_api_v1_upload
    assert "from zuno.utils.file_utils import get_object_storage_base_path" not in zuno_api_v1_upload
    assert 'router = APIRouter(tags=["Upload"])' in zuno_api_v1_upload
    assert "from agentchat.api.v1.upload import *" not in zuno_api_v1_upload
    assert "from zuno.api.services.wechat import WeChatService" in zuno_api_v1_wechat
    assert "from zuno.api.services.workspace_session import WorkSpaceSessionService" not in zuno_api_v1_wechat
    assert "from zuno.services.redis import redis_client" not in zuno_api_v1_wechat
    assert "from zuno.services.workspace.wechat_agent import WeChatAgent" not in zuno_api_v1_wechat
    assert "from zuno.utils.runtime_observability import RedisKeys" not in zuno_api_v1_wechat
    assert 'router = APIRouter(tags=["Wechat"])' in zuno_api_v1_wechat
    assert "from agentchat.api.v1.wechat import *" not in zuno_api_v1_wechat
    assert "from zuno.api.services.history import HistoryService" in zuno_api_service_mcp_chat
    assert "from zuno.api.services.llm import LLMService" in zuno_api_service_mcp_chat
    assert "from zuno.api.services.mcp_stdio_server import MCPServerService" in zuno_api_service_mcp_chat
    assert "from zuno.services.mcp_openai.mcp_manager import MCPManager" in zuno_api_service_mcp_chat
    assert "class MCPChatAgent:" in zuno_api_service_mcp_chat
    assert "from zuno.api.services.workspace_session import WorkSpaceSessionService" in zuno_api_service_wechat
    assert "from zuno.services.redis import redis_client" in zuno_api_service_wechat
    assert "from zuno.utils.runtime_observability import RedisKeys" in zuno_api_service_wechat
    assert "from zuno.settings import app_settings" in zuno_api_service_wechat
    assert "class WeChatService:" in zuno_api_service_wechat
    assert "from zuno.database.dao.llm import LLMDao" in zuno_api_service_llm
    assert "from zuno.database.models.user import AdminUser, SystemUser" in zuno_api_service_llm
    assert "class LLMService:" in zuno_api_service_llm
    assert "from zuno.api.services.llm import LLMService, LLM_Types" in zuno_api_v1_llm
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_llm
    assert "from zuno.schema.llm import LLMActivateReq, LLMCreateReq, LLMDeleteReq, LLMSearchReq, LLMUpdateReq" in zuno_api_v1_llm
    assert 'router = APIRouter(tags=["LLM"], prefix="/llm")' in zuno_api_v1_llm
    assert "from agentchat.api.v1.llm import *" not in zuno_api_v1_llm
    assert "from zuno.database.models.llm import LLMTable" in zuno_dao_llm
    assert "from zuno.database.models.user import SystemUser" in zuno_dao_llm
    assert "from zuno.database.session import async_session_getter, session_getter" in zuno_dao_llm
    assert "from agentchat.database.dao.llm import *" not in zuno_dao_llm
    assert "from zuno.database import AgentTable" in zuno_api_service_agent
    assert "from zuno.database.dao.agent import AgentDao" in zuno_api_service_agent
    assert "from zuno.database.dao.dialog import DialogDao" in zuno_api_service_agent
    assert "from zuno.schema.agent import AgentCreateReq" in zuno_api_service_agent
    assert "class AgentService:" in zuno_api_service_agent
    assert "from zuno.database.models.agent import AgentTable" in zuno_dao_agent
    assert "from zuno.database.session import session_getter" in zuno_dao_agent
    assert "from agentchat.database.dao.agent import *" not in zuno_dao_agent
    assert "from zuno.database import SystemUser, ToolTable" in zuno_api_service_tool
    assert "from zuno.database.dao.tool import ToolDao" in zuno_api_service_tool
    assert "from zuno.services.user_defined_tool_runtime import get_user_defined_runtime_type" in zuno_api_service_tool
    assert "class ToolService:" in zuno_api_service_tool
    assert "from zuno.database.models.tool import ToolTable" in zuno_dao_tool
    assert "from zuno.database.session import async_session_getter, session_getter" in zuno_dao_tool
    assert "from agentchat.database.dao.tool import *" not in zuno_dao_tool
    assert "from zuno.api.services.mcp_user_config import MCPUserConfigService" in zuno_api_service_mcp_server
    assert "from zuno.database.dao.mcp_server import MCPServerDao" in zuno_api_service_mcp_server
    assert "from zuno.database.models.user import AdminUser, SystemUser" in zuno_api_service_mcp_server
    assert "from zuno.services.mcp.manager import MCPManager" in zuno_api_service_mcp_server
    assert "from zuno.utils.convert import convert_mcp_config" in zuno_api_service_mcp_server
    assert "from zuno.utils.helpers import parse_imported_config" in zuno_api_service_mcp_server
    assert "class MCPService:" in zuno_api_service_mcp_server


def test_high_value_mcp_server_service_and_dao_prefer_zuno():
    zuno_api_service_mcp_server = (
        REPO_ROOT / "src/backend/zuno/api/services/mcp_server.py"
    ).read_text(encoding="utf-8")
    zuno_dao_mcp_server = (
        REPO_ROOT / "src/backend/zuno/database/dao/mcp_server.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.api.services.mcp_user_config import MCPUserConfigService" in zuno_api_service_mcp_server
    assert "from zuno.database.dao.mcp_server import MCPServerDao" in zuno_api_service_mcp_server
    assert "from zuno.database.models.user import AdminUser, SystemUser" in zuno_api_service_mcp_server
    assert "from zuno.services.mcp.manager import MCPManager" in zuno_api_service_mcp_server
    assert "class MCPService:" in zuno_api_service_mcp_server
    assert "from zuno.database.models.mcp_server import MCPServerTable" in zuno_dao_mcp_server
    assert "from zuno.database.session import session_getter" in zuno_dao_mcp_server
    assert "from agentchat.database.dao.mcp_server import *" not in zuno_dao_mcp_server


def test_high_value_mcp_user_config_service_and_dao_prefer_zuno():
    zuno_api_service_mcp_user_config = (
        REPO_ROOT / "src/backend/zuno/api/services/mcp_user_config.py"
    ).read_text(encoding="utf-8")
    zuno_dao_mcp_user_config = (
        REPO_ROOT / "src/backend/zuno/database/dao/mcp_user_config.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.database.dao.mcp_user_config import MCPUserConfigDao" in zuno_api_service_mcp_user_config
    assert "class MCPUserConfigService:" in zuno_api_service_mcp_user_config
    assert "from zuno.database.models.mcp_user_config import MCPUserConfigTable" in zuno_dao_mcp_user_config
    assert "from zuno.database.session import session_getter" in zuno_dao_mcp_user_config
    assert "from agentchat.database.dao.mcp_user_config import *" not in zuno_dao_mcp_user_config


def test_high_value_mcp_agent_and_stdio_service_and_dao_prefer_zuno():
    zuno_api_service_mcp_agent = (
        REPO_ROOT / "src/backend/zuno/api/services/mcp_agent.py"
    ).read_text(encoding="utf-8")
    zuno_api_service_mcp_stdio = (
        REPO_ROOT / "src/backend/zuno/api/services/mcp_stdio_server.py"
    ).read_text(encoding="utf-8")
    zuno_dao_mcp_agent = (
        REPO_ROOT / "src/backend/zuno/database/dao/mcp_agent.py"
    ).read_text(encoding="utf-8")
    zuno_dao_mcp_stdio = (
        REPO_ROOT / "src/backend/zuno/database/dao/mcp_stdio_server.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.database.dao.mcp_agent import MCPAgentDao" in zuno_api_service_mcp_agent
    assert "from zuno.database.models.user import AdminUser, SystemUser" in zuno_api_service_mcp_agent
    assert "from zuno.schema.schemas import resp_200, resp_500" in zuno_api_service_mcp_agent
    assert "class MCPAgentService:" in zuno_api_service_mcp_agent
    assert "from agentchat.api.services.mcp_agent import *" not in zuno_api_service_mcp_agent

    assert "from zuno.database.dao.mcp_stdio_server import MCPServerStdioDao" in zuno_api_service_mcp_stdio
    assert "from zuno.database.models.user import AdminUser" in zuno_api_service_mcp_stdio
    assert "class MCPServerService:" in zuno_api_service_mcp_stdio
    assert "from agentchat.api.services.mcp_stdio_server import *" not in zuno_api_service_mcp_stdio

    assert "from zuno.database.models.mcp_agent import MCPAgentTable" in zuno_dao_mcp_agent
    assert "from zuno.database.session import session_getter" in zuno_dao_mcp_agent
    assert "from zuno.utils.helpers import delete_img" in zuno_dao_mcp_agent
    assert "from agentchat.database.dao.mcp_agent import *" not in zuno_dao_mcp_agent

    assert "from zuno.database.models.mcp_server import MCPServerStdioTable" in zuno_dao_mcp_stdio
    assert "from zuno.database.session import session_getter" in zuno_dao_mcp_stdio
    assert "from agentchat.database.dao.mcp_stdio_server import *" not in zuno_dao_mcp_stdio


def test_high_value_mcp_agent_and_stdio_v1_routes_prefer_zuno():
    zuno_api_v1_mcp_agent = (
        REPO_ROOT / "src/backend/zuno/api/v1/mcp_agent.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_mcp_stdio = (
        REPO_ROOT / "src/backend/zuno/api/v1/mcp_stdio_server.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.api.services.mcp_agent import MCPAgentService" in zuno_api_v1_mcp_agent
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_mcp_agent
    assert "from zuno.schema.schemas import UnifiedResponseModel, resp_200, resp_500" in zuno_api_v1_mcp_agent
    assert "from zuno.settings import app_settings" in zuno_api_v1_mcp_agent
    assert "from agentchat.api.v1.mcp_agent import *" not in zuno_api_v1_mcp_agent

    assert "from zuno.api.services.mcp_stdio_server import MCPServerService" in zuno_api_v1_mcp_stdio
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_mcp_stdio
    assert "from zuno.schema.schemas import resp_200, resp_500" in zuno_api_v1_mcp_stdio
    assert "from agentchat.api.v1.mcp_stdio_server import *" not in zuno_api_v1_mcp_stdio


def test_high_value_mcp_server_and_user_config_v1_routes_prefer_zuno():
    zuno_api_v1_mcp_server = (
        REPO_ROOT / "src/backend/zuno/api/v1/mcp_server.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_mcp_user_config = (
        REPO_ROOT / "src/backend/zuno/api/v1/mcp_user_config.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.api.services.mcp_server import MCPService" in zuno_api_v1_mcp_server
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_mcp_server
    assert "from zuno.core.agents.structured_response_agent import StructuredResponseAgent" not in zuno_api_v1_mcp_server
    assert "from zuno.prompts.mcp import McpAsToolPrompt" not in zuno_api_v1_mcp_server
    assert "from zuno.schema.mcp import MCPServerImportedReq, MCPServerUpdateReq" in zuno_api_v1_mcp_server
    assert "from zuno.schema.schemas import resp_200, resp_500" in zuno_api_v1_mcp_server
    assert "from zuno.services.mcp.manager import MCPManager" not in zuno_api_v1_mcp_server
    assert "from zuno.utils.convert import convert_mcp_config" not in zuno_api_v1_mcp_server
    assert "from zuno.utils.helpers import parse_imported_config" not in zuno_api_v1_mcp_server
    assert "from agentchat.api.v1.mcp_server import *" not in zuno_api_v1_mcp_server

    assert "from zuno.api.services.mcp_server import MCPService" in zuno_api_v1_mcp_user_config
    assert "from zuno.api.services.mcp_user_config import MCPUserConfigService" in zuno_api_v1_mcp_user_config
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_mcp_user_config
    assert "from zuno.schema.mcp_user_config import (" in zuno_api_v1_mcp_user_config
    assert "from zuno.schema.schemas import UnifiedResponseModel, resp_200, resp_500" in zuno_api_v1_mcp_user_config
    assert "from agentchat.api.v1.mcp_user_config import *" not in zuno_api_v1_mcp_user_config


def test_high_value_agent_skill_service_v1_and_dao_prefer_zuno():
    zuno_api_service_agent_skill = (
        REPO_ROOT / "src/backend/zuno/api/services/agent_skill.py"
    ).read_text(encoding="utf-8")
    zuno_api_v1_agent_skill = (
        REPO_ROOT / "src/backend/zuno/api/v1/agent_skill.py"
    ).read_text(encoding="utf-8")
    zuno_dao_agent_skill = (
        REPO_ROOT / "src/backend/zuno/database/dao/agent_skill.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.core.agents.structured_response_agent import StructuredResponseAgent" in zuno_api_service_agent_skill
    assert "from zuno.database.dao.agent_skill import AgentSkillDao" in zuno_api_service_agent_skill
    assert "from zuno.database.models.agent_skill import AgentSkill" in zuno_api_service_agent_skill
    assert "from zuno.prompts.skill import AgentSkillAsToolPrompt" in zuno_api_service_agent_skill
    assert "from zuno.schema.agent_skill import (" in zuno_api_service_agent_skill
    assert "class AgentSkillService:" in zuno_api_service_agent_skill
    assert "from agentchat.api.services.agent_skill import *" not in zuno_api_service_agent_skill

    assert "from zuno.api.services.agent_skill import AgentSkillService" in zuno_api_v1_agent_skill
    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_agent_skill
    assert "from zuno.schema.agent_skill import (" in zuno_api_v1_agent_skill
    assert "from zuno.schema.schemas import resp_200" in zuno_api_v1_agent_skill
    assert "from agentchat.api.v1.agent_skill import *" not in zuno_api_v1_agent_skill

    assert "from zuno.database.models.agent_skill import AgentSkill" in zuno_dao_agent_skill
    assert "from zuno.database.session import async_session_getter" in zuno_dao_agent_skill
    assert "from agentchat.database.dao.agent_skill import *" not in zuno_dao_agent_skill


def test_high_value_user_permission_and_memory_daos_prefer_zuno():
    zuno_api_service_user = (
        REPO_ROOT / "src/backend/zuno/api/services/user.py"
    ).read_text(encoding="utf-8")
    zuno_dao_user_role = (
        REPO_ROOT / "src/backend/zuno/database/dao/user_role.py"
    ).read_text(encoding="utf-8")
    zuno_dao_role = (
        REPO_ROOT / "src/backend/zuno/database/dao/role.py"
    ).read_text(encoding="utf-8")
    zuno_dao_memory_history = (
        REPO_ROOT / "src/backend/zuno/database/dao/memory_history.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.database.dao.user_role import UserRoleDao" in zuno_api_service_user
    assert "from zuno.database.models.role import AdminRole" in zuno_dao_user_role
    assert "from zuno.database.models.user_role import UserRole, UserRoleBase" in zuno_dao_user_role
    assert "from zuno.database.session import session_getter" in zuno_dao_user_role
    assert "from agentchat.database.dao.user_role import *" not in zuno_dao_user_role
    assert "from zuno.database.models.role import AdminRole, Role, RoleBase, RoleCreate" in zuno_dao_role
    assert "from zuno.database.session import session_getter" in zuno_dao_role
    assert "from agentchat.database.dao.role import *" not in zuno_dao_role
    assert "from zuno.database.models.memory_history import MemoryHistoryTable" in zuno_dao_memory_history
    assert "from zuno.database.session import session_getter" in zuno_dao_memory_history
    assert "from agentchat.database.dao.memory_history import *" not in zuno_dao_memory_history


def test_workspace_api_session_routes_prefer_zuno():
    zuno_api_v1_workspace = (
        REPO_ROOT / "src/backend/zuno/api/v1/workspace.py"
    ).read_text(encoding="utf-8")
    zuno_api_service_workspace = (
        REPO_ROOT / "src/backend/zuno/api/services/workspace.py"
    ).read_text(encoding="utf-8")

    assert "from zuno.api.services.user import UserPayload, get_login_user" in zuno_api_v1_workspace
    assert "from zuno.api.services.workspace import WorkspaceService" in zuno_api_v1_workspace
    assert "from zuno.api.services.workspace_session import WorkSpaceSessionService" in zuno_api_v1_workspace
    assert "from zuno.database.models.workspace_session import WorkSpaceSessionCreate" not in zuno_api_v1_workspace
    assert "from zuno.database.models.workspace_session import WorkSpaceSessionCreate" in zuno_api_service_workspace
    assert "from zuno.api.services.tool import ToolService" not in zuno_api_v1_workspace
    assert "from zuno.api.services.llm import LLMService" not in zuno_api_v1_workspace
    assert "from zuno.api.services.mcp_server import MCPService" not in zuno_api_v1_workspace
    assert "from zuno.api.services.agent import AgentService" not in zuno_api_v1_workspace
    assert "from zuno.services.execution_policy import (" not in zuno_api_v1_workspace
    assert "from zuno.services.workspace.simple_agent import MCPConfig, WorkSpaceSimpleAgent" not in zuno_api_v1_workspace
    assert "from zuno.services.workspace.attachment_service import (" not in zuno_api_v1_workspace
    assert "from zuno.prompts.completion import SYSTEM_PROMPT" not in zuno_api_v1_workspace
    assert "from zuno.utils.helpers import parse_imported_config" not in zuno_api_v1_workspace
    assert "from zuno.utils.contexts import set_agent_name_context, set_user_id_context" not in zuno_api_v1_workspace
    assert "from zuno.utils.model_output import normalize_model_id_for_provider" not in zuno_api_v1_workspace
    assert "async def get_workspace_plugins(" in zuno_api_v1_workspace
    assert "async def get_workspace_execution_modes(" in zuno_api_v1_workspace
    assert "async def workspace_simple_chat(" in zuno_api_v1_workspace
    assert "from agentchat.api.v1.workspace import *" not in zuno_api_v1_workspace
    assert "from zuno.api.services.tool import ToolService" in zuno_api_service_workspace
    assert "from zuno.api.services.llm import LLMService" in zuno_api_service_workspace
    assert "from zuno.api.services.mcp_server import MCPService" in zuno_api_service_workspace
    assert "from zuno.api.services.agent import AgentService" in zuno_api_service_workspace
    assert "from zuno.services.execution_policy import (" in zuno_api_service_workspace
    assert "from zuno.services.workspace.attachment_service import (" in zuno_api_service_workspace
    assert "from zuno.prompts.completion import SYSTEM_PROMPT" in zuno_api_service_workspace
    assert "from zuno.utils.helpers import parse_imported_config" in zuno_api_service_workspace
    assert "from zuno.utils.contexts import set_agent_name_context, set_user_id_context" in zuno_api_service_workspace
    assert "from zuno.utils.model_output import normalize_model_id_for_provider" in zuno_api_service_workspace


def test_zuno_api_v1_package_no_longer_uses_agentchat_wildcard_bridge():
    zuno_api_v1_init = (
        REPO_ROOT / "src/backend/zuno/api/v1/__init__.py"
    ).read_text(encoding="utf-8")

    assert "from . import (" in zuno_api_v1_init
    assert '"completion"' in zuno_api_v1_init
    assert '"workspace"' in zuno_api_v1_init
    assert "from agentchat.api.v1 import *" not in zuno_api_v1_init
