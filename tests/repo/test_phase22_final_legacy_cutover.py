"""Final PHASE22 Legacy Cutover Audit (V2) boundary tests.

V2 supersedes the V1 PR #119 test set.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Iterator

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools" / "scripts" / "verify_phase22_final_legacy_cutover.py"
FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures" / "phase22_legacy_cutover"


def _load_verifier() -> Any:
    spec = importlib.util.spec_from_file_location(
        "verify_phase22_final_legacy_cutover_v2", str(VERIFIER_PATH),
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def verifier(monkeypatch) -> Any:
    return _load_verifier()


def _seed_canonical_minimum(root: Path) -> None:
    backend = root / "src" / "backend" / "zuno"
    backend.mkdir(parents=True, exist_ok=True)
    for module in ("api", "agent", "memory", "capability", "knowledge", "platform"):
        (backend / module).mkdir(exist_ok=True)
    apps_web = root / "apps" / "web" / "src"
    apps_web.mkdir(parents=True, exist_ok=True)
    apps_desktop = root / "apps" / "desktop" / "src"
    apps_desktop.mkdir(parents=True, exist_ok=True)
    apps_web.joinpath("page.tsx").write_text("// web tree", encoding="utf-8")
    apps_desktop.joinpath("main.ts").write_text("// desktop tree", encoding="utf-8")
    sample_src = backend / "api" / "sample_route.py"
    sample_src.write_text(
        "from zuno.api.dto.workspace import WorkspaceDTO\n"
        "from zuno.platform.services.runtime import start_runtime\n",
        encoding="utf-8",
    )
    vendor = backend / "platform" / "vendor" / "fastapi_jwt_auth"
    vendor.mkdir(parents=True)
    (vendor / "__init__.py").write_text("# placeholder\n", encoding="utf-8")
    wp = root / ".agent" / "programs" / "work-products"
    wp.mkdir(parents=True)
    (wp / "feature-flag-registry.yaml").write_text(
        "flags:\n"
        "  - flag: \"projection_v3_canary\"\n"
        "    owner: \"01 Product Surface\"\n"
        "    scope: \"SSE stream\"\n"
        "    default: \"DECLARED\"\n"
        "    metric: [\"stream_resume_rate\"]\n"
        "    rollback_command: \"set projection_v3_canary=ROLLBACK_WINDOW\"\n"
        "    expires_at_phase: \"PHASE22\"\n"
        "    retire_task: \"P22-T03\"\n"
        "    domain_fact_owner: \"unchanged\"\n"
        "  - flag: \"legacy_general_agent_completion_rollback\"\n"
        "    owner: \"06 Agent Core\"\n"
        "    scope: \"completion route rollback\"\n"
        "    default: \"RETIRED\"\n"
        "    metric: [\"legacy_completion_invocation_count\"]\n"
        "    rollback_command: \"retired and fail-closed\"\n"
        "    expires_at_phase: \"PHASE08\"\n"
        "    retire_task: \"P22-T03\"\n"
        "    domain_fact_owner: \"unchanged\"\n",
        encoding="utf-8",
    )
    (wp / "phase22-removal-candidates.yaml").write_text(
        "mandatory_removal_candidates: []\n"
        "resolved_this_slice: []\n"
        "wave1_resolved: []\n"
        "fixed_blockers: []\n"
        "remaining_not_closed: []\n",
        encoding="utf-8",
    )
    (wp / "temporary-allowlist.yaml").write_text(
        "allowlist: []\n"
        "rules:\n"
        "  new_bypass_default: \"fail\"\n"
        "  path_must_exist_or_glob: true\n"
        "  allowlist_must_shrink_after_phase: \"PHASE02\"\n"
        "  final_zero_task: \"P22-T03\"\n",
        encoding="utf-8",
    )
    (wp / "legacy-bypass-inventory.yaml").write_text(
        "inventory:\n"
        "  - path: \"src/backend/zuno/__init__.py\"\n"
        "    symbol: \"legacy_alias_registry\"\n"
        "    owner: \"Repository Governance\"\n"
        "    category: \"root_alias\"\n",
        encoding="utf-8",
    )


def _retarget_verifier(monkeypatch, verifier, repo_root: Path) -> None:
    monkeypatch.setattr(verifier, "REPO_ROOT", repo_root)
    monkeypatch.setattr(verifier, "PRODUCTION_ROOTS", (
        repo_root / "src" / "backend" / "zuno",
        repo_root / "apps" / "web" / "src",
        repo_root / "apps" / "desktop" / "src",
    ))
    monkeypatch.setattr(verifier, "HISTORY_ROOTS", (repo_root / "docs" / "history",))
    monkeypatch.setattr(verifier, "PUBLIC_ADAPTER_ROOTS", (
        repo_root / "src" / "backend" / "zuno" / "api" / "v1",
        repo_root / "src" / "backend" / "zuno" / "api" / "v2",
        repo_root / "src" / "backend" / "zuno" / "adapters" / "versioned",
    ))
    wp = repo_root / ".agent" / "programs" / "work-products"
    monkeypatch.setattr(verifier, "FEATURE_FLAG_REGISTRY", wp / "feature-flag-registry.yaml")
    monkeypatch.setattr(verifier, "TEMPORARY_ALLOWLIST", wp / "temporary-allowlist.yaml")
    monkeypatch.setattr(verifier, "LEGACY_BYPASS_INVENTORY", wp / "legacy-bypass-inventory.yaml")
    monkeypatch.setattr(verifier, "COMPLETION_SERVICE", repo_root / "src" / "backend" / "zuno" / "api" / "services" / "completion.py")
    monkeypatch.setattr(verifier, "COMPLETION_ROUTE", repo_root / "src" / "backend" / "zuno" / "api" / "v1" / "completion.py")
    monkeypatch.setattr(verifier, "PHASE08_CUTOVER", repo_root / "src" / "backend" / "zuno" / "agent" / "runtime" / "phase08_cutover.py")
    monkeypatch.setattr(verifier, "CANONICAL_VENDOR_SHIM", repo_root / "src" / "backend" / "zuno" / "platform" / "vendor" / "fastapi_jwt_auth")
    monkeypatch.setattr(verifier, "RETIRED_FORBIDDEN_PATHS", (
        repo_root / "src" / "backend" / "zuno" / "platform" / "compatibility",
        repo_root / "src" / "backend" / "zuno" / "platform" / "compatibility" / "legacy_aliases.py",
        repo_root / "tests" / "legacy_guards",
    ))


@pytest.fixture
def temp_canonical_root(tmp_path):
    _seed_canonical_minimum(tmp_path)
    completion_dir = tmp_path / "src" / "backend" / "zuno" / "api" / "services"
    completion_dir.mkdir(parents=True, exist_ok=True)
    (completion_dir / "completion.py").write_text(
        "def stream_unified_runtime():\n    pass\n_marker_ = \"completion rollback mode is retired after PHASE22 cutover\"\n",
        encoding="utf-8",
    )
    v1 = tmp_path / "src" / "backend" / "zuno" / "api" / "v1"
    v1.mkdir(parents=True)
    (v1 / "completion.py").write_text(
        "from zuno.api.services.completion import stream_unified_runtime\nstream_unified_runtime()\n",
        encoding="utf-8",
    )
    runtime_dir = tmp_path / "src" / "backend" / "zuno" / "agent" / "runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "phase08_cutover.py").write_text(
        "from dataclasses import dataclass\n@dataclass\nclass Phase08CutoverController:\n    mode: str = \"new_default\"\n    def handle(self, request):\n        return None\n",
        encoding="utf-8",
    )
    return tmp_path


def test_clean_canonical_fixture_audits_clean(monkeypatch, verifier, temp_canonical_root):
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert result.runtime_blockers == [], result.runtime_blockers
    assert result.dual_path_blockers == [], result.dual_path_blockers
    assert result.alias_bypass_blockers == [], result.alias_bypass_blockers
    assert result.public_adapter_violations == [], result.public_adapter_violations
    assert result.unresolved == [], result.unresolved
    assert result.category == "LEGACY_CUTOVER_AUDIT_CLEAN"


def test_fallback_to_legacy_is_surfaced(monkeypatch, verifier, temp_canonical_root):
    runtime = temp_canonical_root / "src" / "backend" / "zuno" / "agent" / "runtime" / "phase08_cutover.py"
    runtime.write_text(
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class Phase08CutoverController:\n"
        "    mode: str\n"
        "    legacy_runner: object\n"
        "    def handle(self, request):\n"
        "        if self.mode == \"rollback\":\n"
        "            return self._run_legacy(request, allow_side_effect=True)\n"
        "        if self.mode == \"shadow\":\n"
        "            return self._run_legacy(request, allow_side_effect=True)\n"
        "        if self.mode == \"canary\":\n"
        "            return self._run_legacy(request, allow_side_effect=False)\n"
        "        try:\n"
        "            return None\n"
        "        except Exception as exc:\n"
        "            return self._fallback_to_legacy(request, exc)\n"
        "    def _run_legacy(self, request, *, allow_side_effect):\n"
        "        return self.legacy_runner(request, allow_side_effect)\n"
        "    def _fallback_to_legacy(self, request, exc):\n"
        "        return self._run_legacy(request, allow_side_effect=True)\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("legacy_runner" in u for u in result.unresolved), result.unresolved
    assert any("_fallback_to_legacy" in u for u in result.unresolved)
    assert any("_run_legacy" in u for u in result.unresolved)
    for literal in ("rollback", "shadow", "canary"):
        assert any(literal in u for u in result.unresolved), (literal, result.unresolved)
    assert result.category == "AUDIT_UNRESOLVED"


def test_legacy_runner_injection_is_surfaced(monkeypatch, verifier, temp_canonical_root):
    runtime = temp_canonical_root / "src" / "backend" / "zuno" / "agent" / "runtime" / "phase08_cutover.py"
    runtime.write_text(
        "from dataclasses import dataclass\n"
        "from zuno.agent.composition import get_legacy_runner\n"
        "@dataclass\n"
        "class Phase08CutoverController:\n"
        "    mode: str = \"new_default\"\n"
        "    legacy_runner = get_legacy_runner()\n"
        "    def handle(self, request):\n"
        "        if self.mode == \"rollback\":\n"
        "            return self.legacy_runner(request, True)\n"
        "        return None\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("legacy_runner" in u for u in result.unresolved)
    assert result.category == "AUDIT_UNRESOLVED"


def test_rollback_mode_is_surfaced(monkeypatch, verifier, temp_canonical_root):
    runtime = temp_canonical_root / "src" / "backend" / "zuno" / "agent" / "runtime" / "phase08_cutover.py"
    runtime.write_text(
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class Phase08CutoverController:\n"
        "    mode: str = \"rollback\"\n"
        "    legacy_runner: object = None\n"
        "    def handle(self, request):\n"
        "        if self.mode == \"rollback\":\n"
        "            return self._run_legacy(request)\n"
        "        return None\n"
        "    def _run_legacy(self, request):\n"
        "        return None\n"
        "    def _fallback_to_legacy(self, request, exc):\n"
        "        return None\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("rollback" in u for u in result.unresolved), result.unresolved


def test_shadow_legacy_primary_is_surfaced(monkeypatch, verifier, temp_canonical_root):
    runtime = temp_canonical_root / "src" / "backend" / "zuno" / "agent" / "runtime" / "phase08_cutover.py"
    runtime.write_text(
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class Phase08CutoverController:\n"
        "    mode: str = \"shadow\"\n"
        "    legacy_runner: object = None\n"
        "    def handle(self, request):\n"
        "        if self.mode == \"shadow\":\n"
        "            return self._run_legacy(request)\n"
        "        return None\n"
        "    def _run_legacy(self, request):\n"
        "        return None\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("shadow" in u for u in result.unresolved)


def test_canary_legacy_shadow_is_surfaced(monkeypatch, verifier, temp_canonical_root):
    runtime = temp_canonical_root / "src" / "backend" / "zuno" / "agent" / "runtime" / "phase08_cutover.py"
    runtime.write_text(
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class Phase08CutoverController:\n"
        "    mode: str = \"canary\"\n"
        "    legacy_runner: object = None\n"
        "    def handle(self, request):\n"
        "        if self.mode == \"canary\":\n"
        "            return self._run_legacy(request)\n"
        "        return None\n"
        "    def _run_legacy(self, request):\n"
        "        return None\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("canary" in u for u in result.unresolved)


def test_exception_automatic_fallback_to_legacy_is_surfaced(monkeypatch, verifier, temp_canonical_root):
    runtime = temp_canonical_root / "src" / "backend" / "zuno" / "agent" / "runtime" / "phase08_cutover.py"
    runtime.write_text(
        "from dataclasses import dataclass\n"
        "@dataclass\n"
        "class Phase08CutoverController:\n"
        "    mode: str = \"new_default\"\n"
        "    legacy_runner: object = None\n"
        "    def handle(self, request):\n"
        "        try:\n"
        "            raise RuntimeError(\"new runtime down\")\n"
        "        except Exception as exc:\n"
        "            return self._fallback_to_legacy(request, exc)\n"
        "    def _run_legacy(self, request):\n"
        "        return None\n"
        "    def _fallback_to_legacy(self, request, exc):\n"
        "        return self._run_legacy(request)\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("_fallback_to_legacy" in u for u in result.unresolved)


def test_general_agent_in_completion_route_is_runtime_blocker(monkeypatch, verifier, temp_canonical_root):
    services = temp_canonical_root / "src" / "backend" / "zuno" / "api" / "services"
    services.mkdir(parents=True, exist_ok=True)
    (services / "completion.py").write_text(
        "from zuno.agent.core.agents import GeneralAgent\n"
        "def stream():\n"
        "    return GeneralAgent.astream()\n",
        encoding="utf-8",
    )
    v1 = temp_canonical_root / "src" / "backend" / "zuno" / "api" / "v1"
    v1.mkdir(parents=True, exist_ok=True)
    (v1 / "completion.py").write_text(
        "from zuno.api.services.completion import stream\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("GeneralAgent" in m for m in result.runtime_blockers)


def test_public_adapter_direct_dao_write_is_violation(monkeypatch, verifier, temp_canonical_root):
    v1 = temp_canonical_root / "src" / "backend" / "zuno" / "api" / "v1"
    v1.mkdir(parents=True, exist_ok=True)
    (v1 / "adapter.py").write_text(
        "from zuno.api.dto.workspace import WorkspaceDTO\n"
        "from zuno.platform.database.dao.workspace import WorkspaceDao\n"
        "def write(workspace_id, payload):\n"
        "    WorkspaceDao().insert(workspace_id, payload)\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("WorkspaceDao.insert" in v for v in result.public_adapter_violations), result.public_adapter_violations
    assert result.category == "PUBLIC_ADAPTER_OWNERSHIP_VIOLATION"


def test_public_adapter_application_service_is_clean(monkeypatch, verifier, temp_canonical_root):
    v1 = temp_canonical_root / "src" / "backend" / "zuno" / "api" / "v1"
    v1.mkdir(parents=True, exist_ok=True)
    (v1 / "adapter.py").write_text(
        "from zuno.api.services.workspace import WorkspaceService\n"
        "def write(workspace_id, payload):\n"
        "    WorkspaceService.execute(workspace_id, payload)\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert result.public_adapter_violations == [], result.public_adapter_violations


def test_old_root_import_is_alias_bypass(monkeypatch, verifier, temp_canonical_root):
    backend = temp_canonical_root / "src" / "backend" / "zuno" / "agent"
    backend.mkdir(parents=True, exist_ok=True)
    (backend / "service.py").write_text(
        "from zuno.services.storage import storage_client\n"
        "from zuno.core import helpers\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("zuno.services" in m for m in result.alias_bypass_blockers)
    assert any("zuno.core" in m for m in result.alias_bypass_blockers)


def test_dynamic_legacy_import_is_alias_bypass(monkeypatch, verifier, temp_canonical_root):
    backend = temp_canonical_root / "src" / "backend" / "zuno" / "agent"
    backend.mkdir(parents=True, exist_ok=True)
    (backend / "loader.py").write_text(
        "import importlib\n"
        "module = importlib.import_module('zuno.services.deepsearch')\n"
        "m2 = __import__('zuno.tools')\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("importlib.import_module" in m for m in result.alias_bypass_blockers)
    assert any("__import__" in m for m in result.alias_bypass_blockers)


def test_sys_meta_path_hook_is_alias_bypass(monkeypatch, verifier, temp_canonical_root):
    backend = temp_canonical_root / "src" / "backend" / "zuno" / "platform"
    backend.mkdir(parents=True, exist_ok=True)
    (backend / "hook.py").write_text(
        "import sys\n"
        "class _Finder:\n"
        "    def find_module(self, name, path=None):\n"
        "        return None\n"
        "sys.meta_path.insert(0, _Finder())\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("sys.meta_path" in m for m in result.alias_bypass_blockers)


def test_sys_modules_aliasing_is_alias_bypass(monkeypatch, verifier, temp_canonical_root):
    backend = temp_canonical_root / "src" / "backend" / "zuno" / "platform"
    backend.mkdir(parents=True, exist_ok=True)
    (backend / "alias_module.py").write_text(
        "import sys\n"
        "import zuno.services.storage as _real\n"
        "sys.modules['zuno.services'] = sys.modules['zuno.platform.services.storage']\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("sys.modules" in m for m in result.alias_bypass_blockers)


def test_try_canonical_except_legacy_fallback(monkeypatch, verifier, temp_canonical_root):
    backend = temp_canonical_root / "src" / "backend" / "zuno" / "agent"
    backend.mkdir(parents=True, exist_ok=True)
    (backend / "shim.py").write_text(
        "try:\n"
        "    from zuno.agent.core.agents import GeneralAgent\n"
        "except ImportError:\n"
        "    from zuno.core.agents.general_agent import GeneralAgent\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("zuno.core" in m for m in result.alias_bypass_blockers)


def test_typescript_legacy_path_is_runtime_blocker(monkeypatch, verifier, temp_canonical_root):
    web = temp_canonical_root / "apps" / "web" / "src"
    web.mkdir(parents=True, exist_ok=True)
    (web / "page.tsx").write_text(
        "import { something } from '../../legacy/hooks';\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("legacy path" in m for m in result.runtime_blockers), result.runtime_blockers


def test_shell_legacy_env_is_runtime_blocker(monkeypatch, verifier, tmp_path):
    _seed_canonical_minimum(tmp_path)
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir(exist_ok=True)
    (tools_dir / "script.sh").write_text(
        "#!/bin/bash\nexport ZUNO_AGENT_RUNTIME=legacy_general_agent\necho \"fail\"\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, tmp_path)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("legacy runtime env" in m for m in result.runtime_blockers), result.runtime_blockers


def test_workflow_legacy_command_is_runtime_blocker(monkeypatch, verifier, tmp_path):
    _seed_canonical_minimum(tmp_path)
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "ci.yml").write_text(
        "jobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo ZUNO_AGENT_RUNTIME=legacy_general_agent\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, tmp_path)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("legacy command in workflow" in m for m in result.runtime_blockers), result.runtime_blockers


def test_dual_read_marker_in_production(monkeypatch, verifier, temp_canonical_root):
    backend = temp_canonical_root / "src" / "backend" / "zuno" / "platform" / "services" / "pipeline"
    backend.mkdir(parents=True, exist_ok=True)
    (backend / "dual.py").write_text(
        "dual_read = \"always\"\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("DUAL_READ" in m for m in result.dual_path_blockers), result.dual_path_blockers


def test_dual_write_marker_in_production(monkeypatch, verifier, temp_canonical_root):
    backend = temp_canonical_root / "src" / "backend" / "zuno" / "platform" / "services" / "rag"
    backend.mkdir(parents=True, exist_ok=True)
    (backend / "dual_write.py").write_text(
        "dual_write = \"both\"\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("DUAL_WRITE" in m for m in result.dual_path_blockers), result.dual_path_blockers


def test_expired_feature_flag_not_retired_is_dual_path(monkeypatch, verifier, temp_canonical_root):
    registry = temp_canonical_root / ".agent" / "programs" / "work-products" / "feature-flag-registry.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        "flags:\n  - flag: \"bare_expired_flag\"\n    owner: \"01 Product Surface\"\n    scope: \"unspecified\"\n    default: \"DECLARED\"\n    rollback_command: \"set bare_expired_flag=ROLLBACK_WINDOW\"\n    expires_at_phase: \"PHASE10\"\n    retire_task: \"P22-T03\"\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("bare_expired_flag" in m and "not RETIRED" in m for m in result.dual_path_blockers), result.dual_path_blockers
    assert result.category == "DUAL_PATH_BLOCKERS_FOUND"


def test_retired_feature_flag_no_runtime_reader_is_clean(monkeypatch, verifier, temp_canonical_root):
    registry = temp_canonical_root / ".agent" / "programs" / "work-products" / "feature-flag-registry.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        "flags:\n  - flag: \"fully_retired_flag\"\n    owner: \"01 Product Surface\"\n    scope: \"unspecified\"\n    default: \"RETIRED\"\n    rollback_command: \"retired and fail-closed\"\n    expires_at_phase: \"PHASE04\"\n    retire_task: \"P22-T03\"\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert result.dual_path_blockers == [], result.dual_path_blockers


def test_unresolved_dynamic_callout_is_surfaced(monkeypatch, verifier, temp_canonical_root):
    runtime = temp_canonical_root / "src" / "backend" / "zuno" / "agent" / "runtime" / "phase08_cutover.py"
    runtime.write_text(
        "raise IndentationError('dynamic; cannot statically resolve legacy path')\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("phase08_cutover.py" in u for u in result.unresolved)


def test_history_document_is_allowed(monkeypatch, verifier, temp_canonical_root):
    docs_history = temp_canonical_root / "docs" / "history"
    docs_history.mkdir(parents=True)
    (docs_history / "notes.md").write_text(
        "历史档案里允许出现 legacy 关键字\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert result.category == "LEGACY_CUTOVER_AUDIT_CLEAN"


def test_evidence_false_clean_claim_is_noted(monkeypatch, verifier, temp_canonical_root):
    evidence = temp_canonical_root / "docs" / "evidence" / "goal05-phase22-fake-evidence"
    evidence.mkdir(parents=True)
    (evidence / "report.md").write_text(
        "PHASE22 cutover is CLEAN and verified.\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("goal05-phase22-fake-evidence" in n for n in result.notes)


def test_tests_legacy_guards_cannot_reappear(monkeypatch, verifier, temp_canonical_root):
    legacy_guards = temp_canonical_root / "tests" / "legacy_guards"
    legacy_guards.mkdir(parents=True)
    (legacy_guards / "test_aliases.py").write_text("# reintroduced\n", encoding="utf-8")
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("retired shell" in m for m in result.runtime_blockers)


def test_legacy_aliases_py_cannot_reappear(monkeypatch, verifier, temp_canonical_root):
    compat_dir = temp_canonical_root / "src" / "backend" / "zuno" / "platform" / "compatibility"
    compat_dir.mkdir(parents=True, exist_ok=True)
    (compat_dir / "legacy_aliases.py").write_text(
        "_PACKAGE_ALIASES = {}\n_MODULE_ALIASES = {}\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    result = verifier.verify_phase22_final_legacy_cutover()
    assert any("retired shell" in m or "forbidden legacy alias" in m for m in result.runtime_blockers), result.runtime_blockers


def test_verifier_cli_status_table(monkeypatch, verifier):
    summary = verifier._summary(verifier.AuditResult())
    assert summary["category"] == "LEGACY_CUTOVER_AUDIT_CLEAN"
    body = json.dumps(summary)
    assert body


def test_main_emits_correct_category_for_clean_fixture(monkeypatch, verifier, temp_canonical_root):
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    captured = []

    def fake_print(*args, **kwargs):
        captured.append(" ".join(str(a) for a in args))

    monkeypatch.setattr(verifier.sys, "argv", ["verify_phase22_final_legacy_cutover.py"])
    monkeypatch.setattr("builtins.print", fake_print)
    exit_code = verifier.main([])
    assert exit_code == 0
    text = "\n".join(captured)
    assert "LEGACY_CUTOVER_AUDIT_CLEAN" in text


def test_main_emits_dual_path_for_expired_flag(monkeypatch, verifier, temp_canonical_root):
    registry = temp_canonical_root / ".agent" / "programs" / "work-products" / "feature-flag-registry.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        "flags:\n  - flag: \"bare_expired_flag\"\n    owner: \"01 Product Surface\"\n    scope: \"unspecified\"\n    default: \"DECLARED\"\n    rollback_command: \"set bare_expired_flag=ROLLBACK_WINDOW\"\n    expires_at_phase: \"PHASE10\"\n    retire_task: \"P22-T03\"\n",
        encoding="utf-8",
    )
    _retarget_verifier(monkeypatch, verifier, temp_canonical_root)
    captured = []

    def fake_print(*args, **kwargs):
        captured.append(" ".join(str(a) for a in args))

    monkeypatch.setattr(verifier.sys, "argv", ["verify_phase22_final_legacy_cutover.py"])
    monkeypatch.setattr("builtins.print", fake_print)
    exit_code = verifier.main([])
    assert exit_code == 3
    text = "\n".join(captured)
    assert "DUAL_PATH_BLOCKERS_FOUND" in text
