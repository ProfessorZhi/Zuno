# Workflows

## Entrypoint Flow

```text
Agent enters repository
  -> read AGENTS.md
  -> read docs/architecture front path
  -> use .agent references/templates/scripts as needed
  -> update docs when formal truth changes
```

## Documentation Flow

```text
new requirement / feature / refactor / architecture replacement
  -> decide whether a program, phase, spec, ADR, or audit changes
  -> move superseded material to history
  -> update AGENTS.md and .agent references when workflow changes
  -> verify, commit, push when files changed
```

## History Flow

`docs/architecture/history/` is for old programs, replaced designs, stale migration plans, and closure records. History remains reachable, but it must not dominate the current reading path.
