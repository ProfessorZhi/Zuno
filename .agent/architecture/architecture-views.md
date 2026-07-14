# Zuno Architecture Visual Atlas Source

updated: 2026-07-14  
status: normative-target-visual-source  
text_design_source: `docs/architecture/architecture.md`

本文件是 `architecture.html` 的 Mermaid 渲染源，不是第二份文字总架构。模块领域细节以十一份正式模块文档为准。

箭头规范：`==>` 命令/控制，`-->` 数据/结果，`-.->` 横切约束/观测。

## 一、4+1 View Model

### Logical View (4+1)

#### Overall — Eleven Modules

```mermaid
flowchart TB
  PS[01 Product Surface] ==>|RuntimeRequest| AC[06 Agent Core]
  AC -->|Publication and RunOutcome| PS
  PS ==>|Source command| IN[02 Input]
  IN -->|IndexableDocumentSnapshot| KN[03 Knowledge]
  AC ==>|ModelRoleRequirement| MG[04 Model Gateway]
  MG -->|ModelResponse and UsageReceipt| AC
  AC ==>|MemoryReadRequest| MM[05 Memory]
  MM -->|ContextPackVersion| AC
  AC ==>|CapabilityRequirement| CP[07 Capability]
  CP -->|CapabilitySelectionResult| AC
  AC ==>|ActionProposal| TR[08 Tool Runtime]
  TR -->|ToolObservation and EffectReceipt| AC
  SEC[09 Security] -.-> PS & IN & KN & MG & MM & AC & CP & TR
  OBS[10 Observability and Eval] -.-> PS & IN & KN & MG & MM & AC & CP & TR & SEC
  PS & IN & KN & MG & MM & AC & CP & TR & SEC & OBS --> INF[11 Infrastructure]
```

#### Local — Canonical Ownership

```mermaid
flowchart LR
  Domain[Domain Fact Owner] --> Fact[Versioned Domain Fact]
  Fact --> Outbox[Transactional Outbox]
  Outbox --> Projection[Product or Observability Projection]
  Infra[Infrastructure Receipt] -.-> Fact
  Projection -.->|read only| Client[Client]
  Client ==>|Command only| Domain
```

#### Local — Documentation Truth

```mermaid
flowchart LR
  ADR[Global principles and ADR] --> MOD[Eleven canonical module docs]
  MOD --> ARCH[architecture.md integration]
  ARCH --> HTML[architecture.html]
  VIEWS[architecture-views.md render source] --> HTML
  MOD & ARCH --> PROGRAM[Confirmed Program]
  PROGRAM --> CODE[Code Migration Tests Evidence]
```

### Development View (4+1)

#### Overall — Repository Dependency

```mermaid
flowchart TB
  WEB[apps/web] --> API[src/backend/zuno/api]
  API --> PRODUCT[zuno product application]
  PRODUCT --> AGENT[zuno/agent]
  AGENT --> KNOW[zuno/knowledge]
  AGENT --> MEMORY[zuno/memory]
  AGENT --> CAP[zuno/capability]
  KNOW & MEMORY & CAP & AGENT --> PLATFORM[zuno/platform ports and adapters]
  DOCS[docs/modules and docs/architecture] --> VERIFY[verifiers and repo tests]
```

#### Local — Module Package Rule

```mermaid
flowchart LR
  Domain[Domain] --> Application[Application Services]
  Application --> Ports[Typed Ports]
  Adapters[Adapters] --> Ports
  Adapters --> Platform[Infrastructure primitives]
  API[Inbound API] --> Application
  Domain -.->|no provider SDK| Adapters
```

#### Local — Architecture Build Chain

```mermaid
flowchart LR
  Modules[11 module docs] --> SetGuard[Architecture document-set verifier]
  Total[architecture.md] --> Renderer[render_architecture.py]
  Views[architecture-views.md] --> Renderer
  HTML[architecture.html] --> Renderer
  Renderer --> Mirrors[docs and agent mirrors]
  SetGuard --> Tests[focused repository tests]
  Mirrors --> Tests
```

### Process View (4+1)

#### Overall — Agent Run

```mermaid
flowchart TB
  REQ[RuntimeRequest] --> RUN[AgentRunGraph]
  RUN --> PLAN[Plan Proposal Validate Activate]
  PLAN --> READY[ReadySet Admission Budget]
  READY --> SEND[Dispatch Commit and Send]
  SEND --> STEP[StepExecutionGraph]
  STEP --> OBS[NormalizedObservation]
  OBS --> ACCEPT[Evaluation and Acceptance]
  ACCEPT -->|continue| READY
  ACCEPT -->|replan| BARRIER[Replan Barrier and new PlanVersion]
  BARRIER --> READY
  ACCEPT -->|complete| FINAL[FinalCandidate and Final Gate]
  FINAL --> PUB[Publication]
  PUB --> OUT[RunOutcome]
```

#### Local — Ingestion and Index

```mermaid
flowchart LR
  SRC[SourceObject] --> DV[DocumentVersion]
  DV --> PARSE[ParsePlan Job Attempt]
  PARSE --> IR[CanonicalDocumentIR and SourceSpan]
  IR --> QUALITY[Parser Quality Gate]
  QUALITY --> HAND[IndexableDocumentSnapshot]
  HAND --> BUILD[IndexWriteBatch]
  BUILD --> VIS[Write Visibility Verification]
  VIS --> ACCEPT[Knowledge Acceptance]
  ACCEPT --> CUT[IndexCutover and ServingWatermark]
```

#### Local — Tool Effect

```mermaid
flowchart LR
  AP[ActionProposal] --> PREP[PreparedToolAction]
  PREP --> SG[Security Prepare Gate]
  SG --> APPROVAL[Optional Approval]
  APPROVAL --> EXEC[Execute Gate and latest Epoch]
  EXEC --> AUDIT[Mandatory Audit durability]
  AUDIT --> CLAIM[IdempotencyClaim]
  CLAIM --> ATT[ToolAttempt]
  ATT --> EFFECT{Effect result}
  EFFECT -->|known| RECEIPT[EffectReceipt]
  EFFECT -->|unknown| REC[EffectReconciliation]
```

### Physical View (4+1)

#### Overall — Canonical Server Target

```mermaid
flowchart TB
  CLIENT[Web Desktop External API] --> API[Server-hosted Product API]
  API --> CONTROL[Controller role]
  API --> WORKER[Async worker roles]
  CONTROL --> PG[(PostgreSQL)]
  CONTROL --> CP[(LangGraph Checkpointer)]
  WORKER --> PG
  WORKER --> OBJ[(Object Store)]
  WORKER --> Q[(RabbitMQ)]
  WORKER --> IDX[(BM25 Vector Graph projections)]
  CONTROL --> IDX
  CONTROL --> TRACE[(Trace Audit Eval store)]
```

#### Local — Facts and Projections

```mermaid
flowchart LR
  PG[(PostgreSQL Domain Facts)] --> OUTBOX[Outbox]
  OUTBOX --> Q[(RabbitMQ)]
  Q --> WORKER[Idempotent Worker]
  WORKER --> OBJ[(Object Store)]
  WORKER --> INDEX[(Rebuildable Index)]
  INDEX --> RECEIPT[Visibility and verification receipts]
  RECEIPT --> PG
```

#### Local — Recovery

```mermaid
flowchart LR
  RESTART[Process restart] --> CHECK[(Checkpoint)]
  RESTART --> DOMAIN[(Domain Store)]
  CHECK --> RECON[Domain Checkpoint Reconciler]
  DOMAIN --> RECON
  RECON --> RESUME[Resume safe node]
  LEASE[Lease and fencing] -.-> RESUME
  OUTBOX[Inbox and Outbox] -.-> RESUME
```

### Scenarios View (4+1)

#### Overall — Strict Grounded Answer

```mermaid
sequenceDiagram
  participant U as User
  participant P as Product
  participant A as Agent Core
  participant K as Knowledge
  participant M as Model Gateway
  U->>P: submit strict grounded task
  P->>A: RuntimeRequest
  A->>K: KnowledgeQueryRequest
  K-->>A: EvidenceBundle with CitationLineage
  A->>M: SYNTHESIZER requirement
  M-->>A: candidate response
  A-->>P: Publication and RunOutcome
  P-->>U: authorized answer and citations
```

#### Local — Approval and Resume

```mermaid
sequenceDiagram
  participant A as Agent Core
  participant T as Tool Runtime
  participant S as Security
  participant P as Product
  participant U as Approver
  A->>T: ActionProposal
  T->>S: PreparedToolAction
  S-->>P: ApprovalRequest
  P-->>U: authorized approval view
  U->>P: approve
  P->>S: approval command
  S-->>A: SecurityApprovalDecision
  A->>T: resume execution
  T-->>A: EffectReceipt or Reconciliation
```

#### Local — Delete and Revoke

```mermaid
sequenceDiagram
  participant P as Product
  participant S as Security
  participant I as Input
  participant K as Knowledge
  participant M as Memory
  participant F as Infrastructure
  P->>S: delete or revoke command
  S-->>I: authorized deletion
  I->>K: document tombstone
  K->>M: evidence invalidation
  K->>F: physical index deletion request
  F-->>K: deletion verification
  K-->>P: no-longer-retrievable projection
```

## 二、Views & Beyond

### Module View (Views & Beyond)

#### Overall — Eleven Modules to Six Runtime Domains

```mermaid
flowchart LR
  PS[01 Product] --> PD[Product and API]
  IN[02 Input] --> KD[Knowledge and Memory Runtime]
  KN[03 Knowledge] --> KD
  MG[04 Model Gateway] --> AC[Agent Control Plane]
  MM[05 Memory] --> KD
  AG[06 Agent Core] --> AC
  CP[07 Capability] --> TD[Capability and Tool]
  TR[08 Tool Runtime] --> TD
  SEC[09 Security] --> GD[Governance Plane]
  OBS[10 Observability] --> GD
  INF[11 Infrastructure] --> ID[Durable Infrastructure]
```

#### Local — Owns Consumes Produces

```mermaid
flowchart LR
  OWNER[Canonical Owner] -->|owns| FACT[Domain Fact]
  CONSUMER[Consumer] ==>|typed request| OWNER
  OWNER -->|versioned result| CONSUMER
  OWNER -->|domain event| OBS[Observability]
  OWNER ==>|primitive request| INF[Infrastructure]
  INF -->|physical receipt| OWNER
```

#### Local — Boundary Violation Guard

```mermaid
flowchart LR
  MODEL[Model Proposal] --> GATE[Deterministic Gate]
  CLIENT[Client Command] --> GATE
  GATE --> OWNER[Domain Owner]
  BYPASS[Direct SDK DB Tool write] --> REJECT[Repository and runtime guard]
  REJECT -.-> OWNER
```

### Component-and-Connector View (Views & Beyond)

#### Overall — Commands Data and Observation

```mermaid
flowchart TB
  PRODUCT ==>|Command| CORE[Agent Core]
  CORE ==>|Query or Action request| DOMAIN[Knowledge Model Memory Capability Tool]
  DOMAIN -->|Domain result| CORE
  DOMAIN -->|Domain event| OBS[Observability]
  CORE -->|Publication event| PRODUCT
  DOMAIN ==>|Physical operation| INF[Infrastructure]
  INF -->|Receipt| DOMAIN
  SEC[Security] -.-> PRODUCT & CORE & DOMAIN
```

#### Local — CrossModuleEnvelope

```mermaid
flowchart LR
  PRODUCER[Producer] --> ENV[CrossModuleEnvelopeV1]
  ENV --> HASH[Payload and schema hash]
  ENV --> SCOPE[Tenant Workspace Principal]
  ENV --> EPOCH[Security Epoch and authorization ref]
  ENV --> TIME[Deadline correlation causation]
  HASH & SCOPE & EPOCH & TIME --> CONSUMER[Consumer validation]
  CONSUMER -->|valid| HANDLER[Idempotent handler]
  CONSUMER -->|invalid| FAIL[Owned failure namespace]
```

#### Local — Budget and Admission

```mermaid
flowchart LR
  NEED[Step or operation need] --> FEAS[Capability feasibility]
  FEAS --> SEC[Security compatibility]
  SEC --> BUDGET[Budget reservation]
  BUDGET --> CAPACITY[Capacity and quota]
  CAPACITY --> DISPATCH[Dispatch]
  DISPATCH --> SETTLE[Usage and budget settlement]
```

### Data View (Views & Beyond)

#### Overall — Authoritative Facts

```mermaid
flowchart TB
  PG[(PostgreSQL)] --> DOMAIN[Structured domain facts]
  OBJ[(Object Store)] --> LARGE[Large immutable payloads]
  CHECK[(Checkpointer)] --> CONTROL[Graph control state]
  DOMAIN --> BM25[(BM25)]
  DOMAIN --> VECTOR[(Vector)]
  DOMAIN --> GRAPH[(Graph)]
  DOMAIN --> PROJ[Product and Observability projections]
  LARGE --> BM25 & VECTOR & GRAPH
  CONTROL -.-> DOMAIN
```

#### Local — Knowledge Version Publication

```mermaid
flowchart LR
  SPEC[IndexSpec] --> BATCH[IndexWriteBatch]
  BATCH --> WR[IndexWriteReceipt]
  WR --> VR[VisibilityReceipt]
  VR --> VERIFY[IndexVerification]
  VERIFY --> MAN[IndexManifest]
  MAN --> ACCEPT[Domain Acceptance]
  ACCEPT --> CUT[IndexCutover]
  CUT --> WATER[ServingWatermark]
```

#### Local — Version Pinning

```mermaid
flowchart LR
  RUN[AgentRun] --> KS[KnowledgeSnapshot]
  RUN --> MS[MemorySnapshot]
  RUN --> MB[Model config bundle]
  RUN --> SP[Security Policy and Epoch]
  RUN --> RB[Runtime bundle]
  KS & MS & MB & SP & RB --> HASH[ExecutionContextSnapshot hash]
```

### Quality View (Views & Beyond)

#### Overall — Requirement to Evidence

```mermaid
flowchart LR
  REQ[ARCH Requirement] --> CONTROL[Runtime or repository control]
  CONTROL --> UT[Unit Contract]
  CONTROL --> IT[Integration]
  CONTROL --> FT[Fault Injection]
  CONTROL --> E2E[E2E]
  UT & IT & FT & E2E --> EVID[Evidence Registry]
  EVID --> GATE[ReleaseGateEvaluation]
```

#### Local — Quality Status

```mermaid
stateDiagram-v2
  [*] --> PREPARED
  PREPARED --> RUNTIME_OBSERVED
  RUNTIME_OBSERVED --> MEASURED
  PREPARED --> BLOCKED
  RUNTIME_OBSERVED --> BLOCKED
  MEASURED --> QUALITY_PROVEN
  BLOCKED --> MEASURED
  QUALITY_PROVEN --> [*]
```

#### Local — Quality Cost Safety Gate

```mermaid
flowchart LR
  Q[Quality metrics] --> G[Release Gate]
  C[Cost and latency] --> G
  S[Security and privacy] --> G
  R[Reliability and recovery] --> G
  G -->|all constraints pass| PASS[Eligible]
  G -->|any hard constraint fails| BLOCK[Blocked]
```

## 三、Zuno Product Core

### Agentic GraphRAG Evidence and Agent Loop (Zuno)

#### Overall — Outer and Inner Control Loops

```mermaid
flowchart TB
  TASK[TaskContract] --> PLAN[Agent Core Plan]
  PLAN --> KR[KnowledgeRetrievalGraph]
  KR --> STRAT[RetrievalPlan]
  STRAT --> RET[Parallel retrievers]
  RET --> LEDGER[EvidenceLedger and EvidenceFrontier]
  LEDGER --> QUALITY[RetrievalQualityVerdict]
  QUALITY -->|correct| STRAT
  QUALITY -->|sufficient| BUNDLE[SelectedEvidenceBundle]
  QUALITY -->|task change needed| PROP[KnowledgeControlProposal]
  BUNDLE --> ACCEPT[Step Acceptance]
  PROP --> PLAN
  ACCEPT --> FINAL[Final Gate and Publication]
```

#### Local — Evidence Lineage

```mermaid
flowchart LR
  DOC[DocumentVersion] --> SPAN[SourceSpan]
  SPAN --> CHUNK[CitationChunk]
  CHUNK --> EDGE[Entity Relation Community Evidence]
  EDGE --> ROUND[RetrievalRound]
  ROUND --> LEDGER[EvidenceLedger]
  LEDGER --> CLAIM[Claim Evidence Binding]
  CLAIM --> CITATION[Citation]
  CITATION --> ANSWER[GroundedAnswer Publication]
```

#### Local — Corrective Retrieval and Replan

```mermaid
flowchart LR
  GAP[Evidence gap] --> CLASS{Failure class}
  CLASS -->|query issue| REWRITE[Query rewrite or expansion]
  CLASS -->|path issue| ROUTE[Graph text structured route]
  CLASS -->|index issue| RECOVER[Index recovery]
  CLASS -->|task assumption invalid| REPLAN[Agent Replan]
  CLASS -->|no safe path| ABSTAIN[Abstain]
  REWRITE & ROUTE --> NEXT[Next RetrievalRound]
```
