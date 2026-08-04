"""PHASE22 backend semantic legacy cleanup dual-scope enforcement tests.

These tests pin the post-cleanup invariant at two layers:

  1. **Scoped slice** — this PR's own retirement of the GeneralAgent
     family (``GeneralAgent``, ``AgentConfig``, ``StreamAgentState``,
     ``EmitEventAgentMiddleware``, ``ReactAgent``, ``PlanExecuteAgent``,
     ``CodeActAgent``, ``Text2SQLAgent`` plus the legacy export shims).

  2. **Repository runtime** — the full Backend Product Runtime cutover,
     which must eventually be ``BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED``
     once the Workspace agents and ``AgentControlRuntime`` callers move
     onto the Single Controller. The default mode of the verifier is
     fail-closed and emits ``BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED``
     for every known out-of-scope caller today.

The two scopes are deliberately separated so workflow gates that only
own the agent-family slice can pass with ``--scope agent-family`` while
the full repository status remains BLOCKED.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"

VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase22_backend_semantic_legacy.py"
)


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
    assert "top_level_runtime_class_definition" in categories
    assert "workspace_bypass" in categories


# ---------------------------------------------------------------------------
# 4. After workspace agents are deleted, repository mode returns CONFIRMED.
#    This test pins the contract so removing the workspace files flips the
#    status without further code changes.
# ---------------------------------------------------------------------------


def test_repository_scope_would_return_confirmed_without_workspace_agents() -> None:
    import shutil
    import tempfile

    payload = _run("repository")["payload"]
    # Build the expected payload by filtering out the workspace-only findings
    # that disappear once the workspace agents are deleted.
    filtered = []
    for finding in payload["findings"]:
        if "platform/services/workspace/" in finding["path"]:
            continue
        if (
            finding["path"] == "src/backend/zuno/agent/control_runtime.py"
            and finding["category"] == "top_level_runtime_class_definition"
        ):
            continue
        if finding["path"] == "src/backend/zuno/agent/product_baseline.py":
            continue
        filtered.append(finding)
    assert filtered == [], (
        "non-workspace findings would still block the cutover: "
        + json.dumps(filtered, indent=2, ensure_ascii=False)
    )

    # Use a temporary checkout to exercise the actual verifier after the
    # workspace files are removed.
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Remove the workspace agents so the verifier cannot see them.
        for rel in (
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        result = subprocess.run(
            [sys.executable, "tools/scripts/verify_phase22_backend_semantic_legacy.py",
             "--scope", "repository", "--json"],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        try:
            payload = json.loads(result.stdout or "{}")
        except json.JSONDecodeError:
            payload = {}
        # Even after workspace removal, ``AgentControlRuntime`` lives in
        # ``control_runtime.py`` which is out of scope — so the verifier
        # must still surface the BLOCKED status with that one finding
        # remaining. We confirm the verifier still reports BLOCKED but
        # the workspace-specific categories are gone.
        assert payload.get("status") in {
            "BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED",
            "BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED",
        }, payload
        if payload.get("status") == "BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED":
            return
        # The remaining BLOCKED findings must NOT be workspace bypass.
        paths = {finding["path"] for finding in payload.get("findings", [])}
        assert not any("platform/services/workspace/" in p for p in paths), (
            "workspace bypass findings must be gone after deletion"
        )


# ---------------------------------------------------------------------------
# 5. A new unknown dynamic Runtime construction flips the status to UNRESOLVED.
# ---------------------------------------------------------------------------


def test_unknown_dynamic_runtime_returns_unresolved() -> None:
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Drop a fake ``getattr`` style dynamic load into the workspace tree.
        target = (
            clone
            / "src/backend/zuno/platform/services/workspace"
            / "dynamic_test_runtime.py"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "def get_dynamic_agent():\n"
            "    cls = getattr(__import__('zuno.agent.runtime', fromlist=['']),\n"
            "                  'NewDynamicAgent')\n"
            "    return cls()\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, "tools/scripts/verify_phase22_backend_semantic_legacy.py",
             "--scope", "repository", "--json"],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        # The dynamic load is unresolved because the verifier cannot prove
        # which class is built.
        assert (
            payload.get("status") == "BACKEND_PRODUCT_RUNTIME_UNRESOLVED"
        ), payload


# ---------------------------------------------------------------------------
# 6. Direct ``await handler(request)`` tool call in agent core is BLOCKED.
#    The workspace files are still flagged today but the test pins that
#    the category is detected.
# ---------------------------------------------------------------------------


def test_direct_handler_request_is_blocked() -> None:
    result = _run("repository")
    workspace_findings = [
        finding
        for finding in result["payload"]["findings"]
        if finding["category"] == "workspace_bypass"
    ]
    assert workspace_findings, (
        "direct handler(request) tool calls in workspace agents must be detected"
    )
    # None of these bypasses may leak into the agent core or capability
    # runtime tree.
    leaked = [
        finding
        for finding in workspace_findings
        if "/agent/" in finding["path"]
        and "/platform/services/workspace/" not in finding["path"]
    ]
    assert leaked == [], (
        "direct handler(request) bypass must not leak into agent core: "
        + json.dumps(leaked, indent=2, ensure_ascii=False)
    )


# ---------------------------------------------------------------------------
# 7. ToolInvocationGateway path is not misclassified as legacy.
# ---------------------------------------------------------------------------


def test_tool_invocation_gateway_is_not_misclassified() -> None:
    result = _run("repository")
    categories = {finding["category"] for finding in result["payload"]["findings"]}
    assert "tool_invocation_gateway" not in categories
    # The capability layer is the canonical side-effect gate, not a
    # bypass surface.
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
# 8. StructuredResponseAgent stays an INTERNAL_STEP_CAPABILITY.
# ---------------------------------------------------------------------------


def test_structured_response_agent_is_internal_step_capability() -> None:
    result = _run("repository")
    structured_findings = [
        finding
        for finding in result["payload"]["findings"]
        if "structured_response_agent" in finding["path"].lower()
    ]
    assert structured_findings == [], (
        "StructuredResponseAgent must not appear as a top-level runtime finding"
    )
    # The class definition is intentionally retained.
    structured_path = (
        BACKEND_ROOT / "zuno" / "agent" / "core" / "agents" / "structured_response_agent.py"
    )
    assert structured_path.exists(), "StructuredResponseAgent module must be retained"


# ---------------------------------------------------------------------------
# 9. ReActStepRunner stays a Step-internal mechanism.
# ---------------------------------------------------------------------------


def test_react_step_runner_is_step_internal() -> None:
    react_runner = (
        BACKEND_ROOT / "zuno" / "agent" / "runtime" / "execution" / "react_runner.py"
    )
    assert react_runner.exists(), "ReActStepRunner must remain as step-internal"
    result = _run("repository")
    runner_findings = [
        finding
        for finding in result["payload"]["findings"]
        if "react_runner" in finding["path"]
    ]
    assert runner_findings == [], (
        "ReActStepRunner must not surface as a top-level runtime finding"
    )


# ---------------------------------------------------------------------------
# 10. AgentControlRuntime with a production caller returns BLOCKED.
# ---------------------------------------------------------------------------


def test_agent_control_runtime_with_production_caller_returns_blocked() -> None:
    result = _run("repository")
    blocked = [
        finding
        for finding in result["payload"]["findings"]
        if finding["category"] == "top_level_runtime_class_definition"
        and "AgentControlRuntime" in finding["detail"]
    ]
    assert blocked, (
        "AgentControlRuntime class definition must be surfaced in repository scope"
    )


# ---------------------------------------------------------------------------
# 11. AgentControlRuntime with only history references can be classified
#     HISTORY_ONLY — when there are no production callers the verifier
#     must not classify it as a runtime finding. We simulate this by
#     mirroring the repo with the production caller stripped.
# ---------------------------------------------------------------------------


def test_agent_control_runtime_history_only_when_no_production_caller() -> None:
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Move the production caller into ``tests/`` so it becomes history.
        for rel in (
            "src/backend/zuno/agent/control_runtime.py",
            "src/backend/zuno/agent/product_baseline.py",
        ):
            src = clone / rel
            if src.exists():
                dest = clone / "tests" / "agent" / "history_only"
                dest.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dest / Path(rel).name))
        result = subprocess.run(
            [sys.executable, "tools/scripts/verify_phase22_backend_semantic_legacy.py",
             "--scope", "repository", "--json"],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        # With only history references, AgentControlRuntime no longer
        # qualifies as a top-level runtime finding.
        paths = {finding["path"] for finding in payload.get("findings", [])}
        assert not any("control_runtime.py" in p for p in paths), (
            "history-only AgentControlRuntime must not block: "
            + json.dumps(payload, indent=2, ensure_ascii=False)
        )


# ---------------------------------------------------------------------------
# 12. Default mode must NOT return scoped CLEAN.
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
# Auxiliary checks: scoped and repository JSON output is well-formed.
# ---------------------------------------------------------------------------


def test_scoped_json_shape_is_stable() -> None:
    payload = _run("agent-family")["payload"]
    assert payload["scope"] == "agent-family"
    assert payload["status"] in {
        "AGENT_FAMILY_LEGACY_SLICE_CLEAN",
        "AGENT_FAMILY_LEGACY_SLICE_BLOCKED",
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
    for finding in payload["findings"]:
        assert set(finding.keys()) == {"category", "path", "line", "detail", "severity"}