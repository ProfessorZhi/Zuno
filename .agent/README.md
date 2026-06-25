# Agent Workflow Library

`.agent/` is the Agent workflow library. It is not the formal architecture truth.

## Boundaries

- `docs/` holds formal human-facing documentation truth.
- `AGENTS.md` is the repository-level Agent entrypoint.
- `.agent/` holds Agent references, templates, scripts, and operating aids.
- `docs/architecture/history/` archives superseded programs, old plans, and replaced designs.

Formal conclusions go to `docs/`. Agent execution aids go here.

`.agent/references/` is only the Agent navigation layer: quick maps, current
reality snapshots, command maps, and verification maps. It does not carry target
architecture design and does not replace `.agent/architecture/near-term/`.

## Tracked Structure

```text
.agent/
  README.md
  architecture/
    near-term/
    future/
    decisions/
  references/
    README.md
    current-program.md
    docs-map.md
    code-surfaces.md
    verification-map.md
    current_architecture/
  programs/
    current.md
    official-graphrag-cleanup-v1/
  workflows/
  skills/
  lessons/
  templates/
  scripts/
```

Local-only directories are ignored by `.gitignore`:

```text
.agent/local/
.agent/local/notes/
.agent/local/tmp/
.agent/local/logs/
.agent/local/secrets/
```

Do not keep tracked placeholder files inside those local-only directories.

## Self-Maintenance Rule

When a user asks for a new requirement, new feature, refactor, or architecture replacement, first decide whether the change must update:

1. `.agent/programs/<program>/`
2. a phase document
3. a spec, ADR, or audit
4. `docs/architecture/history/`
5. `docs/architecture/README.md`
6. `docs/architecture/current-architecture.md`
7. `docs/architecture/target-architecture.md`
8. `AGENTS.md`
9. `.agent/references/current-program.md`
10. `.agent/references/docs-map.md`
11. `.agent/programs/` or `.agent/references/current_architecture/`
12. `.agent/scripts/` or `.agent/templates/`
13. `.gitignore`
14. verification, commit, and push if files changed

If a change replaces an older design, move the old material to `docs/architecture/history/` instead of deleting it.

## Operating Rules

- Read formal truth from `docs/architecture/` first.
- Use `.agent/references/` only as the Agent navigation layer.
- Use `.agent/templates/` for reusable prompts and closure reports.
- Use `.agent/scripts/` for read-only workflow checks.
- Use `.agent/workflows/` for complete execution procedures.
- Use `.agent/skills/` for thin task-routing entries.
- Use `.agent/lessons/` for verified reusable experience.
- Use `.agent/architecture/near-term/` for the detailed next refactor target.
- Use `.agent/architecture/future/` only for Java, microservices, event/workers,
  and multi-agent horizon discussions.
- Use `.agent/architecture/decisions/` for locked choices, open questions, and
  retired surfaces.
- Modification tasks require verification, commit, and push unless blocked.
- Read-only reconnaissance does not commit or push.

## Knowledge Promotion

Temporary discovery -> `.agent/local/notes/` (ignored).

One-task investigation evidence -> `.agent/audits/`.

Verified reusable experience -> `.agent/lessons/`.

Stable operation procedure -> `.agent/workflows/`.

Task-triggered mature workflow -> `.agent/skills/`.

Rules that apply to every task -> `AGENTS.md`.

Implemented, verified, human-facing facts -> `docs/`.

Promote material only when it has code, tests, commands, or repeated task
evidence; a clear scope; and clear non-scope.
