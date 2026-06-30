from __future__ import annotations


def test_toolcard_manifest_v1_covers_execution_policy_and_risk_fields() -> None:
    from zuno.capability.control_plane import (
        SIDE_EFFECT_RISK_MATRIX,
        ToolApprovalPolicy,
        ToolCardManifest,
        ToolExecutionMode,
        ToolSideEffectLevel,
        ToolTrustTier,
    )

    manifest = ToolCardManifest(
        tool_id="mail.draft_and_send",
        owner="capability.tools.send_email",
        capability_domain="mail",
        description_for_model="Draft an email and send it after approval.",
        input_schema={"type": "object", "properties": {"to": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"message_id": {"type": "string"}}},
        execution_mode=ToolExecutionMode.CLI,
        trust_tier=ToolTrustTier.WORKSPACE,
        side_effect_level=ToolSideEffectLevel.WRITE_EXTERNAL,
        approval_policy=ToolApprovalPolicy.APPROVAL_REQUIRED,
        sandbox_profile="network_limited",
        credential_policy="brokered_secret",
        network_policy="egress_mail_only",
        audit_policy="trace_and_review",
        budget={"timeout_seconds": 30, "cost_units": 1},
        failure_modes=("smtp_rejected", "approval_denied"),
        executor_adapter="cli.send_email",
    )

    payload = manifest.to_dict()

    assert payload["tool_id"] == "mail.draft_and_send"
    assert payload["execution_mode"] == "cli"
    assert payload["side_effect_level"] == "write_external"
    assert payload["approval_policy"] == "approval_required"
    assert manifest.requires_approval is True
    assert SIDE_EFFECT_RISK_MATRIX["write_external"]["default_approval_policy"] == "approval_required"
    assert SIDE_EFFECT_RISK_MATRIX["destructive"]["default_sandbox_profile"] == "isolated"


def test_executor_registry_approval_gate_and_result_normalizer_are_traceable() -> None:
    from zuno.agent.harness import ControllerRuntimeState
    from zuno.capability.control_plane import (
        ApprovalGate,
        ExecutorAdapterContract,
        ExecutorRegistry,
        ToolApprovalPolicy,
        ToolCardManifest,
        ToolExecutionMode,
        ToolResultNormalizer,
        ToolSideEffectLevel,
        ToolTrustTier,
    )

    registry = ExecutorRegistry()
    registry.register(
        ExecutorAdapterContract(
            adapter_id="cli.send_email",
            execution_mode=ToolExecutionMode.CLI,
            sandbox_profile="network_limited",
            network_policy="egress_mail_only",
            credential_policy="brokered_secret",
            timeout_seconds=30,
        )
    )
    manifest = ToolCardManifest(
        tool_id="mail.draft_and_send",
        owner="capability.tools.send_email",
        capability_domain="mail",
        description_for_model="Send email after approval.",
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        execution_mode=ToolExecutionMode.CLI,
        trust_tier=ToolTrustTier.WORKSPACE,
        side_effect_level=ToolSideEffectLevel.WRITE_EXTERNAL,
        approval_policy=ToolApprovalPolicy.APPROVAL_REQUIRED,
        sandbox_profile="network_limited",
        credential_policy="brokered_secret",
        network_policy="egress_mail_only",
        audit_policy="trace_and_review",
        budget={"timeout_seconds": 30},
        failure_modes=("approval_denied",),
        executor_adapter="cli.send_email",
    )
    state = ControllerRuntimeState(
        thread_id="thread_1",
        workspace_id="workspace_1",
        user_id="u_1",
        task_id="task_1",
        trace_id="trace_tool",
        goal="Send a project update email",
    )

    adapter = registry.select_executor(manifest)
    decision = ApprovalGate().evaluate(manifest, runtime_state=state, node="act_react_loop")
    normalized = ToolResultNormalizer.normalize(
        tool_id=manifest.tool_id,
        raw_result={"message_id": "msg_1"},
        trace_span_id="span_tool_1",
        audit_ref="audit_tool_1",
    )

    assert adapter.adapter_id == "cli.send_email"
    assert decision.allowed is False
    assert decision.approval_required is True
    assert decision.interrupt is not None
    assert decision.interrupt["trace_id"] == "trace_tool"
    assert decision.interrupt["required_approval"] == "tool:mail.draft_and_send"
    assert normalized.to_dict() == {
        "tool_id": "mail.draft_and_send",
        "status": "success",
        "data": {"message_id": "msg_1"},
        "summary": "mail.draft_and_send completed",
        "error": "",
        "audit_ref": "audit_tool_1",
        "trace_span_id": "span_tool_1",
    }


def test_mcp_trust_contract_labels_untrusted_content_and_scopes_tools() -> None:
    from zuno.capability.control_plane import MCPTrustContract, ToolTrustTier

    trust = MCPTrustContract(
        server_id="mcp-lark",
        transport="stdio",
        trust_tier=ToolTrustTier.USER,
        auth_policy="user_config_required",
        allowed_tools=("send_message", "list_folder_files"),
        scope="workspace",
        origin="user_registered",
        network_policy="stdio_only",
        credential_policy="user_scoped_secret",
        untrusted_content_label="mcp_untrusted_content",
    )

    payload = trust.to_dict()

    assert trust.allows_tool("send_message") is True
    assert trust.allows_tool("delete_calendar") is False
    assert payload["trust_tier"] == "user"
    assert payload["allowed_tools"] == ["send_message", "list_folder_files"]
    assert payload["untrusted_content_label"] == "mcp_untrusted_content"
