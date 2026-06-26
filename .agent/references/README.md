# Agent Reference Index

`.agent/references/` is the durable navigation layer for Agents. It points to
source-of-truth files and commands; it does not carry long target architecture
design.

## Active Files

```text
.agent/references/
  README.md
  current-program.md
  docs-map.md
  code-map.md
  runtime-call-chain.md
  verification-map.md
  command-catalog.md
  known-pitfalls.md
```

## Use

- `current-program.md`: active executable Agent program.
- `docs-map.md`: formal docs and history entrypoints.
- `code-map.md`: current code owners and protected runtime boundaries.
- `runtime-call-chain.md`: current backend call path.
- `verification-map.md`: verifier, pytest, grep, and closure command map.
- `command-catalog.md`: common command snippets.
- `known-pitfalls.md`: common mistakes and forbidden restorations.

## Archive

Old detailed maps are archived under:

- `docs/architecture/history/agent-reference-fragments/`

If a future task needs archived detail, promote only the smallest current fact
back into the active reference set.
