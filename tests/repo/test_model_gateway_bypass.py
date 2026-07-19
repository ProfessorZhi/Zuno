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
