"""Regression tests for the ordered V3.1.3 closure-class gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/scripts/verify_red_blue_round_v313.py"
SPEC = importlib.util.spec_from_file_location("verify_red_blue_round_v313", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


@pytest.mark.parametrize(
    ("flags", "expected_primary"),
    [
        ((True, True, True, True), "A"),
        ((False, True, True, True), "I"),
        ((False, False, True, True), "E"),
        ((False, False, False, True), "X"),
    ],
)
def test_closure_class_uses_ordered_primary_gate(flags, expected_primary):
    primary, _secondary = MODULE.classify_closure_class(*flags)
    assert primary == expected_primary


def test_secondary_gaps_are_retained_without_changing_primary():
    primary, secondary = MODULE.classify_closure_class(False, False, True, True)
    assert primary == "E"
    assert secondary == ["X"]


def test_round_005_session_verifies():
    assert MODULE.verify() == []
