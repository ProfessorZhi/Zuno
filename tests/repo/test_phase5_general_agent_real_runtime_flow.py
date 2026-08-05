"""PHASE5 GeneralAgent real-runtime flow — retired in PHASE22.

The PHASE5 GeneralAgent real runtime flow (knowledge tool wiring and single
ReAct streaming loop) is no longer a product runtime. The PHASE22 backend
semantic legacy cleanup removed the class and its module; this test enforces
the retirement gate and pins the canonical replacement surface (knowledge
retrieval through the canonical runtime path).
"""

import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    runtime_root = str(BACKEND_ROOT)
    if runtime_root not in sys.path:
        sys.path.insert(0, runtime_root)


def test_retired_general_agent_runtime_is_not_importable() -> None:
    _ensure_runtime_paths()

    for module_name in [
        "zuno.agent.core.agents.general_agent",
        "zuno.agent.core.agents.react_agent",
        "zuno.agent.core.agents.plan_execute_agent",
    ]:
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        raise AssertionError(f"retired real runtime module is importable: {module_name}")


def test_canonical_runtime_factory_replaces_general_agent_wiring() -> None:
    _ensure_runtime_paths()

    from zuno.agent.runtime import RuntimeDependencyFactory, UnifiedAgentRuntimeService

    assembly = RuntimeDependencyFactory.for_completion()
    service = UnifiedAgentRuntimeService(store=assembly.store, dependencies=assembly.dependencies)

    assert assembly.dependencies is not None
    assert assembly.store is not None
    assert service.graph is not None
