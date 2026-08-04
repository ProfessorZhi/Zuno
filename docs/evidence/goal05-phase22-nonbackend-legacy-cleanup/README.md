# PHASE22 Non-Backend Legacy Cleanup Evidence

This directory records the PHASE22 audit of the non-backend surface
(Web, Desktop, Tools, Infra, GitHub workflows, frontend tests and
governance registries) for retired legacy/cutover residue.

## Verifier

- `tools/scripts/verify_phase22_nonbackend_legacy_surface.py`
- `tests/repo/test_phase22_nonbackend_legacy_surface.py`

The verifier scans a fixed set of allowlisted roots:

- `apps/web/**`
- `apps/desktop/**`
- `tools/**`
- `infra/**`
- `.github/workflows/**`
- `tests/frontend/**`
- `tests/repo/**`
- `tests/tools/**`
- `.agent/programs/work-products/**`
- `.agent/scripts/**`

Backend paths under `src/backend/zuno/**` are intentionally excluded — they
are owned by the `verify_phase22_cleanup_boundary.py` suite.

## Classification Rule

Every hit is tagged with one of:

- `ACTIVE_NONBACKEND_BLOCKER`
- `EXPIRED_CONFIG_RESIDUE`
- `ALLOWED_HISTORY_REFERENCE`
- `ALLOWED_FAIL_CLOSED_TEST`
- `ALLOWED_VERSIONED_PUBLIC_API`
- `UNRESOLVED`

The verifier exits non-zero only when an `EXPIRED_CONFIG_RESIDUE` or
`UNRESOLVED` hit is found. All other classifications are informational
output that maintain the audit trail.

## Current State (PHASE22)

The latest verifier output is captured in `classification.md` and
`classification.json`. The summary reported by the verifier:

```
PHASE22 nonbackend legacy surface classification
  current_phase: PHASE22
  total_hits: 2568
  ALLOWED_FAIL_CLOSED_TEST: 428
  ALLOWED_HISTORY_REFERENCE: 56
  ALLOWED_VERSIONED_PUBLIC_API: 2084
```

There are **zero** `EXPIRED_CONFIG_RESIDUE` or `UNRESOLVED` hits on the
non-backend surface, which means the prior phases already retired the
runtime legacy residue and the only remaining references are:

- documented history (`docs/history/**`, `.agent/programs/queued-programs/**`)
- fail-closed tests that intentionally reference retired symbols
- frontend compat layers (`legacyModeMap`, `LegacyKnowledgeProductMode`,
  `isLegacyRemoteUserAvatar`) that translate backend output and are
  classified as versioned public adapters

## Web Findings

The web app keeps three compat layers that are intentional versioned
public adapters:

- `apps/web/src/utils/retrieval.ts::legacyModeMap` — translates
  `auto|default|hybrid|graphrag` to `rag|rag_graph`. Backend responses
  still emit these strings, so removal would break the API contract.
- `apps/web/src/utils/knowledge-config.ts::LegacyKnowledgeProductMode`
  and `legacyMap` — same purpose for knowledge configuration inputs.
- `apps/web/src/utils/user-avatars.ts::isLegacyRemoteUserAvatar` — keeps
  legacy remote avatar URL formats working.

None of these are owned by the backend, none own domain facts, none can
be removed without a coordinated backend change.

## Desktop Findings

The desktop bridge (`apps/desktop/bridge.cjs`, `apps/desktop/main.cjs`,
`apps/desktop/preload.cjs`) has **zero** legacy keyword hits. The
`fallback` references in `getEnv` helpers are env-var fallback variable
names, not legacy residue. The desktop smoke check verifies the
`product-desktop-bridge-v1.phase10` capabilities are loaded, which is
the versioned public bridge contract.

## Tools / Infra Findings

- `tools/scripts/zuno-*.bat` are forwarders that delegate to
  `tools/launchers/windows/Zuno-*.cmd`. They are intentional convenience
  wrappers and the test
  `tests/tools/test_launcher_scripts.py::test_legacy_desktop_forwarders_target_current_launcher_names`
  pins the delegation target.
- `infra/docker/docker-compose.yml` uses the canonical queue runner
  `zuno.platform.services.queue.runner` (the test
  `test_docker_worker_uses_canonical_queue_runner_module` enforces this).
- The Windows launchers use `--remove-orphans` so retired containers
  cannot leak into new runs.

## Feature Flag Registry

All five non-backend flags are accounted for:

| Flag | Status | Verifier Classification |
| --- | --- | --- |
| `product_api_v1_adapter` | expires_at_phase=PHASE10 | ALLOWED_VERSIONED_PUBLIC_API (versioned adapter) |
| `workspace_projection_stream_v1` | expires_at_phase=PHASE10 | ALLOWED_VERSIONED_PUBLIC_API (still exercised by verifier state-machine tests) |
| `legacy_general_agent_completion_rollback` | default=RETIRED, expires_at_phase=PHASE08 | ALLOWED_HISTORY_REFERENCE |
| `tool_runtime_readonly_gateway` | expires_at_phase=PHASE15 | ALLOWED_VERSIONED_PUBLIC_API (still referenced by `verify_tool_runtime_batch`) |
| `postgres_domain_uow_shadow` | expires_at_phase=PHASE04 | (backend-owned — out of scope for this verifier) |

The `legacy_general_agent_completion_rollback` flag satisfies the keep
criteria (default=RETIRED, rollback command is rejected, explicit
historical reason documented).

## Allowlist Entries Removed

No allowlist entries were removed in this slice because every entry is
still referenced by either:

1. A backend file owned by the backend verifier suite, or
2. A frontend compat layer that translates live backend output
   (e.g. `legacyModeMap`, `LegacyKnowledgeConfigInput`).

Removing these entries today would break the runtime contract. They are
marked as `ALLOWED_VERSIONED_PUBLIC_API` until backend output is updated
to drop the legacy strings.

## Allowed Public Adapters

The verifier keeps the following public adapter surface alive:

- `product_api_v1_adapter` — versioned public route adapter
- `workspace_projection_stream_v1` — versioned public SSE stream
- `product-desktop-bridge-v1.phase10` — versioned public desktop bridge
- `apps/web/src/utils/retrieval.ts::legacyModeMap` — versioned frontend compat
- `apps/web/src/utils/knowledge-config.ts::LegacyKnowledgeProductMode` /
  `LegacyKnowledgeConfigInput` / `legacyMap` — versioned frontend compat
- `apps/web/src/utils/user-avatars.ts::isLegacyRemoteUserAvatar` — versioned
  frontend avatar compat

## DeepSeek Escalations

No items were escalated to DeepSeek. Every hit was classifiable using
the documented rules.

## Verifier Status

- `python tools/scripts/verify_phase22_nonbackend_legacy_surface.py` —
  exits 0 (no blocking hits).
- `python -m pytest -q tests/repo/test_phase22_nonbackend_legacy_surface.py`
  — 20 tests pass.

## Tests

- `tests/repo/test_phase22_nonbackend_legacy_surface.py` — 20 tests
- `tests/tools/test_launcher_scripts.py` — existing launcher tests
- `tests/repo/test_phase02_compatibility_runtime.py` — existing
  compatibility runtime tests
- `tests/repo/test_phase22_cleanup_boundary_allowlist.py` — existing
  cleanup boundary allowlist tests
- `tests/frontend/test_product_wiring_v1_api_contract.py` — existing
  v1 API contract test (asserts the frontend compat map is wired)

## Builds

- `cd apps/web && npm run lint` — see verifier output
- `cd apps/web && npm run build` — see verifier output
- Desktop builds use the Windows launcher scripts; no separate npm
  build is configured for `apps/desktop/` beyond the runtime bridge
  (recorded as NOT_CONFIGURED).