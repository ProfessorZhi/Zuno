# Zuno

Zuno 是一个本地优先、短小精悍但工程完整的 **Lean Complete Agentic GraphRAG Product**。

用户可以配置模型、创建 Workspace、上传资料、解析和索引文档，通过 AgentChat 使用标准检索或深度检索，由 Single Controller Agent 完成规划、混合检索、GraphRAG、证据整理、claim-level citation、回答生成、trace、成本统计和反馈。

## 当前定位

近期目标不是大规模分布式企业平台，而是一条真实可运行、可演示、可评测、可恢复的企业知识库 Agent 产品链路：

```text
配置模型
-> 创建 Workspace
-> 上传文档
-> Parse / Index
-> AgentChat 提问
-> ContextPack
-> RetrievalPlan
-> BM25 + Vector + optional Graph
-> EvidenceBundle
-> Claim-level Citation
-> Grounded Answer / Artifact
-> Trace / Cost / Eval
-> Feedback
-> Restart Recovery
```

## 当前仓库形态

Zuno 当前是**前后端分离的 monorepo**，不是传统单体前端直连数据库，也不是默认拆成大量微服务的分布式平台。

```text
apps/web/        Vue 3 + Vite 前端，消费服务端 Product API、Projection、SSE 和 AvailableAction
apps/desktop/    Electron 桌面壳，承载桌面桥接和本地产品入口
src/backend/zuno FastAPI / Python 后端，拥有 Product API、Agent、Knowledge、Memory、Capability、Tool、Security、Observability 和 Platform 运行逻辑
infra/db/        Alembic 迁移和 PostgreSQL schema 管理
infra/docker/    本地开发依赖：PostgreSQL、RabbitMQ、MinIO、Redis、Elasticsearch、Milvus、Neo4j 等
tools/           Eval、Benchmark、Verifier、脚本和 CLI 辅助工具
docs/            正式架构、模块、状态、决策和 evidence
.agent/          本地 Agent 工作流、Program、Reference 和任务卡
```

运行边界：

- 前端只消费后端 Product API / Projection / SSE，不拥有 AgentRun、KnowledgeVersion、Approval、Tool Effect、Evidence、Memory、Eval 或 Artifact 的领域事实。
- 桌面端通过 Desktop bridge 和后端 API 进入产品能力，不直接写数据库、Queue、Object Store、索引、模型 Provider 或 Secret Store。
- 后端当前可以用一个镜像承担 `backend-api`、controller、worker 等多个角色；角色边界由 Owner、Contract、状态机和测试证明，不靠微服务数量证明成熟度。
- PostgreSQL 是领域事实主存；MinIO/Object Store、RabbitMQ、LangGraph Checkpointer、Elasticsearch、Milvus、Neo4j、Redis 等属于可替换基础设施或可重建读模型。
- `docs/status/production-readiness.md` 和 `docs/evidence/` 才能证明 Current / Gap / Measurement / Production Readiness；模块文档描述 Target，不自动证明 Current。

## 文档入口

- [总架构](./docs/architecture/architecture.md)
- [架构十类图 HTML 展示](./docs/architecture/architecture.html)
- [十一逻辑模块设计](./docs/modules/README.md)
- [Production Readiness 状态](./docs/status/production-readiness.md)
- [02 Input / Document Ingestion](./docs/modules/02-input-document-ingestion.md)
- [03 Knowledge / Agentic GraphRAG](./docs/modules/03-knowledge-agentic-graphrag.md)
- [05 Memory & Context](./docs/modules/05-memory-context.md)
- [06 Agent Core / Planning & Control](./docs/modules/06-agent-core-planning-control.md)
- [07 Capability / Skill](./docs/modules/07-capability-skill.md)
- [10 Observability & Eval](./docs/modules/10-observability-eval.md)
- [架构决策](./docs/decisions/README.md)
- [Repository Ownership Matrix](./docs/governance/repo-ownership-matrix.md)
- [文档总入口](./docs/README.md)
- [公开证据入口](./docs/evidence/public-demo.md)
- [历史归档入口](./docs/history/programs/README.md)

`docs/architecture/` 只保留：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## Program 入口

- 当前 program 前台：`.agent/programs/`
- 当前 active program：`zuno-canonical-architecture-runtime-realization-v1`
- 当前 phase：`PHASE22`
- 最近完成归档：`docs/history/programs/zuno-real-unified-runtime-cutover-v1/`
- 历史生产完成归档：`docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`
- 历史 runtime-first 归档：`docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`
- 历史 master architecture 归档：`docs/history/programs/zuno-master-architecture-implementation-v1/`

## Agent 协作入口

Zuno 主仓库目录保持为最终集成仓库；临时 worker worktree 放在：

```text
F:\agent_project\Zuno-worktrees\
```

每个 worker 使用独立 worktree 和 `codex/` branch。Claude Code worker 优先处理简单、大量、重复、下载、环境探测、日志整理和低风险候选补丁；Codex coordinator 负责复杂架构判断、根因定位、安全 / 并发 / 恢复 / 幂等语义、review、合并、最终验证和 push。

worker 的 worktree、branch、commit、evidence、PR 标题和 PR 描述必须带 `agent + model + worker` 身份标签。Claude Code session 用 `stream-json --verbose` 创建并记录真实 `session_id`；同一 PR / handoff 的后续修复优先用 `--resume <session_id>` 复用。时间和成本按单个 agent 的一次 PR / handoff 统计，不按一轮对话统计；API token 估算成本和 provider 平台额度扣减分开记录。

Codex coordinator 必须审查 worker diff、evidence、验证结果、风险和成本账，并按 100 分 scorecard 打分后决定 accept、request changes、reject 或 block。worker PR 只是候选贡献；最终合并、集成验证和 push 只由 coordinator 收口。详细规则见 `.agent/references/workflow.md`、`.agent/references/command-catalog.md` 和 `.agent/templates/phase-closure-report.md`。

## 本地验证入口

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py
```

后端本地入口：

```powershell
uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860
```

前端本地入口：

```powershell
npm run frontend:dev
npm run frontend:lint
npm run frontend:build
```

桌面本地入口：

```powershell
npm run desktop:dev
```

基础设施和迁移入口：

```powershell
docker compose -f infra/docker/docker-compose.yml up -d
python -m alembic -c infra/db/alembic.ini upgrade head
```

## 六个运行域

1. Product & API
2. Input & Knowledge
3. Agent Core
4. Capability & Tool
5. Governance & Observability
6. Local Infrastructure

后端主路径位于 `src/backend/zuno`，按 Product/API、Agent、Memory、Capability、Knowledge 和 Platform owner 分层维护。

## 当前质量声明

Evidence-span Agentic GraphRAG 的本地实现基线已经存在，但 fixed EnterpriseRAG measured pass 仍未完成。

最近完成的 `zuno-unified-agent-runtime-closure-v1` 已把 unified runtime implementation baseline 归档为 `implementation_complete_measurement_blocked`。PHASE13 sample-8 运行产出 `blocked_not_measured`，原因是本地 embedding profile runner 未配置；sample-80 仍因仓库没有 tracked fixed 80-case set 而 blocked。

```text
implementation available
measurement blocked
quality not yet proven
```

不得把 doc-level recall、prepared benchmark 或 incomplete run 写成 strict citation / answer correctness 已完成。Agentic GraphRAG 是否真正完成，仍以 fixed benchmark 和 release gate 为准。
