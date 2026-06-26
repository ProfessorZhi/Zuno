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
4. `docs/architecture/roadmap.md`
5. `.agent/README.md`
6. `.agent/references/current-program.md`
7. `.agent/references/docs-map.md`
8. `.agent/references/code-map.md`
9. `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
10. `.agent/architecture/near-term/01-target-runtime-architecture.md`
11. `.agent/architecture/near-term/02-context-memory-architecture.md`
12. `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
13. `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
14. `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`

For implementation tasks, read the relevant code after the docs. Do not infer runtime behavior from docs alone.

## Task Routing

- scope unclear -> `.agent/skills/zuno-read-only-audit/SKILL.md`
- docs, `.agent`, references, workflows, skills, or history -> `.agent/skills/zuno-docs-maintenance/SKILL.md`
- directory move, deletion, archive, ignore rules, generated/local cleanup -> `.agent/skills/zuno-repo-hygiene/SKILL.md`
- `apps/web` -> `apps/web/AGENTS.md` and `.agent/skills/zuno-frontend-change/SKILL.md`
- `src/backend/zuno` -> `src/backend/zuno/AGENTS.md` and `.agent/skills/zuno-backend-change/SKILL.md`
- API, DTO, request/response, frontend/backend contract -> `.agent/skills/zuno-api-contract-change/SKILL.md`
- architecture replacement -> `.agent/skills/zuno-architecture-refactor/SKILL.md`
- architecture replacement, directory moves, Context/Memory, GraphRAG boundary,
  or repository hygiene tasks must also read
  `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- eval tooling, datasets, metrics, profiles, reports -> `tools/evals/zuno/AGENTS.md` and `.agent/skills/zuno-eval-change/SKILL.md`

## Current Mainline

The completed Phase 0-6 architecture closure remains historical completion truth and must not be rewritten as incomplete.

The active executable Agent program is:

- `.agent/programs/zuno-target-runtime-v2/`

Its current purpose is a controlled first implementation slice after the Zuno
Target Architecture Migration V1 closure: module boundary gates, one low-risk
backend application-boundary move, and minimal callable Context Orchestrator
runtime.

The latest completed program is archived at:

- `docs/architecture/history/programs/zuno-target-architecture-migration-v1/`

Its purpose was to move from the 11A/11B runtime state to the near-term
target architecture and repository layout: finish 11C/12 cleanup, migrate
Contract Review assets, harden GraphRAG Project as the mainline, clean folder
boundaries, then implement Context/Memory and Capability phases around the
single `GeneralAgent`.

The active V2 implementation breakdown is:

- `.agent/programs/zuno-target-runtime-v2/implementation-roadmap.md`
- `.agent/programs/zuno-target-runtime-v2/current-phase.md`
- `.agent/programs/zuno-target-runtime-v2/closure-checklist.md`

The archived V1 near-term implementation breakdown is:

- `docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
- `docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-phases/`
- `docs/architecture/history/programs/official-graphrag-cleanup-v1/` as
  archived evidence for completed GraphRAG cleanup phases and old 11C/12
  planning context
- `docs/architecture/history/programs/zuno-target-runtime-v2/`

Detailed target architecture design for this program lives in:

- `.agent/architecture/`

That directory is a design-stage Agent working set for Zuno architecture. Its
current structure separates:

- `.agent/architecture/near-term/`
  - the detailed near-term ideal architecture for the next refactor target
  - `zuno-ideal-architecture-and-repo-layout.html` as the canonical Target /
    Proposed visual blueprint, not Current Truth
  - five canonical Markdown documents for runtime, Context/Memory,
    Capability/Tool Retrieval, Knowledge/GraphRAG/Retrieval/Fusion, and
    repository boundaries/acceptance gates
- `.agent/architecture/future/`
  - slim long-term horizon for Java business services, microservices,
    event-driven workers, Coding Agent mode, and multi-agent mode
  - not a current refactor acceptance target
- `.agent/architecture/decisions/`
  - slim Agent-side architecture decision summary

Do not treat Java, microservices, event-driven workers, or multi-agent mode as
near-term implementation work unless the user explicitly opens a separate
future-direction implementation program.

## Self-Maintenance Rule

For every new requirement, new feature, refactor, or architecture replacement, decide whether each item must be updated:

1. `.agent/programs/<program>/`
2. a phase document
3. a spec, ADR, or audit
4. `docs/architecture/history/` for any superseded plan
5. `docs/architecture/README.md`
6. `docs/architecture/current-architecture.md`
7. `docs/architecture/target-architecture.md`
8. this `AGENTS.md` current mainline
9. `.agent/references/current-program.md`
10. `.agent/references/docs-map.md`
11. `.agent/programs/`
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
- Module-level `AGENTS.md` files are allowed only where this root entrypoint routes to them.

## Scope Rules

This workflow document does not authorize broad code edits. Respect task-specific forbidden paths. If the requested verification requires changing a forbidden path, stop and return evidence instead of expanding scope.
