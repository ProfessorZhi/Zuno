from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Any

from zuno.agent.domain.finalization import (
    BudgetSettlement,
    ClaimCitationBinding,
    FinalCandidate,
    FinalClaim,
    FinalGateOutcome,
    FinalGateResult,
    FinalizationCommit,
    ProductDeliveryProjection,
    Publication,
    ReflexionCandidateEnvelope,
    RunOutcomeRecord,
)
from zuno.agent.domain.finalization.finalization import stable_hash, stable_ref

if TYPE_CHECKING:
    from zuno.agent.runtime.state import AgentRuntimeState


class FinalizationService:
    def commit(self, state: AgentRuntimeState) -> FinalizationCommit:
        synthesis = _latest_synthesis_metadata(state)
        answer = str(synthesis.get("final_answer") or state.goal)
        claims = _claims(synthesis)
        bindings = _bindings(synthesis, state)
        unsupported_refs = tuple(
            stable_ref("unsupported-claim", state.run_id, claim.claim_id, claim.text)
            for claim in claims
            if claim.required_evidence
            and not _supported_binding(claim.claim_id, bindings)
        )
        budget = BudgetSettlement(
            settlement_id=stable_ref("budget-settlement", state.run_id, str(state.counters.model_dump(mode="json"))),
            run_id=state.run_id,
            status="settled",
            estimated_only=True,
            usage_refs=tuple(state.trace_event_ids),
        )
        candidate = FinalCandidate(
            candidate_id=stable_ref("final-candidate", state.run_id, answer, *unsupported_refs),
            run_id=state.run_id,
            plan_version_ref=_plan_version_ref(state),
            goal_version_ref=f"goal-version:{state.task_id}:current",
            answer_content_ref=stable_ref("answer-content", state.run_id, stable_hash(answer)),
            answer_hash=stable_hash(answer),
            claims=claims,
            citation_bindings=bindings,
            unsupported_claim_refs=unsupported_refs,
            evidence_refs=tuple(_evidence_refs(state)),
            policy_refs=tuple(_policy_refs(state)),
            context_version_ref=_context_pack_ref(state),
            model_version_ref="model-role:final_synthesis:deterministic",
        )
        gate = self.evaluate_gate(state, candidate)
        publication = _publication(state, candidate, gate)
        delivery = _delivery(state, publication) if publication else None
        outcome = RunOutcomeRecord(
            outcome_id=stable_ref("run-outcome", state.run_id, gate.outcome.value, publication.publication_id if publication else ""),
            run_id=state.run_id,
            publication_ref=publication.publication_id if publication else None,
            status=_outcome_status(gate),
            final_gate_ref=gate.gate_result_id,
            budget_settlement_ref=budget.settlement_id,
        )
        reflexion = _reflexion_candidate(state, outcome, gate)
        return FinalizationCommit(
            final_candidate=candidate,
            final_gate=gate,
            budget_settlement=budget,
            publication=publication,
            run_outcome=outcome,
            delivery=delivery,
            reflexion_candidate=reflexion,
        )

    def evaluate_gate(self, state: AgentRuntimeState, candidate: FinalCandidate) -> FinalGateResult:
        reason_codes: list[str] = []
        tool_unknown_refs = tuple(_tool_unknown_refs(state))
        if tool_unknown_refs:
            reason_codes.append("tool_effect_unknown")
        if candidate.unsupported_claim_refs:
            reason_codes.append("unsupported_claim")
        if _security_revoked(state):
            reason_codes.append("security_revoked")
        if _budget_exceeded(state):
            reason_codes.append("budget_exceeded")
        reflection_decision = _enum_value(state.reflection_decision)
        if reflection_decision in {"abstain", "refuse"}:
            reason_codes.append(reflection_decision)

        if "security_revoked" in reason_codes or tool_unknown_refs:
            outcome = FinalGateOutcome.BLOCKED
        elif reflection_decision == "refuse":
            outcome = FinalGateOutcome.FAIL
        elif candidate.unsupported_claim_refs or reflection_decision == "abstain":
            outcome = FinalGateOutcome.ABSTAIN
        elif _budget_exceeded(state):
            outcome = FinalGateOutcome.BLOCKED
        else:
            outcome = FinalGateOutcome.PASS
            reason_codes.append("all_required_checks_passed")

        return FinalGateResult(
            gate_result_id=stable_ref("final-gate", candidate.candidate_id, outcome.value, *reason_codes),
            candidate_ref=candidate.candidate_id,
            outcome=outcome,
            reason_codes=tuple(reason_codes),
            unsupported_claim_refs=candidate.unsupported_claim_refs,
            tool_unknown_refs=tool_unknown_refs,
            security_epoch_ref=_security_epoch_ref(state),
            budget_settlement_ref=stable_ref("budget-settlement", state.run_id, str(state.counters.model_dump(mode="json"))),
        )


def _latest_synthesis_metadata(state: AgentRuntimeState) -> dict[str, Any]:
    for observation in reversed(state.observations):
        if observation.metadata.get("grounded_synthesis"):
            return dict(observation.metadata)
    return {"final_answer": state.goal, "claims": [], "citation_bindings": []}


def _claims(metadata: dict[str, Any]) -> tuple[FinalClaim, ...]:
    raw_claims = metadata.get("claims") or []
    claims: list[FinalClaim] = []
    for index, raw in enumerate(raw_claims, start=1):
        claims.append(
            FinalClaim(
                claim_id=str(raw.get("claim_id") or f"claim:{index}"),
                text=str(raw.get("text") or ""),
                claim_type=str(raw.get("claim_type") or "FACT"),
                confidence=float(raw.get("confidence") or 1.0),
                required_evidence=bool(raw.get("required_citation", raw.get("required_evidence", True))),
                safety_classification=str(raw.get("safety_classification") or "standard"),
            )
        )
    return tuple(claims)


def _bindings(metadata: dict[str, Any], state: AgentRuntimeState) -> tuple[ClaimCitationBinding, ...]:
    raw_bindings = metadata.get("citation_bindings") or []
    bindings: list[ClaimCitationBinding] = []
    for index, raw in enumerate(raw_bindings):
        citation_id = raw.get("citation_id") if raw.get("support_verdict") == "supported" else None
        evidence_ref = raw.get("evidence_id") or raw.get("evidence_ref")
        bindings.append(
            ClaimCitationBinding(
                claim_id=str(raw.get("claim_id") or f"claim:{index + 1}"),
                citation_id=str(citation_id) if citation_id else None,
                evidence_ref=str(evidence_ref) if evidence_ref else None,
                support_verdict=str(raw.get("support_verdict") or "insufficient"),
                lineage_ref=(
                    str(raw.get("provenance_ref"))
                    if raw.get("provenance_ref")
                    else stable_ref("citation-lineage", str(citation_id), str(evidence_ref or ""))
                ),
                authorization_ref=_security_epoch_ref(state),
                document_version_ref=(
                    str(raw.get("document_version_id")) if raw.get("document_version_id") else None
                ),
                source_span_ref=str(raw.get("source_span_id")) if raw.get("source_span_id") else None,
                provenance_ref=str(raw.get("provenance_ref")) if raw.get("provenance_ref") else None,
                failure_class=str(raw.get("failure_class")) if raw.get("failure_class") else None,
                trace_ref=str(raw.get("trace_ref")) if raw.get("trace_ref") else None,
            )
        )
    return tuple(bindings)


def _supported_binding(claim_id: str, bindings: tuple[ClaimCitationBinding, ...]) -> bool:
    return any(binding.claim_id == claim_id and binding.support_verdict == "supported" for binding in bindings)


def _evidence_refs(state: AgentRuntimeState) -> list[str]:
    refs = list(state.evidence_refs)
    for observation in state.observations:
        refs.extend(observation.evidence_ids)
    return list(dict.fromkeys(refs))


def _policy_refs(state: AgentRuntimeState) -> list[str]:
    refs = ["answer-policy:default-final-gate-v1"]
    if state.context_pack:
        refs.append(str(state.context_pack.safety_policy.get("policy_version", "context-policy:runtime")))
    return refs


def _plan_version_ref(state: AgentRuntimeState) -> str:
    if state.plan_state is None:
        return f"plan-version:{state.run_id}:deterministic"
    return state.plan_state.plan_id


def _context_pack_ref(state: AgentRuntimeState) -> str | None:
    return state.context_pack.context_pack_id if state.context_pack else None


def _security_epoch_ref(state: AgentRuntimeState) -> str:
    if state.context_pack:
        epoch = state.context_pack.safety_policy.get("effective_security_epoch_ref")
        if epoch:
            return str(epoch)
    return f"security-epoch:{state.workspace_id}:current"


def _tool_unknown_refs(state: AgentRuntimeState) -> list[str]:
    refs: list[str] = []
    for observation in state.observations:
        if _enum_value(observation.kind) != "tool":
            continue
        effect_status = str(observation.metadata.get("effect_status", "")).upper()
        if effect_status == "UNKNOWN":
            refs.append(observation.observation_id)
    return refs


def _security_revoked(state: AgentRuntimeState) -> bool:
    return any(observation.metadata.get("security_revoked") for observation in state.observations)


def _budget_exceeded(state: AgentRuntimeState) -> bool:
    return any(observation.metadata.get("budget_exceeded") for observation in state.observations)


def _publication(state: AgentRuntimeState, candidate: FinalCandidate, gate: FinalGateResult) -> Publication | None:
    if gate.outcome not in {FinalGateOutcome.PASS, FinalGateOutcome.ABSTAIN}:
        return None
    publication_id = stable_ref("publication", candidate.candidate_id, gate.outcome.value)
    return Publication(
        publication_id=publication_id,
        candidate_ref=candidate.candidate_id,
        answer_content_ref=candidate.answer_content_ref,
        answer_hash=candidate.answer_hash,
        channel="product:assistant_message",
        status="published",
        idempotency_key=stable_ref("publication-idempotency", state.run_id, candidate.answer_hash),
        delivery_ref=stable_ref("product-delivery", publication_id, "product:assistant_message"),
    )


def _delivery(state: AgentRuntimeState, publication: Publication) -> ProductDeliveryProjection:
    return ProductDeliveryProjection(
        delivery_id=publication.delivery_ref or stable_ref("product-delivery", publication.publication_id),
        publication_ref=publication.publication_id,
        channel=publication.channel,
        status="queued",
        idempotency_key=stable_ref("delivery-idempotency", state.run_id, publication.publication_id),
    )


def _outcome_status(gate: FinalGateResult) -> str:
    if gate.outcome is FinalGateOutcome.PASS:
        return "COMPLETED"
    if gate.outcome is FinalGateOutcome.ABSTAIN:
        return "ABSTAINED"
    if gate.outcome is FinalGateOutcome.BLOCKED:
        return "BLOCKED"
    if gate.outcome is FinalGateOutcome.FAIL:
        return "FAILED"
    return gate.outcome.value


def _reflexion_candidate(
    state: AgentRuntimeState,
    outcome: RunOutcomeRecord,
    gate: FinalGateResult,
) -> ReflexionCandidateEnvelope | None:
    if gate.outcome is FinalGateOutcome.PASS:
        return None
    return ReflexionCandidateEnvelope(
        candidate_id=stable_ref("reflexion-candidate", state.run_id, outcome.status, *gate.reason_codes),
        run_outcome_ref=outcome.outcome_id,
        trigger=";".join(gate.reason_codes) or outcome.status.lower(),
        review_status="candidate",
        memory_governance_required=True,
        evidence_refs=tuple(gate.unsupported_claim_refs + gate.tool_unknown_refs + tuple(state.trace_event_ids[-5:])),
    )


def commit_to_observation(commit: FinalizationCommit) -> dict[str, Any]:
    payload = commit.to_dict()
    payload["final_candidate"] = asdict(commit.final_candidate)
    return payload


def _enum_value(value: Any) -> str:
    raw = getattr(value, "value", value)
    return str(raw) if raw is not None else ""
