from __future__ import annotations

"""PHASE22 Import Smoke Test for the workspace composition root.

Coordinator P1 blocker: ``WorkspaceTaskRuntimeService``
``configure_workspace_agent_product_composition`` had two stacked
``@classmethod`` decorators and the module executed the composition at import
time. This test proves:

- the module imports without executing any global composition mutation;
- the composition initializer is a callable classmethod (no TypeError);
- repeated initialization is idempotent;
- importing never requires a live PostgreSQL connection;
- test reset never creates a Product Composition.
"""

from pathlib import Path
import subprocess
import sys

import pytest

import zuno.api.services.workspace_task_runtime as workspace_task_runtime_module
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
from zuno.platform.services.workspace.single_controller_runtime import (
    configure_workspace_product_composition,
    get_workspace_product_composition,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = str(REPO_ROOT / "src" / "backend")


def test_module_imports_without_composition_mutation() -> None:
    """Importing the module must not configure the product composition."""
    assert workspace_task_runtime_module.WorkspaceTaskRuntimeService is WorkspaceTaskRuntimeService
    # Import alone must not have bound a product composition (the binding is
    # explicit at application startup, never an import side effect).
    assert get_workspace_product_composition() is None


def test_composition_initializer_is_a_callable_classmethod() -> None:
    """The double-@classmethod defect must be gone: the attribute is callable."""
    initializer = WorkspaceTaskRuntimeService.configure_workspace_agent_product_composition
    assert callable(initializer)
    assert type(initializer).__name__ == "method"


def test_composition_initialization_does_not_raise_typeerror() -> None:
    """Explicit initialization succeeds without a PostgreSQL connection.

    The initializer only builds SQLAlchemy engine objects / UoW factories; no
    connection is opened during composition wiring.
    """
    configure_workspace_product_composition(None)
    try:
        WorkspaceTaskRuntimeService.configure_workspace_agent_product_composition()
    except TypeError as err:  # pragma: no cover - regression guard
        pytest.fail(f"composition initializer raised TypeError: {err}")
    assert get_workspace_product_composition() is not None


def test_composition_initialization_is_idempotent() -> None:
    """Repeated initialization is idempotent and never throws."""
    configure_workspace_product_composition(None)
    first = WorkspaceTaskRuntimeService.configure_workspace_agent_product_composition()
    composition_after_first = get_workspace_product_composition()
    second = WorkspaceTaskRuntimeService.configure_workspace_agent_product_composition()
    composition_after_second = get_workspace_product_composition()
    assert first is None and second is None
    # Idempotent: the second call rebinds an equivalent composition (same
    # store, same infrastructure bindings, same fail-closed stance) and never
    # throws. (UoW factories / the engine-backed approval sink are fresh
    # objects per call, so equivalence is asserted on the meaningful binding
    # fields, not object identity.)
    assert composition_after_first.store is composition_after_second.store
    assert composition_after_first.security_approval_sink is not None
    assert composition_after_second.security_approval_sink is not None
    assert (
        composition_after_first.security_approval_sink.engine
        is composition_after_second.security_approval_sink.engine
    )
    assert composition_after_first.security_epoch_ref == composition_after_second.security_epoch_ref
    assert composition_after_first.approval_flow == composition_after_second.approval_flow
    assert (
        composition_after_first.security_decision_resolver
        is composition_after_second.security_decision_resolver
    )
    assert (
        composition_after_first.budget_decision_resolver
        is composition_after_second.budget_decision_resolver
    )
    assert composition_after_first.dynamic_dag_planner is composition_after_second.dynamic_dag_planner


def test_reset_runtime_state_does_not_create_product_composition() -> None:
    """Test reset must never (re-)create a Product Composition."""
    configure_workspace_product_composition(None)
    WorkspaceTaskRuntimeService.configure_workspace_agent_product_composition()
    assert get_workspace_product_composition() is not None
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    assert get_workspace_product_composition() is None


def test_no_side_effect_composition_on_fresh_import() -> None:
    """A fresh interpreter import never mutates the composition global."""
    code = (
        "import sys; sys.path.insert(0, %r)\n"
        "import zuno.api.services.workspace_task_runtime as m\n"
        "from zuno.platform.services.workspace.single_controller_runtime import (\n"
        "    get_workspace_product_composition,\n"
        ")\n"
        "print(get_workspace_product_composition())\n"
    ) % BACKEND_ROOT
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "None" in proc.stdout
