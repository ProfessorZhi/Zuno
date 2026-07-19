from __future__ import annotations

import ast
import asyncio
import pytest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_model_gateway_bypass.py"


def _load_verifier():
    spec = spec_from_file_location("verify_model_gateway_bypass", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_model_gateway_bypass_inventory_is_locked_until_cutover() -> None:
    verifier = _load_verifier()
    assert verifier.verify_model_gateway_bypass(strict=False) == []


def test_model_gateway_bypass_strict_mode_documents_current_blocker() -> None:
    verifier = _load_verifier()
    errors = verifier.verify_model_gateway_bypass(strict=True)
    assert errors
    assert any("provider SDK bypass remains" in error for error in errors)


def test_extract_helper_uses_gateway_boundary_without_import_side_effects() -> None:
    verifier = _load_verifier()
    extract_path = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "common" / "extract.py"
    relative_path = "src/backend/zuno/platform/common/extract.py"

    assert relative_path not in verifier.current_bypass_inventory()

    tree = ast.parse(extract_path.read_text(encoding="utf-8"))
    top_level_asyncio_run = [
        node
        for node in tree.body
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Attribute)
        and node.value.func.attr == "run"
    ]
    assert top_level_asyncio_run == []


def test_strict_schema_uses_local_sentinel_instead_of_provider_import() -> None:
    verifier = _load_verifier()
    strict_schema_path = (
        REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "mcp_openai" / "strict_schema.py"
    )
    relative_path = "src/backend/zuno/platform/services/mcp_openai/strict_schema.py"

    assert relative_path not in verifier.current_bypass_inventory()

    spec = spec_from_file_location("zuno_strict_schema_test", strict_schema_path)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    schema = {
        "type": "object",
        "properties": {
            "empty_default": {"type": "string", "default": None},
            "kept_default": {"type": "string", "default": "value"},
        },
    }
    strict_schema = module.ensure_strict_json_schema(schema)

    assert "default" not in strict_schema["properties"]["empty_default"]
    assert strict_schema["properties"]["kept_default"]["default"] == "value"


def test_resume_optimizer_uses_gateway_without_mocking_success() -> None:
    verifier = _load_verifier()
    relative_path = "src/backend/zuno/capability/tools/resume_optimizer/action.py"

    assert relative_path not in verifier.current_bypass_inventory()

    from zuno.capability.tools.resume_optimizer.action import ResumeEnhancer

    class FakeMetrics:
        provider_id = "local_mock_chat"

    class FakeResult:
        status = "succeeded"
        output = "polished resume text"
        metrics = FakeMetrics()

    class FakeGateway:
        def __init__(self) -> None:
            self.request = None

        def invoke(self, request):
            self.request = request
            return FakeResult()

    gateway = FakeGateway()
    enhancer = ResumeEnhancer(gateway=gateway)

    assert enhancer.enhance_text("plain resume text") == "plain resume text"
    assert gateway.request is not None
    assert gateway.request.category.value == "chat"
    assert gateway.request.task_id == "resume_optimizer"


def test_resume_optimizer_returns_non_mock_gateway_output() -> None:
    from zuno.capability.tools.resume_optimizer.action import ResumeEnhancer

    class FakeMetrics:
        provider_id = "gateway_adapter_openai"

    class FakeResult:
        status = "succeeded"
        output = "polished resume text"
        metrics = FakeMetrics()

    class FakeGateway:
        def invoke(self, request):
            return FakeResult()

    enhancer = ResumeEnhancer(gateway=FakeGateway())

    assert enhancer.enhance_text("plain resume text") == "polished resume text"


def test_autobuild_client_constructs_models_through_gateway_boundary() -> None:
    verifier = _load_verifier()
    relative_path = "src/backend/zuno/platform/services/autobuild/client.py"

    assert relative_path not in verifier.current_bypass_inventory()

    autobuild_path = (
        REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "autobuild" / "client.py"
    )
    tree = ast.parse(autobuild_path.read_text(encoding="utf-8"))
    imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and ast.get_source_segment(autobuild_path.read_text(encoding="utf-8"), node)
    ]
    import_text = "\n".join(ast.get_source_segment(autobuild_path.read_text(encoding="utf-8"), node) or "" for node in imports)

    assert "langchain_openai" not in import_text
    assert "ChatOpenAI" not in import_text


def test_mcp_manager_uses_local_invoke_boundary_without_provider_imports() -> None:
    verifier = _load_verifier()
    relative_path = "src/backend/zuno/platform/services/mcp_openai/mcp_manager.py"

    assert relative_path not in verifier.current_bypass_inventory()

    from zuno.services.mcp_openai.mcp_manager import MCPManager

    class AsyncClient:
        async def ainvoke(self, messages, available_tools):
            return {"messages": messages, "tools": available_tools}

    manager = MCPManager(AsyncClient())

    assert asyncio.run(manager._chat_model([{"role": "user", "content": "hi"}], [])) == {
        "messages": [{"role": "user", "content": "hi"}],
        "tools": [],
    }


def test_mcp_manager_preserves_openai_not_implemented_semantics() -> None:
    from zuno.services.mcp_openai.mcp_manager import MCPManager

    OpenAIClient = type("OpenAIClient", (), {"__module__": "openai"})
    manager = MCPManager(OpenAIClient())

    with pytest.raises(NotImplementedError, match="OpenAI MCP chat client is not implemented yet"):
        asyncio.run(manager._chat_model([], []))


def test_core_embedding_model_uses_gateway_owned_provider_adapter(monkeypatch) -> None:
    verifier = _load_verifier()
    relative_path = "src/backend/zuno/agent/core/models/embedding.py"

    assert relative_path not in verifier.current_bypass_inventory()

    from zuno.core.models import embedding as embedding_module

    class FakeEmbeddingAdapter:
        def __init__(self, *, api_key, base_url, model):
            self.api_key = api_key
            self.base_url = base_url
            self.model = model

        def embed(self, query):
            return [len(query), 1.0]

        async def embed_async(self, query):
            if isinstance(query, str):
                return [len(query), 2.0]
            return [[len(item), 2.0] for item in query]

    monkeypatch.setattr(embedding_module, "OpenAIEmbeddingGatewayAdapter", FakeEmbeddingAdapter)

    model = embedding_module.EmbeddingModel(model="embedding-model", api_key="key", base_url="https://example.test")

    assert model.embed("abc") == [3, 1.0]
    assert asyncio.run(model.embed_async(["a", "abcd"])) == [[1, 2.0], [4, 2.0]]


def test_rag_embedding_uses_gateway_owned_provider_adapter(monkeypatch) -> None:
    verifier = _load_verifier()
    relative_path = "src/backend/zuno/platform/services/rag/embedding.py"

    assert relative_path not in verifier.current_bypass_inventory()

    from zuno.services.rag import embedding as rag_embedding_module

    class FakeEmbeddingAdapter:
        def __init__(self, *, api_key, base_url, model):
            self.api_key = api_key
            self.base_url = base_url
            self.model = model

        async def embed_async(self, query):
            if isinstance(query, str):
                return [len(query), 3.0]
            return [[len(item), 3.0] for item in query]

    monkeypatch.setattr(rag_embedding_module, "OpenAIEmbeddingGatewayAdapter", FakeEmbeddingAdapter)

    config = {"api_key": "key", "base_url": "https://example.test", "model_name": "embedding-model"}

    assert asyncio.run(rag_embedding_module.get_embedding("abc", config_override=config)) == [3, 3.0]
    assert asyncio.run(rag_embedding_module.get_embedding(["a", "abcd"], config_override=config)) == [
        [1, 3.0],
        [4, 3.0],
    ]
