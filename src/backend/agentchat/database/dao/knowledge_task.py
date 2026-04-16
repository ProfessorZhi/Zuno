from datetime import datetime, timezone

from sqlmodel import select, update

from agentchat.database.models.knowledge_task import KnowledgeTaskEventTable, KnowledgeTaskTable
from agentchat.database.session import session_getter


class KnowledgeTaskDao:
    @classmethod
    async def create_task(
        cls,
        knowledge_id: str,
        knowledge_file_id: str,
        task_type: str = "ingest",
        payload: dict | None = None,
    ) -> str:
        task = KnowledgeTaskTable(
            knowledge_id=knowledge_id,
            knowledge_file_id=knowledge_file_id,
            task_type=task_type,
            payload=payload or {},
        )
        with session_getter() as session:
            session.add(task)
            session.commit()
            return task.id

    @classmethod
    async def create_task_event(
        cls,
        task_id: str,
        stage: str,
        status: str,
        message: str,
        detail: dict | None = None,
    ):
        with session_getter() as session:
            session.add(
                KnowledgeTaskEventTable(
                    task_id=task_id,
                    stage=stage,
                    status=status,
                    message=message,
                    detail=detail or {},
                )
            )
            session.commit()

    @classmethod
    async def select_task_by_id(cls, task_id: str):
        with session_getter() as session:
            return session.exec(
                select(KnowledgeTaskTable).where(KnowledgeTaskTable.id == task_id)
            ).first()

    @classmethod
    async def list_tasks(cls, knowledge_file_id: str | None = None, knowledge_id: str | None = None):
        with session_getter() as session:
            sql = select(KnowledgeTaskTable)
            if knowledge_file_id:
                sql = sql.where(KnowledgeTaskTable.knowledge_file_id == knowledge_file_id)
            if knowledge_id:
                sql = sql.where(KnowledgeTaskTable.knowledge_id == knowledge_id)
            sql = sql.order_by(KnowledgeTaskTable.create_time.desc())
            return session.exec(sql).all()

    @classmethod
    async def list_task_events(cls, task_id: str):
        with session_getter() as session:
            sql = (
                select(KnowledgeTaskEventTable)
                .where(KnowledgeTaskEventTable.task_id == task_id)
                .order_by(KnowledgeTaskEventTable.create_time.asc())
            )
            return session.exec(sql).all()

    @classmethod
    async def update_task(cls, task_id: str, **kwargs):
        with session_getter() as session:
            sql = update(KnowledgeTaskTable).where(KnowledgeTaskTable.id == task_id).values(**kwargs)
            session.exec(sql)
            session.commit()

    @classmethod
    async def mark_task_started(cls, task_id: str, stage: str):
        await cls.update_task(
            task_id,
            status="running",
            current_stage=stage,
            started_at=datetime.now(timezone.utc),
        )

    @classmethod
    async def mark_task_finished(
        cls,
        task_id: str,
        *,
        status: str,
        current_stage: str,
        error_message: str | None = None,
        result_summary: dict | None = None,
    ):
        await cls.update_task(
            task_id,
            status=status,
            current_stage=current_stage,
            error_message=error_message,
            result_summary=result_summary or {},
            finished_at=datetime.now(timezone.utc),
        )
