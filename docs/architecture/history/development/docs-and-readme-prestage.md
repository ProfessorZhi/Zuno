# Docs And Readme Prestage Checklist

Use this note immediately before staging the `docs_and_readme` group.

## Intended Scope

This prestage flow is only for the first public docs commit:

- `README.md`
- `docs/README.md`
- `docs/architecture/`
- `docs/development/README.md`
- `docs/development/backend-layering-guidelines.md`
- `docs/development/docs-and-readme-signoff.md`
- `docs/development/docs-and-readme-ready.md`
- `docs/development/github-publish-boundary.md`
- `docs/development/public-demo-acceptance.md`
- `docs/development/public-demo-evidence.md`
- `docs/development/public-demo-runbook.md`
- `docs/development/public-release-checklist.md`
- `docs/development/public-release-staging-plan.md`

## Prestage Commands

Run these in order:

```powershell
python tools/scripts/preview_public_release_group.py docs_and_readme
python tools/scripts/preview_public_release_group.py docs_and_readme --stat
python tools/scripts/preview_public_release_stage_dry_run.py docs_and_readme
python tools/scripts/verify_docs_and_readme_ready.py
python tools/scripts/audit_public_release.py
git add README.md docs/
git diff --cached --stat
```

If `git add --dry-run` cannot run because the current environment blocks `.git/index.lock`, use `preview_public_release_stage_dry_run.py` as the non-index preview step before real staging.

## What To Confirm

Before moving past this group, confirm:

1. the cached diff contains only the docs-and-readme paths above
2. `docs/superpowers/` is not staged
3. `apps/web/AGENTS.md` is not staged
4. public docs do not link to ignored eval-run directories
5. the staged README still reads like a public-facing project entrypoint, not an internal handoff note

## If The Cached Diff Looks Wrong

Do not continue to later groups yet.

Instead:

```powershell
git diff --cached --stat
git diff --cached -- README.md docs/
```

Then compare the cached paths against:

```powershell
python tools/scripts/preview_public_release_group.py docs_and_readme
```

If you want one consolidated go/no-go check before real staging, run:

```powershell
python tools/scripts/verify_docs_and_readme_ready.py
```
