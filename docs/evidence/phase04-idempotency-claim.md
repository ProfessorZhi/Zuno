# PHASE04 Idempotency Claim Evidence

phase_id: PHASE04
task_id: P04-T04
date: 2026-07-16
status: partial_implementation_available
same_key_same_hash: passed
same_key_different_hash: passed
renew: passed
expiry: passed
stale_generation_reject: passed
result_replay: passed
owner_crash: partial_expiry_reclaim_only
high_concurrency_single_winner: not_yet_proven

## Boundary

This evidence proves a real PostgreSQL idempotency claim lifecycle subset. It does not close P04-T04 and does not close PHASE04.

Idempotency Claim != Domain Success. A completed claim only records that the same request hash can replay a prior result reference; the domain owner still owns the meaning and validity of that result.

## Environment

| Item | Value |
| --- | --- |
| PostgreSQL service | `zuno-postgres`, image `postgres:16` |
| Database URL | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| Verification command | `python tools/scripts/verify_phase04_idempotency_claim.py` |
| Integration test | `pytest -q tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider` |

## Verified Behavior

- Same key and same request hash returns the active claim or completed result.
- Same key and different request hash fails closed with `InfrastructureConflictError`.
- Current owner can renew an in-progress claim.
- Wrong owner/generation cannot renew the claim.
- Expired in-progress claim transitions to `expired`.
- Same request hash can reclaim an expired claim with the next generation.
- Stale generation cannot complete after a newer generation exists.
- Completed claim replays the stored `result_ref`.

## Commands And Results

```text
python tools/scripts/verify_phase04_idempotency_claim.py
PHASE04 idempotency claim verification passed.
```

```text
pytest -q tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider
6 passed
```

## Remaining Gap

- High-concurrency single-winner contention is not yet proven.
- Owner crash is represented by expiry/reclaim only; process-level crash evidence remains missing.
- Cross-tenant idempotency isolation is not yet proven.
- P04-T04 remains `ready`, not completed.
