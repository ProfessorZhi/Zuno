"""PHASE22 Owner Facts — PostgreSQL integration evidence.

PHASE22-OWNER-FACTS-POSTGRES-INTEGRATION
----------------------------------------

PostgreSQL integration tests for the Budget owner-fact store and the
Security ``expires_at`` extension. The fixture applies the migration
head against a real PostgreSQL backend (``ZUNO_TEST_POSTGRES_URL``) and
truncates the owner-fact tables between tests.

When no PostgreSQL backend is reachable the whole module is skipped
(env block) so the suite stays green in CI lanes that do not provision
a Postgres service. CI lanes that DO provision Postgres will run the
full matrix and record evidence as ``POSTGRES_INTEGRATION_VERIFIED``.
"""

from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.security import (
    BudgetPersistenceError,
    BudgetRepository,
    BudgetUnitOfWork,
    SecurityRepository,
    SecurityUnitOfWork,
)
from zuno.platform.security.decision_resolvers import (
    BUDGET_OWNER,
    PostgresBudgetDecisionResolver,
    PostgresSecurityDecisionResolver,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)
HEX_64 = "a" * 64


def _postgres_reachable() -> bool:
    """Return ``True`` iff the configured PostgreSQL backend answers a
    trivial query. The check is intentionally cheap so a missing
    service skips the whole module without paying the alembic cost.

    A short ``connect_timeout`` prevents the probe from blocking the
    test runner when no Postgres service is provisioned (the default
    psycopg connect timeout is minutes).
    """
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.engine.url import make_url

        url = make_url(DATABASE_URL)
        url = url.set(query={**(url.query or {}), "connect_timeout": "2"})
        engine = create_engine(url, pool_pre_ping=True)
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")).scalar_one()
        finally:
            engine.dispose()
    except Exception:
        return False
    return True


pytestmark = pytest.mark.skipif(
    not _postgres_reachable(),
    reason="PostgreSQL backend unavailable; integration evidence skipped",
)


@pytest.fixture(scope="module", autouse=True)
def migrated_postgres() -> None:
    """Apply alembic migrations against the configured PostgreSQL service."""
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture()
def engine(migrated_postgres):
    pg_engine = create_foundation_engine(DATABASE_URL)
    with pg_engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    budget_owner_admissions,
                    security_outbox_events,
                    security_audit_requirements,
                    security_redaction_decisions,
                    security_secret_leases,
                    security_secret_refs,
                    security_approval_decisions,
                    security_approval_requests,
                    security_authorization_decisions,
                    security_principal_contexts,
                    security_effective_epochs
                RESTART IDENTITY
                """
            )
        )
    try:
        yield pg_engine
    finally:
        pg_engine.dispose()


# ---------------------------------------------------------------------------
# Budget owner-fact integration tests
# ---------------------------------------------------------------------------


def _record_budget(engine, **overrides):
    expires_at = overrides.pop("expires_at", datetime.now(tz=UTC) + timedelta(hours=1))
    base = dict(
        budget_decision_id="bd:test",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        run_id="run-a",
        allowed=True,
        requested_limits={"tokens": 100, "tool_calls": 5},
        admitted_limits={"tokens": 50, "tool_calls": 2},
        policy_ref="policy:budget:test",
        owner=BUDGET_OWNER,
        expires_at=expires_at,
        status="ACTIVE",
    )
    base.update(overrides)
    with BudgetUnitOfWork(engine) as repo:
        return repo.record_budget_owner_admission(**base)


def test_budget_owner_admission_insert_and_read_round_trip(engine) -> None:
    """A well-formed Budget Admission fact is recorded and read back with
    an identical canonical hash."""
    receipt = _record_budget(engine, budget_decision_id="bd:test:round-trip")
    with BudgetUnitOfWork(engine) as repo:
        row = repo.read_budget_owner_admission(
            budget_decision_id="bd:test:round-trip",
            tenant_id="tenant-a",
        )
    assert row is not None
    assert row["tenant_id"] == "tenant-a"
    assert row["workspace_id"] == "workspace-a"
    assert row["principal_id"] == "user-a"
    assert row["run_id"] == "run-a"
    assert row["allowed"] is True
    assert row["status"] == "ACTIVE"
    assert row["owner"] == BUDGET_OWNER
    assert row["decision_hash"] == receipt.decision_hash


def test_budget_resolver_admits_well_formed_fact(engine) -> None:
    """A well-formed ACTIVE Budget Admission fact is admitted by the
    resolver into a BudgetDecisionRef."""
    _record_budget(engine, budget_decision_id="bd:test:admit")
    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="bd:test:admit",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
        },
    )
    assert ref is not None
    assert ref["allowed"] is True
    assert ref["tenant_id"] == "tenant-a"
    assert ref["workspace_id"] == "workspace-a"


def test_budget_resolver_rejects_denied(engine) -> None:
    """A DENIED fact is never admitted, even if the rest looks valid."""
    _record_budget(
        engine,
        budget_decision_id="bd:test:denied",
        allowed=False,
        status="DENIED",
    )
    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="bd:test:denied",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
        },
    )
    assert ref is None


def test_budget_resolver_rejects_expired(engine) -> None:
    """An expired Budget Admission fact fails closed."""
    _record_budget(
        engine,
        budget_decision_id="bd:test:expired",
        expires_at=datetime.now(tz=UTC) - timedelta(minutes=5),
    )
    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="bd:test:expired",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
        },
    )
    assert ref is None


def test_budget_resolver_rejects_revoked(engine) -> None:
    """A REVOKED Budget Admission fact fails closed."""
    _record_budget(engine, budget_decision_id="bd:test:revoked")
    with BudgetUnitOfWork(engine) as repo:
        repo.revoke_budget_owner_admission(
            budget_decision_id="bd:test:revoked",
            tenant_id="tenant-a",
        )
    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="bd:test:revoked",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
        },
    )
    assert ref is None


def test_budget_resolver_rejects_forged_hash(engine) -> None:
    """A row whose stored decision_hash has been tampered is rejected."""
    _record_budget(engine, budget_decision_id="bd:test:forged")
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE budget_owner_admissions
                SET decision_hash = :forged_hash
                WHERE budget_decision_id = :bd_id
                """
            ),
            {"forged_hash": "0" * 64, "bd_id": "bd:test:forged"},
        )
    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="bd:test:forged",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
        },
    )
    assert ref is None


def test_budget_resolver_rejects_foreign_tenant(engine) -> None:
    """A fact whose tenant does not match the caller fails closed."""
    _record_budget(engine, budget_decision_id="bd:test:foreign-tenant")
    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="bd:test:foreign-tenant",
        context={
            "tenant_id": "tenant-other",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
        },
    )
    assert ref is None


def test_budget_resolver_rejects_foreign_workspace(engine) -> None:
    _record_budget(engine, budget_decision_id="bd:test:foreign-ws")
    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="bd:test:foreign-ws",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-other",
            "run_id": "run-a",
            "principal_id": "user-a",
        },
    )
    assert ref is None


def test_budget_resolver_rejects_request_widening(engine) -> None:
    """Caller request limits cannot widen the admitted limits."""
    _record_budget(engine, budget_decision_id="bd:test:widen")
    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="bd:test:widen",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
            "budget_limits": {"tokens": 1000, "tool_calls": 100},
        },
    )
    assert ref is None


def test_budget_resolver_accepts_request_narrowing(engine) -> None:
    """Caller request limits may NARROW the admitted limits."""
    _record_budget(engine, budget_decision_id="bd:test:narrow")
    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="bd:test:narrow",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
            "budget_limits": {"tokens": 25, "tool_calls": 1},
        },
    )
    assert ref is not None
    assert ref["limits"] == {"tokens": 25, "tool_calls": 1}


def test_budget_resolver_rejects_missing_decision_id(engine) -> None:
    """A missing decision_id must fail closed."""
    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
        },
    )
    assert ref is None


def test_budget_resolver_rejects_missing_db(engine) -> None:
    """A resolver without a DB engine always fails closed."""
    resolver = PostgresBudgetDecisionResolver(engine=None)
    ref = resolver.resolve(
        decision_id="bd:test",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
        },
    )
    assert ref is None


def test_budget_rollback_restores_state(engine) -> None:
    """A rolled-back Budget Admission insert leaves the table empty."""
    with pytest.raises(BudgetPersistenceError):
        with BudgetUnitOfWork(engine) as repo:
            repo.record_budget_owner_admission(
                budget_decision_id="bd:test:rollback",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                principal_id="user-a",
                run_id="run-a",
                allowed=True,
                requested_limits={},
                admitted_limits={"tokens": 50},  # admitted required
                policy_ref="policy:budget:test",
                owner=BUDGET_OWNER,
                expires_at=datetime.now(tz=UTC) + timedelta(hours=1),
            )
            raise BudgetPersistenceError("simulated failure mid-transaction")
    with engine.connect() as conn:
        assert (
            conn.execute(
                text(
                    "SELECT count(*) FROM budget_owner_admissions "
                    "WHERE budget_decision_id = 'bd:test:rollback'"
                )
            ).scalar_one()
            == 0
        )


def test_budget_rejects_invalid_status(engine) -> None:
    """``status`` outside the legal set is rejected at the Repository."""
    with pytest.raises(BudgetPersistenceError):
        with BudgetUnitOfWork(engine) as repo:
            repo.record_budget_owner_admission(
                budget_decision_id="bd:test:bad-status",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                principal_id="user-a",
                run_id="run-a",
                allowed=True,
                requested_limits={"tokens": 10},
                admitted_limits={"tokens": 5},
                policy_ref="policy:budget:test",
                owner=BUDGET_OWNER,
                expires_at=datetime.now(tz=UTC) + timedelta(hours=1),
                status="BOGUS",
            )


def test_budget_owner_rejects_non_budget_owner_value(engine) -> None:
    """The Repository refuses to record a row whose ``owner`` is not
    the Budget owner identity (the DB CHECK constraint rejects it)."""
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        with BudgetUnitOfWork(engine) as repo:
            repo.record_budget_owner_admission(
                budget_decision_id="bd:test:wrong-owner",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                principal_id="user-a",
                run_id="run-a",
                allowed=True,
                requested_limits={"tokens": 10},
                admitted_limits={"tokens": 5},
                policy_ref="policy:budget:test",
                owner="attacker",
                expires_at=datetime.now(tz=UTC) + timedelta(hours=1),
            )


# ---------------------------------------------------------------------------
# Security expires_at extension integration tests
# ---------------------------------------------------------------------------


def _seed_security(engine, *, decision_id, expires_at):
    """Seed a Security owner fact via the existing security repository
    plus the new expires_at column."""
    with SecurityUnitOfWork(engine) as repo:
        repo.ensure_effective_epoch(
            epoch_ref="epoch:phase22",
            tenant_id="tenant-a",
            policy_bundle_ref="policy:bundle:phase22",
            policy_bundle={"actions": ["tool.execute"]},
            action_set_version="actions:v1",
            principal_context_hash=HEX_64,
            generation=1,
        )
        repo.ensure_principal_context(
            principal_context_id="principal-context:phase22",
            tenant_id="tenant-a",
            user_principal_id="user-a",
            agent_principal_id="agent-a",
            task_principal_id="task-a",
            session_principal_id="session-a",
            run_id="run-a",
            epoch_ref="epoch:phase22",
        )
        repo.ensure_authorization_decision(
            decision_id=decision_id,
            tenant_id="tenant-a",
            principal_context_id="principal-context:phase22",
            epoch_ref="epoch:phase22",
            resource_ref="tool:test",
            action="tool.execute",
            decision="REQUIRES_APPROVAL",
            reason_code="side_effect",
            prepared_action_hash=HEX_64,
            expires_at=expires_at,
        )


def test_security_resolver_admits_unexpired_fact(engine) -> None:
    """A well-formed Security owner fact with a future expiry is admitted."""
    _seed_security(
        engine,
        decision_id="decision:phase22:valid",
        expires_at=datetime.now(tz=UTC) + timedelta(hours=1),
    )
    resolver = PostgresSecurityDecisionResolver(
        engine=engine, security_epoch_ref="epoch:phase22"
    )
    ref = resolver.resolve(
        decision_id="decision:phase22:valid",
        context={"tenant_id": "tenant-a"},
    )
    assert ref is not None
    assert ref["decision_id"] == "decision:phase22:valid"
    assert ref["expires_at"]


def test_security_resolver_rejects_expired_fact(engine) -> None:
    """A Security owner fact whose expires_at has passed fails closed."""
    _seed_security(
        engine,
        decision_id="decision:phase22:expired",
        expires_at=datetime.now(tz=UTC) - timedelta(minutes=5),
    )
    resolver = PostgresSecurityDecisionResolver(
        engine=engine, security_epoch_ref="epoch:phase22"
    )
    ref = resolver.resolve(
        decision_id="decision:phase22:expired",
        context={"tenant_id": "tenant-a"},
    )
    assert ref is None


def test_security_resolver_rejects_missing_engine(engine) -> None:
    """A Security resolver without an engine always fails closed."""
    resolver = PostgresSecurityDecisionResolver(
        engine=None, security_epoch_ref="epoch:phase22"
    )
    ref = resolver.resolve(
        decision_id="decision:phase22",
        context={"tenant_id": "tenant-a"},
    )
    assert ref is None


def test_security_resolver_rejects_foreign_tenant(engine) -> None:
    """A fact whose tenant does not match the caller fails closed."""
    _seed_security(
        engine,
        decision_id="decision:phase22:foreign-tenant",
        expires_at=datetime.now(tz=UTC) + timedelta(hours=1),
    )
    resolver = PostgresSecurityDecisionResolver(
        engine=engine, security_epoch_ref="epoch:phase22"
    )
    ref = resolver.resolve(
        decision_id="decision:phase22:foreign-tenant",
        context={"tenant_id": "tenant-other"},
    )
    assert ref is None


# ---------------------------------------------------------------------------
# Product no-owner: zero tool dispatch
# ---------------------------------------------------------------------------


def test_product_no_owner_fact_yields_zero_tool_dispatch(engine) -> None:
    """When no Budget owner fact exists for a run, the resolver returns
    ``None`` and Agent Core cannot dispatch any tool step.

    ``validate_budget_decision_ref`` with ``required=True`` then refuses
    to allow the run.
    """
    from zuno.agent.contracts import BudgetDecisionRef
    from zuno.agent.runtime.owner_refs import validate_budget_decision_ref

    resolver = PostgresBudgetDecisionResolver(engine=engine)
    ref = resolver.resolve(
        decision_id="bd:does-not-exist",
        context={
            "tenant_id": "tenant-a",
            "workspace_id": "workspace-a",
            "run_id": "run-a",
            "principal_id": "user-a",
        },
    )
    assert ref is None

    # Even if a caller tried to synthesize a ref, the validator refuses
    # without a real owner-bound hash. No tool dispatch is admitted.
    forged_ref = BudgetDecisionRef(
        budget_decision_id="bd:does-not-exist",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        run_id="run-a",
        allowed=True,
        limits={"tokens": 999, "tool_calls": 999},
        owner="attacker",
        decision_hash="0" * 64,
    )
    verdict = validate_budget_decision_ref(
        forged_ref,
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        run_id="run-a",
        required=True,
    )
    assert verdict.allowed is False