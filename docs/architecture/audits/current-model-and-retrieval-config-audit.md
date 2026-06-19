# Current Model And Retrieval Config Audit

Program: GraphRAG Eval Preparation Program

Phase: A - Current Model & Retrieval Config Audit

Scope: audit only. No runtime, frontend, or test files were moved or rewritten in
this phase.

Baseline commit before this audit: `1a1e385 Wire knowledge product workflows`.

## Evidence Sources

Audited files:

- `src/backend/zuno/schema/knowledge.py`
- `src/backend/zuno/api/services/knowledge.py`
- `src/backend/zuno/services/retrieval/planner.py`
- `src/backend/zuno/services/retrieval/orchestrator.py`
- `src/backend/zuno/services/retrieval/models.py`
- `src/backend/zuno/services/retrieval/retrievers.py`
- `src/backend/zuno/services/retrieval/fusion.py`
- `src/backend/zuno/services/graphrag/**`
- `src/backend/zuno/services/rag/**`
- `apps/web/src/apis/knowledge.ts`
- `apps/web/src/apis/domain-packs.ts`
- `apps/web/src/utils/knowledge-config.ts`
- `apps/web/src/pages/knowledge/knowledge-create.vue`
- `apps/web/src/pages/knowledge/knowledge-settings.vue`
- `tools/evals/zuno/rag_eval/**`
- `tests/test_phase5_deep_graphrag_eval_surface.py`

## Short Verdict

Zuno has a real but still compact configuration surface for model binding,
standard RAG, Local GraphRAG, and Deep GraphRAG routing. The stable backend config
surface is `KnowledgeConfig`. The eval surface has profile-level overrides for
RAG and GraphRAG comparison, but it is not yet a multi-hop dataset runner.

Before HotpotQA / 2WikiMultiHopQA / MuSiQue, the minimum missing surface is not a
runtime rewrite. It is a stable eval-facing profile layer for multi-hop budgets:
BM25/vector split, query rewrite count, seed entity count, community top-k, DRIFT
follow-up limits, and trace expectations.

## Current Model Configuration

| Parameter | Current status | Backend support | Frontend support | Eval support | Recommended action |
|---|---|---|---|---|---|
| `text_embedding_model_id` | implemented | `KnowledgeModelRefs`, runtime resolution via `KnowledgeService.resolve_model_config_by_id` | create wizard and maintenance page expose it | local embedding eval can pass/list embedding ids | Keep. Required before multi-hop eval. |
| `vl_embedding_model_id` | implemented | `KnowledgeModelRefs`; image impact/reindex support exists | maintenance page exposes it; create wizard stores it in config but does not show a separate VL selector | not used by current RAG eval profiles | Keep backend. Not needed for text-only multi-hop V1. |
| `rerank_model_id` | implemented | `KnowledgeModelRefs`; immediate-effect impact | create wizard and maintenance page expose it | local eval supports rerank config and dev rerank server | Keep. Important for baseline parity. |
| extraction LLM | missing | `entity_extraction_mode` exists, but no model id binding for extraction LLM | not exposed | not exposed | Add later as explicit model ref or domain-pack/runtime binding if multi-hop extraction quality requires it. |
| community report LLM | missing | `community_report_prompt_id` exists, but no model id binding for report generation | not exposed except status/actions | not exposed | For Phase C/D sample smoke, do not block. For real global eval, add explicit report model binding. |
| answer LLM | backend_only | current eval uses configured conversation model path in `run_eval.py`; not in `KnowledgeConfig` | not exposed per knowledge | eval supports LLM answer/judge modes through runtime settings | Keep out of Phase A. Consider eval CLI option first, not product setting. |
| rewrite model | missing | query rewrite calls `zuno.services.rewrite.query_write.query_rewriter`; no model id config in `KnowledgeConfig` | not exposed | `needs_query_rewrite` is profile option, model is not | Add as eval/profile setting before serious multi-hop if rewrite quality matters. |
| `eval_profile_id` | backend_only | `KnowledgeConfig.eval_profile_id`; `KnowledgeService.list_eval_profiles` skeleton | not exposed in current create/maintenance pages | profile sets exist in eval harness but not wired to knowledge config | Keep audit item. Add minimal eval profile selection later only if useful for Product UI. |

## Standard Retrieval Configuration

| Parameter | Current status | Backend support | Frontend support | Eval support | Recommended action |
|---|---|---|---|---|---|
| `top_k` | implemented | `KnowledgeRetrievalSettings`; `RetrievalRequest`; orchestrator/fusion use it | API type only; not exposed in current product UI | profile override in `PROFILE_SETTINGS` | Keep. Critical for multi-hop Recall@K. |
| `score_threshold` | implemented | `KnowledgeRetrievalSettings`; vector retrieval and quality checks use it | API type only; not exposed | profile override; stackless compare threshold override exists | Keep. Useful but should default to `None` for recall-first multi-hop smoke. |
| `rerank_enabled` | implemented | `KnowledgeRetrievalSettings`; planner handles rerank availability | API type only; maintenance exposes model binding, not toggle | profile override | Keep. Add eval profile presets rather than product UI toggle first. |
| `rerank_top_k` | implemented | `KnowledgeRetrievalSettings`; planner/rerank policy use it | API type only; not exposed | profile override | Keep. Important for compare profiles. |
| `vector_backend` | implemented | `KnowledgeIndexSettings` supports `milvus`, `chroma`, `milvus_lite` | API/util options exist; not exposed in current create/maintenance pages | stackless path uses local Chroma internally, not through product config | Keep. Do not force product exposure before multi-hop downloader. |
| `chunk_size` | implemented | `KnowledgeIndexSettings`; config impact marks text/BM25/graph rebuild | util options exist; not exposed in current product pages | stackless compare supports `--chunk-size-override` | Critical. Keep as eval override before UI exposure. |
| `overlap` | implemented | `KnowledgeIndexSettings`; config impact marks rebuild | util options exist; not exposed in current product pages | stackless compare supports `--overlap-override` | Critical. Keep as eval override. |
| `separator` | implemented | `KnowledgeIndexSettings`; config impact marks rebuild | API type/util only | not a first-class eval CLI option | Keep backend. Not urgent for multi-hop V1. |
| BM25 enabled | backend_only | planner can enable BM25 only if `enable_keyword_recall=True`; BM25 adapter checks Elasticsearch setting | status displayed as BM25, no toggle | stackless/profile docs mention BM25, but profile does not expose stable `bm25_enabled` | Add minimal eval profile flag before full multi-hop compare. |
| `bm25_top_k` | missing | BM25 adapter slices by generic `top_k` | not exposed | not exposed | Add eval-level split later: `bm25_top_k` vs `vector_top_k`. |
| `fusion_strategy` | backend_only | `RetrievalFusion` exists; planner hardcodes `query_aware` | not exposed | not exposed | Keep hardcoded for Phase C/D. Document metric limitation. |
| `vector_top_k` | missing | vector uses generic `top_k` | not exposed | not exposed | Add eval-level split later if baseline recall needs tuning. |
| query rewrite enabled | backend_only | `needs_query_rewrite` exists in `RetrievalRequest`; orchestrator uses query expander | not exposed | profile override exists | Keep. Important for multi-hop, but expose in eval profile first. |
| `max_query_variants` | missing | query expander returns variants but no stable max setting | not exposed | not exposed | Add before full multi-hop if rewrite is enabled. |

## Enhanced Retrieval Configuration

| Parameter | Current status | Backend support | Frontend support | Eval support | Recommended action |
|---|---|---|---|---|---|
| `default_mode = rag_graph_deep` | implemented | schema/service normalize it; planner routes it | product UI maps enhanced mode to it without exposing literal value | eval public `deep_graphrag` exists but currently uses `rag_graph`, not `rag_graph_deep` | Align eval profiles before Phase D. |
| `graph_hop_limit` | implemented | `KnowledgeRetrievalSettings`; graph retriever receives it | API type only; not exposed | profile override | Keep. Critical for multi-hop. |
| `max_paths_per_entity` | implemented | `KnowledgeRetrievalSettings`; graph retriever receives it | API type only; not exposed | profile override | Keep. Critical for multi-hop. |
| `max_seed_entities` | missing | graph retriever may extract seeds internally, but no config field was found | not exposed | not exposed | Add eval/runtime option before serious multi-hop graph tuning. |
| `community_top_k` | backend_only | community search uses generic `top_k` fallback to `3` | not exposed | not exposed | Add eval option as `community_top_k` before full global eval. |
| `community_version` | implemented | `KnowledgeGraphIndexSettings.community_version`; orchestrator reads index health version | status not directly editable | not used by current eval profiles | Keep. Useful for stale/ready selection. |
| `community_report_prompt_id` | implemented | `KnowledgeGraphIndexSettings`; impact marks community report | not exposed as editable field | not used | Keep backend. Not required for sample smoke. |
| `global_community_top_k` | missing | no separate field; generic `top_k` is reused | not exposed | not exposed | Add later as eval option if global route is measured. |
| `drift_followup_limit` | missing | DRIFT-like route hard-limits follow-ups to `1` in orchestrator | not exposed | not exposed | Add before evaluating DRIFT beyond smoke. |
| `drift_max_rounds` | backend_only | orchestrator has `max_rounds` for fallback, not DRIFT tree depth | not exposed | not exposed | Do not treat as implemented DRIFT depth. Add only when expanding DRIFT. |
| `drift_local_top_k` | missing | follow-up local graph uses generic retrieval options | not exposed | not exposed | Add later for multi-hop evidence-depth tuning. |
| fallback policy | backend_only | `fallback_policy` in `RetrievalRequest` and planner/orchestrator | not exposed | partially available through direct retrieval options, not public profile docs | Keep. Expose in eval runner config before full eval. |
| `trace_enabled` | backend_only | `RetrievalRequest.trace_enabled`; planner metadata includes trace policy | not exposed | LangSmith trace flags exist in eval scripts; metadata is captured locally | Keep. Important for debugging multi-hop failures. |
| route metadata | implemented | orchestrator returns requested/resolved mode, internal route, retriever usage, communities, paths, follow-ups | not shown in current product pages | current eval surface can inspect retrieval outputs, but no multi-hop runner yet | Keep. Important for auditability. |

## Frontend Exposure Summary

Already configurable in current Product UI:

- product mode: standard retrieval / enhanced retrieval
- text embedding model id
- VL embedding model id on maintenance page
- rerank model id
- domain pack binding
- index status visibility
- reindex actions

Backend/API type exists but current Product UI does not expose:

- `top_k`
- `score_threshold`
- `rerank_enabled`
- `rerank_top_k`
- `chunk_size`
- `overlap`
- `separator`
- `vector_backend`
- `graph_hop_limit`
- `max_paths_per_entity`
- `community_report_prompt_id`
- `eval_profile_id`

This is intentional for Product Wiring V1: ordinary users only see product-level
mode choices. For eval work, expose these through eval profiles and runner
options first, not through the main UI.

## Backend-Only And Documented-Only Gaps

Backend-only:

- fallback policy
- trace policy
- route metadata
- community version/status
- profile-level retrieval options in eval harness
- fusion policy name, currently hardcoded as `query_aware`

Documented or desired but missing as stable config:

- extraction model id
- community report model id
- rewrite model id
- BM25/vector separate top-k
- `max_query_variants`
- `max_seed_entities`
- `global_community_top_k`
- `drift_followup_limit`
- `drift_local_top_k`

## Most Important Parameters For Multi-hop Eval

For HotpotQA / 2WikiMultiHopQA / MuSiQue, the most important parameters are:

1. `top_k`, plus future `vector_top_k` and `bm25_top_k`
2. `graph_hop_limit`
3. `max_paths_per_entity`
4. future `max_seed_entities`
5. query rewrite enabled / future `max_query_variants`
6. `rerank_enabled`, `rerank_top_k`, and `score_threshold`
7. future `community_top_k` / `global_community_top_k`
8. future `drift_followup_limit` and `drift_local_top_k`
9. trace and route metadata

## Recommendation Before Dataset Downloaders

Do not modify GraphRAG runtime before Phase C.

Minimum safe preparation:

1. Keep Phase C focused on dataset downloader, adapter, normalized schema, and
   small committed samples.
2. Keep Phase D focused on stackless/mocked runner smoke.
3. Add missing multi-hop parameters first as eval runner/profile options, not as
   ordinary Product UI fields.
4. Only promote a parameter into `KnowledgeConfig` after it proves useful in
   sample eval evidence.

## Phase A Closure Notes

No business code changes are required for Phase A. The current code supports a
minimal multi-hop eval start, but not a full tuning surface.

Next phase should audit `tests/` structure before moving or adding large eval
test groups.

