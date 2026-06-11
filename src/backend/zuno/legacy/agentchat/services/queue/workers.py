from agentchat.services.pipeline.models import KnowledgeTaskStage
from agentchat.services.queue.client import get_queue_names
from agentchat.services.queue.messages import build_task_message


class ParseWorker:
    def __init__(self, *, queue_client, pipeline_manager, queue_names: dict[str, str] | None = None):
        self.queue_client = queue_client
        self.pipeline_manager = pipeline_manager
        self.queue_names = queue_names or get_queue_names()

    async def handle(self, payload: dict):
        await self.pipeline_manager.run_parse_stage(payload["task_id"])
        await self.queue_client.publish(
            self.queue_names["index"],
            build_task_message(
                task_id=payload["task_id"],
                knowledge_id=payload["knowledge_id"],
                knowledge_file_id=payload["knowledge_file_id"],
                stage=KnowledgeTaskStage.rag_indexing,
                trace_id=payload.get("trace_id", ""),
            ),
        )


class IndexWorker:
    def __init__(self, *, queue_client, pipeline_manager, queue_names: dict[str, str] | None = None):
        self.queue_client = queue_client
        self.pipeline_manager = pipeline_manager
        self.queue_names = queue_names or get_queue_names()

    async def handle(self, payload: dict):
        await self.pipeline_manager.run_rag_index_stage(payload["task_id"])
        await self.queue_client.publish(
            self.queue_names["graph"],
            build_task_message(
                task_id=payload["task_id"],
                knowledge_id=payload["knowledge_id"],
                knowledge_file_id=payload["knowledge_file_id"],
                stage=KnowledgeTaskStage.graph_indexing,
                trace_id=payload.get("trace_id", ""),
            ),
        )


class GraphWorker:
    def __init__(self, *, queue_client, pipeline_manager, queue_names: dict[str, str] | None = None):
        self.queue_client = queue_client
        self.pipeline_manager = pipeline_manager
        self.queue_names = queue_names or get_queue_names()

    async def handle(self, payload: dict):
        _ = self.queue_client, self.queue_names
        await self.pipeline_manager.run_graph_stage(payload["task_id"])
