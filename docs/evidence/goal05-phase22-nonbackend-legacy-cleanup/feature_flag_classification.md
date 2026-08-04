# PHASE22 Feature Flag Classification

Branch: `claude/minimax-phase22-nonbackend-legacy-cleanup`
Input: `.agent/programs/work-products/feature-flag-registry.yaml`
Current phase: PHASE22
Allowed classification outcomes (this branch cannot retire a flag whose runtime reader exists outside its scope):

| Flag                                            | Owner               | Scope                  | default     | expires_at_phase | Outcome                                               |
| ----------------------------------------------- | ------------------- | ---------------------- | ----------- | ---------------- | ----------------------------------------------------- |
| `product_api_v1_adapter`                        | 01 Product Surface  | server route           | DECLARED    | PHASE10          | ALLOWED_VERSIONED_PUBLIC_API (v1 adapter; documented exemption) |
| `workspace_projection_stream_v1`                | 01 Product Surface  | SSE stream             | DECLARED    | PHASE10          | ALLOWED_VERSIONED_PUBLIC_API (v1 SSE projection stream; same exemption) |
| `legacy_general_agent_completion_rollback`      | 06 Agent Core       | completion route rollback | RETIRED   | PHASE08          | ALLOWED_HISTORY_REFERENCE (registry record retained; rollback_command rejects `ZUNO_COMPLETION_CUTOVER_MODE=rollback` after PHASE22 cutover) |
| `tool_runtime_readonly_gateway`                 | 08 Tool Runtime     | tool invocation        | DECLARED    | PHASE15          | ACTIVE_NONBACKEND_BLOCKER (tool runtime is outside this branch's scope; running the boundary verifier plus `tools/scripts/phase02_compatibility_runtime.py` still references this flag as SHADOW) |
| `postgres_domain_uow_shadow`                    | 11 Infrastructure   | persistence            | DECLARED    | PHASE04          | ACTIVE_NONBACKEND_BLOCKER (migration / persistence is outside this branch's scope; transition table in `phase02_compatibility_runtime.py` still references this flag as SHADOW) |

## Rationale

- `product_api_v1_adapter` and `workspace_projection_stream_v1`: although
  they are expired-by-phase (PHASE10 < PHASE22), both are explicit versioned
  public-API surface and are explicitly allowed by the worker brief
  ("对于 `product_api_v1_adapter`: 不能因为名字含 v1 就删除").
  All three delete conditions stipulated by the brief hold for both flags:
  - no domain-fact ownership (registry records `domain_fact_owner: unchanged`)
  - no direct DB write
  - no old-runtime fallback.
- `legacy_general_agent_completion_rollback`: already `default: RETIRED`,
  has an explicit `rollback_command` that is now an active fail-closed
  rejection. The registry record is preserved as the canonical
  PHASE22 history reference (verified by
  `tools/scripts/verify_phase22_cleanup_boundary.py`,
  `tests/repo/test_phase22_cleanup_boundary_allowlist.py`).
- `tool_runtime_readonly_gateway`: PHASE15 deadline has passed; runtime
  readers (if any) live under `src/backend/zuno/platform/services/tool_connectivity_service.py`
  and `tools/evals/...` which are outside this worker's allowed scope. We
  register the issue and escalate; do NOT touch the registry from this
  branch.
- `postgres_domain_uow_shadow`: PHASE04 < PHASE22. Persistence is hard out
  of scope. Any read would land on `src/backend/zuno/platform/database/...`,
  which is forbidden. We register the issue and escalate; do NOT touch the
  registry from this branch.

## What this branch changed

None. The registry was preserved verbatim to keep the historical record and
because every expired entry has either a versioned-public-API exemption
(`product_api_v1_adapter` / `workspace_projection_stream_v1`) or a runtime
reader in a forbidden zone.

The new verifier `tools/scripts/verify_phase22_nonbackend_legacy_surface.py`
pins these invariants so that future workers cannot accidentally retire one
of the two exempted v1 adapters from the registry, nor mark the history
reference `legacy_general_agent_completion_rollback` as anything other than
RETIRED.
