from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from zuno.agent.contracts import (
    CostMetric,
    EvidenceBundle,
    ParserDependencyProbe,
    ParseJobStatus,
    RetrievalDecision,
    RetrievalProfile,
    ScenarioSummary,
    TraceMetric,
    TraceRecord,
    TraceSummary,
)
from zuno.agent.control_runtime import AgentControlRuntime, RuntimeObservation
from zuno.agent.planning import PlanningRequest, build_default_strategy_selector
from zuno.api.services.user import UserPayload
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
from zuno.knowledge.agentic_graphrag import (
    AgenticRetrievalRuntime,
    AgenticRetrievalRuntimeRequest,
    ProductMode,
)
from zuno.knowledge.indexing import KnowledgeIndexRuntime
from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway
from zuno.knowledge.ingestion.async_runtime import (
    IndexWorker,
    IngestionReconciler,
    LocalQueueBackend,
    ParserWorker,
)
from zuno.knowledge.storage import (
    LocalObjectStore,
    ParseJobRecord,
    SQLiteDurableIngestionStore,
)
from zuno.memory.contracts import MemoryScope
from zuno.memory.engine import MemoryEngine
from zuno.memory.policy import RetentionPolicy
from zuno.schema.workspace import WorkSpaceSimpleTask, WorkspaceOutputContract


@dataclass(frozen=True, slots=True)
class WorkspaceProductE2EResult:
    scenario_summary: ScenarioSummary
    trace_summary: TraceSummary
    scenario_fixture_path: Path
    trace_fixture_path: Path


def run_workspace_product_e2e_scenario(*, output_dir: str | Path) -> WorkspaceProductE2EResult:
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    workspace_id = "workspace_phase12_product"
    trace_id = "trace_phase12_product"
    task_id = "task_phase12_product"
    user = UserPayload(
        user_id="user_phase12_product",
        user_name="PHASE12 Product User",
        role="admin",
    )
    store_path = output_root / "phase12-product.db"
    object_root = output_root / "objects"
    store = SQLiteDurableIngestionStore(store_path)
    object_store = LocalObjectStore(object_root)
    queue = LocalQueueBackend()

    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    WorkspaceTaskRuntimeService.configure_durable_ingestion(
        store=store,
        object_store=object_store,
    )
    try:
        native_status = _register_and_index_native_files(
            workspace_id=workspace_id,
            trace_id=trace_id,
            user=user,
            store=store,
            object_store=object_store,
            queue=queue,
        )
        blocked_status = _register_blocked_parser_inputs(
            workspace_id=workspace_id,
            trace_id=trace_id,
            user=user,
            store=store,
            object_store=object_store,
            queue=queue,
        )
        dead_letter_payload = _create_dead_letter_fixture(queue=queue, trace_id=trace_id)
        reconciler_findings = _create_reconciler_fixture(store=store, workspace_id=workspace_id)
        binary_source = object_store.save_bytes(
            workspace_id=workspace_id,
            source_id="source_phase12_binary",
            filename="raw-source.bin",
            mime_type="application/octet-stream",
            content=b"phase12 binary source object evidence",
            owner_id=user.user_id,
            sensitivity_tags=["internal"],
        )
        store.save_source_object(binary_source)

        task_payload = WorkSpaceSimpleTask(
            query=(
                "Compare renewal notice across contract, policy, controls, "
                "HTML notes, JSON rules, and code guard evidence."
            ),
            model_id="model-local",
            session_id="session_phase12_product",
            workspace_id=workspace_id,
            task_id=task_id,
            trace_id=trace_id,
            goal="contract renewal evidence report",
            product_mode="contract_review",
            knowledge_space_ids=["ks_phase12_standard", "ks_phase12_deep"],
            retrieval_profiles={
                "ks_phase12_standard": "standard",
                "ks_phase12_deep": "deep",
            },
            uploaded_file_ids=list(native_status),
            output_contract=WorkspaceOutputContract(
                artifact_kinds=["markdown"],
                citation_required=True,
                trace_required=True,
                format="markdown",
            ),
            plugins=[],
            mcp_servers=[],
        )
        created = WorkspaceTaskRuntimeService.create_task(
            simple_task=task_payload,
            login_user=user,
        )
        artifact_id = created["artifact_ids"][0]
        artifact = WorkspaceTaskRuntimeService.get_artifact(artifact_id)
        feedback = WorkspaceTaskRuntimeService.record_feedback(
            task_id=task_id,
            rating=5,
            label="phase12-e2e",
            comment="PHASE12 local product baseline evidence is durable.",
            dataset_candidate=True,
        )
        snapshot = WorkspaceTaskRuntimeService.get_task_snapshot(task_id)
        workspace_events = WorkspaceTaskRuntimeService.list_task_events(task_id)
        retrieval_result = WorkspaceTaskRuntimeService._task_retrieval_results[task_id]
        planner_output = WorkspaceTaskRuntimeService._planner_outputs[task_id]

        standard_result = _run_standard_retrieval_probe(
            runtime=WorkspaceTaskRuntimeService._agentic_retrieval_runtime,
            workspace_id=workspace_id,
            trace_id=trace_id,
        )
        deep_without_graph = _run_deep_without_graph_probe(workspace_id=workspace_id)
        control_replan = _run_replan_probe(planner_trace_id=trace_id)
        control_success = _run_successful_reflection_probe(planner_trace_id=trace_id)
        reflexion_candidate = _run_reflexion_probe(workspace_id=workspace_id)

        restart_result = _prove_restart_rehydrate(
            store_path=store_path,
            object_root=object_root,
            workspace_id=workspace_id,
            user=user,
            task_id=task_id,
            artifact_id=artifact_id,
            feedback_id=feedback["feedback_id"],
        )

        retrieval_decision = _retrieval_decision_from_snapshot(snapshot)
        citation_lineage = _citation_lineage(artifact["citation_refs"])
        metrics = {
            "latency_ms": 0.0,
            "cost_estimate": 0.0,
            "token_count": 0,
            "evidence_count": retrieval_decision.evidence_count,
            "citation_coverage": retrieval_decision.citation_coverage,
            "retrieval_profile_evidence": {
                "standard": standard_result.retrieval_decision.effective_profile
                is RetrievalProfile.STANDARD,
                "deep": retrieval_decision.effective_profile is RetrievalProfile.DEEP,
                "deep_without_graph": deep_without_graph.retrieval_decision.effective_profile
                is RetrievalProfile.DEEP_WITHOUT_GRAPH,
            },
            "native_formats": native_status,
            "blocked_parser_evidence": blocked_status,
            "binary_source_object": {
                "source_id": binary_source.source_id,
                "storage_uri": binary_source.storage_uri,
                "source_sha256": binary_source.source_sha256,
                "size_bytes": binary_source.size_bytes,
                "bytes_verified": object_store.verify_sha256(binary_source),
            },
            "dead_letter": dead_letter_payload,
            "reconciler_findings": reconciler_findings,
            "reflexion_candidate": {
                "lesson_id": reflexion_candidate.reflexion_lesson.lesson_id
                if reflexion_candidate.reflexion_lesson
                else None,
                "review_status": (
                    reflexion_candidate.memory_candidate.review_status.value
                    if reflexion_candidate.memory_candidate
                    else None
                ),
                "evidence_refs": (
                    list(reflexion_candidate.reflexion_lesson.evidence_refs)
                    if reflexion_candidate.reflexion_lesson
                    else []
                ),
            },
        }
        parser_probe, blocked_reason = _blocked_probe_from_status(blocked_status)
        scenario = ScenarioSummary(
            user_question=task_payload.query,
            selected_knowledge_spaces=list(task_payload.knowledge_space_ids),
            retrieval_profiles=dict(task_payload.retrieval_profiles),
            selected_skill=snapshot["capability_snapshot"]["selected_skill"],
            plan_summary=_human_plan_summary(snapshot["plan_summary"]),
            retrieval_decision=retrieval_decision,
            reflection_verdict=control_success.reflection_verdict.model_dump(mode="json"),
            replan_event={
                **control_replan.replan_decision.model_dump(mode="json"),
                "trajectory_changed": True,
            },
            artifact_content_excerpt=artifact["content"][:500],
            citations=list(artifact["citation_refs"]),
            metrics_summary=metrics,
            feedback_result={
                **feedback,
                "durable_status": "persisted",
            },
            restart_rehydrate_result=restart_result,
            file_status_timeline=_file_status_timeline(queue),
            parser_dependency_probe=parser_probe,
            blocked_reason=blocked_reason,
            worker_event={
                "parse_worker_status": "succeeded",
                "index_worker_status": "succeeded",
                "dead_letter_id": dead_letter_payload["dead_letter_id"],
                "reconciler_finding_count": len(reconciler_findings),
            },
            index_status="indexed_with_blocked_inputs_no_fake_index",
            citation_lineage=citation_lineage,
        )
        trace = TraceSummary(
            trace_id=trace_id,
            events=[
                *planner_output.trace_events,
                *_workspace_events_to_trace_records(workspace_events),
                *control_replan.trace_events,
                *control_success.trace_events,
                *reflexion_candidate.trace_events,
            ],
            metrics=[
                TraceMetric(name="citation_coverage", value=retrieval_decision.citation_coverage),
                TraceMetric(name="evidence_count", value=retrieval_decision.evidence_count),
                TraceMetric(name="latency_ms", value=0.0, unit="ms"),
                TraceMetric(name="cost_estimate", value=0.0, unit="usd"),
            ],
            cost_summary=CostMetric(
                model_id="local-runtime",
                token_count=0,
                cost_estimate=0.0,
                latency_ms=0.0,
            ),
        )
        scenario_path, trace_path = _write_fixtures(
            output_root=output_root,
            scenario=scenario,
            trace=trace,
        )
        return WorkspaceProductE2EResult(
            scenario_summary=scenario,
            trace_summary=trace,
            scenario_fixture_path=scenario_path,
            trace_fixture_path=trace_path,
        )
    finally:
        WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()


def _register_and_index_native_files(
    *,
    workspace_id: str,
    trace_id: str,
    user: UserPayload,
    store: SQLiteDurableIngestionStore,
    object_store: LocalObjectStore,
    queue: LocalQueueBackend,
) -> dict[str, str]:
    native_inputs = [
        (
            "file_phase12_text",
            "renewal-policy.txt",
            "text/plain",
            "Renewal notice requires a 45 day owner review and evidence link.",
            "ks_phase12_standard",
        ),
        (
            "file_phase12_markdown",
            "contract.md",
            "text/markdown",
            "# Contract\nRenewal notice must be issued 45 days before anniversary.",
            "ks_phase12_deep",
        ),
        (
            "file_phase12_csv",
            "controls.csv",
            "text/csv",
            "control,renewal,owner\nRC-1,45 day notice,Legal",
            "ks_phase12_standard",
        ),
        (
            "file_phase12_json",
            "rules.json",
            "application/json",
            '{"renewal_notice_days": 45, "owner": "Legal", "evidence": "required"}',
            "ks_phase12_deep",
        ),
        (
            "file_phase12_html",
            "note.html",
            "text/html",
            "<html><body><h1>Renewal</h1><p>Legal reviews renewal evidence.</p></body></html>",
            "ks_phase12_standard",
        ),
        (
            "file_phase12_code",
            "renewal_guard.py",
            "text/x-python",
            "def renewal_notice_days():\n    return 45\n",
            "ks_phase12_deep",
        ),
    ]
    statuses: dict[str, str] = {}
    for file_id, filename, mime_type, content, knowledge_space_id in native_inputs:
        registered = WorkspaceTaskRuntimeService.register_file(
            workspace_id=workspace_id,
            login_user=user,
            file_id=file_id,
            mime_type=mime_type,
            file_hash=None,
            name=filename,
            uri=None,
            trace_id=trace_id,
            security_label="internal",
            content=content,
        )
        _enqueue_parse(
            queue=queue,
            workspace_id=workspace_id,
            file_id=file_id,
            source_id=registered["source_id"],
            knowledge_space_id=knowledge_space_id,
            trace_id=trace_id,
        )
        parse_result, index_result = _run_parse_and_index_once(
            store=store,
            object_store=object_store,
            queue=queue,
        )
        if parse_result.status is not ParseJobStatus.SUCCEEDED or index_result is None:
            raise RuntimeError(f"native file did not index: {file_id}")
        statuses[mime_type] = store.get_workspace_file(file_id).parse_status
    return statuses


def _register_blocked_parser_inputs(
    *,
    workspace_id: str,
    trace_id: str,
    user: UserPayload,
    store: SQLiteDurableIngestionStore,
    object_store: LocalObjectStore,
    queue: LocalQueueBackend,
) -> dict[str, dict[str, Any]]:
    blocked_inputs = [
        ("file_phase12_pdf", "layout.pdf", "application/pdf"),
        (
            "file_phase12_docx",
            "office.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        (
            "file_phase12_pptx",
            "slides.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ),
        (
            "file_phase12_xlsx",
            "sheet.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        ("file_phase12_image", "scan.png", "image/png"),
    ]
    blocked: dict[str, dict[str, Any]] = {}
    for file_id, filename, mime_type in blocked_inputs:
        registered = WorkspaceTaskRuntimeService.register_file(
            workspace_id=workspace_id,
            login_user=user,
            file_id=file_id,
            mime_type=mime_type,
            file_hash=None,
            name=filename,
            uri=None,
            trace_id=trace_id,
            security_label="internal",
            content=f"{filename} blocked parser evidence bytes",
        )
        _enqueue_parse(
            queue=queue,
            workspace_id=workspace_id,
            file_id=file_id,
            source_id=registered["source_id"],
            knowledge_space_id="ks_phase12_blocked",
            trace_id=trace_id,
        )
        parse_result, index_result = _run_parse_and_index_once(
            store=store,
            object_store=object_store,
            queue=queue,
        )
        if parse_result.status is not ParseJobStatus.BLOCKED:
            raise RuntimeError(f"blocked file did not block: {file_id}")
        snapshot = store.get_parse_snapshot(parse_result.parse_job_id)
        blocked[mime_type] = {
            "status": store.get_workspace_file(file_id).parse_status,
            "index_job_created": index_result is not None,
            "blocked_reason": parse_result.blocked_reason,
            "parser_id": snapshot.parser_id,
            "dependency_probe": dict(snapshot.adapter_boundary),
        }
    return blocked


def _enqueue_parse(
    *,
    queue: LocalQueueBackend,
    workspace_id: str,
    file_id: str,
    source_id: str,
    knowledge_space_id: str,
    trace_id: str,
) -> None:
    queue.enqueue(
        topic="parse_requested",
        payload={
            "workspace_id": workspace_id,
            "file_id": file_id,
            "source_id": source_id,
            "knowledge_space_id": knowledge_space_id,
            "trace_id": trace_id,
        },
        idempotency_key=f"parse:{workspace_id}:{file_id}",
        trace_id=trace_id,
    )


def _run_parse_and_index_once(
    *,
    store: SQLiteDurableIngestionStore,
    object_store: LocalObjectStore,
    queue: LocalQueueBackend,
):
    parser = ParserWorker(store=store, object_store=object_store, queue=queue)
    indexer = IndexWorker(
        store=store,
        queue=queue,
        index_runtime=WorkspaceTaskRuntimeService._knowledge_index_runtime,
    )
    parse_result = parser.run_once()
    if parse_result is None:
        raise RuntimeError("parse queue had no message")
    index_result = indexer.run_once()
    return parse_result, index_result


def _create_dead_letter_fixture(*, queue: LocalQueueBackend, trace_id: str) -> dict[str, Any]:
    message = queue.enqueue(
        topic="parse_requested",
        payload={"file_id": "file_phase12_poison"},
        idempotency_key="phase12-poison",
        trace_id=trace_id,
    )
    consumed = queue.consume("parse_requested") or message
    dead_letter = queue.fail(
        consumed.message_id,
        reason="fixture_parse_poison_message",
        retryable=False,
    )
    return {
        "dead_letter_id": dead_letter.dead_letter_id,
        "source_message_id": dead_letter.source_message_id,
        "reason": dead_letter.reason,
        "status": "dead_letter",
    }


def _create_reconciler_fixture(
    *,
    store: SQLiteDurableIngestionStore,
    workspace_id: str,
) -> list[dict[str, Any]]:
    first_file = store.get_workspace_file("file_phase12_text")
    store.create_parse_job(
        ParseJobRecord(
            parse_job_id="parse_phase12_fixture_without_index",
            workspace_id=workspace_id,
            file_id=first_file.file_id,
            source_id=first_file.source_id,
            status="succeeded",
            parser_id="native",
            parser_version="phase12-fixture-v1",
            parse_idempotency_key="phase12-reconciler-fixture",
            document_version_id="doc_phase12_missing_index",
        )
    )
    return [
        finding.model_dump(mode="json")
        for finding in IngestionReconciler(store).scan()
    ]


def _run_standard_retrieval_probe(
    *,
    runtime: AgenticRetrievalRuntime,
    workspace_id: str,
    trace_id: str,
):
    return runtime.answer(
        AgenticRetrievalRuntimeRequest(
            query="What is the renewal notice period?",
            workspace_id=workspace_id,
            knowledge_space_ids=["ks_phase12_standard"],
            retrieval_profile=RetrievalProfile.STANDARD,
            product_mode=ProductMode.AUTO,
            allowed_acl_scopes={"workspace"},
            trace_id=trace_id,
            task_id="task_phase12_standard_probe",
        )
    )


def _run_deep_without_graph_probe(*, workspace_id: str):
    parse_result = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="file_phase12_no_graph",
            source_id="source_phase12_no_graph",
            workspace_id=workspace_id,
            source_uri=f"memory://workspace/{workspace_id}/files/no_graph.md",
            mime_type="text/markdown",
            source_text="Renewal conflict evidence exists without a graph index.",
        )
    )
    index_runtime = KnowledgeIndexRuntime()
    index_runtime.create_knowledge_space(
        "ks_phase12_no_graph",
        workspace_id,
        graph_project_id=None,
    )
    index_runtime.index_document(
        "ks_phase12_no_graph",
        parse_result.document,
        targets=["bm25", "vector"],
        parse_job_snapshot=ParseGateway.get_job_snapshot(parse_result.job_id),
    )
    return AgenticRetrievalRuntime(index_runtime=index_runtime).answer(
        AgenticRetrievalRuntimeRequest(
            query="Compare renewal conflict evidence without graph expansion.",
            workspace_id=workspace_id,
            knowledge_space_ids=["ks_phase12_no_graph"],
            retrieval_profile=RetrievalProfile.DEEP,
            product_mode=ProductMode.AUTO,
            allowed_acl_scopes={"workspace"},
            trace_id="trace_phase12_no_graph",
            task_id="task_phase12_no_graph_probe",
        )
    )


def _run_replan_probe(*, planner_trace_id: str):
    planner = build_default_strategy_selector().select(
        PlanningRequest(
            task_id="task_phase12_replan_probe",
            trace_id=f"{planner_trace_id}_replan",
            workspace_id="workspace_phase12_product",
            user_goal="Compare evidence across contracts and explain conflicts.",
            requested_retrieval_profile=RetrievalProfile.DEEP,
            available_capability_ids=("knowledge.contracts",),
            user_roles=("admin",),
        )
    )
    return AgentControlRuntime().run(
        planner,
        observations=[
            RuntimeObservation(
                step_id="step_1",
                status="completed",
                evidence=EvidenceBundle(evidence_count=0, citation_coverage=0.0),
                output="No matching evidence found.",
            )
        ],
    )


def _run_successful_reflection_probe(*, planner_trace_id: str):
    planner = build_default_strategy_selector().select(
        PlanningRequest(
            task_id="task_phase12_reflection_probe",
            trace_id=f"{planner_trace_id}_reflection",
            workspace_id="workspace_phase12_product",
            user_goal="Write a formal contract report with citations.",
            requested_retrieval_profile=RetrievalProfile.DEEP,
            available_capability_ids=("knowledge.contracts",),
            user_roles=("admin",),
        )
    )
    return AgentControlRuntime().run(
        planner,
        observations=[
            RuntimeObservation(
                step_id="step_2",
                status="completed",
                evidence=EvidenceBundle(
                    evidence_ids=["file_phase12_markdown::block_paragraph_2"],
                    citation_ids=["[1]"],
                    evidence_count=1,
                    citation_coverage=1.0,
                ),
                output="Renewal notice must be issued 45 days before anniversary. [1]",
            )
        ],
    )


def _run_reflexion_probe(*, workspace_id: str):
    planner = build_default_strategy_selector().select(
        PlanningRequest(
            task_id="task_phase12_reflexion_probe",
            trace_id="trace_phase12_reflexion",
            workspace_id=workspace_id,
            user_goal="Fix the failing pytest and remember the lesson for next time.",
            available_capability_ids=("tool.filesystem.read",),
            user_roles=("admin",),
        )
    )
    memory_engine = MemoryEngine()
    return AgentControlRuntime(memory_engine=memory_engine).run(
        planner,
        observations=[
            RuntimeObservation(
                step_id="step_3",
                status="failed",
                failure_reason="test_failed",
                evidence=EvidenceBundle(
                    evidence_ids=["evt_phase12_e2e_failed_then_fixed"],
                    evidence_count=1,
                ),
                output="E2E fixture assertion failed before runner existed.",
            )
        ],
        memory_scope=MemoryScope(
            user_id="user_phase12_product",
            agent_id="agent_phase12",
            project_id=workspace_id,
            thread_id="thread_phase12",
        ),
        retention_policy=RetentionPolicy(ttl_days=365),
    )


def _prove_restart_rehydrate(
    *,
    store_path: Path,
    object_root: Path,
    workspace_id: str,
    user: UserPayload,
    task_id: str,
    artifact_id: str,
    feedback_id: str,
) -> dict[str, str]:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    WorkspaceTaskRuntimeService.configure_durable_ingestion(
        store=SQLiteDurableIngestionStore(store_path),
        object_store=LocalObjectStore(object_root),
        rehydrate=True,
    )
    restored_task = WorkspaceTaskRuntimeService.get_task_snapshot(task_id)
    restored_artifact = WorkspaceTaskRuntimeService.get_artifact(artifact_id)
    cited = WorkspaceTaskRuntimeService.create_task(
        simple_task=WorkSpaceSimpleTask(
            query="What renewal evidence remains after restart?",
            model_id="model-local",
            session_id="session_phase12_restart",
            workspace_id=workspace_id,
            task_id="task_phase12_restart_cited",
            trace_id="trace_phase12_restart_cited",
            goal="restart cited answer",
            product_mode="contract_review",
            knowledge_space_ids=["ks_phase12_standard"],
            retrieval_profiles={"ks_phase12_standard": "standard"},
            uploaded_file_ids=["file_phase12_text"],
            plugins=[],
            mcp_servers=[],
        ),
        login_user=user,
    )
    return {
        "task": "available" if restored_task["task"]["task_id"] == task_id else "missing",
        "artifact": "available" if restored_artifact["content"] else "missing",
        "feedback": "available" if feedback_id in restored_task["feedback_ids"] else "missing",
        "cited_answer": "available" if cited["artifact_ids"] else "missing",
    }


def _retrieval_decision_from_snapshot(snapshot: dict[str, Any]) -> RetrievalDecision:
    plan = snapshot["retrieval_plan"]
    return RetrievalDecision(
        requested_profile=plan["requested_profile"],
        effective_profile=plan["effective_profile"],
        fallback_reason=plan.get("fallback_reason"),
        retrievers_used=list(plan.get("retrievers_used") or []),
        evidence_count=int(plan.get("evidence_count") or 0),
        citation_coverage=float(plan.get("citation_coverage") or 0.0),
        trace_id=snapshot["task"]["trace_id"],
    )


def _citation_lineage(citation_refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lineage = []
    for citation in citation_refs:
        provenance = dict(citation.get("provenance") or {})
        lineage.append(
            {
                "citation_id": citation.get("citation_id"),
                "document_id": citation.get("document_id"),
                "block_id": citation.get("block_id"),
                "parse_job_id": provenance.get("parse_job_id"),
                "parse_attempt_id": provenance.get("parse_attempt_id"),
                "source_sha256": provenance.get("source_sha256"),
                "document_version_id": provenance.get("document_version_id"),
            }
        )
    return lineage


def _blocked_probe_from_status(
    blocked_status: dict[str, dict[str, Any]],
) -> tuple[ParserDependencyProbe, str]:
    first = next(iter(blocked_status.values()))
    probe_payload = dict(first["dependency_probe"])
    blocked_reason = str(first.get("blocked_reason") or probe_payload.get("blocked_reason") or "")
    return (
        ParserDependencyProbe(
            provider_id=str(probe_payload.get("parser_id") or first.get("parser_id") or "parser"),
            capability=str(probe_payload.get("capability_status") or "parser"),
            status="target_blocked",
            blocked_reason=blocked_reason,
            diagnostics=probe_payload,
        ),
        blocked_reason,
    )


def _human_plan_summary(plan_summary: dict[str, Any]) -> str:
    steps = plan_summary.get("steps") or []
    if not steps:
        return "Plan created without executable steps."
    actions = ", ".join(str(step.get("action_type")) for step in steps)
    return f"Strategy {plan_summary.get('strategy')} will retrieve and execute steps: {actions}."


def _file_status_timeline(queue: LocalQueueBackend) -> list[str]:
    timeline: list[str] = []
    for event in queue.outbox_events():
        status = str(event.payload.get("status") or "")
        if status and status not in timeline:
            timeline.append(status)
    return timeline


def _workspace_events_to_trace_records(events: list[dict[str, Any]]) -> list[TraceRecord]:
    records = []
    for event in events:
        records.append(
            TraceRecord(
                event_id=str(event["event_id"]),
                task_id=str(event["task_id"]),
                trace_id=str(event["trace_id"]),
                event_type=str(event["type"]),
                payload=dict(event.get("payload") or {}),
            )
        )
    return records


def _write_fixtures(
    *,
    output_root: Path,
    scenario: ScenarioSummary,
    trace: TraceSummary,
) -> tuple[Path, Path]:
    scenario_path = output_root / "agentic_graphrag_product_baseline_scenario.json"
    trace_path = output_root / "agentic_graphrag_product_baseline_trace.json"
    payload = {
        "scenario_summary": scenario.model_dump(mode="json"),
        "trace_summary": trace.model_dump(mode="json"),
    }
    scenario_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    trace_path.write_text(
        json.dumps(trace.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return scenario_path, trace_path


__all__ = [
    "WorkspaceProductE2EResult",
    "run_workspace_product_e2e_scenario",
]
