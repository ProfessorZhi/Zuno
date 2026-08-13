"""Repository tests for the derived semantic closure audit."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/scripts/verify_closure_semantic_audit_v3131.py"
SPEC = importlib.util.spec_from_file_location("verify_closure_semantic_audit_v3131", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_semantic_audit_verifies_all_questions_and_immutable_hashes():
    assert MODULE.verify() == []


def test_semantic_classifier_does_not_use_question_id_or_quota():
    assert MODULE.derive_class("DomainVersion D31 已提交、Checkpoint 仍在 D30") == "A"
    assert MODULE.derive_class("Graph 成本上升但跨文档任务没有稳定收益") == "E"
    assert MODULE.derive_class("Sandbox 崩溃且 Provider 没有返回结果") == "X"
    assert MODULE.derive_class("OCR Worker 在页 40 完成后崩溃") == "I"
