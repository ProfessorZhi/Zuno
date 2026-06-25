# Known Pitfalls

- Do not treat `domain-packs/`, `DomainQAGraph`, or `tests/compat/` as safe to
  delete before Phase 11 import and test proof.
- Do not restore `docs/architecture/phases/`, `docs/architecture/plans/`, or
  `docs/architecture/programs/` as current front-path directories.
- Do not commit `data/`, `reports/`, `.local/`, `.codex/`, or `node_modules/`.
- Do not claim Java, microservices, event workers, or default multi-agent mode
  as near-term implementation.
- Do not expose old GraphRAG route names or migration-only fields in frontend
  user-facing text.
