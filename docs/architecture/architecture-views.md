# Zuno Architecture Visual Atlas Source

本图源展示 Python-only Target、FastAPI Application Interface、LangGraph orchestration provider、EvidenceRequirement、ConflictProposal、PostgreSQL Domain State 和 Runtime Checkpoint 的边界；这些图不把 Target 伪装成 Current。

updated: 2026-08-13
status: normative-target-visual-source
architecture_state: ACCEPTED_TARGET
text_design_source: `docs/architecture/architecture.md`
canonical_taxonomy_source: `docs/README.md` and `docs/decisions/0011-architecture-document-taxonomy.md`

本文件是总体架构的展示图源。服务、数据、状态和 Owner 事实以 `architecture.md` 与专题 Canonical 文档为准；本文件不创建第二套 Contract。

## 五层责任视图

下面五层用于帮助读者理解责任，不代表最终五个模块、五个服务或五个团队：

1. **Legal Work Surface**：案件分析、合同审查、法律研究、报告和 Human Review；
2. **Legal Domain & Intelligence**：Evidence、Fact / Event、Conflict、Finding、Version 和 Staleness；
3. **Agentic Knowledge & Context**：Ingestion、Hybrid Retrieval、条件 Graph、Citation 和 Memory；
4. **Agent Runtime & Execution**：Single Controller、Plan、受控 Worker、Model、Skill 和 Tool；
5. **Trust & Platform Engineering**：Permission、Approval、Sandbox、Audit、Observability、Eval 和 Infrastructure。

`FINAL_MODULE_COUNT: NOT_DECIDED`。Logical Capability、Physical Service、Worker、Process、Container、Database 和 Team 不做一一映射。

## Product Context

### Product Context View

```mermaid
flowchart LR
  USER[律师 / 法官 / 专业用户] --> SURFACE[Zuno Web / Desktop / WorkBuddy / MCP Client]
  SURFACE --> EDGE[edge-api]
  EDGE --> DOMAIN[platform-domain-service]
  DOMAIN --> WORK[Review / Finding / WorkProduct]
```

### Business Flow View

```mermaid
flowchart LR
  M[Create Matter] --> D[Upload DocumentVersion]
  D --> S[Domain Snapshot / DomainVersion]
  S --> A[Agent Coordinator + PlanVersion]
  A --> G[Evidence / Security / Budget Gate]
  G --> K[Retrieval / Memory / Capability / Tool Proposal]
  K --> P[Domain Proposal + Evidence lineage]
  P --> V[Domain Owner validation/version]
  V --> F[Finding + Human Review]
  F --> W[WorkProduct / Response]
```

## Logical Architecture

### Logical Capability View

```mermaid
flowchart TB
  PRODUCT[Product Surface]
  DOMAIN[Legal Domain Kernel]
  AGENT[Composable Agent Runtime]
  KNOW[Evidence-driven Knowledge]
  TOOL[Tool / Sandbox]
  SECURITY[Security Decision + Enforcement]
  EVAL[Legal Eval + Observability]
  PRODUCT --> DOMAIN
  PRODUCT --> AGENT
  AGENT --> KNOW
  AGENT --> TOOL
  AGENT --> DOMAIN
  SECURITY -.-> PRODUCT & DOMAIN & AGENT & KNOW & TOOL
  EVAL -.-> DOMAIN & AGENT & KNOW & TOOL
```

### Provider Boundary View

```mermaid
flowchart LR
  CONTRACT[Canonical Contract]
  PROVIDER[Local / LLM / OSS / API / MCP Provider]
  PROPOSAL[Proposal / Candidate / Observation / Reference / Receipt]
  OWNER[Canonical Owner]
  CONTRACT --> PROVIDER --> PROPOSAL --> OWNER
  OWNER --> VERSION[Versioned Business State]
```

## Legal Domain

### Domain State View

```mermaid
flowchart LR
  MATTER[Matter] --> DOC[DocumentVersion]
  DOC --> EVIDENCE[Evidence]
  EVIDENCE --> CLAIM[Claim / Fact / Event proposal]
  CLAIM --> FINDING[Finding]
  FINDING --> DECISION[HumanDecision]
  DECISION --> PRODUCT[WorkProduct]
```

### Staleness and Review View

```mermaid
flowchart LR
  NEW[New EvidenceVersion] --> DEP[Dependency lookup]
  DEP --> STALE[Fact/Finding STALE or REVIEW_REQUIRED]
  STALE --> RUN[Bounded re-evaluation Run]
  RUN --> PROPOSAL[New Proposal]
  PROPOSAL --> OWNER[Domain Owner + Human Review]
  OWNER --> COMMIT[New Canonical Version]
```

## Multi-Agent Runtime

### Agent Runtime View

```mermaid
flowchart TB
  SUBMIT[FastAPI Run Submit] --> COORD[Single Controller]
  COORD --> PLAN[PlanVersion / Budget / Policy]
  PLAN --> ROLE[Role Profiles / Dynamic Plan DAG]
  ROLE --> WORKER[Ephemeral Workers / Parallel Tools]
  WORKER --> GATE[Evidence / Security / Budget Gate]
  GATE --> OBS[Observation / Proposal / Receipt]
  OBS --> COORD
  COORD --> HITL[HITL / Replan / Finalize]
  HITL --> DOMAIN[Domain Owner Commit]
```

### Runtime and Domain State View

```mermaid
flowchart LR
  RUNTIME[AgentRun / Plan / Step / Checkpoint]
  DOMAIN[PostgreSQL Domain State]
  RUNTIME -->|versioned input/output| DOMAIN
  DOMAIN -->|generation / dependency / policy| RUNTIME
  EFFECT[EffectReceipt] --> RECON[Reconciliation]
  RECON --> RUNTIME
  RECON --> DOMAIN
```

## Microservice and Deployment

### Microservice View

```mermaid
flowchart TB
  CLIENT[External surfaces / WorkBuddy / MCP] --> EDGE[edge-api]
  EDGE --> PLATFORM[platform-domain-service]
  EDGE --> AGENT[agent-runtime-service]
  EDGE --> KNOW[knowledge-service]
  AGENT --> TOOL[tool-sandbox-service]
  KNOW --> WK[Knowledge workers]
  AGENT --> AW[Agent workers]
  TOOL --> SW[Sandbox workers]
  PLATFORM --> DB[(PostgreSQL logical schemas)]
  NOTE[Candidate boundary; count remains revisable] -.-> EDGE
```

### Deployment Profiles View

```mermaid
flowchart LR
  DEV[Developer Compose] --> STAGE[Staging Multi-service]
  STAGE --> PROD[Production HA / scalable profile]
  PROD --> SCALE[Independent service/worker scaling]
  PROD --> ISOLATE[Failure + security isolation]
```

## Data and Recovery

### Data Ownership View

```mermaid
flowchart TB
  PLATFORM[Platform Domain Owner] --> PDB[(Domain PostgreSQL)]
  RUNTIME[Runtime Owner] --> CDB[(Checkpoint / Runtime Store)]
  KNOW[Knowledge Owner] --> OBJ[(Object + Index + Graph Projections)]
  TOOL[Tool Owner] --> EFFECT[(Effect Receipt / Reconcile)]
  EVAL[Eval Owner] --> METRIC[(Trace / Eval / Release Gate)]
  PDB -. API/Event/Reference .-> CDB & OBJ & EFFECT & METRIC
```

### Failure and Recovery View

```mermaid
sequenceDiagram
  participant R as Runtime
  participant D as Domain DB
  participant T as Tool/Sandbox
  participant C as Checkpointer
  R->>T: PreparedAction + IdempotencyKey
  T-->>R: EffectReceipt or UNKNOWN_EFFECT
  R->>D: Commit business effect reference
  R->>C: Save control checkpoint
  Note over R,C: crash / duplicate delivery
  R->>D: Read DomainGeneration + Receipt
  R->>T: Reconcile ProviderOperationId
  R->>C: Resume only after domain/control agreement
```

## Quality and Security

### A/B/C Eval View

```mermaid
flowchart LR
  A[WorkBuddy Generic Legal Agent] --> METRIC[Legal + efficiency metrics]
  B[WorkBuddy + Zuno Capabilities] --> METRIC
  C[Zuno Native Runtime] --> METRIC
  METRIC --> GATE{C>B?}
  GATE -->|yes, repeatable and attributable| KEEP[Runtime Target may survive]
  GATE -->|no / C≈B| DELETE[Delete or shrink extra runtime complexity]
```

### Security Verification View

```mermaid
flowchart TB
  ARTIFACT[Source / Build / SBOM / Signed Artifact]
  NETWORK[No-egress / Allowlist]
  ACCESS[Secret / Tenant / Permission]
  EXEC[Prompt Injection / Sandbox / Side Effect]
  TRACE[Domain / Tool / Model / Human Trace]
  ARTIFACT & NETWORK & ACCESS & EXEC & TRACE --> ATTEST[Security Evidence / Attestation]
```
