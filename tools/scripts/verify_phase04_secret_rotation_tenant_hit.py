from __future__ import annotations

import os
import subprocess
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.foundation import (
    FencingRejectedError,
    InfrastructureConflictError,
    InfrastructureUnitOfWork,
    create_foundation_engine,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
)


def _upgrade_head() -> list[str]:
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    if result.returncode != 0:
        return [f"alembic upgrade head failed: {result.stdout}{result.stderr}"]
    return []


def _cleanup(engine, marker: str) -> None:
    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM infra_secret_leases WHERE secret_ref LIKE :prefix"),
            {"prefix": f"phase04-secret-{marker}%"},
        )
        connection.execute(
            text("DELETE FROM infra_secret_rotation_heads WHERE secret_ref LIKE :prefix"),
            {"prefix": f"phase04-secret-{marker}%"},
        )
        connection.execute(
            text("DELETE FROM infra_secret_versions WHERE secret_ref LIKE :prefix"),
            {"prefix": f"phase04-secret-{marker}%"},
        )
        connection.execute(
            text("DELETE FROM infra_cross_tenant_hits WHERE resource_ref LIKE :prefix"),
            {"prefix": f"phase04-tenant-hit-{marker}%"},
        )


def verify_phase04_secret_rotation_tenant_hit() -> list[str]:
    errors = _upgrade_head()
    if errors:
        return errors

    marker = uuid4().hex[:12]
    tenant_id = f"tenant-{marker}"
    other_tenant_id = f"tenant-other-{marker}"
    secret_ref = f"phase04-secret-{marker}-minio"
    config_hash_v1 = canonical_sha256({"secret_ref": secret_ref, "version": 1})
    config_hash_v2 = canonical_sha256({"secret_ref": secret_ref, "version": 2})
    engine = create_foundation_engine(DATABASE_URL, pool_size=4, max_overflow=2)
    try:
        _cleanup(engine, marker)
        with InfrastructureUnitOfWork(engine) as repo:
            repo.register_secret_version(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                version=1,
                kms_key_ref="kms://phase04/minio/v1",
                config_hash=config_hash_v1,
                owner_id="secret-owner",
                payload={"rotation": "initial", "kms_key_ref": "kms://phase04/minio/v1"},
            )
            receipt = repo.activate_secret_version(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                version=1,
                expected_generation=0,
                owner_id="secret-owner",
            )
            if receipt.generation != 1 or receipt.version != 1:
                errors.append(f"initial activation receipt mismatch: {receipt!r}")

        try:
            with InfrastructureUnitOfWork(engine) as repo:
                repo.register_secret_version(
                    secret_ref=secret_ref,
                    tenant_id=tenant_id,
                    version=3,
                    kms_key_ref="kms://phase04/minio/v3",
                    config_hash=canonical_sha256({"secret_ref": secret_ref, "version": 3}),
                    owner_id="secret-owner",
                    payload={"secret": "plaintext-must-not-persist"},
                )
                errors.append("secret material payload was accepted")
        except ValueError:
            pass

        with InfrastructureUnitOfWork(engine) as repo:
            repo.register_secret_version(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                version=2,
                kms_key_ref="kms://phase04/minio/v2",
                config_hash=config_hash_v2,
                owner_id="secret-owner",
                payload={"rotation": "canary", "kms_key_ref": "kms://phase04/minio/v2"},
            )
            rotated = repo.activate_secret_version(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                version=2,
                expected_generation=1,
                owner_id="secret-owner",
            )
            if rotated.version != 2 or rotated.generation != 2:
                errors.append(f"rotation receipt mismatch: {rotated!r}")
            lease = repo.issue_secret_lease(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                owner_id="minio-adapter",
                ttl_seconds=60,
            )
            if lease.version != 2 or lease.generation != 2:
                errors.append(f"secret lease did not use active version: {lease!r}")

        try:
            with InfrastructureUnitOfWork(engine) as repo:
                repo.issue_secret_lease(
                    secret_ref=secret_ref,
                    tenant_id=other_tenant_id,
                    owner_id="wrong-tenant",
                    ttl_seconds=60,
                )
                errors.append("cross-tenant secret lease was accepted")
        except InfrastructureConflictError:
            pass

        with InfrastructureUnitOfWork(engine) as repo:
            rolled_back = repo.rollback_secret_version(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                target_version=1,
                expected_generation=2,
                owner_id="secret-owner",
            )
            if rolled_back.version != 1 or rolled_back.generation != 3:
                errors.append(f"rollback receipt mismatch: {rolled_back!r}")
            lease = repo.issue_secret_lease(
                secret_ref=secret_ref,
                tenant_id=tenant_id,
                owner_id="minio-adapter",
                ttl_seconds=60,
            )
            if lease.version != 1 or lease.generation != 3:
                errors.append(f"rollback lease did not use restored version: {lease!r}")

        try:
            with InfrastructureUnitOfWork(engine) as repo:
                repo.rollback_secret_version(
                    secret_ref=secret_ref,
                    tenant_id=tenant_id,
                    target_version=2,
                    expected_generation=1,
                    owner_id="stale-owner",
                )
                errors.append("stale secret rollback generation was accepted")
        except FencingRejectedError:
            pass

        with InfrastructureUnitOfWork(engine) as repo:
            try:
                repo.enforce_tenant_scope(
                    service_kind="RELATIONAL",
                    resource_ref=f"phase04-tenant-hit-{marker}-row",
                    expected_tenant_id=tenant_id,
                    observed_tenant_id=other_tenant_id,
                    action="FAIL_CLOSED",
                    owner_id="database-adapter",
                    payload={"table": "infra_secret_versions", "operation": "read"},
                )
                errors.append("relational cross-tenant hit was accepted")
            except InfrastructureConflictError:
                pass
            try:
                repo.enforce_tenant_scope(
                    service_kind="OBJECT",
                    resource_ref=f"phase04-tenant-hit-{marker}-object",
                    expected_tenant_id=tenant_id,
                    observed_tenant_id=other_tenant_id,
                    action="QUARANTINE",
                    owner_id="object-adapter",
                    payload={"object_ref": "s3://bucket/other-tenant/object"},
                )
                errors.append("object cross-tenant hit was accepted")
            except InfrastructureConflictError:
                pass

        with engine.connect() as connection:
            head = connection.execute(
                text(
                    """
                    SELECT active_version, previous_version, generation, status
                    FROM infra_secret_rotation_heads
                    WHERE secret_ref = :secret_ref
                    """
                ),
                {"secret_ref": secret_ref},
            ).one()
            if (
                int(head.active_version) != 1
                or int(head.previous_version) != 2
                or int(head.generation) != 3
                or str(head.status) != "rolled_back"
            ):
                errors.append(f"secret head did not persist rollback: {head!r}")
            material_rows = connection.execute(
                text(
                    """
                    SELECT payload::text AS payload
                    FROM infra_secret_versions
                    WHERE secret_ref = :secret_ref
                    """
                ),
                {"secret_ref": secret_ref},
            ).all()
            if any("plaintext-must-not-persist" in str(row.payload) for row in material_rows):
                errors.append("secret material was persisted")
            hit_rows = connection.execute(
                text(
                    """
                    SELECT action, status
                    FROM infra_cross_tenant_hits
                    WHERE resource_ref LIKE :prefix
                    ORDER BY action
                    """
                ),
                {"prefix": f"phase04-tenant-hit-{marker}%"},
            ).all()
            hit_status = {(str(row.action), str(row.status)) for row in hit_rows}
            if hit_status != {("FAIL_CLOSED", "blocked"), ("QUARANTINE", "quarantined")}:
                errors.append(f"cross-tenant hit statuses mismatch: {hit_status!r}")
    finally:
        _cleanup(engine, marker)
        engine.dispose()

    return errors


def main() -> int:
    errors = verify_phase04_secret_rotation_tenant_hit()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 secret rotation and tenant hit verification failed.")
        return 1
    print("PHASE04 secret rotation and tenant hit verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
