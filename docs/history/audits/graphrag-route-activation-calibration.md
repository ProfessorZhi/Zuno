# GraphRAG Route Activation Calibration

This audit fixes the scope for GraphRAG route calibration before changing
runtime heuristics.

## Why This Audit Exists

The current blocker is not "no graph data". The blocker is that the first
HotpotQA smoke sample does not cross the current graph-worthiness and planner
gates.

Already verified facts from the previous debug pass:

1. `baseline_rag` runs on real runtime for HotpotQA `limit=5`.
2. `local_graphrag` still falls back `5/5` with
   `fallback_reason = graph_result_empty`.
3. `deep_graphrag` keeps `requested_mode = rag_graph_deep` but
   `internal_route = standard_rag`.
4. The eval corpus can build local graph artifacts:
   - `entity_count = 246`
   - `relation_count = 196`
   - `chunk_backlink_count = 196`
5. All 5 current HotpotQA smoke questions are still:
   - `graph_worthy = false`
   - `path_count = 0`

So this phase is about calibration, not score inflation.

## Current Runtime Gates

Current planner feature extraction in
`src/backend/zuno/services/retrieval/retrievers.py` only marks:

- `relation_question = true` for explicit "关系 / relation / relationship /
  graph" wording
- `global_question = true` for explicit "整体 / overall / global / trend /
  theme" wording
- `evidence_required = true` for explicit "依据 / evidence / citation /
  supporting" wording

Current graph-worthiness in
`src/backend/zuno/services/graphrag/retriever.py` mainly accepts:

- strong explicit relation cues
- some Chinese step or relation cues from domain-pack policy
- otherwise `len(seed_entities) >= 2` plus a weak relation cue

That is too narrow for HotpotQA-style multihop comparison and bridge
questions.

## Route Activation Fixtures

The current `limit=5` HotpotQA smoke sample should be treated as route
activation fixtures for calibration.

### Fixture 1

- `question_id`: `5a8b57f25542995d1e6f1371`
- `question`: `Were Scott Derrickson and Ed Wood of the same nationality?`
- `gold_support titles`: `Scott Derrickson`, `Ed Wood`
- `question type`: attribute comparison
- current `query_features`:
  - `relation_question = false`
  - `global_question = false`
  - `evidence_required = false`
- current `graph_worthy`: `false`
- current `internal_route`: `standard_rag` after fallback
- expected route: `local_graphrag`

Why:

- This is not a simple one-hop lookup.
- It compares the same attribute across two entities.
- The answer needs at least two entity-linked facts before comparison.

### Fixture 2

- `question_id`: `5a8c7595554299585d9e36b6`
- `question`: `What government position was held by the woman who portrayed Corliss Archer in the film Kiss and Tell?`
- `gold_support titles`: `Kiss and Tell (1945 film)`, `Shirley Temple`
- `question type`: bridge entity
- current `query_features`:
  - `relation_question = false`
  - `global_question = false`
  - `evidence_required = false`
- current `graph_worthy`: `false`
- current `internal_route`: `standard_rag` after fallback
- expected route: `local_graphrag`

Why:

- The query first resolves the performer in one document, then resolves that
  person's government position in another.
- This is a two-hop relation chain even without explicit "relationship"
  wording.

### Fixture 3

- `question_id`: `5a85ea095542994775f606a8`
- `question`: `What science fantasy young adult series, told in first person, has a set of companion books narrating the stories of enslaved worlds and alien species?`
- `gold_support titles`: `The Hork-Bajir Chronicles`, `Animorphs`
- `question type`: bridge entity
- current `query_features`:
  - `relation_question = false`
  - `global_question = false`
  - `evidence_required = false`
- current `graph_worthy`: `false`
- current `internal_route`: `standard_rag` after fallback
- expected route: `local_graphrag`

Why:

- The query links a companion-book description to its parent series.
- This is a cross-document entity bridge even though the wording is descriptive
  instead of explicitly relational.

### Fixture 4

- `question_id`: `5adbf0a255429947ff17385a`
- `question`: `Are the Laleli Mosque and Esma Sultan Mansion located in the same neighborhood?`
- `gold_support titles`: `Laleli Mosque`, `Esma Sultan Mansion`
- `question type`: comparison
- current `query_features`:
  - `relation_question = false`
  - `global_question = false`
  - `evidence_required = false`
- current `graph_worthy`: `false`
- current `internal_route`: `standard_rag` after fallback
- expected route: `local_graphrag`

Why:

- The question compares one location attribute across two entities.
- It still needs a two-entity evidence chain, not a single isolated fact.

### Fixture 5

- `question_id`: `5a8e3ea95542995a26add48d`
- `question`: `The director of the romantic comedy "Big Stone Gap" is based in what New York city?`
- `gold_support titles`: `Big Stone Gap (film)`, `Adriana Trigiani`
- `question type`: bridge relation
- current `query_features`:
  - `relation_question = false`
  - `global_question = false`
  - `evidence_required = false`
- current `graph_worthy`: `false`
- current `internal_route`: `standard_rag` after fallback
- expected route: `local_graphrag`

Why:

- The query resolves the director from the film first, then resolves the city
  from the director profile.
- This is the exact kind of nested relation that graph routing should consider.

## Calibration Principle

HotpotQA multihop questions often hide graph structure behind natural-language
comparison and bridge wording.

Examples that should not stay outside graph routing:

- `same nationality / same country / same birthplace`
- `mother of the director of ...`
- `spouse of the performer of ...`
- `based in what city` after resolving an intermediate entity

So the calibration target is:

1. do not mark every query graph-worthy
2. do not use gold answers or gold support in runtime
3. do widen recognition for:
   - comparison questions
   - bridge relation questions
   - multi-entity relation questions

## Expected Next Changes

The next code phase should only do two things:

1. add eval-only forced graph diagnostics so we can separate:
   - planner gating failure
   - graph seed / entity / path failure
2. minimally widen planner and graph-worthiness heuristics so these fixtures can
   enter graph routing conservatively

## Bottom Line

These 5 HotpotQA questions are valid route activation fixtures.

If calibration works, at least part of this sample should stop looking like:

- `query_features = all false`
- `graph_worthy = false`
- `internal_route = standard_rag`

If that still happens after the heuristic update, the next blocker is no longer
planner wording. It is graph seed, entity linking, or graph retrieval quality.
