# Zuno Architecture Views

本文件只提供 `architecture.md` 的视觉补充。图中的边界和箭头用于帮助理解整体关系，不引入第二套架构事实。

updated: 2026-09-10
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
  EFFECT[现实副作用事实\nPreparedAction / EffectReceipt]
  SEC[安全事实\nAuthorization / Approval / Audit]
  OBS[观测与评测\nTelemetry / Eval / Quality Evidence]

  KNOW --> CAND --> DOMAIN
  RUN --> CAND
  RUN --> EFFECT
  SEC --> RUN
  SEC --> EFFECT
  DOMAIN --> OBS
  RUN --> OBS
  EFFECT --> OBS
```

## Boundary Transition View

```mermaid
flowchart LR
  R[Research Artifact]
  CAP[Capability semantics]
  PROV[Provider]
  QUAL[Qualified Provider]
  CAND[Candidate]
  ADM[Formal Admission]
  FACT[Formal Business Fact]
  ACTION[PreparedAction]
  EFFECT[External Effect]

  R --> CAP --> PROV --> QUAL --> CAND --> ADM --> FACT
  FACT --> ACTION --> EFFECT
```

## Responsibility View

```mermaid
flowchart TB
  APP[01 Application & Integration]
  DOM[02 Legal Domain & Work Product]
  KNOW[03 Knowledge & Evidence]
  RUN[04 Agent Runtime & Control]
  CAP[05 Capability & Skill]
  TOOL[06 Tool Runtime & Effects]
  MODEL[07 Model Gateway]
  SEC[08 Security & Governance]
  OBS[09 Observability & Evaluation]
  PLATFORM[Platform / Infrastructure]
  CONTEXT[Optional Context Provider]

  APP --> RUN
  APP --> DOM
  RUN --> KNOW
  RUN --> CAP
  CAP --> MODEL
  RUN --> TOOL
  SEC --> APP
  SEC --> RUN
  SEC --> TOOL
  SEC --> MODEL
  DOM --> OBS
  KNOW --> OBS
  RUN --> OBS
  TOOL --> OBS
  MODEL --> OBS
  PLATFORM --> APP
  PLATFORM --> DOM
  PLATFORM --> KNOW
  PLATFORM --> RUN
  PLATFORM --> TOOL
  PLATFORM --> SEC
  PLATFORM --> OBS
  CONTEXT -. optional .-> RUN
```

## Recovery View

```mermaid
flowchart TD
  F[故障 / 不确定状态]
  C{哪一类事实有疑问?}
  OWNER[查询 Authoritative Owner Fact]
  CAUSE[比较 causation / version / freshness]
  AUTH[重新消费 current Security eligibility]
  REPAIR[修复 Runtime / Cache / Projection / Delivery]
  R1{事实已分类?}
  RETRY[Retry]
  REPLAN[Replan]
  RECON[Reconcile]
  STOP[停止 / 人工处理]

  F --> C --> OWNER --> CAUSE --> AUTH --> REPAIR --> R1
  R1 -->|same assumptions| RETRY
  R1 -->|planning assumptions changed| REPLAN
  R1 -->|external outcome unknown| RECON
  R1 -->|cannot resolve safely| STOP
```

## Deployment and Evolution View

```mermaid
flowchart LR
  PY[Modular Python Backend]
  W[Independent Workers]
  S[Independent Network Services]
  BASE[Simple Host / RAG baseline]
  EVID[Evidence Gate / Measurement]
  KEEP{收益可重复?}
  COMPLEX[GraphRAG / Native Runtime / Reflection / Specialist]
  DELETE[Delete / simplify]

  BASE --> PY
  PY --> W
  W -->|真实隔离/扩缩容需求| S
  BASE --> EVID
  COMPLEX --> EVID --> KEEP
  KEEP -->|yes| COMPLEX
  KEEP -->|no| DELETE
```
