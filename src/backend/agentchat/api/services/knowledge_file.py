from uuid import uuid4

from loguru import logger

from agentchat.database.dao.knowledge_file import KnowledgeFileDao
from agentchat.database.dao.knowledge_task import KnowledgeTaskDao
from agentchat.database.models.user import AdminUser
from agentchat.services.pipeline.manager import KnowledgePipelineManager
from agentchat.services.pipeline.models import KnowledgeTaskStage
from agentchat.services.queue.client import QueueClient, get_queue_names
from agentchat.services.queue.messages import build_task_message
from agentchat.settings import app_settings
from agentchat.services.rag.handler import RagHandler
from agentchat.utils.runtime_observability import get_active_trace_id


class KnowledgeFileService:
    @classmethod
    def parse_knowledge_file(cls):
        pass

    @classmethod
    async def get_knowledge_file(cls, knowledge_id):
        results = await KnowledgeFileDao.select_knowledge_file(knowledge_id)
        return [res.to_dict() for res in results]

    @classmethod
    async def create_knowledge_file(
        cls,
        file_name: str,
        file_path: str,
        knowledge_id: str,
        user_id: str,
        oss_url: str,
        file_size_bytes,
    ):
        knowledge_file_id = uuid4().hex
        await KnowledgeFileDao.create_knowledge_file(
            knowledge_file_id,
            file_name,
            knowledge_id,
            user_id,
            oss_url,
            file_size_bytes,
        )
        task_id = await KnowledgeTaskDao.create_task(
            knowledge_id=knowledge_id,
            knowledge_file_id=knowledge_file_id,
            task_type="ingest",
            payload={
                "file_name": file_name,
                "file_path": file_path,
                "oss_url": oss_url,
            },
        )
        await KnowledgeFileDao.update_pipeline_fields(
            knowledge_file_id,
            last_task_id=task_id,
            status="process",
        )

        try:
            pipeline_manager = KnowledgePipelineManager(
                enable_graph_indexing=True,
                enable_elasticsearch=app_settings.rag.enable_elasticsearch,
            )
            if QueueClient.is_enabled():
                await pipeline_manager.mark_queued(task_id)
                queue_names = get_queue_names()
                await QueueClient().publish(
                    queue_names["parse"],
                    build_task_message(
                        task_id=task_id,
                        knowledge_id=knowledge_id,
                        knowledge_file_id=knowledge_file_id,
                        stage=KnowledgeTaskStage.parsing,
                        trace_id=get_active_trace_id(),
                    ),
                )
                dispatch_mode = "rabbitmq"
            else:
                await pipeline_manager.run_sync(task_id, file_path=file_path)
                dispatch_mode = "sync"
            return {
                "knowledge_file_id": knowledge_file_id,
                "task_id": task_id,
                "dispatch_mode": dispatch_mode,
            }
        except Exception as err:
            logger.error(f"Create Knowledge File Error: {err}")
            raise ValueError(f"Create Knowledge File Error: {err}")

    @classmethod
    async def delete_knowledge_file(cls, knowledge_file_id):
        knowledge_file = await cls.select_knowledge_file_by_id(knowledge_file_id)
        await RagHandler.delete_documents_es_milvus(knowledge_file.id, knowledge_file.knowledge_id)
        await KnowledgeFileDao.delete_knowledge_file(knowledge_file_id)

    @classmethod
    async def select_knowledge_file_by_id(cls, knowledge_file_id):
        return await KnowledgeFileDao.select_knowledge_file_by_id(knowledge_file_id)

    @classmethod
    async def get_task_detail(cls, task_id: str):
        task = await KnowledgeTaskDao.select_task_by_id(task_id)
        events = await KnowledgeTaskDao.list_task_events(task_id)
        return {
            "task": task.to_dict() if task else None,
            "events": [event.to_dict() for event in events],
        }

    @classmethod
    async def list_tasks(cls, knowledge_file_id: str | None = None, knowledge_id: str | None = None):
        tasks = await KnowledgeTaskDao.list_tasks(
            knowledge_file_id=knowledge_file_id,
            knowledge_id=knowledge_id,
        )
        return [task.to_dict() for task in tasks]

    @classmethod
    async def verify_user_permission(cls, knowledge_file_id, user_id):
        knowledge_file = await cls.select_knowledge_file_by_id(knowledge_file_id)
        if user_id not in (AdminUser, knowledge_file.user_id):
            raise ValueError("娌℃湁鏉冮檺璁块棶")

    @classmethod
    async def update_parsing_status(cls, knowledge_file_id, status):
        return await KnowledgeFileDao.update_parsing_status(knowledge_file_id, status)
