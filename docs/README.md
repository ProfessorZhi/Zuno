# Zuno 文档入口

前台文档默认使用中文，承载当前正式结论；历史材料保留在 `docs/history/`，不删除、不改写成当前事实。

## 首读路径

- [总体 Target 架构](./architecture/architecture.md)：十一模块跨模块集成、Single Controller、Contract、状态、失败、恢复和验证原则。
- [架构 Mermaid 图源](./architecture/architecture-views.md)：总体架构的说明性视图源。
- [架构 HTML 展示](./architecture/architecture.html)：Architecture Atlas；不拥有独立架构语义。
- [十一逻辑模块设计](./modules/README.md)：每个领域 Owner 的唯一完整 Target 设计入口。
- [Evidence-Driven Agentic GraphRAG ADR](./decisions/0006-evidence-driven-agentic-graphrag.md)：下一版 `accepted-target` overlay；不代表 Current 实现。
- [Production Readiness](./status/production-readiness.md)：Current、Gap、Measurement、Blocked 和 Production Readiness 状态事实源。
- [架构决策](./decisions/README.md)：仍影响当前或下一版 Target 的正式 ADR。
- [工程治理](./governance/repo-ownership-matrix.md)：代码 Owner、迁移边界和兼容路径。
- [公开证据](./evidence/public-demo.md)：精选可展示证据。
- [历史归档](./history/README.md)：过时计划、旧 Program、旧架构基线和历史证据。

```text
architecture/    总架构四个 canonical 文件
modules/         十一个逻辑模块 Target 设计
status/          Current、Gap、Measurement 与 Production Readiness
decisions/       ADR
governance/      工程、Ownership 与文档治理
evidence/        验证证据
history/         历史归档
```

## 十一个模块

### 产品入口与知识供给

- [01 Product Surface](./modules/01-product-surface.md)
- [02 Input / Document Ingestion](./modules/02-input-document-ingestion.md)

### 智能核心

- [03 Knowledge / Agentic GraphRAG](./modules/03-knowledge-agentic-graphrag.md)
- [05 Memory & Context](./modules/05-memory-context.md)
- [06 Agent Core / Planning & Control](./modules/06-agent-core-planning-control.md)

### 能力执行层

- [04 Model Gateway](./modules/04-model-gateway.md)
- [07 Capability / Skill](./modules/07-capability-skill.md)
- [08 Tool Runtime](./modules/08-tool-runtime.md)

### 治理与运行底座

- [09 Security](./modules/09-security.md)
- [10 Observability & Eval](./modules/10-observability-eval.md)
- [11 Infrastructure](./modules/11-infrastructure.md)

四组只是阅读视图，不改变模块 Ownership，也不是物理部署层级。十一模块均已有唯一正式 Target 文档，不再使用“其余模块后续逐步细化”的旧表述。

## Current / Target 路由

```text
Current
    由最新 main 的代码、Migration、测试、Trace、Eval、docs/status/ 和 docs/evidence/ 证明。

Canonical Target
    由已接受 ADR、共享 Contract Registry、十一模块文档和总体架构定义。

Evidence-Driven Agentic GraphRAG v2
    由 ADR 0006 独立定义为 accepted-target；当前 Program 尚未把它完整实现为 Current。

History
    进入 docs/history/，不能重新解释成当前事实。
```

当前 Program 与 PHASE01–PHASE22 继续使用其冻结的 Architecture v1 基线。PHASE22 收口后，Architecture Owner 需要读取最新 Current，把 ADR 0006 与 Module 03、04、06、10、总体架构和共享 Contract Registry 正式协调，再创建新的实现 Program。

## 前后端边界

Zuno 当前产品形态是前后端分离：

```text
apps/web/               Vue 3 + Vite Web 工作台
apps/desktop/           Electron Desktop 宿主
src/backend/zuno/       FastAPI、Agent Runtime 与领域模块
```

Web / Desktop 通过 HTTP Command / Query、SSE Projection Stream 和版本化 Contract 消费后端能力。Frontend 不拥有 Run、Plan、Approval、Evidence、Effect、Memory 或 Eval 事实。

## 文档治理

`docs/architecture/` 和 `.agent/architecture/` 只能保留：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

模块专题进入 `docs/modules/`；状态进入 `docs/status/`；ADR 进入 `docs/decisions/`；治理进入 `docs/governance/`；历史进入 `docs/history/`。

存在 `.agent` 镜像时，正式文档和镜像必须字节级一致。Target 文档完成不代表实现、测量、质量或生产就绪。
