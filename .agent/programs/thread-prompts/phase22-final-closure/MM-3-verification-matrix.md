# MM-3 Verification Matrix Worker Prompt

WORKER_TASK_ID: MM-3
PARENT_PR: 97
PROVIDER: MiniMax
BASE_BRANCH: codex/phase22-final-closure
WORKER_BRANCH: agent/minimax/phase22-verification-matrix-pr97

MiniMax is currently CONFIG_REQUIRED in controller preflight. Do not run this task until Codex confirms provider availability.

Scope when enabled:

- Run and record Repo, Backend, Web, Desktop, E2E, Fault, Security, Load and DR command matrix.
- Record real command, environment, exit code, stdout/stderr summary and classification.
- If dependency is missing, classify as BLOCKED_EXTERNAL / BLOCKED_NOT_MEASURED / INCOMPARABLE / ERROR. Do not mark PASS.

Allowed paths:

- `tools/scripts/**`
- `tests/**`
- `apps/web/**` read/build only unless a low-risk harness fix is required.
- `docs/evidence/goal05-phase22-verification-matrix-worker-mm3.md`

Final output must use the worker result schema from the controller plan.

