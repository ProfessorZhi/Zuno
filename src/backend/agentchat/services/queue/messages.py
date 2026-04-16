from typing import TypedDict

from agentchat.services.pipeline.models import KnowledgeTaskStage


class KnowledgeTaskMessage(TypedDict):
    task_id: str
    knowledge_id: str
    knowledge_file_id: str
    stage: str
    trace_id: str


def build_task_message(
    *,
    task_id: str,
    knowledge_id: str,
    knowledge_file_id: str,
    stage: str,
    trace_id: str = "",
) -> KnowledgeTaskMessage:
    return {
        "task_id": task_id,
        "knowledge_id": knowledge_id,
        "knowledge_file_id": knowledge_file_id,
        "stage": stage,
        "trace_id": trace_id,
    }


def get_next_stage(stage: str) -> str | None:
    mapping = {
        KnowledgeTaskStage.parsing: KnowledgeTaskStage.rag_indexing,
        KnowledgeTaskStage.rag_indexing: KnowledgeTaskStage.graph_indexing,
    }
    return mapping.get(stage)
