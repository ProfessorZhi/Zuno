# 架构图

## 用途

这份文档只放少节点、可渲染的 Mermaid 图。它帮助第一次阅读的人快速区分 Current、Target 和维护工作流，不替代 `current-architecture.md`、`target-architecture.md` 和 `roadmap.md`。

## Current Runtime

当前图只表达已经由代码和测试证明的主线。

```mermaid
flowchart LR
  classDef node fill:#fbf8ff,stroke:#c4b5fd,stroke-width:1px,color:#1f2937;
  classDef edge stroke:#a78bfa,color:#6b21a8;

  A[Completion API]:::node --> B[CompletionService]:::node
  B --> C[GeneralAgent single loop]:::node
  C --> D[search_knowledge_base]:::node
  D --> E[KnowledgeQueryService]:::node
  E --> F[GraphRAGQueryService]:::node
  F --> G[RetrievalPlanner / Orchestrator]:::node
  G --> H[Evidence / Citation / Trace]:::node
  H --> C
```

## Target Runtime

目标图表达近期目标，不代表当前已经全部实现。

```mermaid
flowchart TB
  classDef node fill:#fbf8ff,stroke:#c4b5fd,stroke-width:1px,color:#1f2937;

  A[Typed API + Web/Desktop]:::node --> B[Application Services]:::node
  B --> C[Single GeneralAgent Runtime]:::node
  C --> D[Context / Memory Engine]:::node
  C --> E[Capability / Tool Retrieval]:::node
  C --> F[Knowledge / GraphRAG Retrieval]:::node
  F --> G[Retrieval / Fusion / Evidence]:::node
  D --> H[Trace / Eval]:::node
  E --> H
  G --> H
```

## Maintenance Workflow

维护图表达本仓库当前文档和执行计划边界。

```mermaid
flowchart LR
  classDef node fill:#fbf8ff,stroke:#c4b5fd,stroke-width:1px,color:#1f2937;

  A[AGENTS.md]:::node --> B[.agent/references]:::node
  B --> C[.agent/programs]:::node
  C --> D[Allowed files for phase]:::node
  D --> E[docs/architecture]:::node
  E --> F[verifiers and tests]:::node
  F --> G[commit and push]:::node
  C --> H[docs/history when replaced]:::node
```

## 边界

- Current Runtime 只写当前真实调用链。
- Target Runtime 可以写成熟目标，但必须保持目标语气。
- Maintenance Workflow 只表达如何维护文档、program、验证和历史归档。
- Domain Pack 只允许作为历史或兼容语境出现，不进入 Current 或 Target 主线图。
