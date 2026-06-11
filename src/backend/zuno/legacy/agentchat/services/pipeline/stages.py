from agentchat.database.models.knowledge_file import Status as KnowledgeFileStatus
from agentchat.services.pipeline.models import KnowledgeTaskStage


def build_running_file_patch(stage: str, task_id: str) -> dict:
    patch = {
        "last_task_id": task_id,
        "last_error": None,
        "status": KnowledgeFileStatus.process,
    }
    if stage == KnowledgeTaskStage.parsing:
        patch["parse_status"] = KnowledgeFileStatus.process
    elif stage == KnowledgeTaskStage.rag_indexing:
        patch["rag_index_status"] = KnowledgeFileStatus.process
    elif stage in {KnowledgeTaskStage.graph_extracting, KnowledgeTaskStage.graph_indexing}:
        patch["graph_index_status"] = KnowledgeFileStatus.process
    return patch


def build_success_file_patch(stage: str, task_id: str) -> dict:
    patch = {
        "last_task_id": task_id,
        "last_error": None,
    }
    if stage == KnowledgeTaskStage.parsing:
        patch["parse_status"] = KnowledgeFileStatus.success
    elif stage == KnowledgeTaskStage.rag_indexing:
        patch["rag_index_status"] = KnowledgeFileStatus.success
    elif stage == KnowledgeTaskStage.graph_indexing:
        patch["graph_index_status"] = KnowledgeFileStatus.success
        patch["status"] = KnowledgeFileStatus.success
    elif stage == KnowledgeTaskStage.completed:
        patch["status"] = KnowledgeFileStatus.success
    return patch


def build_failed_file_patch(stage: str, task_id: str, error_message: str) -> dict:
    patch = {
        "last_task_id": task_id,
        "last_error": error_message,
        "status": KnowledgeFileStatus.fail,
    }
    if stage == KnowledgeTaskStage.parsing:
        patch["parse_status"] = KnowledgeFileStatus.fail
    elif stage == KnowledgeTaskStage.rag_indexing:
        patch["rag_index_status"] = KnowledgeFileStatus.fail
    elif stage in {KnowledgeTaskStage.graph_extracting, KnowledgeTaskStage.graph_indexing}:
        patch["graph_index_status"] = KnowledgeFileStatus.fail
    return patch
