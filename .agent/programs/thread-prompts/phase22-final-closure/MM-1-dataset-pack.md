# MM-1 Dataset Pack Worker Prompt

WORKER_TASK_ID: MM-1
PARENT_PR: 97
PROVIDER: MiniMax
BASE_BRANCH: codex/phase22-final-closure
WORKER_BRANCH: agent/minimax/phase22-dataset-pack-pr97

MiniMax is currently CONFIG_REQUIRED in controller preflight. Do not run this task until Codex confirms provider availability.

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

