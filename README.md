# Zuno

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121-009688?logo=fastapi&logoColor=white)
![Vue](https://img.shields.io/badge/Vue-3-42B883?logo=vuedotjs&logoColor=white)
![Electron](https://img.shields.io/badge/Electron-32-47848F?logo=electron&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

Zuno 是一个本地优先的 Agent Workspace。它把 LangGraph 编排、RAG / GraphRAG、MCP、工具调用、知识库、桌面运行时和评测链路放进同一个项目里，目标不是只做一个聊天界面，而是提供一套可扩展的 Agent 工程底座。

当前这条主线重点落在两个方向：

- 面向真实工程使用的本地 Agent 工作台
- 面向合同审查场景的 Domain Pack + GraphRAG 能力验证

## Why Zuno

Zuno 不是把“模型 + 前端”拼起来的演示项目。它更强调：

- `Local-first runtime`：支持 Web、桌面端、本地工具、Docker 基础设施和本地持久化。
- `Explicit orchestration`：核心问答链路逐步收口到 LangGraph，而不是隐式堆在单个 agent 文件里。
- `Domain-aware retrieval`：RAG、GraphRAG、领域 schema、结构化抽取和引用验证可以一起工作。
- `Evaluatable engineering`：内置本地 embedding、离线评测、stackless compare matrix、合同域题集和多指标报告。

## Key Capabilities

- 多模型对话与工具调用
- MCP 服务接入与技能扩展
- 知识库检索、向量索引、图检索与混合检索
- 合同审查 Domain Pack、结构化 GraphRAG、引用验证
- Web 工作台与 Electron 桌面端
- Docker Compose 一键启动本地基础设施
- 本地评测链：embedding、rerank、RAG / GraphRAG 对比与报告输出

## Architecture Snapshot

Zuno 当前的核心架构方向是：

```text
Domain Pack
  -> LangGraph Runtime
  -> Retrieval Orchestrator
  -> Vector + Graph Hybrid Retrieval
  -> Answer + Citation
  -> Evaluation + Cost Control
```

同时，后端工程结构正在朝更现代的分层架构收口：

```text
Frontend
  -> Backend Control Layer
  -> Backend Service Layer
  -> Backend DAO Layer
  -> Infrastructure Layer
```

## Current Build Status

- `Phase 1`: runtime closure and runnable recovery completed
- `Phase 2`: repository structure governance completed
- `Phase 3`: docs and public presentation hardening completed
- `Phase 4`: layered backend boundary hardening completed
- `Phase 5`: LangGraph + GraphRAG mainline deepening completed
- `Phase 6`: evaluation and evidence-chain hardening completed
- Current serial focus: `Phase 7` interview-facing total cleanup

这不是为了“看起来整齐”，而是为了保留后续三条主线的演进空间：

- 多 agent 功能开发
- 微服务与云原生部署演进
- 接入 Java 等非 Python 业务后端

当前已经形成的重点模块包括：

- `src/backend/zuno/core/graphs/`：Domain QA 图与状态编排
- `src/backend/zuno/services/domain_pack/`：Domain Pack 加载、校验、注册
- `src/backend/zuno/services/graphrag/`：抽取、图存储、图检索、混合检索
- `src/backend/agentchat/evals/rag_eval/`：本地 embedding 评测链、compare matrix、指标汇总
- `src/backend/agentchat/evals/contract_review_eval/`：合同审查评测资产

更完整的架构文档见 [docs/architecture/README.md](./docs/architecture/README.md)。

## Repository Layout

```text
.
├─ apps/
│  └─ desktop/                  # Electron desktop app
├─ docs/
│  ├─ architecture/             # Current architecture, plans, decisions
│  ├─ development/              # Engineering and environment docs
│  ├─ reference/                # Stable reference docs
│  ├─ assets/                   # Documentation assets
│  └─ prototypes/               # Experimental materials safe to publish
├─ infra/
│  └─ docker/                   # Dockerfiles, compose stacks, nginx config
├─ src/
│  ├─ backend/                  # FastAPI, agent runtime, RAG, GraphRAG, evals
│  └─ frontend/                 # Vue web workspace
├─ tests/                       # Repo-level verification
└─ tools/                       # Scripts, launchers, migrations, local maintenance tooling
```

本地临时资产、评测运行残留、Agent 工作流资料不会进入公开仓库主结构：

- `.local/`
- `.agent/`
- `.agentmd`
- `docs/superpowers/`
- `src/frontend/AGENTS.md`

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

停止但保留数据：

```powershell
docker compose -f infra/docker/docker-compose.yml down
```

重置容器与卷：

```powershell
docker compose -f infra/docker/docker-compose.yml down -v
```

更多 Docker 说明见 [infra/docker/README.md](./infra/docker/README.md)。

### 3. Run In Development Mode

后端：

```powershell
pip install -r requirements.txt
cd src\backend
uvicorn zuno.main:app --host 0.0.0.0 --port 7860
```

前端：

```powershell
cd src\frontend
npm install
npm run dev -- --host 127.0.0.1 --port 8090
```

桌面端：

```powershell
cd apps\desktop
npm install
npm start
```

## Local Evaluation And Contract Review

Zuno 已经内置本地评测链，重点支持：

- 本地 embedding 预检与评测启动
- RAG / GraphRAG 对比 profile
- 五项以上检索指标
- 合同审查领域题集、图关系题集与报告输出

关键目录：

- `src/backend/agentchat/evals/rag_eval/`
- `src/backend/agentchat/evals/contract_review_eval/`

关键文档：

- [docs/architecture/plans/rag-local-eval-scheme.md](./docs/architecture/plans/rag-local-eval-scheme.md)
- [docs/architecture/specs/domain-pack-langgraph-graphrag-architecture.md](./docs/architecture/specs/domain-pack-langgraph-graphrag-architecture.md)
- [docs/development/public-demo-runbook.md](./docs/development/public-demo-runbook.md)
- [docs/development/public-demo-acceptance.md](./docs/development/public-demo-acceptance.md)

如果你关心的是“GraphRAG 和领域建模到底值不值得做”，Zuno 当前这套合同审查评测链就是专门为回答这个问题而设计的。

## Public Demo Evidence

The strongest public proof currently committed in this repo is:

### 1. Generic graph-relation benchmark

Reference:
- [docs/development/public-demo-evidence.md](./docs/development/public-demo-evidence.md)
- [docs/development/public-demo-acceptance.md](./docs/development/public-demo-acceptance.md)

Key result:
- `baseline_rag`: Recall@5 `0.1167`, MRR@5 `0.2000`, Citation Accuracy `0.1000`
- `rag_graph_chunk_backed`: Recall@5 `0.3167`, MRR@5 `0.4000`, Citation Accuracy `0.1667`

Meaning:
- on relation-heavy questions, GraphRAG already beats baseline retrieval

### 2. Contract-review scaled domain benchmark

Reference:
- [docs/development/public-demo-evidence.md](./docs/development/public-demo-evidence.md)
- [docs/development/public-demo-acceptance.md](./docs/development/public-demo-acceptance.md)

Key result:
- `baseline_rag`: Recall@5 `0.3333`, MRR@5 `0.1486`, NDCG@5 `0.1931`
- `rag_graph_chunk_backed`: Recall@5 `1.0000`, MRR@5 `0.9583`, NDCG@5 `0.9692`

Meaning:
- once the contract corpus gets larger and noisier, domain modeling plus GraphRAG becomes materially more valuable than baseline RAG

### 3. Why this matters

These two benchmarks together support the core architecture thesis of Zuno:

- GraphRAG is not included as a decorative add-on
- domain modeling becomes more valuable when the dataset has more distractors and relation-heavy questions
- the local evaluation chain is strong enough to prove this without requiring a remote embedding dependency

## Why GraphRAG For Contract Review

Contract review is not just a "find one relevant paragraph" problem.
Once the corpus gets larger, three things get harder at the same time:

1. the same legal concept can appear in multiple contracts with slightly different wording
2. the useful answer often depends on relations between clause, party, obligation, trigger, and regulation
3. generic vector retrieval starts pulling many locally similar but structurally wrong distractors

That is why Zuno treats contract review as a domain-modeling problem instead of a generic chunk-search problem.

The practical takeaway from the committed benchmarks is:

- with small and simple corpora, baseline RAG can look "good enough"
- with larger and noisier corpora, typed extraction plus GraphRAG becomes much more valuable
- the useful unit is no longer only "which chunk is similar", but also "which contract entity and relation path is actually relevant"

In Zuno, that is exactly what the `contract_review` Domain Pack is meant to prove.

## Launchers

Windows 快捷启动入口在 [tools/launchers/windows/README.md](./tools/launchers/windows/README.md)。

常用命令：

```powershell
.\tools\launchers\windows\Zuno-Web-Start.cmd
.\tools\launchers\windows\Zuno-Web-Stop.cmd
.\tools\launchers\windows\Zuno-Desktop-Start.cmd
.\tools\launchers\windows\Zuno-Desktop-Stop.cmd
```

## Documentation

First-time readers start here:

首次阅读：

- [Architecture Index](./docs/architecture/README.md)
- [Current Phase Audit](./docs/architecture/plans/current-phase-audit.md)
- [Public Demo Evidence](./docs/development/public-demo-evidence.md)
- [Public Demo Runbook](./docs/development/public-demo-runbook.md)
- [Public Demo Acceptance](./docs/development/public-demo-acceptance.md)
- [Docs Index](./docs/README.md)

架构与治理：

- [Enterprise Retrieval Governance](./docs/architecture/specs/enterprise-retrieval-governance.md)
- [Retrieval Governance Upgrade Plan](./docs/architecture/plans/retrieval-governance-upgrade-plan.md)

运行与验证：

- `python tools/scripts/verify_public_demo_runtime.py` for the low-cost contract-review end-to-end smoke path
- `python tools/scripts/verify_public_demo_strict_grounding.py` for the low-cost strict-grounded conservative-failure smoke path
- [Docker Runtime Guide](./infra/docker/README.md)
- [Launchers Guide](./tools/launchers/windows/README.md)

Maintainer-only release workflow:

- [Development Docs](./docs/development/README.md)
- [GitHub Publish Boundary](./docs/development/github-publish-boundary.md)
- [Public Release Checklist](./docs/development/public-release-checklist.md)
- [Public Release Staging Plan](./docs/development/public-release-staging-plan.md)

## Verification

前端：

```powershell
cd src\frontend
npm run lint
npm run build
```

仓库级回归：

```powershell
python tools/scripts/verify_repo_structure.py
pytest tests/test_repo_structure_consistency.py
pytest tests/test_publish_boundary.py
pytest tests/test_zuno_runtime_chain_guard.py
pytest tests/test_zuno_public_entrypoints.py
```

Docker 配置检查：

```powershell
docker compose -f infra/docker/docker-compose.yml config
```

## Project Status

First-time readers should stop at the public path below and skip release staging, checklist, and publish-boundary docs on the first pass.

Zuno 当前已经完成 `Phase 1-6`，主运行时、GraphRAG 动态更新、普通 / 增强两档检索、本地 embedding、本地评测与合同审查 Domain Pack 主链已经形成可验证闭环；当前串行主线进入 `Phase 7`，开始做面试前总收口。

如果你第一次看这个项目，建议直接按这条最短路径读：
1. `README.md`
2. `docs/architecture/README.md`
3. `docs/development/public-demo-evidence.md`
4. `docs/development/public-demo-runbook.md`
5. `docs/development/public-demo-acceptance.md`

## Phase 7 final interview path

对外讲解时，优先按这条最短路径走：

1. `README.md`
2. `docs/architecture/README.md`
3. `docs/architecture/plans/current-phase-audit.md`
4. `docs/development/public-demo-evidence.md`
5. `docs/development/public-demo-runbook.md`
6. `docs/development/public-demo-acceptance.md`

最终最小统一验证入口：

- `python tools/scripts/verify_phase7_readiness.py`

已经完成或相对稳定的部分：

- LangGraph + Domain Pack + GraphRAG 主线
- 合同审查领域评测与本地 embedding 评测
- `agentchat -> zuno` 的运行面收口（`src/backend/zuno` direct import 已清零，主入口与最小测试集已打通）

当前 `Phase 7` 需要继续收口的部分：

- 最终 README / docs / architecture 讲解路径统一
- 最终 smoke / publish boundary / structure verifier 统一
- 更完整的演示资产与对外案例

## License

[MIT](./LICENSE)
