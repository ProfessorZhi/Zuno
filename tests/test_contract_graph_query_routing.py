from pathlib import Path


def _contract_review_query_policy() -> dict:
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader

    projects_root = Path(__file__).resolve().parents[1] / "examples" / "graphrag-projects"
    project = GraphRAGProjectLoader(projects_root=projects_root).load("contract_review")
    return dict(project.settings["retrieval_policy"])


def test_contract_relation_question_is_graph_worthy():
    from zuno.services.graphrag.retriever import GraphRetriever

    query = (
        "\u4e3b\u670d\u52a1\u5408\u540c\u91cc\uff0c\u53d1\u751f\u6570\u636e\u6cc4\u9732\u540e"
        "\u4e59\u65b9\u9700\u8981\u5728\u591a\u4e45\u5185\u901a\u77e5\u7532\u65b9\uff1f"
        "\u8fd8\u9700\u8981\u4f9d\u636e\u54ea\u90e8\u6cd5\u5f8b\u914d\u5408\u5904\u7f6e\uff1f"
    )
    query_policy = _contract_review_query_policy()
    seeds = GraphRetriever._extract_query_seeds(query, query_policy)

    assert "\u5408\u540c" in seeds
    assert "\u4e59\u65b9" in seeds
    assert GraphRetriever._is_graph_worthy_query(query, seeds, query_policy) is True


def test_contract_title_alias_is_promoted_to_seed():
    from zuno.services.graphrag.retriever import GraphRetriever

    query = (
        "\u5916\u5305\u8fd0\u7ef4\u670d\u52a1\u5408\u540c\u4e2d\uff0c\u9ad8\u5371\u5b89\u5168\u4e8b\u4ef6"
        "\u53d1\u751f\u540e\uff0c\u4e59\u65b9\u5728\u65f6\u95f4\u7ebf\u4e0a\u8981\u5b8c\u6210"
        "\u54ea\u4e09\u4ef6\u4e8b\uff1f"
    )
    query_policy = _contract_review_query_policy()
    seeds = GraphRetriever._extract_query_seeds(query, query_policy)

    assert "\u5916\u5305\u8fd0\u7ef4\u670d\u52a1\u5408\u540c" in seeds
    assert "\u4e59\u65b9" in seeds
    assert GraphRetriever._is_graph_worthy_query(query, seeds, query_policy) is True


def test_contract_step_question_is_graph_worthy():
    from zuno.services.graphrag.retriever import GraphRetriever

    query = (
        "SaaS\u8ba2\u9605\u670d\u52a1\u5408\u540c\u7ec8\u6b62\u540e\uff0c"
        "\u4e59\u65b9\u5148\u8981\u505a\u4ec0\u4e48\uff0c\u518d\u8981\u505a\u4ec0\u4e48\uff1f"
    )
    query_policy = _contract_review_query_policy()
    seeds = GraphRetriever._extract_query_seeds(query, query_policy)

    assert "saas" in [seed.lower() for seed in seeds]
    assert "\u5408\u540c" in seeds
    assert "\u7ec8\u6b62" in seeds
    assert GraphRetriever._is_graph_worthy_query(query, seeds, query_policy) is True
