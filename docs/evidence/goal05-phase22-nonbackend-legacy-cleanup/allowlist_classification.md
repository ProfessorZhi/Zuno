# PHASE22 Allowlist Classification

Branch: `claude/minimax-phase22-nonbackend-legacy-cleanup`
Inputs:

- `.agent/programs/work-products/temporary-allowlist.yaml`
- `.agent/programs/work-products/legacy-bypass-inventory.yaml`
- `.agent/programs/work-products/phase22-removal-candidates.yaml`

Current phase: PHASE22.
Allowed edits: paths in the allowed scope (apps/web, apps/desktop, tools,
infra, .github/workflows, tests/frontend, tests/repo,
`.agent/programs/work-products/{feature-flag-registry,temporary-allowlist,
legacy-bypass-inventory,phase22-removal-candidates}.yaml`,
`docs/evidence/goal05-phase22-nonbackend-legacy-cleanup/**`).

## Headline counts (canonical tree, not `.claude/worktrees/`)

- `temporary-allowlist.yaml`: 51 entries
  - 3 entries under `apps/web/src/utils/{retrieval,knowledge-config,user-avatars}.ts`
  - 48 entries under `src/backend/zuno/**`
- `legacy-bypass-inventory.yaml`: 51 entries (mirrors the temporary allowlist; same content).
- `phase22-removal-candidates.yaml`: 192 path entries — frozen manifest documenting P22-T03 removal progress and the prior PR-#119 resolutions.

## Per-entry classification

### Web (3 entries — in scope)

| path                                              | symbol                                              | owner               | deadline | classification                                                                                                          |
| ------------------------------------------------- | --------------------------------------------------- | ------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------- |
| `apps/web/src/utils/retrieval.ts`                 | `legacyModeMap`                                     | 01 Product Surface  | PHASE10  | UNRESOLVED (Temporary Allowlist 永久例外; preserves old payload values; live readers in `pages/workspace/defaultPage/defaultPage.vue` etc. would force a contract change) |
| `apps/web/src/utils/knowledge-config.ts`          | `LegacyKnowledgeProductMode / LegacyKnowledgeConfigInput / legacyMap` | 01 Product Surface  | PHASE10  | UNRESOLVED (same; readers in `defaultPage.vue`, `tool.vue`, knowledge components)                                        |
| `apps/web/src/utils/user-avatars.ts`              | `isLegacyRemoteUserAvatar`                          | 01 Product Surface  | PHASE10  | UNRESOLVED (same; readers in `index.vue`, `profile.vue`, `workspace/defaultPage.vue`, `workspace.vue`)                  |

Note: per worker brief "Temporary Allowlist 永久例外 → 停止并记录", these
3 entries must NOT be deleted from this branch; they continue to be
defended by their test signatures (`tests/frontend/test_product_wiring_v1_api_contract.py`
and `tests/repo/test_history_overview_and_branding.py`). Resolution
requires a coordinated frontend+backend contract cutover (separate worker,
separate phase).

### Web (`apps/desktop/**`)

0 entries on `temporary-allowlist.yaml`. No action.

### Backend (48 entries — out of scope)

Every remaining entry falls under `src/backend/zuno/**` and is therefore out
of this worker's scope (worker brief: "禁止修改 src/backend/zuno/**"). They
are all classified as **ESCALATE_TO_DEEPSEEK** so the next wave-1 / wave-B
backend worker branch handles them under P22-T03 removal task.

### Removed-from-this-branch outcomes

None. Worker policy: never delete by keyword; classification only.

## What this branch changed in the allowlist files

None. Two reasons:

1. Three web entries are protected by their owners and active readers; deleting them now would break the front-end compat layer without a confirmed replacement contract.
2. Forty-eight backend entries are explicit out-of-scope.

The new verifier + test (in this PR) pin the 3 web entries with their
existing symbols, owner, deadline, and removal_task so a future worker
cannot silently remove them or rename the symbols without picking up the
classification matrix.
