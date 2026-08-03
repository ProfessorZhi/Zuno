# Goal05 PHASE22 Worker CC-MM-1 DerivationSpec Evidence

## Identity

- agent: claude-code
- model: claude-minimax
- worker: CC-MM-1
- session_id: `be9c0934-546c-452a-9231-a650fe5997a0`
- resume_of_session_id: `be9c0934-546c-452a-9231-a650fe5997a0`
- cost_scope: `single-agent-pr-handoff`
- branch: `codex/phase22-synthetic-dataset-claude-minimax-cc-mm-1`

## Scope

This handoff implements a candidate-only DerivationSpec kernel for three
representative synthetic benchmark cases:

- `single_doc_fact`
- `graph_path`
- `temporal_version`

The validator derives answers from declarative specs plus structured inputs. It
does not use `expected_answer` as derivation input; `expected_answer` is read
only after derivation for validation comparison.

## Changed Files

- `tools/evals/zuno/synthetic_benchmark/__init__.py`
- `tools/evals/zuno/synthetic_benchmark/spec.py`
- `tools/evals/zuno/synthetic_benchmark/fixtures.py`
- `tests/evals/synthetic_benchmark/__init__.py`
- `tests/evals/synthetic_benchmark/test_derivation_spec.py`
- `docs/evidence/goal05-phase22-worker-cc-mm-1-derivation-spec.md`

## Verification

Required behavior is covered by focused tests:

- SourceSpan must literally support a single fact answer.
- Graph path must enforce relation kind, from, to, and direction across two hops.
- Wrong relation direction fails closed.
- Temporal version selection uses `query_time`, `effective_at`, and
  `superseded_by`.
- Wrong temporal expectation fails after independent derivation.
- Same seed and input registry produce reproducible hashes.

Commands run by coordinator after worker resume and amendment:

```powershell
python -m pytest tests/evals/synthetic_benchmark/test_derivation_spec.py -q
git diff --check
```

## Boundary

This is not a fixed benchmark measurement, not a public reviewer-approved case
set, and not PHASE22 completion evidence. It is a candidate pack proving the
minimum derivation boundary needed for later benchmark review.

## Cost Segment

The resume segment ended with `error_max_turns` before worker commit. Segment
metrics are recorded from `stream-json --verbose`:

```text
duration_ms_current_segment=253203
duration_api_ms_current_segment=228621
input_tokens_current_segment=50230
cache_read_input_tokens_current_segment=774656
cache_creation_input_tokens_current_segment=0
output_tokens_current_segment=12026
total_cost_usd_current_segment=0.939128
metrics_source=stream-json final result
provider_quota_basis=unknown
```

Provider quota basis is unknown; API estimated cost is not claimed as actual
provider quota deduction.

## Risk

Risk is low and isolated to new candidate-only eval tooling. The graph path
contract was amended by Codex after worker stopped so the direction requirement
is explicit in the DerivationSpec instead of implied by path traversal comments.
