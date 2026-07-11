# Zuno Architecture Visual Atlas Source

updated: 2026-07-11  
status: normative-target-visual-source  
text_design_source: `docs/architecture/architecture.md`

本文件只维护 HTML Architecture Atlas 所需的 Mermaid 图。完整目标架构设计、模块职责、轻量实现边界和完成标准以 `architecture.md` 为准。

箭头规范：

```text
==>  command / control request
-->  data / result / state transfer
-.-> cross-cutting governance / observation / constraint
```

## 一、4+1 View Model

### Logical View (4+1)

#### Overall — Eleven Logical Capabilities

```mermaid
flowchart TB
  PS["1 Product Surface"]
  IN["2 Input"]
  KN["3 Knowledge"]
  MG["4 Model Gateway"]
  MM["5 Memory"]
  AC["6 Agent Core / Planning & Control"]
  CP["7 Capability"]
  TR["8 Tool Runtime"]
  SEC["9 Security"]
  OBS["10 Observability & Eval"]
  INF["11 Infrastructure"]
  PS ==>|RuntimeRequest| AC
  AC -->|RuntimeEvent · GroundedAnswer · ArtifactRef| PS
  PS ==>|SourceObject| IN
  IN -->|CanonicalDocumentIR · IndexHandoff| KN
  AC ==>|ModelCallRequest| MG
  MG -->|ModelResult · UsageRecord| AC
  AC ==>|MemoryReadRequest · MemoryCommit| MM
  MM -->|ContextPack · Memory refs| AC
  AC ==>|RetrievalPlan| KN
  KN -->|EvidenceBundle · RetrievalVerdict| AC
  AC ==>|CapabilityQuery| CP
  CP -->|CapabilityPlan · AllowedTools| AC
  AC ==>|ToolCallIntent| TR
  TR -->|NormalizedToolObservation| AC
  SEC -.-> PS & IN & KN & MG & MM & AC & CP & TR
  OBS -.-> PS & IN & KN & MG & MM & AC & CP & TR
  PS & IN & KN & MG & MM & AC & CP & TR & SEC & OBS --> INF
```

#### Local — Memory and Context Boundary

```mermaid
flowchart LR
  Input[Current input and observations] --> Sensory[Sensory Memory]
  Sensory --> Short[Short-term Memory]
  Long[Long-term Memory] --> Policy[Memory Policy]
  Entity[Entity Memory] --> Policy
  Short --> Policy
  Policy --> Rank[Retrieve and Rank]
  Rank --> Context[ContextPack]
  Context --> Agent[Agent Core]
  Agent --> Candidate[Memory Candidate]
  Candidate --> Review{Governance Review}
  Review -->|approved lesson or episode| Long
  Review -->|approved entity fact| Entity
  Review -->|pending or rejected| Ledger[Governance Ledger]
```

#### Local — Agent Core Capability Boundary

```mermaid
flowchart TB
  Strategy --> Planner --> Executor --> Observe --> Evidence --> Synthesis --> Reflect{Reflection}
  Reflect -->|PASS| Finalize
  Reflect -->|REWRITE_ANSWER| Synthesis
  Reflect -->|RETRIEVE_MORE| Replan --> Executor
  Reflect -->|USE_TOOL| Executor
  Reflect -->|ASK_USER| Interrupt
  Reflect -->|ABSTAIN| Finalize
  Executor ==>|RetrievalPlan| Knowledge
  Executor ==>|ToolCallIntent| Tool
  Planner ==>|ModelCallRequest| Model
  Strategy ==>|MemoryReadRequest| Memory
  Finalize ==>|MemoryCommit| Memory
```

### Development View (4+1)

#### Overall — Repository Ownership and Dependency Direction

```mermaid
flowchart TB
  Web[apps/web] -->|typed API| API[zuno/api]
  API -->|RuntimeRequest| Agent[zuno/agent]
  Agent --> Memory[zuno/memory]
  Agent --> Knowledge[zuno/knowledge]
  Agent --> Capability[zuno/capability]
  Agent --> Platform[zuno/platform]
  Memory --> Platform
  Knowledge --> Platform
  Capability --> Platform
  Docs[docs/architecture] --> Renderer[tools/agent]
  Renderer --> Tests[tests/repo]
  Tests -.-> Docs
```

#### Local — Runtime Package Dependency Rule

```mermaid
flowchart LR
  API --> Factory[RuntimeDependencyFactory]
  Factory --> Service[UnifiedAgentRuntimeService]
  Service --> Graph[Compiled LangGraph]
  Graph --> Nodes[Runtime Nodes]
  Nodes ==>|typed ports| Protocols[Runtime Protocols]
  Protocols --> Adapters[Model · Memory · Knowledge · Tool Adapters]
  Service --> Stores[Checkpoint · Event · Domain Stores]
  Adapters --> Stores
```

#### Local — Architecture Source Generation Chain

```mermaid
flowchart LR
  Text[architecture.md text-first design] --> Review[Architecture Review]
  Views[architecture-views.md Mermaid source] --> HTML[architecture.html visual atlas]
  Text --> MirrorText[.agent architecture.md]
  Views --> MirrorViews[.agent architecture-views.md]
  HTML --> MirrorHTML[.agent architecture.html]
  Text & Views & HTML --> Verify[renderer and repo guardrails]
  Verify -.->|findings| Text & Views
```

### Process View (4+1)

#### Overall — Unified LangGraph Runtime

```mermaid
flowchart TB
  Start([START]) --> Input[input_gate] --> Context[build_context] --> Strategy{strategy_select}
  Strategy -->|direct| Draft[draft_and_bind_claims]
  Strategy -->|react or plan| Plan[create_or_update_plan]
  Plan --> Execute[execute_step] --> Observe[observe]
  Observe -->|plan remains| Execute
  Observe -->|complete| Evidence[evidence_gate] --> Draft --> Reflect{reflection}
  Reflect -->|PASS| Finalize[finalize]
  Reflect -->|REWRITE_ANSWER| Revise[revise_draft] --> Draft
  Reflect -->|RETRIEVE_MORE| Replan[replan] --> Execute
  Reflect -->|USE_TOOL| Approval[approval and tool execution] --> Observe
  Reflect -->|ASK_USER| Interrupt[interrupt]
  Interrupt -->|Command resume| Execute
  Reflect -->|ABSTAIN| Finalize
  Finalize --> Commit[post_turn_commit] --> End([END])
```

#### Local — Single-step ReAct

```mermaid
flowchart LR
  Step[PlanStep] --> Prompt[Step Context Builder] --> Model[Executor Model]
  Model --> Decision{Action Decision}
  Decision -->|retrieve| Knowledge --> Obs[NormalizedObservation]
  Decision -->|tool| Tool --> Obs
  Decision -->|model transform| Transform --> Obs
  Obs --> Check{Acceptance Check}
  Check -->|accepted| Done[Step Completed]
  Check -->|continue within limit| Prompt
```

#### Local — Interrupt, Approval and Resume

```mermaid
sequenceDiagram
  participant G as LangGraph
  participant T as Tool Runtime
  participant S as Checkpoint Store
  participant API as Product API
  participant U as User
  G->>T: ToolRuntimeRequest
  T-->>G: approval_required
  G->>S: persist checkpoint and interrupt
  G-->>API: RuntimeEvent
  API-->>U: approval UI
  U->>API: approve or deny
  API->>G: Command(resume)
  G->>S: load checkpoint
  G->>T: execute with idempotency_key
  T-->>G: NormalizedToolObservation
```

### Physical View (4+1)

#### Overall — Lean Local-first Deployment

```mermaid
flowchart TB
  User[Browser or Desktop] --> Web[Web UI] ==>|HTTP and SSE| API[FastAPI]
  API ==>|RuntimeRequest| Runtime[Unified LangGraph Runtime]
  Runtime ==>|model calls| Provider[Configured Model Provider]
  API --> Queue[TaskQueuePort]
  Queue --> LocalWorker[In-process or local worker]
  Queue -.-> Rabbit[Optional RabbitMQ adapter]
  Runtime --> DB[(SQLite / SQLModel)]
  API --> Object[(Local Object Store)]
  Runtime --> Index[(BM25 · Vector · Graph Index)]
  Runtime --> Trace[(Local Trace Store)]
  Trace -.-> LangSmith[Optional LangSmith sink]
  Trace --> Eval[(Eval Reports)]
```

#### Local — Durable Storage and Recovery

```mermaid
flowchart LR
  Run[AgentRun] --> Checkpoint[(LangGraph Checkpoint)]
  Run --> Events[(Runtime Event Log)]
  Run --> Plans[(Plan Versions)]
  Run --> Observations[(Observations)]
  Run --> Interrupts[(Interrupts)]
  Run --> Claims[(Tool Idempotency Claims)]
  Restart[New process] --> Checkpoint
  Checkpoint --> Resume[Resume correct node]
  Claims --> Resume
```

#### Local — Model Connectivity

```mermaid
flowchart LR
  Binding[ModelSlotBinding] --> Gateway[Model Gateway]
  Gateway --> Local[Local Provider Adapter]
  Gateway --> Remote[Remote Provider Adapter]
  Gateway --> Mock[Mock Provider test only]
  Local --> Usage[Usage · Cost · Trace]
  Remote --> Usage
  Mock --> Usage
  Security -.-> Gateway
```

### Scenarios View (4+1)

#### Overall — Product Lifecycles

```mermaid
flowchart LR
  Config[Model Configuration] --> Workspace[Workspace]
  Workspace --> Prepare[Knowledge Preparation]
  Prepare --> Ask[Agent Task]
  Ask --> Answer[GroundedAnswer and Artifact]
  Answer --> Inspect[Citation and Trace Inspection]
  Inspect --> Feedback[Feedback]
  Ask -.-> Recovery[Refresh or Restart Recovery]
  Recovery --> Answer
```

#### Local — Document Preparation Scenario

```mermaid
sequenceDiagram
  participant U as User
  participant API as Product API
  participant Q as Task Queue
  participant P as Parse Worker
  participant K as Knowledge Indexer
  participant S as Stores
  U->>API: upload file
  API->>S: save SourceObject
  API->>Q: enqueue ParseJob
  Q->>P: claim job
  P->>S: save CanonicalDocumentIR and SourceSpan
  P->>K: IndexHandoffPayload
  K->>S: save IndexManifest
  API-->>U: indexed or blocked status
```

#### Local — Agent Task and Feedback

```mermaid
sequenceDiagram
  participant U as User
  participant API as Product API
  participant R as Unified Runtime
  participant K as Knowledge
  participant T as Tool Runtime
  U->>API: ask question
  API->>R: RuntimeRequest
  R->>K: RetrievalPlan
  K-->>R: EvidenceBundle
  R->>T: optional ToolCallIntent
  T-->>R: ToolObservation
  R-->>API: RuntimeEvents and GroundedAnswer
  API-->>U: answer, citations, artifact, trace
  U->>API: feedback
```

## 二、Views & Beyond

### Module View (Views & Beyond)

#### Overall — Eleven Modules to Six Runtime Domains

```mermaid
flowchart LR
  PS[Product Surface] --> PA[Product & API]
  IN[Input] --> IK[Input & Knowledge]
  KN[Knowledge] --> IK
  MG[Model Gateway] --> AR[Agent Core Runtime]
  MM[Memory] --> AR
  AC[Agent Core] --> AR
  CP[Capability] --> CT[Capability & Tool]
  TR[Tool Runtime] --> CT
  SEC[Security] --> GO[Governance & Observability]
  OBS[Observability & Eval] --> GO
  INF[Infrastructure] --> LI[Local Infrastructure]
```

#### Local — Agent Core Module

```mermaid
flowchart TB
  State[Runtime State] --> Context[Context Builder]
  Context --> Strategy[Strategy Selector]
  Strategy --> Planner[Planner and Validator]
  Planner --> Executor[Step Executor Registry]
  Executor --> Observe[Observation Normalizer]
  Observe --> Reflect[Reflection and Replan]
  Reflect --> Synthesis[Grounded Synthesis]
  Synthesis --> Finalize[Finalize and Memory Bridge]
  Limits[Budget and Stop Controller] -.-> Strategy & Planner & Executor & Reflect
```

#### Local — Knowledge Module

```mermaid
flowchart LR
  IR[CanonicalDocumentIR] --> Chunk[Parent and Citation Chunks]
  Chunk --> BM25[(BM25)]
  Chunk --> Vector[(Vector)]
  Chunk --> Graph[(Graph Index)]
  Query[RetrievalPlan] --> BM25 & Vector & Graph
  BM25 & Vector & Graph --> Fusion[RRF Fusion]
  Fusion --> Rerank[Rerank and Expansion]
  Rerank --> Ledger[EvidenceLedger]
  Ledger --> Verdict[RetrievalQualityVerdict]
```

### Component-and-Connector View (Views & Beyond)

#### Overall — Runtime Components and Contracts

```mermaid
flowchart TB
  Product ==>|RuntimeRequest| Service[Runtime Service]
  Service ==>|state| Graph[Agent Graph]
  Graph ==>|ModelCallRequest| Model[Model Gateway]
  Graph ==>|MemoryReadRequest| Memory
  Graph ==>|RetrievalPlan| Knowledge
  Graph ==>|CapabilityQuery| Capability
  Graph ==>|ToolCallIntent| Tool
  Model -->|ModelResult| Graph
  Memory -->|ContextPack| Graph
  Knowledge -->|EvidenceBundle| Graph
  Capability -->|CapabilityPlan| Graph
  Tool -->|NormalizedToolObservation| Graph
  Graph -->|RuntimeEvent · GroundedAnswer| Product
```

#### Local — Model and Memory Connectors

```mermaid
sequenceDiagram
  participant A as Agent Core
  participant M as Model Gateway
  participant MEM as Memory
  A->>MEM: MemoryReadRequest
  MEM-->>A: ContextPack and selected refs
  A->>M: ModelCallRequest(role, schema, budget)
  M-->>A: ModelResult and UsageRecord
  A->>MEM: MemoryCommit(candidate, trace refs)
  MEM-->>A: commit status
```

#### Local — Knowledge and Tool Connectors

```mermaid
sequenceDiagram
  participant A as Agent Core
  participant K as Knowledge
  participant C as Capability
  participant T as Tool Runtime
  A->>K: RetrievalPlan
  K-->>A: EvidenceBundle and RetrievalVerdict
  A->>C: CapabilityQuery
  C-->>A: CapabilityPlan and AllowedTools
  A->>T: ToolCallIntent
  T-->>A: approval_required or NormalizedToolObservation
```

### Data View (Views & Beyond)

#### Overall — Authoritative Data Ownership

```mermaid
flowchart TB
  Product[Workspace · Session · Task · Message] --> Run[AgentRun]
  Source[SourceObject · DocumentVersion] --> IR[DocumentIR · SourceSpan]
  IR --> Index[IndexManifest · CitationChunk]
  Run --> Plan[PlanVersion · Observation · Interrupt]
  Index --> Evidence[EvidenceLedger]
  Plan --> Answer[Claim · CitationBinding · GroundedAnswer]
  Evidence --> Answer
  Answer --> Artifact[Artifact · Feedback]
  Run --> Memory[MemoryCandidate · MemoryRecord · EntityFact]
  Run --> Trace[TraceSpan · Usage · EvalRun]
```

#### Local — Document and Citation Lineage

```mermaid
flowchart LR
  Source[SourceObject] --> Version[DocumentVersion]
  Version --> IR[CanonicalDocumentIR]
  IR --> Block[DocumentBlock]
  Block --> Span[SourceSpan]
  Block --> Chunk[CitationChunk]
  Chunk --> Index[IndexManifest]
  Index --> Evidence[EvidenceLedgerRecord]
  Evidence --> Binding[ClaimEvidenceBinding]
  Binding --> Citation[CitationView]
```

#### Local — Runtime and Memory Lifecycle

```mermaid
flowchart LR
  Request[RuntimeRequest] --> Run[AgentRun]
  Run --> Checkpoint[Checkpoint]
  Run --> Event[RuntimeEvent]
  Run --> Observation[NormalizedObservation]
  Run --> Final[GroundedAnswer]
  Final --> Raw[RawMemoryEvent]
  Raw --> Candidate[MemoryCandidate]
  Candidate --> Review[GovernanceRecord]
  Review -->|approved| Record[MemoryRecord]
  Record --> Context[Future ContextPack]
```

### Quality View (Views & Beyond)

#### Overall — Quality Attributes and Gates

```mermaid
flowchart TB
  Runtime[Agent Runtime]
  Security[Security]
  Grounding[Evidence and Citation]
  Recovery[Checkpoint and Idempotency]
  Observability[Trace and Diagnostics]
  Performance[Latency and Throughput]
  Cost[Budget and Usage]
  Privacy[Redaction and Memory Governance]
  Eval[Benchmark and Release Gate]
  Security -.-> Runtime
  Grounding -.-> Runtime
  Recovery -.-> Runtime
  Observability -.-> Runtime
  Performance -.-> Runtime
  Cost -.-> Runtime
  Privacy -.-> Runtime
  Eval -.-> Runtime
```

#### Local — Security and Observability Joint Chain

```mermaid
flowchart LR
  Input[Input Gate] --> Context[Memory and Model Context Gate]
  Context --> Retrieval[Retrieval Gate]
  Retrieval --> Tool[Tool Gate]
  Tool --> Output[Output Gate]
  Output --> Artifact[Artifact Gate]
  Input & Context & Retrieval & Tool & Output & Artifact --> Audit[(Audit Events)]
  Input & Context & Retrieval & Tool & Output & Artifact --> Trace[(Trace Spans)]
  Trace -.-> LangSmith[Optional LangSmith]
```

#### Local — Trace, Failure Buckets and Release Gate

```mermaid
flowchart LR
  Run[AgentRun] --> Spans[Span Tree]
  Spans --> Buckets[Failure Buckets]
  Spans --> Metrics[Recall · Correctness · Citation · Latency · Token · Cost]
  Buckets --> Diagnostics[Environment and Profile Completeness]
  Metrics --> Gate{Release Gate}
  Diagnostics --> Gate
  Gate -->|measured pass| Pass[quality proven]
  Gate -->|measured fail| Fail[quality failed]
  Gate -->|blocked| Blocked[quality not yet proven]
```

## 三、Zuno Product Core

### Agentic GraphRAG Evidence and Agent Loop (Zuno)

#### Overall — Agentic GraphRAG Pipeline

```mermaid
flowchart TB
  Question[Question and ContextPack] --> Need{Need Retrieval?}
  Need -->|yes| Strategy[Query Strategy]
  Strategy --> BM25[BM25]
  Strategy --> Vector[Vector]
  Strategy --> Graph[Graph Traversal]
  BM25 & Vector & Graph --> Fusion[RRF Fusion]
  Fusion --> Rerank[Rerank and Expansion]
  Rerank --> Ledger[EvidenceLedger]
  Ledger --> Quality{Retrieval Quality Gate}
  Quality -->|sufficient| Claims[Claim Extraction and Binding]
  Quality -->|insufficient| Correct[Corrective Action]
  Correct --> Strategy
  Claims --> Synthesis[Grounded Synthesis]
  Synthesis --> Reflect{Reflection}
  Reflect -->|PASS| Final[GroundedAnswer]
  Reflect -->|RETRIEVE_MORE| Correct
  Reflect -->|ABSTAIN| Abstain[Abstained Answer]
```

#### Local — Corrective Retrieval Loop

```mermaid
flowchart LR
  Round[Retrieval Round] --> Verdict{Quality Verdict}
  Verdict -->|doc miss| Rewrite[Rewrite or Multi Query]
  Verdict -->|text miss| HyDE[HyDE or Step-back]
  Verdict -->|entity miss| Entity[Entity Decomposition]
  Verdict -->|relation miss| Relation[Graph Relation Query]
  Verdict -->|contradiction| Diversify[Diversify Sources]
  Rewrite & HyDE & Entity & Relation & Diversify --> Next[Next RetrievalPlan]
  Next --> Round
  Verdict -->|sufficient| Stop[Stop Retrieval]
  Verdict -->|limits reached| Abstain[Abstain or Ask User]
```

#### Local — EvidenceLedger and Claim Binding

```mermaid
flowchart LR
  R1[Round 1 Evidence] --> Ledger[EvidenceLedger]
  R2[Round 2 Evidence] --> Ledger
  R3[Round 3 Evidence] --> Ledger
  Ledger --> Dedup[Deduplicate · Version Check · Contradiction]
  Dedup --> Claims[Structured Claims]
  Claims --> Binder[Claim-level Citation Binder]
  Dedup --> Binder
  Binder --> Supported[Supported Claims]
  Binder --> Unsupported[Unsupported Claims]
  Supported --> Answer[GroundedAnswer]
  Unsupported --> Reflection[Reflection: rewrite, retrieve more, abstain]
```
