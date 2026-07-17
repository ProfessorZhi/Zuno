from __future__ import annotations

import os
import subprocess
from pathlib import Path
from uuid import uuid4

import yaml
from sqlalchemy import text

from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.foundation import FencingRejectedError, InfrastructureConflictError, create_foundation_engine
from zuno.platform.database.migration import BackfillSpec, PostgresBackfillController

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
MIGRATION_LOCK_NAMESPACE = "zuno:alembic:migration:v1"
DATA_CUTOVER_MATRIX = REPO_ROOT / ".agent" / "programs" / "work-products" / "data-cutover-matrix.yaml"


def _run_alembic(*args: str, lock_timeout_seconds: float = 30) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS"] = str(lock_timeout_seconds)
    return subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=120,
    )


def _upgrade_head() -> None:
    result = _run_alembic("upgrade", "head")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def _phase02_backfill_entry() -> dict[str, object]:
    matrix = yaml.safe_load(DATA_CUTOVER_MATRIX.read_text(encoding="utf-8")) or {}
    for entry in matrix.get("entries") or []:
        if "PHASE04" in str(entry.get("target_phase", "")):
            return dict(entry)
    raise RuntimeError("PHASE02 data cutover matrix has no PHASE04 backfill input")


def _verify_advisory_lock(engine) -> list[str]:
    errors: list[str] = []
    with engine.connect() as holder:
        acquired = holder.execute(
            text("SELECT pg_try_advisory_lock(hashtext(:namespace))"),
            {"namespace": MIGRATION_LOCK_NAMESPACE},
        ).scalar_one()
        if not acquired:
            return ["test process could not acquire the Alembic migration advisory lock"]
        try:
            blocked = _run_alembic("upgrade", "head", lock_timeout_seconds=0.5)
            output = blocked.stdout + blocked.stderr
            if blocked.returncode == 0:
                errors.append("parallel Alembic deploy did not fail closed while the migration lock was held")
            if "migration advisory lock timed out" not in output:
                errors.append("parallel Alembic deploy did not report the migration lock timeout")
        finally:
            released = holder.execute(
                text("SELECT pg_advisory_unlock(hashtext(:namespace))"),
                {"namespace": MIGRATION_LOCK_NAMESPACE},
            ).scalar_one()
            if not released:
                errors.append("test process could not release the Alembic migration advisory lock")

    recovered = _run_alembic("upgrade", "head", lock_timeout_seconds=5)
    if recovered.returncode != 0:
        errors.append("Alembic did not recover after migration lock release")
    return errors


def _verify_backfill_controller(engine) -> list[str]:
    errors: list[str] = []
    matrix_entry = _phase02_backfill_entry()
    marker = uuid4().hex
    backfill_id = f"phase04-backfill-{marker}"
    failed_id = f"phase04-backfill-failed-{marker}"
    forward_fix_id = f"phase04-backfill-forward-fix-{marker}"
    ids = [backfill_id, failed_id, forward_fix_id]
    controller = PostgresBackfillController(engine)
    spec = BackfillSpec(
        backfill_id=backfill_id,
        module_owner=str(matrix_entry["data_owner"]),
        source_ref=str(matrix_entry["source"]),
        target_ref=str(matrix_entry["target"]),
        transform_version=f"phase02-{canonical_sha256(matrix_entry)[:32]}",
        chunk_size=2,
    )
    try:
        declared = controller.declare(spec)
        if declared.state != "declared" or declared.cursor != {} or declared.processed_count != 0:
            errors.append("declared backfill did not start from the empty durable cursor")
        try:
            controller.declare(
                BackfillSpec(
                    backfill_id=backfill_id,
                    module_owner=spec.module_owner,
                    source_ref=spec.source_ref,
                    target_ref="different-target",
                    transform_version=spec.transform_version,
                    chunk_size=spec.chunk_size,
                )
            )
            errors.append("backfill id accepted a different immutable specification")
        except InfrastructureConflictError:
            pass

        first_claim = controller.claim(backfill_id=backfill_id, owner="worker-a", lease_seconds=30)
        if not first_claim.acquired or first_claim.backfill.generation != 1:
            errors.append("first backfill worker did not acquire generation 1")
        second_claim = controller.claim(backfill_id=backfill_id, owner="worker-b", lease_seconds=30)
        if second_claim.acquired:
            errors.append("second backfill worker acquired an active lease")

        cursor_1 = {"source_id": "source-a", "sequence": 1}
        payload_1 = canonical_sha256({"rows": [1, 2], "marker": marker})
        first_chunk = controller.apply_chunk(
            backfill_id=backfill_id,
            owner="worker-a",
            generation=1,
            chunk_id="chunk-1",
            start_cursor={},
            end_cursor=cursor_1,
            payload_hash=payload_1,
            row_count=2,
            source_watermark="watermark-1",
        )
        if not first_chunk.first_applied or first_chunk.processed_count != 2:
            errors.append("first backfill chunk did not advance processed_count once")
        duplicate = controller.apply_chunk(
            backfill_id=backfill_id,
            owner="worker-a",
            generation=1,
            chunk_id="chunk-1",
            start_cursor={},
            end_cursor=cursor_1,
            payload_hash=payload_1,
            row_count=2,
            source_watermark="watermark-1",
        )
        if duplicate.first_applied or duplicate.processed_count != 2:
            errors.append("same-hash backfill chunk replay was not idempotent")
        try:
            controller.apply_chunk(
                backfill_id=backfill_id,
                owner="worker-a",
                generation=1,
                chunk_id="chunk-1",
                start_cursor={},
                end_cursor=cursor_1,
                payload_hash=payload_1,
                row_count=2,
                source_watermark="different-watermark",
            )
            errors.append("same chunk receipt accepted a different source watermark")
        except InfrastructureConflictError:
            pass
        try:
            controller.apply_chunk(
                backfill_id=backfill_id,
                owner="worker-a",
                generation=1,
                chunk_id="chunk-1",
                start_cursor={},
                end_cursor=cursor_1,
                payload_hash=canonical_sha256({"rows": [9], "marker": marker}),
                row_count=1,
                source_watermark="watermark-conflict",
            )
            errors.append("same chunk id with a different hash was not rejected")
        except InfrastructureConflictError:
            pass

        paused = controller.pause(backfill_id=backfill_id, owner="worker-a", generation=1)
        if paused.state != "paused" or paused.lease_owner is not None:
            errors.append("backfill pause did not durably release the lease")
        engine.dispose()
        engine = create_foundation_engine(DATABASE_URL)
        controller = PostgresBackfillController(engine)
        resumed = controller.claim(backfill_id=backfill_id, owner="worker-b", lease_seconds=30)
        if not resumed.acquired or resumed.backfill.generation != 2 or resumed.backfill.cursor != cursor_1:
            errors.append("backfill did not resume from the durable cursor with generation 2")
        try:
            controller.apply_chunk(
                backfill_id=backfill_id,
                owner="worker-a",
                generation=1,
                chunk_id="stale-chunk",
                start_cursor=cursor_1,
                end_cursor={"source_id": "stale"},
                payload_hash=canonical_sha256({"stale": True}),
                row_count=1,
                source_watermark="watermark-stale",
            )
            errors.append("stale backfill generation was allowed to write after resume")
        except FencingRejectedError:
            pass

        cursor_2 = {"source_id": "source-b", "sequence": 2}
        second_chunk = controller.apply_chunk(
            backfill_id=backfill_id,
            owner="worker-b",
            generation=2,
            chunk_id="chunk-2",
            start_cursor=cursor_1,
            end_cursor=cursor_2,
            payload_hash=canonical_sha256({"rows": [3], "marker": marker}),
            row_count=1,
            source_watermark="watermark-2",
        )
        if not second_chunk.first_applied or second_chunk.processed_count != 3:
            errors.append("resumed backfill chunk did not advance from the saved cursor")
        completed = controller.complete(
            backfill_id=backfill_id,
            owner="worker-b",
            generation=2,
            verification_hash=canonical_sha256({"count": 3, "cursor": cursor_2}),
        )
        if (
            completed.state != "completed"
            or completed.processed_count != 3
            or completed.cursor != cursor_2
            or completed.conflict_count != 2
            or completed.verification_hash is None
        ):
            errors.append("completed backfill lost cursor/count/conflict/verification evidence")

        failed_spec = BackfillSpec(
            backfill_id=failed_id,
            module_owner=spec.module_owner,
            source_ref=spec.source_ref,
            target_ref=spec.target_ref,
            transform_version="phase02-failing-transform-v1",
            chunk_size=2,
        )
        controller.declare(failed_spec)
        failed_claim = controller.claim(backfill_id=failed_id, owner="worker-failed", lease_seconds=30)
        failed = controller.fail(
            backfill_id=failed_id,
            owner="worker-failed",
            generation=failed_claim.backfill.generation,
            error_code="TransformValidationError",
        )
        if failed.state != "failed" or failed.error_code != "TransformValidationError":
            errors.append("failed backfill did not persist its fail-closed error code")
        forward_fix = controller.declare(
            BackfillSpec(
                backfill_id=forward_fix_id,
                module_owner=spec.module_owner,
                source_ref=spec.source_ref,
                target_ref=spec.target_ref,
                transform_version="phase02-forward-fix-v2",
                chunk_size=2,
                forward_fix_of=failed_id,
            )
        )
        if forward_fix.state != "declared" or forward_fix.forward_fix_of != failed_id:
            errors.append("forward-fix backfill did not preserve failed migration lineage")
        if controller.get(failed_id).state != "superseded":
            errors.append("failed backfill was not superseded by its declared forward-fix")
    finally:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM infra_migration_backfills WHERE backfill_id = ANY(:backfill_ids)"),
                {"backfill_ids": ids},
            )
        engine.dispose()
    return errors


def verify_phase04_migration_control() -> list[str]:
    _upgrade_head()
    engine = create_foundation_engine(DATABASE_URL)
    try:
        errors = _verify_advisory_lock(engine)
        errors.extend(_verify_backfill_controller(engine))
        return errors
    finally:
        engine.dispose()


def main() -> int:
    errors = verify_phase04_migration_control()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 migration control verification failed.")
        return 1
    print("PHASE04 migration control verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
