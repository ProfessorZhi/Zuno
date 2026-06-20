import asyncio
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def test_same_nationality_question_is_graph_worthy():
    from zuno.services.graphrag.retriever import GraphRetriever

    query = "Were Scott Derrickson and Ed Wood of the same nationality?"
    seeds = GraphRetriever._extract_query_seeds(query)

    assert GraphRetriever._is_graph_worthy_query(query, seeds) is True


def test_mother_of_director_question_is_graph_worthy():
    from zuno.services.graphrag.retriever import GraphRetriever

    query = "Who is the mother of the director of film X?"
    seeds = GraphRetriever._extract_query_seeds(query)

    assert GraphRetriever._is_graph_worthy_query(query, seeds) is True


def test_spouse_of_performer_question_is_graph_worthy():
    from zuno.services.graphrag.retriever import GraphRetriever

    query = "Who is the spouse of the performer of song Z?"
    seeds = GraphRetriever._extract_query_seeds(query)

    assert GraphRetriever._is_graph_worthy_query(query, seeds) is True


def test_simple_definition_question_is_not_graph_worthy():
    from zuno.services.graphrag.retriever import GraphRetriever

    query = "What is Redis?"
    seeds = GraphRetriever._extract_query_seeds(query)

    assert GraphRetriever._is_graph_worthy_query(query, seeds) is False


def test_simple_date_lookup_is_not_graph_worthy():
    from zuno.services.graphrag.retriever import GraphRetriever

    query = "When was Big Stone Gap released?"
    seeds = GraphRetriever._extract_query_seeds(query)

    assert GraphRetriever._is_graph_worthy_query(query, seeds) is False


def test_query_processor_marks_comparison_as_relation_question():
    from zuno.services.retrieval.retrievers import QueryProcessor

    payload = asyncio.run(QueryProcessor().process("Were Scott Derrickson and Ed Wood of the same nationality?"))

    assert payload["query_features"]["relation_question"] is True


def test_query_processor_marks_bridge_relation_as_relation_question():
    from zuno.services.retrieval.retrievers import QueryProcessor

    payload = asyncio.run(QueryProcessor().process('The director of the romantic comedy "Big Stone Gap" is based in what New York city?'))

    assert payload["query_features"]["relation_question"] is True


def test_rag_graph_deep_comparison_does_not_stay_standard_rag():
    from zuno.services.retrieval.models import ProcessedQuery, RetrievalRequest
    from zuno.services.retrieval.planner import RetrievalPlanner

    planner = RetrievalPlanner(enable_keyword_recall=True)
    plan = planner.build_plan(
        RetrievalRequest(query="Were Scott Derrickson and Ed Wood of the same nationality?", knowledge_ids=["kb_1"], mode="rag_graph_deep"),
        ProcessedQuery(
            original_query="Were Scott Derrickson and Ed Wood of the same nationality?",
            normalized_query="Were Scott Derrickson and Ed Wood of the same nationality?",
            rewritten_queries=["Were Scott Derrickson and Ed Wood of the same nationality?"],
            intent_labels=[],
            query_features={"relation_question": True, "global_question": False, "evidence_required": False},
            route_hints=[],
        ),
        knowledge_capability="rag_graph",
    )

    assert plan.internal_route != "standard_rag"


def test_rag_graph_deep_bridge_relation_does_not_stay_standard_rag():
    from zuno.services.retrieval.models import ProcessedQuery, RetrievalRequest
    from zuno.services.retrieval.planner import RetrievalPlanner

    planner = RetrievalPlanner(enable_keyword_recall=True)
    plan = planner.build_plan(
        RetrievalRequest(query="Who is the mother of the director of film X?", knowledge_ids=["kb_1"], mode="rag_graph_deep"),
        ProcessedQuery(
            original_query="Who is the mother of the director of film X?",
            normalized_query="Who is the mother of the director of film X?",
            rewritten_queries=["Who is the mother of the director of film X?"],
            intent_labels=[],
            query_features={"relation_question": True, "global_question": False, "evidence_required": False},
            route_hints=[],
        ),
        knowledge_capability="rag_graph",
    )

    assert plan.internal_route != "standard_rag"
