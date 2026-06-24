# Zuno Agent Entry

This is the only repository-level Agent entrypoint.

## First Principles

Start from the current task, not from old phase habit.

When the user's motivation or target is unclear, stop and clarify the decision that would change the work. When the target is clear but the proposed path is longer than needed, say so and choose the shorter path. When something breaks, trace the root cause before writing around it.

## Source Boundaries

- `docs/` is the formal documentation truth for humans.
- `AGENTS.md` is the Agent entrypoint and workflow contract.
- `.agent/` is the Agent workflow library: references, templates, scripts, and local operating aids.
- `docs/architecture/history/` is the archive for superseded plans, old programs, retired migration notes, and replaced designs.

Formal conclusions must land in `docs/`. Agent-only navigation, reusable prompts, and helper scripts belong in `.agent/`. Historical material is moved to `docs/architecture/history/`; do not delete it just because it is no longer current.

## Required Reading Order

For architecture, refactor, new feature, or workflow tasks:

1. `docs/architecture/README.md`
2. `docs/architecture/current-architecture.md`
3. `docs/architecture/target-architecture.md`
4. `docs/architecture/phases/README.md`
5. `.agent/README.md`
6. `.agent/references/current-program.md`
7. `.agent/references/docs-map.md`
8. `.agent/references/current_architecture/README.md`

For implementation tasks, read the relevant code after the docs. Do not infer runtime behavior from docs alone.

## Current Mainline

The completed Phase 0-6 architecture closure remains historical completion truth and must not be rewritten as incomplete.

The current new program is:

- `docs/architecture/programs/official-graphrag-cleanup-v1/`

Its purpose is to standardize docs and Agent workflow, clean legacy surfaces, retire Domain Pack as the front-path architecture mainline, and align the next GraphRAG work with official GraphRAG Project, Prompt Tuning, and Query Method concepts.

## Self-Maintenance Rule

For every new requirement, new feature, refactor, or architecture replacement, decide whether each item must be updated:

1. `docs/architecture/programs/<program>/`
2. a phase document
3. a spec, ADR, or audit
4. `docs/architecture/history/` for any superseded plan
5. `docs/architecture/README.md`
6. `docs/architecture/current-architecture.md`
7. `docs/architecture/target-architecture.md`
8. this `AGENTS.md` current mainline
9. `.agent/references/current-program.md`
10. `.agent/references/docs-map.md`
11. `.agent/references/current_architecture/`
12. `.agent/scripts/` or `.agent/templates/`
13. `.gitignore`
14. verification, commit, and push if the task produced modifications

If the answer is no, the reason should be obvious from the task scope. If the answer is yes, update the file in the same change set.

## Task Closure Rules

- Read-only reconnaissance does not commit or push.
- Modification tasks must run the smallest meaningful verification before closure.
- Modification tasks end with commit and push unless verification or push is blocked.
- Never force push, force-with-lease, or amend old commits unless the user explicitly asks.
- Do not keep legacy lowercase or dotted Agent entrypoints in parallel with `AGENTS.md`.

## Scope Rules

This workflow document does not authorize broad code edits. Respect task-specific forbidden paths. If the requested verification requires changing a forbidden path, stop and return evidence instead of expanding scope.
