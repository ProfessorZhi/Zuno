# 已知坑

- Do not restore root `domain-packs/`, `DomainQAGraph`, retired Domain Pack
  runtime sources, or the former `tests/compat/` holding area after Phase 11
  retirement proof. Do not delete migration compatibility evidence before
  replacement or retirement tests exist. Retired surfaces must not be restored
  as target repository layout.
- Do not restore `docs/architecture/phases/`, `docs/architecture/plans/`, or
  `docs/architecture/programs/` as current front-path directories.
- Do not commit `data/`, `reports/`, `.local/`, `.codex/`, or `node_modules/`.
- Do not claim Java, microservices, event workers, or default multi-agent mode
  as near-term implementation.
- Do not expose old GraphRAG route names or migration-only fields in frontend
  user-facing text.
- Do not use archived near-term 01-19 fragments as active target source.
- Do not expand `.agent/references/` back into long architecture prose; use
  `.agent/architecture/near-term/` for detailed target design.
- Do not call Elasticsearch "BM25" as if the backend were the algorithm. Native
  BM25 is the target local algorithm; Elasticsearch is an optional adapter.
