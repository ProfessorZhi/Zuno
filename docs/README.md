# Zuno 文档入口

前台文档默认使用中文，承载当前正式结论。`docs/history/` 只保留经过批准的历史摘要；
已完成 Program 的 raw construction materials 可以在摘要完成、明确授权且 Git commit
可追溯时从 current tree 移除，但未提交内容、未合并提交、Migration、benchmark evidence
和用户文件不得未经明确 disposition 删除。

## 首读路径

- [Zuno 项目知识入口](./project/README.md)：事实、总体架构和专题架构的统一入口。
- [项目事实目录](./project/facts/README.md)：项目背景、团队、开发演进、交付使用和技术现实；未知信息保留为 `UNKNOWN`。
- [总体 Target 架构](./project/architecture/architecture.md)：Product、Domain、Logical Capability、Physical Service/Deployment 的跨层集成、状态、失败、恢复和验证原则。
- [架构图展示配对](./project/architecture/architecture-views.md)：与 `architecture.html` 配套的 Mermaid 图源；二者只负责展示，不拥有独立架构语义。
- [专题架构入口](./project/README.md)：Product、Domain、Agents、Knowledge、Services、Data、Security、Eval、Deployment 的 Canonical Question 与 Owner。
- [Evidence-Driven Retrieval ADR](./decisions/0006-evidence-driven-agentic-graphrag.md)：受控证据检索的 `accepted-target` overlay；不代表 Current 实现。
- [Reuse-first / Provider Boundary ADR](./decisions/0007-reuse-first-provider-boundary.md)：成熟能力优先复用、Zuno 控制面和 Provider 边界。
- [Production Readiness](./status/production-readiness.md)：Current、Gap、Measurement、Blocked 和 Production Readiness 状态事实源。
- [架构决策](./decisions/README.md)：仍影响当前或下一版 Target 的正式 ADR。
- [工程治理](./governance/repo-ownership-matrix.md)：代码 Owner、迁移边界和兼容路径。
- [架构文档写作标准](./governance/architecture-document-writing-standard.md)：总体与专题文档的统一信息架构、Current/Target 边界和验证规则。
- [当前证据](./evidence/README.md)：当前仍有证明价值的 baseline 与 closure evidence。
- [架构面试验证语料](./verification/interview-qa/README.md)：非规范性 QA Corpus，用真实追问压力测试 canonical architecture。
- [历史归档](./history/README.md)：经过批准的历史摘要，不重新解释成当前事实。

## 两条阅读路径

```text
人类理解：architecture.md → 对应 Canonical Question 专题 → Domain / Product / Service 细节
工程实现：architecture.md → Owner 专题 → ADR/Contract → Status/Evidence → Program
```

每份专题文档解释自己的问题、案例、取舍、Contract、状态、失败、恢复、安全、测试和 Current/Target 边界；专题之间只能通过 Owner 引用，不复制第二套事实。

```text
project/          Zuno 项目知识唯一正式入口
  facts/          项目事实
  architecture/   总架构正文与架构图展示配对
  product/        产品边界
  domain/         法律 Domain State
  agents/         Agent 与 Multi-Agent Runtime
  knowledge/      Knowledge / Evidence
  services/       Service Boundary
  data/           Data Ownership / Recovery
  security/       Security Architecture
  eval/           Legal Eval / Benchmark
  deployment/     Microservice Deployment
status/          Current、Gap、Measurement 与 Production Readiness
decisions/       ADR
governance/      工程、Ownership 与文档治理
evidence/        验证证据
verification/    非规范性架构验证语料与覆盖审计
history/         历史归档
```

## Canonical Architecture Taxonomy

`11 Logical Modules + 1 Architecture` 是上一阶段的 History/Superseded 组织方式，不是永久边界。当前 Target 入口由 [`project/README.md`](./project/README.md) 和以下专题组成：

- [Product](./project/product/product-architecture.md)
- [Domain](./project/domain/legal-domain-model.md) / [Domain Lifecycle](./project/domain/domain-state-lifecycle.md)
- [Agent Platform](./project/agents/agent-platform.md) / [Multi-Agent](./project/agents/multi-agent-runtime.md)
- [Knowledge & Evidence](./project/knowledge/knowledge-evidence-architecture.md)
- [Services](./project/services/service-architecture.md)
- [Data](./project/data/data-ownership-and-recovery.md)
- [Security](./project/security/security-architecture.md)
- [Eval](./project/eval/legal-eval-and-benchmark.md)
- [Deployment](./project/deployment/microservice-deployment.md)

逻辑能力、服务、Worker、进程、容器、数据库和团队不做一一映射。旧模块入口保留为 [Superseded 迁移材料](./project/modules/README.md)，不再拥有新 Target 事实。

## Current / Target 路由

```text
Current
    由最新 main 的代码、Migration、测试、Trace、Eval、docs/status/ 和 docs/evidence/ 证明。

Canonical Target
    由已接受 ADR、共享 Contract Registry、Canonical Taxonomy 专题文档和总体架构定义。

Conditional Evidence Retrieval v2
    由 ADR 0006 独立定义为 accepted-target；当前 Program 尚未把它完整实现为 Current。

History
    只保留批准的摘要；raw construction materials 可按授权和 Git 可追溯规则退出 current tree。
```

上一轮 Runtime 工程收口已完成并归档。当前 `.agent/programs/` 登记的是
`PROJECT-ARCHITECTURE-RECONSTRUCTION-V1` 设计/审查 Program，不是 Runtime Implementation
Program；实现仍须等待架构 Gate。下一阶段按以下顺序推进：

```text
Fact Depth Recovery
→ Product Problem Reconstruction
→ Architecture Red / Blue / Counter Attack
→ Domain / Agent / Service Boundary Review
→ Big Tech Interview Red Team
→ Cross-service Contract / ADR Coordination
→ User Architecture Gate
→ 设计确认后才决定是否建立新的 Implementation Program
```

## 前后端边界

Zuno 当前产品形态是前后端分离：

```text
apps/web/               Vue 3 + Vite Web 工作台
apps/desktop/           Electron Desktop 宿主
src/backend/zuno/       FastAPI、Agent Runtime 与领域模块
```

Web / Desktop 通过 HTTP Command / Query、SSE Projection Stream 和版本化 Contract 消费后端能力。Frontend 不拥有 Run、Plan、Approval、Evidence、Effect、Memory 或 Eval 事实。

## 文档治理

`docs/project/architecture/` 是唯一正式总架构目录。正文 canonical surface 是 `architecture.md`；图源与 HTML 作为不可拆分的展示配对保留；`.agent/` 不保存架构镜像：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

专题设计进入 `docs/project/<topic>/`；`docs/project/modules/` 只保留上一阶段的 Superseded 迁移材料；状态进入 `docs/status/`；ADR 进入 `docs/decisions/`；治理进入 `docs/governance/`；历史进入 `docs/history/`。

`.agent/` 只保存路由、Program 和验证入口，不保存正式架构镜像。Target 文档完成不代表实现、测量、质量或生产就绪。
