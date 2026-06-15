# Zuno

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121-009688?logo=fastapi&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3-42B883?logo=vuedotjs&logoColor=white)
![Electron](https://img.shields.io/badge/Electron-32-47848F?logo=electron&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

Zuno 是一个本地优先的 Agent Workspace。它把 LangGraph 编排、RAG / GraphRAG、MCP、工具调用、知识库、桌面运行时和评测链路放进同一个项目里，目标是做一套可扩展的 Agent 工程底座，而不是只做聊天界面。

## Current Status

当前仓库的执行真相不是“继续做 `services/api` 迁移”，而是：

```text
先恢复一个稳定可运行版本
  -> 用户亲自体验
  -> 再继续后续架构升级
```

当前 phase 程序见：

- [docs/architecture/phases/README.md](05_TopDown_题库学习/项目/02_项目映射/Zuno/docs/architecture/phases/README.md)

当前恢复与深化计划见：

- [docs/architecture/plans/stable-baseline-recovery-and-runtime-deepening-plan.md](stable-baseline-recovery-and-runtime-deepening-plan.md)

## Repo Reality

仓库当前仍是混合态：

- `apps/web` 与 `apps/desktop` 已经是明确应用入口
- 后端最终希望收口到单一稳定基线，而不是长期维持双根
- 根目录 `services/`、`domain-packs/` 等结构已经出现，但恢复阶段还没有完成
- 一部分现有 Docker、launcher、测试仍引用迁移中的运行面

因此当前最重要的不是继续扩目录，而是先把“哪一套路径才是稳定运行真相”收口清楚。

## Architecture Thesis

Zuno 的核心运行主线仍然是：

```text
Domain Pack
  -> LangGraph Runtime
  -> Retrieval Orchestrator
  -> Vector / BM25 / Graph Retrieval
  -> Answer + Citation
  -> Evaluation + Proof
```

后端工程上采用的长期原则是：

```text
monorepo now, service-ready later
```

也就是先把单仓内的运行边界、分层和验证做稳，再决定是否重开更大规模的目录迁移。

## Key Capabilities

- 多模型对话与工具调用
- MCP 服务接入与技能扩展
- 知识库检索、向量索引、图检索与混合检索
- 合同审查 Domain Pack、结构化 GraphRAG、引用验证
- Web 工作台与 Electron 桌面端
- Docker Compose 本地基础设施
- 本地评测链：embedding、rerank、RAG / GraphRAG 对比与报告输出

## Repository Layout

当前需要优先理解的是“哪些目录已经稳定，哪些还在恢复”：

```text
.
├─ apps/
│  ├─ desktop/                  # Electron desktop shell workspace
│  └─ web/                      # Vue web workspace
├─ docs/
│  ├─ architecture/             # Current truth, phases, specs, history
│  ├─ development/              # Maintainer workflow and runbooks
│  ├─ reference/                # Stable reference material
│  ├─ assets/                   # Documentation assets
│  └─ prototypes/               # Experiments safe to keep outside the front path
├─ infra/
│  ├─ db/                       # Database and migration infra
│  └─ docker/                   # Dockerfiles, compose stacks, nginx config
├─ services/                    # Migration-era service surfaces still present in repo
├─ src/
│  └─ backend/                  # Stable-backend recovery baseline and legacy runtime source
├─ tests/                       # Repo-level verification
└─ tools/                       # Scripts, launchers, evals, maintenance tooling
```

如果你是第一次看这个仓库，不要把 `services/` 理解成“当前迁移已经完成”。它现在更接近恢复阶段必须治理的混合面。

## Quick Start

### 1. Requirements

- Python 3.12
- Node.js 18+
- Docker Desktop or Docker Engine with Compose v2

### 2. Start With Docker

在仓库根目录执行：

```powershell
copy infra\docker\docker_config.example.yaml infra\docker\docker_config.local.yaml
docker compose -f infra/docker/docker-compose.yml up --build -d
```

启动后可访问：

- Web UI: [http://127.0.0.1:8090](http://127.0.0.1:8090)
- Backend health: [http://127.0.0.1:7860/health](http://127.0.0.1:7860/health)
- OpenAPI docs: [http://127.0.0.1:7860/docs](http://127.0.0.1:7860/docs)

说明：

- 当前 Docker 栈仍通过仓库里的迁移中运行面启动
- `Phase 0` 的目标之一就是把这条启动链收口成稳定、单一、可解释的基线

更多 Docker 说明见 [infra/docker/README.md](05_TopDown_题库学习/项目/02_项目映射/Zuno/infra/docker/README.md)。

### 3. Local App Surfaces

后端恢复期启动：

```powershell
uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860
```

这条命令是当前 `Phase 0` 应优先验证的本地后端启动路径。
如果本地 PostgreSQL 等依赖没有就绪，后端现在会快速失败并明确报出启动依赖问题，而不是长时间卡住。

前端：

```powershell
cd apps\web
npm install
npm run dev -- --host 127.0.0.1 --port 8090
```

桌面端：

```powershell
cd apps\desktop
npm install
npm start
```

Windows 快捷启动入口见 [tools/launchers/windows/README.md](05_TopDown_题库学习/项目/02_项目映射/Zuno/tools/launchers/windows/README.md)。

Windows 上如果你只想做 `Phase 0` 用户检查，也可以直接运行：

```powershell
.\tools\launchers\windows\Zuno-Phase0-Backend-Start.cmd
```

## Local Evaluation And Contract Review

Zuno 已经内置本地评测链，重点支持：

- 本地 embedding 预检与评测启动
- RAG / GraphRAG 对比 profile
- 合同审查领域题集、图关系题集与报告输出

关键目录：

- `tools/evals/zuno/rag_eval/`
- `tools/evals/zuno/contract_review_eval/`

关键文档：

- [docs/architecture/plans/rag-local-eval-scheme.md](rag-local-eval-scheme.md)
- [docs/architecture/specs/domain-pack-langgraph-graphrag-architecture.md](domain-pack-langgraph-graphrag-architecture.md)
- [docs/development/public-demo-runbook.md](public-demo-runbook.md)
- [docs/development/public-demo-acceptance.md](public-demo-acceptance.md)

## Documentation

First-time readers should stop at the public path below and skip release staging, checklist, and publish-boundary docs on the first pass.

First-time readers start here:

首次阅读建议按这条路径：

1. [docs/architecture/README.md](05_TopDown_题库学习/项目/02_项目映射/Zuno/docs/architecture/README.md)
2. [docs/architecture/current-architecture.md](current-architecture.md)
3. [docs/architecture/plans/stable-baseline-recovery-and-runtime-deepening-plan.md](stable-baseline-recovery-and-runtime-deepening-plan.md)
4. [docs/architecture/target-architecture.md](target-architecture.md)
5. [docs/development/public-demo-evidence.md](public-demo-evidence.md)
6. [docs/development/public-demo-runbook.md](public-demo-runbook.md)
7. [docs/development/public-demo-acceptance.md](public-demo-acceptance.md)

Relative path hints:

- `./docs/architecture/README.md`
- `./docs/architecture/current-architecture.md`
- `./docs/architecture/target-architecture.md`
- `./docs/development/public-demo-evidence.md`
- `./docs/development/public-demo-runbook.md`
- `./docs/development/public-demo-acceptance.md`

Maintainer-only release workflow:

维护者路径：

- [docs/README.md](05_TopDown_题库学习/项目/02_项目映射/Zuno/docs/README.md)
- [docs/architecture/phases/README.md](05_TopDown_题库学习/项目/02_项目映射/Zuno/docs/architecture/phases/README.md)
- [docs/development/architecture-doc-maintenance-workflow.md](architecture-doc-maintenance-workflow.md)
- [docs/development/README.md](05_TopDown_题库学习/项目/02_项目映射/Zuno/docs/development/README.md)

## Verification

文档入口校验：

```powershell
python tools/scripts/verify_docs_entrypoints.py
```

前端：

```powershell
cd apps\web
npm run lint
npm run build
```

仓库级校验：

```powershell
pytest tests/test_phase0_runtime_recovery.py
python tools/scripts/verify_repo_structure.py
pytest tests/test_repo_structure_consistency.py
pytest tests/test_publish_boundary.py
```

## License

[MIT](./LICENSE)
