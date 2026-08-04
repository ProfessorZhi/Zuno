# PHASE22 DeepSeek Escalations

Branch: `claude/minimax-phase22-nonbackend-legacy-cleanup`
Per worker brief: items that meet any of the following conditions are escalated
to DeepSeek instead of being edited from this branch:

- 修改会影响 Runtime 状态
- 修改会影响恢复
- 修改会影响 Side Effect
- 修改会影响 Security/Budget
- 修改会影响外部 API Contract

## Escalation list

### ESC-DS-001 — `tool_runtime_readonly_gateway` feature flag

**Reason:** Tool-invocation gateway flag, deadline PHASE15 < PHASE22. Runtime readers (if any) live in backend tool runtime (`src/backend/zuno/platform/services/tool_connectivity_service.py`,
`src/backend/zuno/capability/tools/*/adapter.py`, evaluation harness under
`tools/evals/zuno/`).
**Why we cannot edit:** Worker brief forbids modification of `src/backend/zuno/**`,
agent core, and security. Editing the flag registry from this branch would
either false-attest a removal we did not perform, or break a real reader.
**Recommended next step:** DeepSeek worker branch verifies zero tool-runtime
readers via repo-grep + `phase02_compatibility_runtime.py` SHADOW coverage,
then flips `default: "DECLARED"` to `default: "RETIRED"` and updates
`rollback_command` accordingly.

### ESC-DS-002 — `postgres_domain_uow_shadow` feature flag

**Reason:** Persistence-flag, deadline PHASE04 < PHASE22. Readers (if any)
live under `src/backend/zuno/platform/database/` and
`src/backend/zuno/agent/runtime/sqlite_store.py` and the alembic migration
tree. Editing from this branch is forbidden by worker brief.
**Recommended next step:** DeepSeek worker branch confirms no shadow-adapter
reader, then retires the flag in the registry.

### ESC-DS-003 — 48 backend entries on `temporary-allowlist.yaml` and `legacy-bypass-inventory.yaml`

**Reason:** All paths under `src/backend/zuno/**`. Out of scope.
**Recommended next step:** Backend worker branch retires the entries in
pairs (allowlist + bypass inventory) with the canonical canonical
`tests/repo/test_*_*.py` signatures preserved; verifies
`tests/repo/test_phase22_cleanup_boundary_allowlist.py::test_legacy_allowlist_does_not_keep_legacy_directory`
and `test_repo_structure_verifier_pins_backend_legacy_import_aliases`
still pass; updates `phase22-removal-candidates.yaml::resolved_this_slice`.

### ESC-DS-004 — `apps/web/src/utils/{retrieval,knowledge-config,user-avatars}.ts`

**Reason:** Three web allowlist entries with deadline PHASE10 < PHASE22.
Per worker brief "Temporary Allowlist 永久例外 → 停止并记录", they cannot
be deleted by this branch. Front-end consumers in
`pages/workspace/defaultPage/defaultPage.vue` and related components still
read them.
**Recommended next step:** Coordinated frontend+backend owner branch in a
later phase: confirm backend no longer emits legacy payload values; remove
compat shims; bump client rebuild. Until then this branch keeps the
symbols and pinning tests.

## Items NOT escalated (this branch handled locally)

- `legacy_general_agent_completion_rollback`: pinned via the existing
  `tools/scripts/verify_phase22_cleanup_boundary.py` and the new
  `tools/scripts/verify_phase22_nonbackend_legacy_surface.py` in this PR.
  No registry change required.
- The 4 `tools/scripts/zuno-*.bat` legacy forwarders: pinned by
  `tests/tools/test_launcher_scripts.py::test_legacy_desktop_forwarders_target_current_launcher_names`.
  No change required.
- The full set of legacy web router redirects in
  `apps/web/src/router/index.ts`: pinned by the new verifier.
  No change required.
- The set of standalone page folders under `apps/web/src/pages/{agent,...}`:
  pinned by the new verifier (they are still imported by
  `WorkspaceSettingsShell.vue` and `defaultPage.vue`). No change required.

## Status register

| ID         | Item                                                 | Status   |
| ---------- | ---------------------------------------------------- | -------- |
| ESC-DS-001 | `tool_runtime_readonly_gateway` flag                 | OPEN     |
| ESC-DS-002 | `postgres_domain_uow_shadow` flag                    | OPEN     |
| ESC-DS-003 | 48 backend allowlist/bypass-inventory entries        | OPEN     |
| ESC-DS-004 | 3 web allowlist entries (retrieval/knowledge/user)   | OPEN     |
