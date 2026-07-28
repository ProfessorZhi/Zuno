from __future__ import annotations

import pytest

from zuno.capability.tool_runtime import SandboxAdapterRegistry, SandboxExecutionResult, SandboxRunner
from zuno.capability.tool_runtime.sandbox import (
    DenoPyodideWasmRunner,
    OciProcessSandboxRunner,
    SandboxDispatch,
    SandboxPolicyViolation,
    SandboxProfile,
)


class _FakeRunner(SandboxRunner):
    def __init__(self, adapter_tier: str) -> None:
        self.adapter_tier = adapter_tier

    def execute(self, *, dispatch: SandboxDispatch, args: dict[str, object]) -> SandboxExecutionResult:
        return SandboxExecutionResult(
            status="SUCCEEDED",
            stdout="sandboxed",
            stderr="",
            exit_code=0,
            output_payload={
                "tier": dispatch.adapter_tier,
                "code": args.get("code", ""),
                "session_ref": dispatch.session_ref,
            },
        )


def test_phase15_wasm_python_sandbox_is_deny_by_default_and_observation_only() -> None:
    dispatch = SandboxAdapterRegistry().prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-python",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={"allowed_paths": ["workspace://inputs/table.csv"]},
    )

    profile = dispatch.dispatch_payload["profile"]
    assert dispatch.adapter_tier == "WASM_PYTHON"
    assert dispatch.dispatch_payload["deno_pyodide_wasm"] is True
    assert dispatch.dispatch_payload["result_boundary"] == "ToolObservationOnly"
    assert profile["denied_env"] is True
    assert profile["denied_host_filesystem"] is True
    assert profile["denied_network_by_default"] is True
    assert profile["denied_subprocess"] is True
    assert profile["denied_ffi"] is True
    assert profile["read_allowlist"] == ["workspace://inputs/table.csv"]
    assert dispatch.session_ref.endswith(":call-python")


def test_phase15_oci_process_sandbox_records_short_lived_container_constraints() -> None:
    dispatch = SandboxAdapterRegistry().prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-cli",
        tool_name="compiler.run",
        adapter_kind="CLI",
        args={"allowed_write_paths": ["workspace://artifacts/"], "allowed_domains": ["pypi.org"]},
    )

    profile = dispatch.dispatch_payload["profile"]
    assert dispatch.adapter_tier == "OCI_PROCESS"
    assert dispatch.dispatch_payload["oci_short_lived_process"] is True
    assert profile["denied_env"] is True
    assert profile["denied_host_filesystem"] is True
    assert profile["denied_network_by_default"] is True
    assert profile["write_allowlist"] == ["workspace://artifacts/"]
    assert profile["egress_allowlist"] == ["pypi.org"]
    assert profile["limits"]["memory_mb"] == 512


def test_phase15_sandbox_registry_fails_closed_when_profile_violates_deny_defaults() -> None:
    profile = SandboxProfile(
        profile_id="sandbox-profile:bad",
        adapter_tier="WASM_PYTHON",
        denied_env=False,
        denied_host_filesystem=True,
        denied_network_by_default=True,
        denied_subprocess=True,
        denied_ffi=True,
    )

    with pytest.raises(SandboxPolicyViolation, match="deny environment"):
        SandboxAdapterRegistry._validate_profile(profile)


def test_phase15_sandbox_registry_executes_matching_runner_contract() -> None:
    registry = SandboxAdapterRegistry(runner_factory=lambda tier: _FakeRunner(tier))
    dispatch = registry.prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-python-execute",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={"code": "print(42)"},
    )

    result = registry.execute(dispatch=dispatch, args={"code": "print(42)"})

    assert result.status == "SUCCEEDED"
    assert result.output_payload["tier"] == "WASM_PYTHON"
    assert result.output_payload["session_ref"] == dispatch.session_ref


def test_phase15_real_runners_fail_closed_when_runtime_dependency_is_missing(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda _name: None)
    dispatch = SandboxAdapterRegistry(runner_factory=lambda tier: _FakeRunner(tier)).prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-runtime-missing",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={"code": "print(42)"},
    )

    with pytest.raises(SandboxPolicyViolation, match="Deno executable unavailable"):
        DenoPyodideWasmRunner().execute(
            dispatch=dispatch,
            args={"code": "print(42)", "pyodide_entrypoint": "file:///opt/zuno/pyodide/pyodide.mjs"},
        )

    oci_dispatch = SandboxAdapterRegistry(runner_factory=lambda tier: _FakeRunner(tier)).prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-oci-missing",
        tool_name="compiler.run",
        adapter_kind="CLI",
        args={"command": "python -V"},
    )
    with pytest.raises(SandboxPolicyViolation, match="Docker executable unavailable"):
        OciProcessSandboxRunner().execute(dispatch=oci_dispatch, args={"command": "python -V"})
