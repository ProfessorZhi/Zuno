import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src" / "backend"))

from zuno.services.graphrag.retriever import GraphRetriever


def test_comparison_question_prefers_attribute_path():
    comparison_path = {
        "source": "Scott Derrickson",
        "target": "American",
        "relation_type": "nationality",
        "chunk_ids": ["c1"],
    }
    noisy_path = {
        "source": "Scott Derrickson",
        "target": "Sinister",
        "relation_type": "directed",
        "chunk_ids": ["c2"],
    }

    assert GraphRetriever._score_path(
        "Were Scott Derrickson and Ed Wood of the same nationality?",
        comparison_path,
        ["Scott Derrickson", "Ed Wood"],
    ) > GraphRetriever._score_path(
        "Were Scott Derrickson and Ed Wood of the same nationality?",
        noisy_path,
        ["Scott Derrickson", "Ed Wood"],
    )


def test_bridge_relation_question_prefers_two_hop_relation_path():
    bridge_path = {
        "source": "Big Stone Gap (film)",
        "target": "Adriana Trigiani",
        "relation_type": "director",
        "chunk_ids": ["c1"],
    }
    noisy_path = {
        "source": "Big Stone Gap (film)",
        "target": "Romantic comedy",
        "relation_type": "genre",
        "chunk_ids": ["c2"],
    }

    assert GraphRetriever._score_path(
        'The director of the romantic comedy "Big Stone Gap" is based in what New York city?',
        bridge_path,
        ["Big Stone Gap", "Adriana Trigiani"],
    ) > GraphRetriever._score_path(
        'The director of the romantic comedy "Big Stone Gap" is based in what New York city?',
        noisy_path,
        ["Big Stone Gap", "Adriana Trigiani"],
    )


def test_generic_entity_path_is_penalized():
    generic_path = {
        "source": "Introduction",
        "target": "Overview",
        "relation_type": "related_to",
        "chunk_ids": ["c1"],
    }
    real_path = {
        "source": "Shirley Temple",
        "target": "United States Ambassador",
        "relation_type": "government_position",
        "chunk_ids": ["c2"],
    }

    assert GraphRetriever._score_path(
        "What government position was held by Shirley Temple?",
        real_path,
        ["Shirley Temple"],
    ) > GraphRetriever._score_path(
        "What government position was held by Shirley Temple?",
        generic_path,
        ["Shirley Temple"],
    )


def test_document_score_uses_graph_support_and_path_score():
    query_terms = {"big", "stone", "gap", "director", "city"}
    strong_doc = {
        "file_name": "Adriana Trigiani",
        "content": "Adriana Trigiani lives in New York and directed Big Stone Gap.",
        "summary": "",
        "graph_support_count": 3,
        "graph_seed_hit_count": 3,
        "graph_file_focus": 2,
        "graph_path_score": 12,
    }
    weak_doc = {
        "file_name": "Romantic comedy",
        "content": "A romantic comedy film.",
        "summary": "",
        "graph_support_count": 1,
        "graph_seed_hit_count": 1,
        "graph_file_focus": 0,
        "graph_path_score": 1,
    }

    assert GraphRetriever._score_document(
        'The director of the romantic comedy "Big Stone Gap" is based in what New York city?',
        query_terms,
        strong_doc,
    ) > GraphRetriever._score_document(
        'The director of the romantic comedy "Big Stone Gap" is based in what New York city?',
        query_terms,
        weak_doc,
    )


def test_path_ranking_is_stable_for_identical_paths():
    path = {
        "source": "Scott Derrickson",
        "target": "American",
        "relation_type": "nationality",
        "chunk_ids": ["c1"],
    }

    left = GraphRetriever._score_path(
        "Were Scott Derrickson and Ed Wood of the same nationality?",
        path,
        ["Scott Derrickson", "Ed Wood"],
    )
    right = GraphRetriever._score_path(
        "Were Scott Derrickson and Ed Wood of the same nationality?",
        path,
        ["Scott Derrickson", "Ed Wood"],
    )

    assert left == right
