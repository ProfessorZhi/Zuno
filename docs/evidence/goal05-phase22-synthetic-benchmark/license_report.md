# Synthetic Benchmark License & Provenance Report

Schema version: 1.0.0
Track id: `syn_cases_v1`
World model id: `wm_auroralis_v1`
Generation seed: `phase22-synthetic-2026-08-03-auroralis-v1`

## Origin

All content in this benchmark — entities, relations, documents, cases, expected
answers, security scopes, and validator logic — is generated deterministically
from a single fictional world model. No external dataset, scrape, model
finetune, or proprietary corpus is referenced or required.

## Fictional disclaimer

Every entity in the world model is fictional:

- The company "Auroralis Manufacturing Group N.V." does not exist.
- All employees, divisions, products, suppliers, contracts, policies, projects,
  events, permissions, and timelines are entirely invented.
- The synthetic content is designed to look enterprise-shaped on purpose so
  retrieval and reasoning can be exercised without using any real facts.

## License of generated artifacts

- The synthetic artifacts (`world_model.json`, `corpus/*.md`,
  `corpus_manifest.json`, `graph_manifest.json`,
  `derived/source_span_index.json`, `derived/corpus_hashes.json`,
  `synthetic_cases.jsonl`, `case_set_manifest.json`, `validation_report.json`)
  are released under the same MIT license as the surrounding Zuno repository
  (`LICENSE`).
- The generation scripts (`build_world_model.py`, `build_cases.py`,
  `validate_cases.py`, `ingest_and_run.py`) are released under the same MIT
  license.
- The synthetic content does not embed any copyrighted text, lyrics, book
  excerpts, code from external repositories, or proprietary contracts. Every
  sentence is original to this generator.
- No real persons, email addresses, phone numbers, customer names, or web
  facts appear in the content.

## Determinism guarantee

Re-running `build_world_model.py` and `build_cases.py` with the
`--out-root` pointing at the same directory produces byte-identical
artifacts. SHA-256 hashes for every artifact are recorded in
`derived/corpus_hashes.json` and `case_set_manifest.json`.

## Tracking separation from the human-review track

The synthetic track explicitly does NOT touch:

- `docs/evidence/goal05-phase22-public-benchmark-review-pack/`
- `docs/evidence/goal05-phase22-blocked-benchmark/`

The human-review track keeps `reviewer_approved_count=0`,
`benchmark_eligible_count=0`, `overall_status=REVIEW_REQUIRED`,
`measurement_state=blocked_pending_human_review`. Synthetic approvals are
tracked only under this directory's `case_set_manifest.json` field
`machine_validated_count` and the approval mode `machine_attested`.

## Why machine attestation only

Synthetic content cannot be reviewed by a human reviewer in any way that
adds empirical evidence about real-world retrieval, reasoning, or
production readiness. The `approval_mode: machine_attested` field on the
manifest signals that all gating for this track is performed by the
deterministic validator (`validate_cases.py`) and by the canonical profile
runners — not by a human reviewer approval. This is the explicit, machine-
only attestation contract for this track and is consistent with the
constraint that "machine validation ≠ human reviewer approval".