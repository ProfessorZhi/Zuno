# Documentation Index

`docs/` is the formal documentation root for Zuno.

The organizing rule is:

```text
keep current truth, execution phases, stable specs, support workflow, and history separate
```

## Sections

- [architecture/](./architecture/README.md)
  - current architecture truth, active phases, stable specs, decisions, history
- [development/](./development/README.md)
  - maintainer workflow, publish boundary, demo runbooks, architecture-doc maintenance
- [reference/](./reference/)
  - stable reference material that is not the active execution path
- [prototypes/](./prototypes/)
  - experiments and non-current materials safe to keep
- [assets/](./assets/)
  - documentation assets

Relative path hints:

- `./architecture/README.md`
- `./development/architecture-doc-maintenance-workflow.md`
- `./development/public-demo-evidence.md`
- `./development/public-demo-runbook.md`
- `./development/public-demo-acceptance.md`
- `./development/README.md`
- `./development/github-publish-boundary.md`

## First-Read Path

If you are reading the project for the first time, use this order:

1. [README.md](../README.md)
2. [docs/architecture/README.md](./architecture/README.md)
3. [docs/architecture/current-architecture.md](./architecture/current-architecture.md)
4. [docs/architecture/plans/stable-baseline-recovery-and-runtime-deepening-plan.md](./architecture/plans/stable-baseline-recovery-and-runtime-deepening-plan.md)
5. [docs/architecture/target-architecture.md](./architecture/target-architecture.md)
6. [docs/development/public-demo-evidence.md](./development/public-demo-evidence.md)
7. [docs/development/public-demo-runbook.md](./development/public-demo-runbook.md)
8. [docs/development/public-demo-acceptance.md](./development/public-demo-acceptance.md)

## Maintainer Path

If you are changing structure, runtime, docs, or release surfaces, use:

1. [docs/architecture/phases/README.md](./architecture/phases/README.md)
2. [docs/development/architecture-doc-maintenance-workflow.md](./development/architecture-doc-maintenance-workflow.md)
3. [docs/development/README.md](./development/README.md)
4. [docs/development/github-publish-boundary.md](./development/github-publish-boundary.md)

## Notes

- `docs/architecture/history/` stores older architecture and phase materials that are no longer current truth.
- `docs/development/history/` stores older workflow notes that should not stay on the active maintainer path.
- completed one-off workflow notes should not remain in the default reading order after the underlying task is done.
