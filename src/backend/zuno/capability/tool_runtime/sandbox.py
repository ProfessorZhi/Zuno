from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from zuno.platform.contracts import canonical_sha256


class SandboxPolicyViolation(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SandboxLimits:
    cpu_seconds: int
    memory_mb: int
    wall_time_seconds: int
    output_bytes: int
    session_bytes: int
    expires_at: datetime

    def to_payload(self) -> dict[str, Any]:
        return {
            "cpu_seconds": self.cpu_seconds,
            "memory_mb": self.memory_mb,
            "wall_time_seconds": self.wall_time_seconds,
            "output_bytes": self.output_bytes,
            "session_bytes": self.session_bytes,
            "expires_at": self.expires_at.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class SandboxProfile:
    profile_id: str
    adapter_tier: str
    denied_env: bool
    denied_host_filesystem: bool
    denied_network_by_default: bool
    denied_subprocess: bool
    denied_ffi: bool
    read_allowlist: tuple[str, ...] = ()
    write_allowlist: tuple[str, ...] = ()
    egress_allowlist: tuple[str, ...] = ()
    limits: SandboxLimits = field(
        default_factory=lambda: SandboxLimits(
            cpu_seconds=3,
            memory_mb=128,
            wall_time_seconds=5,
            output_bytes=64_000,
            session_bytes=512_000,
            expires_at=datetime.now(tz=UTC) + timedelta(minutes=15),
        )
    )

    def to_payload(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "adapter_tier": self.adapter_tier,
            "denied_env": self.denied_env,
            "denied_host_filesystem": self.denied_host_filesystem,
            "denied_network_by_default": self.denied_network_by_default,
            "denied_subprocess": self.denied_subprocess,
            "denied_ffi": self.denied_ffi,
            "read_allowlist": list(self.read_allowlist),
            "write_allowlist": list(self.write_allowlist),
            "egress_allowlist": list(self.egress_allowlist),
            "limits": self.limits.to_payload(),
        }


@dataclass(frozen=True, slots=True)
class SandboxDispatch:
    sandbox_profile_id: str
    adapter_tier: str
    session_ref: str
    session_version: int
    session_hash: str
    profile_hash: str
    limits_hash: str
    dispatch_payload: dict[str, Any]


class SandboxAdapterRegistry:
    """Deterministic control-plane wrapper for the real sandbox adapters.

    The current runtime executes fixtures in-process during tests, but provider
    dispatch is allowed only after this registry resolves a concrete target
    adapter profile that matches the canonical PHASE15 sandbox contract.
    """

    def prepare(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        run_id: str,
        thread_id: str,
        call_id: str,
        tool_name: str,
        adapter_kind: str,
        args: dict[str, Any],
    ) -> SandboxDispatch:
        profile = self._resolve_profile(tool_name=tool_name, adapter_kind=adapter_kind, args=args)
        self._validate_profile(profile)
        session_payload = {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "run_id": run_id,
            "thread_id": thread_id,
            "call_id": call_id,
            "profile_id": profile.profile_id,
            "session_version": 1,
            "expires_at": profile.limits.expires_at.isoformat(),
        }
        dispatch_payload = {
            "sandbox_contract": "PHASE15_AGENT_SANDBOX_CLOSURE_V1",
            "deno_pyodide_wasm": profile.adapter_tier == "WASM_PYTHON",
            "oci_short_lived_process": profile.adapter_tier == "OCI_PROCESS",
            "tenant_workspace_run_thread_isolation": True,
            "result_boundary": "ToolObservationOnly",
            "profile": profile.to_payload(),
            "session": session_payload,
        }
        return SandboxDispatch(
            sandbox_profile_id=profile.profile_id,
            adapter_tier=profile.adapter_tier,
            session_ref=f"sandbox-session:{tenant_id}:{workspace_id}:{run_id}:{thread_id}:{call_id}",
            session_version=1,
            session_hash=canonical_sha256(session_payload),
            profile_hash=canonical_sha256(profile.to_payload()),
            limits_hash=canonical_sha256(profile.limits.to_payload()),
            dispatch_payload=dispatch_payload,
        )

    def _resolve_profile(self, *, tool_name: str, adapter_kind: str, args: dict[str, Any]) -> SandboxProfile:
        kind = str(adapter_kind).upper()
        lowered_tool = tool_name.lower()
        if kind in {"PYTHON", "WASM_PYTHON", "PYODIDE"} or lowered_tool.endswith(".python"):
            return SandboxProfile(
                profile_id="sandbox-profile:wasm-python:v1",
                adapter_tier="WASM_PYTHON",
                denied_env=True,
                denied_host_filesystem=True,
                denied_network_by_default=True,
                denied_subprocess=True,
                denied_ffi=True,
                read_allowlist=_tuple_arg(args, "allowed_paths"),
                egress_allowlist=_tuple_arg(args, "allowed_domains"),
            )
        return SandboxProfile(
            profile_id="sandbox-profile:oci-process:v1",
            adapter_tier="OCI_PROCESS",
            denied_env=True,
            denied_host_filesystem=True,
            denied_network_by_default=True,
            denied_subprocess=False,
            denied_ffi=True,
            read_allowlist=_tuple_arg(args, "allowed_paths"),
            write_allowlist=_tuple_arg(args, "allowed_write_paths"),
            egress_allowlist=_tuple_arg(args, "allowed_domains"),
            limits=SandboxLimits(
                cpu_seconds=10,
                memory_mb=512,
                wall_time_seconds=30,
                output_bytes=256_000,
                session_bytes=1_048_576,
                expires_at=datetime.now(tz=UTC) + timedelta(minutes=15),
            ),
        )

    @staticmethod
    def _validate_profile(profile: SandboxProfile) -> None:
        if not profile.denied_env:
            raise SandboxPolicyViolation("sandbox must deny environment inheritance by default")
        if not profile.denied_host_filesystem:
            raise SandboxPolicyViolation("sandbox must not mount host filesystem by default")
        if not profile.denied_network_by_default:
            raise SandboxPolicyViolation("sandbox network must be deny-by-default")
        if profile.adapter_tier == "WASM_PYTHON" and (not profile.denied_subprocess or not profile.denied_ffi):
            raise SandboxPolicyViolation("WASM Python sandbox must deny subprocess and ffi")
        if profile.adapter_tier == "OCI_PROCESS" and profile.limits.memory_mb <= 0:
            raise SandboxPolicyViolation("OCI process sandbox requires bounded memory")


def _tuple_arg(args: dict[str, Any], key: str) -> tuple[str, ...]:
    value = args.get(key)
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return (str(value),)


__all__ = [
    "SandboxAdapterRegistry",
    "SandboxDispatch",
    "SandboxLimits",
    "SandboxPolicyViolation",
    "SandboxProfile",
]
