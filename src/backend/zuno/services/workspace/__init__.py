from importlib import import_module
from typing import Any


_MODULE_EXPORTS = {
    "attachment_service": "attachment_service",
    "simple_agent": "simple_agent",
    "wechat_agent": "wechat_agent",
}

__all__ = list(_MODULE_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _MODULE_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(f"{__name__}.{module_name}")
    globals()[name] = module
    return module
