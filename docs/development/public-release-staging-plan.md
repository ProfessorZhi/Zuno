# Public Release Staging Plan

This plan turns the current working tree into reviewable public release groups instead of one oversized commit.

## Why This Exists

The current project state spans:

- GraphRAG and local evaluation work
- `agentchat -> zuno` runtime convergence
- frontend workspace polish
- README and public demo documentation
- GitHub publish-boundary and guard tests

Those changes should not be staged as one undifferentiated batch.

## Recommended Staging Groups

Use [tools/scripts/summarize_public_release_scope.py](/abs/path/F:/internship-work/resume%26resume%20project/02_projects/Zuno/tools/scripts/summarize_public_release_scope.py) to group the current `git status --short` output.
Use [tools/scripts/preview_public_release_group.py](/abs/path/F:/internship-work/resume%26resume%20project/02_projects/Zuno/tools/scripts/preview_public_release_group.py) to preview the exact currently changed paths for one group before staging it.
Add `--stat` when you also want the group's current diff summary.
Use [tools/scripts/preview_public_release_stage_dry_run.py](/abs/path/F:/internship-work/resume%26resume%20project/02_projects/Zuno/tools/scripts/preview_public_release_stage_dry_run.py) when you want a non-index staging preview in restricted environments.
Use [tools/scripts/verify_docs_and_readme_ready.py](/abs/path/F:/internship-work/resume%26resume%20project/02_projects/Zuno/tools/scripts/verify_docs_and_readme_ready.py) when you want one go/no-go check for the first public docs group.
For the current acceptance state of the first public docs commit, see [docs-and-readme-signoff.md](./docs-and-readme-signoff.md).
For the first group's readiness rule, see [docs-and-readme-ready.md](./docs-and-readme-ready.md).

Recommended group order:

1. `docs_and_readme`
   - public README
   - architecture and development docs
   - public demo evidence and runbook

2. `tests_and_release_guards`
   - publish-boundary tests
   - `zuno` runtime chain guards
   - release audit scripts

3. `infra_and_launch`
   - Docker defaults
   - startup and rebuild scripts

4. `backend_domain_runtime`
   - Domain Pack runtime
   - LangGraph domain routing
   - contract-review domain runtime pieces

5. `backend_rag_graphrag_eval`
   - local embedding and rerank evaluation
   - GraphRAG retrieval and compare matrix
   - contract-review and graph-relation evaluation support

6. `backend_public_entrypoints`
   - `agentchat -> zuno` public runtime surface
   - API, DAO, schema, config, and startup convergence

7. `frontend_workspace`
   - workspace UI and routing changes

8. `excluded_local_only`
   - internal handoff or workflow-facing materials
   - examples: `docs/superpowers/`, `apps/web/AGENTS.md`

## Recommended Commit Boundaries

Use [tools/scripts/print_public_release_commit_order.py](/abs/path/F:/internship-work/resume%26resume%20project/02_projects/Zuno/tools/scripts/print_public_release_commit_order.py) to print the preferred commit order and review boundary for each group.

The practical intent is:

1. ship the public story first
   - `docs_and_readme`

2. ship the safety rails next
   - `tests_and_release_guards`

3. ship reproducible runtime setup
   - `infra_and_launch`

4. keep runtime-domain behavior and GraphRAG evaluation behavior reviewable as separate backend concerns
   - `backend_domain_runtime`
   - `backend_rag_graphrag_eval`

5. keep rename and public entrypoint convergence separate from the evaluation-heavy GraphRAG work
   - `backend_public_entrypoints`

6. keep frontend polish isolated
   - `frontend_workspace`

If a group has to be split further, split by review intent rather than by directory count.

## Suggested Staging Commands

Use [tools/scripts/print_public_release_stage_commands.py](/abs/path/F:/internship-work/resume%26resume%20project/02_projects/Zuno/tools/scripts/print_public_release_stage_commands.py) to print command templates for each staging group.

These are templates, not blind rules:

- use them to stage one reviewable group at a time
- inspect `git diff --cached --stat` after each group
- do not stage paths listed under local-only exclusions

## Manual Review Bucket

Anything reported under `manual_review` needs explicit human judgment before staging.

Do not stage `manual_review` files by default.

Files that are workflow-facing or handoff-facing should stay local instead of entering any public staging group. Current examples:

- `docs/superpowers/`
- `apps/web/AGENTS.md`

## Suggested Command

```powershell
python tools/scripts/summarize_public_release_scope.py
python tools/scripts/preview_public_release_group.py docs_and_readme
python tools/scripts/preview_public_release_group.py docs_and_readme --stat
python tools/scripts/preview_public_release_stage_dry_run.py docs_and_readme
python tools/scripts/verify_docs_and_readme_ready.py
python tools/scripts/print_public_release_commit_order.py
python tools/scripts/print_public_release_stage_commands.py
```

Then stage by group deliberately instead of staging the whole working tree at once.

## Final Rule

This plan does not replace [public-release-checklist.md](./public-release-checklist.md).

Use both:

- `public-release-staging-plan.md` to split the work into reviewable groups
- `public-release-checklist.md` to confirm the final public push is safe
