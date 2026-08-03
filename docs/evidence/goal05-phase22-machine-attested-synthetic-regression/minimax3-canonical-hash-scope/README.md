# PHASE22 Canonical Hash / Scope Companion Gate — MiniMax3

This directory holds the evidence emitted by the
`verify_phase22_canonical_hash_scope.py` companion gate. The gate is a
read-only, fail-closed Test-only Companion PR for PR #112
(`claude/deepseek1-phase22-canonical-ingestion`).

It enforces two contracts on PR #112's canonical manifests:

- **Hash contract** — `source_manifest_hash`, `canonical_ir_hash`, and the
  `corpus_hash` field of the runtime request manifest (a.k.a.
  `dataset_corpus_hash`) must each be read from its own canonical
  manifest, must be distinct, and must match the frozen values. Aliasing,
  missing fields, wrong-length hex, and ambiguous evidence field names
  all fail closed.
- **Scope contract** — the official scope is `tenant_auroralis` +
  `workspace_regression`. The verification scope
  (`tenant_auroralis_verify` / `workspace_regression_verify`) is
  allowed only when an explicit independent isolation envelope is
  declared (database, schema, compose project). Mixing official and
  verification scopes in the same payload is rejected.

The gate never modifies PR #112's branch. It does not run live
ingestion. It does not write to a database. It reads only
manifest + evidence files in the repository.

## Reports

- `contract_mode_report.json` — every fixture in
  `tests/fixtures/phase22_canonical_hash_scope/` lands on the expected
  status kind.
- `repository_mode_report.json` — verifier verdict against PR #112's
  current manifests.

## Frozen expectations

| Key                   | Value                                                              |
| --------------------- | ------------------------------------------------------------------ |
| `source_manifest_hash`| `0a6ee33cae62e5c3370217f5ec028a4efd1a52855557a71b57f2dc8bdce0c26a` |
| `canonical_ir_hash`   | `43d4842d41ea528cec6bfdfd7540a0c58c8c6653f8fa752b9eee31c7a0f079a6` |
| `dataset_corpus_hash` | `749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4` |
| Official tenant       | `tenant_auroralis`                                                 |
| Official workspace    | `workspace_regression`                                             |

## Boundaries the gate cannot prove

- live database column `tenant_id` / `workspace_id` introspection
- `KnowledgeSpace` scope column vs manifest scope
- `security_decisions` (`security_authorization_decisions`) scope
  consistency in the live database
- `KnowledgeVersion` persistence in `knowledge_versions` table
- `source_upload_manifest.runtime_ingested` live attestation
- `canonical_ir_manifest.parser_runtime_executed` live attestation
- `canonical_ir_manifest.postgres_facts_verified` live attestation

These boundaries are recorded explicitly in
`repository_mode_report.json: not_proven_boundary` so the coordinator
sees exactly what is and is not proven by static analysis.

## Exit codes

| Code | Status                            |
| ---- | --------------------------------- |
| 0    | CANONICAL_HASH_SCOPE_CONFIRMED    |
| 2    | HASH_CONTRACT_VIOLATION           |
| 3    | SCOPE_CONTRACT_VIOLATION          |
| 4    | IDENTITY_UNRESOLVED               |
| 5    | TOOL_ERROR                        |