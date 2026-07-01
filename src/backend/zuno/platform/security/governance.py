from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field, replace
from enum import StrEnum
import re
from typing import Any


class SecurityGate(StrEnum):
    INPUT = "input"
    RETRIEVAL = "retrieval"
    TOOL = "tool"
    OUTPUT = "output"


class SecurityDecision(StrEnum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    REDACT = "redact"
    BLOCK = "block"


class SandboxProfile(StrEnum):
    NONE = "none"
    WORKSPACE_RO = "workspace_ro"
    WORKSPACE_RW_ARTIFACTS = "workspace_rw_artifacts"
    NETWORK_LIMITED = "network_limited"
    EXECUTION_RESTRICTED = "execution_restricted"
    DISABLED = "disabled"


SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]+\b"),
    re.compile(r"\b(api[_ -]?key|token|password|secret)\s*[:=]?\s+[A-Za-z0-9._@:/+-]+\b", re.I),
]
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PROMPT_INJECTION_PATTERN = re.compile(
    r"(ignore\s+(all\s+)?(previous|prior)\s+instructions|system\s*:|developer\s*:|exfiltrate)",
    re.I,
)
UNTRUSTED_INSTRUCTION_PATTERN = re.compile(
    r"\b(system|developer)\s*:\s*[^.。!\n]*(?:[.。!]\s*)?",
    re.I,
)


def redact_sensitive_text(value: str) -> str:
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    redacted = SSN_PATTERN.sub("[REDACTED_PII]", redacted)
    redacted = EMAIL_PATTERN.sub("[REDACTED_PII]", redacted)
    return redacted


def redact_sensitive_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in ("password", "secret", "token", "api_key", "apikey")):
                redacted[key] = "[REDACTED_SECRET]"
            else:
                redacted[key] = redact_sensitive_payload(value)
        return redacted
    if isinstance(payload, list):
        return [redact_sensitive_payload(item) for item in payload]
    if isinstance(payload, tuple):
        return tuple(redact_sensitive_payload(item) for item in payload)
    if isinstance(payload, str):
        return redact_sensitive_text(payload)
    return payload


@dataclass(frozen=True, slots=True)
class SecurityFinding:
    code: str
    gate: SecurityGate
    severity: str
    message: str
    evidence_ref: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "gate": self.gate.value,
            "severity": self.severity,
            "message": self.message,
            "evidence_ref": self.evidence_ref,
        }


@dataclass(frozen=True, slots=True)
class SandboxAuditEvent:
    audit_id: str
    gate: SecurityGate
    workspace_id: str
    task_id: str
    trace_id: str
    model_intent: str
    policy_decision: SecurityDecision
    final_decision: str
    actor: str
    target: str
    sandbox_profile: SandboxProfile
    risk_reasons: list[str] = field(default_factory=list)
    proposed_args_redacted: dict[str, Any] = field(default_factory=dict)

    def to_trace_payload(self) -> dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "gate": self.gate.value,
            "workspace_id": self.workspace_id,
            "task_id": self.task_id,
            "trace_id": self.trace_id,
            "model_intent": self.model_intent,
            "policy_decision": self.policy_decision.value,
            "final_decision": self.final_decision,
            "actor": self.actor,
            "target": self.target,
            "sandbox_profile": self.sandbox_profile.value,
            "risk_reasons": list(self.risk_reasons),
            "proposed_args_redacted": deepcopy(self.proposed_args_redacted),
        }


@dataclass(frozen=True, slots=True)
class GateRequest:
    gate: SecurityGate
    workspace_id: str
    user_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""
    task_id: str = ""


@dataclass(frozen=True, slots=True)
class GateResult:
    gate: SecurityGate
    decision: SecurityDecision
    sanitized_content: str
    findings: list[SecurityFinding]
    audit_event: SandboxAuditEvent
    recommended_action: str = "continue"


class InputSecurityGate:
    def evaluate(self, request: GateRequest) -> GateResult:
        findings = _content_findings(request.content, SecurityGate.INPUT)
        decision = SecurityDecision.BLOCK if findings else SecurityDecision.ALLOW
        return GateResult(
            gate=SecurityGate.INPUT,
            decision=decision,
            sanitized_content=redact_sensitive_text(request.content),
            findings=findings,
            audit_event=_audit_event(
                gate=SecurityGate.INPUT,
                workspace_id=request.workspace_id,
                task_id=request.task_id,
                trace_id=request.trace_id,
                actor=request.user_id,
                target=str(request.metadata.get("source") or "user_input"),
                decision=decision,
                risk_reasons=[finding.code for finding in findings],
            ),
        )


@dataclass(frozen=True, slots=True)
class RetrievalCandidate:
    chunk_id: str
    workspace_id: str
    acl_scope: str
    document_trust_label: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def sanitized(self) -> "RetrievalCandidate":
        return replace(self, text=UNTRUSTED_INSTRUCTION_PATTERN.sub("", self.text).strip())


@dataclass(frozen=True, slots=True)
class RetrievalGateResult:
    decision: SecurityDecision
    allowed_candidates: list[RetrievalCandidate]
    blocked_candidates: list[RetrievalCandidate]
    findings: list[SecurityFinding]
    audit_event: SandboxAuditEvent


class RetrievalSecurityGate:
    def filter_candidates(
        self,
        *,
        workspace_id: str,
        allowed_acl_scopes: set[str],
        candidates: list[RetrievalCandidate],
        trace_id: str,
        task_id: str,
    ) -> RetrievalGateResult:
        allowed: list[RetrievalCandidate] = []
        blocked: list[RetrievalCandidate] = []
        findings: list[SecurityFinding] = []
        for candidate in candidates:
            if candidate.workspace_id != workspace_id:
                blocked.append(candidate)
                findings.append(
                    SecurityFinding(
                        code="cross_workspace_chunk",
                        gate=SecurityGate.RETRIEVAL,
                        severity="high",
                        message="retrieval candidate belongs to another workspace",
                        evidence_ref=candidate.chunk_id,
                    )
                )
                continue
            if candidate.acl_scope not in allowed_acl_scopes:
                blocked.append(candidate)
                findings.append(
                    SecurityFinding(
                        code="acl_scope_denied",
                        gate=SecurityGate.RETRIEVAL,
                        severity="high",
                        message="retrieval candidate ACL scope is not allowed",
                        evidence_ref=candidate.chunk_id,
                    )
                )
                continue
            sanitized = candidate.sanitized()
            if sanitized.text != candidate.text:
                findings.append(
                    SecurityFinding(
                        code="untrusted_instruction_sanitized",
                        gate=SecurityGate.RETRIEVAL,
                        severity="medium",
                        message="untrusted retrieved instruction was stripped",
                        evidence_ref=candidate.chunk_id,
                    )
                )
            allowed.append(sanitized)
        return RetrievalGateResult(
            decision=SecurityDecision.ALLOW if allowed else SecurityDecision.BLOCK,
            allowed_candidates=allowed,
            blocked_candidates=blocked,
            findings=findings,
            audit_event=_audit_event(
                gate=SecurityGate.RETRIEVAL,
                workspace_id=workspace_id,
                task_id=task_id,
                trace_id=trace_id,
                actor="system",
                target="retrieval_candidates",
                decision=SecurityDecision.ALLOW if allowed else SecurityDecision.BLOCK,
                risk_reasons=[finding.code for finding in findings],
            ),
        )


@dataclass(frozen=True, slots=True)
class ToolSecurityProfile:
    tool_id: str
    side_effect_level: str
    execution_mode: str
    approval_required: bool
    sandbox_required: bool
    sandbox_profile: SandboxProfile
    credential_policy: str
    network_policy: str
    audit_required: bool

    @classmethod
    def from_tool_card(
        cls,
        *,
        tool_id: str,
        side_effect_level: str,
        execution_mode: str,
    ) -> "ToolSecurityProfile":
        side_effect = side_effect_level.strip().lower()
        mapping = {
            "none": (False, False, SandboxProfile.NONE, "none", "deny", False),
            "read": (False, True, SandboxProfile.WORKSPACE_RO, "none", "deny", True),
            "write_local": (
                True,
                True,
                SandboxProfile.WORKSPACE_RW_ARTIFACTS,
                "none",
                "deny",
                True,
            ),
            "write_external": (
                True,
                True,
                SandboxProfile.NETWORK_LIMITED,
                "brokered",
                "allowlist",
                True,
            ),
            "destructive": (
                True,
                True,
                SandboxProfile.EXECUTION_RESTRICTED,
                "brokered",
                "deny_by_default",
                True,
            ),
        }
        approval_required, sandbox_required, sandbox_profile, credential_policy, network_policy, audit_required = mapping.get(
            side_effect,
            (True, True, SandboxProfile.EXECUTION_RESTRICTED, "brokered", "deny_by_default", True),
        )
        if execution_mode.strip().lower() in {"ssh", "cli"}:
            approval_required = True
            sandbox_required = True
            sandbox_profile = SandboxProfile.EXECUTION_RESTRICTED
            audit_required = True
        return cls(
            tool_id=tool_id,
            side_effect_level=side_effect,
            execution_mode=execution_mode.strip().lower(),
            approval_required=approval_required,
            sandbox_required=sandbox_required,
            sandbox_profile=sandbox_profile,
            credential_policy=credential_policy,
            network_policy=network_policy,
            audit_required=audit_required,
        )


@dataclass(frozen=True, slots=True)
class ToolGateResult:
    decision: SecurityDecision
    profile: ToolSecurityProfile
    findings: list[SecurityFinding]
    audit_event: SandboxAuditEvent


class ToolSecurityGate:
    def evaluate(
        self,
        *,
        profile: ToolSecurityProfile,
        model_intent: str,
        proposed_args: dict[str, Any],
        workspace_id: str,
        trace_id: str,
        task_id: str,
    ) -> ToolGateResult:
        decision = (
            SecurityDecision.REQUIRE_APPROVAL
            if profile.approval_required
            else SecurityDecision.ALLOW
        )
        risk_reasons = [profile.side_effect_level]
        if profile.credential_policy == "brokered":
            risk_reasons.append("credential_possible")
        findings = [
            SecurityFinding(
                code="approval_required" if decision is SecurityDecision.REQUIRE_APPROVAL else "auto_allowed",
                gate=SecurityGate.TOOL,
                severity="high" if decision is SecurityDecision.REQUIRE_APPROVAL else "info",
                message="tool execution policy decision",
                evidence_ref=profile.tool_id,
            )
        ]
        return ToolGateResult(
            decision=decision,
            profile=profile,
            findings=findings,
            audit_event=_audit_event(
                gate=SecurityGate.TOOL,
                workspace_id=workspace_id,
                task_id=task_id,
                trace_id=trace_id,
                actor="system",
                target=f"tool:{profile.tool_id}",
                decision=decision,
                risk_reasons=risk_reasons,
                model_intent=model_intent,
                proposed_args_redacted=redact_sensitive_payload(proposed_args),
                sandbox_profile=profile.sandbox_profile,
                final_decision="pending" if decision is SecurityDecision.REQUIRE_APPROVAL else "approved",
            ),
        )


class OutputSecurityGate:
    def evaluate(
        self,
        *,
        content: str,
        citation_coverage: float,
        required_citation_coverage: float,
        unsupported_claim_count: int = 0,
        workspace_id: str,
        trace_id: str,
        task_id: str,
    ) -> GateResult:
        findings = _content_findings(content, SecurityGate.OUTPUT, include_prompt_injection=False)
        if unsupported_claim_count > 0:
            findings.append(
                SecurityFinding(
                    code="unsupported_claim",
                    gate=SecurityGate.OUTPUT,
                    severity="high",
                    message="answer contains unsupported claim candidates",
                )
            )
        if citation_coverage < required_citation_coverage:
            findings.append(
                SecurityFinding(
                    code="citation_coverage_low",
                    gate=SecurityGate.OUTPUT,
                    severity="high",
                    message="answer citation coverage is below policy threshold",
                )
            )
        decision = SecurityDecision.BLOCK if findings else SecurityDecision.ALLOW
        return GateResult(
            gate=SecurityGate.OUTPUT,
            decision=decision,
            sanitized_content=redact_sensitive_text(content),
            findings=findings,
            audit_event=_audit_event(
                gate=SecurityGate.OUTPUT,
                workspace_id=workspace_id,
                task_id=task_id,
                trace_id=trace_id,
                actor="system",
                target="answer",
                decision=decision,
                risk_reasons=[finding.code for finding in findings],
            ),
            recommended_action=_output_recommended_action(findings),
        )


@dataclass(frozen=True, slots=True)
class SecurityTraceSummary:
    gate_verdicts: dict[str, str]
    planning_actions: dict[str, str]
    metrics: dict[str, int]
    trace_events: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_verdicts": dict(self.gate_verdicts),
            "planning_actions": dict(self.planning_actions),
            "metrics": dict(self.metrics),
            "trace_events": [deepcopy(event) for event in self.trace_events],
        }


def build_security_trace_summary(
    *,
    input_result: GateResult,
    retrieval_result: RetrievalGateResult,
    tool_result: ToolGateResult,
    output_result: GateResult,
) -> SecurityTraceSummary:
    gate_verdicts = {
        "input": input_result.decision.value,
        "retrieval": retrieval_result.decision.value,
        "tool": tool_result.decision.value,
        "output": output_result.decision.value,
    }
    planning_actions: dict[str, str] = {}
    if input_result.decision is SecurityDecision.BLOCK:
        planning_actions["input"] = input_result.recommended_action if input_result.recommended_action != "continue" else "refuse"
    if retrieval_result.blocked_candidates:
        planning_actions["retrieval"] = (
            "continue_with_filtered_context"
            if retrieval_result.allowed_candidates
            else "refuse"
        )
    if tool_result.decision is SecurityDecision.REQUIRE_APPROVAL:
        planning_actions["tool"] = "ask_user"
    elif tool_result.decision is SecurityDecision.BLOCK:
        planning_actions["tool"] = "refuse"
    if output_result.decision is SecurityDecision.BLOCK:
        planning_actions["output"] = output_result.recommended_action

    trace_events = [
        _security_trace_event(
            gate="input",
            decision=input_result.decision,
            findings=input_result.findings,
            audit_ref=input_result.audit_event.audit_id,
            planning_action=planning_actions.get("input", "continue"),
        ),
        _security_trace_event(
            gate="retrieval",
            decision=retrieval_result.decision,
            findings=retrieval_result.findings,
            audit_ref=retrieval_result.audit_event.audit_id,
            planning_action=planning_actions.get("retrieval", "continue"),
            extra={
                "allowed_candidate_count": len(retrieval_result.allowed_candidates),
                "blocked_candidate_count": len(retrieval_result.blocked_candidates),
            },
        ),
        _security_trace_event(
            gate="tool",
            decision=tool_result.decision,
            findings=tool_result.findings,
            audit_ref=tool_result.audit_event.audit_id,
            planning_action=planning_actions.get("tool", "continue"),
        ),
        _security_trace_event(
            gate="output",
            decision=output_result.decision,
            findings=output_result.findings,
            audit_ref=output_result.audit_event.audit_id,
            planning_action=planning_actions.get("output", "continue"),
        ),
    ]

    return SecurityTraceSummary(
        gate_verdicts=gate_verdicts,
        planning_actions=planning_actions,
        metrics={
            "security_block_count": sum(
                1
                for decision in (
                    input_result.decision,
                    retrieval_result.decision,
                    tool_result.decision,
                    output_result.decision,
                )
                if decision is SecurityDecision.BLOCK
            ),
            "security_approval_count": 1 if tool_result.decision is SecurityDecision.REQUIRE_APPROVAL else 0,
            "security_replan_count": sum(
                1 for action in planning_actions.values() if action == "replan"
            ),
            "security_filtered_candidate_count": len(retrieval_result.blocked_candidates),
        },
        trace_events=trace_events,
    )


def _content_findings(
    content: str,
    gate: SecurityGate,
    *,
    include_prompt_injection: bool = True,
) -> list[SecurityFinding]:
    findings: list[SecurityFinding] = []
    if include_prompt_injection and PROMPT_INJECTION_PATTERN.search(content):
        findings.append(
            SecurityFinding(
                code="prompt_injection",
                gate=gate,
                severity="high",
                message="untrusted content attempts to override instructions",
            )
        )
    if SSN_PATTERN.search(content) or EMAIL_PATTERN.search(content):
        findings.append(
            SecurityFinding(
                code="pii_detected",
                gate=gate,
                severity="high",
                message="content contains PII-like data",
            )
        )
    if any(pattern.search(content) for pattern in SECRET_PATTERNS):
        findings.append(
            SecurityFinding(
                code="secret_detected",
                gate=gate,
                severity="critical",
                message="content contains secret-like data",
            )
        )
    return findings


def _output_recommended_action(findings: list[SecurityFinding]) -> str:
    codes = {finding.code for finding in findings}
    if "secret_detected" in codes or "pii_detected" in codes:
        return "refuse"
    if "unsupported_claim" in codes or "citation_coverage_low" in codes:
        return "replan"
    return "continue"


def _security_trace_event(
    *,
    gate: str,
    decision: SecurityDecision,
    findings: list[SecurityFinding],
    audit_ref: str,
    planning_action: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "gate": gate,
        "decision": decision.value,
        "planning_action": planning_action,
        "reasons": [finding.code for finding in findings],
        "audit_ref": audit_ref,
    }
    if extra:
        payload.update(extra)
    return {
        "type": "security_verdict",
        "status": decision.value,
        "payload": payload,
    }


def _audit_event(
    *,
    gate: SecurityGate,
    workspace_id: str,
    task_id: str,
    trace_id: str,
    actor: str,
    target: str,
    decision: SecurityDecision,
    risk_reasons: list[str],
    model_intent: str = "",
    proposed_args_redacted: dict[str, Any] | None = None,
    sandbox_profile: SandboxProfile = SandboxProfile.NONE,
    final_decision: str | None = None,
) -> SandboxAuditEvent:
    return SandboxAuditEvent(
        audit_id=f"audit_{trace_id or task_id or gate.value}",
        gate=gate,
        workspace_id=workspace_id,
        task_id=task_id,
        trace_id=trace_id,
        model_intent=model_intent,
        policy_decision=decision,
        final_decision=final_decision or decision.value,
        actor=actor,
        target=target,
        sandbox_profile=sandbox_profile,
        risk_reasons=risk_reasons,
        proposed_args_redacted=proposed_args_redacted or {},
    )


__all__ = [
    "GateRequest",
    "GateResult",
    "InputSecurityGate",
    "OutputSecurityGate",
    "RetrievalCandidate",
    "RetrievalGateResult",
    "RetrievalSecurityGate",
    "SandboxAuditEvent",
    "SandboxProfile",
    "SecurityDecision",
    "SecurityFinding",
    "SecurityGate",
    "SecurityTraceSummary",
    "ToolGateResult",
    "ToolSecurityGate",
    "ToolSecurityProfile",
    "build_security_trace_summary",
    "redact_sensitive_payload",
    "redact_sensitive_text",
]
