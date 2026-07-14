# Zuno Architecture Visual Atlas Source

updated: 2026-07-14
status: normative-target-visual-source
text_design_source: `docs/architecture/architecture.md`
canonical_domain_sources: `docs/modules/01-*.md` through `docs/modules/11-*.md`

本文件只提供说明性 Mermaid。领域 Contract、状态、Failure、持久化和测试以十一份模块文档为准；跨模块关系以 `architecture.md` 为准；本图源和 HTML 优先级最低。

箭头规范：`==>` 命令/控制，`-->` 数据/结果，`-.->` 横切约束/观测。

## 一、4+1 View Model

### Logical View (4+1)

#### Overall — Eleven Modules and Canonical Owners

```mermaid
flowchart TB
  PS[01 Product Surface] ==>|RuntimeRequest / Signal| AC[06 Agent Core]
  AC -->|Publication / RunOutcome| PS
  PS ==>|InputSubmission| IN[02 Input]
  IN -->|IndexableDocumentSnapshot| KN[03 Knowledge]
  AC ==>|KnowledgeQueryRequest| KN
  KN -->|KnowledgeRetrievalOutcome / KnowledgeControlProposal| AC
  AC ==>|ModelRoleRequirement| MG[04 Model Gateway]
  MG -->|ModelResponse / UsageReceipt| AC
  AC ==>|MemoryReadRequest| MM[05 Memory]
  MM -->|ContextPackVersion| AC
  AC ==>|CapabilityRequirement| CP[07 Capability]
  CP -->|AvailabilitySnapshot / SelectionResult| AC
  AC ==>|ActionProposal| TR[08 Tool Runtime]
  TR -->|ToolObservation / EffectReceipt / Reconciliation| AC
  SEC[09 Security] -.-> PS & IN & KN & MG & MM & AC & CP & TR
  OBS[10 Observability and Eval] -.-> PS & IN & KN & MG & MM & AC & CP & TR & SEC
  PS & IN & KN & MG & MM & AC & CP & TR & SEC & OBS --> INF[11 Infrastructure]
```

#### Local — Agent Core Control Stack

```mermaid
flowchart TB
  RUN[Fixed AgentRunGraph] --> TASK[TaskContract / GoalVersion]
  TASK --> SNAP[ExecutionContextSnapshot]
  SNAP --> PLAN[Dynamic immutable Plan DAG]
  PLAN --> READY[ReadySet / Admission / Budget]
  READY --> DISPATCH[Dispatch commit before Send]
  DISPATCH --> STEP[Fixed StepExecutionGraph]
  STEP --> ACCEPT[Action Evaluation / Step Acceptance]
  ACCEPT --> JOIN[Join Evaluation / Reflection]
  JOIN --> DECIDE[Agent Core ControlDecision]
  DECIDE -->|replan| BARRIER[Replan Barrier + new PlanVersion]
  DECIDE -->|complete| FINAL[Final Gate / Publication / RunOutcome]
```

#### Local — Evidence Memory and Publication Boundaries

```mermaid
flowchart LR
  SOURCE[DocumentVersion / SourceSpan] --> EVID[Knowledge Evidence / CitationLineage]
  EVID --> CONTEXT[Memory ContextPackVersion]
  CONTEXT --> CORE[Agent Core Step / Final Synthesis]
  CORE --> CAND[FinalCandidate]
  CAND --> GATE[Final Gate]
  GATE --> PUB[Agent Core Publication]
  PUB --> VIEW[Product authorized Projection]
  VIEW --> DELIVERY[ChannelDelivery / ClientRender / UserRead]
```

### Development View (4+1)

#### Overall — Repository Ownership and Dependency

```mermaid
flowchart TB
  WEB[apps/web] --> API[src/backend/zuno/api]
  API --> PRODUCT[zuno product application]
  PRODUCT --> AGENT[zuno/agent]
  AGENT --> KNOW[zuno/knowledge]
  AGENT --> MEMORY[zuno/memory]
  AGENT --> CAP[zuno/capability]
  AGENT --> TOOL[zuno/tool_runtime]
  KNOW & MEMORY & CAP & TOOL & AGENT --> PLATFORM[zuno/platform ports and adapters]
  DOCS[11 module docs + architecture] --> VERIFY[verifiers and repo tests]
```

#### Local — Module Package Rule

```mermaid
flowchart LR
  DOMAIN[Domain objects and transitions] --> APP[Application services]
  APP --> PORTS[Typed inbound and outbound Ports]
  ADAPTERS[Provider and storage Adapters] --> PORTS
  ADAPTERS --> INFRA[Infrastructure primitives]
  API[Inbound API / Worker] --> APP
  DOMAIN -.->|no Provider SDK / no cross-owner DB write| ADAPTERS
```

#### Local — Architecture Fact Source and Build Chain

```mermaid
flowchart LR
  ADR[Global principles / accepted ADR / Registry] --> MOD[Eleven canonical module docs]
  MOD --> ARCH[architecture.md integration]
  ARCH --> VIEWS[architecture-views.md explanatory Mermaid]
  VIEWS --> HTML[architecture.html renderer]
  MOD & ARCH --> PROGRAM[Confirmed Program]
  PROGRAM --> CODE[Code / Migration / Tests / Evidence]
  MOD & ARCH & VIEWS & HTML --> GUARD[semantic alignment verifier]
```

### Process View (4+1)

#### Overall — AgentRunGraph Controller Loop

```mermaid
flowchart TB
  REQ[RuntimeRequest] --> TASK[TaskContract / GoalVersion]
  TASK --> SNAP[ExecutionContextSnapshot]
  SNAP --> PLAN[Plan Proposal / Validate / Repair / Activate]
  PLAN --> CTRL[Controller Loop]
  CTRL --> ARB[Command arbitration + Domain/Checkpoint reconcile]
  ARB --> READY[ReadySet + liveness]
  READY --> RES[Budget / resource / capacity reservation]
  RES --> COMMIT[DispatchGroup / DispatchItem / StepRun commit]
  COMMIT --> SEND[LangGraph dynamic Send]
  SEND --> COLLECT[BranchResultRef collection]
  COLLECT --> REDUCE[Idempotent Reducer]
  REDUCE --> JOIN[Join Evaluation]
  JOIN -->|continue| CTRL
  JOIN -->|wait| WAIT[Interrupt / external wait]
  WAIT --> CTRL
  JOIN -->|complete| FINAL[Finalization / Publication / RunOutcome]
```

#### Local — Dispatch Commit Send Join and Replan

```mermaid
flowchart LR
  ACTIVE[Active PlanVersion] --> READY[Ready Step]
  READY --> CHECK[Dependency / input / security / capability / budget / conflict]
  CHECK --> TX[Transaction: DispatchGroup + Item + StepRun + reservations]
  TX --> EVENT[DispatchCommittedEvent]
  EVENT --> SEND[Send worker]
  SEND --> RESULT[Immutable BranchResultRef]
  RESULT --> GUARD[PlanVersion / epoch / fencing / hash guard]
  GUARD --> JOIN[JoinPolicy + Join Evaluation]
  JOIN -->|assumption invalid| BARRIER[Replan Barrier]
  BARRIER --> NEW[Validate and activate new PlanVersion]
```

#### Local — StepExecutionGraph and External Effect

```mermaid
flowchart TB
  LOAD[Load StepDefinition / verify epochs] --> INPUT[Resolve inputs / resource claims / budget]
  INPUT --> SEC[Preflight Security]
  SEC --> PROPOSE[ActionProposal / validation]
  PROPOSE --> PREP[PreparedToolAction when side effect]
  PREP --> APPROVE[Approval and latest Epoch]
  APPROVE --> CLAIM[Audit receipt / IdempotencyClaim / SecretLease]
  CLAIM --> EXEC[Execute owning module]
  EXEC --> OBS[Normalized Observation]
  OBS --> EVAL[Action Evaluation]
  EVAL --> ACCEPT[Step Acceptance]
  ACCEPT -->|unknown effect| RECON[EffectReconciliation]
  ACCEPT -->|continue / retry / repair / fallback / replan / complete| DECIDE[ControlDecision]
```

### Physical View (4+1)

#### Overall — Canonical Server Target

```mermaid
flowchart TB
  CLIENT[Web / Desktop / External API] --> API[Server-hosted Product API]
  API --> CONTROL[Controller role]
  API --> WORKER[Async worker roles]
  CONTROL --> PG[(PostgreSQL domain facts)]
  CONTROL --> CHECK[(LangGraph PostgreSQL Checkpointer)]
  WORKER --> PG
  WORKER --> OBJ[(S3-compatible Object Store)]
  WORKER --> Q[(RabbitMQ durable quorum queue)]
  WORKER --> IDX[(BM25 / Milvus / Neo4j projections)]
  CONTROL --> IDX
  CONTROL --> OBS[(Trace / Audit / Eval stores)]
  CONTROL & WORKER --> SECRET[Secret Manager / KMS Adapter]
```

#### Local — Domain Facts Checkpoint and Projections

```mermaid
flowchart LR
  PG[(PostgreSQL canonical domain facts)] --> OUTBOX[Transactional Outbox]
  OUTBOX --> Q[(RabbitMQ)]
  Q --> WORKER[Idempotent worker with Lease / Fencing]
  WORKER --> OBJ[(Immutable Object Store)]
  WORKER --> PROJ[(Rebuildable indexes and read models)]
  PROJ --> RECEIPT[Visibility / verification / watermark receipts]
  RECEIPT --> PG
  CHECK[(Checkpointer control state)] -. references committed generation .-> PG
```

#### Local — Recovery Reconciliation and Fencing

```mermaid
flowchart TB
  RESTART[Process or worker restart] --> DOMAIN[(Domain Store)]
  RESTART --> CHECK[(Checkpoint)]
  DOMAIN & CHECK --> GEN[Domain / Checkpoint Generation Reconciler]
  GEN --> ORPHAN[Run / Dispatch / Lease / Interrupt / Publication Reconcilers]
  ORPHAN --> EFFECT[Unknown Model / Tool / Index / Delivery Reconciliation]
  EFFECT --> RESUME[Resume first safe deterministic node]
  LEASE[Lease / heartbeat / fencing token] -.-> ORPHAN & RESUME
  INBOX[Inbox / Outbox / idempotency claim] -.-> ORPHAN & RESUME
```

### Scenarios View (4+1)

#### Overall — Strict Grounded Answer

```mermaid
sequenceDiagram
  participant U as User
  participant P as Product Surface
  participant S as Security
  participant A as Agent Core
  participant K as Knowledge
  participant C as Memory Context
  participant M as Model Gateway
  U->>P: submit strict grounded task
  P->>S: authenticate and authorize entry
  S-->>P: PrincipalContext and allowed scope
  P->>A: RuntimeRequest
  A->>K: KnowledgeQueryRequest + EvidenceRequirement
  K-->>A: SelectedEvidenceBundle + CitationLineage
  A->>C: build ContextPackVersion
  C-->>A: immutable ContextPackVersion
  A->>M: SYNTHESIZER / FINAL_CRITIC requirements
  M-->>A: candidate responses
  A->>A: Step Acceptance + Final Gate
  A-->>P: Publication + RunOutcome
  P-->>U: authorized answer / citations / quality disclosure
```

#### Local — Approval Interrupt Resume and Effect Reconciliation

```mermaid
sequenceDiagram
  participant A as Agent Core
  participant T as Tool Runtime
  participant S as Security
  participant P as Product Surface
  participant U as Approver
  participant I as Infrastructure
  A->>T: ActionProposal
  T->>S: PreparedToolAction + canonical hash
  S-->>P: ApprovalRequest
  P-->>U: authorized approval view
  U->>P: approval command
  P->>S: signed command and current principal
  S-->>A: SecurityApprovalDecision
  A->>T: resume execution
  T->>S: execute gate + latest Epoch
  T->>I: audit receipt + idempotency + lease + secret lease
  T-->>A: EffectReceipt or EffectReconciliation
  A->>A: ControlDecision
```

#### Local — Ingestion Publication Deletion and Revoke

```mermaid
sequenceDiagram
  participant P as Product
  participant S as Security
  participant I as Input
  participant K as Knowledge
  participant M as Memory
  participant F as Infrastructure
  P->>I: upload command
  I->>I: SourceObject / ParseSnapshot / Quality Gate
  I->>K: IndexableDocumentSnapshot
  K->>F: IndexWriteBatch
  F-->>K: write / visibility / verification receipts
  K->>K: Acceptance and Cutover
  P->>S: delete or revoke command
  S-->>I: authorized deletion
  I->>K: document tombstone
  K->>M: evidence invalidation
  K->>F: physical deletion request
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
  MM[05 Memory] --> KD
  MG[04 Model Gateway] --> AC[Agent Control Plane]
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
  CONSUMER[Consumer module] ==>|typed command or request| OWNER[Canonical Owner]
  OWNER -->|versioned domain result| CONSUMER
  OWNER -->|domain event + Outbox| OBS[Observability ingest]
  OWNER ==>|primitive request| INF[Infrastructure]
  INF -->|physical receipt only| OWNER
  PROJ[Product / Observability Projection] -. read only .-> CONSUMER
```

#### Local — Model Proposal and Deterministic Gates

```mermaid
flowchart LR
  MODEL[Model Proposal / Candidate / Score] --> SCHEMA[Schema and canonical validation]
  CLIENT[Client command] --> AUTH[Authentication and authorization]
  SCHEMA & AUTH --> OWNER[Canonical Owner application service]
  OWNER --> POLICY[Security / Budget / Acceptance / Final Gate]
  POLICY --> FACT[Versioned domain fact]
  BYPASS[Direct SDK / cross-owner DB write / frontend terminal state] --> REJECT[Repository and runtime guard]
```

### Component-and-Connector View (Views & Beyond)

#### Overall — Commands Results Events and Receipts

```mermaid
flowchart TB
  PRODUCT ==>|ProductCommand / RuntimeRequest| CORE[Agent Core]
  CORE ==>|Knowledge / Model / Memory / Capability / Tool request| DOMAIN[Canonical Domain Owners]
  DOMAIN -->|Domain result or Proposal| CORE
  CORE -->|PublicationEvent| PRODUCT
  DOMAIN -->|DomainEvent via Outbox| OBS[Observability and Eval]
  DOMAIN ==>|Physical operation| INF[Infrastructure]
  INF -->|Receipt / Watermark / Lease| DOMAIN
  SEC[Security] -. gates .-> PRODUCT & CORE & DOMAIN
```

#### Local — CrossModuleEnvelope Validation

```mermaid
flowchart LR
  PROD[Producer] --> ENV[CrossModuleEnvelopeV1]
  ENV --> CONTRACT[Contract / schema / enum version]
  ENV --> SCOPE[Tenant / Workspace / Principal]
  ENV --> EPOCH[Authorization / EffectiveSecurityEpoch]
  ENV --> ORDER[Aggregate version / expected generation]
  ENV --> TIME[Deadline / correlation / causation / trace]
  ENV --> HASH[Payload and schema hash]
  CONTRACT & SCOPE & EPOCH & ORDER & TIME & HASH --> VALID[Consumer validation]
  VALID -->|valid| INBOX[Inbox / idempotent handler]
  VALID -->|invalid| FAIL[Producer-owned Failure namespace]
```

#### Local — Capability Selection to Tool Execution

```mermaid
flowchart LR
  STEP[Step Requirement] --> SKILL[Skill discovery and progressive loading]
  SKILL --> AVAIL[CapabilityAvailabilitySnapshot]
  AVAIL --> SELECT[CapabilitySelectionResult]
  SELECT --> FEAS[Agent Core StepFeasibilityDecision]
  FEAS --> ACTION[ActionProposal with exact versions]
  ACTION --> TOOL[Tool Runtime PreparedToolAction]
  TOOL --> GATES[Security / Approval / Audit / Idempotency]
  GATES --> ATTEMPT[ToolAttempt]
  ATTEMPT --> EFFECT[EffectReceipt or EffectReconciliation]
```

### Data View (Views & Beyond)

#### Overall — Authoritative Facts and Rebuildable Projections

```mermaid
flowchart TB
  PG[(PostgreSQL)] --> DOMAIN[Structured canonical domain facts]
  OBJ[(Object Store)] --> LARGE[Large immutable payloads]
  CHECK[(LangGraph Checkpointer)] --> CONTROL[Graph control state]
  DOMAIN --> BM25[(BM25 projection)]
  DOMAIN --> VECTOR[(Vector projection)]
  DOMAIN --> GRAPH[(Graph projection)]
  DOMAIN --> PRODUCT[Product read models]
  DOMAIN --> OBS[Trace / Metric / Eval projections]
  LARGE --> BM25 & VECTOR & GRAPH
  CONTROL -. references .-> DOMAIN
```

#### Local — Knowledge and Memory Version Publication

```mermaid
flowchart LR
  SPEC[Knowledge IndexSpec or Memory ProjectionSpec] --> BATCH[IndexWriteBatch]
  BATCH --> WR[IndexWriteReceipt]
  WR --> VR[WriteVisibilityReceipt]
  VR --> VERIFY[IndexVerification]
  VERIFY --> MAN[Domain IndexManifest]
  MAN --> ACCEPT[Knowledge or Memory Acceptance]
  ACCEPT --> CUT[CAS IndexCutover]
  CUT --> WATER[ServingWatermark / active Snapshot]
```

#### Local — ExecutionContextSnapshot and Version Pinning

```mermaid
flowchart TB
  RUN[AgentRun] --> GOAL[GoalVersion]
  RUN --> PLAN[PlanVersion]
  RUN --> KS[KnowledgeSnapshot]
  RUN --> MS[MemorySnapshot]
  RUN --> MODEL[Model routing and prompt bundle]
  RUN --> CAP[CapabilityAvailabilitySnapshot / exact versions]
  RUN --> SEC[Security Policy / EffectiveSecurityEpoch]
  RUN --> RUNTIME[GraphBundle / RuntimePolicy / AnswerPolicy]
  GOAL & PLAN & KS & MS & MODEL & CAP & SEC & RUNTIME --> HASH[ExecutionContextSnapshot hash]
```

### Quality View (Views & Beyond)

#### Overall — Telemetry Audit Eval and Evidence Pipeline

```mermaid
flowchart LR
  OWNER[Domain transaction] --> OUTBOX[Transactional Outbox]
  OUTBOX --> ENV[TelemetryEnvelopeV1]
  ENV --> GUARD[Schema / Scope / Epoch / Redaction / Hash]
  GUARD --> INGEST[Append-only Ingest]
  INGEST --> TRACE[Trace Metric Log Projections]
  INGEST --> AUDIT[Accepted immutable AuditEvent]
  INGEST --> EVID[Evidence Registry]
  TRACE & EVID --> EVAL[EvalRun / MetricAttempt / Judge]
  EVAL --> BENCH[BenchmarkComparison]
  BENCH --> GATE[ReleaseGateEvaluation]
```

#### Local — Measurement and Release Gate States

```mermaid
stateDiagram-v2
  [*] --> PREPARED
  PREPARED --> RUNTIME_OBSERVED
  RUNTIME_OBSERVED --> MEASURED
  PREPARED --> BLOCKED
  PREPARED --> UNAVAILABLE
  RUNTIME_OBSERVED --> BLOCKED
  RUNTIME_OBSERVED --> UNAVAILABLE
  BLOCKED --> MEASURED
  UNAVAILABLE --> MEASURED
  MEASURED --> QUALITY_PROVEN
  state ReleaseGate {
    [*] --> PASSED
    [*] --> FAILED
    [*] --> BLOCKED_GATE
    [*] --> INCOMPARABLE
    [*] --> ERROR
  }
```

#### Local — Requirement Test Evidence and Release Gate

```mermaid
flowchart LR
  REQ[ARCH Requirement] --> CONTROL[Runtime or repository Control]
  CONTROL --> UNIT[Unit / Contract]
  CONTROL --> INT[Integration]
  CONTROL --> FAULT[Fault Injection]
  CONTROL --> E2E[E2E]
  CONTROL --> EVAL[Eval]
  UNIT & INT & FAULT & E2E & EVAL --> EVID[EvidenceRecord]
  EVID --> GATE[ReleaseGateEvaluation]
  GATE -->|hard constraints pass| ELIGIBLE[Eligible]
  GATE -->|failed blocked unavailable incomparable error| NOCLAIM[No release or quality claim]
```

## 三、Zuno Product Core

### Agentic GraphRAG Evidence and Agent Loop (Zuno)

#### Overall — Outer Agent Control and Inner Knowledge Retrieval

```mermaid
flowchart TB
  TASK[TaskContract / GoalVersion] --> NEED[Agent Core RetrievalNeedDecision]
  NEED --> REQ[EvidenceRequirement / KnowledgeQueryRequest]
  REQ --> KG[Fixed KnowledgeRetrievalGraph]
  KG --> PLAN[RetrievalPlan / RetrievalRound]
  PLAN --> RET[Parallel RetrieverBatch]
  RET --> LEDGER[EvidenceLedger / EvidenceFrontier]
  LEDGER --> VERDICT[RetrievalQualityVerdict]
  VERDICT -->|inner correction| CORR[CorrectiveRetrievalDecision + new RetrievalRound]
  CORR --> PLAN
  VERDICT -->|sufficient or partial| OUT[SelectedEvidenceBundle / KnowledgeRetrievalOutcome]
  VERDICT -->|task-level proposal| PROP[KnowledgeControlProposal]
  OUT --> ACCEPT[Agent Core Step Acceptance]
  PROP --> DECIDE[Agent Core ControlDecision]
  DECIDE -->|replan| BARRIER[Replan Barrier + new PlanVersion]
  ACCEPT --> FINAL[Final Gate / Publication]
```

#### Local — Evidence Lineage and Context Assembly

```mermaid
flowchart LR
  DOC[DocumentVersion] --> SPAN[SourceSpan]
  SPAN --> CHUNK[CitationChunk]
  CHUNK --> GRAPH[Entity / Relation / Community Evidence Backlink]
  GRAPH --> ATTEMPT[RetrieverAttempt]
  ATTEMPT --> ROUND[RetrievalRound]
  ROUND --> LEDGER[EvidenceLedger / EvidenceFrontier]
  LEDGER --> BUNDLE[SelectedEvidenceBundle]
  BUNDLE --> CONTEXT[ContextPackVersion]
  CONTEXT --> CLAIM[ClaimEvidenceBinding]
  CLAIM --> CITATION[Citation / Publication]
```

#### Local — Corrective Retrieval versus Agent Replan

```mermaid
flowchart TB
  GAP[Evidence gap or conflict] --> CLASS{Failure classification}
  CLASS -->|query / path / citation / conflict| KCORR[Knowledge CorrectiveRetrievalDecision]
  KCORR --> NEWROUND[Append-only next RetrievalRound]
  NEWROUND --> KVERDICT[Updated RetrievalQualityVerdict]
  CLASS -->|task goal / dependency / capability assumption invalid| KPROP[KnowledgeControlProposal]
  KPROP --> ADECIDE[Agent Core validates and decides]
  ADECIDE -->|replan accepted| BARRIER[Replan Barrier]
  BARRIER --> NEWPLAN[New immutable PlanVersion]
  ADECIDE -->|ask user / external tool / abstain| OTHER[Interrupt or terminal ControlDecision]
  CLASS -->|no safe evidence path| ABSTAIN[ABSTAIN_PROPOSAL]
```
