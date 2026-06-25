# Root Contract Review Domain Pack Archive

This directory preserves the former root `domain-packs/contract_review/` asset
copy as History. It is not Current runtime input and must not be restored as a
target repository layout.

The active Contract Review example now lives under:

- `examples/graphrag-projects/contract_review/`

That GraphRAG Project copy carries the schema, retrieval policy, prompts, and
eval fixture used by current Contract Review eval and compatibility tests. This
archive keeps the old `pack.yaml` and flat prompt/template layout only so older
Domain Pack decisions remain auditable.

Earlier stale backend-package asset history is preserved separately under:

- `docs/architecture/history/domain-packs/backend-package-contract-review/`
