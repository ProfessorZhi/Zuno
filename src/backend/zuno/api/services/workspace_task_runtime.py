from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import time
from uuid import uuid4

from fastapi import HTTPException

from zuno.agent.durable_runtime import InMemoryDurableRuntimeStore, SingleControllerDurableRuntime
from zuno.agent.harness import ControllerRuntimeState
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
from zuno.knowledge.indexing import KnowledgeIndexRuntime
from zuno.knowledge.ingestion import (
    CanonicalDocumentIR,
    DocumentBlock,
    DocumentMetadata,
    DocumentProvenance,
    SourceSpan,
)
from zuno.schema.workspace import (
    ArtifactContract,
    FeedbackContract,
    TraceEventContract,
    UploadedFileContract,
    WorkSpaceSimpleTask,
    WorkspaceTaskBudget,
    WorkspaceTaskContract,
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
    _durable_runtime = SingleControllerDurableRuntime(store=InMemoryDurableRuntimeStore())
    _tool_runtime = build_default_tool_control_plane_runtime()
    _knowledge_index_runtime = KnowledgeIndexRuntime()
    _agentic_retrieval_runtime = AgenticRetrievalRuntime(index_runtime=_knowledge_index_runtime)
    _pending_tool_requests: dict[str, ToolRuntimeRequest] = {}

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
        normalized_hash = file_hash or hashlib.sha256(
            f"{workspace_id}:{normalized_file_id}:{uri or name or mime_type}".encode("utf-8")
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
        cls._file_text[file.file_id] = content or f"{name or normalized_file_id} was uploaded to workspace {workspace_id}."
        return {
            "file": file.model_dump(),
            "name": name,
            "uri": uri,
        }

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
        file.parse_status = "ingest_accepted"
        file.updated_at = str(time.time())
        normalized_trace_id = trace_id or file.trace_id or f"trace_{uuid4().hex[:12]}"
        file.trace_id = normalized_trace_id
        ingest_task_id = f"ingest_{uuid4().hex[:12]}"
        cls._ensure_knowledge_space(
            knowledge_space_id=knowledge_space_id,
            workspace_id=workspace_id,
        )
        document = cls._document_from_file(file=file, content=cls._file_text.get(file_id, ""))
        index_job = cls._knowledge_index_runtime.index_document(
            knowledge_space_id,
            document,
            targets=["bm25", "vector", "graph"],
        )
        file.parse_status = "indexed"
        file.updated_at = str(time.time())
        job = {
            "ingest_task_id": ingest_task_id,
            "workspace_id": workspace_id,
            "file_id": file_id,
            "knowledge_space_id": knowledge_space_id,
            "session_id": session_id,
            "trace_id": normalized_trace_id,
            "status": "accepted",
            "file": file.model_dump(),
            "index_job": index_job.model_dump(),
        }
        cls._ingest_jobs[ingest_task_id] = job
        return job

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
            cls._event(task_id=task_id, trace_id=trace_id, event_type="planning", status="planning", payload={"goal": goal}),
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
                },
            ),
        ]
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
                payload={"reason": normalized_reason},
            )
        )
        return cls.get_task_snapshot(task_id)

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
        retrieval_result = cls._answer_from_index(
            task=task,
            simple_task=simple_task,
            goal=goal,
        )
        if retrieval_result is not None:
            cls._events.setdefault(task_id, []).append(
                cls._event(
                    task_id=task_id,
                    trace_id=trace_id,
                    event_type="retrieval",
                    status="completed",
                    payload=retrieval_result.to_task_event()["payload"],
                )
            )
        artifact_content = cls._render_artifact_content(
            simple_task=simple_task,
            goal=goal,
            retrieval_result=retrieval_result,
        )
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
            created_at=str(time.time()),
            updated_at=str(time.time()),
        )
        cls._artifacts[artifact.artifact_id] = artifact
        cls._artifact_content[artifact.artifact_id] = artifact_content
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
                    payload={"artifact_id": artifact.artifact_id, "kind": artifact.kind},
                ),
                cls._event(
                    task_id=task_id,
                    trace_id=trace_id,
                    event_type="eval_diagnostic",
                    status="finalizing",
                    payload={"citation_required": bool(simple_task.output_contract.citation_required) if simple_task.output_contract else True},
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

    @classmethod
    def get_task_snapshot(cls, task_id: str) -> dict:
        task = cls._require_task(task_id)
        artifact_ids = cls._artifact_ids_by_task.get(task_id, [])
        runtime_snapshot = cls._durable_runtime.get_task_snapshot(task_id)
        return {
            "task": task.model_dump(),
            "artifact_ids": list(artifact_ids),
            "artifacts": [cls._artifacts[artifact_id].model_dump() for artifact_id in artifact_ids],
            "runtime": runtime_snapshot.to_dict() if runtime_snapshot is not None else None,
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
        return {
            "artifact": artifact.model_dump(),
            "content": cls._artifact_content.get(artifact_id, ""),
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
        cls._events.setdefault(task_id, []).append(
            cls._event(
                task_id=task_id,
                trace_id=task.trace_id or "",
                event_type="feedback_received",
                status=task.status,
                payload={"feedback_id": feedback.feedback_id, "dataset_candidate": dataset_candidate},
            ),
        )
        return feedback.model_dump()

    @classmethod
    def _require_task(cls, task_id: str) -> WorkspaceTaskContract:
        task = cls._tasks.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Workspace task not found")
        return task

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
                    product_mode=_product_mode_for_retrieval(simple_task.product_mode),
                    context_pack={
                        "goal": goal,
                        "session_id": simple_task.session_id,
                        "uploaded_file_ids": list(simple_task.uploaded_file_ids),
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

    @staticmethod
    def _to_frontend_stream_payload(event: TraceEventContract) -> dict:
        data = {
            "event_id": event.event_id,
            "task_id": event.task_id,
            "trace_id": event.trace_id,
            "phase": event.type,
            "status": event.payload.get("status") or event.payload.get("phase") or "",
            "message": event.payload.get("message") or event.type,
            **event.payload,
        }
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
