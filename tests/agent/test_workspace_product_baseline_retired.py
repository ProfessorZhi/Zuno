"""PHASE22 runtime cutover: product_baseline.py must be retired from the production tree.

``src/backend/zuno/agent/product_baseline.py`` imported
``AgentControlRuntime`` and ``RuntimeObservation`` from
``zuno.agent.control_runtime``. The file had no production caller
(only ``tests/evals/test_agentic_graphrag_regression_summary.py``
imported it). This slice moves the file to
``tools/evals/zuno/agent/product_baseline.py`` (tests/evals internal
tooling).
"""

from __future__ import annotations

import os
import pathlib


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_src_product_baseline_is_retired() -> None:
    assert not (
        REPO_ROOT / "src/backend/zuno/agent/product_baseline.py"
    ).exists(), (
        "src/backend/zuno/agent/product_baseline.py must be retired "
        "out of the production tree."
    )


def test_evals_product_baseline_lives_under_tests() -> None:
    assert (
        REPO_ROOT / "tools/evals/zuno/agent/product_baseline.py"
    ).exists(), (
        "product_baseline.py must live under tools/evals/zuno/agent/ "
        "(tests/evals internal tooling location)."
    )


def test_evals_agent_package_is_a_real_package() -> None:
    pkg = REPO_ROOT / "tools/evals/zuno/agent/__init__.py"
    assert pkg.exists(), (
        "tools/evals/zuno/agent/ must be a real Python package so "
        "tests can import its scenarios."
    )


def test_agent_control_runtime_has_no_production_caller() -> None:
    """Walk the production tree and ensure no module imports
    AgentControlRuntime."""
    import ast

    production_root = REPO_ROOT / "src" / "backend"
    offenders = []
    for path in production_root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        # the harness module itself is excluded
        if rel == "src/backend/zuno/agent/control_runtime.py":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            target = None
            if isinstance(node, ast.ImportFrom):
                target = (node.module or "") + "." + ",".join(
                    a.name for a in node.names
                )
            elif isinstance(node, ast.Import):
                target = ",".join(a.name for a in node.names)
            if target and "AgentControlRuntime" in target:
                offenders.append(rel)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id == "AgentControlRuntime":
                    offenders.append(rel)
    assert not offenders, (
        "Production tree must not import AgentControlRuntime. Offenders: "
        f"{offenders}"
    )