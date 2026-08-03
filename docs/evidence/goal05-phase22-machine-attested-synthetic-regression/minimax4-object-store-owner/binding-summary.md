# PHASE22-OBJECT-STORE-OWNER-GATE — Binding Summary (MiniMax4)

## Why the old preflight was wrong

The old DeepSeek preflight counted classes whose name ends with
`ObjectStore`:

```
DurableObjectStore       (Protocol / Port)
LocalObjectStore         (local development adapter)
DurableMinioObjectStore  (durable wrapper around the production adapter)
MinioObjectStore         (production MinIO adapter)
```

Four classes do **not** imply four runtime owners.  A port, a local
adapter, a durable wrapper and a single production adapter can coexist
without producing multiple runtime owners.  The correct question is: which
object store does the production composition root actually bind for the
canonical ingestion runtime?

## What the Fail-closed Gate Proves

The verifier inspects:

1. **Canonical Ingestion Application Service dependency** — the runtime
   constructor signature.  In this repository
   `PackageAProductionIngestionRuntime.__init__` declares
   `object_store: DurableMinioObjectStore`, so the runtime depends on the
   durable wrapper, not on a raw adapter.

2. **Production Composition Root binding** — the factory
   `build_package_a_production_ingestion_runtime` in
   `src/backend/zuno/api/services/workspace_task_runtime.py` has signature
   defaults that bind exactly one production adapter
   (`MinioObjectStore`) and exactly one durable wrapper
   (`DurableMinioObjectStore`).  The factory body instantiates each of them
   once and wraps the adapter output inside the wrapper.

3. **Multiple simultaneous production bindings** — none.  There is a
   single call site in `main.py` (`WorkspaceTaskRuntimeService.configure_package_a_production_ingestion`)
   and a single call site in `platform/services/queue/runner.py`
   (`run_package_a_ingestion_worker_forever`).  Both use the default
   factories, so the production binding is unique.

4. **Local Adapter scope** — `LocalObjectStore` is referenced from
   `WorkspaceTaskRuntimeService.configure_durable_ingestion`, the
   Local/Test profile binding site.  The production composition root body
   never mentions it.

5. **Durable Wrapper chains** — `durable_object_store_factory(store=object_store, engine=engine, owner="workspace.file_upload")`
   wraps the output of the production `object_store_factory` call.  There
   is exactly one durable wrapper instantiation in the production factory
   body.

6. **Receipt and tenant/workspace namespace** — the canonical runtime
   emits `s3://<bucket>/<tenant>/<workspace>/source/<source_id>/<filename>`
   receipts (see `_object_name()` in `production_runtime.py`).  Receipts
   are tenant/workspace scoped.

7. **Fail-Closed branches** — `build_package_a_production_ingestion_runtime`
   returns `None` when `settings.storage.mode != "minio"` or when the
   MinIO credentials are missing.  The runtime is not bound until the
   production storage mode is configured.  `main.py` and the queue runner
   both check the returned runtime and refuse to start the worker when it
   is `None`.

## Verdict

| State | Value |
|-------|-------|
| Status | `UNIQUE_PRODUCTION_BINDING_CONFIRMED` |
| Exit code | 0 |
| Production adapter | `MinioObjectStore` |
| Durable wrapper | `DurableMinioObjectStore` |
| Runtime | `PackageAProductionIngestionRuntime` |
| Composition root | `build_package_a_production_ingestion_runtime` |