import asyncio
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src" / "backend"))


def test_queue_message_contains_task_refs():
    from agentchat.services.queue.messages import build_task_message
    from agentchat.services.pipeline.models import KnowledgeTaskStage

    payload = build_task_message(
        task_id="task_1",
        knowledge_id="k_1",
        knowledge_file_id="f_1",
        stage=KnowledgeTaskStage.parsing,
        trace_id="trace_1",
    )
    assert payload["task_id"] == "task_1"
    assert payload["knowledge_id"] == "k_1"
    assert payload["knowledge_file_id"] == "f_1"
    assert payload["stage"] == KnowledgeTaskStage.parsing
    assert payload["trace_id"] == "trace_1"


def test_queue_workers_chain_stages():
    from agentchat.services.pipeline.models import KnowledgeTaskStage
    from agentchat.services.queue.workers import GraphWorker, IndexWorker, ParseWorker

    published_messages = []
    stage_calls = []

    class FakeQueueClient:
        async def publish(self, queue_name: str, payload: dict):
            published_messages.append((queue_name, payload))

    class FakePipelineManager:
        async def run_parse_stage(self, task_id: str):
            stage_calls.append(("parse", task_id))

        async def run_rag_index_stage(self, task_id: str):
            stage_calls.append(("index", task_id))

        async def run_graph_stage(self, task_id: str):
            stage_calls.append(("graph", task_id))

    payload = {
        "task_id": "task_1",
        "knowledge_id": "k_1",
        "knowledge_file_id": "f_1",
        "stage": KnowledgeTaskStage.parsing,
        "trace_id": "trace_1",
    }

    async def run_chain():
        queue_client = FakeQueueClient()
        manager = FakePipelineManager()
        parse_worker = ParseWorker(queue_client=queue_client, pipeline_manager=manager)
        index_worker = IndexWorker(queue_client=queue_client, pipeline_manager=manager)
        graph_worker = GraphWorker(queue_client=queue_client, pipeline_manager=manager)

        await parse_worker.handle(payload)
        assert published_messages[-1][1]["stage"] == KnowledgeTaskStage.rag_indexing

        await index_worker.handle(published_messages[-1][1])
        assert published_messages[-1][1]["stage"] == KnowledgeTaskStage.graph_indexing

        await graph_worker.handle(published_messages[-1][1])

    asyncio.run(run_chain())

    assert stage_calls == [
        ("parse", "task_1"),
        ("index", "task_1"),
        ("graph", "task_1"),
    ]
