# Code Surfaces

This file is an orientation map only. It does not expand the scope of a task.

## Main Surfaces

- `apps/web/`: Vue web workspace
- `apps/desktop/`: Electron desktop workspace
- `src/backend/zuno/`: current Python backend runtime truth
- `infra/`: deployment and environment infrastructure
- `tools/`: scripts, launchers, evals, and maintenance tooling
- `tests/`: repo-level verification
- `docs/`: formal documentation
- `.agent/`: Agent workflow library

## Current Boundary

For documentation and workflow normalization tasks, do not modify runtime surfaces:

- `src/backend/zuno/`
- `apps/web/`
- `apps/desktop/`
- `infra/`

If verification would require a forbidden runtime change, stop and return evidence.
