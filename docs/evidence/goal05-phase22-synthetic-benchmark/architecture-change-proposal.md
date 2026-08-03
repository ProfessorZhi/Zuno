# Architecture Change Proposal — PHASE22 Synthetic Enterprise Benchmark Track

Author: Claude Code + MiniMax (synthetic track implementation)
Date: 2026-08-03
Target Reviewer: ChatGPT
Head: claude-minimax/phase22-synthetic-benchmark @ <exact Head below>
Tracks touched: new synthetic track only — public/human-review track untouched

This ACP proposes a new, third track alongside the existing
human-review track (`goal05-phase22-public-benchmark-review-pack/`) and the
existing blocked fixed-benchmark track (`goal05-phase22-blocked-benchmark/`).
It is intentionally additive: the human-review closure contract is NOT
modified here, and no human-review field is overwritten.

## 1. Scope

The proposal introduces a **machine-attested synthetic enterprise benchmark**
that produces 80 fully-fictional, fully-versioned, fully-machine-validated
questions derived from a deterministic world model and corpus. All gating for
this track is performed by a deterministic validator. The track is
explicitly NOT a substitute for human review of the public benchmark.

## 2. What the synthetic track CAN substitute

- A reproducible, version-pinned, hash-stable corpus of 62 documents and
  92 relations. Every fact is deterministically regenerated from the same
  seed (`phase22-synthetic-2026-08-03-auroralis-v1`).
- A stratification that exercises all 7 PHASE22 question-type buckets the
  fixed benchmark is supposed to measure:
  - 20 single-doc fact
  - 20 cross-document multi-hop
  - 15 graph (path / relation / community)
  - 10 version / time / conflict
  - 5 no-answer (must abstain)
  - 5 permission / sensitive (must deny or restrict)
  - 5 fault / partial-index controlled behavior
- A machine-validated case set with full provenance (world_model_hash,
  corpus_snapshot_hash, graph_manifest_hash, generation_seed, security
  scope, effective time, hard negative references, required relations).
- An end-to-end wiring of the four canonical profile contracts (Standard
  RAG / Local GraphRAG / Deep GraphRAG / Agentic GraphRAG) on the synthetic
  KnowledgeVersion/Snapshot, with honest BLOCKED recording when
  Elasticsearch / Milvus / Neo4j are not reachable.

## 3. What the synthetic track CANNOT prove

The synthetic track explicitly does NOT prove any of the following about the
real-world public benchmark or the Zuno production runtime:

1. **Human-review completion.** No reviewer approval count is added to the
   public benchmark pack; `reviewer_approved_count` remains 0 and
   `benchmark_eligible_count` remains 0.
2. **Production-readiness.** The PHASE22 release decision is BLOCKED when
   infrastructure is not present. The synthetic track does not flip the
   production readiness status from `implementation_available_measurement_in_progress`
   to anything else.
3. **Real-world retrieval correctness on third-party enterprise corpora.**
   The corpus is fictional and cannot speak to retrieval quality on
   TechQA / CFQA / EnterpriseRAG-Bench / OpenRAG or any other third-party
   benchmark the human-review pack ingests.
4. **Real LLM judge faithfulness, citation hallucination rate, or
   answer-correctness on actual enterprise questions.** Synthetic expected
   answers are author-written; they cannot substitute for graded real
   answers by human reviewers.
5. **Multi-tenant isolation, security epoch enforcement, real Postgres /
   RabbitMQ / MinIO behaviour, or runtime attestation under load.**
6. **The four canonical profiles MEASURED under real infrastructure.**
   In the current environment, Elasticsearch, Milvus, Neo4j, Postgres,
   RabbitMQ and MinIO are all unreachable, so the four profiles are
   recorded as `BLOCKED` with explicit gap codes. No MEASURED value is
   invented.

## 4. Machine attestation ownership

- **Owner of the synthetic world model and corpus**: Claude Code + MiniMax,
  this PR. SHA-256 of `world_model.json`, `corpus_manifest.json`,
  `graph_manifest.json` and every corpus document are recorded under
  `derived/corpus_hashes.json`.
- **Owner of the synthetic case set**: Claude Code + MiniMax, this PR.
  SHA-256 of `synthetic_cases.jsonl` is recorded in
  `case_set_manifest.json`.
- **Owner of the machine validator**: deterministic
  `validate_cases.py` shipped with this PR. The validator is the
  authoritative gate for the `machine_validated` field; no model critic
  is allowed to convert a failed case into a passing case.
- **Owner of the canonical runtime adapter wiring**: the existing
  `tools/evals/zuno/rag_eval/canonical_profile_runners.py` plus
  `tools/evals/zuno/rag_eval/adapters/*.py`. The synthetic track calls
  them via `ingest_and_run.py` and records per-profile Trace, RunOutcome,
  Usage/Budget, Citation, Artifact/Measurement Attestation.
- **Owner of the release decision**: `release_decision.json` produced by
  `ingest_and_run.py`. Verdict is BLOCKED today because infrastructure
  is unreachable.

## 5. Self-evaluation / overfitting risks

The synthetic track has known limitations that are easy to over-fit on:

1. **Author-written ground truth.** The expected answers, gold source
   spans, and graph paths are written by the same author that wrote the
   world model. This means a trivial substring retriever can score near
   100% on this benchmark without exercising any real model capability.
   This is why the synthetic track is labelled `machine_attested` and
   explicitly NOT a substitute for human-reviewed benchmark grading.
2. **Closed world.** All facts are inside the corpus; no out-of-corpus
   facts are required. Real enterprise corpora frequently have gaps,
   contradictions across sources, and stale references that the synthetic
   corpus does not exercise with the same difficulty.
3. **Easy distractors.** The hard-negative references are limited to a
   handful of documents; in production a real benchmark should have
   hundreds of distractor documents per question.
4. **English-only, no OCR / VLM / multilingual stress.** The corpus is
   plain English markdown.
5. **No real judge model.** Citation accuracy and answer correctness are
   computed deterministically against the author-written expected answer,
   not against a real judge. The synthetic track therefore does not
   measure LLM judge calibration.
6. **Generation seed reproducibility, not statistical significance.**
   The same seed produces identical hashes; that is reproducibility, not
   variance estimation.

Mitigations:

- The validator explicitly counts and reports the count of
  `machine_validated_count`. Reviewers (and ChatGPT) can decide to
  discount this track for these reasons.
- The synthetic track is published as a **separate, third track** and is
  not used to satisfy any Program verification rule that requires
  `reviewer_approved_count > 0`.
- The PHASE22 completion blocker gate remains in force: PHASE22 may not
  be marked `completed`, Program may not be archived, and
  `production-readiness.md` may not be flipped to `production ready`
  on the basis of this track alone.

## 6. Fixed benchmark completion eligibility

**No**, the synthetic track alone cannot satisfy PHASE22 "Fixed Benchmark
Completion" for the following reasons:

- The PHASE22 contract requires `reviewer_approved_count > 0` on the
  public benchmark pack before PHASE22 may close; the synthetic track
  explicitly does not increment this field.
- The PHASE22 contract requires comparable real MEASURED evidence across
  all four profiles; the synthetic track can only produce MEASURED when
  Elasticsearch / Milvus / Neo4j / Postgres are reachable. In the
  current environment they are not, so the release decision is BLOCKED.
- The PHASE22 contract requires production-readiness to be
  `implementation_available` for Phase-internal evidence; flipping it to
  `production ready` requires human-graded real benchmark evidence.

What the synthetic track CAN do is unblock some prerequisites:

- Provide a hash-stable corpus and case set that future human reviewers
  can reference.
- Provide a deterministic validator and a deterministic reproduction
  recipe so reviewers do not need to trust the generator's word.
- Provide per-profile wiring evidence that the four canonical adapter
  contracts are reachable from the synthetic KnowledgeVersion/Snapshot.

## 7. Open questions for ChatGPT

1. Is the proposed separation between `synthetic_enterprise` track and the
   existing `human-review` track acceptable? Or should the synthetic
   approval_mode be added as an explicit field to the existing
   `approval_summary.json`?
2. Should the synthetic `machine_validated_count` count toward any
   Program-wide completion metric, or should it remain strictly
   informational?
3. Should the synthetic case set be required to ship a "reviewer can
   override" field that, if present, downgrades any machine-validated
   case to BLOCKED pending human review?
4. Should the canonical `release_decision.json` schema accept BLOCKED
   only when dependencies are unreachable, or should there be a distinct
   `INFRASTRUCTURE_MISSING` verdict?
5. Are there specific PHASE22 evidence docs that should be updated to
   reference the synthetic track, or should the synthetic track remain
   self-contained in `goal05-phase22-synthetic-benchmark/`?

## 8. Proposed deliverables (already in this PR)

- `docs/evidence/goal05-phase22-synthetic-benchmark/world_model.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/corpus/*.md` (62 docs)
- `docs/evidence/goal05-phase22-synthetic-benchmark/corpus_manifest.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/graph_manifest.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/derived/source_span_index.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/derived/corpus_hashes.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/synthetic_cases.jsonl`
- `docs/evidence/goal05-phase22-synthetic-benchmark/case_set_manifest.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/validation_report.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/runtime_ingestion.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/canonical_ir.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/profile_results/*.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/core_five_metrics.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/failure_buckets.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/release_decision.json`
- `docs/evidence/goal05-phase22-synthetic-benchmark/license_report.md`
- `docs/evidence/goal05-phase22-synthetic-benchmark/reproduction.md`
- `docs/evidence/goal05-phase22-synthetic-benchmark/build_world_model.py`
- `docs/evidence/goal05-phase22-synthetic-benchmark/build_cases.py`
- `docs/evidence/goal05-phase22-synthetic-benchmark/validate_cases.py`
- `docs/evidence/goal05-phase22-synthetic-benchmark/ingest_and_run.py`
- `docs/evidence/goal05-phase22-synthetic-benchmark/architecture-change-proposal.md`

## 9. Out of scope for this ACP

- Modifying the public/human-review closure contract.
- Modifying PHASE22 state in the Program manifest.
- Modifying `docs/status/production-readiness.md`.
- Archiving the Program.
- Closing the PHASE22 phase.

These are explicitly out of scope until ChatGPT has reviewed the
synthetic closure Contract AND the Program closure gates have been
amended.