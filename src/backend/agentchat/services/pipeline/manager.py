from loguru import logger

from agentchat.database.dao.knowledge_file import KnowledgeFileDao
from agentchat.database.dao.knowledge_task import KnowledgeTaskDao
from agentchat.services.pipeline.models import KnowledgeTaskStage, KnowledgeTaskStatus
from agentchat.services.pipeline.stages import (
    build_failed_file_patch,
    build_running_file_patch,
    build_success_file_patch,
)
from agentchat.services.rag.handler import RagHandler
from agentchat.services.rag.parser import doc_parser


class KnowledgePipelineManager:
    def __init__(self, *, enable_graph_indexing: bool = True, enable_elasticsearch: bool = False):
        self.enable_graph_indexing = enable_graph_indexing
        self.enable_elasticsearch = enable_elasticsearch

    async def _record_stage(
        self,
        task_id: str,
        stage: str,
        status: str,
        message: str,
        *,
        detail: dict | None = None,
        knowledge_file_id: str | None = None,
        file_patch: dict | None = None,
    ):
        await KnowledgeTaskDao.update_task(task_id, status=status, current_stage=stage)
        await KnowledgeTaskDao.create_task_event(task_id, stage, status, message, detail or {})
        if knowledge_file_id and file_patch:
            await KnowledgeFileDao.update_pipeline_fields(knowledge_file_id, **file_patch)

    async def run_sync(self, task_id: str, *, file_path: str):
        task = await KnowledgeTaskDao.select_task_by_id(task_id)
        if not task:
            raise ValueError(f"knowledge task not found: {task_id}")

        knowledge_file_id = task.knowledge_file_id
        try:
            await self._record_stage(
                task_id,
                KnowledgeTaskStage.queued,
                KnowledgeTaskStatus.running,
                "knowledge pipeline queued",
                knowledge_file_id=knowledge_file_id,
                file_patch=build_running_file_patch(KnowledgeTaskStage.queued, task_id),
            )
            await KnowledgeTaskDao.mark_task_started(task_id, KnowledgeTaskStage.queued)

            await self._record_stage(
                task_id,
                KnowledgeTaskStage.parsing,
                KnowledgeTaskStatus.running,
                "parsing knowledge file",
                knowledge_file_id=knowledge_file_id,
                file_patch=build_running_file_patch(KnowledgeTaskStage.parsing, task_id),
            )
            chunks = await doc_parser.parse_doc_into_chunks(
                knowledge_file_id,
                file_path,
                task.knowledge_id,
            )
            await self._record_stage(
                task_id,
                KnowledgeTaskStage.parsing,
                KnowledgeTaskStatus.running,
                "parsing completed",
                detail={"chunk_count": len(chunks)},
                knowledge_file_id=knowledge_file_id,
                file_patch=build_success_file_patch(KnowledgeTaskStage.parsing, task_id),
            )

            await self._record_stage(
                task_id,
                KnowledgeTaskStage.splitting,
                KnowledgeTaskStatus.running,
                "splitting chunks",
                detail={"chunk_count": len(chunks)},
            )

            await self._record_stage(
                task_id,
                KnowledgeTaskStage.rag_indexing,
                KnowledgeTaskStatus.running,
                "indexing rag chunks",
                knowledge_file_id=knowledge_file_id,
                file_patch=build_running_file_patch(KnowledgeTaskStage.rag_indexing, task_id),
            )
            await RagHandler.index_milvus_documents(task.knowledge_id, chunks)
            if self.enable_elasticsearch:
                await RagHandler.index_es_documents(task.knowledge_id, chunks)
            await self._record_stage(
                task_id,
                KnowledgeTaskStage.rag_indexing,
                KnowledgeTaskStatus.running,
                "rag indexing completed",
                detail={"chunk_count": len(chunks)},
                knowledge_file_id=knowledge_file_id,
                file_patch=build_success_file_patch(KnowledgeTaskStage.rag_indexing, task_id),
            )

            if self.enable_graph_indexing:
                await self._record_stage(
                    task_id,
                    KnowledgeTaskStage.graph_extracting,
                    KnowledgeTaskStatus.running,
                    "graph extraction completed",
                    detail={"entity_count": 0, "relation_count": 0},
                    knowledge_file_id=knowledge_file_id,
                    file_patch=build_running_file_patch(KnowledgeTaskStage.graph_extracting, task_id),
                )
                await self._record_stage(
                    task_id,
                    KnowledgeTaskStage.graph_indexing,
                    KnowledgeTaskStatus.running,
                    "graph indexing completed",
                    detail={"entity_count": 0, "relation_count": 0},
                    knowledge_file_id=knowledge_file_id,
                    file_patch=build_success_file_patch(KnowledgeTaskStage.graph_indexing, task_id),
                )

            await KnowledgeTaskDao.mark_task_finished(
                task_id,
                status=KnowledgeTaskStatus.success,
                current_stage=KnowledgeTaskStage.completed,
                result_summary={"chunk_count": len(chunks)},
            )
            await KnowledgeTaskDao.create_task_event(
                task_id,
                KnowledgeTaskStage.completed,
                KnowledgeTaskStatus.success,
                "knowledge pipeline completed",
                {"chunk_count": len(chunks)},
            )
            await KnowledgeFileDao.update_pipeline_fields(
                knowledge_file_id,
                **build_success_file_patch(KnowledgeTaskStage.completed, task_id),
            )
        except Exception as err:
            logger.error(f"knowledge pipeline failed: task_id={task_id} error={err}")
            current_stage = getattr(task, "current_stage", KnowledgeTaskStage.failed)
            await KnowledgeTaskDao.mark_task_finished(
                task_id,
                status=KnowledgeTaskStatus.failed,
                current_stage=current_stage,
                error_message=str(err),
            )
            await KnowledgeTaskDao.create_task_event(
                task_id,
                current_stage,
                KnowledgeTaskStatus.failed,
                "knowledge pipeline failed",
                {"error": str(err)},
            )
            await KnowledgeFileDao.update_pipeline_fields(
                knowledge_file_id,
                **build_failed_file_patch(current_stage, task_id, str(err)),
            )
            raise
