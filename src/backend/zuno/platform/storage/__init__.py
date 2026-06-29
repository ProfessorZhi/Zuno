from __future__ import annotations

from importlib import import_module
from typing import Any


_EXPORT_TO_MODULE = {
    "LazyStorageClient": "zuno.platform.services.storage",
    "MinioClient": "zuno.platform.services.storage",
    "OSSClient": "zuno.platform.services.storage",
    "storage_client": "zuno.platform.services.storage",
}

__all__ = [
    "LazyStorageClient",
    "MinioClient",
    "OSSClient",
    "storage_client",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
