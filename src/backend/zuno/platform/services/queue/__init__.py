from __future__ import annotations

__all__ = ["client", "messages", "runner", "workers"]


def __getattr__(name: str):
    if name in __all__:
        from importlib import import_module

        return import_module(f"{__name__}.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
