import os
from pathlib import Path
from urllib.parse import urlparse

from loguru import logger

from agentchat.database.dao.knowledge_file import KnowledgeFileDao
from agentchat.database.dao.knowledge_task import KnowledgeTaskDao
from agentchat.api.services.knowledge import KnowledgeService
from agentchat.services.graphrag.client import Neo4jClient
from agentchat.services.graphrag.extractor import GraphExtractor
from agentchat.services.pipeline.models import KnowledgeTaskStage, KnowledgeTaskStatus
from agentchat.services.pipeline.stages import (
    build_failed_file_patch,
    build_running_file_patch,
    build_success_file_patch,
)
from agentchat.services.rag.handler import RagHandler
from agentchat.services.rag.parser import doc_parser
from agentchat.services.redis import redis_client
from agentchat.services.storage import storage_client
from agentchat.utils.file_utils import get_object_key_from_public_url, get_save_tempfile
from agentchat.utils.runtime_observability import RedisKeys


class KnowledgePipelineManager:
    def __init__(self, *, enable_graph_indexing: bool = True, enable_elasticsearch: bool = False):
        self.enable_graph_indexing = enable_graph_indexing
        self.enable_elasticsearch = enable_elasticsearch

    def _resolve_local_reference_path(self, file_name: str) -> str | None:
        if not file_name:
            return None

        candidate_roots = [
            Path("/app/agentchat/fixtures/knowledge_reindex"),
            Path(__file__).resolve().parents[2] / "fixtures" / "knowledge_reindex",
        ]
        for root in candidate_roots:
            candidate = root / os.path.basename(file_name)
            if candidate.exists():
                return str(candidate)
        return None

    async def _load_task(self, task_id: str):
        task = await KnowledgeTaskDao.select_task_by_id(task_id)
        if not task:
            raise ValueError(f"knowledge task not found: {task_id}")
        return task

    def _update_task_progress(self, task_id: str, stage: str, status: str, message: str):
        try:
            redis_client.set(
                RedisKeys.task_progress(task_id),
                {
                    "stage": stage,
                    "status": status,
                    "message": message,
                },
                expiration=7200,
            )
        except Exception as err:
            logger.warning(f"skip task progress cache update: task_id={task_id} error={err}")

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
        self._update_task_progress(task_id, stage, status, message)
        if knowledge_file_id and file_patch:
            await KnowledgeFileDao.update_pipeline_fields(knowledge_file_id, **file_patch)

    async def _resolve_file_path(self, task) -> tuple[str, bool]:
        payload = task.payload or {}
        file_path = payload.get("file_path")
        if file_path and os.path.exists(file_path):
            return file_path, False
        if file_path and not payload.get("oss_url"):
            return file_path, False

        oss_url = payload.get("oss_url", "")
        if not oss_url:
            raise ValueError("knowledge task payload missing oss_url")

        if oss_url.startswith("local://"):
            file_name = payload.get("file_name") or oss_url.removeprefix("local://")
            local_reference = self._resolve_local_reference_path(file_name)
            if local_reference:
                return local_reference, False
            raise ValueError(
                f"local source file not found for reindex: {file_name}. Please re-upload the file."
            )

        parsed = urlparse(oss_url)
        bucket_name = parsed.path.lstrip("/").split("/", 1)[0] if parsed.path else ""
        object_key = get_object_key_from_public_url(oss_url, bucket_name=bucket_name)
        file_name = payload.get("file_name") or os.path.basename(parsed.path) or f"{task.knowledge_file_id}.txt"
        local_file_path = get_save_tempfile(file_name)
        storage_client.download_file(object_key, local_file_path)
        return local_file_path, True

    async def _parse_chunks(self, task):
        file_path, cleanup = await self._resolve_file_path(task)
        try:
            payload = task.payload or {}
            knowledge_config = await KnowledgeService.get_knowledge_config(task.knowledge_id)
            chunks = await doc_parser.parse_doc_into_chunks(
                task.knowledge_file_id,
                file_path,
                task.knowledge_id,
                source_url=payload.get("oss_url"),
                knowledge_config=knowledge_config,
            )
            return chunks
        finally:
            if cleanup and os.path.exists(file_path):
                os.remove(file_path)

    async def mark_queued(self, task_id: str):
        task = await self._load_task(task_id)
        await self._record_stage(
            task_id,
            KnowledgeTaskStage.queued,
            KnowledgeTaskStatus.running,
            "knowledge pipeline queued",
            knowledge_file_id=task.knowledge_file_id,
            file_patch=build_running_file_patch(KnowledgeTaskStage.queued, task_id),
        )
        await KnowledgeTaskDao.mark_task_started(task_id, KnowledgeTaskStage.queued)

    async def run_parse_stage(self, task_id: str):
        task = await self._load_task(task_id)
        try:
            await self._record_stage(
                task_id,
                KnowledgeTaskStage.parsing,
                KnowledgeTaskStatus.running,
                "parsing knowledge file",
                knowledge_file_id=task.knowledge_file_id,
                file_patch=build_running_file_patch(KnowledgeTaskStage.parsing, task_id),
            )
            chunks = await self._parse_chunks(task)
            await KnowledgeTaskDao.update_task(task_id, result_summary={"chunk_count": len(chunks)})
            await self._record_stage(
                task_id,
                KnowledgeTaskStage.parsing,
                KnowledgeTaskStatus.running,
                "parsing completed",
                detail={"chunk_count": len(chunks)},
                knowledge_file_id=task.knowledge_file_id,
                file_patch=build_success_file_patch(KnowledgeTaskStage.parsing, task_id),
            )
            await self._record_stage(
                task_id,
                KnowledgeTaskStage.splitting,
                KnowledgeTaskStatus.running,
                "splitting chunks",
                detail={"chunk_count": len(chunks)},
            )
        except Exception as err:
            await self._fail_task(task, KnowledgeTaskStage.parsing, err)
            raise

    async def run_rag_index_stage(self, task_id: str):
        task = await self._load_task(task_id)
        try:
            runtime_settings = await KnowledgeService.get_runtime_settings(task.knowledge_id)
            await self._record_stage(
                task_id,
                KnowledgeTaskStage.rag_indexing,
                KnowledgeTaskStatus.running,
                "indexing rag chunks",
                knowledge_file_id=task.knowledge_file_id,
                file_patch=build_running_file_patch(KnowledgeTaskStage.rag_indexing, task_id),
            )
            chunks = await self._parse_chunks(task)
            await RagHandler.index_milvus_documents(
                task.knowledge_id,
                chunks,
                text_embedding_config=runtime_settings.get("text_embedding_config"),
                vl_embedding_config=runtime_settings.get("vl_embedding_config"),
            )
            if self.enable_elasticsearch:
                await RagHandler.index_es_documents(task.knowledge_id, chunks)
            await KnowledgeTaskDao.update_task(task_id, result_summary={"chunk_count": len(chunks)})
            await self._record_stage(
                task_id,
                KnowledgeTaskStage.rag_indexing,
                KnowledgeTaskStatus.running,
                "rag indexing completed",
                detail={"chunk_count": len(chunks)},
                knowledge_file_id=task.knowledge_file_id,
                file_patch=build_success_file_patch(KnowledgeTaskStage.rag_indexing, task_id),
            )
        except Exception as err:
            await self._fail_task(task, KnowledgeTaskStage.rag_indexing, err)
            raise

    async def run_graph_stage(self, task_id: str):
        task = await self._load_task(task_id)
        try:
            if self.enable_graph_indexing:
                chunks = await self._parse_chunks(task)
                await self._record_stage(
                    task_id,
                    KnowledgeTaskStage.graph_extracting,
                    KnowledgeTaskStatus.running,
                    "graph extracting",
                    knowledge_file_id=task.knowledge_file_id,
                    file_patch=build_running_file_patch(KnowledgeTaskStage.graph_extracting, task_id),
                )
                entity_count = 0
                relation_count = 0
                if Neo4jClient.is_enabled():
                    extractor = GraphExtractor()
                    client = Neo4jClient()
                    for chunk in chunks:
                        graph_data = await extractor.extract_from_chunk(chunk, task.knowledge_id)
                        for entity in graph_data["entities"]:
                            await client.upsert_entity(entity)
                        for relation in graph_data["relations"]:
                            await client.upsert_relation(relation)
                        entity_count += len(graph_data["entities"])
                        relation_count += len(graph_data["relations"])
                await self._record_stage(
                    task_id,
                    KnowledgeTaskStage.graph_extracting,
                    KnowledgeTaskStatus.running,
                    "graph extraction completed",
                    detail={"entity_count": entity_count, "relation_count": relation_count},
                )
                await self._record_stage(
                    task_id,
                    KnowledgeTaskStage.graph_indexing,
                    KnowledgeTaskStatus.running,
                    "graph indexing completed",
                    detail={"entity_count": entity_count, "relation_count": relation_count},
                    knowledge_file_id=task.knowledge_file_id,
                    file_patch=build_success_file_patch(KnowledgeTaskStage.graph_indexing, task_id),
                )

            result_summary = task.result_summary or {}
            await KnowledgeTaskDao.mark_task_finished(
                task_id,
                status=KnowledgeTaskStatus.success,
                current_stage=KnowledgeTaskStage.completed,
                result_summary=result_summary,
            )
            await KnowledgeTaskDao.create_task_event(
                task_id,
                KnowledgeTaskStage.completed,
                KnowledgeTaskStatus.success,
                "knowledge pipeline completed",
                result_summary,
            )
            self._update_task_progress(
                task_id,
                KnowledgeTaskStage.completed,
                KnowledgeTaskStatus.success,
                "knowledge pipeline completed",
            )
            await KnowledgeFileDao.update_pipeline_fields(
                task.knowledge_file_id,
                **build_success_file_patch(KnowledgeTaskStage.completed, task_id),
            )
        except Exception as err:
            await self._fail_task(task, KnowledgeTaskStage.graph_indexing, err)
            raise

    async def _fail_task(self, task, stage: str, err: Exception):
        logger.error(f"knowledge pipeline failed: task_id={task.id} stage={stage} error={err}")
        await KnowledgeTaskDao.mark_task_finished(
            task.id,
            status=KnowledgeTaskStatus.failed,
            current_stage=stage,
            error_message=str(err),
        )
        await KnowledgeTaskDao.create_task_event(
            task.id,
            stage,
            KnowledgeTaskStatus.failed,
            "knowledge pipeline failed",
            {"error": str(err)},
        )
        self._update_task_progress(task.id, stage, KnowledgeTaskStatus.failed, str(err))
        await KnowledgeFileDao.update_pipeline_fields(
            task.knowledge_file_id,
            **build_failed_file_patch(stage, task.id, str(err)),
        )

    async def run_sync(self, task_id: str, *, file_path: str | None = None):
        task = await self._load_task(task_id)
        if file_path:
            payload = dict(getattr(task, "payload", {}) or {})
            payload["file_path"] = file_path
            await KnowledgeTaskDao.update_task(task_id, payload=payload)
        await self.mark_queued(task_id)
        await self.run_parse_stage(task_id)
        await self.run_rag_index_stage(task_id)
        await self.run_graph_stage(task_id)
