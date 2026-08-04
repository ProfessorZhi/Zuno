# PHASE22 Legacy Cutover — Final Audit Summary (V2)

audit_id: goal05-phase22-legacy-cutover-final-audit-v2
phase_id: PHASE22
date: 2026-08-04
branch: claude/minimax-phase22-legacy-cutover-audit-v2
agent_name: MiniMax-Legacy-Audit-V2
execution_client: Claude Code
provider: MiniMax
model: NOT_AVAILABLE
worker_task: PHASE22-LEGACY-CUTOVER-AUDIT-V2
expected_main_sha: 83c1bbd0689d1b2b3b4ffd7f3983de813da11ebb
audit_status: DUAL_PATH_BLOCKERS_FOUND
verifier_exit_code: 3
verifier_version: 2.0.0

## V2 vs PR #119

PR #119 emitted `LEGACY_CUTOVER_AUDIT_CLEAN` with exit code 0 even
though `src/backend/zuno/agent/runtime/phase08_cutover.py` retained the
production ``_fallback_to_legacy`` method, the ``legacy_runner`` field,
and the rollback/shadow/canary mode dispatch. V2 corrects this failure
mode by:

1. Adopting ``ast`` for every Python-surface check (no regex substrings).
2. Parsing work products with ``yaml.safe_load``, not a hand-rolled tiny
   YAML parser.
3. Reading ``git rev-parse HEAD`` for the exact Head SHA (never
   ``.git/HEAD`` text).
4. Parsing each feature flag's ``expires_at_phase`` against the current
   phase (PHASE22). Expired flags whose default is not ``RETIRED`` or
   whose rollback command remains active drive DUAL_PATH_BLOCKERS_FOUND.
5. Treating the Phase08 cutover controller retention as
   AUDIT_UNRESOLVED while the DeepSeek escalation is open.
6. Detecting Public-API Adapter direct DAO/Repository writes as
   PUBLIC_ADAPTER_OWNERSHIP_VIOLATION (exit 5).
7. Scanning non-Python surfaces (.ts, .tsx, .js, .mjs, .cjs, .sh, .ps1,
   .yml, .yaml, .toml, .github/workflows/*.yml).

## Verifier exit-code table

| Status                                       | Exit |
|----------------------------------------------|------|
| LEGACY_CUTOVER_AUDIT_CLEAN                   | 0    |
| LEGACY_RUNTIME_BLOCKERS_FOUND                | 2    |
| DUAL_PATH_BLOCKERS_FOUND                     | 3    |
| ALIAS_BYPASS_BLOCKERS_FOUND                  | 4    |
| PUBLIC_ADAPTER_OWNERSHIP_VIOLATION           | 5    |
| AUDIT_UNRESOLVED                             | 6    |
| TOOL_ERROR                                   | 7    |

## Current head facts

- ``head_sha`` resolved via ``git rev-parse HEAD``.
- ``current_phase = PHASE22``.
- Active repository tree contains the six canonical roots under
  ``src/backend/zuno`` (``api``, ``agent``, ``memory``, ``capability``,
  ``knowledge``, ``platform``) plus ``platform/vendor/`` for the
  canonical ``fastapi_jwt_auth`` shim.
- The compatibility shell (``src/backend/zuno/platform/compatibility``)
  and ``tests/legacy_guards/`` are absent.

## Findings

### Feature-flag registry

The feature flag registry contains four flags with
``expires_at_phase < PHASE22``. None of them has been retired:

| Flag                                | expires_at_phase | default      | Action            |
|-------------------------------------|------------------|--------------|-------------------|
| ``product_api_v1_adapter``          | PHASE10          | DECLARED     | DUAL_PATH_BLOCKER |
| ``workspace_projection_stream_v1``  | PHASE10          | DECLARED     | DUAL_PATH_BLOCKER |
| ``tool_runtime_readonly_gateway``   | PHASE15          | DECLARED     | DUAL_PATH_BLOCKER |
| ``postgres_domain_uow_shadow``      | PHASE04          | DECLARED     | DUAL_PATH_BLOCKER |

Each flag also exposes an active rollback command, which is the
secondary DUAL_PATH invariant.

### Phase08 cutover reachability

``src/backend/zuno/agent/runtime/phase08_cutover.py`` still defines
the following legacy surfaces (each is recorded as AUDIT_UNRESOLVED):

- ``legacy_runner`` attribute
- ``_run_legacy`` method
- ``_fallback_to_legacy`` method
- ``self.mode == "rollback"`` literal in ``handle``
- ``self.mode == "shadow"`` literal in ``handle``
- ``self.mode == "canary"`` literal in ``handle``

The DeepSeek escalation must retire or rename these surfaces before
PHASE22 closure can move past ``AUDIT_UNRESOLVED``. Until then, even
a "clean" feature-flag sweep would still yield AUDIT_UNRESOLVED for
the Phase08 axes.

### Other axes

- Production-source legacy imports: 0 (no ``zuno.core/services/schema/
  database/tools/resources/config/mcp_servers/utils``).
- Production-source ``legacy`` directory segments: 0.
- Production-source re-introduced retired shells: 0.
- Public-adapter direct DAO writes: 0.

## Expected upstream resolution path

1. The four expired feature flags move to ``default: "RETIRED"`` with
   their rollback_command rewritten to ``retired and fail-closed``;
   the verifier then falls into the Phase08 unresolved bucket.
2. DeepSeek retires or renames the Phase08 ``_fallback_to_legacy`` /
   ``legacy_runner`` / ``_run_legacy`` paths and the
   ``self.mode == "rollback|shadow|canary"`` dispatch.
3. Once both axes are clear, the verifier returns
   ``LEGACY_CUTOVER_AUDIT_CLEAN`` with exit code 0.

Until then, this V2 audit remains in
``DUAL_PATH_BLOCKERS_FOUND`` (exit 3), which is the correct
fail-closed outcome. The V1 PR #119 verdict is superseded.
