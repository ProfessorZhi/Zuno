# P22 CC-MM-2 Environment and Verification

agent=claude-code
model=claude-minimax
worker=CC-MM-2
cost_scope=single-agent-pr-handoff
worktree=F:\internship-work\resume project\worktrees\claude-minimax-cc-mm-2
branch=codex/phase22-environment-verification-claude-minimax-cc-mm-2

## Goal

准备并执行真实依赖环境、服务健康、索引 write/read-back 和故障矩阵候选证据。环境健康只能证明 dependency readiness，不能写成 benchmark PASSED。

## Read First

- `AGENTS.md`
- `.agent/references/workflow.md`
- `.agent/references/command-catalog.md`
- `.agent/programs/powershell-runbook.md`
- `.agent/programs/PHASE22_fixed-benchmark-production-readiness-and-closure.md`
- `docs/evidence/goal05-phase22-pr100-codex-review.md`

## Allowed Paths

- `infra/docker/**`
- `tools/evals/zuno/synthetic_benchmark/**`
- `tools/scripts/**phase22*environment*.py`
- `tests/evals/synthetic_benchmark/**`
- `docs/evidence/goal05-phase22-worker-cc-mm-2-environment-verification.md`

## Forbidden Paths

- `.agent/programs/program-manifest.yaml`
- `.agent/programs/current.md`
- `docs/status/production-readiness.md`
- `docs/evidence/goal05-phase22-synthetic-benchmark/**`
- core runtime contracts under `src/backend/zuno/**`
- any destructive host cleanup command

## Tasks

1. Inspect Docker compose paths and required services: PostgreSQL, Elasticsearch, Milvus, Neo4j, RabbitMQ, MinIO, Checkpointer.
2. Record exact commands, versions, ports and health status.
3. Run or draft a non-destructive write/read-back matrix for available services.
4. Test repeated run, partial failure, service unavailable and recovery where feasible.
5. Record only owner-produced refs; do not fabricate receipts.
6. Return blockers with exact command output if Docker or images are unavailable.

## Validation

```powershell
python tools/scripts/verify_phase22_synthetic_truth_boundary.py
git diff --check
```

## Handoff

Return identity, actual `session_id`, branch, commit, changed files, validation, risks, blockers, duration, `api_cost_usd_estimated`, and `provider_quota_basis`.
