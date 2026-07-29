from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from zuno.capability.tool_runtime.invocation_gateway import ToolInvocationGateway, _ExecutePrerequisiteResult
from zuno.capability.tool_runtime import SandboxAdapterRegistry, SandboxExecutionResult, SandboxRunner, InMemorySandboxSessionStore
from zuno.capability.tool_runtime.sandbox import (
    DenoPyodideWasmRunner,
    OciProcessSandboxRunner,
    SandboxDispatch,
    SandboxPolicyViolation,
    SandboxProfile,
    SandboxSessionRecord,
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


class _CompletedProcess:
    def __init__(self, *, stdout: str = "sandboxed", stderr: str = "", returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class _RecordingToolUnitOfWork:
    def __init__(self) -> None:
        self.attempts: list[object] = []
        self.sandbox_sessions: list[object] = []
        self.sandbox_receipts: list[object] = []
        self.effect_reconciliations: list[object] = []
        self.effect_receipts: list[object] = []
        self.observations: list[object] = []
        self.execution_receipts: list[object] = []

    def __enter__(self) -> _RecordingToolUnitOfWork:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def record_attempt(self, attempt: object) -> None:
        self.attempts.append(attempt)

    def record_sandbox_receipt(self, receipt: object) -> None:
        self.sandbox_receipts.append(receipt)

    def record_sandbox_session(self, session: object) -> None:
        self.sandbox_sessions.append(session)

    def get_sandbox_session(self, *, session_ref: str) -> dict[str, object] | None:
        for session in self.sandbox_sessions:
            if getattr(session, "session_ref") == session_ref:
                return {
                    "session_ref": getattr(session, "session_ref"),
                    "tenant_id": getattr(session, "tenant_id"),
                    "workspace_id": getattr(session, "workspace_id"),
                    "run_id": getattr(session, "run_id"),
                    "thread_id": getattr(session, "thread_id"),
                    "call_id": getattr(session, "call_id"),
                    "sandbox_profile_id": getattr(session, "sandbox_profile_id"),
                    "adapter_tier": getattr(session, "adapter_tier"),
                    "session_version": getattr(session, "session_version"),
                    "profile_hash": getattr(session, "profile_hash"),
                    "limits_hash": getattr(session, "limits_hash"),
                    "session_hash": getattr(session, "session_hash"),
                    "expires_at": getattr(session, "expires_at"),
                    "session_size_bytes": getattr(session, "session_size_bytes"),
                }
        return None

    def publish_tool_version(self, *_args: object, **_kwargs: object) -> None:
        return None

    def record_adapter_binding(self, *_args: object, **_kwargs: object) -> None:
        return None

    def install_tool(self, *_args: object, **_kwargs: object) -> None:
        return None

    def activate_tool(self, *_args: object, **_kwargs: object) -> None:
        return None

    def prepare_action(self, *_args: object, **_kwargs: object) -> str:
        return "prepared-action-hash"

    def record_observation(self, observation: object) -> None:
        self.observations.append(observation)

    def record_execution_receipt(self, receipt: object) -> None:
        self.execution_receipts.append(receipt)

    def update_execution_receipt(self, receipt: object) -> None:
        self.execution_receipts.append(receipt)

    def record_bypass_guard(self, *_args: object, **_kwargs: object) -> None:
        return None

    def record_effect_reconciliation(self, reconciliation: object) -> None:
        self.effect_reconciliations.append(reconciliation)

    def record_effect_receipt(self, receipt: object) -> None:
        self.effect_receipts.append(receipt)


class _SandboxObservationOnlyGateway(ToolInvocationGateway):
    def _record_execute_prerequisites(self, **_kwargs: object) -> _ExecutePrerequisiteResult:
        return _ExecutePrerequisiteResult(
            idempotency_scope="tool-side-effect",
            idempotency_key="call-side-effect-sandbox",
            idempotency_generation=1,
            fencing_resource_id="resource:side-effect",
            fencing_lease_id="lease:side-effect",
            fencing_epoch=1,
        )

    def _reauthorize_execute_epoch(self, **_kwargs: object) -> None:
        return None

    def _issue_secret_lease(self, **_kwargs: object) -> str:
        return "security-secret-lease:call-side-effect-sandbox"

    def _complete_execute_prerequisites(self, **_kwargs: object) -> None:
        return None


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


def test_phase15_sandbox_execute_requires_stateful_session_store_entry() -> None:
    preparing_registry = SandboxAdapterRegistry(runner_factory=lambda tier: _FakeRunner(tier))
    dispatch = preparing_registry.prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-stateful-session",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={"code": "print(42)"},
    )

    fresh_registry = SandboxAdapterRegistry(runner_factory=lambda tier: _FakeRunner(tier))
    with pytest.raises(SandboxPolicyViolation, match="session missing from state store"):
        fresh_registry.execute(dispatch=dispatch, args={"code": "print(42)"})

    result = preparing_registry.execute(dispatch=dispatch, args={"code": "print(42)"})
    assert result.status == "SUCCEEDED"


def test_phase15_sandbox_session_store_roundtrip_preserves_stateful_metadata() -> None:
    store = InMemorySandboxSessionStore()
    record = SandboxSessionRecord(
        session_ref="sandbox-session:tenant:workspace:run:thread:call",
        tenant_id="tenant",
        workspace_id="workspace",
        run_id="run",
        thread_id="thread",
        call_id="call",
        sandbox_profile_id="sandbox-profile:wasm-python:v1",
        adapter_tier="WASM_PYTHON",
        session_version=1,
        session_hash="a" * 64,
        profile_hash="b" * 64,
        limits_hash="c" * 64,
        expires_at=datetime.now(tz=UTC) + timedelta(minutes=10),
        session_size_bytes=512,
    )

    store.put(record)
    loaded = store.get("sandbox-session:tenant:workspace:run:thread:call")

    assert loaded == record


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


def test_phase15_gateway_default_registry_persists_sandbox_session_before_execution(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda _name: None)
    unit_of_work = _RecordingToolUnitOfWork()
    gateway = ToolInvocationGateway(unit_of_work_factory=lambda: unit_of_work)  # type: ignore[arg-type]

    blocked_reason, sandbox_result = gateway._prepare_sandbox_or_block(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        trace_id="thread-sandbox",
        call_id="call-db-session",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={"code": "print(42)"},
        prepared_id="prepared-tool-action:call-db-session",
        attempt_id="tool-attempt:call-db-session",
        receipt_id="tool-execution-receipt:call-db-session",
    )

    assert blocked_reason == "Deno executable unavailable for WASM Python sandbox"
    assert sandbox_result is None
    assert len(unit_of_work.sandbox_sessions) == 1
    session = unit_of_work.sandbox_sessions[0]
    assert session.session_ref.endswith(":call-db-session")
    assert session.session_version == 1
    assert len(session.session_hash) == 64
    assert len(unit_of_work.sandbox_receipts) == 1


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


def test_phase15_side_effect_sandbox_output_is_observation_only_before_domain_effect() -> None:
    unit_of_work = _RecordingToolUnitOfWork()
    gateway = _SandboxObservationOnlyGateway(
        unit_of_work_factory=lambda: unit_of_work,  # type: ignore[arg-type]
        infrastructure_unit_of_work_factory=lambda _tenant: object(),  # type: ignore[arg-type]
        sandbox_registry=SandboxAdapterRegistry(runner_factory=lambda tier: _FakeRunner(tier)),
    )
    executor_called = False

    async def executor() -> dict[str, str]:
        nonlocal executor_called
        executor_called = True
        return {"provider_effect_id": "provider-effect:must-not-confirm"}

    result, receipt = asyncio.run(
        gateway.invoke_readonly(
            tool_name="mail.send",
            args={"to": "review@example.com", "body": "hello", "secret_ref": "security-secret-ref:mail"},
            tenant_id="tenant-sandbox",
            workspace_id="workspace-sandbox",
            trace_id="thread-sandbox",
            call_id="call-side-effect-sandbox",
            adapter_kind="API",
            executor=executor,
            readonly=False,
            approved=True,
        )
    )

    assert result == {"provider_effect_id": "provider-effect:must-not-confirm"}
    assert executor_called is True
    assert receipt.status == "completed"
    assert len(unit_of_work.sandbox_receipts) == 0
    assert len(unit_of_work.effect_receipts) == 1
    assert len(unit_of_work.effect_reconciliations) == 0


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


def test_phase15_deno_runner_maps_explicit_path_and_domain_allowlists_to_permissions(monkeypatch) -> None:
    captured_command: list[str] = []
    captured_env: dict[str, str] | None = None
    monkeypatch.setattr("shutil.which", lambda name: f"C:/tools/{name}.exe")

    def fake_run(command: list[str], **_kwargs: object) -> _CompletedProcess:
        nonlocal captured_env
        captured_command.extend(command)
        captured_env = _kwargs.get("env")  # type: ignore[assignment]
        return _CompletedProcess(stdout="42")

    monkeypatch.setattr("subprocess.run", fake_run)
    dispatch = SandboxAdapterRegistry().prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-deno-permissions",
        tool_name="analysis.python",
        adapter_kind="PYTHON",
        args={
            "code": "print(42)",
            "allowed_paths": ["file:///workspace/input.csv", "workspace://logical/input.csv"],
            "allowed_domains": ["example.com"],
        },
    )

    result = DenoPyodideWasmRunner().execute(
        dispatch=dispatch,
        args={
            "code": "print(42)",
            "pyodide_entrypoint": "file:///opt/zuno/pyodide/pyodide.mjs",
        },
    )

    assert result.status == "SUCCEEDED"
    allow_read = next(arg for arg in captured_command if arg.startswith("--allow-read="))
    assert "/opt/zuno/pyodide/pyodide.mjs" in allow_read
    assert "/workspace/input.csv" in allow_read
    assert "workspace://logical/input.csv" not in allow_read
    assert "--allow-net=example.com" in captured_command
    assert "--deny-net" not in captured_command
    assert captured_env == {}


def test_phase15_oci_runner_requires_proxy_for_explicit_egress_allowlist(monkeypatch) -> None:
    monkeypatch.setattr("shutil.which", lambda name: f"C:/tools/{name}.exe")
    dispatch = SandboxAdapterRegistry().prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-oci-egress-no-proxy",
        tool_name="compiler.run",
        adapter_kind="CLI",
        args={"command": "python -V", "allowed_domains": ["pypi.org"]},
    )

    with pytest.raises(SandboxPolicyViolation, match="egress allowlist requires a configured proxy"):
        OciProcessSandboxRunner().execute(dispatch=dispatch, args={"command": "python -V"})


def test_phase15_oci_runner_uses_short_lived_container_and_proxy_env_without_host_mounts(monkeypatch) -> None:
    captured_command: list[str] = []
    captured_env: dict[str, str] | None = None
    monkeypatch.setattr("shutil.which", lambda name: f"C:/tools/{name}.exe")

    def fake_run(command: list[str], **_kwargs: object) -> _CompletedProcess:
        nonlocal captured_env
        captured_command.extend(command)
        captured_env = _kwargs.get("env")  # type: ignore[assignment]
        return _CompletedProcess(stdout="Python 3.12")

    monkeypatch.setattr("subprocess.run", fake_run)
    dispatch = SandboxAdapterRegistry().prepare(
        tenant_id="tenant-sandbox",
        workspace_id="workspace-sandbox",
        run_id="run-sandbox",
        thread_id="thread-sandbox",
        call_id="call-oci-proxy",
        tool_name="compiler.run",
        adapter_kind="CLI",
        args={"command": "python -V", "allowed_domains": ["pypi.org"]},
    )

    result = OciProcessSandboxRunner().execute(
        dispatch=dispatch,
        args={"command": "python -V", "egress_proxy_url": "http://egress-proxy.local:8080"},
    )

    assert result.status == "SUCCEEDED"
    assert captured_command[:3] == ["C:/tools/docker.exe", "run", "--rm"]
    assert captured_command[captured_command.index("--network") + 1] == "bridge"
    assert "--read-only" in captured_command
    assert captured_command[captured_command.index("--cap-drop") + 1] == "ALL"
    assert captured_command[captured_command.index("--security-opt") + 1] == "no-new-privileges"
    assert captured_command[captured_command.index("-u") + 1] == "65532:65532"
    assert "--tmpfs" in captured_command
    assert "--mount" not in captured_command
    assert "-v" not in captured_command
    assert "--volume" not in captured_command
    assert "HTTP_PROXY=http://egress-proxy.local:8080" in captured_command
    assert "HTTPS_PROXY=http://egress-proxy.local:8080" in captured_command
    assert "ZUNO_EGRESS_ALLOWLIST=pypi.org" in captured_command
    assert captured_env == {}
