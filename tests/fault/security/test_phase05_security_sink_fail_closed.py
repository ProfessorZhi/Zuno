from __future__ import annotations

import pytest


def test_security_sink_outage_blocks_approved_side_effect_before_executor_runs() -> None:
    from zuno.capability.runtime import ToolRuntimeRequest, build_default_tool_control_plane_runtime

    class FailingSecuritySink:
        def record_tool_approval_fact(self, fact: dict) -> None:
            raise RuntimeError(f"security sink unavailable for {fact['status']}")

    runtime = build_default_tool_control_plane_runtime(
        security_approval_sink=FailingSecuritySink()
    )

    with pytest.raises(RuntimeError, match="approved_before_effect"):
        runtime.execute(
            ToolRuntimeRequest(
                tool_id="mail.send",
                arguments={"to": "hr@example.com", "body": "Candidate update"},
                workspace_id="workspace_fault",
                user_id="user_fault",
                task_id="task_fault_mail",
                trace_id="trace_fault_mail",
                model_intent="Send a candidate update email.",
                approved=True,
                approval_comment="Approved by user.",
            )
        )


def test_security_sink_outage_blocks_disabled_tool_before_executor_runs() -> None:
    from zuno.capability.control_plane import (
        ExecutorAdapterContract,
        ToolApprovalPolicy,
        ToolCardManifest,
        ToolExecutionMode,
        ToolSideEffectLevel,
        ToolTrustTier,
    )
    from zuno.capability.runtime import ToolControlPlaneRuntime, ToolRuntimeRequest

    calls: list[dict] = []

    class FailingSecuritySink:
        def record_tool_approval_fact(self, fact: dict) -> None:
            raise RuntimeError(f"security sink unavailable for {fact['status']}")

    runtime = ToolControlPlaneRuntime(security_approval_sink=FailingSecuritySink())
    runtime.register_manifest(
        ToolCardManifest(
            tool_id="shell.destroy",
            owner="capability.tools.shell",
            capability_domain="shell",
            description_for_model="Dangerous shell command.",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            execution_mode=ToolExecutionMode.CLI,
            trust_tier=ToolTrustTier.UNTRUSTED,
            side_effect_level=ToolSideEffectLevel.DESTRUCTIVE,
            approval_policy=ToolApprovalPolicy.DISABLED,
            sandbox_profile="isolated",
            credential_policy="none",
            network_policy="deny_by_default",
            audit_policy="trace_and_review",
            budget={"timeout_seconds": 1},
            executor_adapter="cli.shell.destroy",
        )
    )
    runtime.register_executor_adapter(
        ExecutorAdapterContract(
            adapter_id="cli.shell.destroy",
            execution_mode=ToolExecutionMode.CLI,
            sandbox_profile="isolated",
            network_policy="deny_by_default",
            credential_policy="none",
            timeout_seconds=1,
        ),
        lambda args, context: calls.append({"args": args, "context": context}) or {"status": "success"},
    )

    with pytest.raises(RuntimeError, match="failed_closed_before_effect"):
        runtime.execute(
            ToolRuntimeRequest(
                tool_id="shell.destroy",
                arguments={"command": "rm -rf /"},
                workspace_id="workspace_fault",
                user_id="user_fault",
                task_id="task_fault_shell",
                trace_id="trace_fault_shell",
                model_intent="Run destructive command.",
            )
        )

    assert calls == []
