# MM-4 Live MiniMax Worker Probe Prompt

WORKER_TASK_ID: MM-4
PARENT_PR: 97
PROVIDER: MiniMax
BASE_BRANCH: codex/phase22-final-closure
WORKER_BRANCH: agent/minimax/phase22-canonical-cleanup-wave1

This is a live MiniMax Worker probe to record a real Worker Run ID on PR #97.

Quota snapshot status is `CONFIG_REQUIRED`; that does not block execution.

You are a Claude Code Worker for Zuno PHASE22. You are not the controller.

This task card must be passed in full. If you only see the title or a truncated prompt, stop and return BLOCKED_PROMPT_TRUNCATED.

Scope when enabled:

- Verify the dispatcher protocol by performing one small benign edit that proves end-to-end commit/push.
- Append one line to `docs/evidence/goal05-phase22-minimax-live-probe.md` confirming `MiniMax-M3` was the model.
- Do not alter architecture ownership, shared contracts, Program state, production readiness or release facts.

Allowed paths:

- `docs/evidence/goal05-phase22-minimax-live-probe.md`

Required Checks:

- git diff --check
- python -m pytest -q tests/repo/test_dispatch_claude_worker.py::test_only_title_task_card_is_rejected_before_runner -p no:cacheprovider

Completion Contract:

- Return COMMIT_SHA when a commit is made.
- Return TEST_RESULTS for every Required Check.
- Return BLOCKERS when blocked.
- Return BLOCKED_PROMPT_TRUNCATED if this Task Card is not visible in full.

Forbidden Paths:

- .agent/programs/program-manifest.yaml
- src/backend/**
- main branch
- any non-allowed path

Worker Result Schema:

- COMMIT_SHA
- TEST_RESULTS
- BLOCKERS
- METRICS_RUN_ID if available

Stop Conditions:

- BLOCKED_PROMPT_TRUNCATED when prompt is truncated.

This is a minimum-risk probe. Do not make any other changes. Commit your single evidence edit, push the branch, and emit the worker result JSON line `WORKER_RESULT_JSON=...`.