# Risk Register

## Workflow Risks

- Multiple Agent entrypoints can make future runs read stale rules.
- `.agent/` can become a hidden local cache if ignored wholesale.
- Agent-only conclusions can drift from formal docs.

## Documentation Risks

- Completed Phase 0-6 truth can be accidentally overwritten by new program work.
- Superseded programs can stay in the front path and mislead future readers.
- Domain Pack can remain framed as the new front-path mainline instead of historical context or supporting capability.

## GraphRAG Risks

- Official GraphRAG concepts can be mixed with local legacy terminology without clear migration notes.
- Prompt tuning, query method, and project settings can be implemented without durable acceptance gates.

## Mitigation

Keep formal decisions in `docs/`, workflow aids in `.agent/`, and superseded material in `history/`. Run workflow verification before closure.
