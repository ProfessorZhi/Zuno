from __future__ import annotations


def build_runtime_event(*, node: str, status: str, payload: dict | None = None) -> dict:
    return {
        "node": node,
        "status": status,
        "payload": payload or {},
    }
