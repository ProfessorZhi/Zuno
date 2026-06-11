# Development Docs

This section is for engineering-facing documentation.
It is not part of the first-read public project path.

## Maintainer Reading Order

1. [backend-layering-guidelines.md](./backend-layering-guidelines.md)
2. [github-publish-boundary.md](./github-publish-boundary.md)
3. [public-release-checklist.md](./public-release-checklist.md)
4. [public-release-staging-plan.md](./public-release-staging-plan.md)
5. [docs-and-readme-signoff.md](./docs-and-readme-signoff.md)
6. [docs-and-readme-prestage.md](./docs-and-readme-prestage.md)
7. [docs-and-readme-ready.md](./docs-and-readme-ready.md)
8. [public-demo-evidence.md](./public-demo-evidence.md)
9. [public-demo-runbook.md](./public-demo-runbook.md)
10. [public-demo-acceptance.md](./public-demo-acceptance.md)
11. [zuno-upgrade-roadmap.md](./zuno-upgrade-roadmap.md)
12. [install_minio_win.md](./install_minio_win.md)

## Maintainer Scope

Use this section when you are changing repo structure, release surface, publish boundary, or engineering workflow docs.

If you are reading Zuno for the first time, go back to:

1. [README.md](../../README.md)
2. [docs/architecture/README.md](../architecture/README.md)
3. [public-demo-evidence.md](./public-demo-evidence.md)
4. [public-demo-runbook.md](./public-demo-runbook.md)
5. [public-demo-acceptance.md](./public-demo-acceptance.md)

## What Lives Here

- backend layering rules
- publish and open-source boundary rules
- public release checklist
- public release staging plan
- docs and README signoff
- docs and README prestage checklist
- docs and README readiness check
- public release commit order
- public release staging commands
- public release group preview
- public release stage dry run preview
- docs and README readiness verifier
- automated public release audit
- repository structure verification
- public demo evidence
- public demo reproduction guidance
- public demo acceptance gate
- public demo runtime smoke verification
- strict-grounded public demo smoke verification
- upgrade and migration notes
- local development environment guidance

## Current Architecture Direction

The backend is expected to evolve under a layered structure:

- control layer
- service layer
- DAO layer
- infrastructure layer

And the long-term engineering direction remains:

- multi-agent product growth
- microservice and cloud-native readiness
- future integration with non-Python business backends such as Java

For retrieval governance and architecture-upgrade planning, start from:

- `docs/architecture/specs/enterprise-retrieval-governance.md`
- `docs/architecture/plans/retrieval-governance-upgrade-plan.md`

## Documentation Sync Rule

After every major architecture or runtime update, review `docs/architecture/` again.

At minimum, check:

- which architecture problems have now been solved
- which unresolved items should be removed from the docs
- whether current phase status is still accurate
- whether architecture specs, plans, README, and development docs still match

The goal is:

```text
do not let architecture docs lag behind the actual project state
```
