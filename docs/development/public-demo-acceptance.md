# Public Demo Acceptance

This note turns the current public demo material into an explicit public-proof acceptance layer.

## Why This Exists

The public demo is no longer only "we have a runbook" or "we have some benchmark numbers".

For the current architecture-upgrade program, the public-facing proof needs to show all of the following:

1. there is a real quality result for a public audience
2. there is a reproducible local command path
3. there is a clear explanation of why the answer or benchmark result holds
4. there is at least one low-cost end-to-end runtime smoke path that produces a real report artifact
5. evidence-insufficient cases fail conservatively instead of fabricating a grounded-looking answer

## Public Proof Acceptance Gate

Treat the public demo as ready only when all of the following are true:

1. [public-demo-runbook.md](public-demo-runbook.md) contains a local embedding preflight command
2. [public-demo-runbook.md](public-demo-runbook.md) contains both:
   - the generic `graph_relation` compare matrix command
   - the `contract_review` scaled compare matrix command
3. [public-demo-runbook.md](public-demo-runbook.md) explicitly lists the five core retrieval metrics:
   - Recall@5
   - Hit Rate@5
   - Context Precision@5
   - MRR@5
   - NDCG@5
4. [public-demo-evidence.md](public-demo-evidence.md) records the current public benchmark result for:
   - generic graph-relation retrieval
   - scaled contract-review retrieval
5. [README.md](/abs/path/F:/internship-work/resume%26resume%20project/02_projects/Zuno/README.md) exposes the same thesis in public-facing language:
   - GraphRAG beats baseline on relation-heavy retrieval
   - contract-review domain modeling becomes more valuable as corpus size and distractor density increase
6. public docs do not link public proof directly to ignored local `rag_eval/runs/` outputs
7. `python tools/scripts/verify_public_demo_runtime.py` passes and proves the offline contract-review demo path can emit a real report
8. `python tools/scripts/verify_public_demo_strict_grounding.py` passes and proves:
   - supported evidence stays answerable in `strict_grounded`
   - unsupported evidence degrades to `NO_RELEVANT_EVIDENCE_FOUND`

## Current Public Result Baseline

The current public proof set is:

- generic graph-relation:
  - `baseline_rag`: Recall@5 `0.1167`, MRR@5 `0.2000`
  - `rag_graph_chunk_backed`: Recall@5 `0.3167`, MRR@5 `0.4000`
- scaled contract review:
  - `baseline_rag`: Recall@5 `0.3333`, MRR@5 `0.1486`, NDCG@5 `0.1931`
  - `rag_graph_chunk_backed`: Recall@5 `1.0000`, MRR@5 `0.9583`, NDCG@5 `0.9692`

## Single Verification Command

```powershell
python tools/scripts/verify_public_demo_docs.py
```

## Low-Cost Runtime Smoke Command

```powershell
python tools/scripts/verify_public_demo_runtime.py
```

This smoke verifier does not claim that a real remote model is live.
It proves something narrower and more useful for the public proof surface:

- the committed `contract_review` demo path still runs end-to-end in `dev_offline`
- the run emits a real markdown report artifact
- the report still carries answer text, graph-path evidence, and citation output

## Low-Cost Strict Grounding Smoke Command

```powershell
python tools/scripts/verify_public_demo_strict_grounding.py
```

This verifier proves a different and equally important public-demo claim:

- `strict_grounded` keeps an answer when the cited evidence is actually query-aligned
- `strict_grounded` returns `NO_RELEVANT_EVIDENCE_FOUND` when evidence is present but not truly supportive
- public demo proof is therefore not only "can produce answers", but also "can fail conservatively"

## What This Does Not Claim

This acceptance note does not claim that every public demo runtime dependency is already live on every machine.

It proves something narrower and more honest:

- the public repo now contains a coherent, GitHub-safe, reproducible explanation of the strongest current demo evidence
- the explanation is tied to committed docs rather than ignored local output folders
