import importlib
from pathlib import Path


def test_zuno_alias_modules_import():
    from zuno.api.JWT import Settings
    from zuno.api.router import router
    from zuno.api.services.dialog import DialogService
    from zuno.api.services.history import HistoryService
    from zuno.api.services.knowledge import KnowledgeService
    from zuno.api.services.llm import LLMService
    from zuno.api.services.tool import ToolService
    from zuno.api.services.workspace_session import WorkSpaceSessionService
    from zuno.api.v1.completion import completion
    from zuno.api.v1.config import get_runtime_config
    from zuno.api.v1.knowledge import upload_knowledge
    from zuno.api.v1.workspace import get_workspace_sessions
    from zuno.core.graphs.domain_qa_graph import DomainQAGraph
    from zuno.core.graphs.multi_agent_supervisor_graph import MultiAgentSupervisorGraph
    from zuno.core.models.manager import ModelManager
    from zuno.core.runtime.agent_runtime import AgentRuntime
    from zuno.database.metadata import metadata
    from zuno.database.models.knowledge_file import KnowledgeFileTable
    from zuno.middleware.trace_id_middleware import TraceIDMiddleware
    from zuno.middleware.white_list_middleware import WhitelistMiddleware
    from zuno.mcp_servers.remote_proxy.main import main as remote_proxy_main
    from zuno.schema.common import ModelConfig
    from zuno.services.domain_pack.loader import DomainPackLoader
    from zuno.services.graphrag.extractor import GraphExtractor
    from zuno.services.graphrag.extractors.structured_extractor import StructuredGraphExtractor
    from zuno.services.graphrag.retriever import GraphRetriever
    from zuno.services.queue.runner import main
    from zuno.services.rag.handler import RagHandler
    from zuno.services.rag.retrieval import MixRetrival
    from zuno.services.rag.vector_db import milvus_client
    from zuno.services.storage import storage_client
    from zuno.utils.file_utils import get_save_tempfile
    from zuno.utils.runtime_observability import build_langsmith_metadata

    assert Settings is not None
    assert router is not None
    assert DialogService is not None
    assert HistoryService is not None
    assert KnowledgeService is not None
    assert LLMService is not None
    assert ToolService is not None
    assert WorkSpaceSessionService is not None
    assert completion is not None
    assert get_runtime_config is not None
    assert upload_knowledge is not None
    assert get_workspace_sessions is not None
    assert DomainQAGraph is not None
    assert MultiAgentSupervisorGraph is not None
    assert ModelManager is not None
    assert AgentRuntime is not None
    assert metadata is not None
    assert KnowledgeFileTable is not None
    assert TraceIDMiddleware is not None
    assert WhitelistMiddleware is not None
    assert remote_proxy_main is not None
    assert ModelConfig is not None
    assert DomainPackLoader is not None
    assert GraphExtractor is not None
    assert StructuredGraphExtractor is not None
    assert GraphRetriever is not None
    assert main is not None
    assert RagHandler is not None
    assert MixRetrival is not None
    assert milvus_client is not None
    assert storage_client is not None
    assert get_save_tempfile is not None
    assert build_langsmith_metadata is not None


def test_zuno_services_storage_import_prefers_package_contract():
    module = importlib.import_module("zuno.services.storage")
    module_path = Path(module.__file__).as_posix()

    assert module.storage_client is not None
    assert module_path.endswith("/zuno/services/storage/__init__.py")


def test_zuno_api_alias_module_matrix_imports():
    modules = [
        "zuno.api.errcode.base",
        "zuno.api.errcode.user",
        "zuno.api.v1.agent",
        "zuno.api.v1.agent_skill",
        "zuno.api.v1.capability",
        "zuno.api.v1.completion",
        "zuno.api.v1.config",
        "zuno.api.v1.dialog",
        "zuno.api.v1.history",
        "zuno.api.v1.knowledge",
        "zuno.api.v1.knowledge_file",
        "zuno.api.v1.llm",
        "zuno.api.v1.mcp_agent",
        "zuno.api.v1.mcp_chat",
        "zuno.api.v1.mcp_server",
        "zuno.api.v1.mcp_stdio_server",
        "zuno.api.v1.mcp_user_config",
        "zuno.api.v1.message",
        "zuno.api.v1.tool",
        "zuno.api.v1.upload",
        "zuno.api.v1.usage_stats",
        "zuno.api.v1.user",
        "zuno.api.v1.wechat",
        "zuno.api.v1.workspace",
        "zuno.api.services.agent",
        "zuno.api.services.agent_skill",
        "zuno.api.services.dialog",
        "zuno.api.services.history",
        "zuno.api.services.knowledge",
        "zuno.api.services.knowledge_file",
        "zuno.api.services.llm",
        "zuno.api.services.mcp_agent",
        "zuno.api.services.mcp_chat",
        "zuno.api.services.mcp_server",
        "zuno.api.services.mcp_stdio_server",
        "zuno.api.services.mcp_user_config",
        "zuno.api.services.message",
        "zuno.api.services.mineru",
        "zuno.api.services.tool",
        "zuno.api.services.usage_stats",
        "zuno.api.services.user",
        "zuno.api.services.wechat",
        "zuno.api.services.workspace_session",
    ]

    for module_name in modules:
        module = importlib.import_module(module_name)
        assert module is not None, module_name


def test_zuno_api_imports_resolve_from_backend_runtime_surface():
    modules = [
        "zuno.api",
        "zuno.api.router",
        "zuno.api.JWT",
        "zuno.api.errcode",
        "zuno.api.errcode.base",
        "zuno.api.errcode.user",
        "zuno.api.v1.user",
        "zuno.api.services.user",
    ]

    for module_name in modules:
        module = importlib.import_module(module_name)
        module_path = Path(module.__file__).as_posix()
        assert "/src/backend/zuno/api/" in module_path, module_path


def test_zuno_service_imports_resolve_from_backend_runtime_surface():
    modules = [
        "zuno.middleware",
        "zuno.middleware.trace_id_middleware",
        "zuno.middleware.white_list_middleware",
        "zuno.services.queue",
        "zuno.services.queue.client",
        "zuno.services.queue.runner",
        "zuno.services.retrieval",
        "zuno.services.retrieval.orchestrator",
        "zuno.services.rewrite",
        "zuno.services.rewrite.query_write",
    ]

    for module_name in modules:
        module = importlib.import_module(module_name)
        module_path = Path(module.__file__).as_posix()
        assert (
            "/src/backend/zuno/services/" in module_path
            or "/src/backend/zuno/middleware/" in module_path
        ), module_path


def test_zuno_database_alias_module_matrix_imports():
    modules = [
        "zuno.database.init_data",
        "zuno.database.metadata",
        "zuno.database.session",
        "zuno.database.dao.agent",
        "zuno.database.dao.agent_skill",
        "zuno.database.dao.dialog",
        "zuno.database.dao.history",
        "zuno.database.dao.knowledge",
        "zuno.database.dao.knowledge_file",
        "zuno.database.dao.knowledge_task",
        "zuno.database.dao.llm",
        "zuno.database.dao.mcp_agent",
        "zuno.database.dao.mcp_server",
        "zuno.database.dao.mcp_stdio_server",
        "zuno.database.dao.mcp_user_config",
        "zuno.database.dao.memory_history",
        "zuno.database.dao.message",
        "zuno.database.dao.role",
        "zuno.database.dao.tool",
        "zuno.database.dao.usage_stats",
        "zuno.database.dao.user",
        "zuno.database.dao.user_role",
        "zuno.database.dao.workspace_session",
        "zuno.database.models.agent",
        "zuno.database.models.agent_skill",
        "zuno.database.models.base",
        "zuno.database.models.dialog",
        "zuno.database.models.history",
        "zuno.database.models.knowledge",
        "zuno.database.models.knowledge_file",
        "zuno.database.models.knowledge_task",
        "zuno.database.models.llm",
        "zuno.database.models.mcp_agent",
        "zuno.database.models.mcp_server",
        "zuno.database.models.mcp_user_config",
        "zuno.database.models.memory_history",
        "zuno.database.models.message",
        "zuno.database.models.role",
        "zuno.database.models.tool",
        "zuno.database.models.usage_stats",
        "zuno.database.models.user",
        "zuno.database.models.user_role",
        "zuno.database.models.workspace_session",
    ]

    for module_name in modules:
        module = importlib.import_module(module_name)
        assert module is not None, module_name


def test_zuno_queue_and_pipeline_alias_module_matrix_imports():
    modules = [
        "zuno.services.queue.client",
        "zuno.services.queue.messages",
        "zuno.services.queue.runner",
        "zuno.services.queue.workers",
        "zuno.services.pipeline.manager",
        "zuno.services.pipeline.models",
        "zuno.services.pipeline.stages",
    ]

    for module_name in modules:
        module = importlib.import_module(module_name)
        assert module is not None, module_name


def test_zuno_mcp_alias_module_imports():
    modules = [
        "zuno.services.mcp.manager",
    ]

    for module_name in modules:
        module = importlib.import_module(module_name)
        assert module is not None, module_name


def test_zuno_rag_package_exports_retrieval_module():
    module = importlib.import_module("zuno.services.rag")

    assert module.retrieval is not None
