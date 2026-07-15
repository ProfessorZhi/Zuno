from __future__ import annotations

import importlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def verify_phase04_postgres_foundation() -> list[str]:
    errors: list[str] = []
    required_files = [
        REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "database" / "foundation.py",
        REPO_ROOT / "infra" / "db" / "alembic" / "versions" / "20260715_04_infrastructure_foundation.py",
        REPO_ROOT / "tests" / "integration" / "test_phase04_postgres_foundation.py",
        REPO_ROOT / "docs" / "evidence" / "phase04-postgres-foundation.md",
    ]
    for path in required_files:
        if not path.exists():
            errors.append(f"missing PHASE04 file: {path.relative_to(REPO_ROOT).as_posix()}")
    if errors:
        return errors

    migration = required_files[1].read_text(encoding="utf-8")
    for table in [
        "infra_outbox_events",
        "infra_inbox_messages",
        "infra_idempotency_claims",
        "infra_worker_leases",
        "infra_object_manifests",
        "infra_checkpoints",
    ]:
        if table not in migration:
            errors.append(f"PHASE04 migration missing table: {table}")
    if re.search(r"legacy_", migration):
        errors.append("PHASE04 migration must not create legacy_* tables")

    foundation = required_files[0].read_text(encoding="utf-8")
    for phrase in [
        "FOR UPDATE SKIP LOCKED",
        "canonical_sha256",
        "FencingRejectedError",
        "InfrastructureUnitOfWork",
        "infra_checkpoints",
    ]:
        if phrase not in foundation:
            errors.append(f"foundation.py missing required primitive phrase: {phrase}")

    try:
        module = importlib.import_module("zuno.platform.database.foundation")
    except Exception as exc:
        errors.append(f"cannot import PHASE04 foundation module: {exc}")
        return errors
    for symbol in [
        "InfrastructureUnitOfWork",
        "InfrastructureRepository",
        "FencingToken",
        "InfrastructureConflictError",
        "FencingRejectedError",
    ]:
        if not hasattr(module, symbol):
            errors.append(f"foundation module missing symbol: {symbol}")

    evidence = required_files[3].read_text(encoding="utf-8")
    for phrase in [
        "PostgreSQL 16",
        "alembic -c infra/db/alembic.ini upgrade head",
        "5 passed",
        "真实边界",
    ]:
        if phrase not in evidence:
            errors.append(f"phase04 evidence missing phrase: {phrase}")
    return errors


def main() -> int:
    errors = verify_phase04_postgres_foundation()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 PostgreSQL foundation verification failed.")
        return 1
    print("PHASE04 PostgreSQL foundation verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
