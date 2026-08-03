# PHASE22-OBJECT-STORE-AST-GATE-FINAL — Evidence (MiniMax4)

Worker: MiniMax4 (claude/minimax4-phase22-object-store-owner-gate)
Verifier: `tools/scripts/verify_phase22_object_store_owner_binding.py`
Run on: 2026-08-03 (Follow-up Session)
Base SHA: `87f6eeed994d1db28f25ad916e052b3a3cd00992`

## Summary

The PHASE22-OBJECT-STORE-OWNER-GATE has been rewritten as a fail-closed
**AST + Data-flow Static Binding Gate**.  The previous implementation relied
on regex / class-name heuristics; this version uses Python's `ast` module
to:

1. Scan every Python file under `src/` for calls to
   `build_package_a_production_ingestion_runtime(...)`.
2. Resolve import aliases and detect dynamic dispatch.
3. Inspect the composition root factory body to prove a single adapter is
   created, a single wrapper is created, the wrapper wraps the adapter
   (`store=adapter`), and the runtime receives the wrapper
   (`object_store=wrapper`).
4. Verify the composition root returns `None` when production storage is
   unconfigured (storage.mode != "minio" or missing credentials).
5. Verify every call site explicitly handles the `None` return.

Status names are unified:

* `UNIQUE_PRODUCTION_BINDING_STATICALLY_CONFIRMED`
* `MULTIPLE_PRODUCTION_BINDINGS`
* `NO_PRODUCTION_BINDING`
* `BINDING_UNRESOLVED`
* `TOOL_ERROR`

The legacy name `UNIQUE_PRODUCTION_BINDING_CONFIRMED` is **not** used by
this gate because the gate does not perform live MinIO write/read.

## Results

| Run | Exit | Status |
|-----|------|--------|
| `--mode contract` | 0 | `UNIQUE_PRODUCTION_BINDING_STATICALLY_CONFIRMED` (12/12 fixtures) |
| `--mode repository` | 0 | `UNIQUE_PRODUCTION_BINDING_STATICALLY_CONFIRMED` |

## Not Proven Boundary

This gate proves only the static binding topology.  It explicitly does not
prove:

- live MinIO write/read
- receipt authenticity
- PostgreSQL manifest durability
- runtime startup success
- production readiness

A subsequent worker (DeepSeek) is responsible for executing the binding
end-to-end against a live MinIO instance.

## Discovered Call Sites

| File | Line | Qualified Target | Resolution |
|------|------|------------------|------------|
| `src/backend/zuno/main.py` | 73 | `zuno.api.services.workspace_task_runtime.build_package_a_production_ingestion_runtime` | resolved |
| `src/backend/zuno/platform/services/queue/runner.py` | 56 | `zuno.api.services.workspace_task_runtime.build_package_a_production_ingestion_runtime` | resolved |

Both call sites use the default factories; neither overrides
`object_store_factory` or `durable_object_store_factory`.

## Reproduction

```bash
python tools/scripts/verify_phase22_object_store_owner_binding.py --mode contract
python tools/scripts/verify_phase22_object_store_owner_binding.py --mode repository
python tools/scripts/verify_phase22_object_store_owner_binding.py --mode repository --json
```

## Files in this evidence directory

* `evidence.md` — this document.
* `verification.json` — repository-mode machine attestation.
* `contract-self-test.json` — contract-mode machine attestation.
* `binding-summary.md` — human-readable summary of the binding verdict.
* `class-inventory.md` — role-by-role inventory of the four classes.