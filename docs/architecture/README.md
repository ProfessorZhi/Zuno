# Zuno 总体架构文档

`docs/architecture/` 是唯一正式总体架构目录，只能保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## 总体架构回答什么

总体架构回答：Zuno 怎样把法律领域状态、知识与证据、执行控制、专业能力、模型、安全、现实副作用和可验证交付组合成一套可恢复、可替换、可简化的目标架构。

项目为什么存在、为什么值得立项、为什么不只使用通用平台，先读 [`../project/project.md`](../project/project.md)。Architecture 从产品边界继续回答“既然这些语义需要由 Zuno 负责，系统应该怎样组织”。

Round 02 已冻结总体 Target Architecture 与九个 Logical Responsibility Modules（逻辑责任域）。九个责任域是 Ownership / Contract 边界，不是九个进程、数据库或微服务。Platform / Infrastructure 仍是责任层，Memory / Context 仍是可选 Provider Boundary。

## 为什么没有把 Zuno 设计成另一个通用平台

通用 Host 可以继续负责入口、会话、基础工作流、普通模型调用、基础 RAG 和 UI。Zuno 只在复杂法律任务需要 DocumentVersion、Knowledge Readiness、正式 Evidence / Finding / WorkProduct、HumanDecision、失效传播、Effect Recovery、持续授权和法律 Eval 等专业语义时承担责任。

因此简单问答不强制进入 Native Runtime；Native Runtime、GraphRAG、Long-term Memory、Specialist / Multi-Agent 和物理服务拆分都继续受 Measurement / Evidence Gate。设计差异不等于已证明优势，实际收益必须由 09 的对照测量证明。

## 当前设计状态

九篇模块已经完成 Deep Design V2 / Cross-Module Consistency，并且 **9/9 全部进入 Detail Design Candidate V1**。每篇继续保持：

```text
Part A — Human Narrative
  问题、业务流程、异常、取舍、Current / Target / Gap

Part B — Engineering / Agent Reference
  B1–B14 Owner / Contract / State / Failure / Recovery / Persistence / Evidence
  B14.1–B14.8 Detail Freeze Candidate

Part C — Cross-Module Consistency
  Completion Proof、因果版本、新鲜度、取消、晚到、恢复和一致性测试
```

当前治理状态：

```text
overall_architecture: ROUND_02_FROZEN
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_human_narrative: DEEPENED
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

这一步没有改变 `architecture.md` 的 Round 02 冻结语义。Detail Candidate 只能细化既有 Owner / Contract / recovery 规则；如果字段级设计要求新增 / 删除逻辑模块、扩大七对象 Canonical Legal Kernel、改变 Formal Admission、Knowledge / Domain authority、Effect / Security / Lifecycle Owner，必须升级 Architecture Gap。

## Detail Design Candidate 到底细化了什么

九个模块已经不只回答“做什么”，还把实现前必须盘问的问题落到冻结前候选：

- 01：ExternalRequest / Scope / Invocation、AgentVersion、Publication、Delivery / Invalidation / Ack、Outbox、HostContract 和交付 Crash Window；
- 02：AdmissionCommand / AdmissionReceipt、七对象 Identity / Version、依赖 / CitationBinding、Matter-level PostgreSQL 并发、Invalidation；
- 03：KnowledgeGeneration / ProcessingSpec / Manifest / ServingPointer、Readiness / Retrieval、Worker / Cache / Serving CAS；
- 04：AgentRun / PlanVersion / StepRun、Ready / Join Guard、Replan Barrier、Interrupt / Resume、Checkpoint、Takeover / Fencing；
- 05：CapabilityVersion、ProviderBinding、Conformance、Eligibility、Invocation、Fallback / Cache；
- 06：PreparedAction、ActionHash、ToolAttempt、EffectReceipt、Reconciliation、RetrySafety、Send Boundary；
- 07：ModelRequest、Routing、Attempt、Qualification、Usage / Cost、Cancellation、Fallback；
- 08：Authorization / Approval、SecurityEpoch、Secret Lease、Mandatory Audit、Lifecycle / per-store enforcement；
- 09：TelemetryEnvelope、Correlation、Redaction / Sampling、Dataset / EvalRun / Judge、ReleaseEvidence、Complexity Kill Test。

这些全部是 Target Candidate，不是 Current implementation。真实 PostgreSQL race、Serving cutover、Tool remote idempotency、Provider qualification、Policy Engine、full-chain observability、formal benchmark 等仍要看 Evidence。

## 面对横向系统设计问题

高级系统设计问题应先问“哪类事实由谁拥有”，再讨论物理原语。QPS、Queue、Cache、事务、2PC、租户隔离、HA / DR、成本和数据库恢复的责任矩阵在 [`../modules/README.md`](../modules/README.md)。

默认扩容按工作负载而不是九模块拆服务；Cache 只优化 Projection；Owner 内部使用事务 / CAS / 幂等保证自己的完成事实；跨 Owner 通过 receipt、version、causation ref 和恢复收敛，不追求一个覆盖所有 Store 的 2PC。Queue、Worker、Checkpointer、Object Store 都不能因为物理写入成功就替业务 Owner 宣布完成。

没有 Load Test、真实 Provider 配额、RPO / RTO 和 DR 演练，就不能从 Target Architecture 推导“支持多少 QPS”“支持多少文件”或“已经高可用”。

## 阅读顺序

第一次理解 Zuno：

```text
../project/project.md
→ architecture.md Part A
→ ../modules/README.md
→ 目标模块 Part A
```

进入模块实现级审查时，再读 `architecture.md` Part B、目标模块 Part B / Part C，尤其 B14.1–B14.8，以及 ADR、Evidence 和 Governance。

如果问“为什么这样设计”，看 Architecture / Module；如果问“当前真的实现了吗”，看 `../evidence/`；如果问历史争议，按需读取 `../history/red-blue/`。

## 下一道门不是直接实现

9/9 Candidate 完成以后，下一道门是 **Module Detail Freeze Review**。需要逐模块检查：字段 / identity / version 是否闭合；状态 Guard 是否足够；幂等 namespace 是否分离；Owner Store 的事务 / CAS 是否合理；Crash Window 是否有 durable recovery anchor；Migration 是否保护历史；权限变化、Cancel、Late Result 是否一致；Failure Injection 是否足够；是否引入没有证据支持的微服务、锁或状态机。

只有通过冻结审查，具体模块才可以进入 Detail Freeze；即使冻结，也不自动产生 Implementation Authorization。Codex 业务实现仍需要独立明确授权和任务规格。

## 文件职责

- `architecture.md`：唯一总体 Target Architecture 正文。
- `architecture-views.md`：总体 Mermaid 图源，不拥有第二套事实。
- `architecture.html`：图源展示，不维护平行语义。
- `README.md`：状态、边界和阅读入口。
- `../project/project.md`：项目级 Human-first 主叙事。
- `../modules/`：九个责任域的 Deep Design V2 + Detail Design Candidate V1。
- `../decisions/`：仍有效的长期 ADR。
- `../evidence/`：Current 代码、Migration、Test、Trace、Eval 和运行证据。
- `../history/red-blue/`：审查历史，不拥有当前 Target。

## 一致性与维护

总体架构是当前 Target 的整合表达。模块只能细化它，不能局部重写九模块 Owner、Canonical Kernel、Formal Admission、Knowledge / Domain authority、Retry / Replan / Reconcile、安全政策或 Effect truth。

跨层含义变化才修改 `architecture.md`；模块内部细节进 `../modules/`；项目历史和定位进 `../project/`；图形变化同步 `architecture-views.md` 与 `architecture.html`。

常用验证：

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/scripts/verify_architecture_writing_standard.py
python tools/scripts/verify_architecture_human_readability.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

不得创建第五个架构文件、`.agent/architecture/` 或 `.agent/modules/` 镜像，也不得建立第二套 Domain / Runtime / Service / State registry。