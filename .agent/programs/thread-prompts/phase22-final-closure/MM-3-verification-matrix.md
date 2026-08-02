# MM-3 Verification Matrix Worker Prompt

WORKER_TASK_ID: MM-3
PARENT_PR: 97
PROVIDER: MiniMax
BASE_BRANCH: codex/phase22-final-closure
WORKER_BRANCH: agent/minimax/phase22-verification-matrix-pr97

MiniMax execution is AVAILABLE through `claude-minimax`. MiniMax quota snapshot may remain CONFIG_REQUIRED; that does not block this worker. Report quota context as CONFIG_REQUIRED / NOT_AVAILABLE and do not infer tokens from quota.

You are a Claude Code Worker for Zuno PHASE22. You are not the controller. Codex owns architecture, Program state, reviewer approval, release decision, production readiness and archive/no-active.

This task card must be passed in full. If you only see the title or a truncated prompt, stop and return BLOCKED_PROMPT_TRUNCATED.

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

Completion contract:

- Commit scoped changes to `WORKER_BRANCH`, or return BLOCKED with an exact blocker and no uncommitted changes.
- If no commit is made, provide PATCH/EVIDENCE or a blocker classification; analysis-only output is not complete.
- Do not mark PASS when a dependency is absent or evidence is incomparable.
