# Docs And Readme Ready Check

This note records the operational readiness check for the `docs_and_readme` group.

## Ready Condition

The group is considered ready for real staging when all of the following are true:

1. `preview_public_release_group.py docs_and_readme` returns the expected 14 paths
2. `preview_public_release_stage_dry_run.py docs_and_readme` returns the same 14 paths
3. `audit_public_release.py` passes
4. excluded local paths do not appear:
   - `docs/superpowers/`
   - `apps/web/AGENTS.md`

## Single Command

```powershell
python tools/scripts/verify_docs_and_readme_ready.py
```

## Current Expected Paths

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
