# Zuno Architecture Visual Atlas Source

本图源展示 Python-only Target、10 个逻辑模块候选、模块化 Backend + Worker 默认起点、Evidence-gated Physical Service Split、Research → Capability → Domain Result、Native / Embedded Product Mode、FastAPI Application Interface、LangGraph orchestration provider、OTel-compatible Observability Contract、EvidenceRequirement、ConflictProposal、PostgreSQL Domain State 和 Runtime Checkpoint 的边界；这些图不把 Target 伪装成 Current。

updated: 2026-08-14
status: normative-target-visual-source
architecture_state: ACCEPTED_TARGET
text_design_source: `docs/architecture/architecture.md`
canonical_taxonomy_source: `docs/README.md` and `docs/architecture/README.md`

本文件是总体架构的展示图源。服务、数据、状态和 Owner 事实以 `architecture.md` 与专题 Canonical 文档为准；本文件不创建第二套 Contract。

## Responsibility Lens 与 10 个候选模块

下面五层用于帮助读者理解跨层责任，不代表最终五个模块、五个服务或五个团队。10 个模块图也是 Candidate Map，不是冻结后的模块或服务清单：

1. **Legal Work Surface**：案件分析、合同审查、法律研究、报告和 Human Review；
2. **Legal Domain & Intelligence**：Evidence、Fact / Event、Conflict、Finding、Version 和 Staleness；
3. **Agentic Knowledge & Context**：Ingestion、Hybrid Retrieval、条件 Graph、Citation 和 Memory；
4. **Agent Runtime & Execution**：Single Controller、Plan、受控 Worker、Model、Skill 和 Tool；
5. **Trust & Platform Engineering**：Permission、Approval、Sandbox、Audit、Observability、Eval 和 Infrastructure。

`NEW_10_MODULE_SET: CANDIDATE_ONLY`、`FINAL_MODULE_COUNT: NOT_FROZEN`、`MODULE_DECOMPOSITION_GATE: NOT_OPEN`。Logical Capability、Physical Service、Worker、Process、Container、Database 和 Team 不做一一映射。

## Product Context

### Product Context View

```mermaid
flowchart LR
  USER[律师 / 法官 / 专业用户] --> SURFACE[Zuno Workbench / WorkBuddy / Dify / Court Host]
  SURFACE --> EDGE[Host / API Boundary]
  EDGE --> DOMAIN[Zuno Legal Backend / Domain Owner]
  DOMAIN --> WORK[Review / Finding / WorkProduct]
```

### Business Flow View

```mermaid
flowchart TB
  subgraph A[FLOW A — Simple Grounded QA]
    AQ[Question / Scope] --> AR[Authorization + Knowledge Readiness]
    AR --> AE[Retrieve Evidence / Citation]
    AE --> AG[Deterministic Final Gate]
    AG --> AO[Response]
  end
  subgraph B[FLOW B — Complex Legal Analysis]
    BM[Matter / Version Set] --> BR[Readiness + Continuous Authorization]
    BR --> BP[Dynamic DAG Plan]
    BP --> BC[Retrieval / Capability / optional Specialist]
    BC --> BJ[Join / Evaluation / Synthesis]
    BJ --> BD[Domain Admission / Human Review]
    BD --> BW[Versioned WorkProduct]
  end
  subgraph C[FLOW C — Controlled External Effect]
    CT[Tool Proposal] --> CP[PreparedAction]
    CP --> CG[Security / Approval Gate]
    CG --> CE[Execute / EffectReceipt]
    CE --> CR[Reconcile if Unknown]
    CR --> CF[Final Gate / Domain Result]
  end
```

## Logical Architecture

### Logical Capability View

```mermaid
flowchart TB
  P[01 Product Surface & Agent Portfolio]
  D[02 Legal Domain & Work Product]
  K[03 Knowledge & Evidence]
  A[04 Agent Runtime & Multi-Agent]
  CT[05 Capability / Skill & Tool Runtime]
  M[06 Model Gateway]
  X[07 Memory & Context]
  S[08 Security & Governance]
  O[09 Observability & Evaluation]
  I[10 Infrastructure & Persistence]
  P --> D & A
  A --> K & CT & M & X
  CT --> D
  K --> D
  M --> A
  S -.-> P & D & K & A & CT & M & X
  O -.-> P & D & K & A & CT & M & X & S
  I -.-> D & K & A & CT & M & X & O
```

### Provider Boundary View

```mermaid
flowchart LR
  RESEARCH[Research Artifact] --> CAP[Capability Contract]
  CAP --> CP[Provider Conformance / Evaluation]
  CP --> PROPOSAL[Proposal / Candidate / Observation]
  PROVIDER[Algorithm / LLM / OSS / API Provider]
  PROVIDER --> CP
  TOOL[Tool / MCP / External Action] --> PREP[PreparedAction]
  PREP --> GATE[Security / Approval Gate]
  GATE --> EFFECT[EffectReceipt / Reconcile]
  PROPOSAL --> OWNER[Domain Owner]
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
  PORTFOLIO[Agent Portfolio] --> SUBMIT[Agent Invocation]
  SUBMIT --> COORD[Single Controller]
  COORD --> PLAN[PlanVersion / Budget / Policy]
  PLAN --> DAG[Fixed Graph + Dynamic Plan DAG]
  DAG --> STEP[Step / Capability / Tool]
  DAG --> SPEC[Specialist Agent only with independent boundary]
  STEP --> JOIN[Join / Evaluation]
  SPEC --> JOIN
  JOIN --> COORD
  COORD --> HITL[Reflection / Replan / Human Review]
  HITL --> DOMAIN[Domain Admission]
```

### Runtime and Domain State View

```mermaid
flowchart TB
  DOMAIN[DOMAIN STATE<br/>Matter / FactVersion / FindingVersion / HumanDecision / WorkProduct]
  RUNTIME[RUNTIME STATE<br/>Run / PlanVersion / Step / Branch / Checkpoint]
  MEMORY[MEMORY STATE<br/>Summary / Preference / Experience / Context]
  KNOW[KNOWLEDGE PROJECTION<br/>Index / Graph / Knowledge View / Generation]
  DOMAIN -->|Snapshot / Version / Dependency| RUNTIME
  RUNTIME -->|Proposal / Admission Input| DOMAIN
  MEMORY -->|Policy-scoped context| RUNTIME
  KNOW -->|Evidence / Readiness / Citation| RUNTIME
  KNOW -.->|not Domain Truth| DOMAIN
  EFFECT[EffectReceipt] --> RECON[Reconciliation]
  RECON --> RUNTIME & DOMAIN
```

## Physical Deployment and Service Split

### Physical Deployment Decision View

```mermaid
flowchart TB
  START[Modular Backend + Independent Workers] --> GATE{Evidence Gate}
  GATE -->|No independent boundary evidence| KEEP[Keep together / Library / Worker]
  GATE -->|Independent Scaling| SPLIT[Split specific boundary]
  GATE -->|Failure Isolation| SPLIT
  GATE -->|Security / Secret Isolation| SPLIT
  GATE -->|Distinct Availability| SPLIT
  GATE -->|Independent Deployment Lifecycle| SPLIT
  GATE -->|Stable Cross-host API + distinct ownership| SPLIT
  SPLIT --> CONTRACT[Versioned Contract + Operational Owner]
```

### Deployment Profiles View

```mermaid
flowchart LR
  DEV[Developer Compose] --> BASE[Modular Backend + Workers]
  BASE --> GATE{Evidence Gate}
  GATE -->|No split evidence| KEEP[Keep together]
  GATE -->|Validated boundary| DEPLOY[Separate deployment profile]
  DEPLOY --> SCALE[Independent scaling / failure / security / lifecycle as justified]
```

## Data and Recovery

### Data Ownership View

```mermaid
flowchart TB
  DOMAIN[Legal Domain Owner] --> PDB[(PostgreSQL Canonical Domain State)]
  RUNTIME[Agent Runtime Owner] --> CDB[(LangGraph Checkpoint / Runtime Store)]
  KNOW[Knowledge & Evidence Owner] --> OBJ[(Object + Index + Graph Projections)]
  MEMORY[Memory Owner] --> MEM[(Memory Provider / Context Store)]
  MODEL[Model Gateway Owner] --> USAGE[(Usage / Cost Receipt)]
  TOOL[Capability / Tool Owner] --> EFFECT[(Effect Receipt / Reconcile)]
  SEC[Security Owner] --> POLICY[(Policy / Security Epoch)]
  OBS[Observability & Eval Owner] --> TELEMETRY[(OTel-compatible Trace / Eval / Release Gate)]
  INF[Infrastructure Owner] --> INFRA[(Queue / Worker / Backup / DR)]
  PDB -. Reference / Snapshot .-> CDB & OBJ & EFFECT & TELEMETRY
  POLICY -. Current Authorization .-> DOMAIN & RUNTIME & KNOW & MEMORY & MODEL & TOOL
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
