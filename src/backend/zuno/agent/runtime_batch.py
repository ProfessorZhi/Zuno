from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Iterable, Literal

from zuno.agent.contracts import PlanState, PlanStep
from zuno.agent.durable_runtime import (
    InMemoryDurableRuntimeStore,
    SingleControllerDurableRuntime,
)
from zuno.agent.harness import (
    ControllerRuntimeState,
    build_single_controller_runtime_harness,
)
from zuno.agent.runtime.contracts import RuntimeCounters, RuntimeLimits
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_sha256


AGENT_REQUIREMENT_IDS: tuple[str, ...] = tuple(
    f"ARCH-AGENT-{index:03d}" for index in range(1, 81)
)


class RunOutcome(StrEnum):
    SUCCEEDED = "SUCCEEDED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUSED = "REFUSED"
    ABSTAINED = "ABSTAINED"
    EXPIRED = "EXPIRED"


class ResultValidity(StrEnum):
    VALID = "VALID"
    STALE = "STALE"
    TAINTED = "TAINTED"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"


class EventChannel(StrEnum):
    DOMAIN = "DOMAIN"
    PROGRESS = "PROGRESS"
    AUDIT = "AUDIT"
    INTEGRATION = "INTEGRATION"
    PUBLICATION = "PUBLICATION"


class ControlPriority(StrEnum):
    SECURITY = "SECURITY"
    CANCELLATION = "CANCELLATION"
    DEADLINE = "DEADLINE"
    RECONCILE = "RECONCILE"
    APPROVAL = "APPROVAL"
    BUDGET = "BUDGET"
    REPLAN = "REPLAN"
    QUALITY = "QUALITY"


CONTROL_PRIORITY_ORDER: tuple[ControlPriority, ...] = (
    ControlPriority.SECURITY,
    ControlPriority.CANCELLATION,
    ControlPriority.DEADLINE,
    ControlPriority.RECONCILE,
    ControlPriority.APPROVAL,
    ControlPriority.BUDGET,
    ControlPriority.REPLAN,
    ControlPriority.QUALITY,
)


@dataclass(frozen=True, slots=True)
class TaskContract:
    task_contract_id: str
    goal_version_ref: str
    runtime_contract_version: str
    security_context_ref: str
    policy_bundle_version: str
    prompt_bundle_version: str
    contract_bundle_version: str


@dataclass(frozen=True, slots=True)
class GoalVersion:
    goal_version_ref: str
    objective_refs: tuple[str, ...]
    output_contract_ref: str
    classification: Literal[
        "SUPPLEMENTAL_INPUT",
        "CLARIFICATION_RESPONSE",
        "CONSTRAINT_CHANGE",
        "OUTPUT_CONTRACT_CHANGE",
        "OBJECTIVE_CHANGE",
        "CANCELLATION_REQUEST",
        "NEW_TASK",
    ]


@dataclass(frozen=True, slots=True)
class PlanVersionRecord:
    plan_version_ref: str
    goal_version_ref: str
    status: Literal["DRAFT", "VALIDATING", "ACTIVE", "SUPERSEDED"]
    step_ids: tuple[str, ...]
    dependency_edges: tuple[tuple[str, str], ...]
    generation: int
    immutable_hash: str

    @classmethod
    def create(
        cls,
        *,
        plan_version_ref: str,
        goal_version_ref: str,
        status: Literal["DRAFT", "VALIDATING", "ACTIVE", "SUPERSEDED"],
        step_ids: tuple[str, ...],
        dependency_edges: tuple[tuple[str, str], ...],
        generation: int,
    ) -> "PlanVersionRecord":
        payload = {
            "plan_version_ref": plan_version_ref,
            "goal_version_ref": goal_version_ref,
            "status": status,
            "step_ids": list(step_ids),
            "dependency_edges": [list(edge) for edge in dependency_edges],
            "generation": generation,
        }
        return cls(
            plan_version_ref=plan_version_ref,
            goal_version_ref=goal_version_ref,
            status=status,
            step_ids=step_ids,
            dependency_edges=dependency_edges,
            generation=generation,
            immutable_hash=canonical_sha256(payload),
        )


@dataclass(frozen=True, slots=True)
class StepRunRecord:
    step_run_id: str
    plan_step_definition_ref: str
    status: Literal["PENDING", "RUNNING", "WAITING", "COMPLETED", "FAILED"]
    disposition: Literal["ACCEPTED", "RETRY", "REPAIR", "REPLAN", "REJECTED"]
    result_validity: ResultValidity
    attempt_no: int


@dataclass(frozen=True, slots=True)
class ActionRunRecord:
    action_run_id: str
    step_run_ref: str
    proposal_ref: str
    lifecycle_status: Literal[
        "PROPOSED",
        "PREPARED",
        "WAITING_APPROVAL",
        "CLAIMED",
        "EXECUTING",
        "OBSERVED",
        "RECONCILING",
        "TERMINAL",
    ]
    outcome: Literal["SUCCEEDED", "FAILED", "UNKNOWN", "RECONCILED"]
    replay_policy: str
    approval_policy_ref: str
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class BranchResultRef:
    branch_id: str
    step_run_ref: str
    result_ref: str
    result_hash: str
    fencing_epoch: int


@dataclass(frozen=True, slots=True)
class ControlDecision:
    decision_id: str
    command_sequence_no: int
    priority: ControlPriority
    effective_security_epoch_ref: str
    generation: int
    audit_event_ref: str


@dataclass(frozen=True, slots=True)
class BudgetLedger:
    run_reservation: int
    step_reservations: dict[str, int]
    action_reservations: dict[str, int]
    consumed: dict[str, int] = field(default_factory=dict)

    def within_limits(self, limits: RuntimeLimits) -> bool:
        max_steps = limits.max_steps
        if len(self.step_reservations) > max_steps:
            return False
        token_budget = limits.token_budget
        if token_budget is not None and sum(self.consumed.values()) > token_budget:
            return False
        return all(value >= 0 for value in self.step_reservations.values())


@dataclass(frozen=True, slots=True)
class PublicationRecord:
    publication_id: str
    final_candidate_ref: str
    artifact_version_ref: str
    delivery_receipt_ref: str
    result_validity: ResultValidity
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RecoveryWatermark:
    run_id: str
    domain_generation: int
    checkpoint_generation: int
    checkpoint_ref: str
    recovery_rule: Literal["DOMAIN_WINS", "CHECKPOINT_REPLAY", "ESCALATE"]


@dataclass(frozen=True, slots=True)
class OrderedOutboxEvent:
    event_id: str
    run_id: str
    sequence_no: int
    channel: EventChannel
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ReconcilerPolicy:
    reconciler_name: str
    uses_claim: bool
    uses_fencing: bool
    uses_idempotency: bool
    escalation_policy: str


@dataclass(frozen=True, slots=True)
class TimeSemantics:
    deadline_at: datetime
    expires_at: datetime
    lease_duration: timedelta
    user_timezone: str

    def is_explicit(self) -> bool:
        return (
            self.deadline_at.tzinfo is not None
            and self.expires_at.tzinfo is not None
            and self.expires_at > self.deadline_at
            and self.lease_duration.total_seconds() > 0
            and bool(self.user_timezone)
        )


@dataclass(frozen=True, slots=True)
class AgentRuntimeBatchFixture:
    task_contract: TaskContract
    goal_version: GoalVersion
    plan_version: PlanVersionRecord
    plan_state: PlanState
    steps: tuple[StepRunRecord, ...]
    actions: tuple[ActionRunRecord, ...]
    branch_results: tuple[BranchResultRef, ...]
    control_decisions: tuple[ControlDecision, ...]
    budget_ledger: BudgetLedger
    publication: PublicationRecord
    recovery_watermark: RecoveryWatermark
    outbox_events: tuple[OrderedOutboxEvent, ...]
    reconciler_policies: tuple[ReconcilerPolicy, ...]
    time_semantics: TimeSemantics


@dataclass(frozen=True, slots=True)
class AgentRuntimeBatchReport:
    requirement_ids: tuple[str, ...]
    node_count: int
    step_count: int
    action_count: int
    outbox_count: int
    reconciler_count: int
    checkpoint_count: int


class AgentRuntimeBatchError(ValueError):
    def __init__(self, errors: Iterable[str]) -> None:
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


def build_agent_runtime_batch_fixture() -> AgentRuntimeBatchFixture:
    now = datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
    goal = GoalVersion(
        goal_version_ref="goal:v1",
        objective_refs=("objective:primary", "objective:secondary"),
        output_contract_ref="output:answer-with-artifact",
        classification="OBJECTIVE_CHANGE",
    )
    task = TaskContract(
        task_contract_id="task-contract:1",
        goal_version_ref=goal.goal_version_ref,
        runtime_contract_version="agent-runtime-v1",
        security_context_ref="security-context:1",
        policy_bundle_version="policy-bundle:1",
        prompt_bundle_version="prompt-bundle:1",
        contract_bundle_version="2026.07.wave1",
    )
    step_defs = ("step:retrieve", "step:act", "step:join", "step:final")
    plan_version = PlanVersionRecord.create(
        plan_version_ref="plan:v1",
        goal_version_ref=goal.goal_version_ref,
        status="ACTIVE",
        step_ids=step_defs,
        dependency_edges=(
            ("step:retrieve", "step:act"),
            ("step:retrieve", "step:join"),
            ("step:act", "step:join"),
            ("step:join", "step:final"),
        ),
        generation=1,
    )
    plan_state = PlanState(
        plan_id=plan_version.plan_version_ref,
        status="planned",
        steps=(
            PlanStep(
                step_id="step:retrieve",
                goal="Collect evidence",
                action_type="knowledge_query",
                required_evidence=["source_span", "citation"],
                failure_conditions=["retrieval_empty"],
                budget={"deadline_at": now.isoformat(), "snapshot_ref": "knowledge:v1"},
            ),
            PlanStep(
                step_id="step:act",
                goal="Prepare governed action",
                action_type="tool_action",
                dependencies=["step:retrieve"],
                failure_conditions=["approval_required", "unknown_effect"],
                budget={"approval_policy_ref": "approval:tool", "idempotency_required": True},
            ),
            PlanStep(
                step_id="step:join",
                goal="Join branch results",
                action_type="join",
                dependencies=["step:retrieve", "step:act"],
                failure_conditions=["branch_missing", "replan_required"],
                budget={"join_policy": "all_success_or_replan"},
            ),
            PlanStep(
                step_id="step:final",
                goal="Run final gate before publication",
                action_type="final_gate",
                dependencies=["step:join"],
                failure_conditions=["quality_failed", "result_stale"],
                budget={"answer_policy_ref": "answer:grounded"},
            ),
        ),
        current_step_id="step:retrieve",
    )
    steps = (
        StepRunRecord("sr:retrieve", "step:retrieve", "COMPLETED", "ACCEPTED", ResultValidity.VALID, 1),
        StepRunRecord("sr:act", "step:act", "WAITING", "RETRY", ResultValidity.STALE, 1),
        StepRunRecord("sr:join", "step:join", "PENDING", "REPLAN", ResultValidity.STALE, 0),
        StepRunRecord("sr:final", "step:final", "PENDING", "REJECTED", ResultValidity.SUPERSEDED, 0),
    )
    actions = (
        ActionRunRecord(
            action_run_id="ar:tool",
            step_run_ref="sr:act",
            proposal_ref="proposal:tool",
            lifecycle_status="WAITING_APPROVAL",
            outcome="UNKNOWN",
            replay_policy="RECONCILE_BEFORE_RETRY",
            approval_policy_ref="approval:tool",
            idempotency_key="idem:tool:1",
        ),
    )
    branches = (
        BranchResultRef("branch:a", "sr:retrieve", "object://branch/a", "hash:a", 1),
        BranchResultRef("branch:b", "sr:act", "object://branch/b", "hash:b", 1),
    )
    decisions = tuple(
        ControlDecision(
            decision_id=f"decision:{index}",
            command_sequence_no=index,
            priority=priority,
            effective_security_epoch_ref="epoch:security:1",
            generation=index,
            audit_event_ref=f"audit:decision:{index}",
        )
        for index, priority in enumerate(CONTROL_PRIORITY_ORDER, start=1)
    )
    outbox = tuple(
        OrderedOutboxEvent(
            event_id=f"event:{index}",
            run_id="run:agent:1",
            sequence_no=index,
            channel=channel,
            idempotency_key=f"outbox:run:agent:1:{index}",
        )
        for index, channel in enumerate(EventChannel, start=1)
    )
    reconcilers = tuple(
        ReconcilerPolicy(name, True, True, True, "ESCALATE_TO_OPERATOR")
        for name in (
            "run",
            "dispatch",
            "step",
            "unknown_action",
            "interrupt",
            "publication",
            "outbox",
            "budget",
        )
    )
    return AgentRuntimeBatchFixture(
        task_contract=task,
        goal_version=goal,
        plan_version=plan_version,
        plan_state=plan_state,
        steps=steps,
        actions=actions,
        branch_results=branches,
        control_decisions=decisions,
        budget_ledger=BudgetLedger(
            run_reservation=100,
            step_reservations={step.step_id: 20 for step in plan_state.steps},
            action_reservations={"ar:tool": 10},
            consumed={"sr:retrieve": 15},
        ),
        publication=PublicationRecord(
            publication_id="publication:1",
            final_candidate_ref="final-candidate:1",
            artifact_version_ref="artifact-version:1",
            delivery_receipt_ref="delivery-receipt:1",
            result_validity=ResultValidity.VALID,
            idempotency_key="publication:idem:1",
        ),
        recovery_watermark=RecoveryWatermark(
            run_id="run:agent:1",
            domain_generation=2,
            checkpoint_generation=2,
            checkpoint_ref="checkpoint:2",
            recovery_rule="CHECKPOINT_REPLAY",
        ),
        outbox_events=outbox,
        reconciler_policies=reconcilers,
        time_semantics=TimeSemantics(
            deadline_at=now,
            expires_at=now + timedelta(hours=1),
            lease_duration=timedelta(minutes=5),
            user_timezone="Asia/Shanghai",
        ),
    )


def validate_agent_runtime_batch(
    fixture: AgentRuntimeBatchFixture | None = None,
) -> AgentRuntimeBatchReport:
    fixture = fixture or build_agent_runtime_batch_fixture()
    errors: list[str] = []
    harness = build_single_controller_runtime_harness()

    errors.extend(_validate_controller_harness(harness))
    errors.extend(_validate_task_goal_plan(fixture))
    errors.extend(_validate_plan_dag(fixture))
    errors.extend(_validate_state_and_durability(harness))
    errors.extend(_validate_budget_and_time(fixture))
    errors.extend(_validate_step_action_branch_boundaries(fixture))
    errors.extend(_validate_cross_module_boundary(fixture))
    errors.extend(_validate_effect_reconcile(fixture))
    errors.extend(_validate_final_publication_outcome(fixture))
    errors.extend(_validate_failure_recovery_events(fixture))

    if errors:
        raise AgentRuntimeBatchError(errors)

    durable_snapshot = _durable_snapshot()
    return AgentRuntimeBatchReport(
        requirement_ids=AGENT_REQUIREMENT_IDS,
        node_count=len(harness.node_names()),
        step_count=len(fixture.steps),
        action_count=len(fixture.actions),
        outbox_count=len(fixture.outbox_events),
        reconciler_count=len(fixture.reconciler_policies),
        checkpoint_count=len(durable_snapshot.checkpoint_ids),
    )


def _validate_controller_harness(harness: object) -> list[str]:
    errors: list[str] = []
    expected_nodes = (
        "prepare_context",
        "intent_and_policy_route",
        "plan",
        "act_react_loop",
        "observe",
        "evidence_check",
        "reflect",
        "replan_if_needed",
        "answer_or_artifact",
        "post_turn_commit",
    )
    node_names = tuple(harness.node_names())  # type: ignore[attr-defined]
    if node_names != expected_nodes:
        errors.append(f"AgentRunGraph node order mismatch: {node_names}")
    if getattr(harness, "runtime_topology", "") != "single_controller":
        errors.append("runtime topology must be single_controller")
    for node in expected_nodes:
        contract = harness.node_contract(node)  # type: ignore[attr-defined]
        if not contract.trace_span.startswith("runtime."):
            errors.append(f"{node} missing runtime trace span")
        if contract.checkpoint_policy not in {"after", "before_and_after"}:
            errors.append(f"{node} has unsupported checkpoint policy")
    return errors


def _validate_task_goal_plan(fixture: AgentRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    if fixture.task_contract.goal_version_ref != fixture.goal_version.goal_version_ref:
        errors.append("TaskContract must bind GoalVersion")
    if fixture.plan_version.goal_version_ref != fixture.goal_version.goal_version_ref:
        errors.append("PlanVersion must bind GoalVersion")
    if fixture.plan_state.plan_id != fixture.plan_version.plan_version_ref:
        errors.append("PlanState must use active PlanVersion ref")
    if fixture.plan_version.status != "ACTIVE":
        errors.append("exactly one active PlanVersion is required for the fixture")
    if fixture.goal_version.classification not in {
        "SUPPLEMENTAL_INPUT",
        "CLARIFICATION_RESPONSE",
        "CONSTRAINT_CHANGE",
        "OUTPUT_CONTRACT_CHANGE",
        "OBJECTIVE_CHANGE",
        "CANCELLATION_REQUEST",
        "NEW_TASK",
    }:
        errors.append("user input classification is not explicit")
    if not fixture.task_contract.security_context_ref:
        errors.append("TaskContract missing security context ref")
    return errors


def _validate_plan_dag(fixture: AgentRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    step_ids = set(fixture.plan_version.step_ids)
    if len(step_ids) != len(fixture.plan_version.step_ids):
        errors.append("PlanVersion step ids must be unique")
    for before, after in fixture.plan_version.dependency_edges:
        if before not in step_ids or after not in step_ids:
            errors.append(f"dependency edge references unknown step: {before}->{after}")
    if _has_cycle(fixture.plan_version.dependency_edges):
        errors.append("Plan DAG contains a cycle")
    if not any(len(step.dependencies) > 1 for step in fixture.plan_state.steps):
        errors.append("Plan DAG must include a join step with multiple dependencies")
    return errors


def _has_cycle(edges: tuple[tuple[str, str], ...]) -> bool:
    graph: dict[str, set[str]] = {}
    for before, after in edges:
        graph.setdefault(before, set()).add(after)
        graph.setdefault(after, set())
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        for next_node in graph[node]:
            if visit(next_node):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def _validate_state_and_durability(harness: object) -> list[str]:
    errors: list[str] = []
    state = _controller_state("runtime-batch")
    checkpoint = harness.checkpoint_state(state, node="plan")  # type: ignore[attr-defined]
    resumed = harness.resume_from_checkpoint(checkpoint)  # type: ignore[attr-defined]
    if resumed.to_dict() != state.to_dict():
        errors.append("Runtime State must serialize and resume exactly")
    snapshot = _durable_snapshot()
    if snapshot.pending_interrupt is not None:
        errors.append("approved durable run must clear pending interrupt")
    if not snapshot.checkpoint_ids or snapshot.latest_checkpoint is None:
        errors.append("durable runtime must persist checkpoints")
    event_types = [event.type for event in snapshot.events]
    if "runtime_resumed" not in event_types or event_types[-1] != "runtime_completed":
        errors.append("durable runtime must record resume and completion events")
    return errors


def _controller_state(task_id: str) -> ControllerRuntimeState:
    return ControllerRuntimeState(
        thread_id=f"thread:{task_id}",
        workspace_id="workspace:agent",
        user_id="user:agent",
        task_id=task_id,
        trace_id=f"trace:{task_id}",
        goal="validate agent runtime batch",
        context_pack={"refs": ["object://context"], "knowledge_snapshot_ref": "knowledge:v1"},
    )


def _durable_snapshot():
    runtime = SingleControllerDurableRuntime(store=InMemoryDurableRuntimeStore())
    runtime.start_task(
        _controller_state("durable-runtime-batch"),
        interrupt_at_node="act_react_loop",
        required_approval="tool:external-write",
        interrupt_payload={"approval_ref": "approval:1"},
    )
    return runtime.resume_task(
        task_id="durable-runtime-batch",
        approval_decision="approved",
        comment="batch validation",
    )


def _validate_budget_and_time(fixture: AgentRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    limits = RuntimeLimits(max_steps=8, max_replans=2, max_actions_per_step=4, token_budget=100)
    counters = RuntimeCounters(steps_executed=1, replans=1, reflections=1)
    if not fixture.budget_ledger.within_limits(limits):
        errors.append("Budget ledger exceeds runtime limits")
    if counters.replans > limits.max_replans:
        errors.append("Runtime counters exceed replan limits")
    if not fixture.time_semantics.is_explicit():
        errors.append("time semantics must use aware deadline/expiry, positive lease and timezone")
    return errors


def _validate_step_action_branch_boundaries(
    fixture: AgentRuntimeBatchFixture,
) -> list[str]:
    errors: list[str] = []
    step_run_ids = {step.step_run_id for step in fixture.steps}
    if not all(step.result_validity in ResultValidity for step in fixture.steps):
        errors.append("each StepRun must carry ResultValidity")
    for action in fixture.actions:
        if action.step_run_ref not in step_run_ids:
            errors.append(f"ActionRun references unknown StepRun: {action.action_run_id}")
        if action.outcome == "UNKNOWN" and action.replay_policy != "RECONCILE_BEFORE_RETRY":
            errors.append("UNKNOWN action cannot be retried without reconcile")
        if not action.approval_policy_ref or not action.idempotency_key:
            errors.append("side-effect action missing approval or idempotency policy")
    for branch in fixture.branch_results:
        if branch.step_run_ref not in step_run_ids:
            errors.append(f"BranchResultRef references unknown StepRun: {branch.branch_id}")
        if not branch.result_ref.startswith("object://"):
            errors.append("BranchResultRef must return a ref, not inline payload")
        if branch.fencing_epoch < 1:
            errors.append("BranchResultRef missing fencing epoch")
    return errors


def _validate_cross_module_boundary(fixture: AgentRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    payload = {"task_contract_ref": fixture.task_contract.task_contract_id}
    envelope = CrossModuleEnvelopeV1(
        contract_name="TaskContract",
        contract_version="1.0",
        contract_bundle_version=fixture.task_contract.contract_bundle_version,
        message_id="message:agent:1",
        producer_module="Product Surface",
        consumer_module="Agent Core",
        tenant_id="tenant:agent",
        workspace_id="workspace:agent",
        correlation_id="correlation:agent:1",
        trace_id="trace:agent:1",
        data_classification="internal",
        occurred_at=datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
        created_at=datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc),
        payload=payload,
        payload_hash=canonical_sha256(payload),
        payload_schema_hash="schema:task-contract:v1",
        idempotency_key="idem:agent:task-contract",
        expected_generation=fixture.plan_version.generation,
        effective_security_epoch_ref="epoch:security:1",
        effective_security_epoch_hash="hash:epoch:1",
        deadline_at=fixture.time_semantics.deadline_at,
    )
    if envelope.payload_hash != canonical_sha256(payload):
        errors.append("cross-module envelope payload hash mismatch")
    if envelope.consumer_module != "Agent Core":
        errors.append("Agent Core must consume versioned contract envelope")
    return errors


def _validate_effect_reconcile(fixture: AgentRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    if not any(action.outcome == "UNKNOWN" for action in fixture.actions):
        errors.append("fixture must cover UNKNOWN effect boundary")
    if len(fixture.reconciler_policies) < 8:
        errors.append("Run/Dispatch/Step/UNKNOWN/Interrupt/Publication/Outbox/Budget reconcilers required")
    for policy in fixture.reconciler_policies:
        if not (policy.uses_claim and policy.uses_fencing and policy.uses_idempotency):
            errors.append(f"reconciler missing claim/fencing/idempotency: {policy.reconciler_name}")
        if not policy.escalation_policy:
            errors.append(f"reconciler missing escalation policy: {policy.reconciler_name}")
    return errors


def _validate_final_publication_outcome(fixture: AgentRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    if fixture.publication.result_validity != ResultValidity.VALID:
        errors.append("Publication must revalidate ResultValidity before delivery")
    if not fixture.publication.delivery_receipt_ref:
        errors.append("Publication missing DeliveryReceipt")
    if not fixture.publication.final_candidate_ref or not fixture.publication.artifact_version_ref:
        errors.append("FinalCandidate, ArtifactVersion and Publication must be separate")
    if set(item.value for item in RunOutcome) != {
        "SUCCEEDED",
        "PARTIAL",
        "FAILED",
        "CANCELLED",
        "REFUSED",
        "ABSTAINED",
        "EXPIRED",
    }:
        errors.append("RunOutcome taxonomy is incomplete")
    return errors


def _validate_failure_recovery_events(fixture: AgentRuntimeBatchFixture) -> list[str]:
    errors: list[str] = []
    priorities = tuple(decision.priority for decision in fixture.control_decisions)
    if priorities != CONTROL_PRIORITY_ORDER:
        errors.append("control decision priority order is not deterministic")
    if not all(decision.audit_event_ref and decision.generation >= 1 for decision in fixture.control_decisions):
        errors.append("ControlDecision must be audited and carry generation")
    if fixture.recovery_watermark.domain_generation != fixture.recovery_watermark.checkpoint_generation:
        errors.append("Domain generation and checkpoint generation must be coordinated")
    if not fixture.recovery_watermark.checkpoint_ref:
        errors.append("RecoveryWatermark missing checkpoint ref")
    channels = {event.channel for event in fixture.outbox_events}
    if channels != set(EventChannel):
        errors.append("Domain/Progress/Audit/Integration/Publication events must be separated")
    sequences = [event.sequence_no for event in fixture.outbox_events]
    if sequences != sorted(sequences) or len(set(sequences)) != len(sequences):
        errors.append("Outbox sequence must be ordered and unique per run")
    if not all(event.idempotency_key for event in fixture.outbox_events):
        errors.append("Outbox events must carry idempotency keys")
    return errors


__all__ = [
    "AGENT_REQUIREMENT_IDS",
    "AgentRuntimeBatchError",
    "AgentRuntimeBatchFixture",
    "AgentRuntimeBatchReport",
    "BranchResultRef",
    "BudgetLedger",
    "ControlDecision",
    "ControlPriority",
    "EventChannel",
    "GoalVersion",
    "PlanVersionRecord",
    "PublicationRecord",
    "ReconcilerPolicy",
    "RecoveryWatermark",
    "ResultValidity",
    "RunOutcome",
    "StepRunRecord",
    "TaskContract",
    "TimeSemantics",
    "build_agent_runtime_batch_fixture",
    "validate_agent_runtime_batch",
]
