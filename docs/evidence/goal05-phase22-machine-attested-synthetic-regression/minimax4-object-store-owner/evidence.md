# PHASE22-OBJECT-STORE-OWNER-GATE — Evidence (MiniMax4)

Worker: MiniMax4 (claude/minimax4-phase22-object-store-owner-gate)
Verifier: `tools/scripts/verify_phase22_object_store_owner_binding.py`
Run on: 2026-08-03
Base SHA: `87f6eeed994d1db28f25ad916e052b3a3cd00992`

## Summary

The Fail-closed Object Store Owner / Composition Root Binding Gate rejects
the old DeepSeek preflight heuristic ("class-name suffix count").  It
distinguishes Port, Local Adapter, Test Double, Production Adapter, Durable
Wrapper, Composition Root and Runtime Owner, then proves the unique
production binding by inspecting the production composition root signature
defaults, body references, call sites, fail-closed branches and runtime
dependency annotations.

| Run | Exit Code | Status |
|-----|-----------|--------|
| `--mode contract` | 0 | `UNIQUE_PRODUCTION_BINDING_CONFIRMED` (8/8 fixtures pass) |
| `--mode repository` | 0 | `UNIQUE_PRODUCTION_BINDING_CONFIRMED` |

## Files in this evidence directory

* `evidence.md` — this document.
* `verification.json` — repository-mode machine attestation.
* `contract-self-test.json` — contract-mode machine attestation.
* `binding-summary.md` — human-readable summary of the binding verdict.
* `class-inventory.md` — role-by-role inventory of the four classes.

## Reproduction

```bash
python tools/scripts/verify_phase22_object_store_owner_binding.py --mode contract
python tools/scripts/verify_phase22_object_store_owner_binding.py --mode repository
python tools/scripts/verify_phase22_object_store_owner_binding.py --mode repository --json
```

The gate is Fail-closed: if the production binding cannot be proven
uniquely, the exit code is non-zero and the status is one of:

| Exit Code | Status |
|-----------|--------|
| 0 | `UNIQUE_PRODUCTION_BINDING_CONFIRMED` |
| 2 | `MULTIPLE_PRODUCTION_BINDINGS` |
| 3 | `NO_PRODUCTION_BINDING` |
| 4 | `BINDING_UNRESOLVED` |
| 5 | `TOOL_ERROR` |