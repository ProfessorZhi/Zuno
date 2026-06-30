from __future__ import annotations

import hashlib
import json
import time
from uuid import uuid4

from fastapi import HTTPException

from zuno.api.services.user import UserPayload
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
    _ingest_jobs: dict[str, dict] = {}
    _artifacts: dict[str, ArtifactContract] = {}
    _artifact_content: dict[str, str] = {}
    _artifact_ids_by_task: dict[str, list[str]] = {}
    _feedback: dict[str, FeedbackContract] = {}

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
        job = {
            "ingest_task_id": ingest_task_id,
            "workspace_id": workspace_id,
            "file_id": file_id,
            "knowledge_space_id": knowledge_space_id,
            "session_id": session_id,
            "trace_id": normalized_trace_id,
            "status": "accepted",
            "file": file.model_dump(),
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
        approval_required = simple_task.approval_mode not in {"", "auto", "none"}

        task = WorkspaceTaskContract(
            workspace_id=workspace_id,
            owner=login_user.user_id,
            status="approval_waiting" if approval_required else "completed",
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
        if approval_required:
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

        if normalized_decision == "rejected":
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

        simple_task = cls._task_inputs[task_id]
        artifact_kind = (
            simple_task.output_contract.artifact_kinds[0]
            if simple_task.output_contract and simple_task.output_contract.artifact_kinds
            else "markdown"
        )
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
        cls._complete_task(
            task_id=task_id,
            simple_task=simple_task,
            artifact_kind=artifact_kind,
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
        artifact_content = cls._render_artifact_content(simple_task=simple_task, goal=goal)
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
    def _require_file(cls, file_id: str) -> UploadedFileContract:
        file = cls._files.get(file_id)
        if file is None:
            raise HTTPException(status_code=404, detail="Workspace file not found")
        return file

    @classmethod
    def get_task_snapshot(cls, task_id: str) -> dict:
        task = cls._require_task(task_id)
        artifact_ids = cls._artifact_ids_by_task.get(task_id, [])
        return {
            "task": task.model_dump(),
            "artifact_ids": list(artifact_ids),
            "artifacts": [cls._artifacts[artifact_id].model_dump() for artifact_id in artifact_ids],
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

    @staticmethod
    def _render_artifact_content(*, simple_task: WorkSpaceSimpleTask, goal: str) -> str:
        return "\n".join(
            [
                f"# {goal}",
                "",
                f"Query: {simple_task.query}",
                f"Product mode: {simple_task.product_mode}",
                f"Uploaded files: {', '.join(simple_task.uploaded_file_ids) or 'none'}",
                f"Knowledge spaces: {', '.join(simple_task.knowledge_space_ids) or 'none'}",
            ]
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


__all__ = ["WorkspaceTaskRuntimeService"]
