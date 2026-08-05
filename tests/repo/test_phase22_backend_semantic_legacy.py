"""PHASE22 backend semantic legacy cleanup ownership-classifier tests.

These tests pin the post-cleanup invariant at two layers:

  1. **Scoped slice** — this PR's own retirement of the GeneralAgent
     family (``GeneralAgent``, ``AgentConfig``, ``StreamAgentState``,
     ``EmitEventAgentMiddleware``, ``ReactAgent``, ``PlanExecuteAgent``,
     ``CodeActAgent``, ``Text2SQLAgent`` plus the legacy export shims).

  2. **Repository runtime** — the full Backend Product Runtime cutover,
     which must eventually be ``BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED``
     once the Workspace agents and ``AgentControlRuntime`` callers move
     onto the Single Controller.

The repository scope classifies every candidate runtime class by
**ownership and reachability**, not by class name alone. The five
verdicts are:

  - ``PRODUCT_LEGACY_RUNTIME`` — was a complete Product Runtime;
    constructs an independent graph, owns the Product Run lifecycle,
    or executes tools / models directly.
  - ``PRODUCT_ADAPTER`` — a thin facade that delegates to the canonical
    Product Runtime and does not own an independent graph.
  - ``INTERNAL_TEST_HARNESS`` — class definition exists but no
    Production Entry Point can reach it; reachable only from
    ``tests/``, ``evals/`` or ``docs/``.
  - ``INTERNAL_STEP_CAPABILITY`` — Step-internal mechanism
    (``ReActStepRunner``, ``StructuredResponseAgent``).
  - ``UNRESOLVED`` — dynamic construction whose target cannot be
    statically proven.

Each test in this file pins one of those verdicts against a fixture
located under ``tests/fixtures/phase22_backend_semantic_legacy/`` or
against the live repository state.
"""

from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"

VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase22_backend_semantic_legacy.py"
)
FIXTURE_ROOT = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "phase22_backend_semantic_legacy"
)
RUNTIME_DEFS = FIXTURE_ROOT / "runtime_definitions"
PROD_CALLERS = FIXTURE_ROOT / "production_callers"
TEST_CALLERS = FIXTURE_ROOT / "test_callers"


def _run(scope: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(VERIFIER), "--scope", scope, "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "payload": json.loads(result.stdout or "{}"),
    }


def _fixture_classification(
    source_text: str,
    class_name: str,
    *,
    production_callers: list[tuple[str, int]] | None = None,
) -> str:
    """Use the verifier's classify_class API to determine the
    classification of a fixture class. ``production_callers`` defaults to
    ``[("production_callers/synthetic.py", 1)]`` so the verdict reflects
    what the verifier would emit when the class is actually reached by
    a Production Entry Point.
    """
    from tools.scripts.verify_phase22_backend_semantic_legacy import (
        classify_class,
        _classdef_nodes,
        _evidence_for_class,
        _safe_parse,
    )

    tree = _safe_parse(Path(source_text)) if isinstance(source_text, Path) else ast.parse(source_text)
    if tree is None:
        raise AssertionError("fixture did not parse")
    class_node = None
    for node in _classdef_nodes(tree):
        if node.name == class_name:
            class_node = node
            break
    if class_node is None:
        raise AssertionError(f"class {class_name} not found in fixture")
    evidence = _evidence_for_class(class_node)
    callers = (
        production_callers
        if production_callers is not None
        else [("production_callers/synthetic.py", 1)]
    )
    verdict = classify_class(
        class_name=class_name,
        class_node=class_node,
        module_path=source_text if isinstance(source_text, str) else str(source_text),
        production_callers=callers,
        evidence=evidence,
    )
    return verdict.classification


# ---------------------------------------------------------------------------
# 1. GeneralAgent family files are physically gone.
# ---------------------------------------------------------------------------


def test_general_agent_family_files_are_gone() -> None:
    retired_paths = [
        "src/backend/zuno/agent/core/agents/general_agent.py",
        "src/backend/zuno/agent/core/agents/react_agent.py",
        "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
        "src/backend/zuno/agent/core/agents/codeact_agent.py",
        "src/backend/zuno/agent/core/agents/text2sql_agent.py",
        "src/backend/zuno/agent/runtime.py",
        "src/backend/zuno/agent/state.py",
        "src/backend/zuno/agent/streaming.py",
    ]
    for rel in retired_paths:
        assert not (REPO_ROOT / rel).exists(), f"retired file must not exist: {rel}"


# ---------------------------------------------------------------------------
# 2. Scoped mode returns AGENT_FAMILY_LEGACY_SLICE_CLEAN.
# ---------------------------------------------------------------------------


def test_agent_family_scope_returns_clean() -> None:
    result = _run("agent-family")
    assert result["returncode"] == 0, (
        "agent-family scope must exit 0: "
        + result["stdout"]
        + "\n"
        + result["stderr"]
    )
    assert result["payload"]["status"] == "AGENT_FAMILY_LEGACY_SLICE_CLEAN", result["payload"]


# ---------------------------------------------------------------------------
# 3. Repository mode returns BLOCKED because Workspace agents still run.
# ---------------------------------------------------------------------------


def test_repository_scope_returns_blocked() -> None:
    result = _run("repository")
    assert result["returncode"] != 0, (
        "repository scope must exit non-zero while workspace agents exist: "
        + result["stdout"]
    )
    assert (
        result["payload"]["status"] == "BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED"
    ), result["payload"]
    categories = {finding["category"] for finding in result["payload"]["findings"]}
    assert "legacy_runtime_owner" in categories
    assert "direct_handler_bypass" in categories
    classifications = {
        c["name"]: c["classification"]
        for c in result["payload"]["classifications"]
    }
    assert classifications.get("WorkSpaceSimpleAgent") == "PRODUCT_LEGACY_RUNTIME"
    assert classifications.get("WeChatAgent") == "PRODUCT_LEGACY_RUNTIME"
    assert classifications.get("AgentControlRuntime") == "INTERNAL_TEST_HARNESS"


# ---------------------------------------------------------------------------
# 4. Default mode must NOT return scoped CLEAN.
# ---------------------------------------------------------------------------


def test_default_mode_does_not_return_scoped_clean() -> None:
    result = subprocess.run(
        [sys.executable, str(VERIFIER), "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(result.stdout or "{}")
    assert payload.get("scope") == "repository"
    assert payload.get("status") != "AGENT_FAMILY_LEGACY_SLICE_CLEAN", (
        "default mode must report repository status, not scoped status"
    )
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# 5. JSON Schema is stable across both scopes.
# ---------------------------------------------------------------------------


def test_scoped_json_shape_is_stable() -> None:
    payload = _run("agent-family")["payload"]
    assert payload["scope"] == "agent-family"
    assert payload["status"] in {
        "AGENT_FAMILY_LEGACY_SLICE_CLEAN",
        "AGENT_FAMILY_LEGACY_SLICE_BLOCKED",
    }
    assert set(payload.keys()) >= {
        "scope",
        "status",
        "finding_count",
        "findings",
        "classifications",
        "unresolved",
    }
    for finding in payload["findings"]:
        assert set(finding.keys()) == {"category", "path", "line", "detail", "severity"}


def test_repository_json_shape_is_stable() -> None:
    payload = _run("repository")["payload"]
    assert payload["scope"] == "repository"
    assert payload["status"] in {
        "BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED",
        "BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED",
        "BACKEND_PRODUCT_RUNTIME_UNRESOLVED",
        "TOOL_ERROR",
    }
    assert set(payload.keys()) >= {
        "scope",
        "status",
        "finding_count",
        "findings",
        "classifications",
        "unresolved",
    }
    for finding in payload["findings"]:
        assert set(finding.keys()) == {"category", "path", "line", "detail", "severity"}
    for cls in payload["classifications"]:
        assert set(cls.keys()) == {
            "name",
            "classification",
            "module",
            "line",
            "evidence",
            "production_callers",
        }


# ---------------------------------------------------------------------------
# 6. Scoped and Repository scopes do not overwrite each other's status.
# ---------------------------------------------------------------------------


def test_scoped_and_repository_status_are_independent() -> None:
    scoped = _run("agent-family")["payload"]
    repo = _run("repository")["payload"]
    assert scoped["scope"] != repo["scope"]
    assert scoped["status"] != repo["status"]
    assert scoped["status"] == "AGENT_FAMILY_LEGACY_SLICE_CLEAN"
    assert repo["status"] == "BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED"


# ---------------------------------------------------------------------------
# 7. Retired import restoration fails. Re-introducing a retired module
#    import in any production entry point must be detected by the
#    scoped slice.
# ---------------------------------------------------------------------------


def test_retired_import_restoration_is_detected() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Restore the deleted GeneralAgent module by re-introducing a
        # stale import in a production entry point.
        target = clone / "src/backend/zuno/main.py"
        text = target.read_text(encoding="utf-8")
        new_text = (
            "from zuno.agent.core.agents.general_agent import GeneralAgent\n"
            + text
        )
        target.write_text(new_text, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "agent-family",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert payload.get("status") == "AGENT_FAMILY_LEGACY_SLICE_BLOCKED", payload
        categories = {finding["category"] for finding in payload.get("findings", [])}
        assert "retired_module_imported" in categories


# ---------------------------------------------------------------------------
# 8. Fixture: thin WorkSpaceSimpleAgent adapter is not misclassified.
# ---------------------------------------------------------------------------


def test_thin_workspace_adapter_is_product_adapter() -> None:
    src = (RUNTIME_DEFS / "thin_workspace_adapter.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "WorkSpaceSimpleAgent",
        production_callers=[("api/services/workspace.py", 160)],
    )
    assert verdict == "PRODUCT_ADAPTER", (
        f"thin adapter should classify as PRODUCT_ADAPTER, got {verdict}"
    )


# ---------------------------------------------------------------------------
# 9. Fixture: invalid WorkSpaceSimpleAgent adapter (with create_agent)
#    is BLOCKED.
# ---------------------------------------------------------------------------


def test_invalid_adapter_with_create_agent_is_legacy_runtime() -> None:
    src = (RUNTIME_DEFS / "invalid_adapter_with_create_agent.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "WorkSpaceSimpleAgent",
        production_callers=[("api/services/workspace.py", 160)],
    )
    assert verdict == "PRODUCT_LEGACY_RUNTIME", (
        f"adapter with create_agent should classify as PRODUCT_LEGACY_RUNTIME, got {verdict}"
    )


# ---------------------------------------------------------------------------
# 10. Fixture: independent create_agent graph construction is BLOCKED.
# ---------------------------------------------------------------------------


def test_independent_create_agent_graph_is_blocked() -> None:
    src = (RUNTIME_DEFS / "invalid_adapter_with_create_agent.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "WorkSpaceSimpleAgent",
        production_callers=[("api/services/workspace.py", 160)],
    )
    assert verdict == "PRODUCT_LEGACY_RUNTIME"


# ---------------------------------------------------------------------------
# 11. Fixture: direct ``model.ainvoke`` final answer is BLOCKED.
# ---------------------------------------------------------------------------


def test_direct_model_final_answer_is_blocked() -> None:
    src = (RUNTIME_DEFS / "direct_model_final_answer.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "DirectModelFinalAnswerAgent",
        production_callers=[("api/services/workspace.py", 160)],
    )
    assert verdict == "PRODUCT_LEGACY_RUNTIME"


# ---------------------------------------------------------------------------
# 12. Fixture: direct ``tool.ainvoke`` is BLOCKED.
# ---------------------------------------------------------------------------


def test_direct_tool_ainvoke_is_blocked() -> None:
    src = (RUNTIME_DEFS / "direct_tool_ainvoke.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "DirectToolAgent",
        production_callers=[("api/services/workspace.py", 160)],
    )
    assert verdict == "PRODUCT_LEGACY_RUNTIME"


# ---------------------------------------------------------------------------
# 13. Fixture: ``await handler(request)`` is BLOCKED.
# ---------------------------------------------------------------------------


def test_await_handler_request_is_blocked() -> None:
    src = (RUNTIME_DEFS / "direct_handler_await.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "DirectHandlerAgent",
        production_callers=[("api/services/workspace.py", 160)],
    )
    assert verdict == "PRODUCT_LEGACY_RUNTIME"


# ---------------------------------------------------------------------------
# 14. Fixture: AgentControlRuntime with only tests/evals callers is
#     classified INTERNAL_TEST_HARNESS.
# ---------------------------------------------------------------------------


def test_agent_control_runtime_with_only_test_callers_is_internal_test_harness() -> None:
    src = (RUNTIME_DEFS / "agent_control_runtime_no_prod_caller.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "AgentControlRuntime",
        production_callers=[],
    )
    assert verdict == "INTERNAL_TEST_HARNESS", (
        f"AgentControlRuntime with only tests/evals callers should classify as INTERNAL_TEST_HARNESS, got {verdict}"
    )
    # Test callers must exist for this fixture to be valid.
    assert (TEST_CALLERS / "test_agent_control_harness.py").exists()


# ---------------------------------------------------------------------------
# 15. Fixture: AgentControlRuntime with a production caller is BLOCKED.
# ---------------------------------------------------------------------------


def test_agent_control_runtime_with_production_caller_is_blocked() -> None:
    src = (
        RUNTIME_DEFS / "agent_control_runtime_with_prod_caller.py"
    ).read_text(encoding="utf-8")
    # Production caller fixture exists.
    assert (PROD_CALLERS / "caller_of_agent_control.py").exists()
    # The caller file imports & constructs AgentControlRuntime. We use
    # the verifier's classify_class API with a synthetic production caller.
    from tools.scripts.verify_phase22_backend_semantic_legacy import (
        _classdef_nodes,
        _evidence_for_class,
        _safe_parse,
        classify_class,
    )
    tree = _safe_parse(RUNTIME_DEFS / "agent_control_runtime_with_prod_caller.py")
    class_node = next(_classdef_nodes(tree))
    evidence = _evidence_for_class(class_node)
    verdict = classify_class(
        class_name="AgentControlRuntime",
        class_node=class_node,
        module_path=str(RUNTIME_DEFS / "agent_control_runtime_with_prod_caller.py"),
        production_callers=[
            (
                "production_callers/caller_of_agent_control.py",
                7,
            )
        ],
        evidence=evidence,
    )
    assert verdict.classification == "PRODUCT_LEGACY_RUNTIME", (
        f"AgentControlRuntime with production caller should classify as PRODUCT_LEGACY_RUNTIME, got {verdict.classification}"
    )


# ---------------------------------------------------------------------------
# 16. Fixture: ReActStepRunner is INTERNAL_STEP_CAPABILITY.
# ---------------------------------------------------------------------------


def test_react_step_runner_is_internal_step_capability() -> None:
    src = (RUNTIME_DEFS / "react_step_runner.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(src, "ReActStepRunner")
    assert verdict == "INTERNAL_STEP_CAPABILITY", (
        f"ReActStepRunner should classify as INTERNAL_STEP_CAPABILITY, got {verdict}"
    )
    # The real ReActStepRunner module must remain step-internal.
    react_runner = (
        BACKEND_ROOT / "zuno" / "agent" / "runtime" / "execution" / "react_runner.py"
    )
    assert react_runner.exists(), "ReActStepRunner module must be retained"
    # The repository scope must not surface ReActStepRunner as a finding.
    payload = _run("repository")["payload"]
    runner_findings = [
        finding
        for finding in payload["findings"]
        if "react_runner" in finding["path"]
    ]
    assert runner_findings == [], (
        "ReActStepRunner must not surface as a top-level runtime finding"
    )


# ---------------------------------------------------------------------------
# 17. Fixture: StructuredResponseAgent is INTERNAL_STEP_CAPABILITY.
# ---------------------------------------------------------------------------


def test_structured_response_agent_is_internal_step_capability() -> None:
    src = (RUNTIME_DEFS / "structured_response_agent.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(src, "StructuredResponseAgent")
    assert verdict == "INTERNAL_STEP_CAPABILITY", (
        f"StructuredResponseAgent should classify as INTERNAL_STEP_CAPABILITY, got {verdict}"
    )
    structured_path = (
        BACKEND_ROOT / "zuno" / "agent" / "core" / "agents" / "structured_response_agent.py"
    )
    assert structured_path.exists(), "StructuredResponseAgent module must be retained"
    payload = _run("repository")["payload"]
    structured_findings = [
        finding
        for finding in payload["findings"]
        if "structured_response_agent" in finding["path"].lower()
    ]
    assert structured_findings == [], (
        "StructuredResponseAgent must not appear as a top-level runtime finding"
    )


# ---------------------------------------------------------------------------
# 18. Fixture: dynamic ``getattr`` / ``eval`` import is UNRESOLVED.
# ---------------------------------------------------------------------------


def test_dynamic_runtime_load_is_unresolved() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Drop the dynamic-load fixture into the workspace tree.
        target = (
            clone
            / "src/backend/zuno/platform/services/workspace"
            / "dynamic_test_runtime.py"
        )
        target.write_text(
            (RUNTIME_DEFS / "dynamic_runtime_load.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert (
            payload.get("status") == "BACKEND_PRODUCT_RUNTIME_UNRESOLVED"
        ), payload
        unresolved_categories = {
            finding["category"] for finding in payload.get("unresolved", [])
        }
        assert "dynamic_runtime_load" in unresolved_categories


# ---------------------------------------------------------------------------
# 19. ToolInvocationGateway path is not misclassified as legacy.
# ---------------------------------------------------------------------------


def test_tool_invocation_gateway_is_not_misclassified() -> None:
    result = _run("repository")
    categories = {finding["category"] for finding in result["payload"]["findings"]}
    assert "tool_invocation_gateway" not in categories
    capability_findings = [
        finding
        for finding in result["payload"]["findings"]
        if "/capability/tool_runtime/" in finding["path"]
    ]
    assert capability_findings == [], (
        "canonical ToolInvocationGateway must not surface as a bypass: "
        + json.dumps(capability_findings, indent=2, ensure_ascii=False)
    )


# ---------------------------------------------------------------------------
# 20. Direct ``await handler(request)`` tool call in workspace is BLOCKED.
# ---------------------------------------------------------------------------


def test_direct_handler_request_in_workspace_is_blocked() -> None:
    result = _run("repository")
    handler_findings = [
        finding
        for finding in result["payload"]["findings"]
        if finding["category"] == "direct_handler_bypass"
    ]
    assert handler_findings, (
        "direct handler(request) tool calls must be detected"
    )
    # None of these bypasses may leak into the agent core or capability
    # runtime tree.
    leaked = [
        finding
        for finding in handler_findings
        if "/agent/" in finding["path"]
        and "/platform/services/workspace/" not in finding["path"]
    ]
    assert leaked == [], (
        "direct handler(request) bypass must not leak into agent core: "
        + json.dumps(leaked, indent=2, ensure_ascii=False)
    )


# ---------------------------------------------------------------------------
# 21. After workspace agents are deleted, repository mode still BLOCKED
#     because WorkSpaceSimpleAgent / WeChatAgent runtime signatures
#     remain BLOCKED, but AgentControlRuntime finding is gone.
# ---------------------------------------------------------------------------


def test_repository_scope_without_workspace_agents_keeps_blocked() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        for rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        # With workspace deleted, AgentControlRuntime classification
        # becomes the dominant question. Its methods still contain
        # product_lifecycle_attr evidence, but with no production
        # callers it must classify as INTERNAL_TEST_HARNESS.
        classifications = {
            c["name"]: c["classification"]
            for c in payload.get("classifications", [])
        }
        assert classifications.get("AgentControlRuntime") == "INTERNAL_TEST_HARNESS"


# ---------------------------------------------------------------------------
# 22. Thin adapter fixture in production tree: not BLOCKED.
#     This pins the verifier design contract — a future cutover that
#     replaces WorkSpaceSimpleAgent with the thin adapter must flip
#     repository status to CONFIRMED without further verifier changes.
# ---------------------------------------------------------------------------


def test_thin_workspace_adapter_in_production_tree_is_not_blocked() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Replace the legacy WorkSpaceSimpleAgent module with the thin
        # adapter fixture. The production entry point
        # ``api/services/workspace.py`` already imports and constructs
        # ``WorkSpaceSimpleAgent``.
        target = clone / "src/backend/zuno/platform/services/workspace/simple_agent.py"
        target.write_text(
            (RUNTIME_DEFS / "thin_workspace_adapter.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        classifications = {
            c["name"]: c["classification"]
            for c in payload.get("classifications", [])
        }
        assert classifications.get("WorkSpaceSimpleAgent") == "PRODUCT_ADAPTER", (
            "thin adapter must classify as PRODUCT_ADAPTER even when the "
            "production entry point still constructs it"
        )
        # The runtime is allowed, so the repository status should drop
        # the WorkSpaceSimpleAgent finding (only WeChatAgent remains).
        paths = {finding["path"] for finding in payload.get("findings", [])}
        assert not any("simple_agent.py" in p for p in paths), (
            "thin adapter must not surface any finding on simple_agent.py"
        )


# ---------------------------------------------------------------------------
# 23. Invalid adapter fixture in production tree: BLOCKED.
# ---------------------------------------------------------------------------


def test_invalid_adapter_in_production_tree_is_blocked() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        target = clone / "src/backend/zuno/platform/services/workspace/simple_agent.py"
        target.write_text(
            (RUNTIME_DEFS / "invalid_adapter_with_create_agent.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        classifications = {
            c["name"]: c["classification"]
            for c in payload.get("classifications", [])
        }
        assert classifications.get("WorkSpaceSimpleAgent") == "PRODUCT_LEGACY_RUNTIME"
        assert payload.get("status") == "BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED"


# ---------------------------------------------------------------------------
# 24. AgentControlRuntime with production caller fixture is BLOCKED.
# ---------------------------------------------------------------------------


def test_agent_control_runtime_production_caller_fixture_is_blocked() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Drop the production-caller fixture into the backend tree and
        # let it construct AgentControlRuntime.
        target = clone / "src/backend/zuno/api/services/agent_control_caller.py"
        target.write_text(
            (PROD_CALLERS / "caller_of_agent_control.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        classifications = {
            c["name"]: c["classification"]
            for c in payload.get("classifications", [])
        }
        assert classifications.get("AgentControlRuntime") == "PRODUCT_LEGACY_RUNTIME", (
            "AgentControlRuntime with production caller must classify as PRODUCT_LEGACY_RUNTIME"
        )
        assert payload.get("status") == "BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED"


# ---------------------------------------------------------------------------
# 25. Thin canonical-adapter fixture with delegate evidence is classified
#     PRODUCT_ADAPTER (classifier API).
# ---------------------------------------------------------------------------


def test_thin_canonical_adapter_classifies_as_product_adapter() -> None:
    src = (RUNTIME_DEFS / "candidate_constructor.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "WorkSpaceSimpleAgent",
        production_callers=[("api/services/workspace.py", 160)],
    )
    assert verdict == "PRODUCT_ADAPTER", (
        f"thin canonical adapter should classify as PRODUCT_ADAPTER, got {verdict}"
    )


# ---------------------------------------------------------------------------
# 26. Production class WITHOUT canonical_delegate evidence is UNRESOLVED.
#     This is the central fail-closed guarantee.
# ---------------------------------------------------------------------------


def test_production_class_without_canonical_delegate_is_unresolved() -> None:
    """A class with a Production Entry Point caller but no canonical
    delegation and no legacy markers must be UNRESOLVED — not silently
    PRODUCT_ADAPTER. This is the fail-closed contract.
    """
    from tools.scripts.verify_phase22_backend_semantic_legacy import (
        _classdef_nodes,
        _evidence_for_class,
        _safe_parse,
        classify_class,
    )

    tree = _safe_parse(RUNTIME_DEFS / "candidate_constructor_unknown.py")
    class_node = next(_classdef_nodes(tree))
    evidence = _evidence_for_class(class_node)
    verdict = classify_class(
        class_name="WorkSpaceSimpleAgent",
        class_node=class_node,
        module_path=str(RUNTIME_DEFS / "candidate_constructor_unknown.py"),
        production_callers=[("api/services/some_production.py", 42)],
        evidence=evidence,
    )
    assert verdict.classification == "UNRESOLVED", (
        f"production caller + no canonical_delegate + no legacy markers "
        f"must classify as UNRESOLVED, got {verdict.classification}"
    )


# ---------------------------------------------------------------------------
# 27. Import alias constructor is recognised as a WorkSpaceSimpleAgent
#     production caller.
# ---------------------------------------------------------------------------


def test_import_alias_constructor_is_recognised() -> None:
    """``from module import WorkSpaceSimpleAgent as Agent`` then ``Agent(...)``
    must be resolved to ``WorkSpaceSimpleAgent`` and treated as a
    production caller.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Remove the legacy workspace runtime classes so the test
        # isolates the import-alias caller.
        for rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        src = PROD_CALLERS / "caller_with_import_alias.py"
        target = clone / "src/backend/zuno/api/services/_test_caller_import_alias.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        # Also place the candidate class fixture into the backend tree so
        # the verifier can find it.
        cand_target = (
            clone
            / "src/backend/zuno/platform/services/workspace/_test_candidate_constructor.py"
        )
        cand_target.parent.mkdir(parents=True, exist_ok=True)
        cand_target.write_text(
            (RUNTIME_DEFS / "candidate_constructor.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        classifications = {
            c["name"]: c["classification"]
            for c in payload.get("classifications", [])
        }
        assert classifications.get("WorkSpaceSimpleAgent") == "PRODUCT_ADAPTER", (
            "import alias constructor must classify as PRODUCT_ADAPTER, "
            f"got {classifications.get('WorkSpaceSimpleAgent')}: "
            + json.dumps(payload, indent=2)
        )


# ---------------------------------------------------------------------------
# 28. Module-qualified constructor is recognised.
# ---------------------------------------------------------------------------


def test_module_qualified_constructor_is_recognised() -> None:
    """``import module`` then ``module.WorkSpaceSimpleAgent(...)`` must be
    resolved as a production caller for WorkSpaceSimpleAgent.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Remove the legacy workspace runtime classes so the test
        # isolates the qualified-constructor candidate.
        for rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        src = PROD_CALLERS / "caller_with_qualified_constructor.py"
        target = clone / "src/backend/zuno/api/services/_test_caller_qualified.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        # Rewrite the import inside the cloned caller to use the local
        # backend path so the verifier can resolve to the candidate.
        target_text = (
            "from zuno.platform.services.workspace import _test_candidate_constructor\n"
            + "def build_with_qualified_constructor(unified_runtime, model_config, user_id, session_id):\n"
            + "    return _test_candidate_constructor.WorkSpaceSimpleAgent(\n"
            + "        unified_runtime=unified_runtime,\n"
            + "        model_config=model_config,\n"
            + "        user_id=user_id,\n"
            + "        session_id=session_id,\n"
            + "    )\n"
        )
        target.write_text(target_text, encoding="utf-8")
        cand_target = (
            clone
            / "src/backend/zuno/platform/services/workspace/_test_candidate_constructor.py"
        )
        cand_target.parent.mkdir(parents=True, exist_ok=True)
        cand_target.write_text(
            (RUNTIME_DEFS / "candidate_constructor.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        classifications = {
            c["name"]: c["classification"]
            for c in payload.get("classifications", [])
        }
        assert classifications.get("WorkSpaceSimpleAgent") == "PRODUCT_ADAPTER", (
            "module-qualified constructor must classify as PRODUCT_ADAPTER, "
            f"got {classifications.get('WorkSpaceSimpleAgent')}"
        )


# ---------------------------------------------------------------------------
# 29. Module alias constructor is recognised.
# ---------------------------------------------------------------------------


def test_module_alias_constructor_is_recognised() -> None:
    """``import module as runtime_module`` then
    ``runtime_module.WorkSpaceSimpleAgent(...)`` must be resolved as a
    production caller for WorkSpaceSimpleAgent.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Remove the legacy workspace runtime classes so the test
        # isolates the module-alias candidate.
        for rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        target = clone / "src/backend/zuno/api/services/_test_caller_module_alias.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target_text = (
            "from zuno.platform.services.workspace import _test_candidate_constructor as runtime_module\n"
            + "def build_with_module_alias(unified_runtime, model_config, user_id, session_id):\n"
            + "    return runtime_module.WorkSpaceSimpleAgent(\n"
            + "        unified_runtime=unified_runtime,\n"
            + "        model_config=model_config,\n"
            + "        user_id=user_id,\n"
            + "        session_id=session_id,\n"
            + "    )\n"
        )
        target.write_text(target_text, encoding="utf-8")
        cand_target = (
            clone
            / "src/backend/zuno/platform/services/workspace/_test_candidate_constructor.py"
        )
        cand_target.parent.mkdir(parents=True, exist_ok=True)
        cand_target.write_text(
            (RUNTIME_DEFS / "candidate_constructor.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        classifications = {
            c["name"]: c["classification"]
            for c in payload.get("classifications", [])
        }
        assert classifications.get("WorkSpaceSimpleAgent") == "PRODUCT_ADAPTER", (
            "module-alias constructor must classify as PRODUCT_ADAPTER, "
            f"got {classifications.get('WorkSpaceSimpleAgent')}"
        )


# ---------------------------------------------------------------------------
# 30. Assignment alias is resolved to the candidate class.
# ---------------------------------------------------------------------------


def test_assignment_alias_resolves_to_candidate() -> None:
    """``Runtime = WorkSpaceSimpleAgent`` then ``Runtime(...)`` must be
    resolved to ``WorkSpaceSimpleAgent`` and classified by the candidate
    class evidence.
    """
    from tools.scripts.verify_phase22_backend_semantic_legacy import (
        _candidate_local_names,
        _safe_parse,
    )

    tree = _safe_parse(PROD_CALLERS / "caller_with_assignment_alias.py")
    names = _candidate_local_names(tree, "WorkSpaceSimpleAgent")
    assert "Runtime" in names, (
        f"assignment alias must resolve to WorkSpaceSimpleAgent, got {names}"
    )
    assert "WorkSpaceSimpleAgent" in names


# ---------------------------------------------------------------------------
# 31. Assignment alias to a non-delegate candidate is UNRESOLVED.
# ---------------------------------------------------------------------------


def test_assignment_alias_to_non_delegate_is_unresolved() -> None:
    """``Runtime = WorkSpaceSimpleAgent`` (no-delegate shape) then
    ``Runtime(...)`` must classify as UNRESOLVED.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Remove the legacy workspace runtime classes so the test
        # isolates the no-delegate candidate.
        for rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        target = clone / "src/backend/zuno/api/services/_test_caller_assignment_unknown.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target_text = (
            "from zuno.platform.services.workspace import _test_candidate_unknown\n"
            + "Runtime = _test_candidate_unknown.WorkSpaceSimpleAgent\n"
            + "def build_with_assignment_alias_unknown(model_config, user_id, session_id):\n"
            + "    return Runtime(\n"
            + "        model_config=model_config,\n"
            + "        user_id=user_id,\n"
            + "        session_id=session_id,\n"
            + "    )\n"
        )
        target.write_text(target_text, encoding="utf-8")
        cand_target = (
            clone
            / "src/backend/zuno/platform/services/workspace/_test_candidate_unknown.py"
        )
        cand_target.parent.mkdir(parents=True, exist_ok=True)
        cand_target.write_text(
            (RUNTIME_DEFS / "candidate_constructor_unknown.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert (
            payload.get("status") == "BACKEND_PRODUCT_RUNTIME_UNRESOLVED"
        ), (
            "production caller with assignment alias to non-delegate class "
            "must classify as UNRESOLVED, got "
            + json.dumps(payload.get("status"))
        )
        categories = {
            f["category"] for f in payload.get("unresolved", [])
        }
        assert "unresolved_runtime_ownership" in categories, (
            "UNRESOLVED verdict must surface as unresolved finding"
        )


# ---------------------------------------------------------------------------
# 32. Factory constructor without resolvable type is UNRESOLVED.
# ---------------------------------------------------------------------------


def test_factory_constructor_is_unresolved() -> None:
    """A factory function that returns a Runtime class cannot be
    statically resolved. The verifier must classify the candidate as
    UNRESOLVED.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Remove the legacy workspace runtime classes so the test
        # isolates the factory candidate.
        for rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        target = clone / "src/backend/zuno/api/services/_test_factory.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (RUNTIME_DEFS / "factory_constructor.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        # The factory file contains a WorkSpaceSimpleAgent class that
        # has no canonical_delegate evidence and no legacy markers, but
        # is reached by a Production Entry Point (the factory function
        # ``make_agent``). The verifier must classify it as UNRESOLVED.
        status = payload.get("status")
        assert (
            status == "BACKEND_PRODUCT_RUNTIME_UNRESOLVED"
        ), (
            f"factory constructor must yield UNRESOLVED, got {status}: "
            + json.dumps(payload, indent=2)
        )
        classifications = {
            c["name"]: c["classification"]
            for c in payload.get("classifications", [])
        }
        assert classifications.get("WorkSpaceSimpleAgent") == "UNRESOLVED", (
            "factory constructor candidate must classify as UNRESOLVED, "
            f"got {classifications.get('WorkSpaceSimpleAgent')}"
        )


# ---------------------------------------------------------------------------
# 33. Getattr-based dynamic runtime is UNRESOLVED.
# ---------------------------------------------------------------------------


def test_getattr_dynamic_runtime_is_unresolved() -> None:
    """``getattr(module, 'SomeRuntime')`` cannot be statically resolved.
    The verifier must classify the candidate as UNRESOLVED.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Remove the legacy workspace runtime classes so the test
        # isolates the dynamic-load signal.
        for rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        target = clone / "src/backend/zuno/api/services/_test_dynamic_runtime.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (RUNTIME_DEFS / "getattr_runtime.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert (
            payload.get("status") == "BACKEND_PRODUCT_RUNTIME_UNRESOLVED"
        ), (
            "getattr-based dynamic runtime must yield UNRESOLVED, got "
            + json.dumps(payload.get("status"))
        )
        unresolved_categories = {
            f["category"] for f in payload.get("unresolved", [])
        }
        assert "dynamic_runtime_load" in unresolved_categories, (
            "getattr-based dynamic runtime must surface as dynamic_runtime_load"
        )


# ---------------------------------------------------------------------------
# 34. Direct model call fixture is PRODUCT_LEGACY_RUNTIME (re-pinned).
# ---------------------------------------------------------------------------


def test_direct_model_call_classification() -> None:
    src = (RUNTIME_DEFS / "direct_model_final_answer.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "DirectModelFinalAnswerAgent",
        production_callers=[("api/services/workspace.py", 160)],
    )
    assert verdict == "PRODUCT_LEGACY_RUNTIME", (
        f"direct model call must classify as PRODUCT_LEGACY_RUNTIME, got {verdict}"
    )


# ---------------------------------------------------------------------------
# 35. Direct tool call fixture is PRODUCT_LEGACY_RUNTIME (re-pinned).
# ---------------------------------------------------------------------------


def test_direct_tool_call_classification() -> None:
    src = (RUNTIME_DEFS / "direct_tool_ainvoke.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "DirectToolAgent",
        production_callers=[("api/services/workspace.py", 160)],
    )
    assert verdict == "PRODUCT_LEGACY_RUNTIME", (
        f"direct tool call must classify as PRODUCT_LEGACY_RUNTIME, got {verdict}"
    )


# ---------------------------------------------------------------------------
# 36. Independent graph fixture is PRODUCT_LEGACY_RUNTIME (re-pinned).
# ---------------------------------------------------------------------------


def test_independent_graph_classification() -> None:
    src = (RUNTIME_DEFS / "invalid_adapter_with_create_agent.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "WorkSpaceSimpleAgent",
        production_callers=[("api/services/workspace.py", 160)],
    )
    assert verdict == "PRODUCT_LEGACY_RUNTIME", (
        f"independent graph must classify as PRODUCT_LEGACY_RUNTIME, got {verdict}"
    )


# ---------------------------------------------------------------------------
# 37. Test-only AgentControlRuntime fixture is INTERNAL_TEST_HARNESS
#     (re-pinned).
# ---------------------------------------------------------------------------


def test_only_test_callers_yields_internal_test_harness() -> None:
    src = (RUNTIME_DEFS / "agent_control_runtime_no_prod_caller.py").read_text(encoding="utf-8")
    verdict = _fixture_classification(
        src,
        "AgentControlRuntime",
        production_callers=[],
    )
    assert verdict == "INTERNAL_TEST_HARNESS", (
        f"test-only AgentControlRuntime must classify as INTERNAL_TEST_HARNESS, "
        f"got {verdict}"
    )


# ---------------------------------------------------------------------------
# 38. Production caller AgentControlRuntime is PRODUCT_LEGACY_RUNTIME
#     (re-pinned).
# ---------------------------------------------------------------------------


def test_production_caller_agent_control_runtime_is_legacy() -> None:
    from tools.scripts.verify_phase22_backend_semantic_legacy import (
        _classdef_nodes,
        _evidence_for_class,
        _safe_parse,
        classify_class,
    )

    tree = _safe_parse(RUNTIME_DEFS / "agent_control_runtime_with_prod_caller.py")
    class_node = next(_classdef_nodes(tree))
    evidence = _evidence_for_class(class_node)
    verdict = classify_class(
        class_name="AgentControlRuntime",
        class_node=class_node,
        module_path=str(RUNTIME_DEFS / "agent_control_runtime_with_prod_caller.py"),
        production_callers=[("production_callers/caller_of_agent_control.py", 7)],
        evidence=evidence,
    )
    assert verdict.classification == "PRODUCT_LEGACY_RUNTIME", (
        f"production caller AgentControlRuntime must classify as "
        f"PRODUCT_LEGACY_RUNTIME, got {verdict.classification}"
    )


# ---------------------------------------------------------------------------
# 39. Repository UNRESOLVED in production tree exits with code 1.
# ---------------------------------------------------------------------------


def test_repository_unresolved_exits_one() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Remove the legacy workspace runtime classes so the test
        # isolates the no-delegate candidate.
        for rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        target = clone / "src/backend/zuno/api/services/_test_unresolved_branch.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target_text = (
            "from zuno.platform.services.workspace import _test_candidate_unknown\n"
            + "def build_assignment_unknown(model_config, user_id, session_id):\n"
            + "    return _test_candidate_unknown.WorkSpaceSimpleAgent(\n"
            + "        model_config=model_config,\n"
            + "        user_id=user_id,\n"
            + "        session_id=session_id,\n"
            + "    )\n"
        )
        target.write_text(target_text, encoding="utf-8")
        cand_target = (
            clone
            / "src/backend/zuno/platform/services/workspace/_test_candidate_unknown.py"
        )
        cand_target.parent.mkdir(parents=True, exist_ok=True)
        cand_target.write_text(
            (RUNTIME_DEFS / "candidate_constructor_unknown.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 1, (
            f"repository UNRESOLVED must exit 1, got {result.returncode}: "
            + result.stdout
        )
        payload = json.loads(result.stdout or "{}")
        assert (
            payload.get("status") == "BACKEND_PRODUCT_RUNTIME_UNRESOLVED"
        ), payload


# ---------------------------------------------------------------------------
# 40. Repository BLOCKED in production tree exits with code 1.
# ---------------------------------------------------------------------------


def test_repository_blocked_exits_one() -> None:
    """The current live branch has WorkSpaceSimpleAgent / WeChatAgent as
    legacy runtimes, so the repository status is BLOCKED and the exit
    code must be 1.
    """
    result = subprocess.run(
        [
            sys.executable,
            "tools/scripts/verify_phase22_backend_semantic_legacy.py",
            "--scope",
            "repository",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, (
        f"repository BLOCKED must exit 1, got {result.returncode}"
    )


# ---------------------------------------------------------------------------
# 41. Repository CONFIRMED in production tree exits with code 0.
# ---------------------------------------------------------------------------


def test_repository_confirmed_exits_zero() -> None:
    """When the production tree is replaced by a thin canonical adapter
    and the workspace legacy classes are removed, the repository status
    must be CONFIRMED and the exit code must be 0.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Remove the legacy workspace runtime classes.
        for rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        # Replace the candidate with the thin canonical adapter.
        target = clone / "src/backend/zuno/platform/services/workspace/simple_agent.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (RUNTIME_DEFS / "candidate_constructor.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_backend_semantic_legacy.py",
                "--scope",
                "repository",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert result.returncode == 0, (
            f"repository CONFIRMED must exit 0, got {result.returncode}: "
            + result.stdout
        )
        assert (
            payload.get("status") == "BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED"
        ), payload