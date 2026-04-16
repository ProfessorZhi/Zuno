from sqlmodel import delete, select, update

from agentchat.database.models.knowledge_file import KnowledgeFileTable
from agentchat.database.session import session_getter


class KnowledgeFileDao:
    @classmethod
    async def create_knowledge_file(
        cls,
        knowledge_file_id,
        file_name,
        knowledge_id,
        user_id,
        oss_url,
        file_size_bytes,
    ):
        with session_getter() as session:
            session.add(
                KnowledgeFileTable(
                    file_name=file_name,
                    knowledge_id=knowledge_id,
                    file_size=file_size_bytes,
                    user_id=user_id,
                    oss_url=oss_url,
                    id=knowledge_file_id,
                    status="process",
                )
            )
            session.commit()

    @classmethod
    async def delete_knowledge_file(cls, knowledge_file_id):
        with session_getter() as session:
            sql = delete(KnowledgeFileTable).where(KnowledgeFileTable.id == knowledge_file_id)
            session.exec(sql)
            session.commit()

    @classmethod
    async def select_knowledge_file(cls, knowledge_id):
        with session_getter() as session:
            sql = select(KnowledgeFileTable).where(KnowledgeFileTable.knowledge_id == knowledge_id)
            return session.exec(sql).all()

    @classmethod
    async def select_knowledge_file_by_id(cls, knowledge_file_id):
        with session_getter() as session:
            sql = select(KnowledgeFileTable).where(KnowledgeFileTable.id == knowledge_file_id)
            return session.exec(sql).first()

    @classmethod
    async def update_parsing_status(cls, knowledge_file_id, status):
        await cls.update_pipeline_fields(
            knowledge_file_id,
            status=status,
            parse_status=status,
        )

    @classmethod
    async def update_pipeline_fields(cls, knowledge_file_id, **kwargs):
        with session_getter() as session:
            sql = update(KnowledgeFileTable).where(KnowledgeFileTable.id == knowledge_file_id).values(**kwargs)
            session.exec(sql)
            session.commit()
