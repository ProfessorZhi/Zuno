from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimeDependencies:
    model_gateway: Any | None = None
    memory_engine: Any | None = None
    knowledge_runtime: Any | None = None
    capability_runtime: Any | None = None
    tool_control_plane: Any | None = None


__all__ = ["RuntimeDependencies"]
