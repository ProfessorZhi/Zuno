from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_workspace_and_knowledge_pages_expose_retrieval_modes():
    knowledge_page = (REPO_ROOT / "src/frontend/src/pages/knowledge/knowledge.vue").read_text(encoding="utf-8")
    workspace_page = (REPO_ROOT / "src/frontend/src/pages/workspace/defaultPage/defaultPage.vue").read_text(encoding="utf-8")
    retrieval_utils = (REPO_ROOT / "src/frontend/src/utils/retrieval.ts").read_text(encoding="utf-8")

    assert "default_retrieval_mode" in knowledge_page
    assert "retrievalModeOptions" in workspace_page
    assert "selectedRetrievalMode" in workspace_page
    assert "跟随知识库默认" in retrieval_utils


def test_knowledge_file_page_includes_task_status_and_retry_hooks():
    knowledge_file_page = (REPO_ROOT / "src/frontend/src/pages/knowledge/knowledge-file.vue").read_text(encoding="utf-8")

    assert "retryKnowledgeTaskAPI" in knowledge_file_page
    assert "taskDrawerVisible" in knowledge_file_page
    assert "last_task_id" in knowledge_file_page
