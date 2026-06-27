from pathlib import Path

import pytest


def _write_project(
    root: Path,
    project_id: str = "legal",
    *,
    settings: str | None = None,
    prompts: dict[str, str] | None = None,
) -> Path:
    project_dir = root / project_id
    project_dir.mkdir(parents=True)
    if settings is not None:
        (project_dir / "settings.yaml").write_text(settings, encoding="utf-8")
    for relative_path, content in (prompts or {}).items():
        path = project_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return project_dir


def test_graphrag_project_loader_loads_settings_and_prompts(tmp_path):
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader

    _write_project(
        tmp_path,
        settings="""
graphrag_project_id: legal
prompt_version: extract-v2
index_version: idx-v7
query_method: local
query_prompt_version: query-v3
community_version: community-v2
document_hash: doc-sha
chunk_hash: chunk-sha
status: ready
prompts:
  extract_graph: prompts/extract_graph.md
  query: prompts/query.md
""",
        prompts={
            "prompts/extract_graph.md": "Extract graph facts.",
            "prompts/query.md": "Answer with citations.",
        },
    )

    project = GraphRAGProjectLoader(projects_root=tmp_path).load("legal")

    assert project.contract.graphrag_project_id == "legal"
    settings_path = Path(project.contract.settings_path)
    assert settings_path.name == "settings.yaml"
    assert settings_path.parent.name == "legal"
    assert project.contract.query_method == "local"
    assert project.contract.status == "ready"
    extract_prompt_path = Path(project.prompt_paths["extract_graph"])
    assert extract_prompt_path.name == "extract_graph.md"
    assert extract_prompt_path.parent.name == "prompts"
    assert extract_prompt_path.parent.parent.name == "legal"
    assert project.prompt_texts["query"] == "Answer with citations."
    assert project.readiness.ready is True
    assert project.readiness.errors == []


def test_graphrag_project_loader_reports_missing_settings(tmp_path):
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader

    _write_project(tmp_path, settings=None)

    with pytest.raises(ValueError, match="settings.yaml not found: legal"):
        GraphRAGProjectLoader(projects_root=tmp_path).load("legal")


def test_graphrag_project_loader_rejects_invalid_query_method(tmp_path):
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader

    _write_project(
        tmp_path,
        settings="""
graphrag_project_id: legal
query_method: community_global
""",
    )

    with pytest.raises(ValueError, match="query_method"):
        GraphRAGProjectLoader(projects_root=tmp_path).load("legal")


def test_graphrag_project_loader_exposes_not_ready_state_for_missing_prompt(tmp_path):
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader

    _write_project(
        tmp_path,
        settings="""
graphrag_project_id: legal
status: ready
prompts:
  extract_graph: prompts/extract_graph.md
""",
    )

    project = GraphRAGProjectLoader(projects_root=tmp_path).load("legal")

    assert project.readiness.ready is False
    assert project.readiness.status == "not_ready"
    assert project.readiness.errors == ["missing prompt: extract_graph"]
    assert project.prompt_paths == {}
    assert project.prompt_texts == {}


def test_knowledge_service_exposes_project_readiness_without_runtime_load(tmp_path):
    from zuno.api.services.knowledge import KnowledgeService

    _write_project(
        tmp_path,
        settings="""
graphrag_project_id: legal
status: ready
prompts:
  query: prompts/query.md
""",
        prompts={"prompts/query.md": "Answer."},
    )

    ready = KnowledgeService.describe_graphrag_project_readiness(
        {"graphrag_project_id": "legal"},
        projects_root=tmp_path,
    )
    missing = KnowledgeService.describe_graphrag_project_readiness(
        {"graphrag_project_id": "missing"},
        projects_root=tmp_path,
    )

    assert ready["ready"] is True
    assert ready["status"] == "ready"
    assert ready["graphrag_project_id"] == "legal"
    assert ready["prompt_names"] == ["query"]
    assert missing["ready"] is False
    assert missing["status"] == "not_ready"
    assert missing["errors"] == ["settings.yaml not found: missing"]
