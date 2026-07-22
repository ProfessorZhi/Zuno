from __future__ import annotations

import ast
import asyncio
import pytest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_model_gateway_bypass.py"
BOUNDARY_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_model_gateway_boundaries.py"
TEMPORARY_ALLOWLIST = REPO_ROOT / ".agent" / "programs" / "work-products" / "temporary-allowlist.yaml"
MIGRATED_PROVIDER_PATHS = {
    "src/backend/zuno/agent/core/models/anthropic.py",
    "src/backend/zuno/agent/core/models/embedding.py",
    "src/backend/zuno/agent/core/models/manager.py",
    "src/backend/zuno/agent/core/models/reason_model.py",
    "src/backend/zuno/agent/core/models/tool_call.py",
    "src/backend/zuno/agent/core/models/usage_model.py",
    "src/backend/zuno/capability/tools/resume_optimizer/action.py",
    "src/backend/zuno/platform/common/extract.py",
    "src/backend/zuno/platform/services/autobuild/client.py",
    "src/backend/zuno/platform/services/mcp_openai/mcp_manager.py",
    "src/backend/zuno/platform/services/mcp_openai/strict_schema.py",
    "src/backend/zuno/platform/services/rag/embedding.py",
}
ALLOWLIST_TRACKED_MIGRATED_PROVIDER_PATHS = MIGRATED_PROVIDER_PATHS - {
    "src/backend/zuno/platform/services/mcp_openai/strict_schema.py",
}


def _load_verifier():
    spec = spec_from_file_location("verify_model_gateway_bypass", VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_boundary_verifier():
    spec = spec_from_file_location("verify_model_gateway_boundaries", BOUNDARY_VERIFIER)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_model_gateway_bypass_inventory_is_locked_until_cutover() -> None:
    verifier = _load_verifier()
    assert verifier.verify_model_gateway_bypass(strict=False) == []


def test_model_gateway_bypass_strict_mode_passes_after_cutover() -> None:
    verifier = _load_verifier()
    assert verifier.verify_model_gateway_bypass(strict=True) == []


def test_migrated_provider_paths_are_not_allowed_as_legacy_boundaries() -> None:
    boundary = _load_boundary_verifier()
    allowlist_text = TEMPORARY_ALLOWLIST.read_text(encoding="utf-8")

    assert boundary.ALLOWED_LEGACY_PATHS.isdisjoint(MIGRATED_PROVIDER_PATHS)
    for path in ALLOWLIST_TRACKED_MIGRATED_PROVIDER_PATHS:
        marker = f'  - path: "{path}"'
        assert marker in allowlist_text
        block = allowlist_text.split(marker, 1)[1].split("\n  - path: ", 1)[0]
        assert 'category: "direct_provider_sdk"' not in block
        assert 'category: "resolved_provider_sdk_cutover"' in block


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
        async def embed_async(self, query):
            if isinstance(query, str):
                return [len(query), 3.0]
            return [[len(item), 3.0] for item in query]

    calls = []

    def fake_build_openai_embedding_gateway_adapter(config_override=None):
        calls.append(config_override)
        return FakeEmbeddingAdapter()

    monkeypatch.setattr(
        rag_embedding_module,
        "build_openai_embedding_gateway_adapter",
        fake_build_openai_embedding_gateway_adapter,
    )

    config = {"api_key": "key", "base_url": "https://example.test", "model_name": "embedding-model"}
    assert asyncio.run(rag_embedding_module.get_embedding("abc", config_override=config)) == [3, 3.0]
    assert asyncio.run(rag_embedding_module.get_embedding(["a", "abcd"], config_override=config)) == [
        [1, 3.0],
        [4, 3.0],
    ]
    assert calls == [config, config]


def test_model_manager_uses_gateway_chat_model_builder(monkeypatch) -> None:
    verifier = _load_verifier()
    relative_path = "src/backend/zuno/agent/core/models/manager.py"

    assert relative_path not in verifier.current_bypass_inventory()

    from zuno.core.models import manager as manager_module

    calls = []

    def fake_build_openai_chat_gateway_model(**kwargs):
        calls.append(kwargs)
        return object()

    monkeypatch.setattr(manager_module, "build_openai_chat_gateway_model", fake_build_openai_chat_gateway_model)

    manager_module.ModelManager.get_user_model(
        model="deepseek-chat",
        api_key="key",
        base_url="https://api.deepseek.com",
    )

    assert calls == [
        {
            "stream_usage": True,
            "model": "deepseek-chat",
            "api_key": "key",
            "base_url": "https://api.deepseek.com",
        }
    ]


def test_gateway_chat_builder_keeps_deepseek_v4_kwargs(monkeypatch) -> None:
    import zuno.platform.model_gateway as gateway_module

    calls = []

    class FakeChatOpenAI:
        def __init__(self, **kwargs):
            calls.append(kwargs)

    original_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "langchain_openai":
            return type("FakeLangchainOpenAI", (), {"ChatOpenAI": FakeChatOpenAI})
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    gateway_module.build_openai_chat_gateway_model(
        stream_usage=True,
        model="deepseek-v4-flash",
        api_key="key",
        base_url="https://api.deepseek.com",
    )

    assert calls == [
        {
            "stream_usage": True,
            "model": "deepseek-v4-flash",
            "api_key": "key",
            "base_url": "https://api.deepseek.com",
            "extra_body": {"thinking": {"type": "disabled"}},
        }
    ]


def test_reasoning_model_uses_gateway_chat_completions_adapter(monkeypatch) -> None:
    verifier = _load_verifier()
    relative_path = "src/backend/zuno/agent/core/models/reason_model.py"

    assert relative_path not in verifier.current_bypass_inventory()

    from langchain_core.messages import HumanMessage
    from zuno.core.models import reason_model as reason_model_module

    calls = []

    class FakeChatCompletionsAdapter:
        def __init__(self, *, api_key, base_url):
            calls.append({"api_key": api_key, "base_url": base_url})

        async def create(self, **kwargs):
            calls.append(kwargs)
            return "stream-response"

    monkeypatch.setattr(reason_model_module, "OpenAIChatCompletionsGatewayAdapter", FakeChatCompletionsAdapter)

    model = reason_model_module.ReasoningModel(
        base_url="https://example.test",
        api_key="key",
        model_name="reasoning-model",
    )

    assert asyncio.run(model.astream([HumanMessage(content="think")])) == "stream-response"
    assert calls == [
        {"api_key": "key", "base_url": "https://example.test"},
        {
            "model": "reasoning-model",
            "messages": [{"role": "user", "content": "think"}],
            "stream": True,
        },
    ]


def test_tool_call_model_uses_gateway_chat_completions_adapter(monkeypatch) -> None:
    verifier = _load_verifier()
    relative_path = "src/backend/zuno/agent/core/models/tool_call.py"

    assert relative_path not in verifier.current_bypass_inventory()

    from langchain_core.messages import HumanMessage
    from zuno.core.models import tool_call as tool_call_module

    calls = []

    class FakeMessage:
        content = "tool-result"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeChatCompletionsAdapter:
        def __init__(self, *, api_key, base_url):
            calls.append({"api_key": api_key, "base_url": base_url})

        async def create(self, **kwargs):
            calls.append(kwargs)
            return FakeResponse()

    monkeypatch.setattr(tool_call_module, "OpenAIChatCompletionsGatewayAdapter", FakeChatCompletionsAdapter)

    model = tool_call_module.ToolCallModel(
        base_url="https://example.test",
        api_key="key",
        model_name="tool-model",
    )
    model.bind_tools([{"type": "function", "function": {"name": "search"}}])

    result = asyncio.run(model.ainvoke([HumanMessage(content="call tool")]))

    assert result.content == "tool-result"
    assert calls == [
        {"api_key": "key", "base_url": "https://example.test"},
        {
            "model": "tool-model",
            "messages": [{"role": "user", "content": "call tool"}],
            "tools": [{"type": "function", "function": {"name": "search"}}],
        },
    ]


def test_usage_model_uses_gateway_usage_adapter(monkeypatch) -> None:
    verifier = _load_verifier()
    relative_path = "src/backend/zuno/agent/core/models/usage_model.py"

    assert relative_path not in verifier.current_bypass_inventory()

    from zuno.core.models import usage_model as usage_model_module

    calls = []

    class FakeUsageAdapter:
        def __init__(self, *, api_key, base_url):
            calls.append({"api_key": api_key, "base_url": base_url})

    monkeypatch.setattr(usage_model_module, "OpenAIUsageChatGatewayAdapter", FakeUsageAdapter)
    monkeypatch.setattr(usage_model_module, "is_openai_well_known_tool", lambda tool_choice: tool_choice == "file_search")

    model = usage_model_module.ChatModelWithTokenUsage(
        model="usage-model",
        api_key="secret-key",
        base_url="https://example.test",
    )

    assert calls == [{"api_key": "secret-key", "base_url": "https://example.test"}]
    bound = model.bind_tools([], tool_choice="file_search")
    assert bound.kwargs["tool_choice"] == {"type": "file_search"}


def test_anthropic_wrappers_use_gateway_adapters(monkeypatch) -> None:
    verifier = _load_verifier()
    relative_path = "src/backend/zuno/agent/core/models/anthropic.py"

    assert relative_path not in verifier.current_bypass_inventory()

    from zuno.core.models import anthropic as anthropic_module

    calls = []

    class FakeAnthropicAdapter:
        def __init__(self, *, api_key, base_url):
            calls.append({"api_key": api_key, "base_url": base_url})

        def create(self, **kwargs):
            calls.append(kwargs)
            return "anthropic-response"

    monkeypatch.setattr(anthropic_module, "AnthropicMessagesGatewayAdapter", FakeAnthropicAdapter)

    model = anthropic_module.DeepAnthropic(
        api_key="key",
        model="claude-model",
        base_url="https://example.test",
        max_tokens=256,
    )

    assert model.invoke([{"role": "user", "content": "hi"}], [{"name": "tool"}]) == "anthropic-response"
    assert calls == [
        {"api_key": "key", "base_url": "https://example.test"},
        {
            "model": "claude-model",
            "max_tokens": 256,
            "messages": [{"role": "user", "content": "hi"}],
            "tools": [{"name": "tool"}],
        },
    ]


def test_async_anthropic_wrapper_uses_gateway_adapter(monkeypatch) -> None:
    from zuno.core.models import anthropic as anthropic_module

    calls = []

    class FakeAsyncAnthropicAdapter:
        def __init__(self, *, api_key, base_url):
            calls.append({"api_key": api_key, "base_url": base_url})

        async def create(self, **kwargs):
            calls.append(kwargs)
            return "async-anthropic-response"

    monkeypatch.setattr(anthropic_module, "AsyncAnthropicMessagesGatewayAdapter", FakeAsyncAnthropicAdapter)

    model = anthropic_module.DeepAsyncAnthropic(
        api_key="key",
        model="claude-model",
        base_url="https://example.test",
        max_tokens=128,
    )

    assert asyncio.run(model.ainvoke([{"role": "user", "content": "hi"}], [{"name": "tool"}])) == (
        "async-anthropic-response"
    )
    assert calls == [
        {"api_key": "key", "base_url": "https://example.test"},
        {
            "model": "claude-model",
            "max_tokens": 128,
            "messages": [{"role": "user", "content": "hi"}],
            "tools": [{"name": "tool"}],
        },
    ]
