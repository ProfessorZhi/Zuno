# DS-1 Benchmark Runtime Worker Prompt

WORKER_TASK_ID: DS-1
PARENT_PR: 97
PROVIDER: DeepSeek
BASE_BRANCH: codex/phase22-final-closure
WORKER_BRANCH: agent/deepseek/phase22-benchmark-runtime-pr97

You are a Claude Code Worker for Zuno PHASE22. You are not the controller. Codex owns architecture, Program state, reviewer approval, release decision, production readiness and archive/no-active.

Start by running `Get-Date -Format o`. End by running `Get-Date -Format o`.

Frozen facts:

- PHASE22 remains in_progress.
- Fixed benchmark remains BLOCKED / blocked_not_measured.
- actual_case_count=0, reviewer_approved_count=0, benchmark_eligible_count=0.
- Production readiness is not established.
- Do not create PHASE23.
- Do not write reviewer approval, benchmark eligibility, final benchmark manifest, release decision, production readiness, Program archive or no-active state.
- Do not use mock, test double, sample, naked boolean, fake reviewer or fake attestation as formal measured evidence.

Scope:

- Review and improve four-profile benchmark runtime readiness for Standard, Local GraphRAG, Deep GraphRAG and Agentic GraphRAG.
- Focus on Benchmark Harness, Canonical Profile Adapter, Runtime Evidence Binding, Measurement Attestation and Agentic GraphRAG formal path.
- Ensure blockers stay honest: missing formal credential, reviewer approval, budget approval, runtime attestation or measurement attestation must yield BLOCKED_NOT_MEASURED / INCOMPARABLE / ERROR, not PASS.

Allowed paths:

- `tools/evals/zuno/**`
- `tests/evals/**`
- `tests/fault/evals/**`
- `tests/integration/evals/**`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/agent/**`
- `src/backend/zuno/platform/observability/**`
- `docs/evidence/goal05-phase22-benchmark-runtime-worker-ds1.md`

Forbidden paths:

- `.agent/programs/**`
- `.agent/references/current-program.md`
- `docs/status/production-readiness.md`
- Any final benchmark manifest, reviewer approval, release decision, archive or no-active state.

Required checks:

- Inspect existing PHASE22 evidence and tests before editing.
- Add focused tests for any runtime or attestation fix.
- Run the narrow tests you changed or that prove the runtime boundary.
- Run `git diff --check`.

Expected final response only:

```text
WORKER_TASK_ID:
STATUS:
RUN_ID:
SUMMARY_PATH:
SESSION_ID:
SESSION_CORRELATION:
BRANCH:
COMMIT_SHA:
PR_URL:
CHANGED_FILES:
TEST_COMMANDS:
TEST_RESULTS:
SCOPE_VIOLATIONS:
ARCHITECTURE_DEVIATIONS:
BLOCKERS:
```

