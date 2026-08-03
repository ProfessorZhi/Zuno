# P22 CC-MM-1 Synthetic Dataset and Validator

agent=claude-code
model=claude-minimax
worker=CC-MM-1
cost_scope=single-agent-pr-handoff
worktree=F:\internship-work\resume project\worktrees\claude-minimax-cc-mm-1
branch=codex/phase22-synthetic-dataset-claude-minimax-cc-mm-1

## Goal

把 PR #100 的 synthetic dataset 候选改造成真正机器可验证的 dataset tooling 初稿，但不得运行真实 benchmark，不得声明 measured/pass/completed/production ready。

## Read First

- `AGENTS.md`
- `.agent/references/workflow.md`
- `.agent/references/command-catalog.md`
- `.agent/programs/PHASE22_fixed-benchmark-production-readiness-and-closure.md`
- `docs/evidence/goal05-phase22-pr100-codex-review.md`

## Allowed Paths

- `tools/evals/zuno/synthetic_benchmark/**`
- `tests/evals/synthetic_benchmark/**`
- `docs/evidence/goal05-phase22-worker-cc-mm-1-synthetic-dataset.md`

## Forbidden Paths

- `.agent/programs/program-manifest.yaml`
- `.agent/programs/current.md`
- `docs/status/production-readiness.md`
- `docs/evidence/goal05-phase22-synthetic-benchmark/**`
- `tools/evals/zuno/rag_eval/**`
- runtime production code under `src/backend/zuno/**`

## Tasks

1. Use PR #100 only as candidate source via `git show d7566624b702b74ebf6a89db2f916b9ea19b310c:<path>`.
2. Move executable dataset code into `tools/evals/zuno/synthetic_benchmark/**`.
3. Add declaration-level DerivationSpec per case.
4. Validator must independently derive answer support from world model / corpus / graph, not from runtime outputs.
5. Validate relation `kind/from/to/direction`, temporal version, source span support, no-answer authorized corpus scan, and security caller principal / role / scope / epoch.
6. Prove empty-directory same seed regeneration is hash-stable.
7. Add focused tests under `tests/evals/synthetic_benchmark/**`.
8. Evidence must state `synthetic_dataset_candidate_only`, not benchmark measured.

## Validation

```powershell
python tools/scripts/verify_phase22_synthetic_truth_boundary.py
pytest -q tests/evals/synthetic_benchmark -p no:cacheprovider
git diff --check
```

## Handoff

Return identity, actual `session_id`, branch, commit, changed files, validation, risks, blockers, duration, `api_cost_usd_estimated`, and `provider_quota_basis`.
