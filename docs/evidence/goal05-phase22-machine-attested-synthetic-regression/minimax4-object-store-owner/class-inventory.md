# PHASE22-OBJECT-STORE-AST-GATE-FINAL — Class Inventory (MiniMax4)

The AST gate classifies every object-store-related class by role.  The
inventory below mirrors what `tools/scripts/verify_phase22_object_store_owner_binding.py --mode repository --json`
returns, with the canonical source paths.

## Port / Protocol

| Class | Path | Line |
|-------|------|------|
| `DurableObjectStore` | `src/backend/zuno/knowledge/ingestion/source_object_upload.py` | 23 |

The Port is a structural `Protocol` declaring `stage(...)` and `commit(...)`.
The Protocol is implemented by `DurableMinioObjectStore` (Durable Wrapper).

## Local Development Adapter

| Class | Path | Line |
|-------|------|------|
| `LocalObjectStore` | `src/backend/zuno/knowledge/storage/local_object_store.py` | 14 |

`LocalObjectStore` is referenced only from
`WorkspaceTaskRuntimeService.configure_durable_ingestion`, the Local/Test
profile binding site.

## Test Double

| Class | Path | Line |
|-------|------|------|
| `FakeObjectStore` | `tests/fixtures/phase22_object_store_owner_binding/fake_object_store.py` | 13 |

`FakeObjectStore` is intentionally excluded from the production owner
count by the gate.

## Production MinIO Adapter

| Class | Path | Line |
|-------|------|------|
| `MinioObjectStore` | `src/backend/zuno/platform/storage/object_store.py` | 80 |

This is the only production object store adapter.  The composition root
binds it as the default for `object_store_factory`.

## Durable Wrapper

| Class | Path | Line |
|-------|------|------|
| `DurableMinioObjectStore` | `src/backend/zuno/platform/storage/durable.py` | 73 |

`DurableMinioObjectStore` wraps a `MinioObjectStore` and a SQLAlchemy
`Engine` and records PostgreSQL object manifests.  The composition root
binds it as the default for `durable_object_store_factory` and the
canonical runtime declares it as the `object_store` parameter type.

## Composition Root Binding

| Factory | Path | Line |
|---------|------|------|
| `build_package_a_production_ingestion_runtime` | `src/backend/zuno/api/services/workspace_task_runtime.py` | 116 |

AST signature defaults:

| Parameter | Default |
|-----------|---------|
| `object_store_factory` | `MinioObjectStore` |
| `durable_object_store_factory` | `DurableMinioObjectStore` |
| `runtime_factory` | `PackageAProductionIngestionRuntime` |

AST data-flow facts (verified by the gate):

| Fact | Value |
|------|-------|
| Adapter variable | `object_store` |
| Wrapper variable | `durable_object_store` |
| Wrapper wraps adapter | True (`durable_object_store_factory(store=object_store, ...)`) |
| Runtime uses wrapper | True (`runtime_factory(object_store=durable_object_store, ...)`) |
| Multi-adapter | False |
| Multi-wrapper | False |
| Fail-closed branches | 3 (`storage is None / mode != minio`, `minio is None`, missing creds) |
| Auto-fallback to LocalObjectStore | False |

Composition root call sites (resolved via AST):

| File | Line | Arguments |
|------|------|-----------|
| `src/backend/zuno/main.py` | 73 | `engine=engine, settings=app_settings` |
| `src/backend/zuno/platform/services/queue/runner.py` | 56 | `engine=engine, settings=app_settings, worker_id="phase11-package-a-parser-worker"` |

Both call sites use the default factories; neither overrides
`object_store_factory` or `durable_object_store_factory`.

## Runtime Owner

| Class | Path | Line |
|-------|------|------|
| `PackageAProductionIngestionRuntime` | `src/backend/zuno/knowledge/ingestion/production_runtime.py` | 116 |

`__init__` declares `object_store: DurableMinioObjectStore`, confirming
that the canonical Ingestion Application Service depends on the durable
wrapper, not on a raw adapter.  Receipts (`s3://<bucket>/<…>`) and
tenant/workspace prefixes (`{tenant_id}/{workspace_id}/`) are bound in
`_object_name()`.