from __future__ import annotations


def test_capability_record_schema_covers_required_types_and_fields() -> None:
    from zuno.services.application.capabilities import (
        CapabilityCost,
        CapabilityHealth,
        CapabilityPermissions,
        CapabilityRecord,
        CapabilityType,
    )

    assert {item.value for item in CapabilityType} == {
        "Knowledge",
        "ActionTool",
        "MCPTool",
        "MCPResource",
        "MCPPrompt",
        "Skill",
    }

    record = CapabilityRecord(
        name="send_email",
        type=CapabilityType.ACTION_TOOL,
        description="Send an email through the configured mail provider.",
        schema={"type": "object", "properties": {"to": {"type": "string"}}},
        permissions=CapabilityPermissions(scopes=("mail:send",), side_effects=True),
        cost=CapabilityCost(token_estimate=120, latency_ms=300),
        health=CapabilityHealth.READY,
        source="system_tools",
        owner="zuno",
        tags=("email", "message"),
    )

    assert record.to_dict() == {
        "name": "send_email",
        "type": "ActionTool",
        "description": "Send an email through the configured mail provider.",
        "schema": {"type": "object", "properties": {"to": {"type": "string"}}},
        "permissions": {"scopes": ["mail:send"], "side_effects": True},
        "cost": {"token_estimate": 120, "latency_ms": 300, "unit_cost": None},
        "health": "ready",
        "source": "system_tools",
        "owner": "zuno",
        "tags": ["email", "message"],
        "metadata": {},
    }


def test_tool_card_contract_serializes_compact_retrieval_metadata() -> None:
    from zuno.services.application.capabilities import (
        CapabilityCost,
        CapabilityHealth,
        CapabilityPermissions,
        CapabilityRecord,
        CapabilityType,
        ToolCard,
    )

    record = CapabilityRecord(
        name="send_email",
        type=CapabilityType.ACTION_TOOL,
        description="Send an email through the configured mail provider.",
        schema={"type": "object", "properties": {"to": {"type": "string"}}},
        permissions=CapabilityPermissions(scopes=("mail:send",), side_effects=True),
        cost=CapabilityCost(token_estimate=120, latency_ms=300),
        health=CapabilityHealth.READY,
        source="system_tools",
        owner="capability.tools.send_email",
        tags=("email", "message"),
        metadata={"aliases": ["mail_sender"], "examples": ["send a status email"]},
    )

    card = ToolCard.from_capability_record(record)

    assert card.id == "ActionTool:send_email"
    assert card.input_schema_summary == "object: to"
    assert card.owner_module == "capability.tools.send_email"
    assert card.to_dict() == {
        "id": "ActionTool:send_email",
        "name": "send_email",
        "aliases": ["mail_sender"],
        "type": "ActionTool",
        "description": "Send an email through the configured mail provider.",
        "input_schema_summary": "object: to",
        "output_schema_summary": "",
        "permissions": {"scopes": ["mail:send"], "side_effects": True},
        "side_effects": True,
        "cost_hint": {"token_estimate": 120, "latency_ms": 300, "unit_cost": None},
        "latency_hint": 300,
        "health": "ready",
        "examples": ["send a status email"],
        "owner_module": "capability.tools.send_email",
        "source": "system_tools",
        "tags": ["email", "message"],
        "metadata": {"aliases": ["mail_sender"], "examples": ["send a status email"]},
    }


def test_native_bm25_retriever_returns_explainable_tool_card_candidates() -> None:
    from zuno.services.application.capabilities import (
        CapabilityCost,
        CapabilityHealth,
        CapabilityPermissions,
        CapabilityType,
        NativeBM25Retriever,
        ToolCard,
    )

    cards = (
        ToolCard(
            id="mcp_tool:lark:send_message",
            name="send_message",
            aliases=("飞书", "lark"),
            type=CapabilityType.MCP_TOOL,
            description="给飞书联系人发送消息",
            input_schema_summary="object: receiver, text",
            output_schema_summary="message id",
            permissions=CapabilityPermissions(scopes=("mcp:tool:invoke",), side_effects=True),
            cost_hint=CapabilityCost(token_estimate=200),
            health=CapabilityHealth.READY,
            owner_module="capability.mcp.servers.lark_mcp",
            source="user",
            tags=("mcp", "message"),
        ),
        ToolCard(
            id="tool:web_search",
            name="web_search",
            aliases=("search",),
            type=CapabilityType.ACTION_TOOL,
            description="Search public web pages.",
            input_schema_summary="object: query",
            output_schema_summary="web evidence",
            permissions=CapabilityPermissions(scopes=("web:read",), side_effects=False),
            cost_hint=CapabilityCost(token_estimate=100),
            health=CapabilityHealth.READY,
            owner_module="capability.tools.web_search",
            source="system",
            tags=("web",),
        ),
    )

    result = NativeBM25Retriever(cards).search("飞书 发消息", top_k=2)

    assert result[0].tool_card_id == "mcp_tool:lark:send_message"
    assert result[0].score > 0
    assert "飞书" in result[0].matched_terms
    assert result[0].explanation["algorithm"] == "native_bm25"


def test_dynamic_selector_uses_task_relevance_and_does_not_return_every_capability() -> None:
    from zuno.services.application.capabilities import (
        CapabilityCost,
        CapabilityHealth,
        CapabilityPermissions,
        CapabilityRecord,
        CapabilityRegistry,
        CapabilitySelectionRequest,
        CapabilityType,
        DynamicCapabilitySelector,
    )

    registry = CapabilityRegistry(
        [
            CapabilityRecord(
                name="contract_knowledge",
                type=CapabilityType.KNOWLEDGE,
                description="Search contract review evidence and clauses.",
                schema={"retrieval": "graphrag_project"},
                permissions=CapabilityPermissions(scopes=("knowledge:read",)),
                cost=CapabilityCost(token_estimate=800),
                health=CapabilityHealth.READY,
                source="graphrag_project",
                owner="knowledge",
                tags=("contract", "knowledge"),
            ),
            CapabilityRecord(
                name="send_email",
                type=CapabilityType.ACTION_TOOL,
                description="Send email messages to a recipient.",
                schema={"type": "object", "properties": {"to": {"type": "string"}}},
                permissions=CapabilityPermissions(scopes=("mail:send",), side_effects=True),
                cost=CapabilityCost(token_estimate=100),
                health=CapabilityHealth.READY,
                source="tool_service",
                owner="tooling",
                tags=("email", "message"),
            ),
            CapabilityRecord(
                name="paper_search_skill",
                type=CapabilityType.SKILL,
                description="Search academic papers and summarize findings.",
                schema={"tool_name": "paper_search_skill"},
                permissions=CapabilityPermissions(scopes=("web:read",)),
                cost=CapabilityCost(token_estimate=500),
                health=CapabilityHealth.READY,
                source="agent_skill",
                owner="skills",
                tags=("paper", "research"),
            ),
        ]
    )

    result = DynamicCapabilitySelector(registry).select(
        CapabilitySelectionRequest(
            task="Please email the contract review summary to the team",
            allowed_types=(CapabilityType.ACTION_TOOL, CapabilityType.SKILL),
            max_capabilities=2,
        )
    )

    assert [item.name for item in result.capabilities] == ["send_email"]
    assert result.trace.selected_names == ("send_email",)
    assert "contract_knowledge" in result.trace.dropped_names
    assert "paper_search_skill" in result.trace.dropped_names
    assert result.tool_schemas() == {
        "send_email": {"type": "object", "properties": {"to": {"type": "string"}}}
    }


def test_selector_can_choose_knowledge_without_loading_tool_schemas() -> None:
    from zuno.services.application.capabilities import (
        CapabilityCost,
        CapabilityHealth,
        CapabilityPermissions,
        CapabilityRecord,
        CapabilityRegistry,
        CapabilitySelectionRequest,
        CapabilityType,
        DynamicCapabilitySelector,
    )

    registry = CapabilityRegistry(
        [
            CapabilityRecord(
                name="contract_knowledge",
                type=CapabilityType.KNOWLEDGE,
                description="Search contract review evidence and clauses.",
                schema={"retrieval": "graphrag_project"},
                permissions=CapabilityPermissions(scopes=("knowledge:read",)),
                cost=CapabilityCost(token_estimate=800),
                health=CapabilityHealth.READY,
                source="graphrag_project",
                owner="knowledge",
                tags=("contract", "review"),
            ),
            CapabilityRecord(
                name="send_email",
                type=CapabilityType.ACTION_TOOL,
                description="Send email messages to a recipient.",
                schema={"type": "object"},
                permissions=CapabilityPermissions(scopes=("mail:send",), side_effects=True),
                cost=CapabilityCost(token_estimate=100),
                health=CapabilityHealth.READY,
                source="tool_service",
                owner="tooling",
                tags=("email",),
            ),
        ]
    )

    result = DynamicCapabilitySelector(registry).select(
        CapabilitySelectionRequest(
            task="Find contract review evidence for indemnity clauses",
            allowed_types=(CapabilityType.KNOWLEDGE,),
            max_capabilities=3,
        )
    )

    assert [item.name for item in result.capabilities] == ["contract_knowledge"]
    assert result.tool_schemas() == {}
    assert result.trace.to_dict()["selection_reasons"]["contract_knowledge"] == "task_match"


def test_dynamic_selector_records_toolcard_trace_and_policy_filters() -> None:
    from zuno.services.application.capabilities import (
        CapabilityCost,
        CapabilityHealth,
        CapabilityPermissions,
        CapabilityRecord,
        CapabilityRegistry,
        CapabilitySelectionRequest,
        CapabilityType,
        DynamicCapabilitySelector,
    )

    registry = CapabilityRegistry(
        [
            CapabilityRecord(
                name="lark_send_message",
                type=CapabilityType.MCP_TOOL,
                description="Send a Lark message to a contact.",
                schema={"type": "object", "properties": {"text": {"type": "string"}}},
                permissions=CapabilityPermissions(scopes=("mcp:tool:invoke",), side_effects=True),
                cost=CapabilityCost(token_estimate=200),
                health=CapabilityHealth.READY,
                source="mcp",
                owner="capability.mcp.servers.lark_mcp",
                tags=("lark", "message"),
            ),
            CapabilityRecord(
                name="send_email",
                type=CapabilityType.ACTION_TOOL,
                description="Send email messages.",
                schema={"type": "object"},
                permissions=CapabilityPermissions(scopes=("mail:send",), side_effects=True),
                cost=CapabilityCost(token_estimate=100),
                health=CapabilityHealth.READY,
                source="tool",
                owner="capability.tools.send_email",
                tags=("email",),
            ),
            CapabilityRecord(
                name="weather_mcp",
                type=CapabilityType.MCP_TOOL,
                description="Lookup weather through MCP.",
                schema={"type": "object"},
                permissions=CapabilityPermissions(scopes=("mcp:tool:invoke",), side_effects=False),
                cost=CapabilityCost(token_estimate=80),
                health=CapabilityHealth.DISABLED,
                source="mcp",
                owner="capability.mcp.servers.weather",
                tags=("weather",),
            ),
        ]
    )

    selected = DynamicCapabilitySelector(registry).select(
        CapabilitySelectionRequest(
            task="send a lark message",
            allowed_types=(CapabilityType.MCP_TOOL, CapabilityType.ACTION_TOOL),
            required_permissions=("mcp:tool:invoke",),
            max_capabilities=2,
        )
    )
    blocked = DynamicCapabilitySelector(registry).select(
        CapabilitySelectionRequest(
            task="send a lark message",
            allowed_types=(CapabilityType.MCP_TOOL, CapabilityType.ACTION_TOOL),
            required_permissions=("mcp:tool:invoke",),
            allow_side_effects=False,
            max_capabilities=2,
        )
    )

    trace = selected.trace.to_dict()
    assert selected.capabilities[0].name == "lark_send_message"
    assert trace["candidate_tool_card_ids"][0] == "MCPTool:lark_send_message"
    assert trace["selected_tool_card_ids"] == ["MCPTool:lark_send_message"]
    assert trace["injected_schema_ids"] == ["lark_send_message"]
    assert trace["rejected_tool_card_ids"]["ActionTool:send_email"] == "permission_not_allowed"
    assert trace["rejected_tool_card_ids"]["MCPTool:weather_mcp"] == "disabled"

    blocked_trace = blocked.trace.to_dict()
    assert blocked.capabilities == ()
    assert blocked_trace["rejected_tool_card_ids"]["MCPTool:lark_send_message"] == "side_effect_not_allowed"


def test_tool_runtime_blocks_denied_network_egress_and_records_sandbox_decision() -> None:
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
    runtime = ToolControlPlaneRuntime()
    runtime.register_manifest(
        ToolCardManifest(
            tool_id="web.fetch",
            owner="capability.tools.web",
            capability_domain="web",
            description_for_model="Fetch a public URL.",
            input_schema={"type": "object", "properties": {"url": {"type": "string"}}},
            output_schema={"type": "object"},
            execution_mode=ToolExecutionMode.API,
            trust_tier=ToolTrustTier.WORKSPACE,
            side_effect_level=ToolSideEffectLevel.READ,
            approval_policy=ToolApprovalPolicy.AUTO,
            sandbox_profile="network_limited",
            credential_policy="none",
            network_policy="deny",
            audit_policy="trace",
            budget={"timeout_seconds": 3},
            executor_adapter="api.web.fetch",
        )
    )
    runtime.register_executor_adapter(
        ExecutorAdapterContract(
            adapter_id="api.web.fetch",
            execution_mode=ToolExecutionMode.API,
            sandbox_profile="network_limited",
            network_policy="deny",
            credential_policy="none",
            timeout_seconds=3,
        ),
        lambda args, context: calls.append({"args": args, "context": context}) or {"status": "success"},
    )

    result = runtime.execute(
        ToolRuntimeRequest(
            tool_id="web.fetch",
            arguments={
                "url": "https://example.com/private",
                "metadata": {"endpoint": "https://example.com/private"},
            },
            workspace_id="workspace_tools",
            user_id="user_tools",
            task_id="task_network",
            trace_id="trace_network",
            model_intent="Fetch a public URL.",
        )
    )

    assert result.status == "blocked"
    assert result.security_decision == "block"
    assert calls == []
    decision = result.sandbox_context.to_dict()["network_policy_decision"]
    assert decision["allowed"] is False
    assert decision["reason"] == "network_egress_denied"
    assert decision["denied_targets"] == ["https://example.com/private"]
    assert result.sandbox_context.to_dict()["real_isolation"] is False
    assert result.task_events[1]["payload"]["sandbox"]["network_policy_decision"]["allowed"] is False
    assert result.task_events[-1]["payload"]["error"] == "network_egress_denied"


def test_tool_runtime_rejects_raw_secret_refs_and_records_redacted_approval_ledger() -> None:
    from zuno.capability.runtime import (
        InMemoryCredentialBroker,
        ToolRuntimeRequest,
        build_default_tool_control_plane_runtime,
    )

    broker = InMemoryCredentialBroker()
    try:
        broker.register_secret_ref(
            policy="brokered_secret",
            workspace_id="workspace_tools",
            user_id="user_tools",
            secret_ref="sk-live-secret",
        )
    except ValueError as err:
        assert "credential reference" in str(err)
        assert "sk-live-secret" not in str(err)
    else:
        raise AssertionError("raw secret values must not be stored in the credential broker")

    broker.register_secret_ref(
        policy="brokered_secret",
        workspace_id="workspace_tools",
        user_id="user_tools",
        secret_ref="credref://workspace_tools/mail",
    )
    runtime = build_default_tool_control_plane_runtime()
    runtime.set_credential_broker(broker)
    pending = runtime.execute(
        ToolRuntimeRequest(
            tool_id="mail.send",
            arguments={"to": "hr@example.com", "smtp_password": "raw-secret"},
            workspace_id="workspace_tools",
            user_id="user_tools",
            task_id="task_mail",
            trace_id="trace_mail",
            model_intent="Send email.",
        )
    )
    approved = runtime.execute(
        ToolRuntimeRequest(
            tool_id="mail.send",
            arguments={"to": "hr@example.com", "smtp_password": "raw-secret"},
            workspace_id="workspace_tools",
            user_id="user_tools",
            task_id="task_mail",
            trace_id="trace_mail",
            model_intent="Send email.",
            approved=True,
            approval_comment="approved with raw-secret",
            tool_request_id=pending.tool_request_id,
            approval_id=pending.approval_id,
        )
    )

    ledger = runtime.approval_ledger()

    assert pending.status == "approval_required"
    assert approved.status == "completed"
    assert [entry["status"] for entry in ledger] == ["approval_waiting", "approved_executed"]
    assert ledger[0]["approval_id"] == pending.approval_id
    assert ledger[1]["approval_id"] == pending.approval_id
    assert ledger[1]["credential_refs"] == ["credref://workspace_tools/mail"]
    assert ledger[1]["approval_comment"] == "approved with [REDACTED_SECRET]"
    assert "raw-secret" not in repr(ledger)
