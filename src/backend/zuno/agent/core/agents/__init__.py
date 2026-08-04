"""Agent core classes.

Only capabilities retained as internal step mechanisms live here after the
PHASE22 backend semantic legacy cleanup:

- ``StructuredResponseAgent`` is a deterministic structured-output capability
  used by production services (``agent_skill`` / ``mcp_server``) to obtain a
  schema-validated model answer. It never owns a top-level product run.

The retired product runtimes (``GeneralAgent``, ``ReactAgent``,
``PlanExecuteAgent``, ``CodeActAgent``, ``Text2SQLAgent``) were removed in
PHASE22; the Single Controller Product Runtime owns every product run.

The lazy export pattern is intentional: importing the package surface must not
pull heavy runtime modules (e.g. ``zuno.api.services``) into the import path.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.agent.core.agents.structured_response_agent import StructuredResponseAgent


_EXPORT_TO_MODULE = {
    "StructuredResponseAgent": "structured_response_agent",
}

__all__ = [
    "StructuredResponseAgent",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
