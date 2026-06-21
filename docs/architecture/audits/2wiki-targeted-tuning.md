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
