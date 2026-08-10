from __future__ import annotations

import pytest
from fastapi import HTTPException

from zuno.api.dto.workspace import ArtifactContract, WorkspaceCitationRef
from zuno.api.services.product import ProductService
from zuno.knowledge.storage import (
    ArtifactRecord,
    SQLiteDurableIngestionStore,
    WorkspaceTaskRecord,
)


class _RecordingProductActionGuard:
    def __init__(self) -> None:
        self.actions: list[str] = []

    def require_authorized_action(self, request) -> None:
        self.actions.append(request.action)


def test_product_artifact_and_feedback_are_durable_and_product_owned(tmp_path) -> None:
    db_path = tmp_path / "product-surface.db"
    store = SQLiteDurableIngestionStore(db_path)
    guard = _RecordingProductActionGuard()
    ProductService.configure_product_artifact_store(store, security_guard=guard)
    try:
        store.save_workspace_task(
            WorkspaceTaskRecord(
                task_id="task-product-1",
                workspace_id="workspace-a",
                owner_id="principal-a",
                status="completed",
                trace_id="trace-product-1",
                payload={"task": {"goal": "Durable product artifact"}},
            )
        )
        artifact = ArtifactContract(
            workspace_id="workspace-a",
            owner="principal-a",
            status="ready",
            trace_id="trace-product-1",
            artifact_id="artifact-product-1",
            task_id="task-product-1",
            kind="answer",
            uri="memory://workspace/workspace-a/artifacts/task-product-1",
            hash="artifact-hash",
            citation_refs=[
                WorkspaceCitationRef(
                    citation_id="citation-1",
                    evidence_id="evidence-1",
                    document_id="document-1",
                    block_id="block-1",
                    source_ref="source-1",
                )
            ],
        )
        store.save_artifact(
            ArtifactRecord(
                artifact_id=artifact.artifact_id,
                task_id=artifact.task_id,
                workspace_id=artifact.workspace_id,
                owner_id=artifact.owner,
                kind=artifact.kind,
                uri=artifact.uri,
                content="# durable artifact",
                content_sha256="content-hash",
                trace_id=artifact.trace_id,
                payload={"artifact": artifact.model_dump(mode="json")},
            )
        )

        artifact_payload = ProductService.get_artifact(
            "artifact-product-1",
            principal_id="principal-a",
        )
        assert artifact_payload["content"] == "# durable artifact"
        assert artifact_payload["download"]["url"] == "/api/v1/product/artifacts/artifact-product-1/download"
        assert artifact_payload["citation_refs"][0]["citation_id"] == "citation-1"
        assert guard.actions == ["artifact.read", "citation.read"]

        feedback = ProductService.record_feedback(
            task_id="task-product-1",
            rating=5,
            label="helpful",
            comment="durable",
            dataset_candidate=True,
        )
        assert feedback["task_id"] == "task-product-1"
        assert store.list_feedback_for_task("task-product-1")[0].payload["feedback"]["comment"] == "durable"
        assert store.list_task_events("task-product-1")[0].event_type == "feedback_received"

        ProductService.configure_product_artifact_store(SQLiteDurableIngestionStore(db_path))
        restored = ProductService.download_artifact(
            "artifact-product-1",
            principal_id="principal-a",
        )
        assert restored["content"] == "# durable artifact"
    finally:
        ProductService.configure_product_artifact_store(None)


def test_product_artifact_surface_fails_closed_without_durable_owner() -> None:
    ProductService.configure_product_artifact_store(None)
    with pytest.raises(HTTPException) as exc_info:
        ProductService.get_artifact("artifact-unbound", principal_id="principal-a")
    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "PRODUCT_ARTIFACT_OWNER_NOT_BOUND"
