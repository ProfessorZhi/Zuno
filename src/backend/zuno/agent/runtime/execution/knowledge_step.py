from __future__ import annotations

from zuno.agent.contracts import PlanStep, RetrievalProfile
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution.registry import StepExecutionResult
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.knowledge.agentic import CorrectiveRetrievalRequest


class KnowledgeStepExecutor:
    action_types = frozenset({"retrieve_evidence", "compare_evidence", "answer_with_citations"})

    def execute(
        self,
        *,
        state: AgentRuntimeState,
        step: PlanStep,
        deps: RuntimeDependencies,
    ) -> StepExecutionResult:
        if deps.knowledge_runtime is not None and hasattr(deps.knowledge_runtime, "retrieve"):
            return self._execute_with_runtime(state=state, step=step, deps=deps)
        observation = NormalizedObservation(
            observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
            step_id=step.step_id,
            kind=ObservationKind.RETRIEVAL,
            status=ObservationStatus.BLOCKED,
            source="KnowledgeStepExecutor",
            summary="knowledge runtime dependency missing",
            failure_reason="missing_knowledge_runtime",
            metadata={
                "blocked": True,
                "missing_dependency": "knowledge_runtime",
                "retrieval_request": True,
                "action_type": step.action_type,
            },
        )
        return StepExecutionResult(step_id=step.step_id, status=ObservationStatus.BLOCKED, observation=observation)

    def _execute_with_runtime(
        self,
        *,
        state: AgentRuntimeState,
        step: PlanStep,
        deps: RuntimeDependencies,
    ) -> StepExecutionResult:
        request = CorrectiveRetrievalRequest(
            query=state.goal,
            workspace_id=state.workspace_id,
            knowledge_space_ids=self._knowledge_space_ids(state),
            trace_id=state.trace_id,
            task_id=state.task_id,
            tenant_id=f"user:{state.user_id}",
            snapshot_id=self._knowledge_snapshot_id(state),
            agent_core_decision_ref=f"agent-core:{state.run_id}:{step.step_id}",
            authorization_ref=self._authorization_ref(state),
            retrieval_profile=self._retrieval_profile(state),
            claims=list(step.required_evidence),
            max_rounds=int(step.budget.get("max_retrieval_rounds", 2)),
            failure_bucket=str(step.budget.get("failure_bucket", "")),
        )
        result = deps.knowledge_runtime.retrieve(request)
        ledger_records = result.ledger.records()
        evidence_ids = [record.evidence_id for record in ledger_records]
        citation_ids = [f"citation:{record.evidence_id}" for record in ledger_records if record.strict_citation_allowed]
        durable_trace = result.trace.get("durable_knowledge_port")
        graph_trace = result.trace.get("knowledge_retrieval_graph")
        control_proposal = graph_trace.get("proposal") if isinstance(graph_trace, dict) else None
        proposal_decision = _agent_core_proposal_decision(control_proposal)
        durable_blocked = isinstance(durable_trace, dict) and durable_trace.get("status") == "blocked"
        durable_failure_reason = _durable_failure_reason(durable_trace) if durable_blocked else None
        proposal_blocked = proposal_decision["decision"] != "accepted"
        observation = NormalizedObservation(
            observation_id=f"obs:{state.run_id}:{step.step_id}:{step.attempt + 1}",
            step_id=step.step_id,
            kind=ObservationKind.RETRIEVAL,
            status=ObservationStatus.BLOCKED if durable_blocked or proposal_blocked else ObservationStatus.COMPLETED,
            source=type(deps.knowledge_runtime).__name__,
            summary=f"corrective retrieval action={result.final_action.value} verdict={result.final_verdict.value}",
            failure_reason=durable_failure_reason or (
                proposal_decision["failure_reason"] if proposal_blocked else None
            ),
            evidence_ids=evidence_ids,
            citation_ids=citation_ids,
            metadata={
                "agentic_corrective_retrieval": True,
                "action_type": step.action_type,
                "final_action": result.final_action.value,
                "final_verdict": result.final_verdict.value,
                "rounds": list(result.rounds),
                "ledger": result.ledger.to_trace(),
                "knowledge_retrieval_graph": graph_trace,
                "knowledge_control_proposal": control_proposal,
                "agent_core_proposal_decision": proposal_decision,
                "durable_knowledge_port": durable_trace,
            },
        )
        return StepExecutionResult(step_id=step.step_id, status=observation.status, observation=observation)

    def _knowledge_space_ids(self, state: AgentRuntimeState) -> list[str]:
        task_state = state.context_pack.task_state if state.context_pack else {}
        raw = (
            task_state.get("knowledge_space_ids")
            or task_state.get("selected_knowledge_spaces")
            or task_state.get("knowledge_space_id")
            or []
        )
        if isinstance(raw, str):
            return [raw]
        if isinstance(raw, list):
            return [str(item) for item in raw]
        return []

    def _knowledge_snapshot_id(self, state: AgentRuntimeState) -> str | None:
        task_state = state.context_pack.task_state if state.context_pack else {}
        value = task_state.get("knowledge_snapshot_id") or task_state.get("knowledge_snapshot_ref")
        return str(value) if value else None

    def _authorization_ref(self, state: AgentRuntimeState) -> str:
        task_state = state.context_pack.task_state if state.context_pack else {}
        value = task_state.get("authorization_ref") or task_state.get("authorized_scope_ref")
        return str(value) if value else f"authorization:{state.user_id}:current"

    def _retrieval_profile(self, state: AgentRuntimeState):
        if state.retrieval_plan is not None:
            return state.retrieval_plan.effective_profile
        if state.strategy is not None and state.strategy.retrieval_profile:
            return state.strategy.retrieval_profile
        return RetrievalProfile.STANDARD


def _durable_failure_reason(durable_trace) -> str:
    if isinstance(durable_trace, dict) and durable_trace.get("reason") == "active_snapshot_unavailable":
        return "active_knowledge_snapshot_unavailable"
    return "durable_knowledge_persistence_failed"


def _agent_core_proposal_decision(control_proposal) -> dict[str, str]:
    if not isinstance(control_proposal, dict):
        return {
            "decision": "rejected",
            "proposal_type": "missing",
            "failure_reason": "knowledge_control_proposal_missing",
        }
    proposal_type = str(control_proposal.get("proposal_type") or "unknown")
    if proposal_type == "accept_evidence":
        return {
            "decision": "accepted",
            "proposal_type": proposal_type,
            "failure_reason": "",
        }
    failure_reason = {
        "abstain": "knowledge_retrieval_abstained",
        "request_user_clarification": "knowledge_requested_user_clarification",
        "request_external_tool": "knowledge_requested_external_tool",
        "request_agent_replan": "knowledge_requested_agent_replan",
        "corrective_retrieval": "knowledge_corrective_retrieval_unresolved",
    }.get(proposal_type, "knowledge_control_proposal_rejected")
    return {
        "decision": "rejected",
        "proposal_type": proposal_type,
        "failure_reason": failure_reason,
    }


__all__ = ["KnowledgeStepExecutor"]
