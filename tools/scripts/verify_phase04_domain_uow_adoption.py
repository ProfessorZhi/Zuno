from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text

from zuno.platform.database import engine, postgres_runtime
from zuno.platform.database.dao.message import MessageDownDao, MessageLikeDao
from zuno.platform.database.dao.workspace_session import WorkSpaceSessionDao
from zuno.platform.database.models.workspace_session import WorkSpaceSession
from zuno.platform.database.session import (
    async_domain_uow,
    async_session_getter,
    domain_uow,
    session_getter,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DAO_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "database" / "dao"


def _verify_dao_transaction_ownership(errors: list[str]) -> None:
    for path in sorted(DAO_ROOT.glob("*.py")):
        content = path.read_text(encoding="utf-8")
        if "from zuno.database.session import" in content:
            errors.append(f"{path.name} still imports the legacy session alias")
        if "session.commit(" in content or "session.rollback(" in content:
            errors.append(f"{path.name} still owns commit or rollback instead of the UoW")


def _count_message_rows(user_input: str) -> tuple[int, int]:
    with engine.connect() as connection:
        liked = int(
            connection.execute(
                text("SELECT count(*) FROM message_like WHERE user_input = :user_input"),
                {"user_input": user_input},
            ).scalar_one()
        )
        down = int(
            connection.execute(
                text("SELECT count(*) FROM message_down WHERE user_input = :user_input"),
                {"user_input": user_input},
            ).scalar_one()
        )
    return liked, down


def _verify_sync_default_path(errors: list[str], marker: str) -> None:
    if engine is not postgres_runtime.sync_engine:
        errors.append("legacy engine export is not owned by the default PostgresRuntime")

    committed = f"phase04-domain-uow-commit-{marker}"
    rolled_back = f"phase04-domain-uow-rollback-{marker}"
    MessageLikeDao.create_message_like(committed, "committed")
    if _count_message_rows(committed) != (1, 0):
        errors.append("default DAO call did not commit through its implicit UoW")

    try:
        with domain_uow(tenant_id="tenant-domain-uow") as outer_session:
            with session_getter() as repository_session:
                if repository_session is not outer_session:
                    errors.append("repository did not reuse the active sync Domain UoW")
                tenant_id = str(
                    repository_session.exec(
                        text("SELECT current_setting('app.tenant_id', true)")
                    ).scalar_one()
                    or ""
                )
                if tenant_id != "tenant-domain-uow":
                    errors.append("sync repository session lost the Domain UoW tenant context")
            try:
                outer_session.commit()
                errors.append("sync repository session allowed a direct commit")
            except RuntimeError:
                pass
            MessageLikeDao.create_message_like(rolled_back, "rollback-like")
            MessageDownDao.create_message_down(rolled_back, "rollback-down")
            raise RuntimeError("force cross-repository rollback")
    except RuntimeError as exc:
        if str(exc) != "force cross-repository rollback":
            raise
    if _count_message_rows(rolled_back) != (0, 0):
        errors.append("cross-repository Domain UoW did not roll back atomically")

    with session_getter() as later_session:
        tenant_id = str(
            later_session.exec(
                text("SELECT current_setting('app.tenant_id', true)")
            ).scalar_one()
            or ""
        )
        if tenant_id:
            errors.append("sync tenant context leaked into a later default DAO transaction")

    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM message_like WHERE user_input IN (:committed, :rolled_back)"),
            {"committed": committed, "rolled_back": rolled_back},
        )
        connection.execute(
            text("DELETE FROM message_down WHERE user_input = :rolled_back"),
            {"rolled_back": rolled_back},
        )


async def _verify_async_default_path(errors: list[str], marker: str) -> None:
    committed_id = f"phase04-async-uow-commit-{marker}"
    rolled_back_id = f"phase04-async-uow-rollback-{marker}"
    committed = WorkSpaceSession(
        session_id=committed_id,
        title="PHASE04 committed",
        agent="normal",
        user_id="phase04-domain-uow",
        contexts=[],
    )
    await WorkSpaceSessionDao.create_workspace_session(committed)
    with engine.connect() as connection:
        count = int(
            connection.execute(
                text("SELECT count(*) FROM workspace_session WHERE session_id = :session_id"),
                {"session_id": committed_id},
            ).scalar_one()
        )
    if count != 1:
        errors.append("default async DAO call did not commit through its implicit UoW")

    try:
        async with async_domain_uow(tenant_id="tenant-async-domain-uow") as outer_session:
            async with async_session_getter() as repository_session:
                if repository_session is not outer_session:
                    errors.append("repository did not reuse the active async Domain UoW")
                tenant_id = str(
                    (
                        await repository_session.exec(
                            text("SELECT current_setting('app.tenant_id', true)")
                        )
                    ).scalar_one()
                    or ""
                )
                if tenant_id != "tenant-async-domain-uow":
                    errors.append("async repository session lost the Domain UoW tenant context")
            try:
                await outer_session.commit()
                errors.append("async repository session allowed a direct commit")
            except RuntimeError:
                pass

            async def child_task_probe() -> None:
                async with async_session_getter():
                    pass

            child = asyncio.create_task(child_task_probe())
            try:
                await child
                errors.append("async Domain UoW session was shared across tasks")
            except RuntimeError:
                pass

            await WorkSpaceSessionDao.create_workspace_session(
                WorkSpaceSession(
                    session_id=rolled_back_id,
                    title="PHASE04 rolled back",
                    agent="normal",
                    user_id="phase04-domain-uow",
                    contexts=[],
                )
            )
            raise RuntimeError("force async repository rollback")
    except RuntimeError as exc:
        if str(exc) != "force async repository rollback":
            raise

    async with async_session_getter() as later_session:
        tenant_id = str(
            (
                await later_session.exec(
                    text("SELECT current_setting('app.tenant_id', true)")
                )
            ).scalar_one()
            or ""
        )
        if tenant_id:
            errors.append("async tenant context leaked into a later default DAO transaction")
    with engine.begin() as connection:
        rolled_back_count = int(
            connection.execute(
                text("SELECT count(*) FROM workspace_session WHERE session_id = :session_id"),
                {"session_id": rolled_back_id},
            ).scalar_one()
        )
        if rolled_back_count:
            errors.append("async repository write survived its Domain UoW rollback")
        connection.execute(
            text("DELETE FROM workspace_session WHERE session_id IN (:committed, :rolled_back)"),
            {"committed": committed_id, "rolled_back": rolled_back_id},
        )


async def _run_async_verification(errors: list[str], marker: str) -> None:
    try:
        await _verify_async_default_path(errors, marker)
    finally:
        await postgres_runtime.async_engine.dispose()


def verify_phase04_domain_uow_adoption() -> list[str]:
    errors: list[str] = []
    marker = uuid4().hex
    _verify_dao_transaction_ownership(errors)
    _verify_sync_default_path(errors, marker)
    asyncio.run(_run_async_verification(errors, marker))
    return errors


def main() -> int:
    errors = verify_phase04_domain_uow_adoption()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 Domain UoW adoption verification failed.")
        return 1
    print("PHASE04 Domain UoW adoption verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
