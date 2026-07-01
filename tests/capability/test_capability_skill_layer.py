from __future__ import annotations


def test_default_registry_loads_skill_and_capability_contracts() -> None:
    from zuno.agent.contracts import CapabilityCard, CapabilityPolicy, RetrievalProfile
    from zuno.capability.layer import build_default_capability_layer_registry

    registry = build_default_capability_layer_registry()

    skills = {skill.skill_id: skill for skill in registry.skills()}
    capabilities = {card.capability_id: card for card in registry.list_capabilities()}

    assert {"contract_review", "research_report"}.issubset(skills)
    assert skills["contract_review"].recommended_retrieval_profile is RetrievalProfile.DEEP
    assert skills["contract_review"].allowed_tools == [
        "knowledge.contracts",
        "tool.filesystem.read",
        "artifact.report",
    ]
    assert capabilities["knowledge.contracts"].capability_type == "knowledge"
    assert capabilities["tool.filesystem.read"].capability_type == "tool"
    assert capabilities["mcp.lark.send_message"].capability_type == "mcp"
    assert capabilities["external_api.public_web"].capability_type == "external_api"
    assert capabilities["file.workspace.read"].capability_type == "file"
    assert capabilities["code.local_test_runner"].capability_type == "code"
    assert capabilities["browser.workspace_preview"].capability_type == "browser"
    assert capabilities["artifact.report"].capability_type == "artifact"
    assert all(isinstance(card, CapabilityCard) for card in capabilities.values())
    assert all(isinstance(card.policy, CapabilityPolicy) for card in capabilities.values())
    assert capabilities["artifact.report"].metadata["redaction_policy"] == "required_before_share"


def test_skill_card_fixtures_serialize_allowed_tools_and_output_contract() -> None:
    from zuno.capability.layer import build_default_capability_layer_registry

    registry = build_default_capability_layer_registry()
    payload = registry.require_skill("research_report").model_dump(mode="json")

    assert payload["skill_id"] == "research_report"
    assert payload["recommended_retrieval_profile"] == "deep"
    assert payload["allowed_tools"] == [
        "knowledge.research_corpus",
        "tool.web.search",
        "artifact.report",
    ]
    assert payload["output_contract"] == {
        "artifact_type": "research_report",
        "requires_citations": True,
        "sections": ["answer", "evidence", "limitations"],
    }
    assert payload["eval_rubric"]["citation_coverage"] == "required"


def test_router_limits_tools_to_selected_skill_and_records_audit_events() -> None:
    from zuno.capability.layer import CapabilityRouteRequest, CapabilityRouter
    from zuno.capability.layer import build_default_capability_layer_registry

    router = CapabilityRouter(build_default_capability_layer_registry())

    decision = router.route(
        CapabilityRouteRequest(
            task_id="task_capability_contract",
            workspace_id="workspace_alpha",
            task_goal="Review contract indemnity and cite the source clauses.",
            requested_capability_ids=(
                "knowledge.contracts",
                "tool.filesystem.read",
                "tool.mail.send",
                "artifact.report",
            ),
            user_roles=("analyst",),
        )
    )

    assert decision.selected_skill.skill_id == "contract_review"
    assert decision.allowed_capability_ids == (
        "knowledge.contracts",
        "tool.filesystem.read",
        "artifact.report",
    )
    assert decision.allowed_tool_ids == ("tool.filesystem.read",)
    assert decision.blocked_capability_reasons == {
        "tool.mail.send": "skill_tool_not_allowed",
    }
    assert [event.capability_id for event in decision.audit_events] == [
        "knowledge.contracts",
        "tool.filesystem.read",
        "tool.mail.send",
        "artifact.report",
    ]
    assert decision.trace["skill_selection_mode"] == "automatic"
    assert decision.trace["selected_skill_id"] == "contract_review"


def test_cross_workspace_knowledge_capability_is_blocked_by_policy() -> None:
    from zuno.capability.layer import CapabilityRouteRequest, CapabilityRouter
    from zuno.capability.layer import build_default_capability_layer_registry

    router = CapabilityRouter(build_default_capability_layer_registry())

    decision = router.evaluate_capability(
        "knowledge.contracts",
        CapabilityRouteRequest(
            task_id="task_cross_workspace",
            workspace_id="workspace_beta",
            task_goal="Use the other workspace contracts.",
            requested_capability_ids=("knowledge.contracts",),
            user_roles=("analyst",),
        ),
    )

    assert decision.allowed is False
    assert decision.decision == "blocked"
    assert decision.reason == "workspace_scope_denied"
    assert decision.audit_event.capability_id == "knowledge.contracts"
    assert decision.audit_event.decision == "blocked"
    assert decision.evidence["workspace_scope"] == "workspace:workspace_alpha"


def test_mcp_capability_not_configured_returns_target_blocked_evidence() -> None:
    from zuno.capability.layer import CapabilityRouteRequest, CapabilityRouter
    from zuno.capability.layer import build_default_capability_layer_registry

    router = CapabilityRouter(build_default_capability_layer_registry())

    no_role = router.evaluate_capability(
        "mcp.lark.send_message",
        CapabilityRouteRequest(
            task_id="task_mcp_permission",
            workspace_id="workspace_alpha",
            task_goal="Send a Lark message.",
            requested_capability_ids=("mcp.lark.send_message",),
            user_roles=("analyst",),
        ),
    )
    with_role = router.evaluate_capability(
        "mcp.lark.send_message",
        CapabilityRouteRequest(
            task_id="task_mcp_target_blocked",
            workspace_id="workspace_alpha",
            task_goal="Send a Lark message.",
            requested_capability_ids=("mcp.lark.send_message",),
            user_roles=("workspace_admin",),
        ),
    )

    assert no_role.reason == "permission_denied"
    assert no_role.evidence["missing_roles"] == ["workspace_admin"]
    assert with_role.decision == "target_blocked"
    assert with_role.reason == "mcp_dependency_not_configured"
    assert with_role.evidence["dependency_probe"] == {
        "provider": "lark_mcp",
        "configured": False,
        "target_state": "configure_mcp_server",
    }


def test_pinned_skill_overrides_automatic_selection_contract() -> None:
    from zuno.capability.layer import CapabilityRouteRequest, CapabilityRouter
    from zuno.capability.layer import build_default_capability_layer_registry

    router = CapabilityRouter(build_default_capability_layer_registry())

    decision = router.route(
        CapabilityRouteRequest(
            task_id="task_pinned_skill",
            workspace_id="workspace_alpha",
            task_goal="Review contract clauses, but use the pinned research workflow.",
            requested_capability_ids=("knowledge.research_corpus", "tool.web.search", "artifact.report"),
            pinned_skill_id="research_report",
            user_roles=("analyst",),
        )
    )

    assert decision.selected_skill.skill_id == "research_report"
    assert decision.trace["skill_selection_mode"] == "pinned"
    assert decision.trace["automatic_candidate_skill_id"] == "contract_review"


def test_tool_and_mcp_boundaries_include_permission_and_trace_fields() -> None:
    from zuno.agent.contracts import ToolCard
    from zuno.capability.layer import build_default_capability_layer_registry

    registry = build_default_capability_layer_registry()

    filesystem = registry.require_tool_card("tool.filesystem.read")
    lark = registry.require_tool_card("mcp.lark.send_message")

    assert isinstance(filesystem, ToolCard)
    assert filesystem.permission.capability_type == "tool"
    assert filesystem.trace_fields == [
        "capability_id",
        "permission_decision",
        "audit_ref",
        "sandbox_profile",
    ]
    assert lark.permission.capability_type == "mcp"
    assert lark.permission.required_roles == ["workspace_admin"]
    assert lark.trace_fields == [
        "capability_id",
        "permission_decision",
        "audit_ref",
        "dependency_probe",
    ]
