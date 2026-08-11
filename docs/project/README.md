# Zuno Project Knowledge Canonical Set

`docs/project/` 是项目知识唯一正式入口。它把历史事实、跨领域架构和专题设计分开；Target 不能证明 Current，旧架构不能与新架构并列成为 Canonical Source。

## 三层入口

| 层 | 回答的问题 | Canonical 内容 |
|---|---|---|
| `facts/` | What actually happened? | 背景、团队、开发、交付、技术现实和 UNKNOWN |
| `architecture/` | How do the layers fit? | 总体集成、跨层关系、四个展示文件 |
| 专题目录 | How does one concern work? | Product、Domain、Agents、Knowledge、Services、Data、Security、Eval、Deployment |

## New Architecture Taxonomy

```text
docs/project/
├─ facts/
├─ architecture/
│  ├─ README.md
│  ├─ architecture.md
│  ├─ architecture-views.md
│  └─ architecture.html
├─ product/product-architecture.md
├─ domain/legal-domain-model.md
├─ domain/domain-state-lifecycle.md
├─ agents/agent-platform.md
├─ agents/multi-agent-runtime.md
├─ knowledge/knowledge-evidence-architecture.md
├─ services/service-architecture.md
├─ data/data-ownership-and-recovery.md
├─ security/security-architecture.md
├─ eval/legal-eval-and-benchmark.md
└─ deployment/microservice-deployment.md
```

每份专题文档必须声明 `canonical_question`、`owner`、`replaces`、Current/Target/Gap/Future 和验证入口。专题文档只拥有自己的事实；跨域关系由 `architecture/architecture.md` 组合。逻辑能力、服务、进程、容器、数据库和团队不是一一对应关系。

## Reading paths

```text
Product:  docs/README.md → architecture/architecture.md → product → domain
Agent:    architecture → domain → agents → services → data/security
Knowledge: domain → knowledge → agents → eval
Backend:  domain → services → data → security → deployment
SRE:      services → data → deployment → eval
```

## Current / Target / History

- Current 只由代码、Migration、Test、Trace、Eval、`docs/status/` 和 `docs/evidence/` 证明。
- Target 由 accepted ADR、专题 Canonical 文档和共享 Contract 定义；Python-only/Microservice 是本轮 Target Constraint。
- Hypothesis 必须通过 Benchmark、Spike、Security Evidence 或 User Validation 关闭；没有关闭前不能提升为 Current。
- Future 只记录长期可选方向，例如 Persistent Agent Team、物理数据库拆分、Kubernetes 或 Event Sourcing；它们不是本轮服务成立的前置条件。
- History 保留旧 11 Module 架构的摘要和可追溯迁移材料；旧模块不再是新 Target 的事实源。

入口和服务边界决策见：

- [`ADR-0008`](../decisions/0008-legal-domain-kernel-and-host-boundary.md)
- [`ADR-0009`](../decisions/0009-python-only-backend.md)
- [`ADR-0010`](../decisions/0010-microservice-target-and-service-boundaries.md)
- [`ADR-0011`](../decisions/0011-architecture-document-taxonomy.md)

项目事实目录仍是历史真相源；红蓝过程记录在 `project-red-blue/`，不覆盖正式事实。
