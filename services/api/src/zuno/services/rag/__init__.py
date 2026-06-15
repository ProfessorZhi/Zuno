from importlib import import_module
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_SUBMODULES = {
    "es_client",
    "handler",
    "parser",
    "rerank",
    "retrieval",
    "vector_db",
}

__all__ = sorted(_SUBMODULES)


def __getattr__(name: str):
    if name in _SUBMODULES:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
