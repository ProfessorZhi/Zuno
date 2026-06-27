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
