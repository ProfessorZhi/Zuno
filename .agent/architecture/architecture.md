# Zuno Target Architecture Atlas

updated: 2026-07-11  
status: normative-short-term-target  
current_state_source: `docs/architecture/production-readiness.md`

本文是 Zuno 的目标架构事实源。它使用 **4+1 View Model、Views & Beyond 和 Zuno Product Core** 三组、十类 canonical views，描述最终目标架构及其关键局部关系。

本文描述的是 **Target**。仓库当前真实实现、已知差距和 measured 状态以 `docs/architecture/production-readiness.md` 为准。目标架构不得被误写成 Current。

## 1. 总体目标

Zuno 的近期目标是本地优先、可恢复、可观测、可评测的企业知识库 Agent 产品：

```text
Zuno
=
Single Controller LangGraph Runtime
+ Independent Model / Memory / Knowledge / Capability / Tool modules
+ Source-span Agentic GraphRAG
+ Governed Tool Execution
+ Durable Local Infrastructure
+ Honest Measurement and Release Gates
```

核心边界：

- LangGraph 负责 Agent Core 的状态、控制流、循环、中断、恢复和停止条件。
- Model Gateway、Memory、Knowledge、Capability、Tool Runtime 保持独立 owner、contract、生命周期和测试边界。
- Security 与 Observability 是横切能力。
- Infrastructure 保存事实，不决定 Agent 策略。
- Product Surface 展示与交互，不成为业务事实源。

当前质量口径：

```text
implementation available
measurement blocked
quality not yet proven
```

## 2. 十一逻辑能力模块

| # | 模块 | 最终责任 | 关键输出 |
| --- | --- | --- | --- |
| 1 | Product Surface | AgentChat、Workspace、Artifact、Citation、Trace、Feedback、Recovery UI | RuntimeRequest、用户操作、可视化结果 |
| 2 | Input | SourceObject、解析路由、CanonicalDocumentIR、SourceSpan、index handoff | Document IR、ParseSnapshot、SourceSpan |
| 3 | Knowledge | Chunk、Index、BM25、Vector、GraphRAG、EvidenceLedger、CitationLineage | EvidenceBundle、RetrievalVerdict |
| 4 | Model Gateway | model slot、provider、timeout、retry、fallback、usage、cost、structured output | ModelResult、UsageRecord |
| 5 | Memory | Sensory、Short-term、Long-term、Entity、ContextPack、治理和跨任务复用 | ContextPack、MemoryRecord |
| 6 | Agent Core / Planning & Control | Strategy、Plan、ReAct、Observation、Reflection、Replan、Reflexion、Finalize | GroundedAnswer、RuntimeEvent |
| 7 | Capability | CapabilityCard、SkillCard、目录、选择、策略和路由 | CapabilityPlan、AllowedTools |
| 8 | Tool Runtime | approval、credential ref、sandbox、timeout、idempotency、执行和归一化 | NormalizedToolObservation |
| 9 | Security | Input、Retrieval、Memory、Tool、Output、Artifact gates | GateDecision、AuditEvent |
| 10 | Observability & Eval | spans、usage、cost、failure buckets、benchmark、release gate | TraceTree、EvalReport |
| 11 | Infrastructure | SQLite、ObjectStore、Index、Checkpoint、EventStore、Migration、Recovery | Durable records and handles |

## 3. 六个物理运行域

| 运行域 | 逻辑模块映射 |
| --- | --- |
| Product & API | Product Surface |
| Input & Knowledge | Input、Knowledge |
| Agent Core Runtime | Model Gateway、Memory、Agent Core / Planning & Control，逻辑 owner 保持独立 |
| Capability & Tool | Capability、Tool Runtime |
| Governance & Observability | Security、Observability & Eval |
| Local Infrastructure | Infrastructure |

---

# Architecture Visual Atlas

箭头规范：

```text
==>  command / control request
-->  data / result / state transfer
-.-> cross-cutting governance / observation / constraint
```

颜色规范：

```text
blue    Product / API
yellow  Agent Core / Control
white   Independent capability
purple  Security / Observability
green   Infrastructure
orange  Decision / Gate
red     Blocked / Failure
```

## 一、4+1 View Model

### Logical View (4+1)

回答“系统需要哪些逻辑能力，以及它们通过什么 contract 协作”。

#### Overall — Eleven Logical Capabilities

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "basis"}}}%%
flowchart TB
  classDef product fill:#eaf3ff,stroke:#2563a6,stroke-width:1.5px,color:#16202a;
  classDef core fill:#fff4d8,stroke:#c58a18,stroke-width:2px,color:#16202a;
  classDef capability fill:#ffffff,stroke:#64748b,stroke-width:1.2px,color:#16202a;
  classDef governance fill:#f2ecff,stroke:#7c5cbf,stroke-width:1.4px,color:#16202a;
  classDef infra fill:#eef6f1,stroke:#60766a,stroke-width:1.4px,color:#16202a;

  PS["1 Product Surface<br/>AgentChat · Workspace · Artifact · Citation · Trace UI"]
  IN["2 Input<br/>SourceObject · ParseGateway · DocumentIR · SourceSpan"]
  KN["3 Knowledge<br/>Index · Hybrid Retrieval · GraphRAG · EvidenceLedger"]
  MG["4 Model Gateway<br/>Model Slot · Provider · Timeout · Fallback · Usage"]
  MM["5 Memory<br/>Sensory · Short-term · Long-term · Entity"]
  AC["6 Agent Core / Planning & Control<br/>Strategy · Plan · ReAct · Reflect · Replan · Finalize"]
  CP["7 Capability<br/>Catalog · Skill · Policy · Routing"]
  TR["8 Tool Runtime<br/>Approval · Credential · Sandbox · Execution"]
  SEC["9 Security<br/>Input · Retrieval · Memory · Tool · Output Gates"]
  OBS["10 Observability & Eval<br/>Trace · Cost · Benchmark · Release Gate"]
  INF["11 Infrastructure<br/>SQLite · Object Store · Index · Checkpoint · Recovery"]

  PS ==>|RuntimeRequest| AC
  AC -->|RuntimeEvent · GroundedAnswer · ArtifactRef| PS
  PS ==>|Upload · SourceObject| IN
  IN -->|CanonicalDocumentIR · IndexHandoff| KN

  AC ==>|ModelCallRequest| MG
  MG -->|ModelResult · Usage · Cost| AC
  AC ==>|MemoryReadRequest · MemoryCommit| MM
  MM -->|ContextPack · SelectedMemory| AC
  AC ==>|RetrievalPlan| KN
  KN -->|EvidenceBundle · RetrievalVerdict| AC
  AC ==>|CapabilityQuery| CP
  CP -->|CapabilityPlan · AllowedTools| AC
  CP -->|ToolManifest · ExecutionPolicy| TR
  AC ==>|ToolCallIntent| TR
  TR -->|NormalizedToolObservation| AC

  SEC -.->|policy and gates| PS
  SEC -.->|policy and gates| IN
  SEC -.->|policy and gates| KN
  SEC -.->|policy and gates| MG
  SEC -.->|policy and gates| MM
  SEC -.->|policy and gates| AC
  SEC -.->|policy and gates| CP
  SEC -.->|policy and gates| TR

  OBS -.->|spans and metrics| PS
  OBS -.->|spans and metrics| IN
  OBS -.->|spans and metrics| KN
  OBS -.->|spans and metrics| MG
  OBS -.->|spans and metrics| MM
  OBS -.->|spans and metrics| AC
  OBS -.->|spans and metrics| CP
  OBS -.->|spans and metrics| TR

  PS -->|business state| INF
  IN -->|source · parse snapshots| INF
  KN -->|index · evidence ledger| INF
  MG -->|model bindings · usage| INF
  MM -->|memory records| INF
  AC -->|run · checkpoint · interrupt| INF
  CP -->|catalog · policies| INF
  TR -->|approval · result · idempotency| INF
  SEC -->|audit records| INF
  OBS -->|trace · eval reports| INF

  class PS product;
  class AC core;
  class IN,KN,MG,MM,CP,TR capability;
  class SEC,OBS governance;
  class INF infra;
```

#### Local — Memory and Context Subsystem

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "basis"}}}%%
flowchart LR
  classDef memory fill:#ffffff,stroke:#64748b,stroke-width:1.2px,color:#16202a;
  classDef policy fill:#f2ecff,stroke:#7c5cbf,stroke-width:1.4px,color:#16202a;
  classDef context fill:#eaf3ff,stroke:#2563a6,stroke-width:1.5px,color:#16202a;
  classDef core fill:#fff4d8,stroke:#c58a18,stroke-width:1.8px,color:#16202a;

  INPUT["Current Input<br/>message · observation · event"]
  SENSORY["Sensory Memory<br/>raw current-turn signals"]
  SHORT["Short-term Memory<br/>working state · recent window · PlanState"]
  LONG["Long-term Memory<br/>episodic · semantic · procedural"]
  ENTITY["Entity Memory<br/>user · project · relation · effective time"]
  POLICY["Memory Policy<br/>scope · privacy · freshness · conflict · token budget"]
  RETRIEVE["Retrieval and Ranking<br/>relevance · confidence · recency · diversity"]
  CONTEXT["ContextPack<br/>selected memories + exclusion reasons"]
  AGENT["Agent Core<br/>Strategy · Planner · ReAct · Reflection"]
  CAPTURE["Post-turn Capture<br/>raw event · task summary · facts · lessons"]
  CANDIDATE["Memory Candidate"]
  REVIEW{"Governance Review<br/>redact · deduplicate · conflict · approve"}
  AUDIT["Governance Ledger"]
  STORE["Approved Memory Store"]

  INPUT --> SENSORY --> SHORT
  SHORT --> POLICY
  LONG --> POLICY
  ENTITY --> POLICY
  POLICY --> RETRIEVE --> CONTEXT
  CONTEXT -->|bounded read view| AGENT
  AGENT --> CAPTURE --> CANDIDATE --> REVIEW
  REVIEW -->|approved lesson or episode| STORE
  REVIEW -->|approved entity fact| ENTITY
  REVIEW -->|pending or rejected| AUDIT
  STORE --> LONG
  REVIEW --> AUDIT

  class SENSORY,SHORT,LONG,ENTITY,RETRIEVE,CAPTURE,CANDIDATE,STORE memory;
  class POLICY,REVIEW,AUDIT policy;
  class CONTEXT context;
  class AGENT core;
```

#### Local — Agent Core Internal Capability Boundary

```mermaid
%%{init: {"theme": "base", "flowchart": {"curve": "basis"}}}%%
flowchart TB
  classDef core fill:#fff4d8,stroke:#c58a18,stroke-width:1.6px,color:#16202a;
  classDef external fill:#ffffff,stroke:#64748b,stroke-width:1.2px,color:#16202a;
  classDef gate fill:#fff0e6,stroke:#c56a18,stroke-width:1.4px,color:#16202a;

  STRATEGY["Strategy Selector"]
  PLANNER["Planner and Plan Validator"]
  EXECUTOR["Plan Executor"]
  REACT["Single-step ReAct Controller"]
  OBSERVE["Observation Normalizer"]
  EVIDENCE["Evidence Gate"]
  SYNTH["Grounded Synthesis and Claim Binding"]
  REFLECT{"Reflection"}
  REPLAN["Replanner"]
  FINAL["Finalize and Post-turn Commit"]

  MODEL["Model Gateway"]
  MEMORY["Memory"]
  KNOWLEDGE["Knowledge"]
  CAPABILITY["Capability"]
  TOOL["Tool Runtime"]

  STRATEGY --> PLANNER --> EXECUTOR --> REACT --> OBSERVE --> EVIDENCE --> SYNTH --> REFLECT
  REFLECT -->|PASS| FINAL
  REFLECT -->|REWRITE_ANSWER| SYNTH
  REFLECT -->|RETRIEVE_MORE| REPLAN --> EXECUTOR
  REFLECT -->|USE_TOOL| EXECUTOR
  REFLECT -->|ASK_USER| FINAL
  REFLECT -->|ABSTAIN| FINAL

  STRATEGY ==>|ModelCallRequest| MODEL
  PLANNER ==>|PlannerRequest| MODEL
  SYNTH ==>|SynthesisRequest| MODEL
  REFLECT ==>|optional CriticRequest| MODEL
  STRATEGY ==>|MemoryReadRequest| MEMORY
  MEMORY -->|ContextPack| STRATEGY
  EXECUTOR ==>|RetrievalPlan| KNOWLEDGE
  KNOWLEDGE -->|EvidenceBundle| OBSERVE
  EXECUTOR ==>|CapabilityQuery| CAPABILITY
  CAPABILITY -->|CapabilityPlan| EXECUTOR
  REACT ==>|ToolCallIntent| TOOL
  TOOL -->|ToolObservation| OBSERVE
  FINAL ==>|MemoryCommit| MEMORY

  class STRATEGY,PLANNER,EXECUTOR,REACT,OBSERVE,EVIDENCE,SYNTH,REPLAN,FINAL core;
  class MODEL,MEMORY,KNOWLEDGE,CAPABILITY,TOOL external;
  class REFLECT gate;
```

### Development View (4+1)

回答“代码目录、owner、允许依赖和禁止绕过边界”。

#### Overall — Repository Ownership and Dependency Direction

```mermaid
flowchart TB
  classDef product fill:#eaf3ff,stroke:#2563a6,color:#16202a;
  classDef core fill:#fff4d8,stroke:#c58a18,color:#16202a;
  classDef module fill:#ffffff,stroke:#64748b,color:#16202a;
  classDef platform fill:#eef6f1,stroke:#60766a,color:#16202a;
  classDef governance fill:#f2ecff,stroke:#7c5cbf,color:#16202a;

  WEB["apps/web<br/>Product UI"]
  API["zuno/api<br/>DTO · routes · SSE"]
  AGENT["zuno/agent<br/>Single Controller and LangGraph"]
  MEMORY["zuno/memory<br/>Memory Engine and Context"]
  KNOWLEDGE["zuno/knowledge<br/>Ingestion · Retrieval · GraphRAG"]
  CAPABILITY["zuno/capability<br/>Capability · Skill · Tool · MCP"]
  PLATFORM["zuno/platform<br/>Model Gateway · DB · Storage · Security · Observability"]
  TOOLS["tools<br/>renderer · verifier · eval"]
  TESTS["tests<br/>focused · E2E · guardrails"]
  DOCS["docs/architecture<br/>normative source"]

  WEB -->|typed API| API
  API -->|RuntimeRequest| AGENT
  AGENT -->|Memory contracts| MEMORY
  AGENT -->|Retrieval contracts| KNOWLEDGE
  AGENT -->|Capability contracts| CAPABILITY
  AGENT -->|Gateway · state · trace contracts| PLATFORM
  MEMORY -->|store adapter| PLATFORM
  KNOWLEDGE -->|store · model slots · gates| PLATFORM
  CAPABILITY -->|tool control · store · gates| PLATFORM

  DOCS -->|source| TOOLS
  TOOLS -->|generated HTML · verifier output| TESTS
  TESTS -->|guardrail feedback| DOCS

  class WEB,API product;
  class AGENT core;
  class MEMORY,KNOWLEDGE,CAPABILITY module;
  class PLATFORM platform;
  class DOCS,TOOLS,TESTS governance;
```

#### Local — Runtime Package Dependency Rule

```mermaid
flowchart LR
  API["API Service"]
  FACTORY["RuntimeDependencyFactory"]
  SERVICE["UnifiedAgentRuntimeService"]
  GRAPH["Compiled LangGraph"]
  NODES["Runtime Nodes"]
  PORTS["Typed Runtime Protocols"]
  ADAPTERS["Model · Memory · Knowledge · Tool Adapters"]
  STORES["Checkpoint · Event · Domain Stores"]

  API ==>|create request| FACTORY
  FACTORY -->|dependencies| SERVICE
  SERVICE -->|invoke or stream| GRAPH
  GRAPH -->|state transition| NODES
  NODES ==>|protocol calls| PORTS
  PORTS -->|implemented by| ADAPTERS
  SERVICE -->|checkpoint and events| STORES
  ADAPTERS -->|durable facts| STORES
```

#### Local — Architecture Source and Verification Chain

```mermaid
flowchart LR
  MD["docs/architecture/architecture.md<br/>single normative source"]
  RENDER["tools/agent/render_architecture.py<br/>true Mermaid HTML renderer"]
  HTML["docs/architecture/architecture.html"]
  MIRROR_MD[".agent/architecture/architecture.md"]
  MIRROR_HTML[".agent/architecture/architecture.html"]
  VERIFY["architecture render check"]
  TESTS["repo guardrail tests"]
  CODEX["Codex cross-review"]

  MD ==>|parse canonical sections| RENDER
  RENDER -->|generate| HTML
  RENDER -->|sync| MIRROR_MD
  RENDER -->|generate| MIRROR_HTML
  MD --> VERIFY
  HTML --> VERIFY
  MIRROR_MD --> VERIFY
  MIRROR_HTML --> VERIFY
  VERIFY --> TESTS
  TESTS --> CODEX
  CODEX -.->|review findings| MD
```

### Process View (4+1)

回答“一次任务如何在 LangGraph 中运行、循环、中断、恢复和终止”。

#### Overall — Unified LangGraph Runtime

```mermaid
flowchart TB
  classDef node fill:#ffffff,stroke:#64748b,color:#16202a;
  classDef core fill:#fff4d8,stroke:#c58a18,color:#16202a;
  classDef gate fill:#fff0e6,stroke:#c56a18,color:#16202a;
  classDef end fill:#eef6f1,stroke:#60766a,color:#16202a;

  START(["START"])
  INPUT["input_gate"]
  CONTEXT["build_context"]
  STRATEGY{"strategy_select"}
  PLAN["create_or_update_plan"]
  EXECUTE["execute_step"]
  OBSERVE["observe"]
  EVIDENCE["evidence_gate"]
  DRAFT["draft_and_bind_claims"]
  REFLECT{"reflection"]
  REVISE["revise_draft"]
  REPLAN["replan"]
  APPROVAL["approval / tool execution"]
  INTERRUPT["interrupt / ask user"]
  FINAL["finalize"]
  COMMIT["post_turn_commit"]
  END(["END"])

  START --> INPUT --> CONTEXT --> STRATEGY
  STRATEGY -->|direct| DRAFT
  STRATEGY -->|react or plan_and_execute| PLAN --> EXECUTE --> OBSERVE
  OBSERVE -->|plan remains| EXECUTE
  OBSERVE -->|plan complete| EVIDENCE --> DRAFT --> REFLECT
  REFLECT -->|PASS| FINAL
  REFLECT -->|REWRITE_ANSWER| REVISE --> DRAFT
  REFLECT -->|RETRIEVE_MORE| REPLAN --> EXECUTE
  REFLECT -->|USE_TOOL| APPROVAL --> OBSERVE
  REFLECT -->|ASK_USER| INTERRUPT
  INTERRUPT -->|Command resume| EXECUTE
  REFLECT -->|ABSTAIN| FINAL
  FINAL --> COMMIT --> END

  class INPUT,CONTEXT,PLAN,EXECUTE,OBSERVE,EVIDENCE,DRAFT,REVISE,REPLAN,APPROVAL,INTERRUPT,FINAL,COMMIT node;
  class STRATEGY,REFLECT gate;
  class START,END end;
```

#### Local — Single-step ReAct Loop

```mermaid
flowchart LR
  STEP["PlanStep<br/>goal · acceptance · allowed capabilities"]
  PROMPT["Step Context Builder"]
  MODEL["Executor Model via Model Gateway"]
  INTENT{"Action Decision"}
  KNOWLEDGE["Knowledge Retrieval"]
  TOOL["Governed Tool Runtime"]
  DIRECT["Model-only Transform"]
  OBS["NormalizedObservation"]
  CHECK{"Step Acceptance Check"}
  DONE["Step Completed"]
  CONTINUE["Continue ReAct<br/>bounded by max_actions_per_step"]

  STEP --> PROMPT ==>|ModelCallRequest| MODEL --> INTENT
  INTENT -->|retrieve| KNOWLEDGE --> OBS
  INTENT -->|tool call| TOOL --> OBS
  INTENT -->|model transform| DIRECT --> OBS
  OBS --> CHECK
  CHECK -->|accepted| DONE
  CHECK -->|needs another action| CONTINUE --> PROMPT
```

#### Local — Interrupt, Approval and Durable Resume

```mermaid
sequenceDiagram
  participant G as LangGraph
  participant T as Tool Runtime
  participant S as Checkpoint Store
  participant API as Product API
  participant U as User

  G->>T: ToolRuntimeRequest
  T-->>G: approval_required
  G->>S: persist checkpoint + interrupt
  G-->>API: RuntimeEvent(approval_required)
  API-->>U: show approval UI
  U->>API: approve / deny
  API->>G: Command(resume=decision)
  G->>S: load checkpoint by thread_id
  G->>T: execute with idempotency_key
  T-->>G: NormalizedToolObservation
  G->>S: persist resumed state and event
```

### Physical View (4+1)

回答“近期本地优先系统实际部署在哪里，以及状态和外部 provider 如何连接”。

#### Overall — Local-first Deployment Topology

```mermaid
flowchart TB
  USER["Browser / Desktop"]
  WEB["Web UI"]
  API["FastAPI Product API"]
  RUNTIME["Unified LangGraph Runtime"]
  MODEL["Configured Model Provider<br/>local or remote"]
  SQLITE[("SQLite / SQLModel")]
  OBJECT[("Local Object Store")]
  INDEX[("Local BM25 / Vector / Graph Index")]
  TRACE[("Local Trace Store")]
  EVAL[("Eval Reports")]

  USER --> WEB ==>|HTTP · SSE| API ==>|RuntimeRequest| RUNTIME
  RUNTIME ==>|model calls| MODEL
  RUNTIME -->|run · checkpoint · memory · approval| SQLITE
  API -->|workspace · task · message| SQLITE
  API -->|source · artifact| OBJECT
  RUNTIME -->|retrieval| INDEX
  RUNTIME -->|spans · usage · diagnostics| TRACE
  TRACE -->|evaluation input| EVAL
```

#### Local — Durable Storage and Recovery Topology

```mermaid
flowchart LR
  RUN["Agent Run"]
  CHECKPOINT["LangGraph Checkpoint"]
  EVENTS["Runtime Event Log"]
  MEMORY["Memory Records"]
  EVIDENCE["EvidenceLedger"]
  APPROVAL["Approval and Tool Claims"]
  ARTIFACT["Artifact and Source Objects"]
  DB[("SQLite")]
  OBJECT[("Object Store")]
  RESTART["New Service Instance"]

  RUN --> CHECKPOINT --> DB
  RUN --> EVENTS --> DB
  RUN --> MEMORY --> DB
  RUN --> EVIDENCE --> DB
  RUN --> APPROVAL --> DB
  RUN --> ARTIFACT --> OBJECT
  RESTART ==>|thread_id · run_id| DB
  DB -->|state · pending interrupt · events| RESTART
  OBJECT -->|source and artifact handles| RESTART
```

#### Local — Replaceable External Adapter Boundary

```mermaid
flowchart TB
  CORE["Zuno Typed Contracts"]
  LOCAL["Near-term Local Adapters<br/>SQLite · local object · local index"]
  MODEL["Model Provider Adapters<br/>OpenAI-compatible · local LLM"]
  OPTIONAL["Future Optional Adapters<br/>Postgres · Redis · MinIO · external vector / graph"]

  CORE ==>|stable ports| LOCAL
  CORE ==>|stable ports| MODEL
  CORE -.->|future replacement, not current blocker| OPTIONAL
  LOCAL -.->|migration path| OPTIONAL
```

### Scenarios View (4+1)

回答“用户生命周期如何衔接”，而不是把所有动作误画成一条固定直线。

#### Overall — Product Lifecycles

```mermaid
flowchart TB
  MODEL["Model Configuration Lifecycle"]
  KNOWLEDGE["Knowledge Preparation Lifecycle"]
  AGENT["Agent Execution Lifecycle"]
  RESULT["Result Inspection Lifecycle"]
  RECOVERY["Refresh and Restart Recovery"]
  FEEDBACK["Feedback and Regression Lifecycle"]
  TRACE["Cross-cutting Trace · Cost · Security"]

  MODEL -->|ModelSlotBinding| AGENT
  KNOWLEDGE -->|KnowledgeSpace · IndexManifest| AGENT
  AGENT -->|GroundedAnswer · Artifact · Citation| RESULT
  RESULT --> FEEDBACK
  AGENT --> RECOVERY
  RESULT --> RECOVERY
  FEEDBACK -->|failure cases · fixed dataset| AGENT

  TRACE -.-> MODEL
  TRACE -.-> KNOWLEDGE
  TRACE -.-> AGENT
  TRACE -.-> RESULT
  TRACE -.-> RECOVERY
  TRACE -.-> FEEDBACK
```

#### Local — Document Preparation Scenario

```mermaid
flowchart LR
  UPLOAD["Upload File"]
  SOURCE["SourceObject<br/>checksum · workspace scope"]
  PARSE["ParseJob"]
  IR["CanonicalDocumentIR"]
  SPAN["DocumentBlock · SourceSpan"]
  CHUNK["CitationChunk · ParentChunk"]
  MANIFEST["Candidate IndexManifest"]
  VALIDATE{"Validate<br/>span · ACL · index health"}
  ACTIVE["Active IndexManifest"]
  BLOCKED["Blocked<br/>no fake index"]

  UPLOAD --> SOURCE --> PARSE
  PARSE -->|success| IR --> SPAN --> CHUNK --> MANIFEST --> VALIDATE
  VALIDATE -->|pass| ACTIVE
  PARSE -->|parser unavailable or failed| BLOCKED
  VALIDATE -->|missing span or invalid index| BLOCKED
```

#### Local — AgentChat, Result and Recovery Scenario

```mermaid
sequenceDiagram
  participant U as User
  participant P as Product API
  participant G as Unified Runtime
  participant D as Durable Stores
  participant UI as Result UI

  U->>P: ask(question, workspace, model slot)
  P->>G: RuntimeRequest
  G->>D: persist run and checkpoint
  G-->>P: live RuntimeEvents
  P-->>UI: plan / retrieval / tool / answer events
  G->>D: persist GroundedAnswer, citations, trace
  UI-->>U: answer + evidence + artifact
  U->>P: refresh or reconnect
  P->>D: load task, answer, events, trace
  D-->>P: recovered product state
  P-->>UI: restore result and pending actions
```

## 二、Views & Beyond

### Module View (Views & Beyond)

回答“十一逻辑模块如何映射到六个物理运行域，以及重点模块内部如何分解”。

#### Overall — Eleven Modules to Six Runtime Domains

```mermaid
flowchart LR
  subgraph LOGICAL["Eleven Logical Capabilities"]
    PS["Product Surface"]
    IN["Input"]
    KN["Knowledge"]
    MG["Model Gateway"]
    MM["Memory"]
    AC["Agent Core"]
    CP["Capability"]
    TR["Tool Runtime"]
    SEC["Security"]
    OBS["Observability & Eval"]
    INF["Infrastructure"]
  end

  subgraph PHYSICAL["Six Physical Runtime Domains"]
    PRODUCT["Product & API"]
    IK["Input & Knowledge"]
    AGENT["Agent Core Runtime"]
    CT["Capability & Tool"]
    GOV["Governance & Observability"]
    LOCAL["Local Infrastructure"]
  end

  PS --> PRODUCT
  IN --> IK
  KN --> IK
  MG --> AGENT
  MM --> AGENT
  AC --> AGENT
  CP --> CT
  TR --> CT
  SEC --> GOV
  OBS --> GOV
  INF --> LOCAL

  PRODUCT --> LOCAL
  IK --> LOCAL
  AGENT --> LOCAL
  CT --> LOCAL
  GOV --> LOCAL
```

#### Local — Agent Core Module Decomposition

```mermaid
flowchart TB
  STATE["Versioned AgentRuntimeState"]
  GRAPH["LangGraph Builder"]
  STRATEGY["Strategy Selector"]
  PLANNER["Planner · Validator"]
  EXEC["Plan Executor · Step Registry"]
  REACT["ReAct Runner"]
  OBS["Observation Normalizer"]
  REFLECT["Reflection · Replan"]
  SYNTH["Claims · Citation Binding · GroundedAnswer"]
  DURABLE["Checkpoint · Interrupt · Event Bridge"]
  MEMORY["Post-turn Reflexion Bridge"]

  GRAPH --> STATE
  GRAPH --> STRATEGY --> PLANNER --> EXEC --> REACT --> OBS --> REFLECT --> SYNTH
  STATE <--> DURABLE
  SYNTH --> MEMORY
  REFLECT --> EXEC
```

#### Local — Independent Capability Modules

```mermaid
flowchart LR
  AGENT["Agent Core"]
  MODEL["Model Gateway<br/>provider-neutral model execution"]
  MEMORY["Memory<br/>context and governed learning"]
  KNOWLEDGE["Knowledge<br/>evidence retrieval"]
  CAPABILITY["Capability<br/>catalog and policy"]
  TOOL["Tool Runtime<br/>side-effect execution"]

  AGENT ==>|ModelCallRequest| MODEL
  MODEL -->|ModelResult| AGENT
  AGENT ==>|MemoryRead / Commit| MEMORY
  MEMORY -->|ContextPack| AGENT
  AGENT ==>|RetrievalPlan| KNOWLEDGE
  KNOWLEDGE -->|EvidenceBundle| AGENT
  AGENT ==>|CapabilityQuery| CAPABILITY
  CAPABILITY -->|CapabilityPlan| AGENT
  AGENT ==>|ToolCallIntent| TOOL
  TOOL -->|ToolObservation| AGENT
  CAPABILITY -->|ToolManifest and policy| TOOL
```

### Component-and-Connector View (Views & Beyond)

回答“运行时组件之间通过什么 connector、command 和 result contract 连接”。

#### Overall — Runtime Components and Typed Connectors

```mermaid
flowchart LR
  PRODUCT["Product API"]
  SERVICE["UnifiedAgentRuntimeService"]
  GRAPH["Compiled LangGraph"]
  MODEL["Model Gateway"]
  MEMORY["Memory Runtime"]
  KNOWLEDGE["Knowledge Runtime"]
  CAPABILITY["Capability Router"]
  TOOL["Tool Control Plane"]
  SECURITY["Security Gates"]
  TRACE["Trace and Eval Sink"]
  STORE["Durable Stores"]

  PRODUCT ==>|RuntimeRequest| SERVICE
  SERVICE ==>|invoke · stream · resume| GRAPH
  GRAPH ==>|ModelCallRequest| MODEL
  MODEL -->|ModelResult| GRAPH
  GRAPH ==>|MemoryReadRequest · MemoryCommit| MEMORY
  MEMORY -->|ContextPack · MemoryRefs| GRAPH
  GRAPH ==>|RetrievalPlan| KNOWLEDGE
  KNOWLEDGE -->|EvidenceBundle · Verdict| GRAPH
  GRAPH ==>|CapabilityQuery| CAPABILITY
  CAPABILITY -->|CapabilityPlan · AllowedTools| GRAPH
  GRAPH ==>|ToolRuntimeRequest| TOOL
  TOOL -->|NormalizedToolResult| GRAPH
  SECURITY -.->|GateDecision| GRAPH
  GRAPH -.->|ZunoSpan · RuntimeEvent| TRACE
  SERVICE -->|run · checkpoint · interrupt| STORE
  MODEL -->|usage · cost| STORE
  MEMORY -->|memory records| STORE
  KNOWLEDGE -->|ledger · index refs| STORE
  TOOL -->|approval · result · idempotency| STORE
  GRAPH -->|GroundedAnswer| SERVICE
  SERVICE -->|RuntimeEvent · ProductResult| PRODUCT
```

#### Local — Model, Memory and Knowledge Connectors

```mermaid
flowchart TB
  NODE["LangGraph Node"]

  MREQ["ModelCallRequest<br/>role · slot · schema · budget"]
  MRES["ModelResult<br/>output · usage · latency · fallback"]
  MEMREQ["MemoryReadRequest<br/>scope · query · token budget"]
  CTX["ContextPack<br/>selected and excluded memory"]
  RETREQ["RetrievalPlan<br/>queries · retrievers · top-k · rounds"]
  EVIDENCE["EvidenceBundle<br/>source spans · scores · ledger ref"]

  MODEL["Model Gateway"]
  MEMORY["Memory Runtime"]
  KNOWLEDGE["Knowledge Runtime"]

  NODE --> MREQ ==>|invoke| MODEL --> MRES --> NODE
  NODE --> MEMREQ ==>|retrieve| MEMORY --> CTX --> NODE
  NODE --> RETREQ ==>|retrieve| KNOWLEDGE --> EVIDENCE --> NODE
```

#### Local — Capability and Governed Tool Connector

```mermaid
flowchart LR
  PLAN["CapabilityPlan"]
  SKILL["Skill metadata → instruction → resource"]
  INTENT["Function Call Intent"]
  ROUTER["Capability Router"]
  POLICY{"Policy and Approval Gate"}
  CREDENTIAL["CredentialRef"]
  MANIFEST["ToolCard / MCP Tool"]
  ADAPTER["Execution Adapter"]
  NORMALIZE["Result Normalizer"]
  OBS["ToolObservation"]
  TRACE["ToolTrace"]

  PLAN --> SKILL --> ROUTER
  INTENT --> ROUTER
  ROUTER --> POLICY
  POLICY -->|approved| CREDENTIAL --> MANIFEST --> ADAPTER --> NORMALIZE --> OBS
  POLICY -->|approval required| TRACE
  POLICY -->|blocked| OBS
  ADAPTER --> TRACE
  NORMALIZE --> TRACE
```

### Data View (Views & Beyond)

回答“权威数据实体、版本、引用、运行状态和持久化事实如何流动”。

#### Overall — Authoritative Information Model

```mermaid
flowchart TB
  WORKSPACE["Workspace"]
  SESSION["Session"]
  TASK["Task / AgentRun"]
  MESSAGE["Message / GroundedAnswer"]
  ARTIFACT["Artifact"]
  SOURCE["SourceObject"]
  DOC["DocumentVersion"]
  IR["CanonicalDocumentIR"]
  SPAN["DocumentBlock · SourceSpan"]
  CHUNK["CitationChunk · ParentChunk"]
  INDEX["IndexManifest"]
  LEDGER["EvidenceLedger"]
  CLAIM["Claim"]
  BIND["CitationBinding"]
  MEMORY["MemoryRecord"]
  TOOL["ToolRequest · Approval · Result"]
  TRACE["TraceSpan · Usage · Eval"]

  WORKSPACE --> SESSION --> TASK --> MESSAGE --> ARTIFACT
  WORKSPACE --> SOURCE --> DOC --> IR --> SPAN --> CHUNK --> INDEX --> LEDGER
  TASK --> LEDGER
  MESSAGE --> CLAIM --> BIND
  LEDGER --> BIND
  TASK --> MEMORY
  TASK --> TOOL
  TASK --> TRACE
  TOOL --> TRACE
  LEDGER --> TRACE
  BIND --> TRACE
```

#### Local — Source-span Evidence and Citation Lineage

```mermaid
flowchart LR
  SOURCE["SourceObject<br/>uri · checksum"]
  VERSION["DocumentVersion"]
  BLOCK["DocumentBlock"]
  SPAN["SourceSpan<br/>page · bbox · line · cell"]
  CHUNK["CitationChunk"]
  INDEX["Index Entry"]
  RECORD["EvidenceLedgerRecord"]
  CLAIM["StructuredClaim"]
  BIND["ClaimEvidenceBinding"]
  ANSWER["GroundedAnswer"]

  SOURCE --> VERSION --> BLOCK --> SPAN
  BLOCK --> CHUNK --> INDEX --> RECORD
  SPAN --> CHUNK
  RECORD --> BIND
  CLAIM --> BIND --> ANSWER
  VERSION -.->|freshness validation| BIND
```

#### Local — Runtime, Memory and Tool State

```mermaid
flowchart TB
  RUN["AgentRuntimeState<br/>versioned control state"]
  CHECKPOINT["Checkpoint"]
  EVENT["RuntimeEvent"]
  INTERRUPT["PendingInterrupt"]
  OBS["NormalizedObservation"]
  PLAN["PlanState"]
  GROUND["GroundedAnswer"]
  MEMCAND["MemoryCandidate"]
  MEMREC["Approved MemoryRecord"]
  TOOLREQ["ToolRuntimeRequest"]
  APPROVAL["ApprovalDecision"]
  TOOLRES["NormalizedToolResult"]

  RUN --> CHECKPOINT
  RUN --> EVENT
  RUN --> INTERRUPT
  RUN --> OBS
  RUN --> PLAN
  RUN --> GROUND
  GROUND --> MEMCAND --> MEMREC
  RUN --> TOOLREQ --> APPROVAL --> TOOLRES --> OBS
```

### Quality View (Views & Beyond)

回答“安全、正确性、可恢复性、可观测性、性能、成本和诚实测量如何贯穿系统”。

#### Overall — Cross-cutting Quality Attributes

```mermaid
flowchart TB
  PRODUCT["Product Request"]
  INPUT["Input"]
  CONTEXT["Context Build"]
  AGENT["Agent Runtime"]
  RETRIEVAL["Retrieval"]
  MODEL["Model Calls"]
  TOOL["Tool Calls"]
  ANSWER["Grounded Answer"]
  STORE["Durable State"]

  SECURITY["Security · Privacy"]
  GROUNDING["Evidence · Citation Correctness"]
  OBS["Trace · Usage · Cost"]
  RECOVERY["Checkpoint · Idempotency · Recovery"]
  BUDGET["Timeout · Step · Token · Cost Limits"]
  EVAL["Benchmark · Failure Buckets · Release Gate"]

  PRODUCT --> INPUT --> CONTEXT --> AGENT
  AGENT --> RETRIEVAL --> ANSWER
  AGENT --> MODEL --> ANSWER
  AGENT --> TOOL --> ANSWER
  AGENT --> STORE

  SECURITY -.-> PRODUCT
  SECURITY -.-> INPUT
  SECURITY -.-> CONTEXT
  SECURITY -.-> RETRIEVAL
  SECURITY -.-> MODEL
  SECURITY -.-> TOOL
  SECURITY -.-> ANSWER

  GROUNDING -.-> RETRIEVAL
  GROUNDING -.-> ANSWER
  OBS -.-> PRODUCT
  OBS -.-> AGENT
  OBS -.-> RETRIEVAL
  OBS -.-> MODEL
  OBS -.-> TOOL
  RECOVERY -.-> AGENT
  RECOVERY -.-> STORE
  BUDGET -.-> AGENT
  EVAL -.-> OBS
  EVAL -.-> GROUNDING
```

#### Local — Security Gate Chain

```mermaid
flowchart LR
  REQUEST["User Request"]
  INPUT{"Input Gate<br/>ACL · injection · secret · PII"}
  MEMORY{"Memory Gate<br/>scope · privacy · stale · conflict"}
  RETRIEVAL{"Retrieval Gate<br/>workspace · ACL · trust · source span"}
  MODEL{"Model Context Gate<br/>redaction · policy · budget"}
  TOOL{"Tool Gate<br/>allowlist · args · approval · credential · network"}
  OUTPUT{"Output Gate<br/>unsupported claim · leakage · citation"}
  ARTIFACT{"Artifact Gate<br/>path · type · sensitivity"}
  RESULT["Product Result"]
  BLOCKED["Blocked / Redacted / Approval Required"]

  REQUEST --> INPUT --> MEMORY --> RETRIEVAL --> MODEL --> TOOL --> OUTPUT --> ARTIFACT --> RESULT
  INPUT -->|block| BLOCKED
  MEMORY -->|exclude or block| BLOCKED
  RETRIEVAL -->|block| BLOCKED
  MODEL -->|block| BLOCKED
  TOOL -->|approval or block| BLOCKED
  OUTPUT -->|rewrite or abstain| BLOCKED
  ARTIFACT -->|block| BLOCKED
```

#### Local — Trace, Failure Diagnosis and Release Gate

```mermaid
flowchart TB
  RUN["Agent Run Span Tree"]
  RET["Retrieval Metrics"]
  GEN["Generation Metrics"]
  AGENT["Agent Metrics"]
  MEM["Memory Metrics"]
  PROD["Product Metrics"]
  BUCKETS["Failure Buckets<br/>doc_miss · text_miss · citation_miss · answer_wrong"]
  DATASET["Tracked Fixed Dataset"]
  PROFILES["standard · deep · agentic profiles"]
  COMPLETE{"Profile Completeness"}
  GATE{"Release Gate"}
  PASS["measured_pass"]
  FAIL["measured_fail"]
  BLOCKED["blocked_not_measured"]

  RUN --> RET
  RUN --> GEN
  RUN --> AGENT
  RUN --> MEM
  RUN --> PROD
  RET --> BUCKETS
  GEN --> BUCKETS
  DATASET --> PROFILES --> COMPLETE
  RET --> GATE
  GEN --> GATE
  AGENT --> GATE
  MEM --> GATE
  PROD --> GATE
  COMPLETE -->|complete| GATE
  COMPLETE -->|incomplete or unavailable| BLOCKED
  GATE -->|thresholds met| PASS
  GATE -->|thresholds missed| FAIL
```

## 三、Zuno Product Core

### Agentic GraphRAG Evidence and Agent Loop (Zuno)

回答“Agent 如何规划检索、纠正失败、跨轮积累 source-span evidence、绑定 claim 并进入 Reflection / Replan”。

#### Overall — Agentic GraphRAG and Agent Loop

```mermaid
flowchart TB
  QUESTION["Question + ContextPack"]
  NEED{"Need Retrieval?"}
  QUERY["Query Strategy"]
  BM25["BM25"]
  VECTOR["Vector"]
  GRAPH["Graph Expansion"]
  FUSION["RRF / Fusion"]
  RERANK["Rerank · Parent Expansion"]
  LEDGER["EvidenceLedger"]
  QUALITY{"Retrieval Quality Gate"}
  CLAIM["Claim Extraction"]
  BIND["Claim-level Citation Binding"]
  SYNTH["Grounded Synthesis"]
  REFLECT{"Reflection"}
  CORRECT["Corrective Action / Replan"]
  FINAL["Grounded Answer · Partial · Abstain"]
  EVAL["Failure Buckets · Release Gate"]

  QUESTION --> NEED
  NEED -->|yes| QUERY
  NEED -->|no| CLAIM
  QUERY --> BM25 --> FUSION
  QUERY --> VECTOR --> FUSION
  QUERY --> GRAPH --> FUSION
  FUSION --> RERANK --> LEDGER --> QUALITY
  QUALITY -->|sufficient| CLAIM --> BIND --> SYNTH --> REFLECT
  QUALITY -->|ambiguous · irrelevant · insufficient span| CORRECT --> QUERY
  REFLECT -->|PASS| FINAL
  REFLECT -->|REWRITE_ANSWER| SYNTH
  REFLECT -->|RETRIEVE_MORE| CORRECT
  REFLECT -->|ABSTAIN| FINAL
  FINAL --> EVAL
```

#### Local — Query Strategy and Corrective Retrieval

```mermaid
flowchart LR
  ORIGINAL["Original Query"]
  DIRECT["DIRECT"]
  REWRITE["REWRITE"]
  MULTI["MULTI_QUERY"]
  STEPBACK["STEP_BACK"]
  HYDE["HYDE"]
  ENTITY["ENTITY_DECOMPOSITION"]
  RELATION["RELATION_QUERY"]
  PLAN["RetrievalPlan<br/>query set · retriever mix · graph traversal"]
  ROUND["Retrieval Round"]
  VERDICT{"RELEVANT · AMBIGUOUS · IRRELEVANT · CONFLICTING · INSUFFICIENT_SPAN"}
  CONTINUE["Continue to Claims"]
  CORRECT["Choose unused corrective action"]
  ABSTAIN["Abstain"]

  ORIGINAL --> DIRECT --> PLAN
  ORIGINAL --> REWRITE --> PLAN
  ORIGINAL --> MULTI --> PLAN
  ORIGINAL --> STEPBACK --> PLAN
  ORIGINAL --> HYDE --> PLAN
  ORIGINAL --> ENTITY --> PLAN
  ORIGINAL --> RELATION --> PLAN
  PLAN --> ROUND --> VERDICT
  VERDICT -->|sufficient| CONTINUE
  VERDICT -->|retry allowed and novelty expected| CORRECT --> PLAN
  VERDICT -->|budget exhausted or no novelty| ABSTAIN
```

#### Local — EvidenceLedger, Claim Binding and Failure Attribution

```mermaid
flowchart TB
  ROUND1["Round 1 EvidenceLedgerRecords"]
  ROUND2["Round 2 EvidenceLedgerRecords"]
  DEDUPE["Deduplicate · Conflict Group · Freshness Check"]
  SELECT["Evidence Selection<br/>context budget · source span required"]
  CLAIMS["Structured Claims"]
  BIND["ClaimEvidenceBinding"]
  VERIFY{"Support Verification"}
  ANSWER["GroundedAnswer"]
  DOCMISS["doc_miss"]
  TEXTMISS["doc_hit_text_miss"]
  CITMISS["text_hit_citation_miss"]
  WRONG["citation_hit_answer_wrong"]

  ROUND1 --> DEDUPE
  ROUND2 --> DEDUPE
  DEDUPE --> SELECT --> BIND
  CLAIMS --> BIND --> VERIFY
  VERIFY -->|supported| ANSWER
  VERIFY -->|document absent| DOCMISS
  VERIFY -->|document hit but evidence absent| TEXTMISS
  VERIFY -->|evidence hit but binding absent| CITMISS
  VERIFY -->|citation correct but answer wrong| WRONG
```

## 4. Target completion criteria

目标架构只有在以下事实同时成立时，才能写成完整实现：

1. Completion 与 Workspace 默认使用同一个 UnifiedAgentRuntimeService。
2. Unified runtime 使用 compiled LangGraph、原生 checkpoint、interrupt/resume 和 live event stream。
3. 所有真实模型调用经过 Model Gateway，并读取有效 model slot binding。
4. Memory 使用 durable store，跨请求和重启可复用；ContextPack 可观测。
5. Knowledge 返回 durable EvidenceLedger 和 source-span EvidenceBundle。
6. Capability 负责选择与 policy；Tool Runtime 完成真实安全工具执行。
7. GroundedAnswer 是正式 runtime state，包含 claims、bindings、unsupported claims 和 ledger ref。
8. Security 与 Observability 覆盖所有关键边界。
9. 关键事实可持久化、恢复、审计和重放。
10. fixed paired benchmark 形成完整 measured profile，并诚实输出 pass、fail 或 blocked。

## 5. Current / Target 边界

- 本文所有图默认表达 Target。
- `docs/architecture/production-readiness.md` 表达 Current。
- Current 不得因为 contract、mock、fixture、sidecar 或 deterministic baseline 存在而写成完整 runtime。
- 质量只能由 fixed benchmark 与 release gate 证明。
