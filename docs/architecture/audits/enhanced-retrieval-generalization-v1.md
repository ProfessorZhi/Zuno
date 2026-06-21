# Enhanced Retrieval Generalization V1

This audit closes `Phase G1` of `Enhanced Retrieval Generalization V1`.

The scope is intentionally narrow:

- explain the remaining HotpotQA false-positive requery hurt case
- identify why current proactive requery is still too permissive
- define the smallest `G2` precision gate that can clean this up without
  collapsing the new HotpotQA gains

Evidence comes from:

- `reports/evals/multihop/real_runtime/hotpotqa_standard_retrieval_limit50_post_tuning.json`
- `reports/evals/multihop/real_runtime/hotpotqa_enhanced_retrieval_limit50_post_tuning_v3.json`
- `src/backend/zuno/services/retrieval/orchestrator.py`
- `src/backend/zuno/services/retrieval/fusion.py`

## Closure Summary

HotpotQA `limit=50` post-tuning already crossed the main product gate:

- `enhanced Recall@5 > standard Recall@5`
- `enhanced FullChainHit@3 > standard FullChainHit@3`
- `missed_opportunity_cases = 0`

But one hurt case remains:

- `5a79311755429970f5fffe67`

This is not graph noise.

It is a precision failure in proactive requery:

1. the query matches the current broad pattern `born in what year`
2. proactive requery is triggered even though standard top5 already has full
   chain coverage
3. requery results enter fusion without a dedicated confidence gate
4. requery candidates are treated too much like normal baseline vector
   candidates
5. a weak but related manga document is allowed into top5 and displaces the
   gold author document

So `G2` should not remove proactive requery entirely.

It should add a precision gate that answers:

- did requery actually recover missing evidence?
- or did it just add same-domain but low-value neighbors?

## Target Hurt Case

- `question_id = 5a79311755429970f5fffe67`
- question:
  `A Japanese manga series based on a 16 year old high school student Ichitaka Seto, is written and illustrated by someone born in what year?`

Gold docs:

- `I&quot;s`
- `Masakazu Katsura`

## Standard vs Enhanced Outcome

### Standard top5

1. `I&quot;s`
2. `Haven't You Heard? I'm Sakamoto`
3. `Clear Skies!`
4. `Silver Spoon (manga)`
5. `Masakazu Katsura`

Standard metrics:

- `Recall@5 = 1.0`
- `FullChainHit@5 = 1.0`

This matters because standard floor is already good enough here.

The gold pair is present by `top5`.

### Enhanced top6

1. `I&quot;s`
2. `Haven't You Heard? I'm Sakamoto`
3. `Clear Skies!`
4. `Silver Spoon (manga)`
5. `My Bride is a Mermaid`
6. `Masakazu Katsura`

Enhanced metrics:

- `Recall@5 = 0.5`
- `Recall@10 = 1.0`
- `FullChainHit@5 = 0.0`
- `FullChainHit@10 = 1.0`

So the damage is precise:

- requery did not destroy the broader candidate pool
- it damaged early ranking quality by pushing `Masakazu Katsura` from rank 5 to
  rank 6

## Trigger Evidence

Current route metadata:

- `internal_route = standard_rag`
- `route_selection_reason = standard_question`
- `graph_used = false`
- `requery_used = true`
- `requery_triggered_reason = bridge_attribute_pattern`
- `requery_queries = [`
  `What year was the author and illustrator of a Japanese manga series about 16-year-old high school student Ichitaka Seto born?`
  `]`
- `requery_result_count = 5`
- `requery_fallback_to_floor = false`
- `enhanced_fallback_to_floor = false`
- `standard_floor_reused = false`

Important consequence:

- this question is still on `standard_rag`
- the only enhancement channel that changed the ranking is requery

## Why This Query Triggered Requery

The current proactive requery pattern list in
`src/backend/zuno/services/retrieval/orchestrator.py` includes:

- `born in what year`

That rule is currently too broad.

It captures at least two very different situations:

1. useful attribute-hop questions where the target person/entity is still
   missing from the standard floor
2. already-good standard-floor questions where the query only contains an
   attribute phrase but the main evidence pair is already present

This hurt case belongs to the second category.

## Which Requery Candidate Caused The Damage

The directly visible displaced ranking change is:

- standard rank 5: `Masakazu Katsura`
- enhanced rank 5: `My Bride is a Mermaid`
- `Masakazu Katsura` moves to rank 6

So the current harmful candidate is:

- `My Bride is a Mermaid`

Why it is suspicious:

1. it is not one of the gold docs
2. it does not itself close the missing author-evidence gap
3. it is consistent with a same-domain / same-author / same-manga-neighborhood
   retrieval leak
4. it behaves like a related work, not like the missing core evidence node

This is exactly the kind of candidate that should be allowed only as a lower
rank supplement, not as a top5 replacement.

## Root Cause

### 1. The standard floor was already sufficient

The first key fact is simple:

- standard top5 already had both `I&quot;s` and `Masakazu Katsura`

So there was no missing evidence side that required rescue.

That means proactive requery should have faced a much higher promotion bar.

### 2. Requery trigger is pattern-only today

Current proactive requery is activated from query text pattern matching alone.

For this case:

- `born in what year` matched
- requery fired

What is missing is a second question:

- does the current standard floor still have an actual evidence gap?

Right now the answer is not checked before allowing requery participation.

### 3. Requery candidates enter fusion too close to baseline candidates

This is the most important implementation detail.

In `orchestrator.py`:

- requery documents are created with `source_type = "vector"`
- only `metadata["matched_by"] = ["requery"]` is changed

In `fusion.py`:

- `source_name == "requery"` still assigns `vector_rank`
- `_is_baseline_candidate(...)` returns true because `source_type == "vector"`

So the system currently treats requery docs as:

- special in metadata
- but still strong baseline-like candidates in ranking

That is why low-value requery results can enter the top ranks too easily.

### 4. There is no requery confidence gate

Current runtime exposes:

- `requery_triggered_reason`
- `requery_queries`
- `requery_result_count`

But it does not expose:

- `requery_confidence_score`
- `requery_promotion_allowed`
- `requery_promotion_blocked_reason`
- `requery_help_reason`
- `requery_noise_reason`

Without these, the system has no principled place to say:

- this requery result is related
- but not useful enough to outrank current standard evidence

### 5. Full-chain preservation is only implemented for other channels

Current architecture already has strong protection ideas in two places:

1. standard floor invariance
   - when no enhancement channel really contributes
2. comparison / bridge graph guardrails
   - when graph-only candidates would damage chain evidence

What is missing is the equivalent rule for requery:

- when standard floor already has full-chain coverage,
- low-confidence requery must not change top3/top5

## What This Case Says About Query Type

Question type:

- attribute question
- but not high-value bridge rescue

More precisely:

- it asks for an author birth year
- but the standard floor already recovered both the target manga and the target
  author

So the right rule is not:

- never trigger requery on `born in what year`

The right rule is:

- trigger is allowed
- promotion is conditional

## Should This Query Still Trigger Requery?

Yes, but only weakly.

Recommended interpretation:

- `born in what year` remains a valid candidate trigger
- but by itself it should not grant top-rank promotion power

This means:

1. allow requery execution
2. inspect whether requery retrieves the missing evidence side
3. if not, keep requery behind the standard floor

## What Conditions Should Allow Requery Promotion

Requery should only promote into top3/top5 when at least one of these is true:

1. it directly introduces a missing gold-like evidence side
2. it covers the original query's core seed entity and the missing bridge/role
   side
3. it matches the same entity or same relation as a weak standard candidate and
   clearly strengthens that evidence chain
4. it improves a standard floor that is not yet full-chain

For this hurt case, current evidence suggests none of those conditions were
met.

## What Should Count As Low-confidence Requery

Low-confidence requery should include at least these shapes:

1. same-domain but not same-evidence candidate
   - example shape: another manga / another work / another neighbor node
2. candidate does not recover the missing evidence side
3. candidate does not align to the original query's strongest seed entity pair
4. candidate only broadens topical similarity
5. standard floor is already full-chain

This hurt case satisfies several of those conditions at once.

## Which Query Patterns Should Be Downgraded

The audit does not support globally disabling:

- `born in what year`

It supports downgrading it unless extra evidence exists.

Recommended downgrade rule:

- pure attribute phrase triggers such as `born in what year` should require
  stronger missing-evidence justification than explicit bridge patterns like:
  - `but where does`
  - `located in what city`
  - `founded by`
  - `administration of`

In other words:

- explicit bridge rescue patterns may keep a lower activation threshold
- generic attribute patterns need a stronger promotion threshold

## G2 Implementation Requirement

The next fix should be a requery precision gate, not another trigger rewrite.

The minimum gate must enforce:

1. if standard floor already has full-chain:
   - low-confidence requery cannot alter top3/top5
2. if requery does not add missing evidence:
   - it can stay as supplementary context only
3. if requery adds only weakly related neighbors:
   - mark it as noise and block promotion
4. if requery truly recovers missing evidence:
   - allow promotion and record why

Required metadata:

- `requery_confidence_score`
- `requery_promotion_allowed`
- `requery_promotion_blocked_reason`
- `requery_fallback_to_floor`
- `requery_help_reason`
- `requery_noise_reason`

## G1 Verdict

The current diagnosis is strong enough to proceed to `G2`.

Verified conclusions:

1. the remaining HotpotQA hurt case is a requery precision problem, not a graph
   problem
2. the current trigger `born in what year` is too broad to imply promotion by
   itself
3. requery documents are currently ranked too much like baseline vector docs
4. the current runtime lacks a dedicated requery confidence / promotion gate
5. the next correct move is:
   - add requery precision gate
   - rerun HotpotQA `limit=50`
   - only then enter `2Wiki small smoke`

## G2 Implementation Closure

`G2` is now implemented in:

- `src/backend/zuno/services/retrieval/fusion.py`
- `src/backend/zuno/services/retrieval/orchestrator.py`
- `tests/test_enhanced_requery_precision_gate.py`

The final precision gate does two things:

1. treat `requery`-only candidates as a separate fusion class instead of normal
   baseline vector docs
2. block promotion when requery support comes only from generic same-domain
   tokens such as `Japanese` or `manga`

This closes the exact leak observed in `5a79311755429970f5fffe67`:

- generic nationality/topic tokens no longer count as enough seed support
- low-confidence requery stays supplementary instead of entering early ranks

Runtime metadata now exposes:

- `requery_confidence_score`
- `requery_promotion_allowed`
- `requery_promotion_blocked_reason`
- `requery_help_reason`
- `requery_noise_reason`
- `requery_confidence_summary`

## HotpotQA Limit=50 Post-cleanup Rerun

Verified reports:

- `hotpotqa_standard_retrieval_limit50_post_cleanup.json`
- `hotpotqa_enhanced_retrieval_limit50_post_cleanup_v2.json`

### standard_retrieval

- `Recall@2 = 0.85`
- `Recall@5 = 0.97`
- `Recall@10 = 0.97`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.97`
- `FullChainHit@5 = 0.94`
- `avg/p50/p95 latency = 13291.03 / 12854.74 / 17251.26 ms`
- `fallback_count = 0`
- `failure_count = 0`

### enhanced_retrieval

- `Recall@2 = 0.85`
- `Recall@5 = 0.98`
- `Recall@10 = 0.99`
- `MRR@10 = 1.00`
- `ChainRecall@5 = 0.98`
- `FullChainHit@5 = 0.96`
- `avg/p50/p95 latency = 13823.47 / 12821.26 / 21651.31 ms`
- `fallback_count = 0`
- `failure_count = 0`

### Route Diagnostics

- `internal_route distribution = {standard_rag: 42, local_graphrag: 8}`
- `route_selection_reason distribution = {standard_question: 42, relation_question: 8}`
- `graph_used = 8/50`
- `requery_used = 9/50`
- `community_used = 0/50`
- `drift_used = 0/50`
- `p95 latency ratio vs standard = 1.26x`

### Per-question Delta Summary

- `enhanced_helps cases = 1`
  - `5ae4a3265542995ad6573de5`
- `enhanced_hurts cases = 0`
- `enhanced_ties cases = 49`

The previous hurt case is now closed:

- `5a79311755429970f5fffe67`
- `requery_confidence_summary = {count: 0, promoted_count: 0}`
- top5 again keeps both `I&quot;s` and `Masakazu Katsura`

## 2Wiki Small Smoke

Verified reports:

- `twowiki_standard_retrieval_limit10_smoke.json`
- `twowiki_enhanced_retrieval_limit10_smoke.json`

Current smoke result is intentionally small and should be treated only as a
cross-dataset guardrail check.

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

### Smoke Verdict

`2Wiki` is not ready for expansion yet.

Observed blocker:

- `question_id = 2ec440560bb011ebab90acde48001122`
- question: `Who is the maternal grandfather of Antiochus X Eusebes?`
- standard top5 keeps both:
  - `Antiochus X Eusebes`
  - `Cleopatra IV of Egypt`
- enhanced `local_graphrag` promotes noisy genealogy neighbors into top5 and
  pushes `Cleopatra IV of Egypt` to rank 6

This is not a requery problem.

It is a remaining graph-ranking / path-selection precision gap for genealogical
bridge questions on `2Wiki`.

## Final Verdict

This program is now closed at the intended scope:

1. HotpotQA false-positive requery hurt case is fixed
2. HotpotQA `limit=50` post-cleanup still beats standard on the main retrieval
   surface
3. cautious `2Wiki` smoke is now verified
4. `2Wiki` currently fails the same baseline-preserving standard and should not
   expand to larger samples until graph ranking is tightened for genealogy-style
   bridge questions
