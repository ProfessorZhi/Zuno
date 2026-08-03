# PHASE22-SNAPSHOT-FAIL-CLOSED-GATE — Evidence (MiniMax4)

Worker: MiniMax4 (claude/minimax4-phase22-snapshot-failclosed-gate)
Verifier: `tools/scripts/verify_phase22_snapshot_fail_closed.py`
Run on: 2026-08-04
Base SHA: `ef20d6db0f34ee7b11f59a9f576c850ade613e49`

## Exact Base Head

`ef20d6db0f34ee7b11f59a9f576c850ade613e49` (DeepSeek2 PR #113 head)

## Summary

The Fail-closed Snapshot Activation Persistence / Scope Gate is a static
AST + contract fixture verifier.  It proves the structural preconditions
for snapshot activation fail-closed semantics without executing live
PostgreSQL write/read or live index service calls.  It accompanies
DeepSeek2 PR #113 and produces an accurate, evidence-backed verdict of
the current snapshot binding topology.

| Run | Exit | Status |
|-----|------|--------|
| `--mode contract` | 0 | `SNAPSHOT_FAIL_CLOSED_CONFIRMED` (16/16 fixtures pass) |
| `--mode repository` | 4 | `INDEX_SCOPE_VIOLATION` |

The repository mode reports `INDEX_SCOPE_VIOLATION` because the real
index-client methods (``ElasticsearchBm25IndexClient.search_documents``,
``MilvusVectorIndexClient.search_documents``, ``Neo4jGraphIndexClient.query_path``
and friends) declare ``tenant_id=None`` / ``workspace_id=None`` /
``knowledge_version_id=None`` as default keyword-only parameters.  These
silent ``None`` defaults let a caller bypass the scope guard by simply
omitting the scope arguments.  The DeepSeek2 PR is therefore not yet
ready to fail-closed at the index-client boundary and must be patched
before activation can be declared safe.

## Discovered Activation Paths

| Path | Purpose |
|------|---------|
| `src/backend/zuno/knowledge/indexing/snapshot_activation.py` | Snapshot adapter + persistence port |
| `src/backend/zuno/knowledge/indexing/adapters.py` | Index clients (ES / Milvus / Neo4j) |

## Discovered Persistence Calls

The collector inspects `SnapshotActivationAdapter.activate` for
``self._snapshot_persistence.persist(...)`` and
``self._snapshot_persistence.read(...)`` invocations.  Both calls are
present in the real repository; the gate additionally requires
``persistence_evidence.persisted`` and ``consistency_checks`` checks to
be present.

## Receipt Construction Ordering

The receipt is built via ``build_snapshot_activation_receipt`` *after* a
successful ``read()`` call.  In addition, the activator marks
``persisted=False`` on any ``persist()`` exception, blocking activation.

## Readback Scope

The ``PostgresKnowledgeSnapshotPersistence.read`` method returns a dict
that includes ``tenant_id``, ``knowledge_version_id`` and
``snapshot_hash``.  The gate considers the readback scope enforced when
all three fields are present in the returned dict literal.

## Index Scope

Three index-client methods have silent ``None`` defaults for
``tenant_id`` / ``workspace_id`` / ``knowledge_version_id``.  This is the
root cause of the repository-mode `INDEX_SCOPE_VIOLATION` verdict.

## Violations

- `Neo4jGraphIndexClient.search_documents`: `tenant_id`, `workspace_id`,
  `knowledge_version_id` all default to ``None``.
- `MilvusVectorIndexClient.search_documents`: `tenant_id`,
  `workspace_id`, `knowledge_version_id` all default to ``None``.
- `ElasticsearchBm25IndexClient.search_documents` and friends: same.
- `MilvusVectorIndexClient.search_documents`: dynamic f-string
  (``expr = 'tenant_id == ...'``) without explicit scope filter check.
- `Neo4jGraphIndexClient.query_path`: `tenant_id`, `workspace_id`,
  `knowledge_version_id` default to ``None``.

## Not-Proven Boundary

This gate proves only the static binding topology.  It explicitly does
**not** prove:

- live PostgreSQL write/read;
- real Snapshot activation;
- real three-index corpus visibility;
- four-profile measurement;
- production readiness.

A subsequent DeepSeek worker is required to execute the binding
end-to-end against a live MinIO / PostgreSQL / Elasticsearch / Milvus /
Neo4j stack.

## Reproduction

```bash
python tools/scripts/verify_phase22_snapshot_fail_closed.py --mode contract
python tools/scripts/verify_phase22_snapshot_fail_closed.py --mode repository
python tools/scripts/verify_phase22_snapshot_fail_closed.py --mode repository --json
```

## Files in this evidence directory

* `SNAPSHOT-FAIL-CLOSED-STATUS.md` — this document.
* `contract_results.json` — contract-mode machine attestation.
* `repository_results.json` — repository-mode machine attestation.