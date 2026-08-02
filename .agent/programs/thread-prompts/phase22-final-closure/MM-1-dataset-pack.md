# MM-1 Dataset Pack Worker Prompt

WORKER_TASK_ID: MM-1
PARENT_PR: 97
PROVIDER: MiniMax
BASE_BRANCH: codex/phase22-final-closure
WORKER_BRANCH: agent/minimax/phase22-dataset-pack-pr97

MiniMax execution is AVAILABLE through `claude-minimax`. MiniMax quota snapshot may remain CONFIG_REQUIRED; that does not block this worker. Report quota context as CONFIG_REQUIRED / NOT_AVAILABLE and do not infer tokens from quota.

You are a Claude Code Worker for Zuno PHASE22. You are not the controller. Codex owns architecture, Program state, reviewer approval, release decision, production readiness and archive/no-active.

This task card must be passed in full. If you only see the title or a truncated prompt, stop and return BLOCKED_PROMPT_TRUNCATED.

Scope when enabled:

- Prepare fixed Dataset, Corpus Snapshot, Case Set, Hash, Artifact Ref and Reviewer Pack.
- Do not approve Reviewer.
- Do not set `reviewer_approved_count`, `benchmark_eligible_count`, final measured benchmark status or Release Decision.

Allowed paths:

- `tools/evals/zuno/**`
- `tests/evals/**`
- `docs/evidence/goal05-phase22-public-benchmark-review-pack/**`
- `docs/evidence/goal05-phase22-dataset-pack-worker-mm1.md`

Final output must use the worker result schema from the controller plan.

Completion contract:

- Commit scoped changes to `WORKER_BRANCH`, or return BLOCKED with an exact blocker and no uncommitted changes.
- If no commit is made, provide PATCH/EVIDENCE or a blocker classification; analysis-only output is not complete.
- Do not approve Reviewer, set benchmark eligibility, or write final PHASE22 / production readiness facts.
