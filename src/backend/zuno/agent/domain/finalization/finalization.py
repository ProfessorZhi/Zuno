from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum


class FinalGateOutcome(StrEnum):
    PASS = "PASS"
    REVISE = "REVISE"
    WAIT = "WAIT"
    ABSTAIN = "ABSTAIN"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class FinalClaim:
    claim_id: str
    text: str
    claim_type: str
    confidence: float
    required_evidence: bool
    safety_classification: str


@dataclass(frozen=True, slots=True)
class ClaimCitationBinding:
    claim_id: str
    citation_id: str | None
    evidence_ref: str | None
    support_verdict: str
    lineage_ref: str | None
    authorization_ref: str


@dataclass(frozen=True, slots=True)
class FinalCandidate:
    candidate_id: str
    run_id: str
    plan_version_ref: str
    goal_version_ref: str
    answer_content_ref: str
    answer_hash: str
    claims: tuple[FinalClaim, ...]
    citation_bindings: tuple[ClaimCitationBinding, ...]
    unsupported_claim_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    policy_refs: tuple[str, ...]
    context_version_ref: str | None
    model_version_ref: str | None
    immutable: bool = True


@dataclass(frozen=True, slots=True)
class FinalGateResult:
    gate_result_id: str
    candidate_ref: str
    outcome: FinalGateOutcome
    reason_codes: tuple[str, ...]
    unsupported_claim_refs: tuple[str, ...]
    tool_unknown_refs: tuple[str, ...]
    security_epoch_ref: str
    budget_settlement_ref: str
    deterministic: bool = True


@dataclass(frozen=True, slots=True)
class Publication:
    publication_id: str
    candidate_ref: str
    answer_content_ref: str
    answer_hash: str
    channel: str
    status: str
    idempotency_key: str
    delivery_ref: str | None = None


@dataclass(frozen=True, slots=True)
class RunOutcomeRecord:
    outcome_id: str
    run_id: str
    publication_ref: str | None
    status: str
    final_gate_ref: str
    budget_settlement_ref: str
    terminal: bool = True


@dataclass(frozen=True, slots=True)
class BudgetSettlement:
    settlement_id: str
    run_id: str
    status: str
    estimated_only: bool
    usage_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProductDeliveryProjection:
    delivery_id: str
    publication_ref: str
    channel: str
    status: str
    idempotency_key: str
    retry_reexecutes_agent_run: bool = False


@dataclass(frozen=True, slots=True)
class ReflexionCandidateEnvelope:
    candidate_id: str
    run_outcome_ref: str
    trigger: str
    review_status: str
    memory_governance_required: bool
    evidence_refs: tuple[str, ...]
    hidden_reasoning_persisted: bool = False


@dataclass(frozen=True, slots=True)
class FinalizationCommit:
    final_candidate: FinalCandidate
    final_gate: FinalGateResult
    budget_settlement: BudgetSettlement
    publication: Publication | None
    run_outcome: RunOutcomeRecord
    delivery: ProductDeliveryProjection | None
    reflexion_candidate: ReflexionCandidateEnvelope | None
    commit_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "commit_hash", stable_hash(self.to_dict(include_hash=False)))

    def to_dict(self, *, include_hash: bool = True) -> dict:
        payload = {
            "final_candidate": asdict(self.final_candidate),
            "final_gate": asdict(self.final_gate),
            "budget_settlement": asdict(self.budget_settlement),
            "publication": asdict(self.publication) if self.publication else None,
            "run_outcome": asdict(self.run_outcome),
            "delivery": asdict(self.delivery) if self.delivery else None,
            "reflexion_candidate": asdict(self.reflexion_candidate) if self.reflexion_candidate else None,
        }
        if include_hash:
            payload["commit_hash"] = self.commit_hash
        return payload


def stable_hash(payload: object) -> str:
    serialized = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def stable_ref(prefix: str, *parts: str) -> str:
    return f"{prefix}:{stable_hash(parts)[:16]}"
