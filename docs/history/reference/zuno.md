# Zuno Reference

This page is a stable reference index. It is not the current roadmap and does
not carry execution decisions.

## Current Entrypoints

- [Repository README](../../README.md)
- [Current Architecture](../architecture/current-architecture.md)
- [Target Architecture](../architecture/target-architecture.md)
- [Roadmap](../architecture/roadmap.md)
- [Public Demo Evidence](../evidence/public-demo.md)

## Main Paths

- `apps/web/`: Vue web workspace
- `apps/desktop/`: Electron desktop shell
- `src/backend/zuno/`: current backend runtime truth
- `infra/`: Docker and environment infrastructure
- `tools/`: scripts, launchers, evals, and maintenance tooling
- `tests/`: repository verification
- `docs/`: stable human-facing documentation
- `.agent/`: local Agent workflow library

## Local-Only State

- `.local/`: local machine data and generated outputs
- `.codex/`: local Codex state
- `node_modules/`, `apps/web/node_modules/`, `apps/web/dist/`: generated
  frontend artifacts
- `data/` and `reports/`: generated or downloaded eval data unless promoted
  deliberately

## Related Reference

- [API Reference](api.md)
- [Core Reference](core.md)
- [Database Reference](database.md)
- [Service Reference](service.md)
