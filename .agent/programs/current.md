# Current Agent Program

The current executable program is:

- [Official GraphRAG Cleanup V1](official-graphrag-cleanup-v1/README.md)

Current status:

- Phase 01 through Phase 10 are complete.
- Phase 11A is complete; commit `24abdd9` introduced the project query runtime.
- Phase 11B is complete; commit `b160c4b` unified knowledge queries under the
  single `GeneralAgent` path.
- Phase 11C is blocked by active Domain Pack, `DomainQAGraph`,
  `MultiAgentSupervisorGraph`, Docker/eval/frontend/API, and `tests/compat/`
  dependencies.
- Phase 12 is partial / not closed; final full `pytest` and formal Eval
  baseline comparison are not complete.

The next executable actions are 11C active dependency removal, Contract Review
asset migration, full pytest, eval baseline comparison, and program closure.

Formal public status is summarized in:

- `docs/architecture/roadmap.md`
