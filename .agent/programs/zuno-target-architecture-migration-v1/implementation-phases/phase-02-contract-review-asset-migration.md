# Phase 02: Contract Review Asset Migration

## Goal

Preserve useful Contract Review assets while removing Domain Pack as the active
runtime container.

## Dependency

Phase 01 complete or a narrower asset-only gate approved by the user.

## Scope

- Classify `domain-packs/contract_review` assets as Current, Target, History,
  Eval Fixture, Generated, or Dead.
- Move reusable prompt/schema/eval assets to GraphRAG Project or eval fixture
  destinations.
- Archive superseded Domain Pack documentation under `docs/architecture/history/`.

## Files To Change

- `domain-packs/`
- `tools/evals/zuno/`
- `docs/architecture/history/`
- `.agent/references/`
- tests covering asset resolution

## Files Not To Change

- Runtime behavior before replacement tests exist.
- Database schema.
- Docker topology unless Phase 01 already removed active references.

## Acceptance Gates

- Contract Review evidence is not lost.
- Runtime no longer needs `DomainPackLoader` for Contract Review.
- History paths preserve old Domain Pack evidence.
- Eval fixtures use target names where possible.

## 2026-06-25 Progress

Status: partial. The target GraphRAG Project asset copy now exists at:

- `examples/graphrag-projects/contract_review/`

Asset migration table:

| Source | Target | Classification |
| --- | --- | --- |
| `domain-packs/contract_review/pack.yaml` | `examples/graphrag-projects/contract_review/settings.yaml` | Target asset metadata with `source_domain_pack` provenance |
| `domain-packs/contract_review/schema.json` | `examples/graphrag-projects/contract_review/schema.json` | Target schema asset |
| `domain-packs/contract_review/retrieval_policy.yaml` | `examples/graphrag-projects/contract_review/retrieval_policy.yaml` | Target query policy asset |
| `domain-packs/contract_review/extraction_prompt.md` | `examples/graphrag-projects/contract_review/prompts/extract_graph.md` | Target indexing prompt |
| `domain-packs/contract_review/answer_template.md` | `examples/graphrag-projects/contract_review/prompts/local_query.md` | Target local query prompt/template |
| `domain-packs/contract_review/report_template.md` | `examples/graphrag-projects/contract_review/prompts/report_template.md` | Target report prompt/template |
| `domain-packs/contract_review/eval_dataset.jsonl` | `examples/graphrag-projects/contract_review/eval/eval_dataset.jsonl` | Target eval fixture copy |

Additional progress:

- `GraphRAGProjectLoader` now materializes
  `examples/graphrag-projects/contract_review/retrieval_policy.yaml`,
  `schema.json`, and `eval/eval_dataset.jsonl` into loaded project settings.
- Contract Review graph policy tests use the GraphRAG Project policy as
  explicit `query_policy`; `GraphRetriever` no longer loads policy through
  `DomainPackLoader`.
- Stackless local eval can build the Contract Review local graph from
  GraphRAG Project assets and no longer loads `DomainPackLoader` for the
  `contract_review` project path.

Still blocked:

- Runtime/eval still needs `DomainPackLoader` through Contract Review eval and
  direct `DomainQAGraph` paths. Stackless local eval also keeps a generic
  legacy fallback for unmigrated packs. `KnowledgeService.get_runtime_settings`,
  `GraphRetriever`, and the Contract Review stackless local eval path no
  longer load `DomainPackLoader`, but that does not close Phase 02.
- `domain-packs/contract_review/` remains Blocked Legacy until those runtime
  and eval dependencies are cut over.

## Verification Commands

```powershell
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/test_repo_hygiene.py tests/test_repo_structure_consistency.py
git grep -n "contract_review"
git diff --check
```

## Evidence To Return

- asset migration table
- archived paths
- runtime dependency proof
