# Zuno Architecture Visual Atlas Source

本文件是 `docs/architecture/architecture.md` 的图源配对。它把九个逻辑责任域、Platform / Infrastructure Responsibility Layer、Optional Context Provider 和三条代表性业务流画出来；它不拥有第二套架构事实，也不把 Target 伪装成 Current。图源对应 Python-only Target、FastAPI Application Interface、LangGraph Control Provider、PostgreSQL Domain Store、Independent Workers 和 OTel-compatible Evaluation boundary。

updated: 2026-08-15
status: normative-target-visual-source
architecture_state: ACCEPTED_TARGET
text_design_source: `docs/architecture/architecture.md`
canonical_taxonomy_source: `docs/architecture/README.md` and `docs/decisions/0013-round-02-responsibility-taxonomy.md`

## Product and Business Flows

### Product Context View

```mermaid
flowchart LR
  USER[专业用户 / 法院系统] --> HOST[Generic Host / Zuno Entry]
  HOST --> APP[01 Application & Integration]
  APP --> DOMAIN[02 Legal Domain & Work Product]
  APP --> CAP[Legal Capability / Typed Result]
  DOMAIN --> RESULT[Versioned WorkProduct / Publication]
```

### Business Flow View

```mermaid
flowchart TB
  subgraph A[Simple QA — Host-owned path is allowed]
    AQ[Question + material scope] --> AR[Authorization + Readiness]
    AR --> AE[Source retrieval + citation]
    AE --> AF[Answer eligibility / publication]
  end
  subgraph B[Complex Legal Analysis]
    BM[Matter + document versions] --> BP[Bounded plan / capability]
    BP --> BE[Evidence + proposal]
    BE --> BA[Admission + WorkProduct]
  end
  subgraph C[Controlled External Effect]
    CT[Tool proposal] --> CP[PreparedAction + approval]
    CP --> CE[Execute + EffectReceipt]
    CE --> CR[Reconcile unknown outcome]
  end
```

## Responsibility Taxonomy

### Logical Capability View

```mermaid
flowchart TB
  APP[01 Application & Integration]
  DOMAIN[02 Legal Domain & Work Product]
  KNOW[03 Knowledge & Evidence]
  RUN[04 Agent Runtime & Control]
  CAP[05 Capability & Skill]
  TOOL[06 Tool Runtime & Effects]
  MODEL[07 Model Gateway]
  SEC[08 Security & Governance]
  OBS[09 Observability & Evaluation]
  PLATFORM[Platform / Infrastructure Layer]
  CONTEXT[Optional Context Provider]
  APP --> DOMAIN & RUN
  RUN --> KNOW & CAP & TOOL & MODEL
  KNOW --> DOMAIN
  CAP --> DOMAIN
  TOOL --> DOMAIN
  SEC -. policy .-> APP & DOMAIN & KNOW & RUN & CAP & TOOL & MODEL
  OBS -. projection .-> APP & DOMAIN & KNOW & RUN & TOOL & SEC
  PLATFORM -. primitives .-> DOMAIN & KNOW & RUN & TOOL & MODEL & OBS
  CONTEXT -. policy-scoped context .-> RUN
```

### Provider Boundary View

```mermaid
flowchart LR
  RESEARCH[Research artifact] --> CAPABILITY[Capability contract]
  PROVIDER[Algorithm / LLM / API / OSS] --> CONFORM[Conformance + evaluation]
  CAPABILITY --> CONFORM --> PROPOSAL[Proposal / candidate / observation]
  PROPOSAL --> DOMAIN[Domain owner]
  TOOLDEF[Tool / MCP definition] --> ACTION[PreparedAction]
  ACTION --> GATE[Authorization + approval]
  GATE --> EFFECT[EffectReceipt / reconciliation]
```

## Domain and Control State

### Domain State View

```mermaid
flowchart LR
  MATTER[Matter] --> DOC[DocumentVersion]
  DOC --> CLAIM[Claim]
  CLAIM --> EVIDENCE[Evidence]
  EVIDENCE --> FINDING[Finding]
  FINDING --> HUMAN[HumanDecision]
  HUMAN --> PRODUCT[WorkProduct]
```

### Staleness and Review View

```mermaid
flowchart LR
  NEW[New Evidence / version] --> DEP[Dependency lookup]
  DEP --> STALE[WorkProduct invalidation truth]
  STALE --> RUN[Bounded reevaluation]
  RUN --> PROPOSAL[Finding proposal]
  PROPOSAL --> ADMIT[Domain admission]
  ADMIT --> VERSION[New WorkProduct version]
```

## Agent Runtime and Control

### Agent Runtime View

```mermaid
flowchart TB
  INTAKE[InvocationDecision] --> CTRL[Single Controller]
  CTRL --> PLAN[PlanVersion + budget]
  PLAN --> STEP[Step / Capability / Tool]
  STEP --> JOIN[Join + evaluation]
  JOIN --> CTRL
  CTRL --> REPLAN[Retry / Replan / Human review]
  REPLAN --> ADMISSION[Domain admission when required]
```

### Runtime and Domain State View

```mermaid
flowchart TB
  DOMAIN[Domain State<br/>Matter / Evidence / Finding / WorkProduct]
  RUNTIME[Runtime Control<br/>Run / Plan / Step / Checkpoint]
  KNOW[Knowledge Projection<br/>View / Generation / Readiness]
  CONTEXT[Optional Context Provider]
  EFFECT[External Effect State<br/>Attempt / Receipt / Reconcile]
  AUDIT[Security / Audit Facts]
  TELEMETRY[Telemetry Projection]
  DOMAIN -->|snapshot + version| RUNTIME
  KNOW -->|evidence + readiness| RUNTIME
  CONTEXT -->|policy-scoped context| RUNTIME
  RUNTIME -->|proposal + admission input| DOMAIN
  EFFECT -->|effect truth / reconciliation| RUNTIME & DOMAIN
  AUDIT -. current policy .-> RUNTIME & DOMAIN & EFFECT
  TELEMETRY -. projection only .-> RUNTIME & DOMAIN & EFFECT
```

## Deployment

### Physical Deployment Decision View

```mermaid
flowchart TB
  START[Modular Python Backend + Workers] --> GATE{Evidence Gate}
  GATE -->|No independent boundary evidence| KEEP[Keep together / library / worker]
  GATE -->|Scaling / failure / security / availability / lifecycle evidence| SPLIT[Split specific boundary]
  SPLIT --> CONTRACT[Stable cross-host contract + owner]
```

### Deployment Profiles View

```mermaid
flowchart LR
  HOST[Generic Host / Embedded Mode] --> API[Application & Integration]
  API --> BACKEND[Modular Backend]
  BACKEND --> WORKER[Independent Workers: Ingestion / Model / Eval]
  BACKEND --> STORE[Platform persistence primitives]
  BACKEND -. evidence gate .-> SERVICE[Optional independent service]
```

## Data and Recovery

### Data Ownership View

```mermaid
flowchart TB
  D[Legal Domain] --> DSTORE[(Domain Store)]
  R[Agent Runtime] --> RSTORE[(Runtime Checkpoint)]
  K[Knowledge & Evidence] --> KSTORE[(Object / Index / Graph View)]
  T[Tool Runtime] --> TSTORE[(Attempt / Effect Receipt)]
  S[Security & Governance] --> SSTORE[(Policy / Audit Fact)]
  O[Observability & Evaluation] --> OSTORE[(Trace / Eval Projection)]
  P[Platform Layer] -. provides durability .-> DSTORE & RSTORE & KSTORE & TSTORE & SSTORE & OSTORE
```

### Failure and Recovery View

```mermaid
sequenceDiagram
  participant R as Runtime
  participant D as Domain
  participant C as Checkpoint
  R->>D: Proposal + Formal Admission
  D-->>R: Domain version + AdmissionReceipt
  R->>C: Control checkpoint
  Note over R,C: checkpoint may fail after domain commit
  R->>D: query matching causation receipt
  D-->>R: repair control state or require review
```

## Quality and Security

### A/B/C Eval View

```mermaid
flowchart LR
  A[Generic Host + Legal Skills] --> METRIC[Quality / cost / recovery metrics]
  B[Generic Host + Zuno Legal Backend] --> METRIC
  C[Zuno Native Runtime + Domain State] --> METRIC
  METRIC --> DECIDE{Repeatable attributable gain?}
  DECIDE -->|No| SHRINK[Keep simpler boundary]
  DECIDE -->|Yes| MEASURED[Candidate survives measurement gate]
```

### Security Verification View

```mermaid
flowchart TB
  ACCESS[Current authorization / policy epoch]
  APPROVAL[Approval when required]
  AUDIT[Durable audit fact]
  EFFECT[Tool effect + reconciliation]
  DATA[Redaction / no-egress / tenant isolation]
  ACCESS --> APPROVAL --> AUDIT --> EFFECT
  DATA --> AUDIT
```

## 图源边界

每张图只表达一个主要关系，通常保持在 5–12 个节点。具体 Contract、状态枚举和证据要求以 `architecture.md` Part B 与 ADR 为准；`architecture.html` 由本图源动态展示，不维护第二套 Mermaid 内容。
