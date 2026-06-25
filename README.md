# Zuno

Zuno is a local-first Agent Workspace. It combines a Vue web app, an Electron
desktop shell, a FastAPI backend, LangGraph orchestration, RAG / GraphRAG,
tools, MCP integration, and local evaluation into one monorepo.

## Current Status

Current:

- `apps/web` is the Vue web workspace.
- `apps/desktop` is the Electron desktop workspace.
- `src/backend/zuno` is the only active Python backend runtime boundary.
- Phase 0-6 architecture closure remains complete historical truth.
- The active cleanup program is the official GraphRAG alignment program.

Target:

- Keep one stable monorepo baseline.
- Move the front-path GraphRAG language toward GraphRAG Project, Prompt
  Tuning, Query Method, index versions, evidence, and trace metadata.
- Keep Java services, microservices, event workers, and default multi-agent mode
  as future direction only.

Blocked Legacy:

- `domain-packs/`, Domain Pack runtime services, `DomainQAGraph`, and
  `tests/compat/` still have active runtime, eval, or test dependencies.
- They are not the future public mainline, but they must not be deleted before
  Phase 11 proves replacement behavior and import removal.

## Default Reading Path

First-time readers start here:

1. [README.md](./README.md)
2. [docs/architecture/current-architecture.md](./docs/architecture/current-architecture.md)
3. [docs/architecture/target-architecture.md](./docs/architecture/target-architecture.md)
4. [docs/architecture/roadmap.md](./docs/architecture/roadmap.md)
5. [docs/evidence/public-demo.md](./docs/evidence/public-demo.md)

Maintainers and Agents should then read:

- [AGENTS.md](./AGENTS.md)
- [.agent/README.md](./.agent/README.md)
- [.agent/references/current-program.md](./.agent/references/current-program.md)

## Repository Layout

```text
.
├─ apps/
│  ├─ desktop/                  # Electron desktop shell
│  └─ web/                      # Vue web workspace
├─ docs/                        # stable human-facing documentation
│  ├─ architecture/             # current, target, roadmap, decisions, history
│  ├─ development/              # maintainer runbooks
│  ├─ evidence/                 # selected public evidence
│  └─ reference/                # stable reference material
├─ domain-packs/                # Blocked Legacy runtime assets
├─ infra/                       # deployment and environment infrastructure
├─ src/backend/zuno/            # current backend runtime truth
├─ tests/                       # repo-level verification
├─ tools/                       # scripts, launchers, evals, maintenance tooling
├─ .agent/                      # local Agent workflow library
└─ AGENTS.md                    # repository-level Agent entrypoint
```

## Local Run

Backend:

```powershell
uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860
```

Frontend:

```powershell
cd apps\web
npm ci
npm run dev -- --host 127.0.0.1 --port 8090
```

Desktop:

```powershell
cd apps\desktop
npm ci
npm start
```

Docker:

```powershell
copy infra\docker\docker_config.example.yaml infra\docker\docker_config.local.yaml
docker compose -f infra/docker/docker-compose.yml up --build -d
```

## Verification

Focused documentation and repository checks:

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
powershell -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/test_docs_entrypoints.py
pytest -q tests/test_repo_structure_consistency.py
pytest -q tests/test_publish_boundary.py
```

Full test run:

```powershell
pytest -q
```

## License

[MIT](./LICENSE)
