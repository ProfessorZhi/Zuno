# Zuno Architecture Views

本文件只提供 `architecture.md` 的视觉补充。图中的边界和箭头用于帮助理解整体关系，不引入第二套架构事实。

updated: 2026-09-02
status: normative-target-visual-source
text_design_source: `docs/architecture/architecture.md`

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

## Deployment and Evolution View

```mermaid
flowchart TB
  BACKEND[Modular Python Backend]
  WORKERS[Independent Workers\nKnowledge / Model / Tool / Eval]
  PLATFORM[Platform primitives\nPostgreSQL / Object Store / Queue / Checkpointer / Secret]
  SPLIT{Evidence Gate for service split}
  SERVICE[Optional independent network service]
  SIMPLE[Simple baseline\nRAG / Generic Host + Legal Backend]
  COMPLEX[GraphRAG / Memory / Specialist / Native Runtime]
  EVAL{Repeatable measured gain?}
  KEEP[Keep the added complexity]
  REMOVE[Stay with / return to simpler design]

  PLATFORM -. supports .-> BACKEND
  PLATFORM -. supports .-> WORKERS
  BACKEND --> WORKERS
  BACKEND --> SPLIT
  SPLIT -->|scaling / isolation / lifecycle evidence| SERVICE
  SPLIT -->|no independent need| BACKEND

  SIMPLE --> COMPLEX --> EVAL
  EVAL -->|Yes| KEEP
  EVAL -->|No| REMOVE
```

## 图的阅读边界

六张图分别回答：一件案件怎样随时间变化；系统里有哪些不同事实；哪些跨边界转换需要更强证明；九个责任域为什么存在；两个关键故障窗口怎样恢复；复杂度和部署什么时候应该升级或退回。

模块内部状态、Contract、事务、幂等和故障注入继续由 `docs/modules/` 与相关 ADR 负责；实现是否成立由 `docs/evidence/` 证明。
