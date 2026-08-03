from __future__ import annotations

"""PHASE22 canonical ingestion run domain state — durable current-state owner.

``canonical_ingestion_runs`` is the single owner of the canonical ingestion
state machine. ``ingestion_outbox_events`` remains a delivery fact and is
written in the same unit of work as the state update, never used as the
current-state query source.

Every transition follows the contract:

    read current state (SELECT ... FOR UPDATE)
    -> validate transition (declarative state machine)
    -> update current fact (optimistic state_version guard)
    -> append history + outbox event
    -> commit one UoW

Terminal states reject ordinary overwrites; only explicitly designed retry /
reconciliation transitions may leave a failure state, and nothing may leave
``knowledge_version_ready``.
"""


from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from typing import Any

from sqlalchemy import Engine, text

# --- Canonical ingestion state machine (declarative, single fact source) -------

CANONICAL_STATE_ACCEPTED = "accepted"
CANONICAL_STATE_OBJECT_STAGED = "object_staged"
CANONICAL_STATE_OBJECT_COMMITTED = "object_committed"
CANONICAL_STATE_IR_READY = "canonical_ir_ready"
CANONICAL_STATE_KV_READY = "knowledge_version_ready"

CANONICAL_FAILURE_SECURITY_DENIED = "security_denied"
CANONICAL_FAILURE_CREDENTIAL_BLOCKED = "credential_blocked"
CANONICAL_FAILURE_OBJECT_STAGE_FAILED = "object_stage_failed"
CANONICAL_FAILURE_OBJECT_COMMIT_FAILED = "object_commit_failed"
CANONICAL_FAILURE_CANONICALIZATION_FAILED = "canonicalization_failed"
CANONICAL_FAILURE_RECONCILIATION_REQUIRED = "reconciliation_required"

# States this worker must never write (owned by downstream workers).
FORBIDDEN_CANONICAL_STATES = ("indexes_visible", "snapshot_activated")

CANONICAL_STATE_SEQUENCE: dict[str, int] = {
    CANONICAL_STATE_ACCEPTED: 1,
    CANONICAL_STATE_OBJECT_STAGED: 2,
    CANONICAL_STATE_OBJECT_COMMITTED: 3,
    CANONICAL_STATE_IR_READY: 4,
    CANONICAL_STATE_KV_READY: 5,
    CANONICAL_FAILURE_SECURITY_DENIED: 90,
    CANONICAL_FAILURE_CREDENTIAL_BLOCKED: 91,
    CANONICAL_FAILURE_OBJECT_STAGE_FAILED: 92,
    CANONICAL_FAILURE_OBJECT_COMMIT_FAILED: 93,
    CANONICAL_FAILURE_CANONICALIZATION_FAILED: 94,
    CANONICAL_FAILURE_RECONCILIATION_REQUIRED: 95,
}

CANONICAL_INGESTION_SUCCESS_STATES = (
    CANONICAL_STATE_ACCEPTED,
    CANONICAL_STATE_OBJECT_STAGED,
    CANONICAL_STATE_OBJECT_COMMITTED,
    CANONICAL_STATE_IR_READY,
    CANONICAL_STATE_KV_READY,
)
CANONICAL_INGESTION_FAILURE_STATES = (
    CANONICAL_FAILURE_SECURITY_DENIED,
    CANONICAL_FAILURE_CREDENTIAL_BLOCKED,
    CANONICAL_FAILURE_OBJECT_STAGE_FAILED,
    CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
    CANONICAL_FAILURE_CANONICALIZATION_FAILED,
    CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
)

# Declared transitions. Failure states only leave through explicitly designed
# retry transitions; ``reconciliation_required`` only resumes through the
# explicit reconciliation transitions; ``knowledge_version_ready`` is final.
CANONICAL_STATE_TRANSITIONS: dict[str, tuple[str, ...]] = {
    CANONICAL_STATE_ACCEPTED: (
        CANONICAL_STATE_OBJECT_STAGED,
        CANONICAL_FAILURE_SECURITY_DENIED,
        CANONICAL_FAILURE_CREDENTIAL_BLOCKED,
        CANONICAL_FAILURE_OBJECT_STAGE_FAILED,
    ),
    CANONICAL_STATE_OBJECT_STAGED: (
        CANONICAL_STATE_OBJECT_COMMITTED,
        CANONICAL_FAILURE_OBJECT_STAGE_FAILED,
        CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
    ),
    CANONICAL_STATE_OBJECT_COMMITTED: (
        CANONICAL_STATE_IR_READY,
        CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
        CANONICAL_FAILURE_CANONICALIZATION_FAILED,
        CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
    ),
    CANONICAL_STATE_IR_READY: (
        CANONICAL_STATE_KV_READY,
        CANONICAL_FAILURE_CANONICALIZATION_FAILED,
        CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
    ),
    # the only designed edge out of the success terminal is reconciliation
    CANONICAL_STATE_KV_READY: (CANONICAL_FAILURE_RECONCILIATION_REQUIRED,),
    CANONICAL_FAILURE_SECURITY_DENIED: (),
    CANONICAL_FAILURE_CREDENTIAL_BLOCKED: (),
    # explicit retry: plan and facts remain valid, only execution failed
    CANONICAL_FAILURE_OBJECT_STAGE_FAILED: (CANONICAL_STATE_OBJECT_STAGED,),
    CANONICAL_FAILURE_OBJECT_COMMIT_FAILED: (CANONICAL_STATE_OBJECT_COMMITTED,),
    # canonicalization runs from the object_committed checkpoint; retry re-parses
    CANONICAL_FAILURE_CANONICALIZATION_FAILED: (CANONICAL_STATE_OBJECT_COMMITTED,),
    # explicit reconciliation transitions after unknown side effects are
    # confirmed and facts are re-verified
    CANONICAL_FAILURE_RECONCILIATION_REQUIRED: (
        CANONICAL_STATE_OBJECT_STAGED,
        CANONICAL_STATE_OBJECT_COMMITTED,
        CANONICAL_STATE_IR_READY,
    ),
}


def validate_canonical_state_transition(from_state: str, to_state: str) -> None:
    """Declarative state machine guard; raises on illegal or forbidden moves."""
    if to_state in FORBIDDEN_CANONICAL_STATES:
        raise ValueError(
            f"canonical ingestion must not write {to_state!r}: it is owned by "
            "the index-visibility / snapshot-activation workers"
        )
    if from_state not in CANONICAL_STATE_TRANSITIONS:
        raise ValueError(f"unknown canonical ingestion state: {from_state!r}")
    if to_state not in CANONICAL_STATE_TRANSITIONS[from_state]:
        raise ValueError(
            f"illegal canonical ingestion transition: {from_state!r} -> {to_state!r}"
        )


def canonical_state_sequence(state: str) -> int:
    if state not in CANONICAL_STATE_SEQUENCE:
        raise ValueError(f"unknown canonical ingestion state: {state!r}")
    return CANONICAL_STATE_SEQUENCE[state]


def canonical_run_id(*, tenant_id: str, workspace_id: str, source_id: str) -> str:
    return f"canonical-ingest:{tenant_id}:{workspace_id}:{source_id}"


CANONICAL_INGESTION_STATE_EVENT_TYPE = "ingestion.canonical_ingestion.state_changed"

TERMINAL_SUCCESS_STATE = CANONICAL_STATE_KV_READY
TERMINAL_FAILURE_STATES = CANONICAL_INGESTION_FAILURE_STATES


class CanonicalRunStateError(RuntimeError):
    pass


class CanonicalRunStateConflict(CanonicalRunStateError):
    pass


class CanonicalRunStateTerminal(CanonicalRunStateError):
    pass


@dataclass(frozen=True, slots=True)
class CanonicalRunCurrentFact:
    run_id: str
    tenant_id: str
    workspace_id: str
    source_set_ref: str
    corpus_manifest_ref: str
    current_state: str
    state_version: int
    attempt_number: int
    knowledge_version_id: str | None
    last_error_code: str | None
    last_error_detail: str | None
    idempotency_key: str
    payload_hash: str
    created_at: Any | None = None
    updated_at: Any | None = None
    completed_at: Any | None = None


@dataclass(frozen=True, slots=True)
class CanonicalRunTransitionReceipt:
    run_id: str
    tenant_id: str
    from_state: str | None
    to_state: str
    state_version: int
    attempt_number: int
    outbox_event_id: str


def _bounded_id(prefix: str, value: str, budget: int) -> str:
    """Deterministic identifier that fits the persistence column width.

    When the candidate overflows, the whole candidate is digested so the
    result is always within ``budget`` regardless of prefix length.
    """
    candidate = f"{prefix}{value}"
    if len(candidate) <= budget:
        return candidate
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()
    return digest[:budget]


def canonical_state_event_id(*, run_id: str, state: str) -> str:
    return _bounded_id(
        f"outbox:{run_id}:{canonical_state_sequence(state):02d}:",
        state,
        budget=150,
    )


class CanonicalIngestionRunStore:
    """Atomic, tenant-scoped current-state store for canonical ingestion runs."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    # --- transitions -----------------------------------------------------------

    def ensure_run(
        self,
        *,
        run_id: str,
        tenant_id: str,
        workspace_id: str,
        source_set_ref: str,
        corpus_manifest_ref: str,
        idempotency_key: str,
        payload_hash: str,
    ) -> CanonicalRunTransitionReceipt | None:
        """Create the run row in ``accepted`` if absent; return None when it
        already exists (resume path: the durable checkpoint decides)."""
        with self.engine.begin() as connection:
            existing = connection.execute(
                text(
                    """
                    SELECT run_id FROM canonical_ingestion_runs
                    WHERE run_id = :run_id AND tenant_id = :tenant_id
                    """
                ),
                {"run_id": run_id, "tenant_id": tenant_id},
            ).first()
            if existing is not None:
                return None
            connection.execute(
                text(
                    """
                    INSERT INTO canonical_ingestion_runs(
                        run_id, tenant_id, workspace_id, source_set_ref,
                        corpus_manifest_ref, current_state, state_version,
                        attempt_number, idempotency_key, payload_hash
                    ) VALUES (
                        :run_id, :tenant_id, :workspace_id, :source_set_ref,
                        :corpus_manifest_ref, 'accepted', 1, 1,
                        :idempotency_key, :payload_hash
                    )
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "run_id": run_id,
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "source_set_ref": source_set_ref,
                    "corpus_manifest_ref": corpus_manifest_ref,
                    "idempotency_key": idempotency_key,
                    "payload_hash": payload_hash,
                },
            )
            return CanonicalRunTransitionReceipt(
                run_id=run_id,
                tenant_id=tenant_id,
                from_state=None,
                to_state="accepted",
                state_version=1,
                attempt_number=1,
                outbox_event_id=canonical_state_event_id(
                    run_id=run_id, state="accepted"
                ),
            )

    def transition(
        self,
        *,
        run_id: str,
        tenant_id: str,
        to_state: str,
        expected_from_state: str,
        attempt_number: int | None = None,
        source_id: str | None = None,
        source_hash: str | None = None,
        knowledge_version_id: str | None = None,
        last_error_code: str | None = None,
        last_error_detail: str | None = None,
        outbox_payload: dict[str, Any] | None = None,
    ) -> CanonicalRunTransitionReceipt:
        """Apply one state transition atomically.

        Guards: row must exist; current state must equal
        ``expected_from_state``; the transition must be declared legal; the
        current state must not be terminal for an ordinary overwrite; the
        state_version must match the locked row (optimistic version).
        """
        validate_canonical_state_transition(expected_from_state, to_state)
        with self.engine.begin() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT current_state, state_version, attempt_number,
                           knowledge_version_id, completed_at
                    FROM canonical_ingestion_runs
                    WHERE run_id = :run_id AND tenant_id = :tenant_id
                    FOR UPDATE
                    """
                ),
                {"run_id": run_id, "tenant_id": tenant_id},
            ).mappings().first()
            if row is None:
                raise CanonicalRunStateError(
                    f"canonical ingestion run missing: {run_id}"
                )
            current_state = str(row["current_state"])
            if current_state != expected_from_state:
                raise CanonicalRunStateConflict(
                    f"canonical ingestion run {run_id} is at {current_state!r}, "
                    f"cannot apply {to_state!r} from expected {expected_from_state!r}"
                )
            if (
                current_state == TERMINAL_SUCCESS_STATE
                and to_state != CANONICAL_FAILURE_RECONCILIATION_REQUIRED
            ):
                raise CanonicalRunStateTerminal(
                    f"canonical ingestion run {run_id} is terminal "
                    f"({current_state}); only the designed reconciliation "
                    "transition is allowed"
                )
            next_version = int(row["state_version"]) + 1
            next_attempt = (
                attempt_number
                if attempt_number is not None
                else int(row["attempt_number"])
            )
            if next_attempt < 1:
                raise CanonicalRunStateError("attempt_number must be positive")
            completed_at = None
            if to_state == TERMINAL_SUCCESS_STATE:
                completed_at = datetime.now(timezone.utc)
            payload = {
                "run_id": run_id,
                "state": to_state,
                "tenant_id": tenant_id,
                "source_id": source_id or "",
                "source_hash": source_hash or "",
                "knowledge_version_id": knowledge_version_id or "",
                "last_error_code": last_error_code or "",
            }
            payload_hash = _payload_hash(payload)
            outbox_event_id = canonical_state_event_id(
                run_id=run_id, state=to_state
            )
            updated = connection.execute(
                text(
                    """
                    UPDATE canonical_ingestion_runs
                    SET current_state = :to_state,
                        state_version = :next_version,
                        attempt_number = :next_attempt,
                        knowledge_version_id = COALESCE(
                            :knowledge_version_id, knowledge_version_id),
                        last_error_code = :last_error_code,
                        last_error_detail = :last_error_detail,
                        completed_at = :completed_at,
                        updated_at = now()
                    WHERE run_id = :run_id
                      AND tenant_id = :tenant_id
                      AND state_version = :expected_version
                    """
                ),
                {
                    "to_state": to_state,
                    "next_version": next_version,
                    "next_attempt": next_attempt,
                    "knowledge_version_id": knowledge_version_id,
                    "last_error_code": last_error_code,
                    "last_error_detail": last_error_detail,
                    "completed_at": completed_at,
                    "run_id": run_id,
                    "tenant_id": tenant_id,
                    "expected_version": int(row["state_version"]),
                },
            )
            if updated.rowcount != 1:
                raise CanonicalRunStateConflict(
                    f"canonical ingestion run {run_id} state_version conflict"
                )
            connection.execute(
                text(
                    """
                    INSERT INTO canonical_ingestion_run_history(
                        history_id, run_id, tenant_id, from_state, to_state,
                        state_version, attempt_number, source_id, source_hash,
                        outbox_event_id, payload_hash
                    ) VALUES (
                        :history_id, :run_id, :tenant_id, :from_state, :to_state,
                        :state_version, :attempt_number, :source_id, :source_hash,
                        :outbox_event_id, :payload_hash
                    )
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "history_id": f"history:{run_id}:{next_version}",
                    "run_id": run_id,
                    "tenant_id": tenant_id,
                    "from_state": current_state,
                    "to_state": to_state,
                    "state_version": next_version,
                    "attempt_number": next_attempt,
                    "source_id": source_id,
                    "source_hash": source_hash,
                    "outbox_event_id": outbox_event_id,
                    "payload_hash": payload_hash,
                },
            )
            # Domain state and outbox delivery event commit in one UoW.
            connection.execute(
                text(
                    """
                    INSERT INTO ingestion_outbox_events(
                        outbox_event_id, tenant_id, aggregate_ref, event_type,
                        payload_hash, payload, idempotency_key, publish_status
                    ) VALUES (
                        :outbox_event_id, :tenant_id, :run_id, :event_type,
                        :payload_hash, CAST(:payload AS jsonb),
                        :idempotency_key, 'pending'
                    )
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "outbox_event_id": outbox_event_id,
                    "tenant_id": tenant_id,
                    "run_id": run_id,
                    "event_type": CANONICAL_INGESTION_STATE_EVENT_TYPE,
                    "payload_hash": payload_hash,
                    "payload": _json_dumps(outbox_payload or payload),
                    "idempotency_key": _bounded_id(
                        f"{run_id}:", to_state, budget=120
                    ),
                },
            )
            return CanonicalRunTransitionReceipt(
                run_id=run_id,
                tenant_id=tenant_id,
                from_state=current_state,
                to_state=to_state,
                state_version=next_version,
                attempt_number=next_attempt,
                outbox_event_id=outbox_event_id,
            )

    # --- readback --------------------------------------------------------------

    def current_fact(self, *, run_id: str, tenant_id: str) -> CanonicalRunCurrentFact:
        row = self._one(
            """
            SELECT run_id, tenant_id, workspace_id, source_set_ref,
                   corpus_manifest_ref, current_state, state_version,
                   attempt_number, knowledge_version_id, last_error_code,
                   last_error_detail, idempotency_key, payload_hash,
                   created_at, updated_at, completed_at
            FROM canonical_ingestion_runs
            WHERE run_id = :run_id AND tenant_id = :tenant_id
            """,
            {"run_id": run_id, "tenant_id": tenant_id},
        )
        return CanonicalRunCurrentFact(
            run_id=str(row["run_id"]),
            tenant_id=str(row["tenant_id"]),
            workspace_id=str(row["workspace_id"]),
            source_set_ref=str(row["source_set_ref"]),
            corpus_manifest_ref=str(row["corpus_manifest_ref"]),
            current_state=str(row["current_state"]),
            state_version=int(row["state_version"]),
            attempt_number=int(row["attempt_number"]),
            knowledge_version_id=(
                str(row["knowledge_version_id"])
                if row["knowledge_version_id"] is not None
                else None
            ),
            last_error_code=(
                str(row["last_error_code"])
                if row["last_error_code"] is not None
                else None
            ),
            last_error_detail=(
                str(row["last_error_detail"])
                if row["last_error_detail"] is not None
                else None
            ),
            idempotency_key=str(row["idempotency_key"]),
            payload_hash=str(row["payload_hash"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            completed_at=row["completed_at"],
        )

    def history(self, *, run_id: str, tenant_id: str) -> tuple[dict[str, Any], ...]:
        rows = self._all(
            """
            SELECT history_id, run_id, tenant_id, from_state, to_state,
                   state_version, attempt_number, source_id, source_hash,
                   outbox_event_id, payload_hash, transitioned_at
            FROM canonical_ingestion_run_history
            WHERE run_id = :run_id AND tenant_id = :tenant_id
            ORDER BY state_version
            """,
            {"run_id": run_id, "tenant_id": tenant_id},
        )
        return tuple(dict(row) for row in rows)

    def current_fact_cross_tenant(
        self, *, owner_tenant_id: str, other_tenant_id: str, run_id: str
    ) -> None:
        row = self._one_optional(
            """
            SELECT run_id FROM canonical_ingestion_runs
            WHERE run_id = :run_id AND tenant_id = :tenant_id
            """,
            {"run_id": run_id, "tenant_id": other_tenant_id},
        )
        if row is not None:
            raise CanonicalRunStateError(
                f"run {run_id} of tenant {owner_tenant_id} is visible to "
                f"tenant {other_tenant_id}"
            )

    # --- helpers ---------------------------------------------------------------

    def _one(self, sql: str, params: dict[str, Any]) -> dict[str, Any]:
        with self.engine.connect() as connection:
            row = connection.execute(text(sql), params).mappings().first()
        if row is None:
            raise CanonicalRunStateError("canonical ingestion run fact not found")
        return dict(row)

    def _one_optional(self, sql: str, params: dict[str, Any]) -> dict[str, Any] | None:
        with self.engine.connect() as connection:
            row = connection.execute(text(sql), params).mappings().first()
        return None if row is None else dict(row)

    def _all(self, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        with self.engine.connect() as connection:
            rows = connection.execute(text(sql), params).mappings().all()
        return [dict(row) for row in rows]


def _payload_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        _json_dumps(payload).encode("utf-8")
    ).hexdigest()


def _json_dumps(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


__all__ = [
    "CANONICAL_INGESTION_STATE_EVENT_TYPE",
    "CanonicalIngestionRunStore",
    "CanonicalRunCurrentFact",
    "CanonicalRunStateConflict",
    "CanonicalRunStateError",
    "CanonicalRunStateTerminal",
    "CanonicalRunTransitionReceipt",
    "TERMINAL_FAILURE_STATES",
    "TERMINAL_SUCCESS_STATE",
    "canonical_state_event_id",
]
