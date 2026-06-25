# Known Pitfalls

- Do not restore root `domain-packs/`, `DomainQAGraph`, retired Domain Pack
  runtime sources, or the former `tests/compat/` holding area after Phase 11
  retirement proof. Do not delete migration compatibility evidence before
  replacement or retirement tests exist.
- Do not restore `docs/architecture/phases/`, `docs/architecture/plans/`, or
  `docs/architecture/programs/` as current front-path directories.
- Do not commit `data/`, `reports/`, `.local/`, `.codex/`, or `node_modules/`.
- Do not claim Java, microservices, event workers, or default multi-agent mode
  as near-term implementation.
- Do not expose old GraphRAG route names or migration-only fields in frontend
  user-facing text.
