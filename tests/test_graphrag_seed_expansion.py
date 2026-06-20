import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src" / "backend"))

from zuno.services.graphrag.retriever import GraphRetriever


def test_seed_expansion_can_use_baseline_title_when_query_seed_is_weak():
    candidate_context = {
        "documents": [
            {"title": "Animorphs", "file_name": "Animorphs"},
            {"title": "The Hork-Bajir Chronicles", "file_name": "The Hork-Bajir Chronicles"},
        ]
    }

    seeds = GraphRetriever._build_seed_entities_with_source(
        "What science fantasy young adult series has companion books about alien species?",
        candidate_context=candidate_context,
        max_seed_entities=8,
    )

    values = [item["value"] for item in seeds]

    assert "Animorphs" in values
    assert "The Hork-Bajir Chronicles" in values


def test_seed_expansion_deduplicates_and_tracks_source():
    candidate_context = {
        "documents": [
            {"title": "Shirley Temple", "file_name": "Shirley Temple"},
            {"title": "Shirley Temple", "file_name": "Shirley Temple"},
        ]
    }

    seeds = GraphRetriever._build_seed_entities_with_source(
        "What government position was held by Shirley Temple?",
        candidate_context=candidate_context,
        max_seed_entities=8,
    )

    matching = [item for item in seeds if item["value"] == "Shirley Temple"]

    assert len(matching) == 1
    assert matching[0]["source"] in {"query", "baseline_title"}


def test_seed_expansion_skips_generic_entities():
    candidate_context = {
        "documents": [
            {"title": "Introduction", "file_name": "Introduction"},
            {"title": "Overview", "file_name": "Overview"},
        ]
    }

    seeds = GraphRetriever._build_seed_entities_with_source(
        "What science fantasy young adult series has companion books?",
        candidate_context=candidate_context,
        max_seed_entities=8,
    )

    values = {item["value"] for item in seeds}

    assert "Introduction" not in values
    assert "Overview" not in values


def test_seed_expansion_respects_max_seed_entities():
    candidate_context = {
        "documents": [{"title": f"Doc {idx}", "file_name": f"Doc {idx}"} for idx in range(1, 10)]
    }

    seeds = GraphRetriever._build_seed_entities_with_source(
        "Who is the mother of the director of film X?",
        candidate_context=candidate_context,
        max_seed_entities=4,
    )

    assert len(seeds) == 4


def test_extract_query_seeds_remains_backward_compatible():
    seeds = GraphRetriever._extract_query_seeds("Were Scott Derrickson and Ed Wood of the same nationality?")

    assert isinstance(seeds, list)
    assert "Scott" in seeds
