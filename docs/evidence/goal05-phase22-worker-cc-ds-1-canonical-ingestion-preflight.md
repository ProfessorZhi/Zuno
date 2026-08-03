# Goal05 PHASE22 Worker CC-DS-1 Canonical Ingestion Preflight

## Identity

- agent: claude-code
- model: claude-deepseek
- worker: CC-DS-1
- session_id: `b2624440-d104-4b55-aa64-b92712d844cf`
- resume_of_session_id: `b2624440-d104-4b55-aa64-b92712d844cf`
- cost_scope: `single-agent-pr-handoff`
- branch: `codex/phase22-canonical-ingestion-claude-deepseek-cc-ds-1`

## Scope

This handoff implements a read-only Canonical Ingestion Preflight. It statically
checks whether the repository exposes the formal dependencies required before a
document may enter canonical ingestion.

Output is restricted to:

```text
READY_FOR_CANONICAL_INGESTION
BLOCKED_WITH_EXACT_GAP
```

The tool parses Python source with `ast`; it does not import production runtime
code, open TCP connections, write indexes, create receipts, or mutate production
facts.

## Changed Files

- `tools/scripts/phase22_canonical_ingestion_preflight.py`
- `tests/repo/test_phase22_canonical_ingestion_preflight.py`
- `docs/evidence/goal05-phase22-worker-cc-ds-1-canonical-ingestion-preflight.md`

## Required Checks

- Formal Ingestion Application Service
- UoW / Repository Owner
- Object Store
- PostgreSQL
- Elasticsearch Adapter
- Milvus Adapter
- Neo4j Adapter
- Embedding Gateway
- Snapshot Activation Owner
- Index Visibility / Read-back Contract

## Real Repository Verdict

The real repository currently returns:

```text
BLOCKED_WITH_EXACT_GAP
```

Exact gap:

```text
object store: owner non-unique (expected exactly one *ObjectStore, found 4)
candidate: DurableObjectStore (src/backend/zuno/knowledge/ingestion/source_object_upload.py)
candidate: LocalObjectStore (src/backend/zuno/knowledge/storage/local_object_store.py)
candidate: DurableMinioObjectStore (src/backend/zuno/platform/storage/durable.py)
candidate: MinioObjectStore (src/backend/zuno/platform/storage/object_store.py)
```

This is a preflight blocker, not a production write failure. It means canonical
ingestion readiness cannot claim a unique object-store owner until PHASE22
cleanup resolves the ownership surface.

## Verification

Commands run by coordinator after worker resume:

```powershell
python -m pytest tests/repo/test_phase22_canonical_ingestion_preflight.py -q
python tools/scripts/phase22_canonical_ingestion_preflight.py
git diff --check
```

The script is expected to exit `1` on the current real tree because it honestly
reports `BLOCKED_WITH_EXACT_GAP`.

## Cost Segment

The resume segment ended with `error_max_budget_usd` before worker commit.
Segment metrics are recorded from `stream-json --verbose`:

```text
duration_ms_current_segment=227226
duration_api_ms_current_segment=190919
input_tokens_current_segment=11944
cache_read_input_tokens_current_segment=1129472
cache_creation_input_tokens_current_segment=0
output_tokens_current_segment=23682
total_cost_usd_current_segment=1.296542
metrics_source=stream-json final result
provider_quota_basis=unknown
```

Provider quota basis is unknown; API estimated cost is not claimed as actual
provider quota deduction.

## Risk

Risk is low: the implementation is read-only, deterministic, and covered by
focused synthetic repo tests. It does not change canonical ingestion runtime or
mark any submitted document as ingested.
