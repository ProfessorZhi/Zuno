from uuid import uuid4

from loguru import logger

from agentchat.api.services.knowledge import KnowledgeService
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
    async def _queue_file_task(
        cls,
        *,
        knowledge_id: str,
        knowledge_file_id: str,
        file_name: str,
        oss_url: str,
        task_type: str,
        previous_task_id: str | None = None,
    ):
        task_id = await KnowledgeTaskDao.create_task(
            knowledge_id=knowledge_id,
            knowledge_file_id=knowledge_file_id,
            task_type=task_type,
            payload={
                "file_name": file_name,
                "oss_url": oss_url,
            },
        )
        await KnowledgeFileDao.update_pipeline_fields(
            knowledge_file_id,
            last_task_id=task_id,
            status="process",
            parse_status="pending",
            rag_index_status="pending",
            graph_index_status="pending",
            last_error=None,
        )
        dispatch_mode = await cls._dispatch_task(task_id, knowledge_file_id, knowledge_id)
        return {
            "task_id": task_id,
            "knowledge_file_id": knowledge_file_id,
            "dispatch_mode": dispatch_mode,
            "previous_task_id": previous_task_id,
        }

    @classmethod
    async def _dispatch_task(cls, task_id: str, knowledge_file_id: str, knowledge_id: str):
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
                return "rabbitmq"

            task = await KnowledgeTaskDao.select_task_by_id(task_id)
            file_path = (task.payload or {}).get("file_path") if task else None
            await pipeline_manager.run_sync(task_id, file_path=file_path)
            return "sync"
        except Exception as err:
            logger.error(f"Dispatch Knowledge Task Error: {err}")
            raise ValueError(f"Dispatch Knowledge Task Error: {err}")

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
            dispatch_mode = await cls._dispatch_task(task_id, knowledge_file_id, knowledge_id)
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
    async def retry_task(cls, task_id: str):
        task = await KnowledgeTaskDao.select_task_by_id(task_id)
        if not task:
            raise ValueError("knowledge task not found")

        payload = dict(task.payload or {})
        queued = await cls._queue_file_task(
            knowledge_id=task.knowledge_id,
            knowledge_file_id=task.knowledge_file_id,
            file_name=payload.get("file_name", ""),
            oss_url=payload.get("oss_url", ""),
            task_type=task.task_type,
            previous_task_id=task_id,
        )
        return {
            **queued,
            "previous_task_id": task_id,
        }

    @classmethod
    async def reindex_knowledge_files(cls, knowledge_id: str):
        knowledge_files = await KnowledgeFileDao.select_knowledge_file(knowledge_id)
        summary = {
            "knowledge_id": knowledge_id,
            "total_files": len(knowledge_files),
            "created_tasks": 0,
            "dispatched_tasks": 0,
            "failed_tasks": 0,
        }
        task_ids: list[str] = []
        file_ids: list[str] = []

        for knowledge_file in knowledge_files:
            try:
                task_id = await KnowledgeTaskDao.create_task(
                    knowledge_id=knowledge_id,
                    knowledge_file_id=knowledge_file.id,
                    task_type="reindex",
                    payload={
                        "file_name": knowledge_file.file_name,
                        "oss_url": knowledge_file.oss_url,
                    },
                )
                summary["created_tasks"] += 1
                task_ids.append(task_id)
                file_ids.append(knowledge_file.id)
                await KnowledgeFileDao.update_pipeline_fields(
                    knowledge_file.id,
                    last_task_id=task_id,
                    status="process",
                    parse_status="pending",
                    rag_index_status="pending",
                    graph_index_status="pending",
                    last_error=None,
                )
                await cls._dispatch_task(task_id, knowledge_file.id, knowledge_id)
                summary["dispatched_tasks"] += 1
            except Exception as err:
                logger.error(
                    "Reindex Knowledge File Error: file_id={} error={}",
                    getattr(knowledge_file, "id", None),
                    err,
                )
                summary["failed_tasks"] += 1

        return {
            "summary": summary,
            "task_ids": task_ids,
            "file_ids": file_ids,
        }

    @classmethod
    async def bulk_reindex_knowledge_files(cls, knowledge_id: str, user_id: str):
        await KnowledgeService.verify_user_permission(knowledge_id, user_id)
        return await cls.reindex_knowledge_files(knowledge_id)

    @classmethod
    async def verify_user_permission(cls, knowledge_file_id, user_id):
        knowledge_file = await cls.select_knowledge_file_by_id(knowledge_file_id)
        if user_id not in (AdminUser, knowledge_file.user_id):
            raise ValueError("娌℃湁鏉冮檺璁块棶")

    @classmethod
    async def update_parsing_status(cls, knowledge_file_id, status):
        return await KnowledgeFileDao.update_parsing_status(knowledge_file_id, status)
