import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICE_API_ROOT = REPO_ROOT / "src" / "backend"
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    for runtime_root in (str(BACKEND_ROOT),):
        if runtime_root not in sys.path:
            sys.path.insert(0, runtime_root)


def test_zuno_agent_runtime_facade_is_removed_from_current_source():
    _ensure_runtime_paths()

    runtime_file = BACKEND_ROOT / "zuno" / "core" / "runtime" / "agent_runtime.py"
    runtime_module = importlib.import_module("zuno.agent.core.runtime")
    core_module = importlib.import_module("zuno.agent.core")

    assert not runtime_file.exists()
    assert "AgentRuntime" not in getattr(runtime_module, "__all__", [])
    assert "AgentRuntime" not in getattr(core_module, "__all__", [])


def test_retired_general_agent_domain_runtime_paths_are_gone():
    """The retired GeneralAgent domain runtime paths must not be importable.

    PHASE5 used to bind the GeneralAgent directly to project query runtimes;
    after the PHASE22 backend semantic legacy cleanup those paths are retired
    and any import attempt must fail closed.
    """
    _ensure_runtime_paths()

    for module_name in [
        "zuno.agent.core.agents.general_agent",
        "zuno.agent.core.agents.react_agent",
        "zuno.agent.core.agents.plan_execute_agent",
        "zuno.agent.core.agents.codeact_agent",
    ]:
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        raise AssertionError(f"retired domain runtime module is importable: {module_name}")
