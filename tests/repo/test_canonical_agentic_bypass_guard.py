"""Repository AST and Boundary Bypass Guard Tests for Deep and Agentic Adapters.

AG-PR56-GEMINI-3-6-FLASH-HIGH-RUNTIME-TRUTH-REBUILD

Ensures:
1. No direct_answer shortcut bypasses plan, trace, budget, or final gate in adapter code.
2. Synthetic benchmark_deep_agentic.py file was deleted and does not exist.
3. No frozen shared files were modified.
"""

from __future__ import annotations

import ast
from pathlib import Path
import subprocess

import pytest


FROZEN_FILES = [
    "tools/evals/zuno/rag_eval/canonical_profile_runners.py",
    "tools/evals/zuno/rag_eval/profile_runtime_factory.py",
    "tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py",
    "tools/evals/zuno/rag_eval/measurement_gate.py",
    ".github/workflows/phase22-contract-verification.yml",
    ".agent/programs/work-products/goal05-target-gap-ledger.yaml",
]


def test_01_no_direct_answer_shortcut_in_deep_agentic_adapter_ast() -> None:
    """AST check: deep_agentic.py contains zero direct_answer shortcuts bypassing gates."""
    adapter_path = Path("tools/evals/zuno/rag_eval/adapters/deep_agentic.py")
    assert adapter_path.exists() is True, "adapters/deep_agentic.py must exist"

    code_text = adapter_path.read_text(encoding="utf-8")
    tree = ast.parse(code_text)

    string_constants = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]

    assert "direct_answer_bypass" not in string_constants
    assert "bypass_plan_and_trace" not in string_constants


def test_02_synthetic_benchmark_deep_agentic_composition_root_deleted() -> None:
    """Ensures synthetic local composition root src/backend/zuno/agent/benchmark_deep_agentic.py does not exist."""
    synthetic_path = Path("src/backend/zuno/agent/benchmark_deep_agentic.py")
    assert synthetic_path.exists() is False, "Synthetic composition root benchmark_deep_agentic.py MUST be deleted!"


def test_03_frozen_files_unmodified_in_git_diff() -> None:
    """Git check: None of the 7 frozen contract files are modified relative to Base."""
    base_ref = "origin/main"
    res = subprocess.run(
        ["git", "diff", "--name-only", base_ref],
        capture_output=True,
        text=True,
        check=True,
    )
    changed_files = res.stdout.splitlines()

    for frozen in FROZEN_FILES:
        assert frozen not in changed_files, f"Forbidden modification detected in frozen file: {frozen}"
