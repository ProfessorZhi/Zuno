# Development Docs

This section is for engineering-facing and maintainer-facing documentation.

It is not the first-read public explanation path.

## Current Maintainer Path

1. [Architecture Doc Maintenance Workflow](architecture-doc-maintenance-workflow.md)
2. [backend-layering-guidelines.md](backend-layering-guidelines.md)
3. [github-publish-boundary.md](github-publish-boundary.md)
4. [public-demo-evidence.md](public-demo-evidence.md)
5. [public-demo-runbook.md](public-demo-runbook.md)
6. [public-demo-acceptance.md](public-demo-acceptance.md)
7. [public-release-checklist.md](public-release-checklist.md)
8. [public-release-staging-plan.md](public-release-staging-plan.md)
9. [install_minio_win.md](install_minio_win.md)

## What Lives Here

- architecture-doc maintenance workflow
- backend layering rules
- publish and open-source boundary rules
- public demo evidence and reproduction guidance
- public demo acceptance gate
- release and staging notes that are still operational
- local development environment guidance

## What No Longer Lives On The Main Path

Completed workflow temperature docs have been downgraded to:

- [development/history/README.md](./history/README.md)

This includes one-off:

- prestage notes
- ready-check notes
- signoff notes
- older upgrade roadmaps that no longer define the current architecture program

## Current Sync Rule

After any significant architecture or runtime change, review:

1. [README.md](../../README.md)
2. [docs/architecture/README.md](../architecture/README.md)
3. [docs/architecture/current-architecture.md](../architecture/current-architecture.md)
4. [docs/architecture/target-architecture.md](../architecture/target-architecture.md)
5. the active file under [docs/architecture/phases/](../architecture/phases/)
6. this index

Relative path hints:

- `../../README.md`
- `../architecture/README.md`

The goal is to keep maintainer workflow docs aligned with the current repo rather than the last completed cleanup operation.
