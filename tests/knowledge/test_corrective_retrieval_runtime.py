from __future__ import annotations

from zuno.agent.contracts import ContextPack, PlanStep, RetrievalProfile
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution import KnowledgeStepExecutor
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.knowledge.agentic import (
    CorrectiveAction,
    CorrectiveAgenticGraphRAGRuntime,
    CorrectiveAgenticRetrievalRuntime,
    CorrectiveRetrievalRequest,
    DurableKnowledgeRetrievalPort,
    KnowledgeControlProposalType,
    KnowledgeRetrievalGraphNode,
    QueryStrategy,
    RetrieverAttemptStatus,
    RetrieverKind,
)
from zuno.knowledge.agentic_graphrag import AgenticRetrievalRuntimeRequest, AgenticRetrievalRuntimeResult
from zuno.knowledge.indexing import KnowledgeIndexRuntime
from zuno.knowledge.ingestion import CanonicalDocumentIR, DocumentBlock, DocumentMetadata, DocumentProvenance, SourceSpan


def _index_runtime() -> KnowledgeIndexRuntime:
    index = KnowledgeIndexRuntime()
    index.create_knowledge_space("ks_corrective", "workspace_corrective")
    index.index_document(
        "ks_corrective",
        CanonicalDocumentIR(
            metadata=DocumentMetadata(
                document_id="doc_corrective",
                workspace_id="workspace_corrective",
                source_uri="memory://corrective.md",
                mime_type="text/markdown",
                hash="sha256-corrective",
                parser_id="native",
                parser_version="phase08-test",
            ),
            blocks=[
                DocumentBlock(
                    block_id="block_notice",
                    type="paragraph",
                    text="Renewal notice must be sent 30 days before anniversary.",
                    source_span=SourceSpan(page=3, line_range=[8, 9]),
                )
            ],
            provenance=DocumentProvenance(
                parser_id="native",
                parser_version="phase08-test",
                source_uri="memory://corrective.md",
                confidence=1.0,
            ),
        ),
        targets=["bm25", "vector", "graph"],
    )
    return index


def _runtime() -> CorrectiveAgenticRetrievalRuntime:
    index = _index_runtime()
    return CorrectiveAgenticRetrievalRuntime(index_runtime=index)


def test_corrective_runtime_runs_second_round_after_doc_miss() -> None:
    result = _runtime().retrieve(
        CorrectiveRetrievalRequest(
            query="indemnity waiver",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_corrective",
            task_id="task_corrective",
            failure_bucket="doc_miss",
            max_rounds=2,
        )
    )

    assert len(result.rounds) == 2
    assert result.rounds[0]["corrective_action"] == CorrectiveAction.QUERY_REWRITE.value
    assert result.rounds[1]["query_strategy"] == QueryStrategy.REWRITE.value
    assert result.rounds[1]["query"] != result.rounds[0]["query"]
    assert result.final_action == CorrectiveAction.ABSTAIN
    assert result.trace["ledger"]["rounds"] == []


def test_corrective_runtime_continues_when_first_round_has_strict_source_span() -> None:
    result = _runtime().retrieve(
        CorrectiveRetrievalRequest(
            query="renewal notice 30 days anniversary",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_corrective_pass",
            task_id="task_corrective_pass",
            max_rounds=2,
        )
    )

    assert len(result.rounds) == 1
    assert result.rounds[0]["corrective_action"] == CorrectiveAction.CONTINUE.value
    assert result.ledger.records()[0].source_span["page"] == 3
    assert result.ledger.records()[0].strict_citation_allowed is True


def test_corrective_graphrag_default_path_preserves_legacy_answer_contract() -> None:
    runtime = CorrectiveAgenticGraphRAGRuntime(index_runtime=_index_runtime())

    result = runtime.answer(
        AgenticRetrievalRuntimeRequest(
            query="renewal notice 30 days anniversary",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_default_cutover",
            task_id="task_default_cutover",
            retrieval_profile=RetrievalProfile.STANDARD,
            allowed_acl_scopes={"workspace"},
            budget={"retrieval_max_rounds": 1},
        )
    )

    assert isinstance(result, AgenticRetrievalRuntimeResult)
    assert result.trace_metadata["phase18_default_path"] is True
    assert result.trace_metadata["corrective_final_action"] == CorrectiveAction.CONTINUE.value
    assert result.trace_metadata["knowledge_retrieval_graph"]["fixed_graph"] == [
        node.value for node in KnowledgeRetrievalGraphNode
    ]
    assert result.trace_metadata["knowledge_control_proposal"]["proposal_type"] == (
        KnowledgeControlProposalType.ACCEPT_EVIDENCE.value
    )
    assert result.to_task_event()["payload"]["citation_ids"]


def test_corrective_runtime_does_not_accept_incomplete_claim_coverage() -> None:
    result = _runtime().retrieve(
        CorrectiveRetrievalRequest(
            query="renewal notice 30 days anniversary",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_coverage_gap",
            task_id="task_coverage_gap",
            claims=["renewal notice", "missing claim"],
            max_rounds=1,
        )
    )

    frontier = result.trace["knowledge_retrieval_graph"]["proposal"]["payload"]["frontier"]
    assert frontier["coverage"]["covered_claim_count"] == 1
    assert frontier["uncovered_claim_refs"] == ["missing claim"]
    assert frontier["stop_reasons"] == ["coverage_incomplete"]
    assert result.final_action == CorrectiveAction.ABSTAIN
    assert result.trace["knowledge_retrieval_graph"]["proposal"]["proposal_type"] == (
        KnowledgeControlProposalType.ABSTAIN.value
    )


def test_corrective_runtime_records_fixed_knowledge_retrieval_graph() -> None:
    result = _runtime().retrieve(
        CorrectiveRetrievalRequest(
            query="renewal notice 30 days anniversary",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_graph_contract",
            task_id="task_graph_contract",
            snapshot_id="snapshot:phase18",
            max_rounds=1,
        )
    )

    assert result.graph_trace.fixed_graph == list(KnowledgeRetrievalGraphNode)
    assert result.graph_trace.node_sequence() == [
        "validate",
        "pin_snapshot",
        "scope",
        "interpret",
        "select_profile",
        "plan_round",
        "admit",
        "dispatch",
        "normalize",
        "fuse_rerank",
        "evidence_ledger",
        "evaluate",
        "corrective_decision",
    ]
    graph_trace = result.trace["knowledge_retrieval_graph"]
    assert graph_trace["snapshot_id"] == "snapshot:phase18"
    assert graph_trace["proposal"]["proposal_type"] == KnowledgeControlProposalType.ACCEPT_EVIDENCE.value
    assert graph_trace["proposal"]["requires_agent_core_decision"] is True
    assert graph_trace["proposal"]["accepted_by_knowledge"] is False


def test_corrective_runtime_plans_admitted_parallel_retriever_dispatch() -> None:
    result = _runtime().retrieve(
        CorrectiveRetrievalRequest(
            query="renewal notice 30 days anniversary",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_dispatch_plan",
            task_id="task_dispatch_plan",
            retrieval_profile=RetrievalProfile.DEEP,
            round_budget_tokens=600,
            retriever_timeout_ms=750,
            max_rounds=1,
        )
    )

    graph_trace = result.trace["knowledge_retrieval_graph"]
    plan_event = next(event for event in graph_trace["node_events"] if event["node"] == "plan_round")
    admit_event = next(event for event in graph_trace["node_events"] if event["node"] == "admit")
    dispatch_event = next(event for event in graph_trace["node_events"] if event["node"] == "dispatch")
    retrievers = plan_event["payload"]["retrievers"]

    assert plan_event["payload"]["profile"] == "deep"
    assert [item["retriever"] for item in retrievers] == [kind.value for kind in RetrieverKind]
    assert {item["budget_tokens"] for item in retrievers} == {100}
    assert {item["timeout_ms"] for item in retrievers} == {750}
    assert admit_event["status"] == "admitted"
    assert admit_event["payload"]["round_budget_tokens"] == 600
    assert dispatch_event["payload"]["parallel_group"] == "trace_dispatch_plan:retrieval-round:1"


def test_corrective_runtime_blocks_admission_when_budget_is_exhausted() -> None:
    result = _runtime().retrieve(
        CorrectiveRetrievalRequest(
            query="renewal notice 30 days anniversary",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_budget_exhausted",
            task_id="task_budget_exhausted",
            round_budget_tokens=0,
            max_rounds=1,
        )
    )

    graph_trace = result.trace["knowledge_retrieval_graph"]
    admit_event = next(event for event in graph_trace["node_events"] if event["node"] == "admit")
    assert admit_event["status"] == "blocked"
    assert admit_event["payload"]["admission_reason"] == "budget_exhausted"
    assert [event["node"] for event in graph_trace["node_events"]].count("dispatch") == 0
    assert result.rounds[0]["admission_reason"] == "budget_exhausted"
    assert graph_trace["proposal"]["proposal_type"] == KnowledgeControlProposalType.ABSTAIN.value


def test_corrective_runtime_blocks_when_required_retriever_times_out() -> None:
    result = _runtime().retrieve(
        CorrectiveRetrievalRequest(
            query="renewal notice 30 days anniversary",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_bm25_timeout",
            task_id="task_bm25_timeout",
            retriever_failure_modes={"bm25": "timeout"},
            max_rounds=1,
        )
    )

    graph_trace = result.trace["knowledge_retrieval_graph"]
    normalize_event = next(event for event in graph_trace["node_events"] if event["node"] == "normalize")
    bm25_attempt = next(
        attempt for attempt in normalize_event["payload"]["attempts"] if attempt["retriever"] == RetrieverKind.BM25.value
    )
    assert normalize_event["status"] == "blocked"
    assert normalize_event["payload"]["blocking_failure"] == "retriever_timeout"
    assert bm25_attempt["status"] == RetrieverAttemptStatus.TIMEOUT.value
    assert bm25_attempt["accepted"] is False
    assert [event["node"] for event in graph_trace["node_events"]].count("fuse_rerank") == 0
    assert result.rounds[0]["retriever_failure"] == "retriever_timeout"
    assert graph_trace["proposal"]["proposal_type"] == KnowledgeControlProposalType.ABSTAIN.value


def test_corrective_runtime_fences_late_optional_graph_result_without_blocking_text_evidence() -> None:
    result = _runtime().retrieve(
        CorrectiveRetrievalRequest(
            query="renewal notice 30 days anniversary",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_late_community",
            task_id="task_late_community",
            retrieval_profile=RetrievalProfile.DEEP,
            retriever_failure_modes={"community": "late"},
            max_rounds=1,
        )
    )

    graph_trace = result.trace["knowledge_retrieval_graph"]
    normalize_event = next(event for event in graph_trace["node_events"] if event["node"] == "normalize")
    community_attempt = next(
        attempt
        for attempt in normalize_event["payload"]["attempts"]
        if attempt["retriever"] == RetrieverKind.COMMUNITY.value
    )
    assert normalize_event["status"] == "completed"
    assert community_attempt["status"] == RetrieverAttemptStatus.LATE_RESULT_FENCED.value
    assert community_attempt["late_result"] is True
    assert community_attempt["accepted"] is False
    assert result.final_action == CorrectiveAction.CONTINUE
    assert graph_trace["proposal"]["proposal_type"] == KnowledgeControlProposalType.ACCEPT_EVIDENCE.value


def test_knowledge_step_executor_consumes_corrective_retrieval_runtime() -> None:
    state = AgentRuntimeState(
        run_id="run_corrective",
        thread_id="thread_corrective",
        workspace_id="workspace_corrective",
        user_id="user_corrective",
        task_id="task_corrective_step",
        trace_id="trace_corrective_step",
        goal="renewal notice 30 days anniversary",
        context_pack=ContextPack(
            context_pack_id="context_corrective",
            user_goal="renewal notice 30 days anniversary",
            task_state={"knowledge_space_ids": ["ks_corrective"]},
        ),
    )
    step = PlanStep(
        step_id="step_retrieve",
        goal="retrieve grounded renewal evidence",
        action_type="retrieve_evidence",
    )

    result = KnowledgeStepExecutor().execute(
        state=state,
        step=step,
        deps=RuntimeDependencies(knowledge_runtime=_runtime()),
    )

    assert result.observation.metadata["agentic_corrective_retrieval"] is True
    assert result.observation.metadata["final_action"] == CorrectiveAction.CONTINUE.value
    assert result.observation.metadata["ledger"]["record_count"] == 1
    graph_trace = result.observation.metadata["knowledge_retrieval_graph"]
    assert graph_trace["fixed_graph"] == [node.value for node in KnowledgeRetrievalGraphNode]
    assert result.observation.metadata["knowledge_control_proposal"]["proposal_type"] == (
        KnowledgeControlProposalType.ACCEPT_EVIDENCE.value
    )
    assert result.observation.metadata["agent_core_proposal_decision"] == {
        "decision": "accepted",
        "proposal_type": KnowledgeControlProposalType.ACCEPT_EVIDENCE.value,
        "failure_reason": "",
    }
    assert result.observation.evidence_ids
    assert result.observation.citation_ids


def test_knowledge_step_blocks_when_agent_core_rejects_abstain_proposal() -> None:
    state = AgentRuntimeState(
        run_id="run_abstain_proposal",
        thread_id="thread_abstain_proposal",
        workspace_id="workspace_corrective",
        user_id="user_abstain_proposal",
        task_id="task_abstain_proposal",
        trace_id="trace_abstain_proposal",
        goal="indemnity waiver",
        context_pack=ContextPack(
            context_pack_id="context_abstain_proposal",
            user_goal="indemnity waiver",
            task_state={"knowledge_space_ids": ["ks_corrective"]},
        ),
    )
    step = PlanStep(
        step_id="step_abstain_proposal",
        goal="retrieve missing indemnity evidence",
        action_type="retrieve_evidence",
        budget={"failure_bucket": "doc_miss", "max_retrieval_rounds": 2},
    )

    result = KnowledgeStepExecutor().execute(
        state=state,
        step=step,
        deps=RuntimeDependencies(knowledge_runtime=_runtime()),
    )

    assert result.observation.status == "blocked"
    assert result.observation.failure_reason == "knowledge_retrieval_abstained"
    assert result.observation.metadata["knowledge_control_proposal"]["proposal_type"] == (
        KnowledgeControlProposalType.ABSTAIN.value
    )
    assert result.observation.metadata["agent_core_proposal_decision"] == {
        "decision": "rejected",
        "proposal_type": KnowledgeControlProposalType.ABSTAIN.value,
        "failure_reason": "knowledge_retrieval_abstained",
    }


class _CaptureRequestRuntime:
    def __init__(self) -> None:
        self.request: CorrectiveRetrievalRequest | None = None

    def retrieve(self, request: CorrectiveRetrievalRequest):
        self.request = request
        return _runtime().retrieve(request)


def test_knowledge_step_executor_defaults_to_standard_retrieval_profile() -> None:
    runtime = _CaptureRequestRuntime()
    state = AgentRuntimeState(
        run_id="run_standard_default",
        thread_id="thread_standard_default",
        workspace_id="workspace_corrective",
        user_id="user_standard_default",
        task_id="task_standard_default",
        trace_id="trace_standard_default",
        goal="renewal notice 30 days anniversary",
        context_pack=ContextPack(
            context_pack_id="context_standard_default",
            user_goal="renewal notice 30 days anniversary",
            task_state={"knowledge_space_ids": ["ks_corrective"]},
        ),
    )

    result = KnowledgeStepExecutor().execute(
        state=state,
        step=PlanStep(
            step_id="step_retrieve_standard_default",
            goal="retrieve grounded renewal evidence",
            action_type="retrieve_evidence",
        ),
        deps=RuntimeDependencies(knowledge_runtime=runtime),
    )

    assert result.observation.status == "completed"
    assert runtime.request is not None
    assert runtime.request.retrieval_profile == RetrievalProfile.STANDARD


class _FakeKnowledgeRepo:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []
        self.strict_ids: set[str] = set()

    def active_snapshot_id(self, *, tenant_id: str, knowledge_space_id: str) -> str | None:
        self.calls.append(("active_snapshot_id", {"tenant_id": tenant_id, "knowledge_space_id": knowledge_space_id}))
        return "knowledge-snapshot:fake"

    def start_query_run(self, **kwargs) -> None:
        self.calls.append(("start_query_run", kwargs))

    def start_retrieval_round(self, **kwargs) -> None:
        self.calls.append(("start_retrieval_round", kwargs))

    def commit_evidence(self, **kwargs) -> None:
        self.calls.append(("commit_evidence", kwargs))
        self.strict_ids.add(str(kwargs["evidence_id"]))

    def commit_citation_lineage(self, **kwargs) -> None:
        self.calls.append(("commit_citation_lineage", kwargs))

    def mark_query_run_status(self, **kwargs) -> None:
        self.calls.append(("mark_query_run_status", kwargs))

    def strict_evidence_ids(self, *, query_run_id: str) -> tuple[str, ...]:
        self.calls.append(("strict_evidence_ids", {"query_run_id": query_run_id}))
        return tuple(sorted(self.strict_ids))


class _FakeKnowledgeUow:
    def __init__(self, repo: _FakeKnowledgeRepo) -> None:
        self.repo = repo

    def __enter__(self) -> _FakeKnowledgeRepo:
        return self.repo

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _FailingKnowledgeRepo(_FakeKnowledgeRepo):
    def start_query_run(self, **kwargs) -> None:
        self.calls.append(("start_query_run", kwargs))
        raise RuntimeError("postgres-write-unavailable")


class _MissingSnapshotKnowledgeRepo(_FakeKnowledgeRepo):
    def active_snapshot_id(self, *, tenant_id: str, knowledge_space_id: str) -> str | None:
        self.calls.append(("active_snapshot_id", {"tenant_id": tenant_id, "knowledge_space_id": knowledge_space_id}))
        return None


def test_durable_knowledge_port_commits_query_round_evidence_and_citation_lineage() -> None:
    repo = _FakeKnowledgeRepo()
    runtime = DurableKnowledgeRetrievalPort(
        runtime=_runtime(),
        unit_of_work_factory=lambda: _FakeKnowledgeUow(repo),
    )

    result = runtime.retrieve(
        CorrectiveRetrievalRequest(
            query="renewal notice 30 days anniversary",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_durable_knowledge",
            task_id="task_durable_knowledge",
            tenant_id="tenant-durable",
            agent_core_decision_ref="agent-core:decision:retrieve",
            authorization_ref="authorization:durable",
            max_rounds=1,
        )
    )

    call_names = [name for name, _ in repo.calls]
    assert call_names == [
        "active_snapshot_id",
        "start_query_run",
        "strict_evidence_ids",
        "start_retrieval_round",
        "commit_evidence",
        "commit_citation_lineage",
        "mark_query_run_status",
    ]
    evidence_call = dict(repo.calls[4][1])
    citation_call = dict(repo.calls[5][1])
    query_call = dict(repo.calls[1][1])
    assert query_call["request_payload"]["retrieval_profile"] == RetrievalProfile.STANDARD.value
    assert evidence_call["chunk_id"].endswith("block_notice::cite1")
    assert evidence_call["source_span_ref"].startswith("source-span:")
    assert citation_call["document_version_id"] == "sha256-corrective"
    assert citation_call["authorization_ref"] == "authorization:durable"
    assert result.trace["durable_knowledge_port"]["status"] == "committed"
    assert result.trace["durable_knowledge_port"]["evidence_committed"] == 1
    assert result.trace["durable_knowledge_port"]["evidence_replayed"] == 0


def test_durable_knowledge_port_replays_existing_query_run_without_duplicate_evidence() -> None:
    repo = _FakeKnowledgeRepo()
    runtime = DurableKnowledgeRetrievalPort(
        runtime=_runtime(),
        unit_of_work_factory=lambda: _FakeKnowledgeUow(repo),
    )
    request = CorrectiveRetrievalRequest(
        query="renewal notice 30 days anniversary",
        workspace_id="workspace_corrective",
        knowledge_space_ids=["ks_corrective"],
        trace_id="trace_durable_replay",
        task_id="task_durable_replay",
        tenant_id="tenant-durable",
        agent_core_decision_ref="agent-core:decision:retrieve",
        authorization_ref="authorization:durable",
        max_rounds=1,
    )

    first = runtime.retrieve(request)
    second = runtime.retrieve(request)

    assert first.trace["durable_knowledge_port"]["status"] == "committed"
    assert second.trace["durable_knowledge_port"]["status"] == "idempotent_replay"
    assert second.trace["durable_knowledge_port"]["evidence_committed"] == 0
    assert second.trace["durable_knowledge_port"]["evidence_replayed"] == 1
    assert [name for name, _ in repo.calls].count("commit_evidence") == 1
    assert [name for name, _ in repo.calls].count("commit_citation_lineage") == 2


def test_knowledge_step_blocks_when_durable_persistence_fails() -> None:
    repo = _FailingKnowledgeRepo()
    runtime = DurableKnowledgeRetrievalPort(
        runtime=_runtime(),
        unit_of_work_factory=lambda: _FakeKnowledgeUow(repo),
    )
    state = AgentRuntimeState(
        run_id="run_durable_fail",
        thread_id="thread_durable_fail",
        workspace_id="workspace_corrective",
        user_id="user_durable_fail",
        task_id="task_durable_fail",
        trace_id="trace_durable_fail",
        goal="renewal notice 30 days anniversary",
        context_pack=ContextPack(
            context_pack_id="context_durable_fail",
            user_goal="renewal notice 30 days anniversary",
            task_state={"knowledge_space_ids": ["ks_corrective"]},
        ),
    )

    result = KnowledgeStepExecutor().execute(
        state=state,
        step=PlanStep(
            step_id="step_durable_fail",
            goal="retrieve grounded renewal evidence",
            action_type="retrieve_evidence",
        ),
        deps=RuntimeDependencies(knowledge_runtime=runtime),
    )

    assert result.observation.status == "blocked"
    assert result.observation.failure_reason == "durable_knowledge_persistence_failed"
    assert result.observation.metadata["durable_knowledge_port"] == {
        "status": "blocked",
        "reason": "durable_persistence_failed",
        "failure_type": "RuntimeError",
    }
    assert [name for name, _ in repo.calls] == ["active_snapshot_id", "start_query_run"]


def test_knowledge_step_blocks_when_active_snapshot_is_unavailable() -> None:
    repo = _MissingSnapshotKnowledgeRepo()
    runtime = DurableKnowledgeRetrievalPort(
        runtime=_runtime(),
        unit_of_work_factory=lambda: _FakeKnowledgeUow(repo),
    )
    state = AgentRuntimeState(
        run_id="run_missing_snapshot",
        thread_id="thread_missing_snapshot",
        workspace_id="workspace_corrective",
        user_id="user_missing_snapshot",
        task_id="task_missing_snapshot",
        trace_id="trace_missing_snapshot",
        goal="renewal notice 30 days anniversary",
        context_pack=ContextPack(
            context_pack_id="context_missing_snapshot",
            user_goal="renewal notice 30 days anniversary",
            task_state={"knowledge_space_ids": ["ks_corrective"]},
        ),
    )

    result = KnowledgeStepExecutor().execute(
        state=state,
        step=PlanStep(
            step_id="step_missing_snapshot",
            goal="retrieve grounded renewal evidence",
            action_type="retrieve_evidence",
        ),
        deps=RuntimeDependencies(knowledge_runtime=runtime),
    )

    assert result.observation.status == "blocked"
    assert result.observation.failure_reason == "active_knowledge_snapshot_unavailable"
    assert result.observation.metadata["durable_knowledge_port"] == {
        "status": "blocked",
        "reason": "active_snapshot_unavailable",
    }
    assert [name for name, _ in repo.calls] == ["active_snapshot_id"]
