from __future__ import annotations

import time
from typing import Any
from uuid import uuid4

from fastapi import HTTPException

from zuno.api.dto.workspace import ArtifactContract, FeedbackContract
from zuno.knowledge.storage import (
    ArtifactRecord,
    FeedbackRecord,
    SQLiteDurableIngestionStore,
    TaskEventRecord,
)
from zuno.platform.security import (
    SecurityProductActionDenied,
    SecurityProductActionGuard,
    SecurityProductActionRequest,
    build_product_action_hash,
)


class ProductArtifactService:
    """Product-owned durable artifact and feedback surface.

    The workspace task runtime may still serve bounded compatibility routes,
    but Product routes must read and write durable ingestion contracts from
    this service. An unbound store is an explicit configuration failure rather
    than permission to fall back to process-local state.
    """

    _store: SQLiteDurableIngestionStore | None = None
    _security_product_action_guard: SecurityProductActionGuard | None = None

    @classmethod
    def configure(
        cls,
        *,
        store: SQLiteDurableIngestionStore | None,
        security_guard: SecurityProductActionGuard | None = None,
    ) -> None:
        cls._store = store
        cls._security_product_action_guard = security_guard

    @classmethod
    def configure_security_product_action_guard(
        cls,
        guard: SecurityProductActionGuard | None,
    ) -> None:
        cls._security_product_action_guard = guard

    @classmethod
    def get_artifact(cls, artifact_id: str, *, principal_id: str = "") -> dict[str, Any]:
        record = cls._get_artifact_record(artifact_id)
        artifact = cls._artifact_from_record(record)
        cls._require_authorized_action(
            artifact=artifact,
            owner_id=record.owner_id,
            principal_id=principal_id,
            action="artifact.read",
        )
        citation_refs = [ref.model_dump(mode="json") for ref in artifact.citation_refs]
        if citation_refs:
            cls._require_citation_refs_authorized(
                artifact=artifact,
                owner_id=record.owner_id,
                principal_id=principal_id,
            )
        return {
            "artifact": artifact.model_dump(mode="json"),
            "content": record.content,
            "citation_refs": citation_refs,
            "download": {
                "url": f"/api/v1/product/artifacts/{artifact_id}/download",
                "filename": cls._artifact_filename(record),
                "media_type": "text/markdown; charset=utf-8",
                "policy": artifact.download_policy,
            },
        }

    @classmethod
    def download_artifact(cls, artifact_id: str, *, principal_id: str = "") -> dict[str, Any]:
        record = cls._get_artifact_record(artifact_id)
        artifact = cls._artifact_from_record(record)
        cls._require_authorized_action(
            artifact=artifact,
            owner_id=record.owner_id,
            principal_id=principal_id,
            action="artifact.download",
        )
        return {
            "artifact": artifact.model_dump(mode="json"),
            "content": record.content,
            "filename": cls._artifact_filename(record),
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
    ) -> dict[str, Any]:
        store = cls._require_store()
        try:
            task = store.get_workspace_task(task_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Workspace task not found") from exc

        feedback = FeedbackContract(
            feedback_id=f"feedback_{uuid4().hex[:12]}",
            task_id=task_id,
            rating=rating,
            label=label,
            comment=comment,
            dataset_candidate=dataset_candidate,
            created_at=str(time.time()),
        )
        store.save_feedback(
            FeedbackRecord(
                feedback_id=feedback.feedback_id,
                task_id=feedback.task_id,
                rating=feedback.rating,
                label=feedback.label,
                comment=feedback.comment,
                dataset_candidate=feedback.dataset_candidate,
                payload={"feedback": feedback.model_dump(mode="json")},
            )
        )
        store.save_task_event(
            TaskEventRecord(
                event_id=f"event_{uuid4().hex[:12]}",
                task_id=task.task_id,
                trace_id=task.trace_id or "",
                event_type="feedback_received",
                timestamp=time.time(),
                payload={
                    "feedback_id": feedback.feedback_id,
                    "dataset_candidate": dataset_candidate,
                },
            )
        )
        return feedback.model_dump(mode="json")

    @classmethod
    def _require_store(cls) -> SQLiteDurableIngestionStore:
        if cls._store is None:
            raise HTTPException(status_code=503, detail="PRODUCT_ARTIFACT_OWNER_NOT_BOUND")
        return cls._store

    @classmethod
    def _get_artifact_record(cls, artifact_id: str) -> ArtifactRecord:
        try:
            return cls._require_store().get_artifact(artifact_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Product artifact not found") from exc

    @staticmethod
    def _artifact_from_record(record: ArtifactRecord) -> ArtifactContract:
        artifact_payload = dict(record.payload.get("artifact") or {})
        artifact_payload = {
            "workspace_id": record.workspace_id,
            "owner": record.owner_id,
            "trace_id": record.trace_id,
            "artifact_id": record.artifact_id,
            "task_id": record.task_id,
            "kind": record.kind,
            "uri": record.uri,
            "hash": record.content_sha256,
            **artifact_payload,
        }
        try:
            return ArtifactContract.model_validate(artifact_payload)
        except Exception as exc:
            raise HTTPException(status_code=500, detail="PRODUCT_ARTIFACT_RECORD_INVALID") from exc

    @classmethod
    def _require_authorized_action(
        cls,
        *,
        artifact: ArtifactContract,
        owner_id: str | None,
        principal_id: str,
        action: str,
    ) -> None:
        if cls._security_product_action_guard is None:
            return
        actor = principal_id or artifact.owner or owner_id or ""
        resource_ref = f"workspace-artifact:{artifact.artifact_id}"
        request = SecurityProductActionRequest(
            tenant_id=artifact.workspace_id,
            workspace_id=artifact.workspace_id,
            principal_id=actor,
            action=action,
            resource_ref=resource_ref,
            decision_id=f"authorization-decision:{action}:{artifact.artifact_id}",
            prepared_action_hash=build_product_action_hash(
                tenant_id=artifact.workspace_id,
                workspace_id=artifact.workspace_id,
                principal_id=actor,
                action=action,
                resource_ref=resource_ref,
            ),
        )
        try:
            cls._security_product_action_guard.require_authorized_action(request)
        except SecurityProductActionDenied as exc:
            raise HTTPException(status_code=403, detail=str(exc) or "Security authorization denied") from exc

    @classmethod
    def _require_citation_refs_authorized(
        cls,
        *,
        artifact: ArtifactContract,
        owner_id: str | None,
        principal_id: str,
    ) -> None:
        if cls._security_product_action_guard is None:
            return
        actor = principal_id or artifact.owner or owner_id or ""
        resource_ref = f"workspace-artifact:{artifact.artifact_id}:citations"
        action = "citation.read"
        request = SecurityProductActionRequest(
            tenant_id=artifact.workspace_id,
            workspace_id=artifact.workspace_id,
            principal_id=actor,
            action=action,
            resource_ref=resource_ref,
            decision_id=f"authorization-decision:{action}:{artifact.artifact_id}",
            prepared_action_hash=build_product_action_hash(
                tenant_id=artifact.workspace_id,
                workspace_id=artifact.workspace_id,
                principal_id=actor,
                action=action,
                resource_ref=resource_ref,
            ),
        )
        try:
            cls._security_product_action_guard.require_authorized_action(request)
        except SecurityProductActionDenied as exc:
            raise HTTPException(status_code=403, detail=str(exc) or "Security authorization denied") from exc

    @classmethod
    def _artifact_filename(cls, record: ArtifactRecord) -> str:
        source = str(record.uri.rsplit("/", 1)[-1] or record.artifact_id)
        try:
            task = cls._require_store().get_workspace_task(record.task_id)
        except KeyError:
            task = None
        if task is not None:
            task_payload = dict(task.payload.get("task") or {})
            source = str(task_payload.get("goal") or source)
        slug = source.replace("_", "-").replace(" ", "-").lower()
        safe_slug = "".join(ch for ch in slug if ch.isalnum() or ch in {"-", "."}).strip("-")
        return f"{safe_slug or record.artifact_id}.md"


__all__ = ["ProductArtifactService"]
