# Phase 3 Domain Pack Formalization Design

## Goal

Make `domain-packs/contract_review` a formal domain plugin contract instead of a runtime special case.

## Scope

- Formalize `pack.yaml`, `schema.json`, `retrieval_policy.yaml`, templates, and eval dataset validation.
- Replace ad hoc YAML parsing with real YAML loading.
- Ensure runtime can resolve a validated pack from `domain_pack_id`.
- Remove contract-review-shaped defaults from mainline answer/report rendering.
- Add Phase 3 tests for positive and negative contract behavior.

## Non-Goals

- Community GraphRAG
- DRIFT-like search
- Knowledge Config V2
- Large legacy cleanup

## Contract Decisions

### Manifest

`pack.yaml` remains the entrypoint and must declare:

- `id`
- `name`
- `version`
- `description`
- `schema`
- `extraction_prompt`
- `retrieval_policy`
- optional `answer_template`
- optional `report_template`
- optional `eval_dataset`

Declared paths must stay inside the pack root.

### Schema

`schema.json` stays lightweight in Phase 3 but becomes validated:

- top-level object
- `entities`: non-empty string list
- `relations`: non-empty string list

### Retrieval Policy

`retrieval_policy.yaml` becomes typed YAML and supports:

- `graph_hop_limit`
- `max_paths_per_entity`
- `citation_strictness`
- `risk_relation_preference`
- `graph_seed_terms`
- `graph_relation_cues`
- `graph_step_cues`

Phase 3 validates required keys, types, and positive numeric ranges.

### Templates

`answer_template.md` and `report_template.md` become boundary templates, not simple prefixes.

Supported placeholders:

- answer:
  - `{{conclusion}}`
  - `{{evidence}}`
  - `{{risks}}`
  - `{{citations}}`
- report:
  - `{{summary}}`
  - `{{risks}}`
  - `{{evidence}}`
  - `{{recommendations}}`

Mainline runtime renders placeholders when present. If a runtime-only dict injects plain text without placeholders, compatibility fallback remains prefix-style.

### Eval Dataset

`eval_dataset.jsonl` must be valid UTF-8 JSONL with at least:

- `id`
- `query`
- `reference_answer`
- `gold_evidence`
- `required_citations`

## Runtime Decisions

- `DomainPackLoader` is the single validated load path.
- `KnowledgeService.get_runtime_settings()` loads the pack for database-backed and local-runtime paths when `domain_pack_id` is present.
- `DomainQAGraph.resolve_domain_pack` loads the pack if only `domain_pack_id` is present in state/runtime.
- `GraphRetriever` always merges loaded pack policy before request overrides.
- `citation_strictness` participates in evidence verdict logic.
- `risk_relation_preference` participates in graph path prioritization when relation metadata exists.

## Verification

- Add `tests/test_phase3_domain_pack_formalization.py`
- Keep Phase 2 / Phase 2.5 / Phase 5 runtime tests green
