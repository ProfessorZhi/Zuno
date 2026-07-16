from __future__ import annotations

from sqlalchemy import text

from zuno.platform.database.foundation import (
    FencingRejectedError,
    InfrastructureUnitOfWork,
    create_foundation_engine,
)

DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"


def verify_phase04_lease_fencing() -> list[str]:
    engine = create_foundation_engine(DATABASE_URL)
    errors: list[str] = []
    resource = "phase04-lease-fencing"
    cancel_resource = "phase04-lease-cancel"
    try:
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM infra_worker_leases WHERE resource_id IN (:resource, :cancel_resource)"),
                {"resource": resource, "cancel_resource": cancel_resource},
            )

        uow = InfrastructureUnitOfWork(engine)
        with uow as repo:
            token = repo.acquire_lease(resource_id=resource, owner_id="worker-a", ttl_seconds=30)
            repo.assert_fence(token)
            renewed = repo.renew_lease(token, ttl_seconds=120)
            if renewed.epoch != token.epoch or renewed.lease_id != token.lease_id:
                errors.append(f"renewed token changed identity: {renewed!r}")
            try:
                repo.acquire_lease(resource_id=resource, owner_id="worker-b", ttl_seconds=30)
                errors.append("duplicate worker acquired live lease")
            except FencingRejectedError:
                pass

        with engine.begin() as conn:
            conn.execute(
                text("UPDATE infra_worker_leases SET expires_at = now() - interval '1 second' WHERE resource_id = :resource"),
                {"resource": resource},
            )

        with uow as repo:
            replacement = repo.acquire_lease(resource_id=resource, owner_id="worker-b", ttl_seconds=30)
            if replacement.epoch != renewed.epoch + 1:
                errors.append(f"replacement epoch mismatch: {replacement.epoch!r}")
            try:
                repo.assert_fence(renewed)
                errors.append("late worker fencing token was accepted after transfer")
            except FencingRejectedError:
                pass
            try:
                repo.renew_lease(renewed, ttl_seconds=60)
                errors.append("late worker renewed stale lease token")
            except FencingRejectedError:
                pass

        with uow as repo:
            cancellable = repo.acquire_lease(resource_id=cancel_resource, owner_id="worker-a", ttl_seconds=30)
            repo.cancel_lease(cancellable)
            try:
                repo.assert_fence(cancellable)
                errors.append("cancelled lease still passed fencing")
            except FencingRejectedError:
                pass
            try:
                repo.cancel_lease(cancellable)
                errors.append("cancelled lease was cancelled twice")
            except FencingRejectedError:
                pass

        with uow as repo:
            after_cancel = repo.acquire_lease(resource_id=cancel_resource, owner_id="worker-b", ttl_seconds=30)
            if after_cancel.epoch != cancellable.epoch + 1:
                errors.append(f"cancel transfer epoch mismatch: {after_cancel.epoch!r}")
            repo.assert_fence(after_cancel)
    finally:
        engine.dispose()
    return errors


def main() -> int:
    errors = verify_phase04_lease_fencing()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 lease/fencing verification failed.")
        return 1
    print("PHASE04 lease/fencing verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
