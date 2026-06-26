# Docs Map

## Formal Human Entrypoints

- `README.md`: repository overview and first-read path
- `docs/README.md`: documentation index
- `docs/architecture/current-architecture.md`: current repo reality
- `docs/architecture/target-architecture.md`: near-term target summary
- `docs/architecture/roadmap.md`: current status, blockers, and next step
- `docs/evidence/public-demo.md`: selected public evidence index
- `docs/architecture/decisions/`: formal ADRs
- `docs/architecture/history/`: archived phases, plans, programs, and Agent workflow material

## Agent Workflow Material

- `AGENTS.md`: repository-level Agent entrypoint
- `.agent/README.md`: Agent workflow library rules
- `.agent/programs/current.md`: current program status pointer
- `.agent/programs/zuno-target-runtime-v2/`: active executable Agent program
- `docs/architecture/history/programs/zuno-target-architecture-migration-v1/`:
  completed target migration phase material
- `docs/architecture/history/programs/official-graphrag-cleanup-v1/`: archived
  GraphRAG cleanup evidence, not an active executable program
- `.agent/architecture/near-term/`: detailed near-term target architecture
- `.agent/architecture/future/`: Java, microservices, workers, and multi-agent horizon notes
- `.agent/architecture/decisions/`: locked choices, open questions, retired surfaces
- `.agent/references/`: slim navigation indexes only
- `.agent/templates/`: reusable prompts and reports
- `.agent/scripts/`: workflow checks and local operating aids

## Boundary

`docs/` carries stable conclusions. `.agent/` carries executable workflow and
design-stage detail. Historical material stays reachable through
`docs/architecture/history/`.
## Target Architecture Visual Reference

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`:
  canonical Target / Proposed visual blueprint for architecture replacement,
  directory layout, Context/Memory, GraphRAG boundary, and repository hygiene
  work.
- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`
- The HTML is not Current Truth and is not part of the `docs/` front path.

## Formal Reference Docs

- `docs/reference/terminology.md`: status labels and public architecture terms.
- `docs/evidence/eval-baselines.md`: Eval baseline status.
- `docs/architecture/history/programs/`: superseded execution programs,
  including archived `context-memory-agent-runtime-v1`.
- `docs/architecture/history/near-term-architecture-fragments/`: archived old
  01-19 near-term fragments.
- `docs/architecture/history/agent-reference-fragments/`: archived old
  reference maps.
