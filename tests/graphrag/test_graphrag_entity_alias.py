import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src" / "backend"))

from zuno.services.graphrag.entity_alias import normalize_entity_name, resolve_alias


def test_normalize_entity_name_removes_article_and_parenthetical_suffix():
    assert normalize_entity_name("The Hork-Bajir Chronicles (novel)") == "hork bajir chronicles"


def test_normalize_entity_name_normalizes_hyphen_and_whitespace():
    assert normalize_entity_name("Hork-Bajir   Chronicles") == "hork bajir chronicles"


def test_resolve_alias_prefers_normalized_exact_match():
    resolved = resolve_alias("The Hork-Bajir Chronicles", ["Animorphs", "Hork Bajir Chronicles"])

    assert resolved["resolved_to"] == "Hork Bajir Chronicles"
    assert resolved["matched"] is True


def test_resolve_alias_keeps_simple_exact_match():
    resolved = resolve_alias("Shirley Temple", ["Shirley Temple", "Kiss and Tell (1945 film)"])

    assert resolved["resolved_to"] == "Shirley Temple"
    assert resolved["matched"] is True


def test_generic_entity_does_not_expand_via_alias():
    resolved = resolve_alias("Introduction", ["Introduction", "Animorphs"])

    assert resolved["matched"] is False
    assert resolved["resolved_to"] == "Introduction"
