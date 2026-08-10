from __future__ import annotations


def test_read_only_tool_auto_executes_with_sandbox_audit_and_normalized_result() -> None:
    from zuno.capability.control_plane import (
        ExecutorAdapterContract,
        ToolApprovalPolicy,
        ToolCardManifest,
        ToolExecutionMode,
        ToolSideEffectLevel,
        ToolTrustTier,
    )
    from zuno.capability.runtime import ToolControlPlaneRuntime, ToolRuntimeRequest

    runtime = ToolControlPlaneRuntime()
    runtime.register_manifest(
        ToolCardManifest(
            tool_id="filesystem.read",
            owner="capability.tools.filesystem",
            capability_domain="filesystem",
            description_for_model="Read a workspace file.",
            input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
            output_schema={"type": "object"},
            execution_mode=ToolExecutionMode.LOCAL_FUNCTION,
            trust_tier=ToolTrustTier.WORKSPACE,
            side_effect_level=ToolSideEffectLevel.READ,
            approval_policy=ToolApprovalPolicy.AUTO,
            sandbox_profile="workspace_ro",
            credential_policy="none",
            network_policy="deny",
            audit_policy="trace",
            budget={"timeout_seconds": 3},
            executor_adapter="local.filesystem.read",
        )
    )
    runtime.register_executor_adapter(
        ExecutorAdapterContract(
            adapter_id="local.filesystem.read",
            execution_mode=ToolExecutionMode.LOCAL_FUNCTION,
            sandbox_profile="workspace_ro",
            network_policy="deny",
            credential_policy="none",
            timeout_seconds=3,
        ),
        lambda args, context: {
            "status": "success",
            "summary": "read ok",
            "path": args["path"],
            "sandbox_profile": context.sandbox_profile,
            "credential_refs": list(context.credential_refs),
        },
    )

    result = runtime.execute(
        ToolRuntimeRequest(
            tool_id="filesystem.read",
            arguments={"path": "docs/contract.md"},
            workspace_id="workspace_tools",
            user_id="user_tools",
            task_id="task_read",
            trace_id="trace_read",
            model_intent="Read a workspace contract.",
        )
    )

    assert result.status == "completed"
    assert result.approval_required is False
    assert result.security_decision == "allow"
    assert result.normalized_result is not None
    assert result.normalized_result.status == "success"
    assert result.normalized_result.data["path"] == "docs/contract.md"
    assert result.normalized_result.audit_ref == result.audit_event.audit_id
    assert result.sandbox_context.sandbox_profile == "workspace_ro"
    assert result.sandbox_context.network_policy == "deny"
    assert result.sandbox_context.credential_refs == ()
    assert [event["type"] for event in result.task_events] == [
        "tool_call",
        "sandbox_audit",
        "tool_result",
    ]
    assert result.task_events[1]["payload"]["audit"]["sandbox_profile"] == "workspace_ro"


def test_high_side_effect_tool_fails_closed_without_gateway_before_approval() -> None:
    from zuno.capability.control_plane import (
        ExecutorAdapterContract,
        ToolApprovalPolicy,
        ToolCardManifest,
        ToolExecutionMode,
        ToolSideEffectLevel,
        ToolTrustTier,
    )
    from zuno.capability.runtime import (
        InMemoryCredentialBroker,
        ToolControlPlaneRuntime,
        ToolRuntimeRequest,
    )

    timeline: list[dict] = []
    calls: list[dict] = []
    security_facts: list[dict] = []

    class SecurityFactSink:
        def record_tool_approval_fact(self, fact: dict) -> None:
            entry = {"kind": "security_fact", **fact}
            security_facts.append(entry)
            timeline.append(entry)

    broker = InMemoryCredentialBroker()
    broker.register_secret_ref(
        policy="brokered_secret",
        workspace_id="workspace_tools",
        user_id="user_tools",
        secret_ref="credref://workspace_tools/mail",
    )
    runtime = ToolControlPlaneRuntime(
        credential_broker=broker,
        security_approval_sink=SecurityFactSink(),
    )
    runtime.register_manifest(
        ToolCardManifest(
            tool_id="mail.send",
            owner="capability.tools.send_email",
            capability_domain="mail",
            description_for_model="Send email after approval.",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            execution_mode=ToolExecutionMode.API,
            trust_tier=ToolTrustTier.WORKSPACE,
            side_effect_level=ToolSideEffectLevel.WRITE_EXTERNAL,
            approval_policy=ToolApprovalPolicy.APPROVAL_REQUIRED,
            sandbox_profile="network_limited",
            credential_policy="brokered_secret",
            network_policy="egress_mail_only",
            audit_policy="trace_and_review",
            budget={"timeout_seconds": 10},
            executor_adapter="api.mail.send",
        )
    )

    def execute_mail(args, context):
        calls.append(
            {
                "kind": "executor",
                "args": args,
                "credential_refs": context.credential_refs,
                "network_policy": context.network_policy,
            }
        )
        timeline.append({"kind": "executor"})
        return {
            "status": "success",
            "summary": "email sent",
            "message_id": "msg_123",
        }

    runtime.register_executor_adapter(
        ExecutorAdapterContract(
            adapter_id="api.mail.send",
            execution_mode=ToolExecutionMode.API,
            sandbox_profile="network_limited",
            network_policy="egress_mail_only",
            credential_policy="brokered_secret",
            timeout_seconds=10,
        ),
        execute_mail,
    )

    pending = runtime.execute(
        ToolRuntimeRequest(
            tool_id="mail.send",
            arguments={
                "to": "hr@example.com",
                "body": "Candidate update",
                "smtp_password": "raw-secret",
            },
            workspace_id="workspace_tools",
            user_id="user_tools",
            task_id="task_mail",
            trace_id="trace_mail",
            model_intent="Send a candidate update email.",
        )
    )

    # Side-effect execution cannot even enter approval waiting until the
    # formal ToolInvocationGateway is bound. This test intentionally uses the
    # lightweight runtime without persistence factories, so PHASE22 must fail
    # closed before approval or executor dispatch.
    assert pending.status == "blocked"
    assert pending.blocked_reason == "SIDE_EFFECT_GATEWAY_NOT_BOUND"
    assert pending.approval_required is False
    assert pending.normalized_result is None
    assert calls == []
    assert [event["type"] for event in pending.task_events] == [
        "tool_call",
        "sandbox_audit",
        "tool_result",
    ]
    assert pending.audit_event.final_decision == "blocked"
    assert pending.effect_certainty == "NO_EFFECT"
    assert pending.task_events[-1]["payload"]["error"] == "SIDE_EFFECT_GATEWAY_NOT_BOUND"
    assert "raw-secret" not in repr(pending.to_dict())
    assert "raw-secret" not in repr(security_facts)


def test_tool_runtime_blocks_disabled_tool_before_executor_runs() -> None:
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
    facts: list[dict] = []

    class SecurityFactSink:
        def record_tool_approval_fact(self, fact: dict) -> None:
            facts.append(fact)

    runtime = ToolControlPlaneRuntime(security_approval_sink=SecurityFactSink())
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

    result = runtime.execute(
        ToolRuntimeRequest(
            tool_id="shell.destroy",
            arguments={"command": "rm -rf /"},
            workspace_id="workspace_tools",
            user_id="user_tools",
            task_id="task_shell",
            trace_id="trace_shell",
            model_intent="Run destructive command.",
        )
    )

    assert result.status == "blocked"
    assert result.security_decision == "block"
    assert result.normalized_result is None
    assert calls == []
    assert [event["type"] for event in result.task_events] == [
        "tool_call",
        "sandbox_audit",
        "tool_result",
    ]
    assert result.task_events[-1]["payload"]["status"] == "blocked"
    assert [fact["status"] for fact in facts] == ["failed_closed_before_effect"]
    assert facts[0]["security_decision"] == "block"
    assert facts[0]["prepared_action_hash"]
