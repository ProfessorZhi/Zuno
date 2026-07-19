from __future__ import annotations

import ast
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
