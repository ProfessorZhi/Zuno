from __future__ import annotations

from zuno.agent.contracts import ContextPack, PlanStep, RetrievalProfile
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution import KnowledgeStepExecutor
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.knowledge.agentic import (
    CorrectiveAction,
    CorrectiveAgenticRetrievalRuntime,
    CorrectiveRetrievalRequest,
    DurableKnowledgeRetrievalPort,
    QueryStrategy,
)
from zuno.knowledge.indexing import KnowledgeIndexRuntime
from zuno.knowledge.ingestion import CanonicalDocumentIR, DocumentBlock, DocumentMetadata, DocumentProvenance, SourceSpan


def _runtime() -> CorrectiveAgenticRetrievalRuntime:
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
    assert result.observation.evidence_ids
    assert result.observation.citation_ids


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

    def active_snapshot_id(self, *, tenant_id: str, knowledge_space_id: str) -> str | None:
        self.calls.append(("active_snapshot_id", {"tenant_id": tenant_id, "knowledge_space_id": knowledge_space_id}))
        return "knowledge-snapshot:fake"

    def start_query_run(self, **kwargs) -> None:
        self.calls.append(("start_query_run", kwargs))

    def start_retrieval_round(self, **kwargs) -> None:
        self.calls.append(("start_retrieval_round", kwargs))

    def commit_evidence(self, **kwargs) -> None:
        self.calls.append(("commit_evidence", kwargs))

    def commit_citation_lineage(self, **kwargs) -> None:
        self.calls.append(("commit_citation_lineage", kwargs))

    def mark_query_run_status(self, **kwargs) -> None:
        self.calls.append(("mark_query_run_status", kwargs))


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
        "start_retrieval_round",
        "commit_evidence",
        "commit_citation_lineage",
        "mark_query_run_status",
    ]
    evidence_call = dict(repo.calls[3][1])
    citation_call = dict(repo.calls[4][1])
    query_call = dict(repo.calls[1][1])
    assert query_call["request_payload"]["retrieval_profile"] == RetrievalProfile.STANDARD.value
    assert evidence_call["chunk_id"].endswith("block_notice::cite1")
    assert evidence_call["source_span_ref"].startswith("source-span:")
    assert citation_call["document_version_id"] == "sha256-corrective"
    assert citation_call["authorization_ref"] == "authorization:durable"
    assert result.trace["durable_knowledge_port"]["status"] == "committed"
    assert result.trace["durable_knowledge_port"]["evidence_committed"] == 1


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
