# P22 CC-DS-1 Canonical Ingestion Candidate

agent=claude-code
model=claude-deepseek
worker=CC-DS-1
cost_scope=single-agent-pr-handoff
worktree=F:\internship-work\resume project\worktrees\claude-deepseek-cc-ds-1
branch=codex/phase22-canonical-ingestion-claude-deepseek-cc-ds-1

## Goal

调查并实现 Auroralis corpus 经 Zuno 正式 Ingestion Application Service 进入 KnowledgeVersion、Snapshot 和三索引的候选实现。缺少正式入口时返回 `BLOCKED_WITH_EXACT_GAP`，不得创建平行 runtime。

## Read First

- `AGENTS.md`
- `.agent/references/code-map.md`
- `.agent/references/workflow.md`
- `.agent/programs/PHASE22_fixed-benchmark-production-readiness-and-closure.md`
- `docs/evidence/goal05-phase22-pr100-codex-review.md`

## Allowed Paths

- `src/backend/zuno/knowledge/ingestion/**`
- `src/backend/zuno/knowledge/storage/**`
- `src/backend/zuno/platform/database/ingestion/**`
- `src/backend/zuno/platform/storage/**`
- `src/backend/zuno/platform/services/pipeline/**`
- `src/backend/zuno/platform/services/rag/**`
- `src/backend/zuno/platform/services/graphrag/**`
- `tools/evals/zuno/synthetic_benchmark/**`
- `tests/integration/**`
- `tests/evals/synthetic_benchmark/**`
- `docs/evidence/goal05-phase22-worker-cc-ds-1-canonical-ingestion.md`

## Forbidden Paths

- `.agent/programs/program-manifest.yaml`
- `.agent/programs/current.md`
- `docs/status/production-readiness.md`
- `docs/evidence/goal05-phase22-synthetic-benchmark/**`
- `tools/evals/zuno/rag_eval/**`
- fake Trace / Receipt / RunOutcome / MeasurementAttestation generators

## Tasks

1. Identify formal ingestion owner entrypoints, repositories, UoW, Object Store, ES, Milvus and Neo4j adapters.
2. If a real application service exists, implement a small candidate runner that uses those owner interfaces.
3. Prove write/read-back, visibility, activation and idempotency where local tests can cover it.
4. If formal entrypoints are missing, return `BLOCKED_WITH_EXACT_GAP` with exact file/function gaps.
5. Do not run four profiles and do not generate fake receipts.

## Validation

```powershell
python tools/scripts/verify_phase22_synthetic_truth_boundary.py
pytest -q tests/integration/test_phase11_ingestion_persistence_runtime.py tests/integration/test_phase11_package_a_production_runtime.py -p no:cacheprovider
git diff --check
```

## Handoff

Return identity, actual `session_id`, branch, commit, changed files, validation, risks, blockers, duration, `api_cost_usd_estimated`, and `provider_quota_basis`.
