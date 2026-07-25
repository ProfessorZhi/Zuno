from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from zuno.platform.database.product import ProductCommandSubmission, ProductUnitOfWork


@dataclass(frozen=True, slots=True)
class ProductRuntimeRequestResult:
    command_id: str
    receipt_id: str
    status: str


class ProductService:
    @staticmethod
    def submit_runtime_request(
        *,
        tenant_id: str,
        workspace_id: str,
        conversation_id: str,
        principal_id: str,
        active_agent_version_id: str,
        client_request_id: str,
        runtime_request_ref: str,
        raw_intent_ref: str,
        command_kind: str,
        payload: dict[str, Any],
    ) -> ProductRuntimeRequestResult:
        submission = ProductCommandSubmission(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            principal_id=principal_id,
            active_agent_version_id=active_agent_version_id,
            submission_id=f"submission:{client_request_id}",
            client_request_id=client_request_id,
            raw_intent_ref=raw_intent_ref,
            command_id=f"command:{client_request_id}",
            command_kind=command_kind,
            owner_module="Agent Core",
            runtime_request_ref=runtime_request_ref,
            payload=payload,
            journal_sequence_no=1,
            outbox_message_id=f"outbox:{client_request_id}",
        )
        from zuno.database import engine

        with ProductUnitOfWork(engine) as repo:
            receipt = repo.submit_command(submission)
        return ProductRuntimeRequestResult(
            command_id=receipt.command_id,
            receipt_id=receipt.receipt_id,
            status=receipt.status,
        )


__all__ = ["ProductRuntimeRequestResult", "ProductService"]
