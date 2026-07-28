from __future__ import annotations

import pytest

from zuno.capability.tool_runtime import SandboxAdapterRegistry
from zuno.capability.tool_runtime.sandbox import SandboxPolicyViolation, SandboxProfile


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
