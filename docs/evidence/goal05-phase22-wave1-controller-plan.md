# Goal05 PHASE22 Wave 1 Controller Plan

status: controller_plan_ready
phase: PHASE22
parent_pr: 97
integration_branch: codex/phase22-final-closure
integration_base_sha: dfb9981995f4193488ca022ee5ec15eeff6a6349
integration_setup_sha: c8edb67921dc134c641375dfe624f8b93a048a2a
controller_token_status: NOT_AVAILABLE_APP_SESSION

## Current

- 当前唯一阶段为 PHASE22。
- PHASE15、PHASE20、PHASE21 已 completed。
- Target Coverage Audit 已冻结，不重新扫描十一模块，不重建 Gap Ledger。
- Mandatory Target Coverage = 11/11 CURRENT。
- Removal Candidates = 7/7 resolved_retired。
- Fixed Benchmark = BLOCKED / blocked_not_measured。
- actual_case_count = 0。
- reviewer_approved_count = 0。
- benchmark_eligible_count = 0。
- Program = active，PHASE22 = in_progress。
- Production Readiness not established。
- `source_sha_at_generation` 表示证据生成时的源树，不要求等于承载证据的提交 SHA。

## Gap

- G1 Dataset / Corpus / Case Set / Review Pack：候选包存在，但 reviewer_approved_count 和 benchmark_eligible_count 仍为 0。
- G2 Benchmark Runtime：四 Profile canonical boundary、runtime evidence binding 和 measurement attestation 仍需证明可进入正式 measured/comparable 路径；不得用 test double 或裸布尔值冒充。
- G3 Canonical Tree：已知 removal candidates resolved，但仍需最终扫描重复包、旧命名、临时兼容、旁路和永久双路径。
- G4 Verification Matrix：Repo、Backend、Web、Desktop、E2E、Fault、Security、Load、DR、Backup/Restore 等最终验证尚未完整披露。
- G5 Release / Readiness / Archive：未获得真实 Reviewer Approval 和正式 measured benchmark 前，不得 Release Decision PASS、不得 PHASE22 completed、不得 production ready、不得 archive/no-active。

## DAG

```text
W1-MM-1 Dataset Pack
  -> Wave 2 Human Review Stop
  -> Wave 3 Formal Four-profile Benchmark

W1-DS-1 Benchmark Runtime
  -> Wave 3 Formal Four-profile Benchmark

W1-MM-2 Canonical Tree
  -> Wave 4 Final Verification

W1-MM-3 Verification Matrix
  -> Wave 4 Final Verification

Wave 3 Formal Four-profile Benchmark
  -> Wave 4 Release Decision / Final Verification
  -> Wave 5 Production Readiness Truth / Program Archive / no-active
```

## Worker 分工

| Worker | Provider | Status | Worktree | Branch | Scope |
| --- | --- | --- | --- | --- | --- |
| MM-1 | MiniMax | BLOCKED_EXTERNAL_CONFIG_REQUIRED | TBD | agent/minimax/phase22-dataset-pack-pr97 | Dataset、Corpus、Case、Hash、Manifest、Reviewer Pack；不得批准 Reviewer。 |
| MM-2 | MiniMax | BLOCKED_EXTERNAL_CONFIG_REQUIRED | TBD | agent/minimax/phase22-canonical-tree-pr97 | Canonical tree scan、低风险 cleanup、boundary evidence。 |
| MM-3 | MiniMax | BLOCKED_EXTERNAL_CONFIG_REQUIRED | TBD | agent/minimax/phase22-verification-matrix-pr97 | Verification command matrix、真实退出码和 blocked 分类。 |
| DS-1 | DeepSeek | READY | `F:\internship-work\resume&resume project\02_projects\Zuno-worktrees\deepseek-phase22-benchmark-runtime-pr97` | agent/deepseek/phase22-benchmark-runtime-pr97 | Benchmark harness、Profile adapter、runtime evidence binding、measurement attestation、Agentic GraphRAG formal path。 |

## Allowed Paths

### Codex Only

- `.agent/programs/**`
- `.agent/references/current-program.md`
- `docs/status/production-readiness.md`
- Final benchmark manifest / reviewer approval / release decision / archive state
- Parent PR body and integration commits

### MM-1 Dataset Pack

- `tools/evals/zuno/**`
- `tests/evals/**`
- `docs/evidence/goal05-phase22-public-benchmark-review-pack/**`
- `docs/evidence/goal05-phase22-dataset-pack-worker-mm1.md`

### MM-2 Canonical Tree

- `tools/scripts/verify_phase22_cleanup_boundary.py`
- `tests/repo/**`
- `tests/api/**`
- `tests/frontend/**`
- Low-risk production import cleanup under `src/backend/zuno/**` only when a canonical replacement already exists.
- `docs/evidence/goal05-phase22-canonical-tree-worker-mm2.md`

### MM-3 Verification Matrix

- `tools/scripts/**`
- `tests/**`
- `apps/web/**` read/build only unless a low-risk test harness fix is required.
- `docs/evidence/goal05-phase22-verification-matrix-worker-mm3.md`

### DS-1 Benchmark Runtime

- `tools/evals/zuno/**`
- `tests/evals/**`
- `tests/fault/evals/**`
- `tests/integration/evals/**`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/agent/**`
- `src/backend/zuno/platform/observability/**`
- `docs/evidence/goal05-phase22-benchmark-runtime-worker-ds1.md`

## Conflict Matrix

| Key | Owner | Conflicts With | Rule |
| --- | --- | --- | --- |
| benchmark-final-manifest | Codex | all workers | Workers may draft candidate data only; Codex writes final benchmark facts. |
| reviewer-approval | Codex / Human Reviewer | all workers | Workers must not set reviewer_approved or benchmark_eligible. |
| release-decision | Codex | all workers | Workers may expose inputs; Codex executes final decision. |
| production-readiness | Codex | all workers | Workers may draft evidence; Codex updates readiness truth. |
| program-state | Codex | all workers | PHASE22 remains in_progress until all gates pass. |
| dataset-pack | MM-1 | DS-1 final benchmark | DS-1 must not rewrite review pack approval facts. |
| canonical-runtime-adapter | DS-1 | MM-2 cleanup | MM-2 must not delete runtime code DS-1 needs without explicit Codex review. |
| verification-matrix | MM-3 | MM-2 cleanup / DS-1 runtime | MM-3 records failures; fixes require scoped follow-up. |

## Metrics Preflight

- Objective path `F:\funny_project\agent-metrics-collector` was not present.
- Actual metrics root used for read-only preflight: `F:\funny_project\agent-metrics-workspace\agent-metrics-collector`.
- DeepSeek snapshot status: AVAILABLE.
- MiniMax snapshot status: CONFIG_REQUIRED.
- Codex snapshot status: PARTIAL; controller app token status recorded as NOT_AVAILABLE_APP_SESSION.
- Snapshot quota context is not treated as this task's token usage.

## Stop Conditions

- Architecture Owner / Contract semantic changes.
- Security, approval, budget, attestation or sandbox weakening.
- Irreversible migration.
- Any attempt to promote BLOCKED / REVIEW_REQUIRED / test double / naked boolean into MEASURED or PASS.
- Any attempt to write PHASE22 completed, production ready, archive or no-active before all gates are proven.

