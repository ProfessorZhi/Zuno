# Zuno 文档入口

前台文档默认使用中文，承载当前正式结论。`docs/history/` 只保留经过批准的历史摘要；
已完成 Program 的 raw construction materials 可以在摘要完成、明确授权且 Git commit
可追溯时从 current tree 移除，但未提交内容、未合并提交、Migration、benchmark evidence
和用户文件不得未经明确 disposition 删除。

## 首读路径

- [Zuno 项目知识入口](./project/README.md)：事实、总体架构和技术模块的统一入口。
- [项目事实目录](./project/facts/README.md)：项目背景、团队、开发演进、交付使用和技术现实；未知信息保留为 `UNKNOWN`。
- [总体 Target 架构](./project/architecture/architecture.md)：十一模块跨模块集成、Single Controller、Contract、状态、失败、恢复和验证原则。
- [架构图展示配对](./project/architecture/architecture-views.md)：与 `architecture.html` 配套的 Mermaid 图源；二者只负责展示，不拥有独立架构语义。
- [十一逻辑模块设计](./project/modules/README.md)：每个领域 Owner 的唯一完整 Target 设计入口。
- [Evidence-Driven Retrieval ADR](./decisions/0006-evidence-driven-agentic-graphrag.md)：受控证据检索的 `accepted-target` overlay；不代表 Current 实现。
- [Reuse-first / Provider Boundary ADR](./decisions/0007-reuse-first-provider-boundary.md)：成熟能力优先复用、Zuno 控制面和 Provider 边界。
- [Production Readiness](./status/production-readiness.md)：Current、Gap、Measurement、Blocked 和 Production Readiness 状态事实源。
- [架构决策](./decisions/README.md)：仍影响当前或下一版 Target 的正式 ADR。
- [工程治理](./governance/repo-ownership-matrix.md)：代码 Owner、迁移边界和兼容路径。
- [架构文档写作标准](./governance/architecture-document-writing-standard.md)：总架构和十一模块的统一信息架构与验证规则。
- [当前证据](./evidence/README.md)：当前仍有证明价值的 baseline 与 closure evidence。
- [架构面试验证语料](./verification/interview-qa/README.md)：非规范性 QA Corpus，用真实追问压力测试 canonical architecture。
- [历史归档](./history/README.md)：经过批准的历史摘要，不重新解释成当前事实。

## 两条阅读路径

```text
人类理解：architecture.md Part A → 对应模块 Part A → 按需进入 Part B
工程实现：architecture.md Part B → Owner module Part B → ADR/Contract → Status/Evidence → Program
```

Part A 解释问题、案例、取舍和正常/异常流程；Part B 是 Contract、状态、失败、恢复、安全、持久化、测试和完成证据的规范入口。两部分始终位于同一份 Canonical Markdown 中。

```text
project/          Zuno 项目知识唯一正式入口
  facts/          项目事实
  architecture/   总架构正文与架构图展示配对
  modules/        十一个逻辑模块 Target 设计
status/          Current、Gap、Measurement 与 Production Readiness
decisions/       ADR
governance/      工程、Ownership 与文档治理
evidence/        验证证据
verification/    非规范性架构验证语料与覆盖审计
history/         历史归档
```

## 十一个模块

### 产品入口与知识供给

- [01 Product Surface](./project/modules/01-product-surface.md)
- [02 Input / Document Ingestion](./project/modules/02-input-document-ingestion.md)

### 智能核心

- [03 Knowledge / Conditional Evidence Retrieval](./project/modules/03-knowledge-agentic-graphrag.md)
- [05 Memory & Context](./project/modules/05-memory-context.md)
- [06 Agent Core / Planning & Control](./project/modules/06-agent-core-planning-control.md)

### 能力执行层

- [04 Model Gateway](./project/modules/04-model-gateway.md)
- [07 Capability / Skill](./project/modules/07-capability-skill.md)
- [08 Tool Runtime](./project/modules/08-tool-runtime.md)

### 治理与运行底座

- [09 Security](./project/modules/09-security.md)
- [10 Observability & Eval](./project/modules/10-observability-eval.md)
- [11 Infrastructure](./project/modules/11-infrastructure.md)

四组只是阅读视图，不改变模块 Ownership，也不是物理部署层级。十一模块均已有唯一正式 Target 文档，不再使用“其余模块后续逐步细化”的旧表述。

## Current / Target 路由

```text
Current
    由最新 main 的代码、Migration、测试、Trace、Eval、docs/status/ 和 docs/evidence/ 证明。

Canonical Target
    由已接受 ADR、共享 Contract Registry、十一模块文档和总体架构定义。

Conditional Evidence Retrieval v2
    由 ADR 0006 独立定义为 accepted-target；当前 Program 尚未把它完整实现为 Current。

History
    只保留批准的摘要；raw construction materials 可按授权和 Git 可追溯规则退出 current tree。
```

上一轮 Runtime 工程收口已完成并归档，`.agent/programs/` 当前为 `no-active`。下一阶段不是新的 Runtime Implementation Program；只在独立设计工作中按以下顺序推进：

```text
Current Baseline Review
→ Project Workflow Consolidation
→ Canonical Architecture Deep Review
→ 11 Module Deep Review
→ Cross-module Contract / ADR Coordination
→ Architecture Review
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

模块专题进入 `docs/project/modules/`；状态进入 `docs/status/`；ADR 进入 `docs/decisions/`；治理进入 `docs/governance/`；历史进入 `docs/history/`。

存在 `.agent` 镜像时，正式文档和镜像必须字节级一致。Target 文档完成不代表实现、测量、质量或生产就绪。
