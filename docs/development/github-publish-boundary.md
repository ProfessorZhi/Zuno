# GitHub Publish Boundary

This document defines what belongs in the public GitHub project and what must stay local.

## Public Scope

The public repository should contain the project itself:

- application source code
- public-facing documentation
- published agent-workspace guidance under `AGENTS.md` and `.agent/`
- Docker and launcher assets needed to run the project
- tests that verify product behavior and architecture guards
- evaluation code, schemas, and reusable datasets that are safe to publish

## Local Or Private Scope

The following content is local-only and must not be published:

- `.local/`
- `docs/superpowers/`
- `apps/web/AGENTS.md`
- local config overrides such as `infra/docker/docker_config.local.yaml`
- local backend overrides such as `.local/config/zuno/config.local.yaml`
- secrets, tokens, keys, and personal credentials
- one-off evaluation run outputs under `.local/evals/zuno/rag_eval/runs/`
- large local corpora or scratch corpora under `.local/evals/zuno/rag_eval/corpus/`
- Playwright, pytest, and desktop runtime leftovers

## Release Rule

Before pushing to GitHub, treat the publishable project as:

1. product code
2. public docs
3. reproducible infra
4. reusable tests

Everything else must justify why it belongs in the public repo.

## Current Guardrails

The repository already enforces part of this boundary through:

- `.gitignore`
- `tests/test_zuno_runtime_chain_guard.py`
- `tests/test_zuno_public_entrypoints.py`
- `tests/test_publish_boundary.py`

## Practical Checklist

Before a public push:

1. confirm no private workflow files or secrets are staged
2. confirm no local config or secret files are staged
3. confirm no evaluation run artifacts are staged
4. confirm README and docs reflect the public project, not local operator notes
5. review `git status --short` before staging

For the full pre-push checklist, see [public-release-checklist.md](public-release-checklist.md).
