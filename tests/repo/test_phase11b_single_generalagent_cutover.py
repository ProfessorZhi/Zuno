"""PHASE11b single-GeneralAgent cutover — now a retirement gate.

The single-GeneralAgent product runtime was retired in the PHASE22 backend
semantic legacy cleanup. The cutover contract is now enforced as a fail-closed
gate: the retired module must not exist and must not be importable, and the
canonical Single Controller Product Runtime must be the only top-level
product runtime surface.
"""

import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))


RETIRED_MODULES = [
    "zuno.agent.core.agents.general_agent",
    "zuno.agent.core.agents.react_agent",
    "zuno.agent.core.agents.plan_execute_agent",
    "zuno.agent.core.agents.codeact_agent",
    "zuno.agent.core.agents.text2sql_agent",
    "zuno.agent.state",
    "zuno.agent.streaming",
]


def test_retired_general_agent_modules_cannot_be_imported() -> None:
    _ensure_runtime_paths()

    for module_name in RETIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        raise AssertionError(f"retired GeneralAgent-family module is importable: {module_name}")


def test_general_agent_export_is_gone_from_canonical_surfaces() -> None:
    _ensure_runtime_paths()

    import zuno.agent as agent
    import zuno.agent.core as core
    import zuno.agent.core.agents as agents

    for name in ("GeneralAgent", "AgentConfig", "StreamAgentState", "EmitEventAgentMiddleware"):
        assert name not in agent.__all__, f"zuno.agent still exports retired symbol: {name}"
        assert name not in core.__all__, f"zuno.agent.core still exports retired symbol: {name}"
        assert name not in agents.__all__, f"zuno.agent.core.agents still exports retired symbol: {name}"
        assert not hasattr(agent, name), f"zuno.agent still exposes attribute: {name}"
        assert not hasattr(core, name), f"zuno.agent.core still exposes attribute: {name}"
        assert not hasattr(agents, name), f"zuno.agent.core.agents still exposes attribute: {name}"


def test_single_controller_runtime_is_the_top_level_product_runtime() -> None:
    _ensure_runtime_paths()

    from zuno.agent.runtime import UnifiedAgentRuntimeService, build_agent_graph
    from zuno.agent.runtime.planning import RuntimePlanner
    from zuno.agent.runtime.phase08 import build_phase08_step_graph
    from zuno.agent.harness import SingleControllerRuntimeHarness

    assert SingleControllerRuntimeHarness is not None
    assert callable(build_agent_graph)
    assert callable(build_phase08_step_graph)
    assert RuntimePlanner is not None
    assert UnifiedAgentRuntimeService is not None
