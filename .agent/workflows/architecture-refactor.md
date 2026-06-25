# Architecture Refactor Workflow

## Trigger

Use for architecture replacement, boundary changes, or broad refactor planning.

## Steps

1. Read formal docs first: current, target, roadmap.
2. Read `.agent/architecture/near-term/README.md`.
3. Read `.agent/architecture/decisions/`.
4. Keep future architecture out of near-term implementation unless the user
   explicitly opens a future-direction program.
5. Update docs, `.agent`, tests, and verification scripts in one change set.

## Stop Conditions

- The refactor requires runtime behavior changes outside the requested scope.
- The replacement would erase history or evidence.
