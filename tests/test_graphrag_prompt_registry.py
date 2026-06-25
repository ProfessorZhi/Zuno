from pathlib import Path


def _project(root: Path):
    project_dir = root / "legal"
    prompts_dir = project_dir / "prompts"
    prompts_dir.mkdir(parents=True)
    for name in [
        "extract_graph",
        "summarize",
        "community_report",
        "local_query",
        "global_query",
        "drift_query",
    ]:
        (prompts_dir / f"{name}.md").write_text(f"{name} prompt", encoding="utf-8")
    (project_dir / "settings.yaml").write_text(
        """
graphrag_project_id: legal
prompt_version: extract-v2
query_prompt_version: query-v3
status: ready
prompts:
  extract_graph: prompts/extract_graph.md
  summarize: prompts/summarize.md
  community_report: prompts/community_report.md
  local_query: prompts/local_query.md
  global_query: prompts/global_query.md
  drift_query: prompts/drift_query.md
""",
        encoding="utf-8",
    )


def test_prompt_registry_loads_project_prompt_categories(tmp_path):
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader
    from zuno.services.graphrag.prompts.registry import GraphRAGPromptRegistry

    _project(tmp_path)
    project = GraphRAGProjectLoader(projects_root=tmp_path).load("legal")
    registry = GraphRAGPromptRegistry.from_project(project)

    assert registry.categories() == [
        "community_report",
        "drift_query",
        "extract_graph",
        "global_query",
        "local_query",
        "summarize",
    ]
    assert registry.get("extract_graph").version == "extract-v2"
    assert registry.get("local_query").version == "query-v3"
    assert registry.get("extract_graph").text == "extract_graph prompt"


def test_prompt_registry_separates_indexing_and_query_prompt_impacts(tmp_path):
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader
    from zuno.services.graphrag.prompts.registry import GraphRAGPromptRegistry

    _project(tmp_path)
    project = GraphRAGProjectLoader(projects_root=tmp_path).load("legal")
    registry = GraphRAGPromptRegistry.from_project(project)

    assert registry.impact_for_change("extract_graph") == {
        "category": "extract_graph",
        "scope": "indexing",
        "requires_graph_rebuild": True,
        "requires_community_refresh": True,
    }
    assert registry.impact_for_change("community_report") == {
        "category": "community_report",
        "scope": "indexing",
        "requires_graph_rebuild": False,
        "requires_community_refresh": True,
    }
    assert registry.impact_for_change("local_query") == {
        "category": "local_query",
        "scope": "query",
        "requires_graph_rebuild": False,
        "requires_community_refresh": False,
    }


def test_prompt_registry_rejects_unknown_prompt_category(tmp_path):
    from zuno.services.graphrag.prompts.registry import GraphRAGPromptRegistry

    try:
        GraphRAGPromptRegistry.from_prompt_texts(
            graphrag_project_id="legal",
            prompt_version="extract-v1",
            query_prompt_version="query-v1",
            prompt_texts={"answer_template": "not graph prompt"},
        )
    except ValueError as err:
        assert "unknown prompt category: answer_template" in str(err)
    else:
        raise AssertionError("expected unknown prompt category to be rejected")
