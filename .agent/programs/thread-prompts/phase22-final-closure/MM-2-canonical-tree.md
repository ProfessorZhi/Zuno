# MM-2 Canonical Tree Worker Prompt

WORKER_TASK_ID: MM-2
PARENT_PR: 97
PROVIDER: MiniMax
BASE_BRANCH: codex/phase22-final-closure
WORKER_BRANCH: agent/minimax/phase22-canonical-tree-pr97

MiniMax is currently CONFIG_REQUIRED in controller preflight. Do not run this task until Codex confirms provider availability.

Scope when enabled:

- Scan for duplicate packages, no-owner files, temporary compatibility, old naming, bypasses and permanent dual paths.
- Perform only low-risk cleanup where a canonical replacement already exists.
- Do not alter architecture ownership, shared contracts, program state, production readiness or release facts.

Allowed paths:

- `tools/scripts/verify_phase22_cleanup_boundary.py`
- `tests/repo/**`
- `tests/api/**`
- `tests/frontend/**`
- Low-risk production import cleanup under `src/backend/zuno/**`
- `docs/evidence/goal05-phase22-canonical-tree-worker-mm2.md`

Final output must use the worker result schema from the controller plan.

