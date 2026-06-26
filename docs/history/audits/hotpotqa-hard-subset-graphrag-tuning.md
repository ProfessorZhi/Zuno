# HotpotQA Hard-subset GraphRAG Tuning

This audit explains why `enhanced_retrieval` regressed on a hard comparison
question in HotpotQA `limit=20`, and what was changed to close that gap.

The target is not to blame one branch in the abstract. The goal is to identify
which runtime rule allowed a noisy graph candidate to displace chain evidence
that standard retrieval already had.

## Scope

Target hurt case:

- `question_id = 5a8b57f25542995d1e6f1371`
- question: `Were Scott Derrickson and Ed Wood of the same nationality?`

Pre-fix outcome:

- standard derived `FullChainHit@3 = 1.0`
- enhanced derived `FullChainHit@3 = 0.0`

Post-fix outcome after the June 20, 2026 rerun:

- standard derived `FullChainHit@3 = 0.90`
- enhanced derived `FullChainHit@3 = 0.90`
- the former hurt case now has matching top3 chain coverage in both modes

## Closure Summary

The implemented fix stayed in the fusion layer instead of turning GraphRAG off.

What changed:

1. comparison queries now derive clean comparison seed entities in fusion
2. each candidate gets `candidate_seed_coverage`
3. graph-only promotion is blocked when it would break dual-seed top3 coverage
4. dual-seed / chain-complete candidates receive `chain_completeness_score`
5. fusion metadata now records:
`comparison_question` and `comparison_seed_entities`

Closure evidence:

- enhanced rerun top4 for `5a8b57f25542995d1e6f1371` is now:
  1. `Scott Derrickson`
  2. `Ed Wood (film)`
  3. `Ed Wood`
  4. `Sinister (film)`
- `Sinister (film)` no longer displaces the second gold entity beyond top3
- current `limit=20` product comparison shows:
no help cases, no hurt cases, and enhanced parity with standard on derived
`FullChainHit@3`

## Evidence Snapshot

### Standard top candidates

Standard top4:

1. `Scott Derrickson`
2. `Ed Wood (film)`
3. `Ed Wood`
4. `Conrad Brooks`

Gold entities:

- `Scott Derrickson`
- `Ed Wood`

Why standard succeeds:

- rank 1 already covers one seed entity
- rank 3 restores the second seed entity
- by top3, both gold entities are present

### Enhanced top candidates

Enhanced top4:

1. `Scott Derrickson`
2. `Sinister (film)`
3. `Ed Wood (film)`
4. `Ed Wood`

Why enhanced fails:

- `Sinister (film)` is promoted to rank 2
- that pushes `Ed Wood` from rank 3 to rank 4
- top3 no longer contains both gold entities

## Graph Retrieval Signals

The enhanced run used graph routing:

- `requested_mode = rag_graph_deep`
- `resolved_mode = rag_graph_deep`
- `internal_route = local_graphrag`
- `route_selection_reason = relation_question`
- `graph_route_used = true`

Current seed extraction for this case is noisy:

- `Were Scott Derrickson and Ed Wood of the same nationality`
- `Were`
- `Scott`
- `Derrickson`
- `Ed`
- `Wood`
- `same`
- `nationality`

Baseline-title seed enrichment adds:

- `Scott Derrickson`
- `Ed Wood (film`

So the seed set is not comparison-entity-clean. It contains:

- whole-question strings
- stopword-like fragments
- single-token fragments
- a film title fragment that is close to, but not equal to, the target entity

## Graph Candidate That Caused the Regression

Direct single-question replay shows the main promoted graph candidate:

- `file_name = Sinister (film)`
- `source_type = graph`
- `graph_rank = 1`
- `fusion_score = 144.0`
- `graph_seed_hit_count = 4`
- `graph_support_count = 12`
- `graph_file_focus = 16`

By comparison:

- `Ed Wood (film)` at final rank 3 had `fusion_score = 106.22`
- `Ed Wood` at final rank 4 had `fusion_score = 105.19`

So the current fusion logic strongly prefers `Sinister (film)` even though it
does not help restore missing two-entity chain coverage for the comparison
question.

## Path Evidence Shape

Current top graph paths are noisy anchor-style paths such as:

- `Scott Derrickson -> Sinister`
- `Scott Derrickson -> Derrickson`
- `Scott Derrickson -> C`

This matters because the current graph path layer is willing to boost
same-actor/same-file neighbors around `Scott Derrickson` without checking
whether the promoted document helps cover the second comparison entity.

## Root-cause Analysis

### 1. Is it a seed problem?

Partly yes.

The current seed set for comparison questions is too noisy and too fragmented.
It includes:

- full-question text
- single-token fragments
- a baseline-title fragment pointing at `Ed Wood (film)` instead of only the
  target comparison entity `Ed Wood`

This widens graph neighborhoods around one side of the comparison and makes
film-adjacent nodes easier to promote.

### 2. Is it a path ranking problem?

Yes, partly.

`_score_path(...)` gives comparison bonuses for locality-like relation signals,
but it does not require that the chosen path materially helps cover both
comparison entities. Anchor-style paths around `Scott Derrickson` are still able
to rank highly.

### 3. Is graph confidence too high?

Yes.

`Sinister (film)` received:

- very high `graph_support_count`
- very high `graph_file_focus`
- top `graph_rank`

Those values were enough to create a `fusion_score = 144.0`, well above the
baseline entity documents. The current system therefore treats this candidate as
high-confidence even though its chain-evidence value is weak.

### 4. Is fusion failing to protect comparison dual-entity evidence?

Yes. This is the central bug.

Current fusion is baseline-preserving in a broad sense, but it is not
comparison-chain-aware. Once a graph-only document accumulates enough graph
signal, it can outrank the baseline document that carries the second comparison
entity.

What is missing is a guardrail like:

- if standard top3 already covers both comparison seeds,
- a low/medium confidence graph-only document may not displace the second-seed
  evidence document unless it improves chain completeness.

### 5. Is final rerank missing?

Yes, in the exact place that matters here.

There is rerank inside the vector retrieval path, but there is no explicit final
cross-source rerank after graph/vector fusion that is aware of chain
completeness. So once fusion promotes `Sinister (film)`, nothing downstream
re-corrects the comparison evidence ordering.

### 6. Is graph document noise being promoted?

Yes.

`Sinister (film)` is a graph-only document that is relevant to `Scott
Derrickson`, but not to the second comparison entity coverage that top3 needs.
Its promotion is therefore noise relative to the comparison-chain objective.

## Why Current Fusion Allows the Replacement

The current fusion score is dominated by:

- candidate group
- baseline rank
- graph tier
- graph signal
- local priority score

What it does **not** score directly:

- how many comparison seed entities the candidate covers
- whether the candidate restores a missing seed
- whether the candidate preserves or breaks top3 chain completeness
- whether a graph-only document is just a strong same-file neighbor around one
  entity

So the current system answers the wrong question:

- it promotes “strong graph signal around one entity”
- instead of “does this help the two-entity comparison evidence chain?”

## Root Cause Summary

The regression is not one single bug. It is a stack:

1. noisy comparison seeds
2. path ranking that tolerates anchor-style neighbors
3. graph confidence dominated by support/file-focus counts
4. fusion that is not chain-aware for dual-entity comparison questions
5. no explicit final post-fusion rerank to restore chain completeness

The most important fix is not to disable graph routing. The correct fix is:

- comparison evidence coverage guardrail
- chain-aware fusion scoring

## Recommended Fix Direction

Priority order:

1. add comparison seed coverage metadata to candidate documents
2. protect standard dual-entity top3/top5 evidence from weak graph promotion
3. add chain-aware fusion scoring
4. only then reconsider whether seed cleanup or path bonuses need tightening

That sequence attacks the real failure mode without turning GraphRAG off.
