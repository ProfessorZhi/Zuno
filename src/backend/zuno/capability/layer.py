from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zuno.agent.contracts import (
    CapabilityAuditEvent,
    CapabilityCard,
    CapabilityPolicy,
    CapabilityRiskProfile,
    RetrievalProfile,
    SkillCard,
    ToolCard,
)


@dataclass(frozen=True, slots=True)
class CapabilityRouteRequest:
    task_id: str
    workspace_id: str
    task_goal: str
    requested_capability_ids: tuple[str, ...] = ()
    pinned_skill_id: str | None = None
    user_roles: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CapabilityDecision:
    capability_id: str
    allowed: bool
    decision: str
    reason: str
    audit_event: CapabilityAuditEvent
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CapabilityRouteDecision:
    selected_skill: SkillCard
    allowed_capability_ids: tuple[str, ...]
    allowed_tool_ids: tuple[str, ...]
    blocked_capability_reasons: dict[str, str]
    audit_events: tuple[CapabilityAuditEvent, ...]
    trace: dict[str, Any]


class CapabilityLayerRegistry:
    def __init__(
        self,
        *,
        skills: tuple[SkillCard, ...],
        capabilities: tuple[CapabilityCard, ...],
        tool_cards: tuple[ToolCard, ...],
    ) -> None:
        self._skills = {skill.skill_id: skill for skill in skills}
        self._capabilities = {
            capability.capability_id: capability
            for capability in capabilities
        }
        self._tool_cards = {tool.tool_id: tool for tool in tool_cards}

    def skills(self) -> tuple[SkillCard, ...]:
        return tuple(self._skills.values())

    def list_capabilities(self) -> tuple[CapabilityCard, ...]:
        return tuple(self._capabilities.values())

    def tool_cards(self) -> tuple[ToolCard, ...]:
        return tuple(self._tool_cards.values())

    def require_skill(self, skill_id: str) -> SkillCard:
        try:
            return self._skills[skill_id]
        except KeyError as exc:
            raise KeyError(f"unknown skill: {skill_id}") from exc

    def require_capability(self, capability_id: str) -> CapabilityCard:
        try:
            return self._capabilities[capability_id]
        except KeyError as exc:
            raise KeyError(f"unknown capability: {capability_id}") from exc

    def require_tool_card(self, tool_id: str) -> ToolCard:
        try:
            return self._tool_cards[tool_id]
        except KeyError as exc:
            raise KeyError(f"unknown tool card: {tool_id}") from exc


class CapabilityRouter:
    def __init__(self, registry: CapabilityLayerRegistry) -> None:
        self._registry = registry

    def route(self, request: CapabilityRouteRequest) -> CapabilityRouteDecision:
        automatic_skill_id = self._automatic_skill_id(request.task_goal)
        selected_skill_id = request.pinned_skill_id or automatic_skill_id
        selected_skill = self._registry.require_skill(selected_skill_id)
        allowed_by_skill = set(selected_skill.allowed_tools)

        allowed_capabilities: list[str] = []
        allowed_tools: list[str] = []
        blocked: dict[str, str] = {}
        audit_events: list[CapabilityAuditEvent] = []

        for capability_id in request.requested_capability_ids:
            if capability_id not in allowed_by_skill:
                decision = self._blocked_decision(
                    capability_id=capability_id,
                    request=request,
                    reason="skill_tool_not_allowed",
                )
            else:
                decision = self.evaluate_capability(capability_id, request)

            audit_events.append(decision.audit_event)
            if decision.allowed:
                allowed_capabilities.append(capability_id)
                capability = self._registry.require_capability(capability_id)
                if capability.capability_type == "tool":
                    allowed_tools.append(capability_id)
            else:
                blocked[capability_id] = decision.reason

        return CapabilityRouteDecision(
            selected_skill=selected_skill,
            allowed_capability_ids=tuple(allowed_capabilities),
            allowed_tool_ids=tuple(allowed_tools),
            blocked_capability_reasons=blocked,
            audit_events=tuple(audit_events),
            trace={
                "skill_selection_mode": "pinned" if request.pinned_skill_id else "automatic",
                "selected_skill_id": selected_skill.skill_id,
                "automatic_candidate_skill_id": automatic_skill_id,
                "requested_capability_ids": list(request.requested_capability_ids),
                "allowed_capability_ids": allowed_capabilities,
                "blocked_capability_reasons": dict(blocked),
            },
        )

    def evaluate_capability(
        self,
        capability_id: str,
        request: CapabilityRouteRequest,
    ) -> CapabilityDecision:
        capability = self._registry.require_capability(capability_id)
        policy = capability.policy
        missing_roles = [
            role
            for role in policy.required_roles
            if role not in set(request.user_roles)
        ]
        if missing_roles:
            return self._decision(
                capability_id=capability_id,
                request=request,
                decision="blocked",
                reason="permission_denied",
                evidence={
                    "required_roles": list(policy.required_roles),
                    "missing_roles": missing_roles,
                },
            )

        workspace_scope = policy.workspace_scope
        if workspace_scope.startswith("workspace:"):
            allowed_workspace = workspace_scope.removeprefix("workspace:")
            if allowed_workspace not in {"*", request.workspace_id}:
                return self._decision(
                    capability_id=capability_id,
                    request=request,
                    decision="blocked",
                    reason="workspace_scope_denied",
                    evidence={
                        "workspace_scope": workspace_scope,
                        "request_workspace_id": request.workspace_id,
                    },
                )

        dependency_probe = capability.metadata.get("dependency_probe")
        if capability.capability_type == "mcp" and isinstance(dependency_probe, dict):
            if dependency_probe.get("configured") is False:
                return self._decision(
                    capability_id=capability_id,
                    request=request,
                    decision="target_blocked",
                    reason="mcp_dependency_not_configured",
                    evidence={"dependency_probe": dict(dependency_probe)},
                )

        return self._decision(
            capability_id=capability_id,
            request=request,
            decision="allowed",
            reason="policy_allowed",
        )

    def _blocked_decision(
        self,
        *,
        capability_id: str,
        request: CapabilityRouteRequest,
        reason: str,
    ) -> CapabilityDecision:
        return self._decision(
            capability_id=capability_id,
            request=request,
            decision="blocked",
            reason=reason,
        )

    @staticmethod
    def _decision(
        *,
        capability_id: str,
        request: CapabilityRouteRequest,
        decision: str,
        reason: str,
        evidence: dict[str, Any] | None = None,
    ) -> CapabilityDecision:
        return CapabilityDecision(
            capability_id=capability_id,
            allowed=decision == "allowed",
            decision=decision,
            reason=reason,
            evidence=evidence or {},
            audit_event=CapabilityAuditEvent(
                capability_id=capability_id,
                task_id=request.task_id,
                decision=decision,
                reason=reason,
                latency_ms=0.0,
            ),
        )

    @staticmethod
    def _automatic_skill_id(task_goal: str) -> str:
        text = task_goal.lower()
        if any(term in text for term in ("contract", "clause", "indemnity", "agreement")):
            return "contract_review"
        if any(term in text for term in ("research", "report", "web", "source")):
            return "research_report"
        return "research_report"


def build_default_capability_layer_registry() -> CapabilityLayerRegistry:
    return CapabilityLayerRegistry(
        skills=_default_skill_cards(),
        capabilities=_default_capability_cards(),
        tool_cards=_default_tool_cards(),
    )


def _default_skill_cards() -> tuple[SkillCard, ...]:
    return (
        SkillCard(
            skill_id="contract_review",
            skill_version="1.0.0",
            when_to_use="Review contract clauses and produce source-grounded risk notes.",
            task_type="contract_review",
            recommended_retrieval_profile=RetrievalProfile.DEEP,
            required_evidence=["contract_clause", "citation_lineage"],
            allowed_tools=[
                "knowledge.contracts",
                "tool.filesystem.read",
                "artifact.report",
            ],
            memory_scopes=["working", "session", "episodic"],
            output_contract={
                "artifact_type": "contract_review",
                "requires_citations": True,
                "sections": ["issues", "evidence", "recommendations"],
            },
            safety_policy="workspace_acl_and_citation_required",
            eval_rubric={
                "citation_coverage": "required",
                "unsupported_claims": "blocked",
            },
            max_steps=5,
            reflection_policy="required",
        ),
        SkillCard(
            skill_id="research_report",
            skill_version="1.0.0",
            when_to_use="Collect evidence and synthesize a cited research report.",
            task_type="research_report",
            recommended_retrieval_profile=RetrievalProfile.DEEP,
            required_evidence=["source_quote", "citation_lineage"],
            allowed_tools=[
                "knowledge.research_corpus",
                "tool.web.search",
                "artifact.report",
            ],
            memory_scopes=["working", "session", "semantic"],
            output_contract={
                "artifact_type": "research_report",
                "requires_citations": True,
                "sections": ["answer", "evidence", "limitations"],
            },
            safety_policy="source_grounded_and_redacted",
            eval_rubric={
                "citation_coverage": "required",
                "freshness_check": "required_when_web_used",
            },
            max_steps=6,
            reflection_policy="required",
        ),
    )


def _default_capability_cards() -> tuple[CapabilityCard, ...]:
    return (
        _capability(
            "knowledge.contracts",
            "knowledge",
            "Retrieve contract evidence from the current workspace knowledge space.",
            workspace_scope="workspace:workspace_alpha",
            required_roles=["analyst"],
            data_access_policy="workspace_acl",
            metadata={
                "retrieval_profiles": ["standard", "deep"],
                "sensitivity": ["contract"],
            },
        ),
        _capability(
            "knowledge.research_corpus",
            "knowledge",
            "Retrieve source-grounded evidence from the workspace research corpus.",
            workspace_scope="workspace:*",
            required_roles=["analyst"],
            data_access_policy="workspace_acl",
            metadata={"retrieval_profiles": ["standard", "deep"]},
        ),
        _capability(
            "tool.filesystem.read",
            "tool",
            "Read workspace-scoped files through the tool control plane.",
            workspace_scope="workspace:*",
            required_roles=["analyst"],
            side_effect_level="read",
            metadata={"sandbox_profile": "workspace_ro"},
        ),
        _capability(
            "tool.web.search",
            "tool",
            "Search public web pages through a governed tool boundary.",
            workspace_scope="workspace:*",
            required_roles=["analyst"],
            side_effect_level="read",
            network_policy="allow_public_web",
            metadata={"sandbox_profile": "network_read_only"},
            risk_profile=CapabilityRiskProfile(
                read_only=True,
                network_access=True,
            ),
        ),
        _capability(
            "tool.mail.send",
            "tool",
            "Send external mail after explicit approval.",
            workspace_scope="workspace:*",
            required_roles=["workspace_admin"],
            approval_required=True,
            side_effect_level="write_external",
            network_policy="egress_mail_only",
            credential_policy="brokered_secret",
            risk_profile=CapabilityRiskProfile(
                read_only=False,
                external_write=True,
                network_access=True,
                credential_access=True,
            ),
        ),
        _capability(
            "mcp.lark.send_message",
            "mcp",
            "Send a Lark message through an MCP server when configured.",
            workspace_scope="workspace:workspace_alpha",
            required_roles=["workspace_admin"],
            approval_required=True,
            side_effect_level="write_external",
            network_policy="stdio_or_remote_mcp",
            credential_policy="user_scoped_secret",
            metadata={
                "dependency_probe": {
                    "provider": "lark_mcp",
                    "configured": False,
                    "target_state": "configure_mcp_server",
                },
            },
            risk_profile=CapabilityRiskProfile(
                read_only=False,
                external_write=True,
                network_access=True,
                credential_access=True,
            ),
        ),
        _capability(
            "external_api.public_web",
            "external_api",
            "External public-web API adapter boundary.",
            workspace_scope="workspace:*",
            required_roles=["analyst"],
            side_effect_level="read",
            network_policy="allow_public_web",
            risk_profile=CapabilityRiskProfile(read_only=True, network_access=True),
        ),
        _capability(
            "file.workspace.read",
            "file",
            "Workspace file read capability boundary.",
            workspace_scope="workspace:*",
            required_roles=["analyst"],
            side_effect_level="read",
        ),
        _capability(
            "code.local_test_runner",
            "code",
            "Run local deterministic tests through a governed code capability.",
            workspace_scope="workspace:*",
            required_roles=["developer"],
            side_effect_level="write_workspace",
            risk_profile=CapabilityRiskProfile(
                read_only=False,
                write_workspace=True,
                code_execution=True,
            ),
        ),
        _capability(
            "browser.workspace_preview",
            "browser",
            "Open a workspace preview browser under policy control.",
            workspace_scope="workspace:*",
            required_roles=["developer"],
            side_effect_level="read",
            risk_profile=CapabilityRiskProfile(read_only=True, browser_control=True),
        ),
        _capability(
            "artifact.report",
            "artifact",
            "Create a report artifact with citation and redaction policy.",
            workspace_scope="workspace:*",
            required_roles=["analyst"],
            side_effect_level="write_workspace",
            metadata={
                "artifact_type": "report",
                "redaction_policy": "required_before_share",
            },
            risk_profile=CapabilityRiskProfile(
                read_only=False,
                write_workspace=True,
            ),
        ),
    )


def _default_tool_cards() -> tuple[ToolCard, ...]:
    return (
        ToolCard(
            tool_id="tool.filesystem.read",
            capability_id="tool.filesystem.read",
            input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"content": {"type": "string"}}},
            permission=_policy(
                "tool.filesystem.read",
                "tool",
                workspace_scope="workspace:*",
                required_roles=["analyst"],
                side_effect_level="read",
            ),
            trace_fields=[
                "capability_id",
                "permission_decision",
                "audit_ref",
                "sandbox_profile",
            ],
        ),
        ToolCard(
            tool_id="mcp.lark.send_message",
            capability_id="mcp.lark.send_message",
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"message_id": {"type": "string"}}},
            permission=_policy(
                "mcp.lark.send_message",
                "mcp",
                workspace_scope="workspace:workspace_alpha",
                required_roles=["workspace_admin"],
                approval_required=True,
                side_effect_level="write_external",
                network_policy="stdio_or_remote_mcp",
                credential_policy="user_scoped_secret",
            ),
            trace_fields=[
                "capability_id",
                "permission_decision",
                "audit_ref",
                "dependency_probe",
            ],
        ),
    )


def _capability(
    capability_id: str,
    capability_type: str,
    description: str,
    *,
    workspace_scope: str,
    required_roles: list[str],
    approval_required: bool = False,
    side_effect_level: str = "read",
    network_policy: str = "deny",
    credential_policy: str = "none",
    data_access_policy: str = "workspace_acl",
    audit_policy: str = "trace",
    metadata: dict[str, Any] | None = None,
    risk_profile: CapabilityRiskProfile | None = None,
) -> CapabilityCard:
    return CapabilityCard(
        capability_id=capability_id,
        capability_type=capability_type,
        description=description,
        policy=_policy(
            capability_id,
            capability_type,
            workspace_scope=workspace_scope,
            required_roles=required_roles,
            approval_required=approval_required,
            side_effect_level=side_effect_level,
            network_policy=network_policy,
            credential_policy=credential_policy,
            data_access_policy=data_access_policy,
            audit_policy=audit_policy,
        ),
        risk_profile=risk_profile or CapabilityRiskProfile(),
        metadata=metadata or {},
    )


def _policy(
    capability_id: str,
    capability_type: str,
    *,
    workspace_scope: str,
    required_roles: list[str],
    approval_required: bool = False,
    side_effect_level: str = "read",
    network_policy: str = "deny",
    credential_policy: str = "none",
    data_access_policy: str = "workspace_acl",
    audit_policy: str = "trace",
) -> CapabilityPolicy:
    return CapabilityPolicy(
        capability_id=capability_id,
        capability_type=capability_type,
        workspace_scope=workspace_scope,
        required_roles=required_roles,
        approval_required=approval_required,
        side_effect_level=side_effect_level,
        network_policy=network_policy,
        credential_policy=credential_policy,
        data_access_policy=data_access_policy,
        audit_policy=audit_policy,
    )


__all__ = [
    "CapabilityDecision",
    "CapabilityLayerRegistry",
    "CapabilityRouteDecision",
    "CapabilityRouteRequest",
    "CapabilityRouter",
    "build_default_capability_layer_registry",
]
