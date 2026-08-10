from __future__ import annotations

from datetime import datetime
from typing import Any

from zuno.api.services.user import UserPayload
from zuno.knowledge.ingestion import PackageAProductionIngestionRuntime
from zuno.knowledge.storage import LocalObjectStore, SQLiteDurableIngestionStore

from zuno.api.services.product.runtime_engine import (
    ProductRuntimeMechanics,
    build_package_a_production_ingestion_runtime,
    resolve_package_a_upload_bucket,
)


class ProductIngestionService:
    """Application owner for Product files and ingestion jobs."""

    @staticmethod
    def configure_durable_ingestion(*, store, object_store, rehydrate: bool = False) -> None:
        ProductRuntimeMechanics.configure_durable_ingestion(
            store=store,
            object_store=object_store,
            rehydrate=rehydrate,
        )

    @staticmethod
    def configure_package_a_production_ingestion(**kwargs: Any) -> None:
        ProductRuntimeMechanics.configure_package_a_production_ingestion(**kwargs)

    @staticmethod
    def build_production_runtime(**kwargs: Any) -> PackageAProductionIngestionRuntime | None:
        return build_package_a_production_ingestion_runtime(**kwargs)

    @staticmethod
    def upload_bucket(settings: Any) -> str:
        return resolve_package_a_upload_bucket(settings)

    @staticmethod
    def register_file(
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
        content: str | None,
        deadline_at: datetime | None,
    ) -> dict[str, Any]:
        return ProductRuntimeMechanics.register_file(
            workspace_id=workspace_id,
            login_user=login_user,
            file_id=file_id,
            mime_type=mime_type,
            file_hash=file_hash,
            name=name,
            uri=uri,
            trace_id=trace_id,
            security_label=security_label,
            content=content,
            deadline_at=deadline_at,
        )

    @staticmethod
    def create_ingest_job(
        *,
        workspace_id: str,
        file_id: str,
        knowledge_space_id: str,
        session_id: str | None,
        trace_id: str | None,
    ) -> dict[str, Any]:
        return ProductRuntimeMechanics.create_ingest_job(
            workspace_id=workspace_id,
            file_id=file_id,
            knowledge_space_id=knowledge_space_id,
            session_id=session_id,
            trace_id=trace_id,
        )


__all__ = ["ProductIngestionService"]
