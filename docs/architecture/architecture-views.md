# Zuno Architecture Views

本文件只提供 `architecture.md` 的视觉补充。图中的边界和箭头用于帮助理解整体关系，不引入第二套架构事实。

updated: 2026-09-11
status: normative-target-visual-source
text_design_source: `docs/architecture/architecture.md`

## System Context View

```mermaid
flowchart LR
  USER[专业用户 / Web]
  HOST[法院 Host / API Client]

  subgraph ZUNO[Zuno logical system boundary]
    APP[Application & Integration]
    CORE[Domain / Knowledge / Runtime / Capability]
    GATES[Security / Model Gateway / Effects]
    OBS[Observability & Evaluation]
  end

  subgraph PLATFORM[Platform primitives]
    PG[(PostgreSQL)]
    OBJ[(Object Store)]
    Q[Queue / Checkpointer]
    SECRET[Secret / Identity / Policy]
    OTEL[Telemetry backend]
  end

  MODELS[Model / Research Providers]
  EXT[External Court / Tool Systems]

  USER --> APP
  HOST --> APP
  APP --> CORE
  CORE --> GATES
  GATES --> MODELS
  GATES --> EXT
  CORE -. uses .-> PLATFORM
  GATES -. uses .-> PLATFORM
  OBS -. observes .-> CORE
  OBS -. exports .-> OTEL

  EXT -. owns its internal reality .-> GATES
  MODELS -. returns computation, not business truth .-> GATES
```

Zuno 位于调用者、可替换计算 Provider、外围现实系统和平台基础设施之间。外部输入首先是 assertion / observation；模型结果不是正式业务事实，HTTP timeout 也不是远端现实失败证明。Platform 提供物理机制，不因此拥有法律业务完成语义。

## Case Timeline View

```mermaid
flowchart LR
  M1[合同 v3 / 起诉状 / 扫描附件]
  K1[KnowledgeGeneration]
  R1{ReadinessDecision}
  C1[Candidate / Proposal]
  A1[Human review + Domain Admission]
  W1[WorkProduct v1 + AdmissionReceipt]
  M2[新证据进入]
  S1[旧结果需要复核]
  W2[WorkProduct v2]
  P1[PreparedAction]
  E1[External Effect]
  ER[EffectReceipt]

  M1 --> K1 --> R1
  R1 -->|当前问题可判断| C1 --> A1 --> W1
  M2 --> S1 --> W2
  W1 --> S1
  W2 --> P1 --> E1 --> ER
```

## Fact Authority View

```mermaid
flowchart TB
  KNOW[材料与知识事实\nDocumentVersion / KnowledgeGeneration / ReadinessDecision]
  CAND[机器候选\nEvidenceCandidate / Proposal]
  DOMAIN[正式法律事实\nEvidence / Finding / WorkProduct / AdmissionReceipt]
  RUN[运行控制事实\nRun / PlanVersion / Step / Checkpoint]
  EFFECT[现实副作用事实\nPreparedAction / Attempt / EffectReceipt]
  SEC[08 Security & Governance\nAuthorization / Approval]
  OBS[09 Observability & Evaluation\nTelemetry / Eval]

  KNOW --> CAND --> DOMAIN
  RUN --> CAND
  RUN --> EFFECT
  SEC -. permits transitions .-> CAND
  SEC -. permits transitions .-> DOMAIN
  SEC -. permits transitions .-> EFFECT
  OBS -. observes only .-> KNOW
  OBS -. observes only .-> RUN
  OBS -. observes only .-> DOMAIN
  OBS -. observes only .-> EFFECT
```

## State / Persistence / Consistency View

```mermaid
flowchart TB
  SOURCE[正式材料 / Source bytes\n长期保真]
  DOMAIN[(Domain durable facts\nDomainVersion / AdmissionReceipt)]
  KNOW[(Knowledge generation metadata\nManifest / serving fact)]
  INDEX[(Rebuildable indexes\nBM25 / Vector / Graph)]
  RUN[(Runtime control\nPlan / Step / Checkpoint)]
  EFFECT[(Effect ledger\nAction / Attempt / Effect / Reconciliation)]
  SEC[(Security / Approval / Audit facts)]
  APP[(Application projections\nPublication / Delivery)]
  OBS[(Telemetry / Eval)]
  REMOTE[External reality]

  SOURCE --> KNOW --> INDEX
  SOURCE --> DOMAIN
  DOMAIN -. completion proof .-> RUN
  KNOW -. readiness / serving fact .-> RUN
  SEC -. current eligibility .-> RUN
  RUN --> EFFECT --> REMOTE
  REMOTE -. reconcile by stable identity .-> EFFECT
  DOMAIN -. projection source .-> APP
  EFFECT -. projection source .-> APP
  SEC -. publication gate .-> APP
  DOMAIN -. correlation only .-> OBS
  RUN -. correlation only .-> OBS
  EFFECT -. correlation only .-> OBS
```

Owner 内部使用自己的事务、version / CAS 和完成证明保护强一致；跨 Owner 默认不做全局 2PC。Projection 可以落后并被修复，外部现实不确定时必须保留 Unknown 并 Reconcile。Knowledge index 可重建，不代表 serving pointer 可以指向半成品。

## Boundary Transition View

```mermaid
flowchart LR
  DOC[DocumentVersion]
  KG[KnowledgeGeneration]
  READY[ReadinessDecision]
  CAND[EvidenceCandidate / Proposal]
  ADMIT[Formal Admission]
  RECEIPT[AdmissionReceipt]
  RUN[Runtime Checkpoint]
  PREP[PreparedAction]
  TRY[Tool Attempt]
  UNKNOWN{Outcome known?}
  EFFECT[EffectReceipt]
  RECON[Reconcile]

  DOC --> KG --> READY
  READY --> CAND --> ADMIT --> RECEIPT
  RUN -. control progress .-> CAND
  RECEIPT -. repairs after crash .-> RUN
  RUN --> PREP --> TRY --> UNKNOWN
  UNKNOWN -->|Yes| EFFECT
  UNKNOWN -->|No| RECON --> EFFECT
```

## Responsibility View

```mermaid
flowchart TB
  APP[01 Application & Integration\n产品入口、Matter / Scope、发布与交付]
  DOMAIN[02 Legal Domain & Work Product\n正式法律事实]
  KNOW[03 Knowledge & Evidence\n材料、知识派生、就绪与 lineage]
  RUN[04 Agent Runtime & Control\n计划、步骤、等待与恢复]
  CAP[05 Capability & Skill\n稳定专业能力]
  TOOL[06 Tool Runtime & Effects\n现实副作用]
  MODEL[07 Model Gateway\n模型角色与 Provider]
  SEC[08 Security & Governance\n持续授权与审批]
  OBS[09 Observability & Evaluation\n观测与评测]
  CONTEXT[Optional Context Provider]

  APP --> RUN
  APP --> DOMAIN
  RUN --> KNOW
  RUN --> CAP
  CAP --> MODEL
  KNOW --> DOMAIN
  CAP --> DOMAIN
  RUN --> TOOL
  SEC -. current decisions .-> APP
  SEC -. current decisions .-> RUN
  SEC -. current decisions .-> TOOL
  OBS -. observes .-> APP
  OBS -. observes .-> RUN
  OBS -. observes .-> DOMAIN
  CONTEXT -. policy-scoped context .-> RUN
```

## Recovery View

```mermaid
sequenceDiagram
  participant R as Agent Runtime
  participant D as Legal Domain
  participant C as Checkpoint
  participant T as Tool Runtime
  participant X as External System

  R->>D: submit candidate for Formal Admission
  D-->>R: DomainVersion + AdmissionReceipt
  Note over R,C: crash before next Checkpoint
  R->>D: query by stable causation
  D-->>R: formal fact already exists
  R->>C: repair control state, do not re-submit

  R->>T: execute PreparedAction
  T->>X: send operation
  X--xT: response lost / timeout
  Note over T,X: outcome is Unknown, not ordinary Failed
  T->>X: Reconcile by stable operation identity
  X-->>T: actual outcome
  T-->>R: EffectReceipt / Reconciliation result
```

## Deployment / Scale / Backpressure View

```mermaid
flowchart TB
  CLIENTS[Web / Court Host / API Client]
  APP[Modular Python Backend\nApplication + Domain + control responsibilities]
  CTRL[Logical Runtime Controller]

  subgraph WORKERS[Work-type Worker Pools]
    INGEST[Ingestion / OCR / Parse]
    KWORK[Knowledge rebuild / Retrieval]
    MODEL[Model / Capability work]
    TOOL[Effect execution / Reconcile]
    EVAL[Eval / Batch analysis]
  end

  subgraph PLATFORM[Shared platform primitives]
    PG[(PostgreSQL)]
    OBJ[(Object Store)]
    QUEUE[Queue / Checkpointer]
    SECRET[Secret / Identity / Policy]
  end

  MP[Model Providers]
  EXT[External Court / Tool Systems]

  CLIENTS --> APP --> CTRL
  CTRL --> WORKERS
  WORKERS --> PLATFORM
  APP --> PLATFORM
  MODEL --> MP
  TOOL --> EXT

  INGEST -. scale by parse backlog .-> INGEST
  KWORK -. scale by build/query load .-> KWORK
  MODEL -. bounded by provider quota/budget .-> MODEL
  TOOL -. bounded by target rate/effect safety .-> TOOL
```

默认不按九个责任域拆九个服务。扩容先看工作类型和真实瓶颈；`Single Controller` 是逻辑写者，不等于单机。入口、Runtime、Provider 和外部目标之间都需要显式 Backpressure，避免下游过载被放大成无界队列、费用或重复副作用。

## Deployment Evolution View

```mermaid
flowchart TB
  BASE[Simple baseline\nControlled RAG / Generic Host + Legal Backend]
  MOD[Modular backend + justified workers]
  SPLIT{Independent scaling / isolation / egress / lifecycle need?}
  SERVICE[Optional independent network service]
  COMPLEX[GraphRAG / Memory / Specialist / Native Runtime]
  EVAL{Repeatable measured gain?}
  KEEP[Keep bounded complexity]
  REMOVE[Stay with / return to simpler design]

  BASE --> MOD --> SPLIT
  SPLIT -->|Yes, evidenced| SERVICE
  SPLIT -->|No| MOD
  MOD --> COMPLEX --> EVAL
  EVAL -->|Yes| KEEP
  EVAL -->|No| REMOVE
```

## 图的阅读边界

这些视图分别回答：Zuno 与外部世界的系统边界在哪里；一件案件怎样随时间变化；系统里有哪些不同事实；状态怎样落在不同耐久边界并在没有全局 2PC 的情况下收敛；哪些跨边界转换需要更强证明；九个责任域怎样协作；两个关键故障窗口怎样恢复；默认部署怎样按工作类型扩缩容并传播 Backpressure；复杂度和服务拆分什么时候应该升级或退回。

模块内部状态、Contract、事务、幂等和故障注入继续由 `docs/modules/` 与相关 ADR 负责；实现是否成立由 `docs/evidence/` 证明。