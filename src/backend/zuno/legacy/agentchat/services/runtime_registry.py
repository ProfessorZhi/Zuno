from __future__ import annotations

from copy import deepcopy
from typing import Any


_LOCAL_RUNTIME_SETTINGS: dict[str, dict[str, Any]] = {}


def register_local_runtime_settings(knowledge_id: str, runtime_settings: dict[str, Any]) -> None:
    _LOCAL_RUNTIME_SETTINGS[str(knowledge_id)] = dict(runtime_settings or {})


def get_local_runtime_settings(knowledge_id: str) -> dict[str, Any] | None:
    payload = _LOCAL_RUNTIME_SETTINGS.get(str(knowledge_id))
    return deepcopy(payload) if payload is not None else None


def clear_local_runtime_settings(knowledge_id: str | None = None) -> None:
    if knowledge_id is None:
        _LOCAL_RUNTIME_SETTINGS.clear()
        return
    _LOCAL_RUNTIME_SETTINGS.pop(str(knowledge_id), None)
