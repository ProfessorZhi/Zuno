from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import time
from typing import Any
from urllib.parse import unquote, urlparse
from uuid import uuid4

from fastapi import HTTPException

from zuno.agent.contracts import PlannerOutput, RetrievalProfile
from zuno.agent.durable_runtime import InMemoryDurableRuntimeStore, SingleControllerDurableRuntime
from zuno.agent.harness import ControllerRuntimeState
from zuno.agent.planning import PlanningRequest, build_default_strategy_selector
from zuno.api.services.user import UserPayload
from zuno.capability.runtime import (
    ToolRuntimeExecutionResult,
    ToolRuntimeRequest,
    build_default_tool_control_plane_runtime,
)
from zuno.knowledge.agentic_graphrag import (
    AgenticRetrievalRuntime,
    AgenticRetrievalRuntimeRequest,
    AgenticRetrievalRuntimeResult,
    ProductMode,
)
from zuno.knowledge.indexing import IndexJobManifest, KnowledgeIndexRuntime
from zuno.knowledge.ingestion import (
    CanonicalDocumentIR,
    DocumentBlock,
    DocumentMetadata,
    DocumentProvenance,
    ParseDocumentRequest,
    ParseDocumentResult,
    ParseGateway,
    ParseJobSnapshot,
    SourceSpan,
)
from zuno.knowledge.storage import (
    ArtifactRecord,
    DocumentVersionRecord,
    FeedbackRecord,
    IndexChunkRecord,
    LocalObjectStore,
    ParseJobRecord,
    SQLiteDurableIngestionStore,
    SourceObjectRecord,
    TaskEventRecord,
    WorkspaceFileRecord,
    WorkspaceTaskRecord,
)
from zuno.platform.observability import (
    EvalMetricResult,
    MetricThreshold,
    ReleaseEvalBaseline,
    ZunoSpanBuilder,
    ZunoSpanKind,
)
from zuno.platform.security import (
    GateRequest,
    GateResult,
    InputSecurityGate,
    OutputSecurityGate,
    RetrievalCandidate,
    RetrievalGateResult,
    RetrievalSecurityGate,
    SandboxAuditEvent,
    SecurityDecision,
    SecurityGate,
)
from zuno.schema.workspace import (
    ArtifactContract,
    FeedbackContract,
    TraceEventContract,
    UploadedFileContract,
    WorkSpaceSimpleTask,
    WORKSPACE_TASK_LIFECYCLE_FLOW,
    WORKSPACE_TASK_RECOVERY_ACTIONS,
    WORKSPACE_TASK_STATUS_TO_LIFECYCLE,
    WorkspaceTaskBudget,
    WorkspaceTaskContract,
    WorkspaceFileStatus,
    WorkspaceTaskLifecycleSnapshot,
)


class WorkspaceTaskRuntimeService:
    """In-process PHASE03 task runtime surface.

    This is the first API/runtime bridge for task, event, artifact, and feedback
    IDs. Durability moves to later runtime/storage phases.
    """

    _tasks: dict[str, WorkspaceTaskContract] = {}
    _task_inputs: dict[str, WorkSpaceSimpleTask] = {}
    _events: dict[str, list[TraceEventContract]] = {}
    _files: dict[str, UploadedFileContract] = {}
    _file_text: dict[str, str] = {}
    _ingest_jobs: dict[str, dict] = {}
    _artifacts: dict[str, ArtifactContract] = {}
    _artifact_content: dict[str, str] = {}
    _artifact_ids_by_task: dict[str, list[str]] = {}
    _feedback: dict[str, FeedbackContract] = {}
    _feedback_ids_by_task: dict[str, list[str]] = {}
    _task_recovery: dict[str, dict] = {}
    _planner_outputs: dict[str, PlannerOutput] = {}
    _task_retrieval_results: dict[str, AgenticRetrievalRuntimeResult] = {}
    _artifact_citation_refs: dict[str, list[dict[str, Any]]] = {}
    _durable_runtime = SingleControllerDurableRuntime(store=InMemoryDurableRuntimeStore())
    _tool_runtime = build_default_tool_control_plane_runtime()
    _knowledge_index_runtime = KnowledgeIndexRuntime()
    _agentic_retrieval_runtime = AgenticRetrievalRuntime(index_runtime=_knowledge_index_runtime)
    _durable_ingestion_store: SQLiteDurableIngestionStore | None = None
    _source_object_store: LocalObjectStore | None = None
    _pending_tool_requests: dict[str, ToolRuntimeRequest] = {}
    _input_security_gate = InputSecurityGate()
    _retrieval_security_gate = RetrievalSecurityGate()
    _output_security_gate = OutputSecurityGate()
    _span_builder = ZunoSpanBuilder()
    _trace_spans: dict[str, list[dict]] = {}
    _release_evals: dict[str, dict] = {}
    _trace_replays: dict[str, dict] = {}

    @classmethod
    def configure_durable_ingestion(
        cls,
        *,
        store: SQLiteDurableIngestionStore | None,
        object_store: LocalObjectStore | None,
        rehydrate: bool = False,
    ) -> None:
        cls._durable_ingestion_store = store
        cls._source_object_store = object_store
        if rehydrate and store is not None:
            cls._rehydrate_from_durable_store()

    @classmethod
    def reset_runtime_state_for_tests(cls) -> None:
        cls._tasks = {}
        cls._task_inputs = {}
        cls._events = {}
        cls._files = {}
        cls._file_text = {}
        cls._ingest_jobs = {}
        cls._artifacts = {}
        cls._artifact_content = {}
        cls._artifact_ids_by_task = {}
        cls._feedback = {}
        cls._feedback_ids_by_task = {}
        cls._task_recovery = {}
        cls._planner_outputs = {}
        cls._task_retrieval_results = {}
        cls._artifact_citation_refs = {}
        cls._durable_runtime = SingleControllerDurableRuntime(store=InMemoryDurableRuntimeStore())
        cls._tool_runtime = build_default_tool_control_plane_runtime()
        cls._knowledge_index_runtime = KnowledgeIndexRuntime()
        cls._agentic_retrieval_runtime = AgenticRetrievalRuntime(index_runtime=cls._knowledge_index_runtime)
        cls._pending_tool_requests = {}
        cls._trace_spans = {}
        cls._release_evals = {}
        cls._trace_replays = {}
        cls._durable_ingestion_store = None
        cls._source_object_store = None

    @classmethod
    def _rehydrate_from_durable_store(cls) -> None:
        if cls._durable_ingestion_store is None:
            return
        for durable_file in cls._durable_ingestion_store.list_workspace_files():
            cls._files[durable_file.file_id] = UploadedFileContract(
                workspace_id=durable_file.workspace_id,
                owner=durable_file.owner_id,
                status="ready",
                file_id=durable_file.file_id,
                mime_type=durable_file.mime_type,
                hash=durable_file.source_sha256,
                security_label=durable_file.security_label,
                parse_status=durable_file.parse_status,
            )
            try:
                source_object = cls._durable_ingestion_store.get_source_object(durable_file.source_id)
                cls._file_text[durable_file.file_id] = cls._read_source_text(source_object)
            except KeyError:
                cls._file_text[durable_file.file_id] = ""
        for manifest in cls._durable_ingestion_store.list_index_manifests():
            cls._knowledge_index_runtime.rehydrate_index(
                manifest,
                cls._durable_ingestion_store.list_index_chunks(manifest.job_id),
            )
        for task_record in cls._durable_ingestion_store.list_workspace_tasks():
            task_payload = task_record.payload.get("task", task_record.payload)
            task = WorkspaceTaskContract.model_validate(task_payload)
            cls._tasks[task.task_id] = task
            cls._artifact_ids_by_task[task.task_id] = []
            cls._feedback_ids_by_task[task.task_id] = []
            cls._events[task.task_id] = [
                TraceEventContract(
                    event_id=event.event_id,
                    task_id=event.task_id,
                    trace_id=event.trace_id,
                    type=event.event_type,
                    timestamp=event.timestamp,
                    payload=event.payload,
                )
                for event in cls._durable_ingestion_store.list_task_events(task.task_id)
            ]
            for artifact_record in cls._durable_ingestion_store.list_artifacts_for_task(task.task_id):
                artifact_payload = artifact_record.payload.get("artifact", artifact_record.payload)
                artifact = ArtifactContract.model_validate(artifact_payload)
                cls._artifacts[artifact.artifact_id] = artifact
                cls._artifact_content[artifact.artifact_id] = artifact_record.content
                cls._artifact_ids_by_task.setdefault(task.task_id, []).append(artifact.artifact_id)
            for feedback_record in cls._durable_ingestion_store.list_feedback_for_task(task.task_id):
                feedback_payload = feedback_record.payload.get("feedback", feedback_record.payload)
                feedback = FeedbackContract.model_validate(feedback_payload)
                cls._feedback[feedback.feedback_id] = feedback
                cls._feedback_ids_by_task.setdefault(task.task_id, []).append(feedback.feedback_id)
            cls._trace_spans.setdefault(task.task_id, [])
            cls._trace_replays.setdefault(task.task_id, {"source_refs": []})

    @staticmethod
    def _read_source_text(source_object: SourceObjectRecord) -> str:
        parsed = urlparse(source_object.storage_uri)
        if parsed.scheme != "file":
            return ""
        path_text = unquote(parsed.path)
        if path_text.startswith("/") and len(path_text) > 3 and path_text[2] == ":":
            path_text = path_text[1:]
        path = Path(path_text)
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")

    @classmethod
    def register_file(
        cls,
        *,
        workspace_id: str,
        login_user: UserPayload,
        file_id: str | None,
        mime_type: str,
        file_hash: str | None,
        name: str | None,
        uri: str | None,
        trace_id: str | None,
        security_label: str,
        content: str | None = None,
    ) -> dict:
        normalized_file_id = file_id or f"file_{uuid4().hex[:12]}"
        stored_content = content or f"{name or normalized_file_id} was uploaded to workspace {workspace_id}."
        normalized_hash = file_hash or hashlib.sha256(
            stored_content.encode("utf-8")
        ).hexdigest()
        file = UploadedFileContract(
            workspace_id=workspace_id,
            owner=login_user.user_id,
            status="ready",
            trace_id=trace_id or f"trace_{uuid4().hex[:12]}",
            file_id=normalized_file_id,
            mime_type=mime_type,
            hash=normalized_hash,
            security_label=security_label,
            parse_status="uploaded",
            created_at=str(time.time()),
            updated_at=str(time.time()),
        )
        cls._files[file.file_id] = file
        cls._file_text[file.file_id] = stored_content
        payload = {
            "file": file.model_dump(),
            "name": name,
            "uri": uri,
            "file_status": cls._file_status_payload(
                file=file,
                filename=name,
                storage_uri=uri,
                source_ref=uri or file.file_id,
            ),
        }
        if cls._durable_ingestion_store is not None and cls._source_object_store is not None:
            source_id = f"source_{normalized_file_id}"
            source_object = cls._source_object_store.save_text(
                workspace_id=workspace_id,
                source_id=source_id,
                filename=name or f"{normalized_file_id}.txt",
                mime_type=mime_type,
                content=stored_content,
                owner_id=login_user.user_id,
                acl_scope=file.policy_scope,
                sensitivity_tags=[security_label],
            )
            cls._durable_ingestion_store.save_source_object(source_object)
            cls._durable_ingestion_store.save_workspace_file(
                WorkspaceFileRecord(
                    file_id=file.file_id,
                    workspace_id=workspace_id,
                    source_id=source_id,
                    owner_id=login_user.user_id,
                    filename=name or normalized_file_id,
                    mime_type=mime_type,
                    source_sha256=source_object.source_sha256,
                    parse_status=file.parse_status,
                    security_label=security_label,
                )
            )
            payload.update(
                {
                    "source_id": source_id,
                    "source_sha256": source_object.source_sha256,
                    "storage_uri": source_object.storage_uri,
                    "durable_status": "persisted",
                }
            )
            payload["file_status"] = cls._file_status_payload(
                file=file,
                filename=source_object.filename,
                storage_uri=source_object.storage_uri,
                source_ref=source_object.source_id,
                source_sha256=source_object.source_sha256,
                size_bytes=source_object.size_bytes,
            )
        return payload

    @classmethod
    def create_ingest_job(
        cls,
        *,
        workspace_id: str,
        file_id: str,
        knowledge_space_id: str,
        session_id: str | None,
        trace_id: str | None,
    ) -> dict:
        file = cls._require_file(file_id)
        if file.workspace_id != workspace_id:
            raise HTTPException(status_code=400, detail="Workspace file does not belong to workspace")
        durable_file, source_object = cls._durable_file_source(file_id)
        file.parse_status = "ingest_accepted"
        file.updated_at = str(time.time())
        normalized_trace_id = trace_id or file.trace_id or f"trace_{uuid4().hex[:12]}"
        file.trace_id = normalized_trace_id
        ingest_task_id = f"ingest_{uuid4().hex[:12]}"
        cls._ensure_knowledge_space(
            knowledge_space_id=knowledge_space_id,
            workspace_id=workspace_id,
        )
        parse_job = ParseGateway.submit_parse_job(
            ParseDocumentRequest(
                document_id=file.file_id,
                source_id=source_object.source_id if source_object is not None else file.file_id,
                workspace_id=workspace_id,
                source_uri=source_object.storage_uri if source_object is not None else cls._parser_source_uri(file=file),
                mime_type=file.mime_type,
                source_text=cls._file_text.get(file_id, ""),
                hash=source_object.source_sha256 if source_object is not None else file.hash,
                acl_scope="workspace",
                sensitivity_tags=[file.security_label],
            )
        )
        parse_snapshot = ParseGateway.get_job_snapshot(parse_job.job_id)
        cls._persist_parse_job(
            file=file,
            durable_file=durable_file,
            source_object=source_object,
            parse_job=parse_job,
            parse_snapshot=parse_snapshot,
        )
        if parse_job.status != "succeeded" or parse_job.document is None:
            file.parse_status = parse_job.status
            file.updated_at = str(time.time())
            cls._persist_workspace_file_status(
                durable_file=durable_file,
                parse_status=file.parse_status,
                latest_parse_job_id=parse_job.job_id,
                latest_document_version_id=None,
            )
            job = {
                "ingest_task_id": ingest_task_id,
                "workspace_id": workspace_id,
                "file_id": file_id,
                "knowledge_space_id": knowledge_space_id,
                "session_id": session_id,
                "trace_id": normalized_trace_id,
                "status": parse_job.status,
                "file": file.model_dump(),
                "parse_job": parse_job.model_dump(),
                "parse_snapshot": parse_snapshot.model_dump(),
                "index_job": None,
            }
            job["file_status"] = cls._file_status_payload(
                file=file,
                filename=source_object.filename if source_object is not None else None,
                storage_uri=source_object.storage_uri if source_object is not None else None,
                source_ref=source_object.source_id if source_object is not None else file.file_id,
                source_sha256=source_object.source_sha256 if source_object is not None else file.hash,
                size_bytes=source_object.size_bytes if source_object is not None else 0,
                parse_snapshot=parse_snapshot,
                index_status="blocked",
            )
            cls._attach_blocked_durable_payload(
                job=job,
                source_object=source_object,
            )
            cls._ingest_jobs[ingest_task_id] = job
            return job
        index_job = cls._knowledge_index_runtime.index_document(
            knowledge_space_id,
            parse_job.document,
            targets=["bm25", "vector", "graph"],
            parse_job_snapshot=parse_snapshot,
        )
        file.parse_status = "indexed"
        file.updated_at = str(time.time())
        document_version = cls._persist_successful_ingest(
            file=file,
            durable_file=durable_file,
            source_object=source_object,
            parse_job=parse_job,
            parse_snapshot=parse_snapshot,
            index_job=index_job,
            knowledge_space_id=knowledge_space_id,
        )
        job = {
            "ingest_task_id": ingest_task_id,
            "workspace_id": workspace_id,
            "file_id": file_id,
            "knowledge_space_id": knowledge_space_id,
            "session_id": session_id,
            "trace_id": normalized_trace_id,
            "status": "accepted",
            "file": file.model_dump(),
            "parse_job": parse_job.model_dump(),
            "parse_snapshot": parse_snapshot.model_dump(),
            "index_job": index_job.model_dump(),
        }
        job["file_status"] = cls._file_status_payload(
            file=file,
            filename=source_object.filename if source_object is not None else None,
            storage_uri=source_object.storage_uri if source_object is not None else None,
            source_ref=source_object.source_id if source_object is not None else file.file_id,
            source_sha256=source_object.source_sha256 if source_object is not None else file.hash,
            size_bytes=source_object.size_bytes if source_object is not None else 0,
            parse_snapshot=parse_snapshot,
            document_version=document_version,
            index_job=index_job,
            index_status="indexed",
        )
        cls._attach_success_durable_payload(
            job=job,
            source_object=source_object,
            document_version=document_version,
            index_job=index_job,
        )
        cls._ingest_jobs[ingest_task_id] = job
        return job

    @classmethod
    def _durable_file_source(
        cls,
        file_id: str,
    ) -> tuple[WorkspaceFileRecord | None, SourceObjectRecord | None]:
        if cls._durable_ingestion_store is None:
            return None, None
        try:
            durable_file = cls._durable_ingestion_store.get_workspace_file(file_id)
            source_object = cls._durable_ingestion_store.get_source_object(durable_file.source_id)
        except KeyError:
            return None, None
        return durable_file, source_object

    @classmethod
    def _persist_parse_job(
        cls,
        *,
        file: UploadedFileContract,
        durable_file: WorkspaceFileRecord | None,
        source_object: SourceObjectRecord | None,
        parse_job: ParseDocumentResult,
        parse_snapshot: ParseJobSnapshot,
    ) -> None:
        if cls._durable_ingestion_store is None or source_object is None:
            return
        parser_version = (
            parse_job.document.metadata.parser_version
            if parse_job.document is not None
            else "phase05-runtime-v1"
        )
        cls._durable_ingestion_store.create_parse_job(
            ParseJobRecord(
                parse_job_id=parse_job.job_id,
                workspace_id=file.workspace_id,
                file_id=file.file_id,
                source_id=source_object.source_id,
                status=parse_job.status,
                parser_id=parse_snapshot.parser_id,
                parser_version=parser_version,
                parse_idempotency_key=parse_snapshot.parse_idempotency_key,
                attempt_count=parse_snapshot.attempt_count,
                document_version_id=parse_snapshot.source_provenance.get("document_version_id"),
                blocked_reason=parse_snapshot.blocked_reason,
                failure_reason=parse_snapshot.failure_reason,
            )
        )
        cls._durable_ingestion_store.save_parse_snapshot(parse_snapshot)
        cls._persist_workspace_file_status(
            durable_file=durable_file,
            parse_status=parse_job.status,
            latest_parse_job_id=parse_job.job_id,
            latest_document_version_id=parse_snapshot.source_provenance.get("document_version_id"),
        )

    @classmethod
    def _persist_successful_ingest(
        cls,
        *,
        file: UploadedFileContract,
        durable_file: WorkspaceFileRecord | None,
        source_object: SourceObjectRecord | None,
        parse_job: ParseDocumentResult,
        parse_snapshot: ParseJobSnapshot,
        index_job: IndexJobManifest,
        knowledge_space_id: str,
    ) -> DocumentVersionRecord | None:
        if (
            cls._durable_ingestion_store is None
            or source_object is None
            or parse_job.document is None
        ):
            return None
        document_version = cls._durable_ingestion_store.save_document_version(parse_job.document)
        cls._durable_ingestion_store.save_index_manifest(index_job)
        for chunk in cls._index_chunks_for_manifest(
            index_job=index_job,
            knowledge_space_id=knowledge_space_id,
            query=cls._file_text.get(file.file_id, ""),
        ):
            cls._durable_ingestion_store.save_index_chunk(chunk)
        cls._persist_workspace_file_status(
            durable_file=durable_file,
            parse_status="indexed",
            latest_parse_job_id=parse_snapshot.job_id,
            latest_document_version_id=document_version.document_version_id,
        )
        return document_version

    @classmethod
    def _persist_workspace_file_status(
        cls,
        *,
        durable_file: WorkspaceFileRecord | None,
        parse_status: str,
        latest_parse_job_id: str | None,
        latest_document_version_id: str | None,
    ) -> None:
        if cls._durable_ingestion_store is None or durable_file is None:
            return
        cls._durable_ingestion_store.save_workspace_file(
            durable_file.model_copy(
                update={
                    "parse_status": parse_status,
                    "latest_parse_job_id": latest_parse_job_id,
                    "latest_document_version_id": latest_document_version_id,
                }
            )
        )

    @classmethod
    def _index_chunks_for_manifest(
        cls,
        *,
        index_job: IndexJobManifest,
        knowledge_space_id: str,
        query: str,
    ) -> list[IndexChunkRecord]:
        payload = cls._knowledge_index_runtime.to_retrieval_payload(knowledge_space_id, query or "__all__")
        chunks: list[IndexChunkRecord] = []
        seen_chunk_ids: set[str] = set()
        for source_name in ("bm25", "vector", "graph"):
            for document in payload.get("documents_by_source", {}).get(source_name, []):
                chunk_id = str(document.get("chunk_id") or "")
                if not chunk_id or chunk_id in seen_chunk_ids:
                    continue
                seen_chunk_ids.add(chunk_id)
                metadata = dict(document.get("metadata") or {})
                chunks.append(
                    IndexChunkRecord(
                        chunk_id=chunk_id,
                        index_job_id=index_job.job_id,
                        knowledge_space_id=index_job.knowledge_space_id,
                        workspace_id=index_job.workspace_id,
                        document_id=str(document.get("document_id") or index_job.document_id),
                        document_version_id=index_job.document_version_id,
                        block_id=str(metadata.get("block_id") or chunk_id.split("::", 1)[-1]),
                        content=str(document.get("content") or ""),
                        source_type=str(document.get("source_type") or source_name),
                        metadata=metadata,
                        citation_lineage=dict(metadata.get("citation_lineage") or {}),
                        acl_scope=str(metadata.get("acl_scope") or "workspace"),
                        sensitivity_tags=list(metadata.get("sensitivity_tags") or index_job.sensitivity_tags),
                    )
                )
        return chunks

    @staticmethod
    def _attach_blocked_durable_payload(
        *,
        job: dict,
        source_object: SourceObjectRecord | None,
    ) -> None:
        if source_object is None:
            return
        job.update(
            {
                "source_object": source_object.model_dump(),
                "durable_status": "persisted",
            }
        )

    @staticmethod
    def _attach_success_durable_payload(
        *,
        job: dict,
        source_object: SourceObjectRecord | None,
        document_version: DocumentVersionRecord | None,
        index_job: IndexJobManifest,
    ) -> None:
        if source_object is None or document_version is None:
            return
        job.update(
            {
                "source_object": source_object.model_dump(),
                "document_version": document_version.model_dump(exclude={"ir_json"}),
                "index_manifest_ref": {
                    "index_job_id": index_job.job_id,
                    "knowledge_space_id": index_job.knowledge_space_id,
                    "document_version_id": index_job.document_version_id,
                    "source_sha256": index_job.source_sha256,
                },
                "durable_status": "persisted",
            }
        )

    @classmethod
    def create_task(
        cls,
        *,
        simple_task: WorkSpaceSimpleTask,
        login_user: UserPayload,
    ) -> dict:
        workspace_id = simple_task.workspace_id or "workspace_default"
        task_id = simple_task.task_id or f"task_{uuid4().hex[:12]}"
        trace_id = simple_task.trace_id or f"trace_{uuid4().hex[:12]}"
        goal = simple_task.goal or simple_task.query
        artifact_kind = (
            simple_task.output_contract.artifact_kinds[0]
            if simple_task.output_contract and simple_task.output_contract.artifact_kinds
            else "markdown"
        )
        manual_approval_required = simple_task.approval_mode not in {"", "auto", "none"}

        task = WorkspaceTaskContract(
            workspace_id=workspace_id,
            owner=login_user.user_id,
            status="approval_waiting" if manual_approval_required else "running",
            trace_id=trace_id,
            task_id=task_id,
            session_id=simple_task.session_id,
            goal=goal,
            product_mode=simple_task.product_mode,
            budget=simple_task.budget or WorkspaceTaskBudget(),
            created_at=str(time.time()),
            updated_at=str(time.time()),
        )
        cls._tasks[task_id] = task
        cls._task_inputs[task_id] = simple_task
        cls._artifact_ids_by_task[task_id] = []
        cls._feedback_ids_by_task[task_id] = []
        cls._task_recovery.pop(task_id, None)
        planner_output = cls._build_planner_output(
            task=task,
            simple_task=simple_task,
            login_user=login_user,
        )
        cls._planner_outputs[task_id] = planner_output
        cls._task_retrieval_results.pop(task_id, None)
        cls._trace_spans[task_id] = []
        cls._release_evals.pop(task_id, None)
        cls._trace_replays[task_id] = {"source_refs": []}
        runtime_state = cls._runtime_state_for_task(
            simple_task=simple_task,
            login_user=login_user,
            task_id=task_id,
            trace_id=trace_id,
            workspace_id=workspace_id,
            goal=goal,
        )
        cls._events[task_id] = [
            cls._event(task_id=task_id, trace_id=trace_id, event_type="task_started", status="created", payload={"session_id": task.session_id}),
            cls._event(
                task_id=task_id,
                trace_id=trace_id,
                event_type="planning",
                status="planning",
                payload={
                    "goal": goal,
                    "strategy": planner_output.strategy.strategy,
                    "selected_skill": planner_output.strategy.selected_skill,
                    "retrieval_plan": planner_output.retrieval_plan.model_dump(mode="json"),
                },
            ),
            cls._event(
                task_id=task_id,
                trace_id=trace_id,
                event_type="retrieval",
                status="running",
                payload={
                    "knowledge_space_ids": list(simple_task.knowledge_space_ids),
                    "uploaded_file_ids": list(simple_task.uploaded_file_ids),
                    "uploaded_files": cls._uploaded_file_payloads(simple_task.uploaded_file_ids),
                    "retrieval_mode": simple_task.retrieval_mode,
                    "retrieval_profiles": cls._retrieval_profile_map(simple_task),
                },
            ),
        ]
        input_gate = cls._input_security_gate.evaluate(
            GateRequest(
                gate=SecurityGate.INPUT,
                workspace_id=workspace_id,
                user_id=login_user.user_id,
                content=simple_task.query,
                metadata={"source": "workspace_task"},
                trace_id=trace_id,
                task_id=task_id,
            )
        )
        cls._record_security_span(task_id=task_id, audit=input_gate.audit_event)
        if input_gate.decision is SecurityDecision.BLOCK:
            cls._append_security_gate_event(task_id=task_id, result=input_gate)
            cls._fail_task(
                task_id=task_id,
                simple_task=simple_task,
                reason="input_security_block",
                citation_coverage=1.0,
                required_citation_coverage=0.0,
                security_block_count=1,
                failure_examples=[
                    {
                        "gate": "input",
                        "findings": [finding.to_dict() for finding in input_gate.findings],
                        "sanitized_content": input_gate.sanitized_content,
                    }
                ],
            )
            return cls.get_task_snapshot(task_id)

        if manual_approval_required:
            cls._durable_runtime.start_task(
                runtime_state,
                interrupt_at_node="act_react_loop",
                required_approval=simple_task.approval_mode,
                interrupt_payload={
                    "approval_mode": simple_task.approval_mode,
                    "plugins": list(simple_task.plugins),
                    "mcp_servers": list(simple_task.mcp_servers),
                },
            )
            cls._events[task_id].append(
                cls._event(
                    task_id=task_id,
                    trace_id=trace_id,
                    event_type="approval_required",
                    status="approval_waiting",
                    payload={
                        "approval_mode": simple_task.approval_mode,
                        "plugins": list(simple_task.plugins),
                        "mcp_servers": list(simple_task.mcp_servers),
                    },
                )
            )
            return cls.get_task_snapshot(task_id)

        pending_tool_result = cls._run_workspace_tools_until_interrupt(
            task_id=task_id,
            simple_task=simple_task,
            login_user=login_user,
            runtime_state=runtime_state,
        )
        if pending_tool_result is not None:
            cls._durable_runtime.start_task(
                runtime_state,
                interrupt_at_node="act_react_loop",
                required_approval=f"tool:{pending_tool_result.tool_id}",
                interrupt_payload={
                    "tool_id": pending_tool_result.tool_id,
                    "approval_decision": pending_tool_result.approval_decision,
                    "audit_ref": pending_tool_result.audit_event.audit_id,
                },
            )
            task.status = "approval_waiting"
            task.updated_at = str(time.time())
            return cls.get_task_snapshot(task_id)

        cls._durable_runtime.start_task(runtime_state)
        cls._complete_task(
            task_id=task_id,
            simple_task=simple_task,
            artifact_kind=artifact_kind,
        )
        return cls.get_task_snapshot(task_id)

    @classmethod
    def approve_task(cls, *, task_id: str, decision: str, comment: str | None) -> dict:
        task = cls._require_task(task_id)
        normalized_decision = decision.strip().lower()
        if normalized_decision not in {"approved", "rejected"}:
            raise HTTPException(status_code=400, detail="Approval decision must be approved or rejected")
        if task.status != "approval_waiting":
            raise HTTPException(status_code=409, detail="Workspace task is not waiting for approval")

        cls._events.setdefault(task_id, []).append(
            cls._event(
                task_id=task_id,
                trace_id=task.trace_id or "",
                event_type="approval_decision",
                status="resuming" if normalized_decision == "approved" else "failed",
                payload={"decision": normalized_decision, "comment": comment},
            )
        )

        pending_tool_request = cls._pending_tool_requests.pop(task_id, None)

        if normalized_decision == "rejected":
            cls._durable_runtime.resume_task(
                task_id=task_id,
                approval_decision="rejected",
                comment=comment,
            )
            task.status = "failed"
            task.updated_at = str(time.time())
            cls._events[task_id].append(
                cls._event(
                    task_id=task_id,
                    trace_id=task.trace_id or "",
                    event_type="failure",
                    status="failed",
                    payload={"error": comment or "Approval rejected."},
                )
            )
            return cls.get_task_snapshot(task_id)

        cls._durable_runtime.resume_task(
            task_id=task_id,
            approval_decision="approved",
            comment=comment,
        )
        simple_task = cls._task_inputs[task_id]
        task.status = "completed"
        task.updated_at = str(time.time())
        cls._events[task_id].append(
            cls._event(
                task_id=task_id,
                trace_id=task.trace_id or "",
                event_type="resuming",
                status="resuming",
                payload={"approval": "approved"},
            )
        )
        if pending_tool_request is not None:
            approved_tool = cls._tool_runtime.execute(
                replace(
                    pending_tool_request,
                    approved=True,
                    approval_comment=comment or "",
                )
            )
            cls._append_tool_runtime_events(task_id=task_id, result=approved_tool)
        artifact_kind = (
            simple_task.output_contract.artifact_kinds[0]
            if simple_task.output_contract and simple_task.output_contract.artifact_kinds
            else "markdown"
        )
        cls._complete_task(
            task_id=task_id,
            simple_task=simple_task,
            artifact_kind=artifact_kind,
        )
        return cls.get_task_snapshot(task_id)

    @classmethod
    def cancel_task(cls, *, task_id: str, reason: str | None) -> dict:
        task = cls._require_task(task_id)
        if task.status in {"completed", "failed", "cancelled"}:
            raise HTTPException(status_code=409, detail="Workspace task cannot be cancelled")
        normalized_reason = reason or "cancelled"
        try:
            cls._durable_runtime.cancel_task(task_id, reason=normalized_reason)
        except ValueError as err:
            raise HTTPException(status_code=409, detail=str(err))
        task.status = "cancelled"
        task.updated_at = str(time.time())
        cls._events.setdefault(task_id, []).append(
            cls._event(
                task_id=task_id,
                trace_id=task.trace_id or "",
                event_type="task_cancelled",
                status="cancelled",
                payload={"reason": normalized_reason, "lifecycle_state": "cancelled"},
            )
        )
        return cls.get_task_snapshot(task_id)

    @classmethod
    def task_lifecycle_contract(cls) -> dict:
        return {
            "states": list(WORKSPACE_TASK_LIFECYCLE_FLOW),
            "terminal_states": ["recoverable_failed", "cancelled", "completed"],
            "status_mapping": dict(WORKSPACE_TASK_STATUS_TO_LIFECYCLE),
            "recovery_actions": {
                state: list(actions)
                for state, actions in WORKSPACE_TASK_RECOVERY_ACTIONS.items()
            },
        }

    @classmethod
    def _complete_task(
        cls,
        *,
        task_id: str,
        simple_task: WorkSpaceSimpleTask,
        artifact_kind: str,
    ) -> None:
        task = cls._require_task(task_id)
        trace_id = task.trace_id or ""
        goal = task.goal
        retrieval_gate = cls._preflight_retrieval_security(
            task=task,
            simple_task=simple_task,
        )
        if retrieval_gate is not None:
            cls._record_security_span(task_id=task_id, audit=retrieval_gate.audit_event)
            if retrieval_gate.findings:
                cls._append_security_gate_event(task_id=task_id, result=retrieval_gate)
            if retrieval_gate.decision is SecurityDecision.BLOCK:
                cls._fail_task(
                    task_id=task_id,
                    simple_task=simple_task,
                    reason="retrieval_security_block",
                    citation_coverage=0.0,
                    required_citation_coverage=0.8,
                    security_block_count=1,
                    failure_examples=[
                        {
                            "gate": "retrieval",
                            "findings": [finding.to_dict() for finding in retrieval_gate.findings],
                        }
                    ],
                )
                return

        retrieval_result = cls._answer_from_index(
            task=task,
            simple_task=simple_task,
            goal=goal,
        )
        if retrieval_result is not None:
            cls._task_retrieval_results[task_id] = retrieval_result
            cls._events.setdefault(task_id, []).append(
                cls._event(
                    task_id=task_id,
                    trace_id=trace_id,
                    event_type="retrieval",
                    status="completed",
                    payload=retrieval_result.to_task_event()["payload"],
                )
            )
            cls._record_retrieval_observability(
                task=task,
                simple_task=simple_task,
                retrieval_result=retrieval_result,
            )
        artifact_content = cls._render_artifact_content(
            simple_task=simple_task,
            goal=goal,
            retrieval_result=retrieval_result,
        )
        citation_coverage = (
            retrieval_result.trace.citation_coverage
            if retrieval_result is not None
            else 1.0
        )
        required_citation_coverage = (
            0.8
            if retrieval_result is not None
            and (
                simple_task.output_contract.citation_required
                if simple_task.output_contract
                else True
            )
            else 0.0
        )
        output_gate = cls._output_security_gate.evaluate(
            content=artifact_content,
            citation_coverage=citation_coverage,
            required_citation_coverage=required_citation_coverage,
            workspace_id=task.workspace_id,
            trace_id=trace_id,
            task_id=task_id,
        )
        cls._record_security_span(task_id=task_id, audit=output_gate.audit_event)
        if output_gate.findings:
            cls._append_security_gate_event(task_id=task_id, result=output_gate)
        if output_gate.decision is SecurityDecision.BLOCK:
            cls._fail_task(
                task_id=task_id,
                simple_task=simple_task,
                reason="output_security_block",
                citation_coverage=citation_coverage,
                required_citation_coverage=required_citation_coverage,
                security_block_count=1,
                source_refs=cls._trace_replays.get(task_id, {}).get("source_refs", []),
                recoverable=True,
                failure_examples=[
                    {
                        "gate": "output",
                        "findings": [finding.to_dict() for finding in output_gate.findings],
                        "sanitized_content": output_gate.sanitized_content,
                    }
                ],
            )
            return

        citation_refs = cls._citation_refs_from_result(retrieval_result)
        artifact = ArtifactContract(
            workspace_id=task.workspace_id,
            owner=task.owner,
            status="ready",
            trace_id=trace_id,
            artifact_id=f"artifact_{uuid4().hex[:12]}",
            task_id=task_id,
            kind=artifact_kind,
            uri=f"memory://workspace/{task.workspace_id}/artifacts/{task_id}",
            hash=hashlib.sha256(artifact_content.encode("utf-8")).hexdigest(),
            citation_refs=citation_refs,
            created_at=str(time.time()),
            updated_at=str(time.time()),
        )
        cls._artifacts[artifact.artifact_id] = artifact
        cls._artifact_content[artifact.artifact_id] = artifact_content
        cls._artifact_citation_refs[artifact.artifact_id] = citation_refs
        cls._artifact_ids_by_task[task_id] = [artifact.artifact_id]
        cls._events.setdefault(task_id, []).extend(
            [
                cls._event(
                    task_id=task_id,
                    trace_id=trace_id,
                    event_type="answer",
                    status="running",
                    payload={"message": f"Prepared answer artifact for {goal}."},
                ),
                cls._event(
                    task_id=task_id,
                    trace_id=trace_id,
                    event_type="artifact_created",
                    status="finalizing",
                    payload={
                        "artifact_id": artifact.artifact_id,
                        "kind": artifact.kind,
                        "download_url": cls._artifact_download_url(artifact.artifact_id),
                        "citation_ids": [ref["citation_id"] for ref in citation_refs],
                        "citation_refs": citation_refs,
                    },
                ),
                cls._event(
                    task_id=task_id,
                    trace_id=trace_id,
                    event_type="eval_diagnostic",
                    status="finalizing",
                    payload={
                        "citation_required": bool(simple_task.output_contract.citation_required) if simple_task.output_contract else True,
                        "release_eval": cls._record_release_eval(
                            task=task,
                            simple_task=simple_task,
                            citation_coverage=citation_coverage,
                            required_citation_coverage=required_citation_coverage,
                            security_block_count=0,
                            source_refs=cls._trace_replays.get(task_id, {}).get("source_refs", []),
                        ),
                    },
                ),
                cls._event(task_id=task_id, trace_id=trace_id, event_type="task_completed", status="completed", payload={"artifact_id": artifact.artifact_id}),
            ]
        )
        task.status = "completed"
        task.updated_at = str(time.time())

    @classmethod
    def _uploaded_file_payloads(cls, uploaded_file_ids: list[str]) -> list[dict]:
        return [
            cls._files[file_id].model_dump()
            for file_id in uploaded_file_ids
            if file_id in cls._files
        ]

    @staticmethod
    def _file_status_payload(
        *,
        file: UploadedFileContract,
        filename: str | None = None,
        storage_uri: str | None = None,
        source_ref: str | None = None,
        source_sha256: str | None = None,
        size_bytes: int = 0,
        parse_snapshot: ParseJobSnapshot | None = None,
        document_version: DocumentVersionRecord | None = None,
        index_job: IndexJobManifest | None = None,
        index_status: str = "not_indexed",
    ) -> dict:
        source_provenance = (
            dict(getattr(parse_snapshot, "source_provenance", {}) or {})
            if parse_snapshot is not None
            else {}
        )
        dependency_probe = (
            dict(getattr(parse_snapshot, "diagnostics", {}) or {})
            if parse_snapshot is not None
            else {}
        )
        resolved_index_status = index_status
        if index_job is not None:
            resolved_index_status = "indexed" if index_job.status == "succeeded" else index_job.status
        status = WorkspaceFileStatus(
            file_id=file.file_id,
            filename=filename or file.file_id,
            mime_type=file.mime_type,
            size_bytes=size_bytes,
            source_sha256=source_sha256 or file.hash,
            storage_uri=storage_uri,
            source_ref=source_ref or file.file_id,
            parse_status=file.parse_status,
            index_status=resolved_index_status,
            parser_id=getattr(parse_snapshot, "parser_id", None),
            document_version_id=(
                document_version.document_version_id
                if document_version is not None
                else source_provenance.get("document_version_id")
            ),
            index_job_id=index_job.job_id if index_job is not None else None,
            blocked_reason=getattr(parse_snapshot, "blocked_reason", None),
            dependency_probe=dependency_probe,
            retry_count=int(getattr(parse_snapshot, "attempt_count", 1) or 1) - 1
            if parse_snapshot is not None
            else 0,
            last_error=getattr(parse_snapshot, "failure_reason", None),
        )
        return status.model_dump(mode="json")

    @staticmethod
    def _retrieval_profile_map(simple_task: WorkSpaceSimpleTask | None) -> dict[str, str]:
        if simple_task is None:
            return {}
        profiles = {
            knowledge_space_id: "standard"
            for knowledge_space_id in simple_task.knowledge_space_ids
        }
        for knowledge_space_id, profile in simple_task.retrieval_profiles.items():
            profiles[knowledge_space_id] = str(profile)
        for selection in simple_task.knowledge_space_profiles:
            profiles[selection.knowledge_space_id] = str(selection.retrieval_profile)
        if (
            simple_task.retrieval_mode in {"standard", "deep"}
            and simple_task.knowledge_space_ids
            and not simple_task.retrieval_profiles
            and not simple_task.knowledge_space_profiles
        ):
            profiles = {
                knowledge_space_id: simple_task.retrieval_mode
                for knowledge_space_id in simple_task.knowledge_space_ids
            }
        return profiles

    @classmethod
    def _requested_retrieval_profile(cls, simple_task: WorkSpaceSimpleTask | None) -> RetrievalProfile:
        profiles = cls._retrieval_profile_map(simple_task)
        if any(profile == "deep" for profile in profiles.values()):
            return RetrievalProfile.DEEP
        return RetrievalProfile.STANDARD

    @classmethod
    def _explicit_retrieval_profile(cls, simple_task: WorkSpaceSimpleTask | None) -> RetrievalProfile | None:
        if simple_task is None:
            return None
        explicit_profiles = bool(simple_task.retrieval_profiles or simple_task.knowledge_space_profiles)
        explicit_mode = simple_task.retrieval_mode in {"standard", "deep"}
        if not explicit_profiles and not explicit_mode:
            return None
        return cls._requested_retrieval_profile(simple_task)

    @classmethod
    def _retrieval_plan_summary(
        cls,
        *,
        task: WorkspaceTaskContract,
        simple_task: WorkSpaceSimpleTask | None,
    ) -> dict:
        planner_output = cls._planner_outputs.get(task.task_id)
        retrieval_result = cls._task_retrieval_results.get(task.task_id)
        product_decision = (
            retrieval_result.retrieval_decision
            if retrieval_result is not None
            else None
        )
        requested_profile = (
            product_decision.requested_profile.value
            if product_decision is not None
            else (
                planner_output.retrieval_plan.requested_profile.value
                if planner_output is not None
                else cls._requested_retrieval_profile(simple_task).value
            )
        )
        effective_profile = (
            product_decision.effective_profile.value
            if product_decision is not None
            else (
                planner_output.retrieval_plan.effective_profile.value
                if planner_output is not None
                else requested_profile
            )
        )
        return {
            "retrieval_profiles": cls._retrieval_profile_map(simple_task),
            "requested_profile": requested_profile,
            "effective_profile": effective_profile,
            "fallback_reason": (
                product_decision.fallback_reason
                if product_decision is not None
                else (
                    planner_output.retrieval_plan.fallback_reason
                    if planner_output is not None
                    else None
                )
            ),
            "retrievers_used": (
                list(product_decision.retrievers_used)
                if product_decision is not None
                else (
                    list(planner_output.retrieval_plan.retrievers_used)
                    if planner_output is not None
                    else []
                )
            ),
            "evidence_count": (
                product_decision.evidence_count
                if product_decision is not None
                else 0
            ),
            "citation_coverage": (
                product_decision.citation_coverage
                if product_decision is not None
                else 0.0
            ),
        }

    @classmethod
    def _plan_summary(cls, task_id: str) -> dict:
        planner_output = cls._planner_outputs.get(task_id)
        if planner_output is None:
            return {"strategy": None, "selected_skill": None, "steps": []}
        return {
            "strategy": planner_output.strategy.strategy,
            "reason": planner_output.strategy.reason,
            "selected_skill": planner_output.strategy.selected_skill,
            "plan_id": planner_output.plan_state.plan_id,
            "status": planner_output.plan_state.status,
            "steps": [
                {
                    "step_id": step.step_id,
                    "action_type": step.action_type,
                    "goal": step.goal,
                }
                for step in planner_output.plan_state.steps
            ],
        }

    @classmethod
    def _reflection_summary(cls, task_id: str) -> dict:
        planner_output = cls._planner_outputs.get(task_id)
        if planner_output is None:
            return {"decision": None, "reason": "planner_output_missing"}
        return planner_output.reflection_verdict.model_dump(mode="json")

    @classmethod
    def _replan_summary(cls, task_id: str) -> dict:
        planner_output = cls._planner_outputs.get(task_id)
        if planner_output is None or planner_output.replan_decision is None:
            return {"created": False}
        payload = planner_output.replan_decision.model_dump(mode="json")
        payload["created"] = True
        return payload

    @classmethod
    def _trace_summary(cls, task_id: str) -> dict:
        task = cls._tasks.get(task_id)
        events = cls._events.get(task_id, [])
        replay = cls._trace_replays.get(task_id, {"source_refs": []})
        return {
            "trace_id": task.trace_id if task is not None else None,
            "event_count": len(events),
            "event_types": [event.type for event in events],
            "span_count": len(cls._trace_spans.get(task_id, [])),
            "source_refs": list(replay.get("source_refs") or []),
        }

    @classmethod
    def _eval_summary(cls, task_id: str) -> dict:
        release_eval = cls._release_evals.get(task_id) or {}
        return {
            "release_eval_status": release_eval.get("status"),
            "dataset_version": release_eval.get("dataset_version"),
            "metric_results": dict(release_eval.get("metric_results") or {}),
            "source_refs": list(release_eval.get("source_refs") or []),
        }

    @staticmethod
    def _cost_summary(task_id: str) -> dict:
        _ = task_id
        return {
            "estimated_cost": 0.0,
            "token_count": 0,
            "latency_ms": 0.0,
            "model_id": "local-runtime",
            "source": "local_estimate",
        }

    @classmethod
    def _capability_snapshot(cls, task_id: str) -> dict:
        planner_output = cls._planner_outputs.get(task_id)
        if planner_output is None:
            return {"selected_skill": None, "allowed_tools": [], "allowed_capabilities": []}
        return {
            "selected_skill": (
                planner_output.selected_skill.skill_id
                if planner_output.selected_skill is not None
                else planner_output.strategy.selected_skill
            ),
            "selection_mode": (
                planner_output.selected_skill.selection_mode
                if planner_output.selected_skill is not None
                else None
            ),
            "allowed_tools": list(planner_output.capability_plan.allowed_tools),
            "allowed_capabilities": list(planner_output.capability_plan.allowed_capabilities),
            "approval_required_tools": list(planner_output.capability_plan.approval_required_tools),
        }

    @classmethod
    def _knowledge_config_summary(cls, simple_task: WorkSpaceSimpleTask | None) -> dict:
        return {
            "selected_knowledge_spaces": list(simple_task.knowledge_space_ids)
            if simple_task is not None
            else [],
            "retrieval_profiles": cls._retrieval_profile_map(simple_task),
            "retrieval_defaults": {
                "default_profile": "standard",
                "available_profiles": ["standard", "deep"],
            },
        }

    @staticmethod
    def _citation_refs_from_result(
        retrieval_result: AgenticRetrievalRuntimeResult | None,
    ) -> list[dict[str, Any]]:
        if retrieval_result is None:
            return []
        return [
            {
                "citation_id": citation.label,
                "evidence_id": citation.evidence_id,
                "document_id": citation.document_id,
                "block_id": citation.block_id,
                "source_ref": f"{citation.document_id}::{citation.block_id}",
                "source_span": dict(citation.source_span),
                "trust_label": citation.trust_label,
                "source_uri": citation.source_uri,
                "provenance": dict(citation.provenance),
            }
            for citation in retrieval_result.citations
        ]

    @classmethod
    def _run_workspace_tools_until_interrupt(
        cls,
        *,
        task_id: str,
        simple_task: WorkSpaceSimpleTask,
        login_user: UserPayload,
        runtime_state: ControllerRuntimeState,
    ) -> ToolRuntimeExecutionResult | None:
        for tool_id in simple_task.plugins:
            if cls._tool_runtime.get_manifest(tool_id) is None:
                continue
            request = ToolRuntimeRequest(
                tool_id=tool_id,
                arguments=cls._tool_arguments(simple_task=simple_task, tool_id=tool_id),
                workspace_id=simple_task.workspace_id or "workspace_default",
                user_id=login_user.user_id,
                task_id=task_id,
                trace_id=simple_task.trace_id or runtime_state.trace_id,
                model_intent=simple_task.query,
                runtime_state=runtime_state,
            )
            result = cls._tool_runtime.execute(request)
            cls._append_tool_runtime_events(task_id=task_id, result=result)
            if result.approval_required:
                cls._pending_tool_requests[task_id] = request
                return result
            if result.status == "blocked":
                task = cls._require_task(task_id)
                task.status = "failed"
                task.updated_at = str(time.time())
                return result
        return None

    @classmethod
    def _append_tool_runtime_events(
        cls,
        *,
        task_id: str,
        result: ToolRuntimeExecutionResult,
    ) -> None:
        task = cls._require_task(task_id)
        cls._record_security_span(task_id=task_id, audit=result.audit_event)
        for event in result.task_events:
            cls._events.setdefault(task_id, []).append(
                cls._event(
                    task_id=task_id,
                    trace_id=task.trace_id or "",
                    event_type=str(event["type"]),
                    status=str(event["status"]),
                    payload=dict(event["payload"]),
                )
            )

    @staticmethod
    def _tool_arguments(*, simple_task: WorkSpaceSimpleTask, tool_id: str) -> dict:
        if tool_id == "filesystem.read":
            target = (
                simple_task.uploaded_file_ids[0]
                if simple_task.uploaded_file_ids
                else "workspace://current"
            )
            return {"path": target, "query": simple_task.query}
        if tool_id == "filesystem.write":
            return {
                "path": f"artifacts/{simple_task.task_id or 'task'}.md",
                "content": simple_task.query,
            }
        if tool_id == "mail.send":
            return {
                "to": "workspace-review@example.com",
                "subject": simple_task.goal or "Zuno task update",
                "body": simple_task.query,
            }
        return {"query": simple_task.query}

    @classmethod
    def _require_file(cls, file_id: str) -> UploadedFileContract:
        file = cls._files.get(file_id)
        if file is None:
            raise HTTPException(status_code=404, detail="Workspace file not found")
        return file

    @classmethod
    def _preflight_retrieval_security(
        cls,
        *,
        task: WorkspaceTaskContract,
        simple_task: WorkSpaceSimpleTask,
    ) -> RetrievalGateResult | None:
        if not simple_task.knowledge_space_ids:
            return None
        candidates: list[RetrievalCandidate] = []
        try:
            for knowledge_space_id in simple_task.knowledge_space_ids:
                payload = cls._knowledge_index_runtime.to_retrieval_payload(
                    knowledge_space_id,
                    simple_task.query,
                )
                for documents in payload.get("documents_by_source", {}).values():
                    for document in documents:
                        if float(document.get("score") or 0.0) <= 0:
                            continue
                        metadata = dict(document.get("metadata") or {})
                        candidates.append(
                            RetrievalCandidate(
                                chunk_id=str(document.get("chunk_id") or ""),
                                workspace_id=str(document.get("workspace_id") or payload.get("manifest", {}).get("workspace_id") or ""),
                                acl_scope=str(metadata.get("acl_scope") or "workspace"),
                                document_trust_label=str(metadata.get("trust_label") or "indexed"),
                                text=str(document.get("content") or ""),
                                metadata=metadata,
                            )
                        )
        except KeyError:
            return None
        if not candidates:
            return None
        return cls._retrieval_security_gate.filter_candidates(
            workspace_id=task.workspace_id,
            allowed_acl_scopes={"workspace", task.policy_scope},
            candidates=candidates,
            trace_id=task.trace_id or "",
            task_id=task.task_id,
        )

    @classmethod
    def _ensure_knowledge_space(cls, *, knowledge_space_id: str, workspace_id: str) -> None:
        try:
            cls._knowledge_index_runtime.to_retrieval_payload(knowledge_space_id, "__health__")
        except KeyError:
            cls._knowledge_index_runtime.create_knowledge_space(
                knowledge_space_id=knowledge_space_id,
                workspace_id=workspace_id,
                graph_project_id=f"graph_{knowledge_space_id}",
            )

    @staticmethod
    def _document_from_file(*, file: UploadedFileContract, content: str) -> CanonicalDocumentIR:
        return CanonicalDocumentIR(
            metadata=DocumentMetadata(
                document_id=file.file_id,
                workspace_id=file.workspace_id,
                source_uri=f"memory://workspace/{file.workspace_id}/files/{file.file_id}",
                mime_type=file.mime_type,
                hash=file.hash,
                parser_id="workspace_text_runtime",
                parser_version="phase09-runtime-v1",
                acl_scope=file.policy_scope,
            ),
            blocks=[
                DocumentBlock(
                    block_id="block_1",
                    type="paragraph",
                    text=content or f"Uploaded file {file.file_id}.",
                    source_span=SourceSpan(line_range=[1, 1]),
                    acl_scope=file.policy_scope,
                )
            ],
            provenance=DocumentProvenance(
                parser_id="workspace_text_runtime",
                parser_version="phase09-runtime-v1",
                source_uri=f"memory://workspace/{file.workspace_id}/files/{file.file_id}",
                confidence=1.0,
            ),
        )

    @staticmethod
    def _parser_source_uri(*, file: UploadedFileContract) -> str:
        base_uri = f"memory://workspace/{file.workspace_id}/files/{file.file_id}"
        if "." in file.file_id.rsplit("/", 1)[-1]:
            return base_uri
        extension_by_mime = {
            "text/markdown": ".md",
            "text/plain": ".txt",
            "text/csv": ".csv",
            "application/json": ".json",
            "text/html": ".html",
            "text/x-python": ".py",
            "application/pdf": ".pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        }
        return f"{base_uri}{extension_by_mime.get(file.mime_type, '')}"

    @classmethod
    def _persist_workspace_product_state(cls, task_id: str) -> None:
        if cls._durable_ingestion_store is None:
            return
        task = cls._tasks.get(task_id)
        if task is None:
            return
        cls._durable_ingestion_store.save_workspace_task(
            WorkspaceTaskRecord(
                task_id=task.task_id,
                workspace_id=task.workspace_id,
                owner_id=task.owner,
                status=task.status,
                trace_id=task.trace_id,
                payload={"task": task.model_dump()},
            )
        )
        for event in cls._events.get(task_id, []):
            cls._durable_ingestion_store.save_task_event(
                TaskEventRecord(
                    event_id=event.event_id,
                    task_id=event.task_id,
                    trace_id=event.trace_id,
                    event_type=event.type,
                    timestamp=event.timestamp,
                    payload=event.payload,
                )
            )
        for artifact_id in cls._artifact_ids_by_task.get(task_id, []):
            artifact = cls._artifacts.get(artifact_id)
            if artifact is None:
                continue
            content = cls._artifact_content.get(artifact_id, "")
            cls._durable_ingestion_store.save_artifact(
                ArtifactRecord(
                    artifact_id=artifact.artifact_id,
                    task_id=artifact.task_id,
                    workspace_id=artifact.workspace_id,
                    owner_id=artifact.owner,
                    kind=artifact.kind,
                    uri=artifact.uri,
                    content=content,
                    content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
                    trace_id=artifact.trace_id,
                    payload={"artifact": artifact.model_dump()},
                )
            )
        for feedback_id in cls._feedback_ids_by_task.get(task_id, []):
            feedback = cls._feedback.get(feedback_id)
            if feedback is None:
                continue
            cls._durable_ingestion_store.save_feedback(
                FeedbackRecord(
                    feedback_id=feedback.feedback_id,
                    task_id=feedback.task_id,
                    rating=feedback.rating,
                    label=feedback.label,
                    comment=feedback.comment,
                    dataset_candidate=feedback.dataset_candidate,
                    payload={"feedback": feedback.model_dump()},
                )
            )

    @classmethod
    def get_task_snapshot(cls, task_id: str) -> dict:
        task = cls._require_task(task_id)
        cls._persist_workspace_product_state(task_id)
        artifact_ids = cls._artifact_ids_by_task.get(task_id, [])
        feedback_ids = cls._feedback_ids_by_task.get(task_id, [])
        runtime_snapshot = cls._durable_runtime.get_task_snapshot(task_id)
        simple_task = cls._task_inputs.get(task_id)
        return {
            "task": task.model_dump(),
            "artifact_ids": list(artifact_ids),
            "artifacts": [cls._artifacts[artifact_id].model_dump() for artifact_id in artifact_ids],
            "feedback_ids": list(feedback_ids),
            "feedback": [cls._feedback[feedback_id].model_dump() for feedback_id in feedback_ids],
            "lifecycle": cls._task_lifecycle_snapshot(
                task=task,
                runtime_snapshot=runtime_snapshot,
            ).model_dump(),
            "runtime": runtime_snapshot.to_dict() if runtime_snapshot is not None else None,
            "observability": {
                "spans": list(cls._trace_spans.get(task_id, [])),
                "release_eval": cls._release_evals.get(task_id),
                "trace_replay": cls._trace_replays.get(task_id, {"source_refs": []}),
            },
            "retrieval_plan": cls._retrieval_plan_summary(task=task, simple_task=simple_task),
            "plan_summary": cls._plan_summary(task_id),
            "reflection_summary": cls._reflection_summary(task_id),
            "replan_summary": cls._replan_summary(task_id),
            "trace_summary": cls._trace_summary(task_id),
            "eval_summary": cls._eval_summary(task_id),
            "cost_summary": cls._cost_summary(task_id),
            "capability_snapshot": cls._capability_snapshot(task_id),
            "knowledge_config_summary": cls._knowledge_config_summary(simple_task),
        }

    @classmethod
    def list_task_events(cls, task_id: str) -> list[dict]:
        cls._require_task(task_id)
        return [event.model_dump() for event in cls._events.get(task_id, [])]

    @classmethod
    async def stream_task_events(cls, task_id: str):
        cls._require_task(task_id)
        for event in cls._events.get(task_id, []):
            payload = cls._to_frontend_stream_payload(event)
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    @classmethod
    def get_artifact(cls, artifact_id: str) -> dict:
        artifact = cls._artifacts.get(artifact_id)
        if artifact is None:
            raise HTTPException(status_code=404, detail="Workspace artifact not found")
        citation_refs = cls._artifact_citation_refs.get(
            artifact_id,
            [ref.model_dump(mode="json") for ref in artifact.citation_refs],
        )
        return {
            "artifact": artifact.model_dump(),
            "content": cls._artifact_content.get(artifact_id, ""),
            "citation_refs": citation_refs,
            "download": {
                "url": cls._artifact_download_url(artifact_id),
                "filename": cls._artifact_filename(artifact),
                "media_type": "text/markdown; charset=utf-8",
                "policy": artifact.download_policy,
            },
        }

    @classmethod
    def download_artifact(cls, artifact_id: str) -> dict:
        artifact = cls._artifacts.get(artifact_id)
        if artifact is None:
            raise HTTPException(status_code=404, detail="Workspace artifact not found")
        return {
            "artifact": artifact,
            "content": cls._artifact_content.get(artifact_id, ""),
            "filename": cls._artifact_filename(artifact),
            "media_type": "text/markdown; charset=utf-8",
        }

    @classmethod
    def record_feedback(
        cls,
        *,
        task_id: str,
        rating: int | None,
        label: str | None,
        comment: str | None,
        dataset_candidate: bool,
    ) -> dict:
        task = cls._require_task(task_id)
        feedback = FeedbackContract(
            feedback_id=f"feedback_{uuid4().hex[:12]}",
            task_id=task_id,
            rating=rating,
            label=label,
            comment=comment,
            dataset_candidate=dataset_candidate,
            created_at=str(time.time()),
        )
        cls._feedback[feedback.feedback_id] = feedback
        cls._feedback_ids_by_task.setdefault(task_id, []).append(feedback.feedback_id)
        cls._events.setdefault(task_id, []).append(
            cls._event(
                task_id=task_id,
                trace_id=task.trace_id or "",
                event_type="feedback_received",
                status=task.status,
                payload={"feedback_id": feedback.feedback_id, "dataset_candidate": dataset_candidate},
            ),
        )
        cls._persist_workspace_product_state(task_id)
        return feedback.model_dump()

    @classmethod
    def _require_task(cls, task_id: str) -> WorkspaceTaskContract:
        task = cls._tasks.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Workspace task not found")
        return task

    @staticmethod
    def _artifact_download_url(artifact_id: str) -> str:
        return f"/api/v1/workspace/artifact/{artifact_id}/download"

    @classmethod
    def _artifact_filename(cls, artifact: ArtifactContract) -> str:
        task = cls._tasks.get(artifact.task_id)
        source = task.goal if task is not None else artifact.uri.rsplit("/", 1)[-1]
        slug = source.replace("_", "-").replace(" ", "-").lower()
        safe_slug = "".join(
            ch for ch in slug if ch.isalnum() or ch in {"-", "."}
        ).strip("-")
        return f"{safe_slug or artifact.artifact_id}.md"

    @classmethod
    def _task_lifecycle_snapshot(
        cls,
        *,
        task: WorkspaceTaskContract,
        runtime_snapshot: object | None,
    ) -> WorkspaceTaskLifecycleSnapshot:
        _ = runtime_snapshot
        recovery = cls._task_recovery.get(task.task_id, {})
        state = cls._lifecycle_state_for_status(task.status, recovery=recovery)
        recoverable = bool(recovery.get("recoverable")) if state == "recoverable_failed" else False
        return WorkspaceTaskLifecycleSnapshot(
            task_id=task.task_id,
            trace_id=task.trace_id,
            state=state,
            status=task.status,
            recoverable=recoverable,
            recovery_actions=cls._recovery_actions_for_state(
                state,
                recoverable=recoverable,
            ),
            downloadable_artifact_ids=list(cls._artifact_ids_by_task.get(task.task_id, [])),
        )

    @classmethod
    def _lifecycle_state_for_status(cls, status: str, *, recovery: dict | None = None) -> str:
        normalized = (status or "").strip().lower()
        if normalized == "failed" and recovery and recovery.get("recoverable") is True:
            return "recoverable_failed"
        return WORKSPACE_TASK_STATUS_TO_LIFECYCLE.get(normalized, "running")

    @staticmethod
    def _recovery_actions_for_state(state: str, *, recoverable: bool) -> list[str]:
        if state == "recoverable_failed" and not recoverable:
            return ["download_trace", "send_feedback"]
        return list(WORKSPACE_TASK_RECOVERY_ACTIONS.get(state, []))

    @staticmethod
    def _event(
        *,
        task_id: str,
        trace_id: str,
        event_type: str,
        status: str,
        payload: dict,
    ) -> TraceEventContract:
        event_payload = {"status": status, **payload}
        return TraceEventContract(
            event_id=f"event_{uuid4().hex[:12]}",
            task_id=task_id,
            trace_id=trace_id,
            type=event_type,
            timestamp=time.time(),
            payload=event_payload,
        )

    @classmethod
    def _append_security_gate_event(
        cls,
        *,
        task_id: str,
        result: GateResult | RetrievalGateResult,
    ) -> None:
        audit = result.audit_event
        payload = audit.to_trace_payload()
        payload["findings"] = [finding.to_dict() for finding in result.findings]
        sanitized_content = getattr(result, "sanitized_content", None)
        if sanitized_content is not None:
            payload["sanitized_content"] = sanitized_content
        allowed_candidates = getattr(result, "allowed_candidates", None)
        blocked_candidates = getattr(result, "blocked_candidates", None)
        if allowed_candidates is not None:
            payload["allowed_candidate_ids"] = [candidate.chunk_id for candidate in allowed_candidates]
        if blocked_candidates is not None:
            payload["blocked_candidate_ids"] = [candidate.chunk_id for candidate in blocked_candidates]
        cls._events.setdefault(task_id, []).append(
            cls._event(
                task_id=task_id,
                trace_id=audit.trace_id,
                event_type="security_gate",
                status=audit.policy_decision.value,
                payload=payload,
            )
        )

    @classmethod
    def _record_security_span(cls, *, task_id: str, audit: SandboxAuditEvent) -> None:
        span = cls._span_builder.from_security_audit(
            audit,
            run_id=f"run_{audit.audit_id}",
        )
        cls._trace_spans.setdefault(task_id, []).append(span.to_otel_span())

    @classmethod
    def _record_retrieval_observability(
        cls,
        *,
        task: WorkspaceTaskContract,
        simple_task: WorkSpaceSimpleTask,
        retrieval_result: AgenticRetrievalRuntimeResult,
    ) -> None:
        trace_metadata = retrieval_result.trace_metadata
        artifact_manifest = dict(trace_metadata.get("artifact_manifest") or {})
        source_refs = list(artifact_manifest.get("retrieval_refs") or [])
        cls._trace_replays[task.task_id] = {
            "trace_id": task.trace_id,
            "task_id": task.task_id,
            "source_refs": source_refs,
            "event_ids": list(artifact_manifest.get("event_ids") or []),
        }
        span = cls._span_builder.build_span(
            trace_id=task.trace_id or "",
            session_id=simple_task.session_id,
            thread_id=simple_task.session_id,
            task_id=task.task_id,
            turn_id=task.task_id,
            run_id=f"run_retrieval_{task.task_id}",
            parent_run_id=None,
            run_type="retriever",
            span_kind=ZunoSpanKind.RETRIEVAL,
            name="agentic retrieval",
            inputs={"query": simple_task.query},
            outputs={
                "evidence_count": len(retrieval_result.evidence_bundle.items),
                "citation_coverage": retrieval_result.trace.citation_coverage,
                "source_refs": source_refs,
            },
            redacted_payload=trace_metadata,
            policy_decision="allow",
            metadata={
                "router_decision": retrieval_result.decision.router_decision,
                "resolved_methods": [
                    method.value for method in retrieval_result.decision.resolved_methods
                ],
            },
        )
        cls._trace_spans.setdefault(task.task_id, []).append(span.to_otel_span())

    @classmethod
    def _build_planner_output(
        cls,
        *,
        task: WorkspaceTaskContract,
        simple_task: WorkSpaceSimpleTask,
        login_user: UserPayload,
    ) -> PlannerOutput:
        selector = build_default_strategy_selector()
        return selector.select(
            PlanningRequest(
                task_id=task.task_id,
                trace_id=task.trace_id or "",
                workspace_id=task.workspace_id,
                user_goal=task.goal,
                requested_retrieval_profile=cls._requested_retrieval_profile(simple_task),
                context_pack={
                    "session_id": simple_task.session_id,
                    "knowledge_space_ids": list(simple_task.knowledge_space_ids),
                    "retrieval_profiles": cls._retrieval_profile_map(simple_task),
                    "product_mode": simple_task.product_mode,
                },
                pinned_skill_id=(
                    simple_task.agent_skill_ids[0]
                    if simple_task.agent_skill_ids
                    else None
                ),
                available_capability_ids=tuple(simple_task.plugins),
                user_roles=cls._user_roles(login_user),
                graph_available=True,
            )
        )

    @staticmethod
    def _user_roles(login_user: UserPayload) -> tuple[str, ...]:
        roles = getattr(login_user, "user_role", None)
        if isinstance(roles, list):
            return tuple(str(role) for role in roles)
        if roles:
            return (str(roles),)
        return ("member",)

    @classmethod
    def _record_release_eval(
        cls,
        *,
        task: WorkspaceTaskContract,
        simple_task: WorkSpaceSimpleTask,
        citation_coverage: float,
        required_citation_coverage: float,
        security_block_count: int,
        source_refs: list[str] | None = None,
        failure_examples: list[dict] | None = None,
    ) -> dict:
        baseline = ReleaseEvalBaseline(
            dataset_version="workspace-runtime-phase10-v1",
            evaluator_version="security-observability-v1",
            commit_sha="local-runtime",
            metrics=[
                EvalMetricResult(
                    name="citation_coverage",
                    value=citation_coverage,
                    threshold=required_citation_coverage,
                ),
                EvalMetricResult(name="approval_escape_count", value=0, threshold=0),
                EvalMetricResult(name="secret_redaction_miss_count", value=0, threshold=0),
                EvalMetricResult(name="security_block_count", value=security_block_count, threshold=0),
            ],
            failure_examples=failure_examples or [],
        )
        result = baseline.evaluate(
            [
                MetricThreshold(name="citation_coverage", operator=">=", value=required_citation_coverage),
                MetricThreshold(name="approval_escape_count", operator="==", value=0),
                MetricThreshold(name="secret_redaction_miss_count", operator="==", value=0),
                MetricThreshold(name="security_block_count", operator="==", value=0),
            ]
        )
        payload = result.to_release_evidence()
        payload["source_refs"] = list(source_refs or [])
        cls._release_evals[task.task_id] = payload
        span = cls._span_builder.build_span(
            trace_id=task.trace_id or "",
            session_id=simple_task.session_id,
            thread_id=simple_task.session_id,
            task_id=task.task_id,
            turn_id=task.task_id,
            run_id=f"run_eval_{task.task_id}",
            parent_run_id=None,
            run_type="evaluator",
            span_kind=ZunoSpanKind.EVAL,
            name="release baseline",
            inputs={"dataset_version": payload["dataset_version"]},
            outputs={
                "status": payload["status"],
                "citation_coverage": citation_coverage,
                "security_block_count": security_block_count,
            },
            redacted_payload=payload,
            policy_decision=payload["status"],
        )
        cls._trace_spans.setdefault(task.task_id, []).append(span.to_otel_span())
        return payload

    @classmethod
    def _fail_task(
        cls,
        *,
        task_id: str,
        simple_task: WorkSpaceSimpleTask,
        reason: str,
        citation_coverage: float,
        required_citation_coverage: float,
        security_block_count: int,
        source_refs: list[str] | None = None,
        recoverable: bool = False,
        failure_examples: list[dict] | None = None,
    ) -> None:
        task = cls._require_task(task_id)
        task.status = "failed"
        task.updated_at = str(time.time())
        cls._task_recovery[task_id] = {
            "reason": reason,
            "recoverable": recoverable,
            "actions": cls._recovery_actions_for_state(
                "recoverable_failed",
                recoverable=recoverable,
            ),
        }
        release_eval = cls._record_release_eval(
            task=task,
            simple_task=simple_task,
            citation_coverage=citation_coverage,
            required_citation_coverage=required_citation_coverage,
            security_block_count=security_block_count,
            source_refs=source_refs or [],
            failure_examples=failure_examples or [{"reason": reason}],
        )
        try:
            cls._durable_runtime.mark_failure(
                task_id,
                node="answer_or_artifact",
                error=reason,
                recoverable=recoverable,
                details={
                    "source_refs": list(source_refs or []),
                    "artifact_ids": list(cls._artifact_ids_by_task.get(task_id, [])),
                    "release_eval_status": release_eval.get("status"),
                },
            )
        except KeyError:
            pass
        cls._events.setdefault(task_id, []).extend(
            [
                cls._event(
                    task_id=task_id,
                    trace_id=task.trace_id or "",
                    event_type="eval_diagnostic",
                    status="failed",
                    payload={"release_eval": release_eval},
                ),
                cls._event(
                    task_id=task_id,
                    trace_id=task.trace_id or "",
                    event_type="task_failed",
                    status="failed",
                    payload={
                        "reason": reason,
                        "lifecycle_state": cls._lifecycle_state_for_status(
                            task.status,
                            recovery=cls._task_recovery.get(task_id),
                        ),
                        "recovery_actions": cls._task_recovery[task_id]["actions"],
                    },
                ),
            ]
        )

    @classmethod
    def _answer_from_index(
        cls,
        *,
        task: WorkspaceTaskContract,
        simple_task: WorkSpaceSimpleTask,
        goal: str,
    ) -> AgenticRetrievalRuntimeResult | None:
        if not simple_task.knowledge_space_ids:
            return None
        try:
            return cls._agentic_retrieval_runtime.answer(
                AgenticRetrievalRuntimeRequest(
                    query=simple_task.query,
                    workspace_id=task.workspace_id,
                    knowledge_space_ids=list(simple_task.knowledge_space_ids),
                    retrieval_profile=cls._explicit_retrieval_profile(simple_task),
                    product_mode=_product_mode_for_retrieval(simple_task.product_mode),
                    context_pack={
                        "goal": goal,
                        "session_id": simple_task.session_id,
                        "uploaded_file_ids": list(simple_task.uploaded_file_ids),
                        "retrieval_profiles": cls._retrieval_profile_map(simple_task),
                    },
                    allowed_acl_scopes={"workspace", task.policy_scope},
                    trace_id=task.trace_id or "",
                    task_id=task.task_id,
                )
            )
        except KeyError:
            return None

    @staticmethod
    def _render_artifact_content(
        *,
        simple_task: WorkSpaceSimpleTask,
        goal: str,
        retrieval_result: AgenticRetrievalRuntimeResult | None = None,
    ) -> str:
        answer_lines = []
        if retrieval_result is not None:
            answer_lines = [
                "",
                "## Answer",
                retrieval_result.answer,
                "",
                "## Citations",
                *[
                    f"- {citation.label} {citation.document_id}::{citation.block_id}"
                    for citation in retrieval_result.citations
                ],
            ]
        return "\n".join(
            [
                f"# {goal}",
                "",
                f"Query: {simple_task.query}",
                f"Product mode: {simple_task.product_mode}",
                f"Uploaded files: {', '.join(simple_task.uploaded_file_ids) or 'none'}",
                f"Knowledge spaces: {', '.join(simple_task.knowledge_space_ids) or 'none'}",
                *answer_lines,
            ]
        )

    @staticmethod
    def _runtime_state_for_task(
        *,
        simple_task: WorkSpaceSimpleTask,
        login_user: UserPayload,
        task_id: str,
        trace_id: str,
        workspace_id: str,
        goal: str,
    ) -> ControllerRuntimeState:
        return ControllerRuntimeState(
            thread_id=simple_task.session_id or f"thread_{task_id}",
            workspace_id=workspace_id,
            user_id=login_user.user_id,
            task_id=task_id,
            trace_id=trace_id,
            goal=goal,
            context_pack={
                "session_id": simple_task.session_id,
                "product_mode": simple_task.product_mode,
                "knowledge_space_ids": list(simple_task.knowledge_space_ids),
                "uploaded_file_ids": list(simple_task.uploaded_file_ids),
                "retrieval_mode": simple_task.retrieval_mode,
            },
        )

    @classmethod
    def _to_frontend_stream_payload(cls, event: TraceEventContract) -> dict:
        data = {
            "event_id": event.event_id,
            "task_id": event.task_id,
            "trace_id": event.trace_id,
            "phase": event.type,
            "status": event.payload.get("status") or event.payload.get("phase") or "",
            "message": event.payload.get("message") or event.type,
            **event.payload,
        }
        data.setdefault(
            "lifecycle_state",
            cls._lifecycle_state_for_status(str(data.get("status") or "")),
        )
        return {
            "event": event.type,
            "timestamp": event.timestamp,
            "data": data,
        }


def _product_mode_for_retrieval(product_mode: str) -> ProductMode:
    normalized = product_mode.strip().lower()
    if normalized in {"normal"}:
        return ProductMode.NORMAL
    if normalized in {"enhanced", "enterprise_kb", "hr_resume", "contract_review"}:
        return ProductMode.ENHANCED
    return ProductMode.AUTO


__all__ = ["WorkspaceTaskRuntimeService"]
