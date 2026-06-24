# Agent Workflow Library

`.agent/` is the Agent workflow library. It is not the formal architecture truth.

## Boundaries

- `docs/` holds formal human-facing documentation truth.
- `AGENTS.md` is the repository-level Agent entrypoint.
- `.agent/` holds Agent references, templates, scripts, and operating aids.
- `docs/architecture/history/` archives superseded programs, old plans, and replaced designs.

Formal conclusions go to `docs/`. Agent execution aids go here.

## Tracked Structure

```text
.agent/
  README.md
  references/
    README.md
    current-program.md
    docs-map.md
    code-surfaces.md
    verification-map.md
    current_architecture/
  templates/
  scripts/
```

Local-only directories are ignored by `.gitignore`:

```text
.agent/notes/
.agent/tmp/
.agent/logs/
.agent/local/
.agent/secrets/
```

## Self-Maintenance Rule

When a user asks for a new requirement, new feature, refactor, or architecture replacement, first decide whether the change must update:

1. `docs/architecture/programs/<program>/`
2. a phase document
3. a spec, ADR, or audit
4. `docs/architecture/history/`
5. `docs/architecture/README.md`
6. `docs/architecture/current-architecture.md`
7. `docs/architecture/target-architecture.md`
8. `AGENTS.md`
9. `.agent/references/current-program.md`
10. `.agent/references/docs-map.md`
11. `.agent/references/current_architecture/`
12. `.agent/scripts/` or `.agent/templates/`
13. `.gitignore`
14. verification, commit, and push if files changed

If a change replaces an older design, move the old material to `docs/architecture/history/` instead of deleting it.

## Operating Rules

- Read formal truth from `docs/architecture/` first.
- Use `.agent/references/` only as the Agent navigation layer.
- Use `.agent/templates/` for reusable prompts and closure reports.
- Use `.agent/scripts/` for read-only workflow checks.
- Modification tasks require verification, commit, and push unless blocked.
- Read-only reconnaissance does not commit or push.
