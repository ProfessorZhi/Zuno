# HotpotQA Missed-opportunity Tuning

This audit closes `Phase M1` of `HotpotQA Missed-opportunity Tuning V1`.

The scope here is narrow on purpose:

- explain the 2 current `enhanced_hurts` cases
- explain why 6 `missed_opportunity_cases` stayed on `standard_rag`
- identify the smallest runtime contracts that must change in `M2` to `M4`

Evidence comes from:

- `reports/evals/multihop/real_runtime/hotpotqa_standard_retrieval_limit50.json`
- `reports/evals/multihop/real_runtime/hotpotqa_enhanced_retrieval_limit50.json`
- `src/backend/zuno/services/retrieval/orchestrator.py`
- `src/backend/zuno/services/retrieval/retrievers.py`
- `src/backend/zuno/services/retrieval/fusion.py`
- `src/backend/zuno/services/graphrag/retriever.py`

## Closure Summary

Current `limit=50` state is not a route-activation outage anymore.

The remaining gap is more specific:

1. one hurt case is true graph noise on a bridge relation question
2. one hurt case is a standard-floor invariance failure
3. six missed-opportunity cases never trigger graph or requery, because the
   current classifier and query rewrite policy are still too conservative for
   bridge / attribute lookup questions

So the next sequence stays correct:

1. `M2` standard floor invariance
2. `M3` bridge relation graph guardrail
3. `M4` requery activation for bridge / attribute questions

## Current Questions Under Audit

Current hurt cases:

1. `5a828c8355429966c78a6a50`
   - `Kaiser Ventures corporation was founded by an American industrialist who became known as the father of modern American shipbuilding?`
2. `5a7571135542992d0ec05f98`
   - `Ralph Hefferline was a psychology professor at a university that is located in what city?`

Current missed-opportunity cases:

1. `5ab6d09255429954757d337d`
2. `5a75e05c55429976ec32bc5f`
3. `5ae0d4c9554299603e418468`
4. `5adddccd5542997dc7907069`
5. `5a79311755429970f5fffe67`
6. `5abbf698554299114383a0b5`

Shared current pattern:

- all 8 cases use `query_variants`
- only 1 of the 8 routes to `local_graphrag`
- all 8 have `requery_used = false`
- 7 of the 8 cases never leave `standard_rag`

## Hurt Case 1: Bridge Graph Noise

Question:

- `5a828c8355429966c78a6a50`
- `Kaiser Ventures corporation was founded by an American industrialist who became known as the father of modern American shipbuilding?`

Observed ranking:

- standard top5:
  - `Henry J. Kaiser`
  - `Kaiser Ventures`
  - `Kaiser Shipyards`
  - `Edgar Kaiser Sr.`
  - `Edgar Kaiser Jr.`
- enhanced top5:
  - `Henry J. Kaiser`
  - `Cho Kyuhyun`
  - `Kaiser Ventures`
  - `Method Man`
  - `Kaiser Shipyards`

Metric damage:

- `Recall@2`: `1.0 -> 0.5`
- `FullChainHit@2`: `1.0 -> 0.0`
- `Recall@5` and `MRR@10` still survive

Route evidence:

- `internal_route = local_graphrag`
- `route_selection_reason = relation_question`
- `graph_used = true`
- `requery_used = false`
- `standard_floor_used = true`
- `confidence_gated_fusion_used = true`

Current processed query shape:

- `relation_question = true`
- `seed_entity_count = 8`
- extracted seeds are noisy:
  - full-question fragment
  - `Kaiser`
  - `Ventures`
  - `American`
  - `corporation`
  - `was`
  - `founded`
  - `industrialist`

Current graph evidence shape:

- top graph paths are obviously noisy and not bridge-chain-clean, for example:
  - `Heaven Upside Down -> American`
  - `Conrad Biedrzycki -> American`
  - `Super Junior-K -> Y`
- `fusion_metadata.comparison_question = false`
- no bridge-specific chain protection exists in fusion today

Root cause:

1. the query is bridge-like, but current fusion only has explicit comparison
   chain protection, not bridge chain protection
2. graph route activation is correct, but graph path quality is not gated by
   “does this document preserve the bridge evidence pair?”
3. graph-only noisy candidates can still enter top2/top3 if graph signal is
   high enough

Why the current guardrail missed it:

- `RetrievalFusion` protects comparison dual-seed coverage
- this question is not classified as a comparison question
- so the current guardrail never runs
- bridge noise therefore survives if graph score is large enough

M3 consequence:

- add bridge relation metadata and top2/top3 protection, not just comparison
  protection

## Hurt Case 2: Standard Floor Invariance Failure

Question:

- `5a7571135542992d0ec05f98`
- `Ralph Hefferline was a psychology professor at a university that is located in what city?`

Observed ranking:

- standard top5:
  - `Ralph Hefferline`
  - `Columbia University`
  - `Virginia Commonwealth University`
  - `University of the Incarnate Word`
  - `University of Kansas`
- enhanced top5:
  - `Ralph Hefferline`
  - `Virginia Commonwealth University`
  - `University of the Incarnate Word`
  - `University of Kansas`
  - `Amherst, Massachusetts`

Metric damage:

- `Recall@2`: `1.0 -> 0.5`
- `Recall@5`: `1.0 -> 0.5`
- `FullChainHit@3`: `1.0 -> 0.0`

Route evidence:

- `internal_route = standard_rag`
- `route_selection_reason = standard_question`
- `graph_used = false`
- `requery_used = false`
- `community_used = false`
- `drift_used = false`
- `standard_floor_used = true`

This is the important fact:

- enhanced hurt this question **without using any enhancement channel**

Current processed query shape:

- `relation_question = false`
- `graph_worthy = false`
- only one retriever run exists: `vector`

Root cause:

1. enhanced currently records `standard_floor_used = true`, but it does not
   guarantee `final documents == standard floor documents`
2. when graph / requery / community / drift are all inactive, there is no hard
   invariance contract in `RetrievalOrchestrator.run(...)`
3. so enhanced can still drift away from the baseline floor even when it has
   done nothing productively different

Important nuance:

- in eval runs, standard and enhanced use separate temporary knowledge ids
- so part of the observed drift may come from separate index instances
- but that does not weaken the runtime conclusion
- the product runtime still lacks an explicit “no enhancement, no ranking drift”
  contract

M2 consequence:

- if no enhancement channel materially contributes, enhanced must reuse the
  standard floor and record that decision in metadata

## Missed-opportunity Cases

### Shared Runtime Pattern

All 6 missed-opportunity cases currently show the same behavior:

- `internal_route = standard_rag`
- `graph_used = false`
- `requery_used = false`
- `community_used = false`
- `drift_used = false`
- only `vector` retriever runs

This means the current failure is not “graph failed after activation”.

It is:

- the router never escalated beyond standard retrieval
- rewrite variants existed, but no second retrieval round ever used them

### Case Group A: Bridge / Role / Administration Questions

Questions:

1. `5ab6d09255429954757d337d`
   - `The football manager who recruited David Beckham managed Manchester United during what timeframe?`
2. `5ae0d4c9554299603e418468`
   - `Roger O. Egeberg was Assistant Secretary for Health and Scientific Affairs during the administration of a president that served during what years?`
3. `5adddccd5542997dc7907069`
   - `Aside from the Apple Remote, what other device can control the program Apple Remote was originally designed to interact with?`

Current classifier failure:

- all 3 are bridge or role-hop questions
- current `QueryProcessor.process(...)` only sets `relation_question` from:
  - explicit relation words
  - `GraphRetriever._has_graph_relation_signal(...)`
- these phrasings do not match current bridge cues strongly enough

Why this matters:

- they need relation-aware routing or at least relation-aware requery
- today they are treated as plain fact lookups

### Case Group B: Attribute Lookup Through an Intermediate Entity

Questions:

1. `5a75e05c55429976ec32bc5f`
   - `Brown State Fishing Lake is in a country that has a population of how many inhabitants ?`
2. `5a79311755429970f5fffe67`
   - `A Japanese manga series based on a 16 year old high school student Ichitaka Seto, is written and illustrated by someone born in what year?`
3. `5abbf698554299114383a0b5`
   - `Which British first-generation jet-powered medium bomber was used in the South West Pacific theatre of World War II?`

Current classifier failure:

- these are attribute lookup questions that still require one bridge hop
- current relation detection is too dependent on explicit relation phrases like
  `founded by`, `directed by`, `based in what`
- these forms rely on paraphrases like:
  - `is in a country that has a population`
  - `written and illustrated by someone born in what year`
  - `was used in`

Why this matters:

- vector-only top5 often gets one gold doc plus near-miss distractors
- no requery is generated to isolate the missing bridge entity or target
  attribute

### Case Group C: Explicit Bridge Pattern That Still Missed

Question:

1. `5a7571135542992d0ec05f98`
   - `Ralph Hefferline was a psychology professor at a university that is located in what city?`

This one is both:

- a hurt case
- a missed routing opportunity

Why it matters:

- the phrase `located in what city` should be enough to trigger at least
  requery
- current `processed_query.query_features.relation_question = false`
- `graph_worthy = false`

So the current bridge / attribute phrase coverage is still too narrow.

## Why Requery Stayed 0/50

Root cause is structural, not incidental.

Current runtime behavior:

1. `RetrievalOrchestrator.run(...)` expands `candidate_queries`
2. but `_build_retry_plan(...)` only uses alternate queries when the first pass
   returns a quality failure such as:
   - `empty_result`
   - `too_few_documents`
   - `low_rerank_score`
3. the current missed-opportunity cases return acceptable-looking top5 results
4. so no second round is triggered

So `requery_used = 0/50` is expected under the current design.

This is the key architectural point:

- rewrite exists today as a fallback tool
- it does not exist yet as a proactive bridge / attribute retrieval strategy

M4 consequence:

- add positive requery triggers for bridge / attribute questions even when the
  first pass is not “bad enough” to trip fallback

## Is The Current Classifier Too Conservative?

Yes.

Current classifier succeeds on:

- explicit comparison questions
- some explicit bridge phrases such as `founded by`

Current classifier misses:

- `located in what city`
- `managed during what timeframe`
- `during the administration of a president that served during what years`
- `what other device can control the program ... designed to interact with`
- `written and illustrated by someone born in what year`
- `is in a country that has a population`

So the current relation detector is:

- strong on explicit comparison
- acceptable on a small bridge subset
- too weak on bridge paraphrase and attribute-hop phrasing

## Does Enhanced Have Standard-floor Drift Risk Today?

Yes.

Evidence:

- `5a7571135542992d0ec05f98` hurts without graph, requery, community, or drift
- metadata still reports `standard_floor_used = true`
- therefore “standard floor used” currently means:
  - vector baseline participated
- but does **not** mean:
  - final ranking is invariant to no-op enhancement

That semantic gap must be closed in `M2`.

## Which Query Patterns Should Trigger Escalation?

The following patterns are supported by current audit evidence and should drive
`M3` or `M4`:

1. bridge relation phrases:
   - `founded by`
   - `managed ... during what timeframe`
   - `during the administration of`
   - `what other device can control`
2. attribute-hop phrases:
   - `located in what city`
   - `is in a country that has a population`
   - `born in what year`
   - `served during what years`
3. paraphrased two-hop roles:
   - `who recruited X`
   - `professor at a university`
   - `written and illustrated by someone`

Recommended routing consequence:

- bridge questions:
  - enable graph and bridge guardrail
- attribute-hop questions:
  - enable requery first
  - allow graph only if confidence is sufficient

## Direct Requirements For M2 To M4

### M2: Standard Floor Invariance

Must guarantee:

- if `graph_used = false`
- and `requery_used = false`
- and `community_used = false`
- and `drift_used = false`
- then enhanced final documents must equal the standard floor documents

Must expose metadata:

- `standard_floor_reused`
- `enhanced_noop`
- `enhanced_noop_reason`
- `enhanced_fallback_to_floor`

### M3: Bridge Relation Guardrail

Must add bridge-specific chain protection analogous to the current comparison
guardrail.

Must block:

- graph-only noisy candidates that do not preserve bridge evidence pair quality

Must expose metadata:

- `bridge_relation_question`
- `bridge_seed_entities`
- `bridge_relation_cues`
- `bridge_chain_score`
- `bridge_promotion_blocked_reason`
- `noisy_bridge_graph_only`

### M4: Requery Activation

Must stop treating rewrite as fallback-only.

Need proactive requery for bridge / attribute questions such as:

- `located in what city`
- `based in what city`
- `born in what year`
- `served during what years`
- `managed during what timeframe`
- `is in a country that has a population`

Must expose metadata:

- `requery_triggered_reason`
- `requery_queries`
- `requery_result_count`
- `requery_used`
- `requery_fallback_to_floor`

## M1 Verdict

The current diagnosis is strong enough to move on.

Verified conclusions:

1. the classifier is still too conservative for bridge / attribute-hop queries
2. `requery_used = 0/50` is expected from current fallback-only rewrite design
3. enhanced currently has a true standard-floor invariance gap
4. graph hurt on `Kaiser Ventures` is bridge-noise that current comparison-only
   guardrail cannot stop
5. the next correct order remains:
   - `M2` floor invariance
   - `M3` bridge guardrail
   - `M4` proactive requery
