# Goal05 PHASE22 Reviewer Pack Controller Handoff

status: reviewer_pack_ready_human_review_required
phase: PHASE22
parent_pr: 97

## Frozen Facts

- PHASE22 = in_progress
- Fixed Benchmark = BLOCKED / blocked_not_measured
- actual_case_count = 0
- reviewer_approved_count = 0
- benchmark_eligible_count = 0
- Production Readiness = not established

## Dataset Pack Hashes

```text
8b22d71456f43964  size=4488  docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json
4ee485bb9395a657  size=388   docs/evidence/goal05-phase22-blocked-benchmark/corpus_manifest.json
4ee485bb9395a657  size=388   docs/evidence/goal05-phase22-blocked-benchmark/corpus/manifest.json
48ab6c2aa8541db0  size=4230  docs/evidence/goal05-phase22-blocked-benchmark/cases.jsonl
0778845012e31392  size=85733 docs/evidence/goal05-phase22-public-benchmark-review-pack/candidate_cases.jsonl
f3592deea7e86fbd  size=1321  docs/evidence/goal05-phase22-public-benchmark-review-pack/integrity_report.json
962819e3750e0a62  size=339   docs/evidence/goal05-phase22-public-benchmark-review-pack/coverage_report.json
89b6dc6424e5efe0  size=397   docs/evidence/goal05-phase22-public-benchmark-review-pack/approval_summary.json
```

## Pack Contents (already produced by prior slices)

- `docs/evidence/goal05-phase22-blocked-benchmark/benchmark_manifest.json`
  records `status=BLOCKED`, `measurement_status=blocked_not_measured`,
  `actual_case_count=0`, `reviewer_approved_case_count=0`,
  `benchmark_eligible_case_count=0`.
- `docs/evidence/goal05-phase22-blocked-benchmark/corpus_manifest.json`
  records the fixed corpus snapshot reference.
- `docs/evidence/goal05-phase22-blocked-benchmark/cases.jsonl` lists the
  pinned blocked cases.
- `docs/evidence/goal05-phase22-public-benchmark-review-pack/candidate_cases.jsonl`
  contains 80 candidates (20 evidence_complete, 60 incomplete or rejected).
- `docs/evidence/goal05-phase22-public-benchmark-review-pack/integrity_report.json`
  records `Overall Status = REVIEW_REQUIRED`, near-duplicate threshold 0.8, no
  exact or near duplicates.
- `docs/evidence/goal05-phase22-public-benchmark-review-pack/coverage_report.json`
  records dataset slice coverage.
- `docs/evidence/goal05-phase22-public-benchmark-review-pack/approval_summary.json`
  records `reviewer_approved_count=0`, `benchmark_eligible_count=0`.

## Human Reviewer Items (must remain human only)

The controller does **not** approve reviewers, set eligibility, or write
release decision. The following items must be completed by the human reviewer
role before any of these values may change:

1. Inspect `integrity_report.json` and confirm 20 evidence_complete cases.
2. Approve or reject each candidate via the review pack tooling.
3. Sign or counter-sign the approval summary with reviewer identity and date.
4. Set `reviewer_approved_count` and `benchmark_eligible_count` only after
   approvals are recorded in the review pack.
5. Hand the signed pack back to the controller; controller then records a
   Measured benchmark run against the approved case set.

## Controller Boundary

The controller prepared the pack and recorded hashes. The controller did not
edit `integrity_report.json`, `coverage_report.json` or
`approval_summary.json` to promote any candidate from `REVIEW_REQUIRED` to
approved. The pack remains `REVIEW_REQUIRED` until the human reviewer signs.

## Reproducibility

The pack is reproducible via:

```powershell
python -m tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark `
    --questions-file tools/evals/zuno/rag_eval/python_notes_eval.jsonl `
    --runtime-mode contract-smoke `
    --sample-size 80 `
    --output-root docs/evidence/goal05-phase22-blocked-benchmark `
    --hard-negative-count 20 `
    --allow-blocked
```

## Boundary

This evidence does not claim PHASE22 completed, fixed benchmark measured,
release gate passed, production ready, archive or no-active reset.