# PHASE22 Final Legacy Cutover Audit — V3

Work package: `PHASE22-FINAL-LEGACY-AUDIT-V3`
Worker: `minimax2` (Execution-Client: Claude Code, Provider: MiniMax)
Integration Basis: `claude/minimax-phase22-approved-slices-integration` @ `d730d31de93e2f3cd77f0a9ebddf37798ba2c6d7`
Branch: `claude/minimax-phase22-final-legacy-audit-v3`
Verifier source: `tools/scripts/verify_phase22_final_legacy_cutover.py`

## Verdict (current Integration Branch)

```
FINAL_AUDIT_REVALIDATION_REQUIRED
```

PHASE22-PR133-FINAL-ENGINEERING-CLOSURE interim state after
worker `minimax1` (Execution-Client: Claude Code, Provider: MiniMax).
The prior `LEGACY_CUTOVER_AUDIT_CLEAN` verdict at HEAD `1ae54b58` is
**withdrawn** because the CLEAN was achieved partly through name
changes (variable `tool` → `binding`, identifier
`_guess_direct_mcp_call` → `_classify_mcp_route_tool`) that bypassed
the AST substring detector. Variable / function / file location
changes MUST NOT change the safety classification.

Until `minimax2` delivers its semantic-hardening verifier slice, the
audit is held at `FINAL_AUDIT_REVALIDATION_REQUIRED` and the live
tree is NOT eligible to claim CLEAN, regardless of the current
`findings` count. After the `minimax2` slice merges and the
semantically-strengthened verifier runs against the combined tree,
the final verdict will be re-evaluated.

The audit is a **structural boundary**, not a runtime correctness
guarantee. It does NOT declare `PHASE22_COMPLETED`, `PRODUCTION_READY`,
or `FULL_BACKEND_CUTOVER_CONFIRMED`.

## Status priority

```
TOOL_ERROR
> AUDIT_UNRESOLVED
> PUBLIC_ADAPTER_OWNERSHIP_VIOLATION
> TOOL_BYPASS_BLOCKERS_FOUND
> LEGACY_RUNTIME_BLOCKERS_FOUND
> DUAL_PATH_BLOCKERS_FOUND
> LEGACY_CUTOVER_AUDIT_CLEAN
```

The current run reports `TOOL_BYPASS_BLOCKERS_FOUND` because the
workspace agents still call `await handler(request)` directly,
bypassing `ToolInvocationGateway`. Tool bypass dominates legacy
runtime in priority order.

## Findings summary

| Category | Count |
|---|---|
| `legacy_runtime_class_def` | 0 |
| `legacy_workspace_runtime` | 10 |
| `tool_bypass_handler` | 4 |
| `tool_bypass_mcp_direct` | 1 |
| `dual_path_expired_flag_reader` | 0 |
| `ownership_dao_write` | 0 |
| `ownership_plan_owned` | 0 |
| `unresolved_dynamic_constructor` | 0 |
| `unresolved_alias_factory` | 0 |
| **Total** | **15** |

## Detection categories

### 1. Legacy Runtime

- `legacy_runtime_class_def` — any `ClassDef` for a GeneralAgent family
  class (`GeneralAgent`, `ReactAgent`, `PlanExecuteAgent`, `CodeActAgent`,
  `Text2SQLAgent`) in the production tree.
- `legacy_phase08_reachability` — `phase08_cutover` / `Phase08LegacyRuntime`
  / `legacy_phase08_agent` / `build_phase08_legacy` / `rollback_to_phase08`
  symbol references in production code.
- `legacy_workspace_runtime` — `WorkSpaceSimpleAgent` / `WeChatAgent`
  carrying `create_agent`, `self.model.ainvoke`, `self.tool.ainvoke`, or
  `await handler(request)`.

### 2. Dual Path

- `dual_path_signal` — `rollback`, `shadow`, `canary`, `dual_read`,
  `dual_write`, `expired_flag`, `fallback_to_legacy`,
  `legacy_runtime_selector`, `runtime_selector` identifiers.
- `dual_path_expired_flag_reader` — a `yaml.safe_load` followed by an
  `expires_at` / `valid_until` comparison. Plain record timestamps that
  happen to be named `expires_at` are NOT flagged.

### 3. Tool Bypass

- `tool_bypass_direct` — `self.tool.ainvoke`, `self.tool.invoke` on
  attribute owned by the class. Function-adapter patterns that take
  `tool` as a parameter are NOT flagged.
- `tool_bypass_handler` — `await handler(request)` direct invocation.
- `tool_bypass_mcp_direct` — `mcp_direct` / `direct_mcp` identifiers.
- `tool_bypass_image_gen` — `image_gen_bypass` identifier.
- `tool_bypass_read_only` — `skill_direct_execute` identifier.

### 4. Ownership

- `ownership_dao_write` — `session.add`, `session.commit`, `session.delete`
  inside a public adapter module (`src/backend/zuno/agent/harness.py`,
  `src/backend/zuno/agent/runtime/adapters.py`,
  `src/backend/zuno/agent/runtime/service.py`,
  `src/backend/zuno/agent/runtime/factory.py`).
- `ownership_plan_owned` — `PlannerOutput()`, `CapabilityPlan()`,
  `RunOutcome()`, `FinalGate()` instantiation or self-assignment
  inside a public adapter.

### 5. Unresolved (Dynamic / Alias / Factory)

- `unresolved_dynamic_constructor` — `globals()`, `getattr()`, `eval()`,
  `__import__()`, `import_module()`, `locals()`, `vars()` calls whose
  text contains an `Agent` / `Runtime` / `Controller` / `Service` /
  `Harness` / `Factory` token.
- `unresolved_alias_factory` — module-level `Runtime = X` /
  `AgentRuntime = X` / `AdapterRuntime = X` assignment aliases.

## Exclusions

The verifier excludes these paths from the scanner:

- `tests/` — test files.
- `docs/` — documentation, history-only references.
- `.agent/` — agent-side scripts.
- `tools/evals/` — evaluation scaffolding.
- `tools/scripts/_archive/` — archived tooling.
- `node_modules/` — JavaScript dependencies.

`__init__.py` facade re-exports and `product_baseline.py` are not
considered as production reachability evidence.

## Not proven boundary

The verifier does NOT prove:

- That runtime selectors are reduced to a single value at runtime.
  The current code base uses class-name-only dispatch which is
  statically ambiguous.
- That `AgentControlRuntime` is permanently
  `INTERNAL_TEST_HARNESS`. A future production caller would flip it
  to `LEGACY_RUNTIME_BLOCKERS_FOUND`.
- That the audit CLEAN on the live integration tree implies
  `PHASE22_COMPLETED` / `PRODUCTION_READY` / `FULL_BACKEND_CUTOVER_CONFIRMED`.
  The audit is fail-closed and live-tree CLEAN is a structural
  property, not a runtime correctness guarantee.

## Verifier usage

```sh
python tools/scripts/verify_phase22_final_legacy_cutover.py \
  --integration-base-sha 10501e0382d863014513f993822abd6bcf758cf6

python tools/scripts/verify_phase22_final_legacy_cutover.py \
  --integration-base-sha 10501e0382d863014513f993822abd6bcf758cf6 \
  --json

python tools/scripts/verify_phase22_final_legacy_cutover.py \
  --integration-base-sha 10501e0382d863014513f993822abd6bcf758cf6 \
  --report
```

The exit code is non-zero for every status except
`LEGACY_CUTOVER_AUDIT_CLEAN`.

## Test matrix

`tests/repo/test_phase22_final_legacy_cutover.py` — 16 tests:

1. `test_clean_fixture_produces_zero_findings` — clean fixture → CLEAN.
2. `test_phase08_fallback_triggers_legacy_runtime_blocker` — phase08
   legacy symbol reachable.
3. `test_expired_flag_reader_triggers_dual_path_blocker` — yaml +
   expires_at → dual_path.
4. `test_direct_tool_call_triggers_tool_bypass_blocker` — direct
   tool.ainvoke → tool_bypass.
5. `test_public_adapter_dao_write_triggers_ownership_violation` —
   public adapter DAO write → ownership.
6. `test_dynamic_import_triggers_audit_unresolved` — getattr /
   __import__ → UNRESOLVED.
7. `test_alias_factory_triggers_audit_unresolved` — assignment alias
   → UNRESOLVED.
8. `test_allowlisted_bypass_still_blocks` — allowlist comment does
   not silence the bypass.
9. `test_history_only_docs_reference_does_not_block` — docs/ is
   excluded.
10. `test_versioned_public_api_not_misclassified` — versioned public
    API names do not misfire.
11. `test_unknown_path_does_not_silence_findings` — SCANNED_ROOTS
    contract is enforced.
12. `test_exact_integration_tree_sha_recorded` — integration SHA
    recorded in the report.
13. `test_unresolved_count_blocks_clean` — unresolved_count > 0 →
    not CLEAN.
14. `test_current_integration_branch_returns_nonzero` — current
    integration branch returns non-zero, non-CLEAN status.
15. `test_json_shape_is_stable` — JSON output schema is stable.
16. `test_status_priority_is_observed` — TOOL_BYPASS > LEGACY_RUNTIME
    priority is observed.

## What this slice does NOT declare

- `PHASE22_COMPLETED` — not declared.
- `PRODUCTION_READY` — not declared.
- `FULL_BACKEND_CUTOVER_CONFIRMED` — not declared.
- The audit is a structural boundary, not a runtime correctness
  guarantee.

## Out of scope

- Verifier cannot detect runtime selectors that resolve via
  attribute-chain / class-name-only dispatch where the target is a
  runtime symbol but the call chain is too long to follow statically.
- Verifier does not execute Yaml flag readers and cannot judge
  whether a particular flag has expired. It only flags the
  structural pattern.
- Verifier does not follow import_module / __import__ to its target.
  Any dynamic loader is reported as UNRESOLVED.
