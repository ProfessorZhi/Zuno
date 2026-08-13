# Current Repository Reality

## Canonical Question

当前 GitHub / 本地仓库实际有什么？

## Evidence Boundary

当前仓库是 `PARTIAL_REPOSITORY_EVIDENCE`，不是完整历史项目。可审计入口包括：

| Surface | Evidence |
|---|---|
| Python/FastAPI | `pyproject.toml`、`src/backend/zuno/main.py` |
| Database/Migrations | `infra/db/`、`src/backend/zuno/platform/` |
| Compose | `infra/docker/` |
| Agent/Memory/Knowledge/Tool | `src/backend/zuno/agent/`、`memory/`、`knowledge/`、`capability/` |
| Tests/Eval | `tests/`、`tools/evals/` |
| Architecture / Status | `docs/project/architecture/`、`docs/project/status/`、`docs/evidence/` |

这些入口证明某阶段仓库表面，不证明历史项目从一开始具备同样内容。
