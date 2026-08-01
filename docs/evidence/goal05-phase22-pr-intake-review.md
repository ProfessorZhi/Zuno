# Goal05 PHASE22 PR Intake Review Evidence

status: in_progress
date: 2026-08-01
branch: agent/antigravity/phase22-authoritative-remote-test-gate
target_main_sha: 5b6f880df88fd1d1f3efc782eedd8466aff45554

## Scope

本证据记录 PHASE22 多 Agent Draft PR 的 intake 审核结果，用于后续合并排序、替代关系和状态判定。

本证据不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 quality proven，不声明 production ready。

## Current PR Topology

按 2026-08-01 已获取的 GitHub PR 元数据和本地 `origin/*` refs，当前 PR 链路为：

| PR | Head | Base | 判断 |
| --- | --- | --- | --- |
| #51 | `codex/goal05-target-coverage-audit` | `main` | PR A 入口；Coverage Audit / Gap Ledger 冻结入口，仍为 Draft。 |
| #52 | `codex/goal05-phase15-sandbox-repair` | `codex/goal05-target-coverage-audit` | PHASE15/20/21/22 主修复串；远端 PHASE22 Contract Verification 曾通过，但 PR 面积很大，仍需按后续 PR 逐项吸收。 |
| #54 | `agent/qoder/phase22-dataset-evidence-integrity` | `codex/goal05-phase15-sandbox-repair` | 可作为 benchmark candidate integrity evidence；不能解锁 measured benchmark。 |
| #56 | `agent/antigravity/phase22-deep-agentic-canonical-adapters` | `codex/goal05-phase15-sandbox-repair` | 可作为 deep/agentic canonical adapter boundary 候选；证明 fail-closed adapter boundary，不证明质量提升。 |
| #59 | `docs/phase22-agent-performance-governance` | `codex/goal05-phase15-sandbox-repair` | governance base；已吸收 release decision engine 子 PR，并有远端 PHASE22 Contract Verification 通过记录。 |
| #60 | `agent/deepseek/phase22-runtime-evidence-binding-contract-v2` | `docs/phase22-agent-performance-governance` | 被 #64 整合替代；不应再单独合并以免重复控制面。 |
| #61 | `agent/minimax/phase22-benchmark-preflight-contract-v2` | `docs/phase22-agent-performance-governance` | 被 #64 整合替代；不应再单独合并以免重复控制面。 |
| #64 | `agent/deepseek/phase22-measurement-admission-evidence-closure` | `docs/phase22-agent-performance-governance` | measurement admission / runtime binding / preflight closure 候选；本地目标测试通过，但不等于 fixed benchmark measured。 |

## Local Review Results

### `.qoder/repowiki/`

` .qoder/repowiki/` 是 Qoder 生成的 repo wiki/cache：75 个文件，约 1.6 MiB。抽样发现：

- 元数据包含 `raw_data: WikiEncrypted...`、生成时间、生成分支和工具版本；
- 内容形成一套非 `docs/` / `.agent/` 治理的架构叙述；
- 抽样文档存在与 current canonical tree 不完全一致的说法，例如把容器依赖写成 `PostgreSQL/MySQL`，以及引用疑似旧路径 `src/backend/zuno/agent/runtime.py`。

结论：不纳入 Git。已在 `.gitignore` 加入 `.qoder/repowiki/`，本地生成物可保留但不得成为正式事实源。

### PR #54 Dataset Integrity

本地验证：

```text
python -m pytest -q tests/evals/test_public_benchmark_candidate_integrity.py -p no:cacheprovider
43 passed in 2.89s
```

已审阅 `docs/evidence/goal05-phase22-public-benchmark-review-pack/integrity_report.json`：

```text
total_case_count: 80
verified_count: 20
incomplete_count: 60
reviewer_approved_count: 0
benchmark_eligible_count: 0
overall_status: REVIEW_REQUIRED
```

结论：#54 可以作为候选数据完整性审计证据；它明确阻断 measured benchmark，不得作为 P22-T01/P22-T02 完成证据。

### PR #56 Deep / Agentic Adapter Boundaries

本地验证：

```text
python -m pytest -q tests/evals/test_canonical_deep_agentic_runtime.py tests/fault/evals/test_canonical_deep_agentic_faults.py tests/integration/evals/test_canonical_deep_agentic_integration.py tests/repo/test_canonical_agentic_bypass_guard.py -p no:cacheprovider
37 passed in 4.41s
```

结论：#56 可以作为 fail-closed deep/agentic canonical adapter boundary 候选；它不证明 runtime_observed quality，也不证明 production ready。

### PR #64 Measurement Admission / Preflight / Runtime Binding

本地验证：

```text
python -m pytest -q tests/evals/test_runtime_evidence_binding.py tests/evals/test_phase22_benchmark_preflight.py tests/evals/test_phase22_measurement_control_contracts.py -p no:cacheprovider
227 passed, 30 subtests passed in 7.90s
```

结论：#64 是 #60/#61 的替代整合候选；它证明 admission/preflight/runtime binding 控制面 fail-closed，不证明正式 fixed benchmark 已测量。

## Merge Guidance

建议合并/吸收顺序：

```text
#51
→ #52
→ #54 / #56 / #59
→ #64
```

若采用 #64，应关闭 #60/#61，不再单独合并。

任何合并后状态更新必须继续保持：

- `REVIEW_REQUIRED` / `BLOCKED` 不能写成 `MEASURED`；
- adapter boundary 不能写成 quality proven；
- preflight/admission pass 不能写成 benchmark measured；
- PHASE22 completed 仍需等待 fixed benchmark 真实状态、legacy-free final verification、Production Readiness truth 和 Program archive evidence。

## Commands

```text
git fetch origin main
git rev-parse origin/main
git branch --show-current
git status --short -uall
gh pr list --repo ProfessorZhi/Zuno --state open --limit 20 --json number,title,headRefName,baseRefName,isDraft,updatedAt,url
python .agent/scripts/verify_repo_hygiene.py
git diff --check
```

GitHub API 在 2026-08-01 的两次列表请求出现 transient `EOF`，因此本证据同时使用已获取的 PR 元数据、本地 `origin/*` refs 和各 PR worktree 的目标测试结果。
