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
Phase 0 已完成稳定运行恢复
  -> Phase 1 已完成 LangGraph Runtime 深化
  -> Phase 2 已完成 GraphRAG Mainline Deepening
  -> Phase 2.5 已完成 legacy boundary hardening
  -> Phase 3 已完成 Domain Pack Formalization
  -> 当前收口 Phase 4-6
     - Phase 4: Knowledge Config V2 + Local Eval Strengthening
     - Phase 5: Docs And Public Explanation Sync
     - Phase 6: Agent GraphRAG Pluginization / Future Platform Layer
```

当前 phase 程序见：

- [docs/architecture/phases/README.md](./docs/architecture/phases/README.md)

当前恢复与深化计划见：

- [docs/architecture/plans/stable-baseline-recovery-and-runtime-deepening-plan.md](./docs/architecture/plans/stable-baseline-recovery-and-runtime-deepening-plan.md)

## Repo Reality

仓库当前的边界已经比恢复初期更清楚：

- `apps/web` 与 `apps/desktop` 已经是明确应用入口
- `src/backend/zuno` 是当前唯一后端运行真相
- 当前仓库不存在 active services root；后端运行面只有 `src/backend/zuno`
- 当前 Docker、launcher、测试应统一围绕 `src/backend/zuno`

因此当前最重要的不是继续扩目录，而是在稳定运行真相之上推进后续架构升级。

## Architecture Thesis

Zuno 的核心运行主线仍然是：

```text
Domain Pack
  -> LangGraph Runtime
  -> Retrieval Orchestrator
  -> Local GraphRAG + Vector / BM25 / Graph Retrieval
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
├─ domain-packs/                # Domain knowledge packs and related runtime assets
├─ infra/
│  ├─ db/                       # Database and migration infra
│  └─ docker/                   # Dockerfiles, compose stacks, nginx config
├─ src/
│  └─ backend/                  # Stable-backend recovery baseline and legacy runtime source
├─ tests/                       # Repo-level verification
└─ tools/                       # Scripts, launchers, evals, maintenance tooling
```

如果未来真的要重开 root-level `services/` 微服务化，必须作为新的 architecture phase 重新创建，而不是沿用旧迁移残留。

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

- 当前 Docker 栈已经与 `src/backend/zuno` 运行真相对齐
- 根目录没有第二套后端运行树；当前运行入口只指向 `src/backend/zuno`

更多 Docker 说明见 [infra/docker/README.md](./infra/docker/README.md)。

### 3. Local App Surfaces

后端恢复期启动：

```powershell
uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860
```

这条命令是当前稳定后端的本地启动路径。
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

Windows 快捷启动入口见 [tools/launchers/windows/README.md](./tools/launchers/windows/README.md)。

Windows 上如果你只想做 Phase 0 恢复验收，可以直接运行：

```powershell
.\tools\launchers\windows\Zuno-Phase0-Backend-Start.cmd
```

## Local Evaluation And Contract Review

Zuno 已经内置本地评测链，重点支持：

- 本地 embedding 预检与评测启动
- stackless compare matrix
- retrieval metrics 与 citation metrics
- RAG / Local GraphRAG 对比 profile
- 合同审查领域题集、图关系题集与报告输出

当前 Phase 4 的目标不是“把 GraphRAG 写死成合同功能”，而是证明这条能力链路已经具备平台化边界：

- Knowledge Config V2 可以表达标准索引、图谱索引、默认查询模式、Local GraphRAG 设置、Domain Pack 绑定、eval profile
- Local Eval 可以稳定输出 compare matrix、retrieval metrics、citation metrics、GraphRAG-vs-RAG proof surface
- GraphRAG 当前主线是 `Local GraphRAG`
- `Community GraphRAG` 和 `DRIFT-like Search` 目前只保留 future capability slot，不作为已实现主线

关键目录：

- `tools/evals/zuno/rag_eval/`
- `tools/evals/zuno/contract_review_eval/`

关键文档：

- [docs/architecture/plans/rag-local-eval-scheme.md](./docs/architecture/plans/rag-local-eval-scheme.md)
- [docs/architecture/specs/domain-pack-langgraph-graphrag-architecture.md](./docs/architecture/specs/domain-pack-langgraph-graphrag-architecture.md)
- [docs/development/public-demo-runbook.md](./docs/development/public-demo-runbook.md)
- [docs/development/public-demo-acceptance.md](./docs/development/public-demo-acceptance.md)

## Public Demo Evidence

当前公开 proof surface 统一收口到这三份文档：

- [docs/development/public-demo-evidence.md](./docs/development/public-demo-evidence.md)
- [docs/development/public-demo-runbook.md](./docs/development/public-demo-runbook.md)
- [docs/development/public-demo-acceptance.md](./docs/development/public-demo-acceptance.md)

当前 README 只保留最短结论：

- Generic Graph-Relation Benchmark:
  - `baseline_rag` -> Recall@5 `0.1167`, MRR@5 `0.2000`
  - `rag_graph_chunk_backed` -> Recall@5 `0.3167`, MRR@5 `0.4000`
- Contract-Review Scaled Domain Benchmark:
  - `baseline_rag` -> Recall@5 `0.3333`, MRR@5 `0.1486`, NDCG@5 `0.1931`
  - `rag_graph_chunk_backed` -> Recall@5 `1.0000`, MRR@5 `0.9583`, NDCG@5 `0.9692`

最小验证命令：

```powershell
python tools/scripts/verify_public_demo_docs.py
python tools/scripts/verify_public_demo_runtime.py
python tools/scripts/verify_public_demo_strict_grounding.py
```

## Why GraphRAG For Contract Review

合同审查在这里不是普通 FAQ 检索问题，而是一个 `domain-modeling problem`。

如果只做 generic vector retrieval，系统很容易在大语料里拉回“局部相似但结构错误”的干扰条款。
当合同数量更大、噪声更多时，`contract_review` Domain Pack、typed extraction、Local GraphRAG 和 citation check 会明显更有价值。

一句话收口：

- GraphRAG beats baseline on relation-heavy retrieval
- with larger and noisier corpora, typed extraction plus GraphRAG becomes much more valuable

## Documentation

First-time readers should stop at the public path below and skip release staging, checklist, and publish-boundary docs on the first pass.

First-time readers start here:

首次阅读建议按这条路径：

1. [docs/architecture/README.md](./docs/architecture/README.md)
2. [docs/architecture/current-architecture.md](./docs/architecture/current-architecture.md)
3. [docs/architecture/target-architecture.md](./docs/architecture/target-architecture.md)
4. [docs/architecture/phases/README.md](./docs/architecture/phases/README.md)
5. [docs/development/public-demo-evidence.md](./docs/development/public-demo-evidence.md)
6. [docs/development/public-demo-runbook.md](./docs/development/public-demo-runbook.md)
7. [docs/development/public-demo-acceptance.md](./docs/development/public-demo-acceptance.md)

Relative path hints:

- `./docs/architecture/README.md`
- `./docs/architecture/current-architecture.md`
- `./docs/architecture/target-architecture.md`
- `./docs/architecture/phases/README.md`
- `./docs/development/public-demo-evidence.md`
- `./docs/development/public-demo-runbook.md`
- `./docs/development/public-demo-acceptance.md`

Maintainer-only release workflow:

维护者路径：

- [docs/README.md](./docs/README.md)
- [docs/architecture/phases/README.md](./docs/architecture/phases/README.md)
- [docs/development/architecture-doc-maintenance-workflow.md](./docs/development/architecture-doc-maintenance-workflow.md)
- [docs/development/README.md](./docs/development/README.md)

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
