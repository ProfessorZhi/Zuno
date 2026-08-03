from __future__ import annotations

"""Object Store runtime binding — single formal ownership declaration.

PHASE22 runtime-binding resolution. The repository historically surfaced four
``*ObjectStore`` classes; the preflight read-only audit (CC-DS-1) reported
``BLOCKED_WITH_EXACT_GAP: object store owner non-unique`` because it counted
class names instead of runtime roles. This module is the machine-readable
ownership fact source that resolves the surface without deleting classes:

===========  ==================================================  =================
Role         Class                                               Deployment class
===========  ==================================================  =================
Port         ``DurableObjectStore`` (Protocol,                  n/a (typed port)
             knowledge.ingestion.source_object_upload)
Production   ``DurableMinioObjectStore``                        SERVER_PRODUCT
adapter      (platform.storage.durable)                         (canonical owner)
Physical     ``MinioObjectStore``                               SERVER_PRODUCT
transport    (platform.storage.object_store)                    (owned by Durable)
Local        ``LocalObjectStore``                               DEVELOPER_CI
adapter      (knowledge.storage.local_object_store)             (Local/Test only)
===========  ==================================================  =================

Rules enforced here:

* The formal Object Store Port is ``DurableObjectStore`` (stage/commit ticket).
* The sole production adapter is ``DurableMinioObjectStore``; it is the only
  adapter allowed to be the composition-root owner in the server profile.
* ``LocalObjectStore`` is bound to the ``DEVELOPER_CI`` profile only; building a
  local adapter under ``SERVER_PRODUCT`` fails closed.
* When the production binding is not configured (mode, endpoint or credential
  missing) resolution returns ``None`` / raises ``ObjectStoreBindingMissing``:
  fail closed, never a silent fallback to the local filesystem.
"""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Engine

# --- Roles and deployment classes -------------------------------------------


@dataclass(frozen=True, slots=True)
class ObjectStoreAdapterDeclaration:
    """One entry in the formal object store ownership surface."""

    role: str
    adapter_name: str
    import_path: str
    deployment_class: str
    authoritative: bool
    description: str


OBJECT_STORE_PORT_NAME = "DurableObjectStore"

OBJECT_STORE_OWNERSHIP: tuple[ObjectStoreAdapterDeclaration, ...] = (
    ObjectStoreAdapterDeclaration(
        role="port",
        adapter_name=OBJECT_STORE_PORT_NAME,
        import_path="zuno.knowledge.ingestion.source_object_upload.DurableObjectStore",
        deployment_class="n/a",
        authoritative=False,
        description=(
            "Typed Object Store Port (stage/commit ticket contract) used by the "
            "SourceObjectUploadRuntime and PHASE22 canonical runtime."
        ),
    ),
    ObjectStoreAdapterDeclaration(
        role="production_adapter",
        adapter_name="DurableMinioObjectStore",
        import_path="zuno.platform.storage.durable.DurableMinioObjectStore",
        deployment_class="SERVER_PRODUCT",
        authoritative=True,
        description=(
            "Sole canonical production Object Store owner: MinIO durable adapter "
            "that binds physical object writes to the PostgreSQL object manifest "
            "(content hash, size, owner, visibility)."
        ),
    ),
    ObjectStoreAdapterDeclaration(
        role="physical_transport",
        adapter_name="MinioObjectStore",
        import_path="zuno.platform.storage.object_store.MinioObjectStore",
        deployment_class="SERVER_PRODUCT",
        authoritative=False,
        description=(
            "Physical S3-compatible transport owned by DurableMinioObjectStore; "
            "never a domain fact owner by itself."
        ),
    ),
    ObjectStoreAdapterDeclaration(
        role="local_adapter",
        adapter_name="LocalObjectStore",
        import_path="zuno.knowledge.storage.local_object_store.LocalObjectStore",
        deployment_class="DEVELOPER_CI",
        authoritative=False,
        description=(
            "Product V1 local filesystem adapter; DEVELOPER_CI profile only. "
            "Cannot satisfy production durability claims and is rejected by the "
            "server profile composition root."
        ),
    ),
)


def object_store_ownership() -> tuple[ObjectStoreAdapterDeclaration, ...]:
    """Return the formal ownership surface (immutable)."""
    return OBJECT_STORE_OWNERSHIP


def production_object_store_adapter() -> ObjectStoreAdapterDeclaration:
    """Return the declaration of the single production Object Store owner."""
    return next(
        declaration
        for declaration in OBJECT_STORE_OWNERSHIP
        if declaration.role == "production_adapter"
    )


def binding_declaration_payload() -> dict[str, Any]:
    """Stable machine-readable binding declaration used by evidence and guards."""
    return {
        "port": OBJECT_STORE_PORT_NAME,
        "production_adapter": production_object_store_adapter().adapter_name,
        "production_adapter_import": production_object_store_adapter().import_path,
        "local_adapter": "LocalObjectStore",
        "local_deployment_class": "DEVELOPER_CI",
        "server_deployment_class": "SERVER_PRODUCT",
        "fail_closed_when_unbound": True,
        "adapters": [
            {
                "role": declaration.role,
                "adapter_name": declaration.adapter_name,
                "import_path": declaration.import_path,
                "deployment_class": declaration.deployment_class,
                "authoritative": declaration.authoritative,
            }
            for declaration in OBJECT_STORE_OWNERSHIP
        ],
    }


# --- Errors ------------------------------------------------------------------


class ObjectStoreBindingError(RuntimeError):
    pass


class ObjectStoreBindingMissing(ObjectStoreBindingError):
    """Production binding is not configured; the caller must fail closed."""


class ObjectStoreCredentialMissing(ObjectStoreBindingMissing):
    """MinIO credentials or endpoint are missing in the server profile."""


class ObjectStoreLocalAdapterForbidden(ObjectStoreBindingError):
    """LocalObjectStore was requested under a profile that forbids it."""


# --- Fail-closed resolver -----------------------------------------------------


def minio_storage_settings(settings: Any) -> tuple[Any, bool]:
    """Return ``(minio_config, configured)`` for the settings storage profile.

    ``configured`` is True only when mode is ``minio`` and endpoint plus both
    credentials are present. Resolution never raises for an unconfigured
    profile; enforcement is the caller's choice (``None`` return / 503, or
    ``require_durable_minio_binding`` fail-fast).
    """
    storage = getattr(settings, "storage", None)
    if storage is None or getattr(storage, "mode", None) != "minio":
        return None, False
    minio = getattr(storage, "minio", None)
    if minio is None:
        return None, False
    endpoint = str(getattr(minio, "endpoint", "") or "").strip()
    access_key = str(getattr(minio, "access_key_id", "") or "").strip()
    secret_key = str(getattr(minio, "access_key_secret", "") or "").strip()
    if not endpoint or not access_key or not secret_key:
        return minio, False
    return minio, True


def resolve_durable_minio_binding(
    *,
    engine: Engine,
    settings: Any,
    owner: str,
    object_store_factory: Any = None,
    durable_object_store_factory: Any = None,
) -> Any:
    """Resolve the sole production Object Store binding from settings.

    Returns a configured ``DurableMinioObjectStore`` or ``None`` when the
    production binding is not configured (profile, endpoint or credential
    missing). ``None`` is the fail-closed signal: the caller must not fall
    back to a local filesystem adapter, and the API layer rejects uploads
    with 503 until a binding is configured.

    ``object_store_factory`` / ``durable_object_store_factory`` are injectable
    for tests and keep the historical composition-root signature compatible.
    """
    from zuno.platform.storage import DurableMinioObjectStore, MinioObjectStore

    object_store_factory = object_store_factory or MinioObjectStore
    durable_object_store_factory = durable_object_store_factory or DurableMinioObjectStore
    minio, configured = minio_storage_settings(settings)
    if not configured:
        return None
    object_store = object_store_factory(
        endpoint=str(getattr(minio, "endpoint", "") or "").strip(),
        access_key=str(getattr(minio, "access_key_id", "") or "").strip(),
        secret_key=str(getattr(minio, "access_key_secret", "") or "").strip(),
        secure=False,
    )
    return durable_object_store_factory(
        store=object_store,
        engine=engine,
        owner=owner,
    )


def require_durable_minio_binding(
    *,
    engine: Engine,
    settings: Any,
    owner: str,
    object_store_factory: Any = None,
    durable_object_store_factory: Any = None,
) -> Any:
    """Like :func:`resolve_durable_minio_binding` but fail closed when unbound."""
    binding = resolve_durable_minio_binding(
        engine=engine,
        settings=settings,
        owner=owner,
        object_store_factory=object_store_factory,
        durable_object_store_factory=durable_object_store_factory,
    )
    if binding is None:
        raise ObjectStoreBindingMissing(
            "production Object Store binding is not configured (storage mode, "
            "endpoint or MinIO credentials missing); the server profile must "
            "fail closed instead of degrading to a local adapter"
        )
    return binding


# --- Local adapter gating ------------------------------------------------------

SERVER_PRODUCT_PROFILE = "server_product"
DEVELOPER_CI_PROFILE = "developer_ci"

LOCAL_ADAPTER_ALLOWED_PROFILES = {DEVELOPER_CI_PROFILE}


def build_local_object_store(root: Any, *, profile: str = DEVELOPER_CI_PROFILE) -> Any:
    """Build the LocalObjectStore adapter under an explicit runtime profile.

    The local filesystem adapter is only legal for the ``developer_ci``
    (Local/Test) profile. Requesting it under ``server_product`` fails closed:
    it must never become a production fact owner.
    """
    from zuno.knowledge.storage.local_object_store import LocalObjectStore

    normalized_profile = str(profile or "").strip().lower()
    if normalized_profile not in LOCAL_ADAPTER_ALLOWED_PROFILES:
        raise ObjectStoreLocalAdapterForbidden(
            f"LocalObjectStore is only allowed for profile in "
            f"{sorted(LOCAL_ADAPTER_ALLOWED_PROFILES)}, got {profile!r}"
        )
    return LocalObjectStore(root)


def assert_binding_is_production_durable(object_store: Any) -> None:
    """Fail closed when an object store does not implement the durable port.

    The canonical runtime only accepts the production durable adapter surface
    (``stage`` / ``commit`` returning commit tickets plus manifest-backed
    readback). Passing a bare local adapter raises instead of silently
    substituting a filesystem for MinIO.
    """
    if object_store is None:
        raise ObjectStoreBindingMissing("object store binding is None")
    required = ("stage", "commit", "read_committed")
    missing = [name for name in required if not hasattr(object_store, name)]
    if missing:
        raise ObjectStoreBindingError(
            f"object store {type(object_store).__name__} does not implement the "
            f"durable port; missing {missing}"
        )
    if not hasattr(object_store, "store"):
        raise ObjectStoreBindingError(
            f"object store {type(object_store).__name__} has no physical store "
            "binding; only the DurableMinioObjectStore is a canonical owner"
        )


__all__ = [
    "DEVELOPER_CI_PROFILE",
    "LOCAL_ADAPTER_ALLOWED_PROFILES",
    "OBJECT_STORE_OWNERSHIP",
    "OBJECT_STORE_PORT_NAME",
    "ObjectStoreAdapterDeclaration",
    "ObjectStoreBindingError",
    "ObjectStoreBindingMissing",
    "ObjectStoreCredentialMissing",
    "ObjectStoreLocalAdapterForbidden",
    "SERVER_PRODUCT_PROFILE",
    "assert_binding_is_production_durable",
    "binding_declaration_payload",
    "build_local_object_store",
    "minio_storage_settings",
    "object_store_ownership",
    "production_object_store_adapter",
    "require_durable_minio_binding",
    "resolve_durable_minio_binding",
]
