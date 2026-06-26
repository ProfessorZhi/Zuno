# Public Release Checklist

Use this checklist before staging or pushing changes to the public GitHub repository.

## 1. Confirm The Scope

The public push should contain only:

- product source code
- public documentation
- reproducible Docker or launcher assets
- reusable tests and evaluation code

If a file does not clearly fit one of those categories, treat it as suspicious until reviewed.

## 2. Confirm Local-Only Assets Are Excluded

Make sure none of the following are staged:

- `.local/`
- `docs/superpowers/`
- `apps/web/AGENTS.md`
- `infra/docker/docker_config.local.yaml`
- `.local/config/zuno/config.local.yaml`
- secrets, tokens, keys, or personal credentials
- `.local/evals/zuno/rag_eval/runs/`
- `.local/evals/zuno/rag_eval/corpus/`

## 3. Confirm Public Docs Use Public Evidence

Public docs must point to committed evidence pages, not ignored local run outputs.

Check that:

- README links to `docs/development/public-demo-evidence.md`
- demo docs do not link to `.local/evals/zuno/rag_eval/runs/`
- public explanations are written for external readers, not local operator memory

## 4. Confirm The Working Tree Before Staging

Run these checks before staging:

```powershell
python tools/scripts/summarize_public_release_scope.py
python tools/scripts/preview_public_release_group.py docs_and_readme
python tools/scripts/preview_public_release_group.py docs_and_readme --stat
python tools/scripts/preview_public_release_stage_dry_run.py docs_and_readme
python tools/scripts/verify_docs_and_readme_ready.py
python tools/scripts/print_public_release_commit_order.py
python tools/scripts/print_public_release_stage_commands.py
git status --short
git diff --stat
```

If you already staged files, also inspect:

```powershell
git diff --cached --stat
```

## 5. Confirm Guard Tests Pass

Run the publish and runtime guard tests:

```powershell
python tools/scripts/audit_public_release.py
pytest -q tests/test_publish_boundary.py
pytest -q tests/test_zuno_public_entrypoints.py tests/test_zuno_runtime_chain_guard.py
```

## 6. Final Push Decision

Only push when all of the following are true:

- the staged diff matches the intended public project story
- no private-only assets are staged
- public docs link only to publishable evidence
- publish-boundary and runtime-guard tests pass
