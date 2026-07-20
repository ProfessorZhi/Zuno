from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Literal

from pydantic import BaseModel, Field

from .contracts import ParseDocumentRequest, ParseDocumentResult, ParseJobSnapshot
from .gateway import ParseGateway
from .lease import ParseAttemptLeaseReceipt, ParseAttemptLeaseRuntime


ParseControlState = Literal[
    "planned",
    "queued",
    "leased",
    "running",
    "succeeded",
    "failed",
    "cancelled",
    "dead_letter",
]


class ParseControlReceipt(BaseModel):
    parse_plan_id: str
    parse_job_id: str | None = None
    parse_attempt_id: str | None = None
    workspace_id: str
    document_id: str
    state: ParseControlState
    idempotency_key: str
    worker_id: str | None = None
    fencing_token: int | None = None
    lease: ParseAttemptLeaseReceipt | None = None
    snapshot: ParseJobSnapshot | None = None
    terminal_status: str | None = None
    retry_exhausted: bool = False
    cancel_reason: str | None = None
    history: list[str] = Field(default_factory=list)


@dataclass
class ParseControlRuntime:
    lease_runtime: ParseAttemptLeaseRuntime | None = None
    lease_ttl_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.lease_runtime is None:
            self.lease_runtime = ParseAttemptLeaseRuntime()

    def plan(self, request: ParseDocumentRequest, *, idempotency_key: str) -> ParseControlReceipt:
        return ParseControlReceipt(
            parse_plan_id=f"plan_{idempotency_key[:24]}",
            workspace_id=request.workspace_id,
            document_id=request.document_id,
            state="planned",
            idempotency_key=idempotency_key,
            history=["planned"],
        )

    def queue(self, receipt: ParseControlReceipt) -> ParseControlReceipt:
        return receipt.model_copy(update={"state": "queued", "history": [*receipt.history, "queued"]})

    def lease(
        self,
        receipt: ParseControlReceipt,
        *,
        worker_id: str,
        now: float | None = None,
    ) -> ParseControlReceipt:
        if receipt.state != "queued":
            raise ValueError(f"parse control can only lease queued jobs, got {receipt.state}")
        lease = self.lease_runtime.claim(
            parse_job_id=receipt.parse_plan_id,
            worker_id=worker_id,
            attempt_no=1,
            now=time.time() if now is None else now,
            ttl_seconds=self.lease_ttl_seconds,
        )
        return receipt.model_copy(
            update={
                "state": "leased",
                "worker_id": worker_id,
                "parse_attempt_id": lease.parse_attempt_id,
                "fencing_token": lease.fencing_token,
                "lease": lease,
                "history": [*receipt.history, "leased"],
            }
        )

    def run_once(
        self,
        request: ParseDocumentRequest,
        receipt: ParseControlReceipt,
        *,
        worker_id: str,
        fencing_token: int,
    ) -> tuple[ParseControlReceipt, ParseDocumentResult]:
        self._require_current_lease(receipt, worker_id=worker_id, fencing_token=fencing_token)
        running = receipt.model_copy(update={"state": "running", "history": [*receipt.history, "running"]})
        result = ParseGateway.submit_parse_job(request)
        snapshot = ParseGateway.get_job_snapshot(result.job_id)
        terminal_state = self._terminal_state(result.status)
        lease = running.lease
        if lease is not None and terminal_state == "succeeded":
            lease = self.lease_runtime.commit_if_current(
                lease,
                worker_id=worker_id,
                fencing_token=fencing_token,
                idempotency_key=running.idempotency_key,
            )
        return (
            running.model_copy(
                update={
                    "state": terminal_state,
                    "parse_job_id": result.job_id,
                    "parse_attempt_id": snapshot.parse_attempt_id,
                    "snapshot": snapshot,
                    "lease": lease,
                    "terminal_status": result.status,
                    "cancel_reason": result.failure.reason if result.status == "cancelled" and result.failure else None,
                    "history": [*running.history, terminal_state],
                }
            ),
            result,
        )

    def run_to_dead_letter(
        self,
        request: ParseDocumentRequest,
        receipt: ParseControlReceipt,
        *,
        worker_id: str,
        fencing_token: int,
    ) -> tuple[ParseControlReceipt, ParseDocumentResult]:
        controlled, result = self.run_once(
            request,
            receipt,
            worker_id=worker_id,
            fencing_token=fencing_token,
        )
        while result.status == "failed":
            result = ParseGateway.retry_parse_job(result.job_id, request)
            snapshot = ParseGateway.get_job_snapshot(result.job_id)
            controlled = controlled.model_copy(
                update={
                    "state": self._terminal_state(result.status),
                    "parse_job_id": result.job_id,
                    "parse_attempt_id": snapshot.parse_attempt_id,
                    "snapshot": snapshot,
                    "terminal_status": result.status,
                    "retry_exhausted": result.status == "dead_letter",
                    "history": [*controlled.history, "retrying", result.status],
                }
            )
            if result.status != "failed":
                break
        return controlled, result

    def _require_current_lease(
        self,
        receipt: ParseControlReceipt,
        *,
        worker_id: str,
        fencing_token: int,
    ) -> None:
        if receipt.state != "leased":
            raise ValueError(f"parse control can only run leased jobs, got {receipt.state}")
        if receipt.worker_id != worker_id or receipt.fencing_token != fencing_token:
            raise ValueError("parse control worker or fencing token is stale")

    @staticmethod
    def _terminal_state(status: str) -> ParseControlState:
        if status in {"succeeded", "failed", "cancelled", "dead_letter"}:
            return status  # type: ignore[return-value]
        if status == "blocked":
            return "failed"
        raise ValueError(f"parse status is not terminal for control runtime: {status}")


__all__ = ["ParseControlReceipt", "ParseControlRuntime", "ParseControlState"]
