from __future__ import annotations

from collections.abc import Callable, MutableMapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import json
import shutil
import subprocess
import tempfile
from typing import Any
from urllib.parse import unquote, urlparse

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


@dataclass(frozen=True, slots=True)
class SandboxExecutionResult:
    status: str
    stdout: str
    stderr: str
    exit_code: int
    output_payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SandboxSessionRecord:
    session_ref: str
    session_version: int
    session_hash: str
    profile_hash: str
    limits_hash: str
    expires_at: datetime
    session_size_bytes: int


class SandboxSessionStore:
    def put(self, record: SandboxSessionRecord) -> None:
        raise NotImplementedError

    def get(self, session_ref: str) -> SandboxSessionRecord | None:
        raise NotImplementedError


class InMemorySandboxSessionStore(SandboxSessionStore):
    def __init__(self) -> None:
        self._records: MutableMapping[str, SandboxSessionRecord] = {}

    def put(self, record: SandboxSessionRecord) -> None:
        self._records[record.session_ref] = record

    def get(self, session_ref: str) -> SandboxSessionRecord | None:
        return self._records.get(session_ref)


class SandboxRunner:
    adapter_tier: str

    def execute(self, *, dispatch: SandboxDispatch, args: dict[str, Any]) -> SandboxExecutionResult:
        raise NotImplementedError


class DenoPyodideWasmRunner(SandboxRunner):
    adapter_tier = "WASM_PYTHON"

    def __init__(self, *, deno_executable: str = "deno") -> None:
        self._deno_executable = deno_executable

    def execute(self, *, dispatch: SandboxDispatch, args: dict[str, Any]) -> SandboxExecutionResult:
        deno_path = shutil.which(self._deno_executable)
        if deno_path is None:
            raise SandboxPolicyViolation("Deno executable unavailable for WASM Python sandbox")
        code = str(args.get("code") or args.get("python") or "")
        if not code.strip():
            raise SandboxPolicyViolation("WASM Python sandbox requires explicit code payload")
        pyodide_entrypoint = str(args.get("pyodide_entrypoint") or "")
        if not pyodide_entrypoint:
            raise SandboxPolicyViolation("WASM Python sandbox requires explicit Pyodide entrypoint")
        profile = dispatch.dispatch_payload["profile"]
        payload = {
            "code": code,
            "profile": profile,
            "session": dispatch.dispatch_payload["session"],
        }
        script = _deno_pyodide_runner_script()
        with tempfile.NamedTemporaryFile("w", suffix=".mjs", encoding="utf-8", delete=False) as handle:
            handle.write(script)
            script_path = handle.name
        deno_permissions = _deno_permission_args(
            script_path=script_path,
            pyodide_entrypoint=pyodide_entrypoint,
            profile=profile,
        )
        try:
            completed = subprocess.run(
                [
                    deno_path,
                    "run",
                    "--quiet",
                    "--no-prompt",
                    "--no-config",
                    "--no-lock",
                    "--no-npm",
                    "--no-remote",
                    *deno_permissions,
                    script_path,
                    pyodide_entrypoint,
                ],
                input=json.dumps(payload, ensure_ascii=True, sort_keys=True),
                text=True,
                capture_output=True,
                env={},
                timeout=int(profile["limits"]["wall_time_seconds"]),
            )
        except subprocess.TimeoutExpired as exc:
            raise SandboxPolicyViolation("WASM Python sandbox timed out") from exc
        finally:
            try:
                import os

                os.unlink(script_path)
            except OSError:
                pass
        stdout = completed.stdout[: int(profile["limits"]["output_bytes"])]
        stderr = completed.stderr[: int(profile["limits"]["output_bytes"])]
        return SandboxExecutionResult(
            status="SUCCEEDED" if completed.returncode == 0 else "FAILED",
            stdout=stdout,
            stderr=stderr,
            exit_code=completed.returncode,
            output_payload={
                "sandbox_adapter_tier": "WASM_PYTHON",
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": completed.returncode,
                "session_ref": dispatch.session_ref,
            },
        )


class OciProcessSandboxRunner(SandboxRunner):
    adapter_tier = "OCI_PROCESS"

    def __init__(self, *, docker_executable: str = "docker", image: str = "python:3.12-alpine") -> None:
        self._docker_executable = docker_executable
        self._image = image

    def execute(self, *, dispatch: SandboxDispatch, args: dict[str, Any]) -> SandboxExecutionResult:
        docker_path = shutil.which(self._docker_executable)
        if docker_path is None:
            raise SandboxPolicyViolation("Docker executable unavailable for OCI process sandbox")
        command = _command_arg(args)
        if not command:
            raise SandboxPolicyViolation("OCI process sandbox requires explicit command payload")
        profile = dispatch.dispatch_payload["profile"]
        egress_allowlist = [str(domain) for domain in profile["egress_allowlist"] if str(domain).strip()]
        egress_proxy_url = str(args.get("egress_proxy_url") or args.get("egress_proxy") or "").strip()
        if egress_allowlist and not egress_proxy_url:
            raise SandboxPolicyViolation("OCI process sandbox egress allowlist requires a configured proxy")
        docker_command = [
            docker_path,
            "run",
            "--rm",
            "--network",
            "bridge" if egress_proxy_url else "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            "128",
            "--memory",
            f"{int(profile['limits']['memory_mb'])}m",
            "--cpus",
            str(max(1, int(profile["limits"]["cpu_seconds"]))),
            "-u",
            "65532:65532",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--tmpfs",
            "/workspace:rw,nosuid,size=128m",
            "--workdir",
            "/workspace",
            *_oci_proxy_env_args(egress_proxy_url=egress_proxy_url, egress_allowlist=egress_allowlist),
            self._image,
            "sh",
            "-lc",
            command,
        ]
        try:
            completed = subprocess.run(
                docker_command,
                text=True,
                capture_output=True,
                env={},
                timeout=int(profile["limits"]["wall_time_seconds"]),
            )
        except subprocess.TimeoutExpired as exc:
            raise SandboxPolicyViolation("OCI process sandbox timed out") from exc
        except OSError as exc:
            raise SandboxPolicyViolation(f"OCI process sandbox failed to start: {exc}") from exc
        stdout = completed.stdout[: int(profile["limits"]["output_bytes"])]
        stderr = completed.stderr[: int(profile["limits"]["output_bytes"])]
        if completed.returncode == 125:
            raise SandboxPolicyViolation(f"OCI process sandbox runtime unavailable: {stderr or stdout}")
        return SandboxExecutionResult(
            status="SUCCEEDED" if completed.returncode == 0 else "FAILED",
            stdout=stdout,
            stderr=stderr,
            exit_code=completed.returncode,
            output_payload={
                "sandbox_adapter_tier": "OCI_PROCESS",
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": completed.returncode,
                "session_ref": dispatch.session_ref,
                "image": self._image,
            },
        )


class SandboxAdapterRegistry:
    """Deterministic control-plane wrapper for the real sandbox adapters.

    The current runtime executes fixtures in-process during tests, but provider
    dispatch is allowed only after this registry resolves a concrete target
    adapter profile that matches the canonical PHASE15 sandbox contract.
    """

    def __init__(
        self,
        *,
        runner_factory: Callable[[str], SandboxRunner] | None = None,
        session_store: SandboxSessionStore | None = None,
    ) -> None:
        self._runner_factory = runner_factory or self._default_runner
        self._session_store = session_store or InMemorySandboxSessionStore()

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
        session_ref = f"sandbox-session:{tenant_id}:{workspace_id}:{run_id}:{thread_id}:{call_id}"
        session_hash = canonical_sha256(session_payload)
        profile_payload = profile.to_payload()
        profile_hash = canonical_sha256(profile_payload)
        limits_hash = canonical_sha256(profile.limits.to_payload())
        self._session_store.put(
            SandboxSessionRecord(
                session_ref=session_ref,
                session_version=1,
                session_hash=session_hash,
                profile_hash=profile_hash,
                limits_hash=limits_hash,
                expires_at=profile.limits.expires_at,
                session_size_bytes=len(json.dumps(session_payload, ensure_ascii=True, sort_keys=True).encode("utf-8")),
            )
        )
        return SandboxDispatch(
            sandbox_profile_id=profile.profile_id,
            adapter_tier=profile.adapter_tier,
            session_ref=session_ref,
            session_version=1,
            session_hash=session_hash,
            profile_hash=profile_hash,
            limits_hash=limits_hash,
            dispatch_payload=dispatch_payload,
        )

    def execute(self, *, dispatch: SandboxDispatch, args: dict[str, Any]) -> SandboxExecutionResult:
        self._validate_dispatch_integrity(dispatch)
        self._validate_stored_session(dispatch)
        runner = self._runner_factory(dispatch.adapter_tier)
        if runner.adapter_tier != dispatch.adapter_tier:
            raise SandboxPolicyViolation("sandbox runner tier does not match dispatch profile")
        result = runner.execute(dispatch=dispatch, args=args)
        self._validate_execution_result(dispatch=dispatch, result=result)
        return result

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

    @staticmethod
    def _default_runner(adapter_tier: str) -> SandboxRunner:
        if adapter_tier == "WASM_PYTHON":
            return DenoPyodideWasmRunner()
        if adapter_tier == "OCI_PROCESS":
            return OciProcessSandboxRunner()
        raise SandboxPolicyViolation(f"unsupported sandbox adapter tier: {adapter_tier}")

    def _validate_stored_session(self, dispatch: SandboxDispatch) -> None:
        record = self._session_store.get(dispatch.session_ref)
        if record is None:
            raise SandboxPolicyViolation("sandbox session missing from state store")
        if record.session_version != dispatch.session_version:
            raise SandboxPolicyViolation("sandbox stored session version mismatch")
        if record.session_hash != dispatch.session_hash:
            raise SandboxPolicyViolation("sandbox stored session hash mismatch")
        if record.profile_hash != dispatch.profile_hash:
            raise SandboxPolicyViolation("sandbox stored profile hash mismatch")
        if record.limits_hash != dispatch.limits_hash:
            raise SandboxPolicyViolation("sandbox stored limits hash mismatch")
        if record.expires_at <= datetime.now(tz=UTC):
            raise SandboxPolicyViolation("sandbox stored session expired")
        if record.session_size_bytes > int(dispatch.dispatch_payload["profile"]["limits"]["session_bytes"]):
            raise SandboxPolicyViolation("sandbox stored session exceeds configured size limit")

    @staticmethod
    def _validate_dispatch_integrity(dispatch: SandboxDispatch) -> None:
        session = dispatch.dispatch_payload.get("session")
        profile = dispatch.dispatch_payload.get("profile")
        if not isinstance(session, dict) or not isinstance(profile, dict):
            raise SandboxPolicyViolation("sandbox dispatch missing session or profile payload")
        limits = profile.get("limits")
        if not isinstance(limits, dict):
            raise SandboxPolicyViolation("sandbox dispatch missing limits payload")
        if canonical_sha256(session) != dispatch.session_hash:
            raise SandboxPolicyViolation("sandbox session integrity hash mismatch")
        if canonical_sha256(profile) != dispatch.profile_hash:
            raise SandboxPolicyViolation("sandbox profile integrity hash mismatch")
        if canonical_sha256(limits) != dispatch.limits_hash:
            raise SandboxPolicyViolation("sandbox limits integrity hash mismatch")
        if int(session.get("session_version", 0)) != dispatch.session_version:
            raise SandboxPolicyViolation("sandbox session version mismatch")
        if len(json.dumps(session, ensure_ascii=True, sort_keys=True).encode("utf-8")) > int(limits["session_bytes"]):
            raise SandboxPolicyViolation("sandbox session exceeds configured size limit")
        expires_at = datetime.fromisoformat(str(session["expires_at"]))
        if expires_at <= datetime.now(tz=UTC):
            raise SandboxPolicyViolation("sandbox session expired")

    @staticmethod
    def _validate_execution_result(*, dispatch: SandboxDispatch, result: SandboxExecutionResult) -> None:
        if result.status not in {"SUCCEEDED", "FAILED", "BLOCKED"}:
            raise SandboxPolicyViolation("sandbox execution returned invalid status")
        limits = dispatch.dispatch_payload["profile"]["limits"]
        output_limit = int(limits["output_bytes"])
        if len(result.stdout.encode("utf-8")) > output_limit:
            raise SandboxPolicyViolation("sandbox stdout exceeds configured output limit")
        if len(result.stderr.encode("utf-8")) > output_limit:
            raise SandboxPolicyViolation("sandbox stderr exceeds configured output limit")
        if not isinstance(result.output_payload, dict):
            raise SandboxPolicyViolation("sandbox execution output must be a mapping")
        if len(json.dumps(result.output_payload, ensure_ascii=True, sort_keys=True).encode("utf-8")) > output_limit:
            raise SandboxPolicyViolation("sandbox output payload exceeds configured output limit")
        if result.output_payload.get("sandbox_adapter_tier") != dispatch.adapter_tier:
            raise SandboxPolicyViolation("sandbox output adapter tier mismatch")
        if result.output_payload.get("session_ref") != dispatch.session_ref:
            raise SandboxPolicyViolation("sandbox output session ref mismatch")


def _tuple_arg(args: dict[str, Any], key: str) -> tuple[str, ...]:
    value = args.get(key)
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return (str(value),)


def _command_arg(args: dict[str, Any]) -> str:
    command = args.get("command") or args.get("shell") or args.get("cmd")
    if isinstance(command, str):
        return command
    if isinstance(command, Sequence) and not isinstance(command, (bytes, bytearray, str)):
        return " ".join(str(part) for part in command)
    return ""


def _deno_read_permission_path(entrypoint: str) -> str:
    parsed = urlparse(entrypoint)
    if parsed.scheme == "file":
        return unquote(parsed.path)
    return entrypoint


def _deno_permission_args(*, script_path: str, pyodide_entrypoint: str, profile: dict[str, Any]) -> list[str]:
    read_paths = [script_path, _deno_read_permission_path(pyodide_entrypoint)]
    for allowed_path in profile.get("read_allowlist", []):
        permission_path = _deno_optional_permission_path(str(allowed_path))
        if permission_path:
            read_paths.append(permission_path)
    permissions = [
        "--deny-env",
        "--deny-ffi",
        "--deny-hrtime",
        f"--allow-read={','.join(read_paths)}",
        "--deny-run",
        "--deny-sys",
        "--deny-write",
    ]
    egress_allowlist = [str(domain) for domain in profile.get("egress_allowlist", []) if str(domain).strip()]
    if egress_allowlist:
        permissions.append(f"--allow-net={','.join(egress_allowlist)}")
    else:
        permissions.append("--deny-net")
    return permissions


def _deno_optional_permission_path(path: str) -> str:
    parsed = urlparse(path)
    if parsed.scheme == "file":
        return unquote(parsed.path)
    if parsed.scheme:
        return ""
    return path


def _oci_proxy_env_args(*, egress_proxy_url: str, egress_allowlist: Sequence[str]) -> list[str]:
    if not egress_proxy_url:
        return []
    allowlist = ",".join(str(domain) for domain in egress_allowlist)
    return [
        "--env",
        f"HTTP_PROXY={egress_proxy_url}",
        "--env",
        f"HTTPS_PROXY={egress_proxy_url}",
        "--env",
        "NO_PROXY=localhost,127.0.0.1",
        "--env",
        f"ZUNO_EGRESS_ALLOWLIST={allowlist}",
    ]


def _deno_pyodide_runner_script() -> str:
    return """
const decoder = new TextDecoder();
let input = "";
for await (const chunk of Deno.stdin.readable) {
  input += decoder.decode(chunk);
}
const payload = JSON.parse(input || "{}");
const pyodideEntrypoint = Deno.args[0];
const pyodide = await import(pyodideEntrypoint);
if (!pyodide.loadPyodide) {
  throw new Error("Pyodide entrypoint must export loadPyodide");
}
const runtime = await pyodide.loadPyodide({ stdout: (line) => console.log(line), stderr: (line) => console.error(line) });
const value = await runtime.runPythonAsync(String(payload.code || ""));
console.log(JSON.stringify({ session: payload.session, value }));
""".strip()


__all__ = [
    "SandboxAdapterRegistry",
    "SandboxDispatch",
    "SandboxExecutionResult",
    "SandboxSessionRecord",
    "SandboxSessionStore",
    "SandboxLimits",
    "SandboxPolicyViolation",
    "SandboxProfile",
    "SandboxRunner",
    "InMemorySandboxSessionStore",
    "DenoPyodideWasmRunner",
    "OciProcessSandboxRunner",
]
