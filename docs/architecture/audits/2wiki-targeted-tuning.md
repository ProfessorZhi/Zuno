# 2Wiki Targeted Tuning V1

This audit opens `2Wiki Targeted Tuning V1`.

Scope:

- explain why `enhanced_retrieval` is not baseline-preserving on the current
  `2Wiki limit=10` smoke
- identify the genealogy-style bridge blocker
- classify the three current `missed_opportunity_cases`
- define the smallest safe next tuning direction

Evidence comes from:

- `reports/evals/multihop/real_runtime/twowiki_standard_retrieval_limit10_smoke.json`
- `reports/evals/multihop/real_runtime/twowiki_enhanced_retrieval_limit10_smoke.json`
- `src/backend/zuno/services/retrieval/fusion.py`
- `src/backend/zuno/services/graphrag/retriever.py`
- `src/backend/zuno/services/retrieval/orchestrator.py`

## Current Product Gap

Current `2Wiki limit=10` product comparison:

### standard_retrieval

- `Recall@5 = 0.85`
- `FullChainHit@5 = 0.70`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@5 = 0.80`
- `FullChainHit@5 = 0.60`
- `fallback_count = 0`
- `failure_count = 0`

Current summary:

- `enhanced_helps cases = 0`
- `enhanced_hurts cases = 1`
- `standard_gap_cases = 3`
- `missed_opportunity_cases = 3`

So the current failure is not broad instability.

It is a narrow but real cross-dataset generalization failure:

1. one genealogy-style bridge blocker where graph noise displaces standard
   evidence
2. three standard-gap questions where enhanced does not activate or does not
   recover the missing evidence side

## Primary Blocker

- `question_id = 2ec440560bb011ebab90acde48001122`
- question:
  `Who is the maternal grandfather of Antiochus X Eusebes?`

Gold docs:

- `Antiochus X Eusebes`
- `Cleopatra IV of Egypt`

### Standard top5

1. `Antiochus X Eusebes`
2. `Laodice of the Sameans`
3. `Albert III, Prince of Anhalt-Zerbst`
4. `Fujiwara no Nagara`
5. `Cleopatra IV of Egypt`

Standard result:

- `Recall@5 = 1.0`
- `FullChainHit@5 = 1.0`

This means the standard floor is already sufficient.

### Enhanced top6

1. `Antiochus X Eusebes`
2. `Laodice of the Sameans`
3. `North Marion High School (West Virginia)`
4. `Albert III, Prince of Anhalt-Zerbst`
5. `Fujiwara no Nagara`
6. `Cleopatra IV of Egypt`

Enhanced result:

- `Recall@5 = 0.5`
- `FullChainHit@5 = 0.0`

The direct harm is precise:

- `North Marion High School (West Virginia)` enters top5
- `Cleopatra IV of Egypt` is pushed to rank 6

### Route and Activation Facts

Standard:

- `internal_route = standard_rag`
- `route_selection_reason = relation_question`
- `graph_worthy = true`
- `graph_used = false`

Enhanced:

- `internal_route = local_graphrag`
- `route_selection_reason = relation_question`
- `graph_worthy = true`
- `graph_used = true`
- `requery_used = false`

So this blocker is not caused by requery.

It is a graph-route ranking / fusion precision problem.

### Seed Entity Facts

Enhanced `seed_entities_with_source`:

- query-derived:
  - `Who is the maternal grandfather of Antiochus X Eusebes`
  - `Antiochus`
  - `X`
  - `Eusebes`
- baseline-title derived:
  - `Antiochus X Eusebes`
  - `Laodice of the Sameans`
  - `Albert III, Prince of Anhalt-Zerbst`
  - `Fujiwara no Nagara`

This already hints at the problem:

- the current seed builder does not isolate the real bridge target
- it mixes target person, generic pronoun-like fragments, and unrelated
  baseline genealogy names

### Graph Path Facts

Current `used_paths` include shapes like:

- `Syria Antiochus X Eusebes -> She`
- `Syria Antiochus X Eusebes -> Seleucid`
- `North Marion High School -> U`
- `North Marion High School -> S`
- `Saxe- Wittemberg -> Prince`
- `Saxe- Wittemberg -> Anhalt- Zerbst`

These are not bridge-clean family paths.

They are noisy neighboring edges with weak entity semantics.

### Why Current Guardrails Miss This Case

Current `fusion_metadata` only shows:

- `bridge_relation_question = true`
- `bridge_seed_entities = ['antiochus x eusebes', 'laodice of the sameans']`
- `bridge_relation_cues = ['father of']`

This is the core misfit:

1. the query asks for `maternal grandfather`
2. current bridge metadata collapses that into a broad `father of` family
3. the guardrail protects generic bridge-seed coverage, not direct genealogy
   relation precision
4. graph-only candidates can still enter top5 if they carry enough general
   graph signal, even when their path semantics do not match the query

So the current bridge guardrail is too coarse for family-tree questions.

It distinguishes "bridge-like" from "not bridge-like", but not:

- direct relation path
- indirect family noise path
- same-family neighborhood noise
- wrong kinship direction

## Root Cause for the Blocker

The current blocker is caused by three interacting issues.

### 1. Genealogy relation cues are too coarse

Current bridge handling groups many questions into a single relation bucket:

- `father of`
- `mother of`
- `spouse of`
- other bridge phrases

But genealogy-style questions need finer meaning:

- father
- mother
- maternal grandfather
- paternal grandfather
- spouse
- child
- sibling

The current route/fusion stack does not preserve that precision.

### 2. Graph path ranking does not distinguish direct family bridge from family noise

`GraphRetriever._score_path(...)` currently boosts bridge questions when
`relation_type` is in broad sets like:

- `director`
- `founder`
- `author`
- `performer`
- `spouse`
- `mother`

But it does not encode:

- query relation label match
- kinship direction match
- direct-vs-indirect family hop precision
- family-noise penalty

So same-family neighbors and weak graph neighborhoods can still look strong.

### 3. Graph-only promotion threshold is still too permissive for genealogy

Current fusion logic has:

- comparison guardrail
- bridge guardrail
- requery precision gate

But no genealogy-specific guardrail.

That means a graph-only candidate can still survive if:

- graph signal is high enough
- bridge coverage appears non-empty
- no stricter family-path precision rule blocks it

## Missed Opportunity Cases

Current `missed_opportunity_cases` are:

1. `e2a3bf2a0bdd11eba7f7acde48001122`
2. `f9dcb4a60bda11eba7f7acde48001122`
3. `298f23b8088a11ebbd6eac1f6bf848b6`

These are not all the same problem.

### Case A

- `question_id = e2a3bf2a0bdd11eba7f7acde48001122`
- question:
  `When did John V, Prince Of Anhalt-Zerbst's father die?`

Current facts:

- standard `Recall@5 = 0.5`
- enhanced `Recall@5 = 0.5`
- standard and enhanced both stay on the same top5
- enhanced route:
  - `internal_route = standard_rag`
  - `route_selection_reason = standard_question`
  - `graph_worthy = false`
  - `graph_used = false`
  - `requery_used = false`

Diagnosis:

- this is route under-activation
- the query is clearly genealogy / family bridge
- current classifier does not treat `father die` as a strong enough relation
  cue

### Case B

- `question_id = f9dcb4a60bda11eba7f7acde48001122`
- question:
  `Where was the director of film Ronnie Rocket born?`

Current facts:

- standard `Recall@5 = 0.5`
- enhanced `Recall@5 = 0.5`
- enhanced route:
  - `internal_route = local_graphrag`
  - `graph_used = true`
  - `requery_used = true`

Enhanced top8 adds:

- `Viktor Yeliseyev`
- `Bernhard VII, Prince of Anhalt-Zerbst`
- `Jason Moore (director)`

Used paths include:

- `Yale University Press -> Director`
- `Viscount -> Director`
- `Indian Intelligence Bureau -> Director`
- `Polish-Russian War -> Xawery`
- `North Marion High School -> U`

Diagnosis:

- this is not under-activation
- graph and requery both activate
- but they do not recover the missing bridge evidence
- instead they broaden into generic `director` neighbors

So this is low precision after activation, not no activation.

### Case C

- `question_id = 298f23b8088a11ebbd6eac1f6bf848b6`
- question:
  `Which film has the director who was born later, El Extraño Viaje or Love In Pawn?`

Current facts:

- standard `Recall@5 = 0.5`
- enhanced `Recall@5 = 0.5`
- enhanced route:
  - `internal_route = standard_rag`
  - `route_selection_reason = standard_question`
  - `graph_worthy = false`
  - `graph_used = false`
  - `requery_used = false`

Diagnosis:

- this is comparison-style under-activation
- the wording `who was born later` is a multi-entity comparison over directors
- current comparison / bridge detection misses this phrasing

So this is another route under-activation case.

## What 2Wiki Is Asking That HotpotQA Did Not

HotpotQA relation questions that currently work better are mostly:

- bridge / role-hop
- attribute-hop
- creator / author / founder / location questions

The 2Wiki failures add a harder family-tree and comparative layer:

1. genealogy direction matters
2. weak nearby family entities are abundant
3. entity neighborhoods can be very dense and very noisy
4. wording often combines kinship with comparison or time attributes

So 2Wiki relation questions are not just "more bridge questions".

They are a harder subtype:

- genealogy bridge
- relation direction precision
- comparison over bridge targets

## Answers Required by W1

### 1. How are 2Wiki relation questions different from HotpotQA relation questions?

They rely more on:

- family-tree structure
- kinship direction
- same-cluster genealogical noise
- comparison phrasing over bridge-derived attributes

HotpotQA mostly tested whether the system could enter the bridge space.

2Wiki now tests whether it can stay precise inside a dense family graph.

### 2. Does current GraphRAG over-trust shallow family paths?

Yes.

The blocker case shows that shallow or weak family-neighborhood paths can
produce enough graph signal to displace standard evidence.

### 3. Does current path ranking distinguish direct bridge evidence from family noise?

No, not enough.

Current path scoring has broad bridge bonuses, but no dedicated precision layer
for:

- direct relation label match
- kinship direction
- indirect family noise

### 4. Are graph-only top5 conditions too wide?

Yes, for genealogy questions.

Current bridge guardrail is good enough for earlier HotpotQA bridge noise, but
still too permissive for family-noise neighbors on 2Wiki.

### 5. Is a genealogy-specific guardrail needed?

Yes.

Need a dedicated guardrail that blocks graph-only promotion unless the path is a
high-precision family bridge match.

### 6. Is a stronger path precision score needed?

Yes.

Need explicit path metadata for:

- relation labels seen on promoted paths
- direct relation path
- indirect family noise path
- genealogy path precision score

### 7. Do the missed opportunities need graph, requery, or baseline tuning?

Mixed answer:

- `e2a3...`: mostly graph activation / genealogy activation
- `f9dc...`: graph + requery precision after activation
- `298f...`: comparison / bridge activation expansion

So this is not only baseline tuning.

## W2-W3 Recommendation

The smallest safe next move is:

1. add a genealogy bridge guardrail
   - protect standard top5 on family-tree questions
   - block graph-only noise unless relation precision is high
2. then expand 2Wiki activation carefully
   - add genealogy / comparison bridge cues
   - only when standard floor is incomplete
   - still behind confidence gates

Do not start with broader activation first.

If activation is broadened before genealogy precision is added, the likely
outcome is:

- more graph usage
- more noisy family neighbors
- more hurt cases
- possible HotpotQA regression

## W1 Verdict

Current evidence is strong enough to proceed to implementation.

Verified conclusions:

1. the main 2Wiki blocker is a genealogy-style graph-noise displacement, not a
   requery false positive
2. current bridge guardrail is too coarse for kinship direction questions
3. path ranking needs genealogy-specific precision features
4. two missed opportunities are route under-activation
5. one missed opportunity is activation without precision
6. the correct next order is:
   - genealogy guardrail first
   - activation review second
   - then rerun `2Wiki limit=10`

## W2-W3 Implementation Closure

`W2` and `W3` are now implemented in:

- `src/backend/zuno/services/retrieval/fusion.py`
- `src/backend/zuno/services/graphrag/retriever.py`
- `src/backend/zuno/services/retrieval/orchestrator.py`
- `tests/test_graphrag_genealogy_guardrail.py`
- `tests/test_2wiki_missed_opportunity_activation.py`

Current runtime additions:

- genealogy / family relation activation now recognizes:
  - `maternal grandfather`
  - `paternal grandfather`
  - `father die`
  - `mother die`
  - `who was born later`
- enhanced route metadata now records:
  - `enhanced_activation_reason`
  - `graph_activation_reason`
  - `requery_activation_reason`
  - `missed_opportunity_trigger_reason`
  - `candidate_blocked_reason`
  - `floor_preserved_reason`

This means the original 2Wiki under-activation cases are no longer silent:

- `e2a3...` now enters `local_graphrag` through genealogy activation
- `298f...` now enters `local_graphrag` through comparison activation
- `f9dc...` still activates graph + requery, but now exposes blocked low-confidence requery metadata

## W4: 2Wiki Limit=10 Targeted Rerun

Verified reports:

- `twowiki_standard_retrieval_limit10_targeted_v2.json`
- `twowiki_enhanced_retrieval_limit10_targeted_v2.json`

### standard_retrieval

- `Recall@2 = 0.70`
- `Recall@5 = 0.85`
- `Recall@10 = 0.85`
- `Precision@5 = 0.36`
- `Precision@10 = 0.18`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.85`
- `ChainRecall@10 = 0.85`
- `FullChainHit@5 = 0.70`
- `FullChainHit@10 = 0.70`
- `avg/p50/p95 latency = 14866.14 / 14033.90 / 18782.37 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@2 = 0.70`
- `Recall@5 = 0.80`
- `Recall@10 = 0.90`
- `Precision@5 = 0.34`
- `Precision@10 = 0.19`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.80`
- `ChainRecall@10 = 0.90`
- `FullChainHit@5 = 0.60`
- `FullChainHit@10 = 0.80`
- `avg/p50/p95 latency = 16494.69 / 12822.09 / 27024.74 ms`
- `fallback_count = 0`
- `failure_count = 0`

### Route Diagnostics

- `internal_route distribution = {local_graphrag: 9, standard_rag: 1}`
- `route_selection_reason distribution = {relation_question: 9, standard_question: 1}`
- `graph_used = 9/10`
- `requery_used = 4/10`
- `community_used = 0/10`
- `drift_used = 0/10`
- `standard_floor_used = 10/10`
- `genealogy_promotion_blocked count = 6`

### Rerun Delta Summary

- `enhanced_helps cases = 0`
- `enhanced_hurts cases = 1`
  - `2ec440560bb011ebab90acde48001122`
- `standard_gap_cases = 3`
- `missed_opportunity_cases = 3`

Current missed-opportunity set is still:

1. `e2a3bf2a0bdd11eba7f7acde48001122`
2. `f9dcb4a60bda11eba7f7acde48001122`
3. `298f23b8088a11ebbd6eac1f6bf848b6`

But the shape changed:

- all three now activate as intended
- none stays on the old under-activation path
- the remaining problem is recovery precision, not activation silence

### Updated Blocker Interpretation

The blocker `2ec440...` still fails, but with better diagnostics:

- `graph_activation_reason = genealogy_bridge_pattern`
- `enhanced_activation_reason = genealogy_bridge_pattern`
- `candidate_blocked_reason = low_precision_genealogy`
- `floor_preserved_reason = standard_floor_chain_protection`
- `genealogy_relation_cues = [maternal grandfather, grandfather, father of]`

So the new result is not "genealogy never activated".

It is:

- genealogy activation now works
- genealogy blocking now records low-precision candidates
- but the current guardrail still does not fully stop noisy family neighbors from surviving above the missing bridge evidence

That is why:

- `Recall@10` improves from `0.85 -> 0.90`
- `FullChainHit@10` improves from `0.70 -> 0.80`
- but `Recall@5` and `FullChainHit@5` are still below standard

## W4 Verdict

Current rerun does **not** pass the required 2Wiki gate.

Required gate:

1. `enhanced Recall@5 >= standard Recall@5`
2. `enhanced FullChainHit@5 >= standard FullChainHit@5`
3. `failure_count = 0`
4. `fallback_rate <= 30%`
5. `p95 latency <= standard p95 * 2.5`
6. `enhanced_hurts cases <= 1`

Result:

1. failed
2. failed
3. passed
4. passed
5. passed
6. passed

Current interpretation:

- activation got better
- top10 recovery got slightly better
- early-rank preservation is still not solved
- this is still not baseline-preserving on 2Wiki `limit=10`

So `2Wiki limit=20` is still blocked.

## W5: HotpotQA Regression Check

Verified reports:

- `hotpotqa_standard_retrieval_limit50_2wiki_regression_v2.json`
- `hotpotqa_enhanced_retrieval_limit50_2wiki_regression_v2.json`

### standard_retrieval

- `Recall@2 = 0.86`
- `Recall@5 = 0.98`
- `Recall@10 = 0.98`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.98`
- `FullChainHit@5 = 0.96`
- derived `FullChainHit@3 = 0.88`
- `avg/p50/p95 latency = 12418.59 / 11968.05 / 15253.67 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@2 = 0.85`
- `Recall@5 = 0.98`
- `Recall@10 = 0.99`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.98`
- `FullChainHit@5 = 0.96`
- derived `FullChainHit@3 = 0.88`
- `avg/p50/p95 latency = 16108.13 / 13625.91 / 28336.51 ms`
- `fallback_count = 0`
- `failure_count = 0`

### Regression Verdict

This is not a hard regression, but it is also no longer a clean enhanced win.

What still holds:

- `enhanced Recall@5 >= standard Recall@5`
- `enhanced FullChainHit@3 >= standard FullChainHit@3`
- `fallback_count = 0`
- `failure_count = 0`
- `p95 latency ratio = 1.86x < 2.2`

What no longer holds:

- `enhanced Recall@2 > standard Recall@2`
- `enhanced_helps_count > enhanced_hurts_count`

Current HotpotQA hurt count on this rerun is `1`, and the main surface is now a
baseline-preserving tie rather than a clear enhanced lead.

So the current 2Wiki activation change is keepable for local analysis, but it
does not justify broader 2Wiki expansion or a stronger product claim.

## W7: Genealogy Path Precision Ranking

Verified reports:

- `twowiki_standard_retrieval_limit10_targeted_v4.json`
- `twowiki_enhanced_retrieval_limit10_targeted_v4.json`

### What changed

- genealogy paths now emit typed metadata:
  - `normalized_relation_types`
  - `path_length`
  - `seed_entity_coverage`
  - `bridge_entity_coverage`
  - `text_unit_support_count`
  - `relation_cue_match`
  - `genealogy_path_template_match`
- enhanced genealogy ranking now starts from the `standard_retrieval` top5
  floor, then lets graph-only candidates enter only as challengers
- low-confidence graph-only genealogy candidates now record explicit blocked
  reasons such as:
  - `graph_only_without_text_support`
  - `relation_label_mismatch`
  - `indirect_family_noise_path`
  - `high_degree_entity_noise`

### standard_retrieval

- `Recall@5 = 0.85`
- `Recall@10 = 0.85`
- `FullChainHit@5 = 0.70`
- `FullChainHit@10 = 0.70`
- `MRR@10 = 1.00`
- `avg/p50/p95 latency = 12257.86 / 12260.31 / 16796.76 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@5 = 0.85`
- `Recall@10 = 0.90`
- `FullChainHit@5 = 0.70`
- `FullChainHit@10 = 0.80`
- `MRR@10 = 1.00`
- `avg/p50/p95 latency = 16459.45 / 15381.96 / 24912.50 ms`
- `fallback_count = 0`
- `failure_count = 0`

### W7 Verdict

This rerun clears the 2Wiki gate:

1. `enhanced Recall@5 >= standard Recall@5`: passed
2. `enhanced FullChainHit@5 >= standard FullChainHit@5`: passed
3. `failure_count = 0`: passed
4. `fallback_rate <= 30%`: passed
5. `p95 latency <= standard p95 * 2.5`: passed
6. `enhanced_hurts cases <= 1`: passed with `0`

Most importantly, the earlier blocker is no longer a hurt case:

- `2ec440560bb011ebab90acde48001122`
- `Who is the maternal grandfather of Antiochus X Eusebes?`

The enhanced route now keeps the standard floor intact unless a typed
genealogy challenger has enough evidence to justify promotion.

## W8: 2Wiki Limit=20 Cautious Expansion

Verified reports:

- `twowiki_standard_retrieval_limit20_cautious_v1.json`
- `twowiki_enhanced_retrieval_limit20_cautious_v1.json`

### standard_retrieval

- `Recall@2 = 0.65`
- `Recall@5 = 0.7625`
- `Recall@10 = 0.7625`
- `Precision@5 = 0.38`
- `Precision@10 = 0.19`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.7625`
- `ChainRecall@10 = 0.7625`
- `FullChainHit@5 = 0.45`
- `FullChainHit@10 = 0.45`
- `avg/p50/p95 latency = 12480.22 / 12132.71 / 15620.04 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@2 = 0.65`
- `Recall@5 = 0.725`
- `Recall@10 = 0.775`
- `Precision@5 = 0.36`
- `Precision@10 = 0.19`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.725`
- `ChainRecall@10 = 0.775`
- `FullChainHit@5 = 0.40`
- `FullChainHit@10 = 0.50`
- `avg/p50/p95 latency = 13180.70 / 11269.22 / 19574.10 ms`
- `fallback_count = 0`
- `failure_count = 0`

### Diagnostics Summary

- `internal_route distribution = {local_graphrag: 13, standard_rag: 7}`
- `route_selection_reason distribution = {relation_question: 13, standard_question: 7}`
- `graph_used = 13/20`
- `requery_used = 6/20`
- `community_used = 0/20`
- `drift_used = 0/20`
- `standard_floor_used = 20/20`
- `graph_challenger_pool_size avg = 1.95`
- `graph_promotion_allowed count = 2`
- `graph_promotion_blocked_reason distribution = {low_precision_genealogy: 2}`
- `final_top5_floor_preserved count = 2`
- `enhanced_helps cases = 0`
- `enhanced_hurts cases = 2`
- `missed_opportunity_cases = 0`
- `standard_gap_cases = 7`

### Hurt Cases

1. `2ec440560bb011ebab90acde48001122`
   - `Who is the maternal grandfather of Antiochus X Eusebes?`
   - `graph_used = true`
   - `graph_challenger_pool_size = 12`
   - `graph_promotion_allowed = true`
   - `final_top5_floor_preserved = false`
   - current issue: genealogy challenger gate is still too permissive on the larger slice

2. `5bec3cd408a711ebbd7fac1f6bf848b6`
   - `Which film has the director who died earlier, Il Seduttore or The Trial Of Joan Of Arc?`
   - `graph_used = false`
   - `internal_route = standard_rag`
   - current issue: this one is not a graph-promotion failure; it is a standard floor completeness gap on a comparison-style question

### W8 Verdict

W7 does not yet generalize to 2Wiki `limit=20`.

Why it fails the gate:

1. `enhanced Recall@5 >= standard Recall@5`: failed
2. `enhanced FullChainHit@5 >= standard FullChainHit@5`: failed
3. `enhanced_hurts cases <= 2`: passed
4. `fallback_count = 0`: passed
5. `failure_count = 0`: passed
6. `p95 latency <= standard p95 * 2.5`: passed

Interpretation:

- W7 remains valid on the targeted `limit=10` slice
- but its baseline-preserving genealogy challenger gate is not yet stable enough
  to claim `limit=20` generalization
- `limit=50` expansion should stay blocked for now
- the next step should be targeted tuning against the two new hurt surfaces,
  not blind sample expansion
