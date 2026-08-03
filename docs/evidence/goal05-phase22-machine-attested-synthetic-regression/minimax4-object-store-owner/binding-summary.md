# PHASE22-OBJECT-STORE-AST-GATE-FINAL — Binding Summary (MiniMax4)

## AST + Data-flow Proof

The gate proves the unique production binding by inspecting the actual
Python AST of the composition root file
`src/backend/zuno/api/services/workspace_task_runtime.py`:

```
function build_package_a_production_ingestion_runtime(
    *,
    engine: Any,
    settings: Any,
    worker_id: str = "workspace-file-upload",
    object_store_factory: Callable[..., Any] = MinioObjectStore,         # canonical
    durable_object_store_factory: Callable[..., Any] = DurableMinioObjectStore,  # canonical
    runtime_factory: Callable[..., PackageAProductionIngestionRuntime] = PackageAProductionIngestionRuntime,
):
    # fail-closed branches
    if storage is None or getattr(storage, "mode", None) != "minio": return None
    if minio is None: return None
    if not endpoint or not access_key or not secret_key: return None

    # single adapter binding
    object_store = object_store_factory(endpoint=..., access_key=..., secret_key=..., secure=False)

    # single wrapper binding that wraps the adapter
    durable_object_store = durable_object_store_factory(store=object_store, engine=engine, owner="workspace.file_upload")

    # runtime receives the wrapper
    return runtime_factory(engine=engine, object_store=durable_object_store, worker_id=worker_id)
```

The AST analysis confirms:

1. **One adapter assignment**: `object_store = object_store_factory(...)`
2. **One wrapper assignment**: `durable_object_store = durable_object_store_factory(...)`
3. **`wrapper.store == adapter`**: the wrapper wraps the adapter.
4. **`runtime.object_store == wrapper`**: the runtime depends on the wrapper.
5. **Two fail-closed branches**: storage.mode != "minio" and missing credentials.
6. **No auto-fallback to LocalObjectStore**.

## Call Sites

| Site | Line | Override |
|------|------|----------|
| `src/backend/zuno/main.py` | 73 | none (uses defaults) |
| `src/backend/zuno/platform/services/queue/runner.py` | 56 | none (uses defaults) |

## Verdict

| State | Value |
|-------|-------|
| Status | `UNIQUE_PRODUCTION_BINDING_STATICALLY_CONFIRMED` |
| Exit code | 0 |
| Not proven | live MinIO write/read; receipt authenticity; PostgreSQL manifest durability; runtime startup success; production readiness |