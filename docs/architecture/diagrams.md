# 架构图

## 用途

这份文档只放少节点、可渲染的 Mermaid 图。它帮助第一次阅读的人快速区分 Current、Target 和维护工作流，不替代 `current-architecture.md`、`target-architecture.md` 和 `roadmap.md`。

## 同步规则

Mermaid 源只维护在本文。`docs/architecture/overview.html` 和 `.agent/architecture/blueprint.html` 由 `tools/agent/render_architecture.py` 从本文生成；HTML 可以用本地 `file://` 打开，Mermaid 渲染使用 CDN runtime，离线时仍保留标题、说明和 Mermaid source。修改图后运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
```

## Current Runtime

当前图只表达已经由代码和测试证明的主线。

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f8f8fb"}}}%%
flowchart LR
  classDef node fill:#f6f3ff,stroke:#a99cff,stroke-width:1px,color:#2c255f;

  A[Completion API]:::node --> B[CompletionService]:::node
  B --> C[GeneralAgent single loop]:::node
  C --> D[search_knowledge_base]:::node
  D --> E[KnowledgeQueryService]:::node
  E --> F[GraphRAGQueryService]:::node
  F --> G[RetrievalPlanner / Orchestrator]:::node
  G --> H[Evidence / Citation / Trace]:::node
  H --> C
  linkStyle default stroke:#9b8cff,color:#2c255f;
```

## Target Runtime

目标图表达近期目标，不代表当前已经全部实现。

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f8f8fb"}}}%%
flowchart TB
  classDef node fill:#f6f3ff,stroke:#a99cff,stroke-width:1px,color:#2c255f;

  A[Typed API + Web/Desktop]:::node --> B[Application Services]:::node
  B --> C[Single GeneralAgent Runtime]:::node
  C --> D[Context / Memory Engine]:::node
  C --> E[Capability / Tool Retrieval]:::node
  C --> F[Knowledge / GraphRAG Retrieval]:::node
  F --> G[Retrieval / Fusion / Evidence]:::node
  D --> H[Trace / Eval]:::node
  E --> H
  G --> H
  linkStyle default stroke:#9b8cff,color:#2c255f;
```

## Maintenance Workflow

维护图表达本仓库当前文档和执行计划边界。

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#f8f8fb"}}}%%
flowchart LR
  classDef node fill:#f6f3ff,stroke:#a99cff,stroke-width:1px,color:#2c255f;

  A[AGENTS.md]:::node --> B[.agent/references]:::node
  B --> C[.agent/programs]:::node
  C --> D[Allowed files for phase]:::node
  D --> E[docs/architecture]:::node
  E --> F[verifiers and tests]:::node
  F --> G[commit and push]:::node
  C --> H[docs/history when replaced]:::node
  linkStyle default stroke:#9b8cff,color:#2c255f;
```

## 边界

- Current Runtime 只写当前真实调用链。
- Target Runtime 可以写成熟目标，但必须保持目标语气。
- Maintenance Workflow 只表达如何维护文档、program、验证和历史归档。
- Domain Pack 只允许作为历史或兼容语境出现，不进入 Current 或 Target 主线图。
