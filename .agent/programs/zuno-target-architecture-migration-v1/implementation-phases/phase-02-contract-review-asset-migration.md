# Phase 02: Contract Review Asset Migration

## Status

Complete. Contract Review assets are preserved in the GraphRAG Project target
copy and the old Domain Pack asset surfaces remain archived as history.

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

Status: root asset migration complete; broader 11C closure is still blocked by
migration compatibility tests. The target GraphRAG Project asset copy now exists at:

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
- The dedicated Contract Review eval now loads its compatibility payload and
  eval dataset from `examples/graphrag-projects/contract_review/` and no longer
  loads `DomainPackLoader` or executes through `DomainQAGraph`; its extraction
  path now calls `StructuredGraphExtractor` with
  `project_payload=project_payload`.
- Stackless local eval no longer has a generic Domain Pack loader fallback;
  when an id is provided, it must resolve to GraphRAG Project assets. Its local
  graph builder also calls extractors with `project_payload=project_payload`
  and no longer keeps a private `_load_graph_project_domain_payload` alias.
- GraphRAG Project assets now expose `to_project_payload()` as the project-named
  compatibility payload API. The legacy `to_domain_pack_payload()` wrapper has
  been retired from the active project loader.
- Stackless compare/local embedding evals prefer `graphrag_project_id` /
  `--graphrag-project-id` for Contract Review project binding while retaining
  `domain_pack_id` as a legacy alias where current runtime contracts still
  require it.

Closure evidence:

- `KnowledgeService.get_runtime_settings`, `GraphRetriever`, stackless local
  eval, and the dedicated Contract Review eval no longer load
  `DomainPackLoader`; the dedicated Contract Review eval also no longer
  executes through `DomainQAGraph`, and the direct `DomainQAGraph` source is
  retired.
- Contract Review graph extraction uses `project_payload` as the active
  payload name. The old extractor `domain_pack` payload alias is retired from
  active extractor APIs.
- `domain-packs/contract_review/` is archived under
  `docs/architecture/history/domain-packs/root-contract-review/`.
- Docker no longer copies or mounts `/app/domain-packs`.
- The `src/backend/zuno/services/domain_pack/` runtime service package is
  retired from current backend source.
- The former `tests/compat/` holding area is retired; remaining migration
  compatibility tests live under root `tests/`.

## 2026-06-26 Verification

Phase 01 active runtime cleanup is closed for the current code path, so Phase
02 no longer depends on a narrower asset-only exception. Fresh verification on
2026-06-26 confirmed:

- `examples/graphrag-projects/contract_review/` contains the target settings,
  schema, retrieval policy, prompts, and eval fixture.
- `docs/architecture/history/domain-packs/root-contract-review/` preserves the
  old root Domain Pack evidence.
- `docs/architecture/history/domain-packs/backend-package-contract-review/`
  preserves the former backend package asset copy.
- Contract Review eval and stackless local eval load GraphRAG Project payloads
  and call extractors with `project_payload=project_payload`.
- Docker documentation points Contract Review example assets to
  `examples/graphrag-projects/contract_review/`; active Docker config no
  longer mounts `/app/domain-packs`.

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
