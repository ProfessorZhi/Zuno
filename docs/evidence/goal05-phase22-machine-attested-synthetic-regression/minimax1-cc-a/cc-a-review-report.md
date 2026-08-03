# PHASE22 CC-A Dataset / Corpus / Validator Review (MiniMax1)

## Identity

- Agent-Name: MiniMax1
- Provider: MiniMax
- Worker-Task: PHASE22-CC-A
- Base SHA: `87f6eeed994d1db28f25ad916e052b3a3cd00992` (PR #107 exact head)
- Branch: `claude/minimax1-phase22-cc-a`

## Scope Reviewed

1. 80-case candidate dataset (`docs/evidence/goal05-phase22-machine-attested-synthetic-regression/candidate-dataset/synthetic_cases.jsonl`).
2. Synthetic corpus (`candidate-dataset/corpus/*.md`, 8 documents).
3. World model (`candidate-dataset/world_model.json`).
4. Derivation validator (`tools/evals/zuno/synthetic_benchmark/derivation_validator.py`).
5. Source span / source evidence (125 spans across 8 docs).
6. Duplicate question / case_id audit.
7. Gold leakage guard.
8. Hard negative (`abstain_scan`) guard.
9. Input hash / case hash integrity for all 80 cases.

## Current Facts (observed and re-verified)

| Metric                       | Target | Observed |
|------------------------------|-------:|---------:|
| case_count                   |     80 |       80 |
| derivation_valid_count       |     80 |       80 |
| source_evidence_valid_count  |     80 |       80 |
| unsupported_answer_count     |      0 |        0 |
| duplicate_question_count     |      0 |        0 |
| gold_leakage_count           |      0 |        0 |
| hard_negative_valid_count    |      5 |        5 |
| hash_valid_count             |     80 |       80 |
| reviewer_approved_count      |      0 |        0 |
| benchmark_eligible_count     |      0 |        0 |

Hashes (re-computed, all match):

- `dataset_hash`: `b7832e537dbaab14a7d664f334676120f10b86aa8b7efddfc7220bc7bc915f0c`
- `corpus_hash`: `749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4`
- `world_model_hash`: `f3078e20b11feb468285fcca07fa09a920a5be4f280841957dc447938dc76242`
- `candidate_derivation_report_hash`: `7c0a118e77b6d2c49a9b4086b853d3eaf4ddf5a56236bda64cd8644e07e5d834`

## Verifier Results

- `python tools/scripts/verify_phase22_synthetic_regression_track.py` → exit 0, "PHASE22 synthetic regression track boundary passed".
- `python -m pytest -q tests/evals/synthetic_benchmark/test_dataset_contract.py tests/repo/test_phase22_synthetic_regression_track.py -p no:cacheprovider` → 45 passed.
- `git diff --check` → clean (no whitespace or conflict markers introduced; this branch adds only evidence).

## SourceSpan / Source Evidence Audit

- Total spans in candidate dataset: 125
- Spans that resolve in their cited document body: 125
- Unmatched document refs: 0

## Duplicate Audit

- Total case_ids: 80 — unique: 80
- Total questions (lowercased + whitespace-normalized): 80 — unique: 80
- No question contains its own expected_answer substring.

## Gold Leakage Audit

- Forbidden runtime gold fields: `gold_document_ids`, `gold_source_spans`, `gold_citations`, `gold_document_refs`, `gold_evidence_refs`, `citation_ground_truth`, `expected_path` — none appear in any of the 80 cases.

## Hard Negative Audit

- 5 `abstain_scan` cases use `missing_fact=fy2025_revenue` with `authorized_corpus_scope=["global/open"]`. None of the global/open corpus docs contain a `fy2025 revenue` token, so the negative is genuine.

## Findings

- `FIND-CC-A-001` (info): 80/80 candidate dataset, derivation, source evidence, hash all pass.
- `FIND-CC-A-002` (info): 125/125 source spans resolve to the cited corpus body.
- `FIND-CC-A-003` (info): world model derives the expected answer for all 80 cases.
- `FIND-CC-A-004` (info): hard negative count is exactly 5; negative is genuinely absent.
- `FIND-CC-A-005` (info): reviewer_approved_count and benchmark_eligible_count remain 0; the track is machine-attested candidate only.

No real defects found — no fixes were required.

## Boundary Assertions

- Did NOT create a second dataset.
- Did NOT change `PHASE22 -> completed`.
- Did NOT change `Synthetic Track -> ready`.
- Did NOT change `Production Readiness -> ready`.
- Did NOT change `Public Benchmark -> passed`.
- Machine attestation is not being substituted for a human reviewer approval.

## Tests Not Run

- Live MinIO readback — out of CC-A scope (CC-B).
- Live PostgreSQL fact idempotency — out of CC-A scope (CC-B).
- Live ES / Milvus / Neo4j visibility receipts — out of CC-A scope (CC-B / CC-C).
- Four-profile runtime — out of CC-A scope (CC-C).
- Cross-tenant / workspace isolation matrix — out of CC-A scope (CC-D).
- Fault injection matrix — out of CC-A scope (CC-D).

These are intentionally NOT_RUN for CC-A and belong to the downstream CC-B/CC-C/CC-D workers.

## Remaining Gaps (reported, not fixed)

- `GAP-META-001`: `phase22-synthetic-handoff-{gap-ledger,manifest}.yaml` reference
  `source_pr_107_head=6c9c75eaea16a047107e20fa156824bce068ee4c` but the actual
  PR #107 head at review time is `87f6eeed994d1db28f25ad916e052b3a3cd00992`.
  These work-product files are explicitly out of CC-A's allowed scope; flagged
  for coordinator attention.
