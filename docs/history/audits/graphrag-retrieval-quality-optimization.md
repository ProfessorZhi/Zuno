# GraphRAG Retrieval Quality Optimization

This audit explains why current `local_graphrag` can enter graph routing but
still underperforms `baseline_rag` on HotpotQA `limit=5`.

## Scope

Evidence source:

- gitignored real runtime reports under `reports/evals/multihop/real_runtime/`
- current runtime code in:
  - `src/backend/zuno/services/retrieval/orchestrator.py`
  - `src/backend/zuno/services/retrieval/fusion.py`
  - `src/backend/zuno/services/graphrag/retriever.py`

Compared runs:

- `hotpotqa_baseline_rag_limit5_calibrated.json`
- `hotpotqa_local_graphrag_limit5_calibrated.json`

## Current Result Gap

Current verified metrics:

- `baseline_rag`
  - `Recall@5 = 1.00`
  - `MRR@10 = 0.90`
  - `fallback = 0`
- `local_graphrag`
  - `Recall@5 = 0.80`
  - `MRR@10 = 0.80`
  - `fallback = 1/5`

So the current problem is no longer route activation.
It is retrieval quality loss after graph results are added.

## Why Recall@5 Dropped From 1.00 To 0.80

Short answer:

- `local_graphrag` is not preserving baseline top candidates strongly enough
- graph-added candidates can outrank or displace baseline gold-like candidates
- this hurts at least two questions inside the first 5-sample HotpotQA smoke

The two clear regression cases are:

1. `5a8b57f25542995d1e6f1371`
   - question: `Were Scott Derrickson and Ed Wood of the same nationality?`
   - baseline top5 contains both gold docs:
     - `Scott Derrickson`
     - `Ed Wood`
   - local top5 keeps `Scott Derrickson` but loses `Ed Wood`
   - local top5 injects:
     - `Sinister (film)`
     - `Adam Collis`

2. `5a8c7595554299585d9e36b6`
   - question: `What government position was held by the woman who portrayed Corliss Archer in the film Kiss and Tell?`
   - baseline top5 contains both gold docs:
     - `Kiss and Tell (1945 film)`
     - `Shirley Temple`
   - local top5 keeps `Kiss and Tell (1945 film)` but loses `Shirley Temple`
   - local top5 injects:
     - `Charles Craft`

So the recall drop is caused by ranking displacement, not by total loss of the
gold documents from the broader candidate pool.

## Did Graph Documents Push Out Baseline Gold-like Documents?

Yes.

This is the core observed failure mode.

### Question `5a8b57f25542995d1e6f1371`

- baseline top5:
  - `Tyler Bates`
  - `Scott Derrickson`
  - `Ed Wood (film)`
  - `Ed Wood`
  - `Conrad Brooks`
- local top5:
  - `Sinister (film)`
  - `Scott Derrickson`
  - `Conrad Brooks`
  - `Adam Collis`
  - `Tyler Bates`

Gold displacement:

- lost from baseline top5: `Ed Wood`
- graph-side noise promoted:
  - `Sinister (film)`
  - `Adam Collis`

### Question `5a8c7595554299585d9e36b6`

- baseline top5:
  - `Kiss and Tell (1945 film)`
  - `A Kiss for Corliss`
  - `Meet Corliss Archer (TV series)`
  - `Janet Waldo`
  - `Shirley Temple`
- local top5:
  - `Kiss and Tell (1945 film)`
  - `A Kiss for Corliss`
  - `Janet Waldo`
  - `Charles Craft`
  - `Meet Corliss Archer (TV series)`

Gold displacement:

- lost from baseline top5: `Shirley Temple`
- graph-side noise promoted:
  - `Charles Craft`

## Does Current Fusion Preserve Baseline Top Candidates?

Not strongly enough.

Current runtime behavior:

1. vector candidates are retrieved
2. graph candidates are retrieved
3. both sources are merged in `RetrievalFusion.merge(...)`
4. merged docs are globally re-sorted by `_rank_key(...)`

Current weakness:

- there is no explicit rule saying baseline top candidates must survive into the
  fused top5 unless graph evidence is clearly stronger
- graph-aware boosts can lift graph-related siblings and relation-adjacent docs
  above baseline gold-like docs
- graph results therefore behave partly as destructive replacement, not only as
  non-destructive promotion

So the answer is:

- no, current fusion does not guarantee baseline preservation

## Does Current Rerank Preserve Baseline Top Candidates?

No hard guarantee exists in the current local GraphRAG path.

Evidence from current behavior:

- baseline top5 already contains both gold docs for two regression questions
- local GraphRAG still loses one gold doc in each of those two questions
- this means post-merge ordering is free to demote already-good baseline docs

Current rerank policy is enabled, but the merged ranking signal is already
allowing harmful graph promotions before the final top5 is observed.

## How Much Do Baseline And Graph-augmented Results Overlap?

At `top5`, the overlap is high but not safe:

- `5a8b57f25542995d1e6f1371`: overlap `3/5`
- `5a8c7595554299585d9e36b6`: overlap `4/5`
- `5a85ea095542994775f606a8`: overlap `4/5`
- `5adbf0a255429947ff17385a`: overlap `4/5`
- `5a8e3ea95542995a26add48d`: overlap `3/5`

Interpretation:

- local GraphRAG is not replacing the whole candidate set
- but even one or two bad swaps are enough to break `Recall@5`
- this is exactly why baseline-preserving fusion is needed

## Which Questions Does Graph Help?

Graph is clearly helping these current question shapes:

1. `5a8b57f25542995d1e6f1371`
   - graph route activates
   - non-empty graph docs and graph paths are produced
   - graph understands the comparison style, but ranking still over-promotes
     side documents

2. `5a8c7595554299585d9e36b6`
   - graph route activates
   - non-empty graph docs and graph paths are produced
   - graph helps enter the bridge relation space, but ranking still misses the
     best person node

3. `5adbf0a255429947ff17385a`
   - graph route activates
   - both gold docs remain in top5
   - current graph additions do not break the answer-supporting pair

4. `5a8e3ea95542995a26add48d`
   - graph route activates
   - both gold docs remain in top5
   - current graph additions are acceptable even though some noisy docs appear
     lower in top10

## Which Questions Does Graph Hurt?

Current graph-hurt cases:

1. `5a8b57f25542995d1e6f1371`
   - hurts `Recall@5`
   - loses gold doc `Ed Wood`

2. `5a8c7595554299585d9e36b6`
   - hurts `Recall@5`
   - loses gold doc `Shirley Temple`

Current route-activation miss that is not mainly a fusion regression:

3. `5a85ea095542994775f606a8`
   - falls back with `graph_result_empty`
   - still needs better seed / alias / path handling
   - this one is not the baseline-preserving fusion problem first

## Is Baseline-preserving Fusion Needed?

Yes.

Why:

1. baseline is already strong on this sample
2. graph is now additive evidence, not a replacement retrieval stack
3. current failures are caused by harmful promotions, not by the absence of
   graph activation
4. preserving baseline top candidates is the smallest aligned change that can
   improve local GraphRAG without hiding ranking problems

Required product/runtime principle:

- graph results should promote strong graph-supported candidates
- graph results should not destructively evict baseline top candidates unless
  graph confidence is clearly higher
- if graph retrieval is empty or noisy, local GraphRAG must not return a weaker
  top5 than baseline by default

## Next Step

The next implementation phase should add:

1. baseline-preserving candidate fusion
2. explicit candidate debug metadata:
   - `source`
   - `vector_rank`
   - `graph_rank`
   - `graph_support_count`
   - `graph_seed_hit_count`
   - `graph_path_count`
   - `fusion_score`

Only after that should seed expansion, alias normalization, and path-aware
ranking be tuned.
