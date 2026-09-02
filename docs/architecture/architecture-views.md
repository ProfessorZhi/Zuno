# Zuno Architecture Views

本文件只提供 `architecture.md` 的视觉补充。图中的边界和箭头用于帮助理解整体关系，不引入第二套架构事实。

updated: 2026-09-02
status: normative-target-visual-source
text_design_source: `docs/architecture/architecture.md`

## System Context View

```mermaid
flowchart LR
  USER[专业用户 / 法院系统 / Generic Host]
  APP[01 Application & Integration]
  DOMAIN[02 Legal Domain & Work Product]
  USER --> APP
  APP --> DOMAIN

  subgraph INTELLIGENCE[Knowledge & Intelligence]
    KNOW[03 Knowledge & Evidence]
    CAP[05 Capability & Skill]
    MODEL[07 Model Gateway]
  end

  subgraph EXECUTION[Execution & Effects]
    RUN[04 Agent Runtime & Control]
    TOOL[06 Tool Runtime & Effects]
  end

  SEC[08 Security & Governance]
  OBS[09 Observability & Evaluation]
  PLATFORM[Platform / Infrastructure]
  CONTEXT[Optional Context Provider]

  APP --> RUN
  RUN --> KNOW
  RUN --> CAP
  RUN --> MODEL
  RUN --> TOOL
  KNOW --> DOMAIN
  CAP --> DOMAIN
  TOOL --> DOMAIN
  SEC -. current policy .-> APP
  SEC -. current policy .-> RUN
  SEC -. current policy .-> TOOL
  OBS -. telemetry / evaluation .-> APP
  OBS -. telemetry / evaluation .-> RUN
  OBS -. telemetry / evaluation .-> DOMAIN
  PLATFORM -. primitives .-> APP
  PLATFORM -. primitives .-> DOMAIN
  PLATFORM -. primitives .-> KNOW
  PLATFORM -. primitives .-> RUN
  PLATFORM -. primitives .-> TOOL
  CONTEXT -. policy-scoped context .-> RUN
```

## Responsibility View

```mermaid
flowchart TB
  REQUEST[External request / task scope]
  APP[01 Application & Integration\n产品入口与交付]
  KNOW[03 Knowledge & Evidence\n材料版本、知识派生、任务就绪]
  RUN[04 Agent Runtime & Control\n计划、步骤、等待、恢复]
  CAP[05 Capability & Skill\n稳定专业能力]
  MODEL[07 Model Gateway\n受控模型依赖]
  DOMAIN[02 Legal Domain & Work Product\n正式法律事实]
  TOOL[06 Tool Runtime & Effects\n现实副作用]
  SEC[08 Security & Governance\n持续授权与审批]
  OBS[09 Observability & Evaluation\n观测与评测]

  REQUEST --> APP
  APP --> KNOW
  APP --> RUN
  RUN --> KNOW
  RUN --> CAP
  CAP --> MODEL
  KNOW --> DOMAIN
  CAP --> DOMAIN
  RUN --> TOOL
  TOOL --> DOMAIN
  SEC -. governs .-> APP
  SEC -. governs .-> RUN
  SEC -. governs .-> MODEL
  SEC -. governs .-> TOOL
  OBS -. observes .-> APP
  OBS -. observes .-> RUN
  OBS -. observes .-> DOMAIN
```

## Task Flow View

```mermaid
flowchart TB
  START[Request + Matter + Scope]
  AUTH[Current authorization]
  READY[Knowledge readiness]
  SIMPLE{Simple QA?}
  RETRIEVE[Retrieval + citation]
  MODEL[Model / capability computation]
  PLAN[PlanVersion + controlled steps]
  PROPOSAL[Candidate / proposal]
  ADMIT{Formal business fact needed?}
  DOMAIN[Domain admission + versioned WorkProduct]
  EFFECT{External effect needed?}
  PREP[PreparedAction + approval / audit]
  EXEC[Tool attempt]
  CONFIRM[EffectReceipt or Reconciliation]
  PUBLISH[Publication / delivery]

  START --> AUTH --> READY --> SIMPLE
  SIMPLE -->|Yes| RETRIEVE --> MODEL --> PUBLISH
  SIMPLE -->|No| PLAN --> RETRIEVE --> MODEL --> PROPOSAL --> ADMIT
  ADMIT -->|No| PUBLISH
  ADMIT -->|Yes| DOMAIN --> EFFECT
  EFFECT -->|No| PUBLISH
  EFFECT -->|Yes| PREP --> EXEC --> CONFIRM --> PUBLISH
```

## Authority and State View

```mermaid
flowchart LR
  DOC[DocumentVersion\n正式材料]
  KG[KnowledgeGeneration\n可重建知识派生]
  READY[ReadinessDecision\n任务可用性]
  CAND[Candidate / Proposal\n机器结果]
  DOMAIN[DomainVersion\n正式业务事实]
  RUN[Run / Plan / Checkpoint\n运行控制]
  EFFECT[EffectReceipt\n现实结果]
  SEC[Authorization / Approval\n安全决定]
  OBS[Trace / Metric / Eval\n观测投影]

  DOC --> KG --> READY
  READY --> CAND
  CAND --> DOMAIN
  RUN --> CAND
  SEC -. permits .-> RUN
  SEC -. permits .-> EFFECT
  EFFECT --> DOMAIN
  OBS -. observes only .-> RUN
  OBS -. observes only .-> DOMAIN
  OBS -. observes only .-> EFFECT
```

## Recovery View

```mermaid
sequenceDiagram
  participant R as Runtime
  participant D as Legal Domain
  participant C as Checkpoint
  participant T as Tool Runtime
  participant X as External System

  R->>D: submit proposal for formal admission
  D-->>R: DomainVersion + AdmissionReceipt
  Note over R,C: process may crash before checkpoint update
  R->>D: query matching admission causation
  D-->>R: formal fact already exists
  R->>C: repair control state

  R->>T: execute prepared external action
  T->>X: send operation
  X--xT: response lost / timeout
  T->>X: reconcile by stable operation identity
  X-->>T: actual outcome
  T-->>R: EffectReceipt / ReconciliationReceipt
```

## Deployment and Evolution View

```mermaid
flowchart TB
  START[Modular Python Backend]
  WORKERS[Independent Workers\nKnowledge / Model / Tool / Eval]
  PLATFORM[Platform primitives\nPostgreSQL / Object Store / Queue / Secret / Checkpointer]
  GATE{Evidence Gate}
  SERVICE[Optional independent network service]
  BASELINE[Simple baseline]
  COMPLEX[GraphRAG / Memory / Specialist / Native Runtime]
  EVAL{Repeatable measured gain?}
  KEEP[Keep complexity]
  REMOVE[Stay with / return to simpler design]

  START --> WORKERS
  PLATFORM -. supports .-> START
  PLATFORM -. supports .-> WORKERS
  START --> GATE
  GATE -->|Scaling / isolation / lifecycle evidence| SERVICE
  GATE -->|No independent need| START

  BASELINE --> COMPLEX --> EVAL
  EVAL -->|Yes| KEEP
  EVAL -->|No| REMOVE
```

## 图的阅读边界

这些图只表达总体关系。九个责任域的内部状态、Contract、事务、幂等和故障注入设计继续由 `docs/modules/` 与相关 ADR 负责；实现是否成立由 `docs/evidence/` 证明。
