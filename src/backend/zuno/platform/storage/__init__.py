from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zuno.platform.storage.durable import (
        DurableMinioObjectStore,
        ObjectCommitTicket,
        ObjectNotCommittedError,
        SessionObjectManifest,
    )
    from zuno.platform.storage.object_store import (
        MinioObjectStore,
        MultipartCleanupReceipt,
        MultipartPartReceipt,
        MultipartUploadSession,
        ObjectAuthorizationError,
        ObjectGovernanceReceipt,
        ObjectHashMismatchError,
        ObjectLifecycleReceipt,
        ObjectStoreReceipt,
    )
    from zuno.platform.services.storage import (
        LazyStorageClient,
        MinioClient,
        OSSClient,
        storage_client,
    )


_EXPORT_TO_MODULE = {
    "DurableMinioObjectStore": "zuno.platform.storage.durable",
    "LazyStorageClient": "zuno.platform.services.storage",
    "MinioObjectStore": "zuno.platform.storage.object_store",
    "MinioClient": "zuno.platform.services.storage",
    "MultipartCleanupReceipt": "zuno.platform.storage.object_store",
    "MultipartPartReceipt": "zuno.platform.storage.object_store",
    "MultipartUploadSession": "zuno.platform.storage.object_store",
    "ObjectAuthorizationError": "zuno.platform.storage.object_store",
    "ObjectCommitTicket": "zuno.platform.storage.durable",
    "ObjectGovernanceReceipt": "zuno.platform.storage.object_store",
    "ObjectHashMismatchError": "zuno.platform.storage.object_store",
    "ObjectLifecycleReceipt": "zuno.platform.storage.object_store",
    "ObjectNotCommittedError": "zuno.platform.storage.durable",
    "ObjectStoreReceipt": "zuno.platform.storage.object_store",
    "OSSClient": "zuno.platform.services.storage",
    "SessionObjectManifest": "zuno.platform.storage.durable",
    "storage_client": "zuno.platform.services.storage",
}

__all__ = [
    "DurableMinioObjectStore",
    "LazyStorageClient",
    "MinioObjectStore",
    "MinioClient",
    "MultipartCleanupReceipt",
    "MultipartPartReceipt",
    "MultipartUploadSession",
    "ObjectAuthorizationError",
    "ObjectCommitTicket",
    "ObjectGovernanceReceipt",
    "ObjectHashMismatchError",
    "ObjectLifecycleReceipt",
    "ObjectNotCommittedError",
    "ObjectStoreReceipt",
    "OSSClient",
    "SessionObjectManifest",
    "storage_client",
]


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_TO_MODULE.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
