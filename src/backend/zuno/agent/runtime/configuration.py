from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RuntimeFactoryConfig:
    sqlite_path: Path | None = None
    enable_memory: bool = True
    enable_local_tool_runtime: bool = True
    enable_default_model_gateway: bool = True
    knowledge_index_runtime: object | None = None


__all__ = ["RuntimeFactoryConfig"]
