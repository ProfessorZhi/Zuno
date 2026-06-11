# Docs And Readme Signoff

This note records the current acceptance decision for the `docs_and_readme` release group.

## Current Decision

`docs_and_readme` can be treated as a valid first public commit group.

## Included Paths

Current preview:

- `README.md`
- `docs/README.md`
- `docs/architecture/`
- `docs/development/README.md`
- `docs/development/backend-layering-guidelines.md`
- `docs/development/docs-and-readme-prestage.md`
- `docs/development/docs-and-readme-ready.md`
- `docs/development/docs-and-readme-signoff.md`
- `docs/development/github-publish-boundary.md`
- `docs/development/public-demo-acceptance.md`
- `docs/development/public-demo-evidence.md`
- `docs/development/public-demo-runbook.md`
- `docs/development/public-release-checklist.md`
- `docs/development/public-release-staging-plan.md`

## Why This Group Is Acceptable

These files now do four public-facing jobs cleanly:

1. explain the project to external readers
2. document the architecture direction and phased implementation status
3. explain why GraphRAG and contract-review domain modeling matter
4. define the GitHub publish boundary for public release

## Boundary Checks Already Satisfied

- public docs no longer present `docs/superpowers/` as a public documentation entrypoint
- public docs no longer link public evidence directly to ignored local eval-run directories
- historical local-only workflow inventory such as `superpowers-legacy-migration-inventory.md` is not part of the public docs entry surface
- excluded local content remains:
  - `docs/superpowers/`
  - `src/frontend/AGENTS.md`
  - `.agent/`
  - `.agentmd`
  - `.local/`

## Recommended Pre-Stage Check

Before staging this group:

```powershell
python tools/scripts/preview_public_release_group.py docs_and_readme
python tools/scripts/preview_public_release_group.py docs_and_readme --stat
python tools/scripts/verify_docs_and_readme_ready.py
python tools/scripts/audit_public_release.py
```

For the full first-group staging flow, see [docs-and-readme-prestage.md](./docs-and-readme-prestage.md).
