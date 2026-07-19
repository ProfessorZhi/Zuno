from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Engine, text
from sqlalchemy.engine import Connection

from zuno.platform.contracts import canonical_json, canonical_sha256
from zuno.platform.security import SandboxAuditEvent, redact_sensitive_payload
from zuno.platform.observability.trace_eval import ZunoSpan, ZunoSpanBuilder


class ObservabilityPersistenceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ObservabilityEnvelopeReceipt:
    envelope_id: str
    tenant_id: str
    trace_id: str
    status: str
    payload_hash: str


@dataclass(frozen=True, slots=True)
class ObservabilityTraceReceipt:
    trace_id: str
    tenant_id: str
    trace_hash: str


@dataclass(frozen=True, slots=True)
class ObservabilitySpanReceipt:
    span_id: str
    trace_id: str
    span_hash: str


@dataclass(frozen=True, slots=True)
class ObservabilityRuntimeEventReceipt:
    event_id: str
    trace_id: str
    stream_id: str
    sequence: int
    payload_hash: str


@dataclass(frozen=True, slots=True)
class ObservabilityAuditReceipt:
    audit_id: str
    trace_id: str
    sequence: int
    audit_hash: str


@dataclass(frozen=True, slots=True)
class ObservabilityWatermarkReceipt:
    watermark_id: str
    stream_id: str
    contiguous_sequence: int
    max_seen_sequence: int
    freshness_status: str


@dataclass(frozen=True, slots=True)
class ObservabilityDeadLetterReceipt:
    dead_letter_id: str
    source_ref: str
    reason_code: str
    payload_hash: str


@dataclass(frozen=True, slots=True)
class ObservabilityTimelineRecord:
    event_id: str
    stream_id: str
    sequence: int
    event_type: str
    redacted_payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ObservabilityFreshnessRecord:
    trace_id: str
    stream_id: str
    contiguous_sequence: int
    max_seen_sequence: int
    freshness_status: str
    open_gap_count: int
    dead_letter_count: int


class PostgresObservabilityRuntimeAdapter:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self._span_builder = ZunoSpanBuilder()

    def record_span(self, span: ZunoSpan) -> ObservabilityRuntimeEventReceipt:
        tenant_id = span.session_id or span.thread_id or span.task_id
        workspace_id = span.session_id or tenant_id
        with ObservabilityUnitOfWork(self.engine) as repo:
            repo.record_trace(
                trace_id=span.trace_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                root_run_id=span.run_id,
            )
            repo.record_span(
                span_id=span.run_id,
                trace_id=span.trace_id,
                tenant_id=tenant_id,
                span_kind=span.span_kind.value,
                name=span.name,
                parent_span_id=span.parent_run_id,
                status="failed" if span.error else "completed",
            )
            receipt = repo.record_runtime_event(
                event_id=f"event:{span.trace_id}:{span.run_id}",
                tenant_id=tenant_id,
                trace_id=span.trace_id,
                span_id=span.run_id,
                stream_id=f"trace:{span.trace_id}",
                sequence=1,
                event_type=f"span.{span.span_kind.value}",
                payload=span.to_otel_span(),
            )
            repo.record_audit(
                audit_id=f"audit:{span.trace_id}:{span.run_id}",
                tenant_id=tenant_id,
                trace_id=span.trace_id,
                sequence=1,
                previous_hash="0" * 64,
                payload={
                    "span_id": span.run_id,
                    "span_kind": span.span_kind.value,
                    "policy_decision": span.policy_decision,
                },
            )
            return receipt

    def record_security_audit(
        self,
        audit: SandboxAuditEvent,
        *,
        run_id: str,
        parent_run_id: str | None = None,
    ) -> ObservabilityRuntimeEventReceipt:
        span = self._span_builder.from_security_audit(
            audit,
            run_id=run_id,
            parent_run_id=parent_run_id,
        )
        return self.record_span(span)


class ObservabilityUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self._active = False

    def __enter__(self) -> ObservabilityRepository:
        if self._active:
            raise RuntimeError("ObservabilityUnitOfWork cannot be nested")
        self._active = True
        self._context = self.engine.begin()
        try:
            self.connection = self._context.__enter__()
            return ObservabilityRepository(self.connection)
        except BaseException:
            self._active = False
            raise

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            self._context.__exit__(exc_type, exc, tb)
        finally:
            self._active = False


class ObservabilityRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def ingest_envelope(
        self,
        *,
        envelope_id: str,
        tenant_id: str,
        workspace_id: str,
        trace_id: str,
        schema_ref: str,
        schema_version: str,
        producer: str,
        scope_ref: str,
        effective_security_epoch_ref: str,
        payload: dict[str, Any],
    ) -> ObservabilityEnvelopeReceipt:
        self._require_boundary(tenant_id=tenant_id, workspace_id=workspace_id, trace_id=trace_id)
        redacted_payload = redact_sensitive_payload(payload)
        payload_hash = canonical_sha256(redacted_payload)
        redaction_hash = canonical_sha256({"schema_ref": schema_ref, "payload": redacted_payload})
        existing = self.connection.execute(
            text(
                """
                SELECT envelope_id
                FROM observability_ingest_envelopes
                WHERE tenant_id = :tenant_id
                  AND schema_ref = :schema_ref
                  AND payload_hash = :payload_hash
                """
            ),
            {"tenant_id": tenant_id, "schema_ref": schema_ref, "payload_hash": payload_hash},
        ).first()
        if existing is not None:
            return ObservabilityEnvelopeReceipt(str(existing.envelope_id), tenant_id, trace_id, "duplicate", payload_hash)
        self.connection.execute(
            text(
                """
                INSERT INTO observability_ingest_envelopes(
                    envelope_id, tenant_id, workspace_id, trace_id, schema_ref,
                    schema_version, producer, scope_ref, effective_security_epoch_ref,
                    payload_hash, redaction_hash, payload, status, quarantine_reason
                ) VALUES (
                    :envelope_id, :tenant_id, :workspace_id, :trace_id, :schema_ref,
                    :schema_version, :producer, :scope_ref, :effective_security_epoch_ref,
                    :payload_hash, :redaction_hash, CAST(:payload AS jsonb), 'accepted', NULL
                )
                """
            ),
            {
                "envelope_id": envelope_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "trace_id": trace_id,
                "schema_ref": schema_ref,
                "schema_version": schema_version,
                "producer": producer,
                "scope_ref": scope_ref,
                "effective_security_epoch_ref": effective_security_epoch_ref,
                "payload_hash": payload_hash,
                "redaction_hash": redaction_hash,
                "payload": canonical_json(redacted_payload),
            },
        )
        return ObservabilityEnvelopeReceipt(envelope_id, tenant_id, trace_id, "accepted", payload_hash)

    def record_trace(
        self,
        *,
        trace_id: str,
        tenant_id: str,
        workspace_id: str,
        root_run_id: str,
        lifecycle_state: str = "runtime_observed",
        terminal: bool = False,
    ) -> ObservabilityTraceReceipt:
        trace_hash = canonical_sha256(
            {
                "trace_id": trace_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "root_run_id": root_run_id,
                "lifecycle_state": lifecycle_state,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO observability_traces(
                    trace_id, tenant_id, workspace_id, root_run_id,
                    lifecycle_state, terminal, trace_hash, completed_at
                ) VALUES (
                    :trace_id, :tenant_id, :workspace_id, :root_run_id,
                    :lifecycle_state, :terminal, :trace_hash,
                    CASE WHEN :terminal THEN now() ELSE NULL END
                )
                ON CONFLICT (trace_id) DO UPDATE
                SET lifecycle_state = EXCLUDED.lifecycle_state,
                    terminal = observability_traces.terminal OR EXCLUDED.terminal,
                    completed_at = CASE
                        WHEN observability_traces.completed_at IS NULL AND EXCLUDED.terminal
                        THEN now()
                        ELSE observability_traces.completed_at
                    END
                """
            ),
            {
                "trace_id": trace_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "root_run_id": root_run_id,
                "lifecycle_state": lifecycle_state,
                "terminal": terminal,
                "trace_hash": trace_hash,
            },
        )
        return ObservabilityTraceReceipt(trace_id, tenant_id, trace_hash)

    def record_span(
        self,
        *,
        span_id: str,
        trace_id: str,
        tenant_id: str,
        span_kind: str,
        name: str,
        parent_span_id: str | None = None,
        causation_id: str | None = None,
        status: str = "open",
    ) -> ObservabilitySpanReceipt:
        span_hash = canonical_sha256(
            {
                "span_id": span_id,
                "trace_id": trace_id,
                "tenant_id": tenant_id,
                "parent_span_id": parent_span_id,
                "causation_id": causation_id,
                "span_kind": span_kind,
                "name": name,
                "status": status,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO observability_spans(
                    span_id, trace_id, tenant_id, parent_span_id, causation_id,
                    span_kind, name, status, span_hash, ended_at
                ) VALUES (
                    :span_id, :trace_id, :tenant_id, :parent_span_id, :causation_id,
                    :span_kind, :name, :status, :span_hash,
                    CASE WHEN :terminal_status THEN now() ELSE NULL END
                )
                ON CONFLICT (span_id) DO UPDATE
                SET status = EXCLUDED.status,
                    ended_at = CASE
                        WHEN observability_spans.ended_at IS NULL
                         AND EXCLUDED.status IN ('completed','failed')
                        THEN now()
                        ELSE observability_spans.ended_at
                    END
                """
            ),
            {
                "span_id": span_id,
                "trace_id": trace_id,
                "tenant_id": tenant_id,
                "parent_span_id": parent_span_id,
                "causation_id": causation_id,
                "span_kind": span_kind,
                "name": name,
                "status": status,
                "terminal_status": status in {"completed", "failed"},
                "span_hash": span_hash,
            },
        )
        return ObservabilitySpanReceipt(span_id, trace_id, span_hash)

    def record_runtime_event(
        self,
        *,
        event_id: str,
        tenant_id: str,
        trace_id: str,
        stream_id: str,
        sequence: int,
        event_type: str,
        payload: dict[str, Any],
        span_id: str | None = None,
    ) -> ObservabilityRuntimeEventReceipt:
        if sequence < 1:
            raise ObservabilityPersistenceError("observability event sequence must be positive")
        redacted_payload = redact_sensitive_payload(payload)
        payload_hash = canonical_sha256(redacted_payload)
        existing = self.connection.execute(
            text(
                """
                SELECT event_id, payload_hash
                FROM observability_runtime_events
                WHERE tenant_id = :tenant_id
                  AND stream_id = :stream_id
                  AND sequence = :sequence
                """
            ),
            {"tenant_id": tenant_id, "stream_id": stream_id, "sequence": sequence},
        ).first()
        if existing is not None:
            if str(existing.payload_hash) != payload_hash:
                self.record_dead_letter(
                    dead_letter_id=f"dead-letter:{event_id}",
                    tenant_id=tenant_id,
                    source_ref=event_id,
                    reason_code="duplicate_sequence_payload_mismatch",
                    payload=redacted_payload,
                )
            return ObservabilityRuntimeEventReceipt(str(existing.event_id), trace_id, stream_id, sequence, str(existing.payload_hash))
        self.connection.execute(
            text(
                """
                INSERT INTO observability_runtime_events(
                    event_id, tenant_id, trace_id, span_id, stream_id, sequence,
                    event_type, payload_hash, redacted_payload, status
                ) VALUES (
                    :event_id, :tenant_id, :trace_id, :span_id, :stream_id, :sequence,
                    :event_type, :payload_hash, CAST(:redacted_payload AS jsonb), 'accepted'
                )
                """
            ),
            {
                "event_id": event_id,
                "tenant_id": tenant_id,
                "trace_id": trace_id,
                "span_id": span_id,
                "stream_id": stream_id,
                "sequence": sequence,
                "event_type": event_type,
                "payload_hash": payload_hash,
                "redacted_payload": canonical_json(redacted_payload),
            },
        )
        self.update_watermark(
            tenant_id=tenant_id,
            projection_id="runtime-events",
            stream_id=stream_id,
            observed_sequence=sequence,
        )
        return ObservabilityRuntimeEventReceipt(event_id, trace_id, stream_id, sequence, payload_hash)

    def record_audit(
        self,
        *,
        audit_id: str,
        tenant_id: str,
        trace_id: str,
        sequence: int,
        previous_hash: str,
        payload: dict[str, Any],
    ) -> ObservabilityAuditReceipt:
        if sequence < 1:
            raise ObservabilityPersistenceError("audit sequence must be positive")
        redacted_payload = redact_sensitive_payload(payload)
        payload_hash = canonical_sha256(redacted_payload)
        audit_hash = canonical_sha256(
            {
                "audit_id": audit_id,
                "trace_id": trace_id,
                "sequence": sequence,
                "previous_hash": previous_hash,
                "payload_hash": payload_hash,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO observability_audit_records(
                    audit_id, tenant_id, trace_id, sequence, previous_hash,
                    audit_hash, payload_hash, redacted_payload, accepted
                ) VALUES (
                    :audit_id, :tenant_id, :trace_id, :sequence, :previous_hash,
                    :audit_hash, :payload_hash, CAST(:redacted_payload AS jsonb), true
                )
                """
            ),
            {
                "audit_id": audit_id,
                "tenant_id": tenant_id,
                "trace_id": trace_id,
                "sequence": sequence,
                "previous_hash": previous_hash,
                "audit_hash": audit_hash,
                "payload_hash": payload_hash,
                "redacted_payload": canonical_json(redacted_payload),
            },
        )
        return ObservabilityAuditReceipt(audit_id, trace_id, sequence, audit_hash)

    def update_watermark(
        self,
        *,
        tenant_id: str,
        projection_id: str,
        stream_id: str,
        observed_sequence: int,
    ) -> ObservabilityWatermarkReceipt:
        watermark_id = f"watermark:{tenant_id}:{projection_id}:{stream_id}"
        row = self.connection.execute(
            text(
                """
                SELECT contiguous_sequence, max_seen_sequence
                FROM observability_projection_watermarks
                WHERE watermark_id = :watermark_id
                FOR UPDATE
                """
            ),
            {"watermark_id": watermark_id},
        ).first()
        if row is None:
            contiguous = observed_sequence if observed_sequence == 1 else 0
            max_seen = observed_sequence
        else:
            contiguous = int(row.contiguous_sequence)
            max_seen = max(int(row.max_seen_sequence), observed_sequence)
        contiguous = self._contiguous_sequence(
            tenant_id=tenant_id,
            stream_id=stream_id,
            start_sequence=contiguous,
            max_seen_sequence=max_seen,
        )
        freshness_status = "fresh" if contiguous == max_seen else "gap"
        self._fill_gaps(
            tenant_id=tenant_id,
            stream_id=stream_id,
            contiguous_sequence=contiguous,
        )
        if freshness_status == "gap":
            self.record_gap(
                tenant_id=tenant_id,
                stream_id=stream_id,
                missing_after_sequence=contiguous,
                missing_before_sequence=max_seen,
            )
        self.connection.execute(
            text(
                """
                INSERT INTO observability_projection_watermarks(
                    watermark_id, tenant_id, projection_id, stream_id,
                    contiguous_sequence, max_seen_sequence, freshness_status
                ) VALUES (
                    :watermark_id, :tenant_id, :projection_id, :stream_id,
                    :contiguous_sequence, :max_seen_sequence, :freshness_status
                )
                ON CONFLICT (watermark_id) DO UPDATE
                SET contiguous_sequence = EXCLUDED.contiguous_sequence,
                    max_seen_sequence = EXCLUDED.max_seen_sequence,
                    freshness_status = EXCLUDED.freshness_status,
                    updated_at = now()
                """
            ),
            {
                "watermark_id": watermark_id,
                "tenant_id": tenant_id,
                "projection_id": projection_id,
                "stream_id": stream_id,
                "contiguous_sequence": contiguous,
                "max_seen_sequence": max_seen,
                "freshness_status": freshness_status,
            },
        )
        return ObservabilityWatermarkReceipt(watermark_id, stream_id, contiguous, max_seen, freshness_status)

    def trace_timeline(
        self,
        *,
        tenant_id: str,
        trace_id: str,
    ) -> tuple[ObservabilityTimelineRecord, ...]:
        rows = self.connection.execute(
            text(
                """
                SELECT event_id, stream_id, sequence, event_type, redacted_payload
                FROM observability_runtime_events
                WHERE tenant_id = :tenant_id
                  AND trace_id = :trace_id
                ORDER BY stream_id, sequence, event_id
                """
            ),
            {"tenant_id": tenant_id, "trace_id": trace_id},
        ).all()
        return tuple(
            ObservabilityTimelineRecord(
                event_id=str(row.event_id),
                stream_id=str(row.stream_id),
                sequence=int(row.sequence),
                event_type=str(row.event_type),
                redacted_payload=dict(row.redacted_payload),
            )
            for row in rows
        )

    def projection_freshness(
        self,
        *,
        tenant_id: str,
        trace_id: str,
        stream_id: str,
        projection_id: str = "runtime-events",
    ) -> ObservabilityFreshnessRecord:
        watermark_id = f"watermark:{tenant_id}:{projection_id}:{stream_id}"
        row = self.connection.execute(
            text(
                """
                SELECT contiguous_sequence, max_seen_sequence, freshness_status
                FROM observability_projection_watermarks
                WHERE watermark_id = :watermark_id
                """
            ),
            {"watermark_id": watermark_id},
        ).first()
        gap_count = int(
            self.connection.execute(
                text(
                    """
                    SELECT count(*)
                    FROM observability_gaps
                    WHERE tenant_id = :tenant_id
                      AND stream_id = :stream_id
                      AND status = 'open'
                    """
                ),
                {"tenant_id": tenant_id, "stream_id": stream_id},
            ).scalar_one()
        )
        dead_letter_count = int(
            self.connection.execute(
                text(
                    """
                    SELECT count(*)
                    FROM observability_dead_letters
                    WHERE tenant_id = :tenant_id
                      AND status = 'open'
                    """
                ),
                {"tenant_id": tenant_id},
            ).scalar_one()
        )
        if row is None:
            return ObservabilityFreshnessRecord(trace_id, stream_id, 0, 0, "stale", gap_count, dead_letter_count)
        return ObservabilityFreshnessRecord(
            trace_id=trace_id,
            stream_id=stream_id,
            contiguous_sequence=int(row.contiguous_sequence),
            max_seen_sequence=int(row.max_seen_sequence),
            freshness_status=str(row.freshness_status),
            open_gap_count=gap_count,
            dead_letter_count=dead_letter_count,
        )

    def dead_letters(
        self,
        *,
        tenant_id: str,
    ) -> tuple[ObservabilityDeadLetterReceipt, ...]:
        rows = self.connection.execute(
            text(
                """
                SELECT dead_letter_id, source_ref, reason_code, payload_hash
                FROM observability_dead_letters
                WHERE tenant_id = :tenant_id
                  AND status = 'open'
                ORDER BY created_at, dead_letter_id
                """
            ),
            {"tenant_id": tenant_id},
        ).all()
        return tuple(
            ObservabilityDeadLetterReceipt(
                dead_letter_id=str(row.dead_letter_id),
                source_ref=str(row.source_ref),
                reason_code=str(row.reason_code),
                payload_hash=str(row.payload_hash),
            )
            for row in rows
        )

    def record_gap(
        self,
        *,
        tenant_id: str,
        stream_id: str,
        missing_after_sequence: int,
        missing_before_sequence: int,
    ) -> None:
        if missing_before_sequence <= missing_after_sequence:
            return
        gap_id = f"gap:{tenant_id}:{stream_id}:{missing_after_sequence}:{missing_before_sequence}"
        self.connection.execute(
            text(
                """
                INSERT INTO observability_gaps(
                    gap_id, tenant_id, stream_id, missing_after_sequence,
                    missing_before_sequence, status
                ) VALUES (
                    :gap_id, :tenant_id, :stream_id, :missing_after_sequence,
                    :missing_before_sequence, 'open'
                )
                ON CONFLICT (gap_id) DO NOTHING
                """
            ),
            {
                "gap_id": gap_id,
                "tenant_id": tenant_id,
                "stream_id": stream_id,
                "missing_after_sequence": missing_after_sequence,
                "missing_before_sequence": missing_before_sequence,
            },
        )

    def record_dead_letter(
        self,
        *,
        dead_letter_id: str,
        tenant_id: str,
        source_ref: str,
        reason_code: str,
        payload: dict[str, Any],
    ) -> ObservabilityDeadLetterReceipt:
        redacted_payload = redact_sensitive_payload(payload)
        payload_hash = canonical_sha256(redacted_payload)
        self.connection.execute(
            text(
                """
                INSERT INTO observability_dead_letters(
                    dead_letter_id, tenant_id, source_ref, reason_code,
                    payload_hash, redacted_payload, status
                ) VALUES (
                    :dead_letter_id, :tenant_id, :source_ref, :reason_code,
                    :payload_hash, CAST(:redacted_payload AS jsonb), 'open'
                )
                ON CONFLICT (dead_letter_id) DO NOTHING
                """
            ),
            {
                "dead_letter_id": dead_letter_id,
                "tenant_id": tenant_id,
                "source_ref": source_ref,
                "reason_code": reason_code,
                "payload_hash": payload_hash,
                "redacted_payload": canonical_json(redacted_payload),
            },
        )
        return ObservabilityDeadLetterReceipt(dead_letter_id, source_ref, reason_code, payload_hash)

    def _require_boundary(self, *, tenant_id: str, workspace_id: str, trace_id: str) -> None:
        if not tenant_id.strip() or not workspace_id.strip() or not trace_id.strip():
            raise ObservabilityPersistenceError("tenant_id, workspace_id and trace_id are required")

    def _contiguous_sequence(
        self,
        *,
        tenant_id: str,
        stream_id: str,
        start_sequence: int,
        max_seen_sequence: int,
    ) -> int:
        rows = self.connection.execute(
            text(
                """
                SELECT sequence
                FROM observability_runtime_events
                WHERE tenant_id = :tenant_id
                  AND stream_id = :stream_id
                  AND sequence > :start_sequence
                  AND sequence <= :max_seen_sequence
                ORDER BY sequence
                """
            ),
            {
                "tenant_id": tenant_id,
                "stream_id": stream_id,
                "start_sequence": start_sequence,
                "max_seen_sequence": max_seen_sequence,
            },
        ).all()
        contiguous = start_sequence
        for row in rows:
            sequence = int(row.sequence)
            if sequence == contiguous + 1:
                contiguous = sequence
                continue
            if sequence > contiguous + 1:
                break
        return contiguous

    def _fill_gaps(
        self,
        *,
        tenant_id: str,
        stream_id: str,
        contiguous_sequence: int,
    ) -> None:
        self.connection.execute(
            text(
                """
                UPDATE observability_gaps
                SET status = 'filled',
                    filled_at = now()
                WHERE tenant_id = :tenant_id
                  AND stream_id = :stream_id
                  AND status = 'open'
                  AND missing_before_sequence <= :contiguous_sequence
                """
            ),
            {
                "tenant_id": tenant_id,
                "stream_id": stream_id,
                "contiguous_sequence": contiguous_sequence,
            },
        )


__all__ = [
    "ObservabilityAuditReceipt",
    "ObservabilityDeadLetterReceipt",
    "ObservabilityEnvelopeReceipt",
    "ObservabilityFreshnessRecord",
    "ObservabilityPersistenceError",
    "PostgresObservabilityRuntimeAdapter",
    "ObservabilityRepository",
    "ObservabilityRuntimeEventReceipt",
    "ObservabilitySpanReceipt",
    "ObservabilityTraceReceipt",
    "ObservabilityTimelineRecord",
    "ObservabilityUnitOfWork",
    "ObservabilityWatermarkReceipt",
]
