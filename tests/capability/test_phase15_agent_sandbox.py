from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from zuno.capability.tool_runtime.invocation_gateway import ToolInvocationGateway
from zuno.capability.tool_runtime import SandboxAdapterRegistry, SandboxExecutionResult, SandboxRunner
from zuno.capability.tool_runtime.sandbox import (
    DenoPyodideWasmRunner,
    OciProcessSandboxRunner,
    SandboxDispatch,
    SandboxPolicyViolation,
    SandboxProfile,
)
from zuno.platform.contracts import canonical_sha256


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
                "sandbox_adapter_tier": dispatch.adapter_tier,
                "code": args.get("code", ""),
                "session_ref": dispatch.session_ref,
            },
        )


class _FailingRunner(SandboxRunner):
    def __init__(self, adapter_tier: str, reason: str = "sandbox runtime denied") -> None:
        self.adapter_tier = adapter_tier
        self.reason = reason

    def execute(self, *, dispatch: SandboxDispatch, args: dict[str, object]) -> SandboxExecutionResult:
        raise SandboxPolicyViolation(self.reason)


class _LeakyRunner(SandboxRunner):
    def __init__(self, adapter_tier: str) -> None:
        self.adapter_tier = adapter_tier

    def execute(self, *, dispatch: SandboxDispatch, args: dict[str, object]) -> SandboxExecutionResult:
        return SandboxExecutionResult(
            status="SUCCEEDED",
            stdout="token abc123SECRET",
            stderr="",
            exit_code=0,
            output_payload={
                "sandbox_adapter_tier": dispatch.adapter_tier,
                "session_ref": dispatch.session_ref,
                "api_token": "abc123SECRET",
                "email": "person@example.com",
            },
        )


class _RecordingToolUnitOfWork:
    def __init__(self) -> None:
        self.attempts: list[object] = []
        self.sandbox_receipts: list[object] = []

    def __enter__(self) -> _RecordingToolUnitOfWork:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def record_attempt(self, attempt: object) -> None:
        self.attempts.append(attempt)

    def record_sandbox_receipt(self, receipt: object) -> None:
        self.sandbox_receipts.append(receipt)


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
    assert result.output_payload["sandbox_adapter_tier"] == "WASM_PYTHON"
    assert result.output_payload["session_ref"] == dispatch.session_ref


def test_phase15_sandbox_execute_rejects_invalid_runner_output_contract() -> None:
    class _InvalidRunner(SandboxRunner):
        adapter_tier = "WASM_PYTHON"

        def execute(self, *, dispatch: SandboxDispatch, args: dict[str, object]) -> SandboxExecutionResult:
            return SandboxExecutionResult(
                status="SUCCEEDED",
                stdout="",
                stderr="",
                exit_code=0,
                output_payload={"session_ref": dispatch.session_ref},
            )

    registry = SandboxAdapterRegistry(runner_factory=lambda _tier: _InvalidRunner())
    dispatch = registry.prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-invalid-output",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={"code": "print(42)"},
    )

    with pytest.raises(SandboxPolicyViolation, match="adapter tier mismatch"):
        registry.execute(dispatch=dispatch, args={"code": "print(42)"})


def test_phase15_sandbox_execute_validates_session_integrity_expiry_and_size() -> None:
    registry = SandboxAdapterRegistry(runner_factory=lambda tier: _FakeRunner(tier))
    dispatch = registry.prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-integrity",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={"code": "print(42)"},
    )

    tampered_payload = deepcopy(dispatch.dispatch_payload)
    tampered_payload["session"]["call_id"] = "call-tampered"
    tampered_dispatch = replace(dispatch, dispatch_payload=tampered_payload)
    with pytest.raises(SandboxPolicyViolation, match="session integrity hash mismatch"):
        registry.execute(dispatch=tampered_dispatch, args={"code": "print(42)"})

    version_payload = deepcopy(dispatch.dispatch_payload)
    version_payload["session"]["session_version"] = 2
    version_dispatch = replace(
        dispatch,
        dispatch_payload=version_payload,
        session_hash=canonical_sha256(version_payload["session"]),
    )
    with pytest.raises(SandboxPolicyViolation, match="session version mismatch"):
        registry.execute(dispatch=version_dispatch, args={"code": "print(42)"})

    expired_payload = deepcopy(dispatch.dispatch_payload)
    expired_payload["session"]["expires_at"] = (datetime.now(tz=UTC) - timedelta(seconds=1)).isoformat()
    expired_dispatch = replace(
        dispatch,
        dispatch_payload=expired_payload,
        session_hash=canonical_sha256(expired_payload["session"]),
    )
    with pytest.raises(SandboxPolicyViolation, match="session expired"):
        registry.execute(dispatch=expired_dispatch, args={"code": "print(42)"})

    oversized_dispatch = registry.prepare(
        tenant_id="tenant-" + ("x" * 520_000),
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-oversized",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={"code": "print(42)"},
    )
    with pytest.raises(SandboxPolicyViolation, match="session exceeds configured size limit"):
        registry.execute(dispatch=oversized_dispatch, args={"code": "print(42)"})


def test_phase15_gateway_records_sandbox_receipt_when_execution_fails_closed() -> None:
    unit_of_work = _RecordingToolUnitOfWork()
    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: unit_of_work,  # type: ignore[arg-type]
        sandbox_registry=SandboxAdapterRegistry(runner_factory=lambda tier: _FailingRunner(tier)),
    )

    blocked_reason, sandbox_result = gateway._prepare_sandbox_or_block(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        trace_id="thread-sandbox",
        call_id="call-sandbox-fail",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={"code": "print(42)"},
        prepared_id="prepared-tool-action:call-sandbox-fail",
        attempt_id="tool-attempt:call-sandbox-fail",
        receipt_id="tool-execution-receipt:call-sandbox-fail",
    )

    assert blocked_reason == "sandbox runtime denied"
    assert sandbox_result is None
    assert len(unit_of_work.attempts) == 1
    assert len(unit_of_work.sandbox_receipts) == 1
    receipt = unit_of_work.sandbox_receipts[0]
    assert receipt.receipt_payload["sandbox_execution_status"] == "BLOCKED"
    assert receipt.receipt_payload["sandbox_execution"]["sandbox_blocked_reason"] == "sandbox runtime denied"
    assert receipt.receipt_payload["sandbox_execution"]["session_ref"].endswith(":call-sandbox-fail")


def test_phase15_gateway_redacts_sandbox_output_before_receipt_and_observation_boundary() -> None:
    unit_of_work = _RecordingToolUnitOfWork()
    gateway = ToolInvocationGateway(
        unit_of_work_factory=lambda: unit_of_work,  # type: ignore[arg-type]
        sandbox_registry=SandboxAdapterRegistry(runner_factory=lambda tier: _LeakyRunner(tier)),
    )

    blocked_reason, sandbox_result = gateway._prepare_sandbox_or_block(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        trace_id="thread-sandbox",
        call_id="call-sandbox-redact",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={"code": "print(42)", "api_token": "abc123SECRET"},
        prepared_id="prepared-tool-action:call-sandbox-redact",
        attempt_id="tool-attempt:call-sandbox-redact",
        receipt_id="tool-execution-receipt:call-sandbox-redact",
    )

    assert blocked_reason == ""
    assert sandbox_result is not None
    assert sandbox_result.stdout == "[REDACTED_SECRET]"
    assert sandbox_result.output_payload["api_token"] == "[REDACTED_SECRET]"
    assert sandbox_result.output_payload["email"] == "[REDACTED_PII]"
    receipt = unit_of_work.sandbox_receipts[0]
    assert receipt.receipt_payload["sandbox_execution"]["api_token"] == "[REDACTED_SECRET]"
    assert receipt.receipt_payload["sandbox_execution"]["email"] == "[REDACTED_PII]"


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
