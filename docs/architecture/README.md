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

## 研究成果和先进算法怎样进入 Architecture

Zuno 不把“用了最新论文 / 最新开源组件”本身当成架构质量。2026-08-16 接受的 [ADR-0015](../decisions/0015-research-native-adaptive-intelligence.md) 把研究资产进入产品的路径固定为：

```text
Research Artifact
→ Source Verification / Reproduction
→ Capability Semantics
→ Versioned Provider
→ Conformance
→ Domain Eval
→ Eligibility
→ Runtime use
→ Proposal / Candidate
→ Owner Admission when required
```

因此，葛季栋 / LIPLAB 的 JIA / TRL 事件抽取、事件对齐、冲突 / 争议识别可以变成 05 的专业 Capability family；现代 LLM、encoder、规则和旧论文算法可以作为不同 Provider 做可比 Eval。论文结果不能直接写成 Current，也不能因为某算法来自课题组就越过 02 Formal Admission。

同一 ADR 进一步吸收各领域先进论文的机制，而不是复制完整论文系统：

- 03 使用 Adaptive Multi-Route Retrieval：lexical / BM25、dense、metadata / source-scoped、entity / fact、graph / multi-hop 按 QueryClass 组合，RRF / calibrated fusion 后 rerank；复杂多文档允许依赖感知的迭代分解；EvidenceGain / Sufficiency 决定继续、focused probe 或停止。
- Optional Memory 使用 Typed Memory Control Plane：Working / Episodic / Semantic / Procedural / Context Archive 分开；模型只能提出 MemoryCandidate，长期写入由 scope、source、security、freshness、conflict / dedup 和 lifecycle policy 决定；OpenViking、Graphiti、Mem0、LangMem 等只是条件 Provider candidate。
- 04 在 Planner 与 PlanVersion activation 之间增加 Structure → Feasibility → Usefulness 三层 Plan Quality Gate，并用真实 Owner fact / execution feedback 驱动 Retry / Replan，而不是 open-loop 盲跑。
- 06 使用 Propose–Verify–Execute–Observe：PreparedAction 在现实执行前经过 schema、semantic constraint、side-effect、idempotency / reconciliation、Authorization / Approval freshness 和 audit guard；模型不能批准自己提出的动作。
- 09 对每种复杂机制保留 baseline / ablation / kill test。Graph、Memory、Reflection、强模型和复杂 Planner 没有稳定边际收益时必须允许删除或缩小。

这些是 Target refinement，不是新增第十模块，也不改变 ADR-0013 / 0014 冻结的九模块 Owner、七对象 Legal Domain Kernel、Single Controller、Formal Admission、Retry / Replan / Reconcile 或安全门禁。

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
research_native_adaptive_intelligence: ACCEPTED_TARGET
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

这一步没有改变 `architecture.md` 的 Round 02 冻结语义。Detail Candidate 和 ADR-0015 只能细化既有 Owner / Contract / recovery 规则；如果算法设计要求新增 / 删除逻辑模块、扩大七对象 Canonical Legal Kernel、改变 Formal Admission、Knowledge / Domain authority、Effect / Security / Lifecycle Owner，必须升级 Architecture Gap。

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

ADR-0015 的算法 refinement 在 Detail Freeze Review 中还需要继续下沉为 owner-specific Contract：03 的 RetrievalIntent / Route / EvidenceGain，04 的 Plan Quality Gate，05 的法律 Capability family，06 的 Action Validator，以及 Optional Memory 的 MemoryCandidate / MemoryWriteDecision / ContextCandidate。没有字段、状态、Crash / late-result 和 Eval 规格前，不应把这些概念写成实现任务。

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

如果问题涉及“为什么把论文 / Open Source / Provider 融进来但不直接绑定”，先读 ADR-0007；涉及多路检索 / Agentic RAG 先读 ADR-0006；涉及研究成果、Memory、Planning、Tool safety 的整体算法组合先读 ADR-0015。

如果问“为什么这样设计”，看 Architecture / Module；如果问“当前真的实现了吗”，看 `../evidence/`；如果问历史争议，按需读取 `../history/red-blue/`。

## 下一道门不是直接实现

9/9 Candidate 完成以后，下一道门仍然是 **Module Detail Freeze Review**。需要逐模块检查：字段 / identity / version 是否闭合；状态 Guard 是否足够；幂等 namespace 是否分离；Owner Store 的事务 / CAS 是否合理；Crash Window 是否有 durable recovery anchor；Migration 是否保护历史；权限变化、Cancel、Late Result 是否一致；Failure Injection 是否足够；是否引入没有证据支持的微服务、锁或状态机。

对 ADR-0015 新引入的 Target refinement，还要额外检查：算法的 trigger / stop condition 是否明确；论文指标和 Zuno Eval 是否分开；Provider 是否可退出；复杂路线是否有 simpler baseline；Memory 是否可能污染正式事实；Graph / Reflection / strong model 是否有 kill test；Tool Validator 是否仍然服从 08，而不是产生第二套 Authorization。

只有通过冻结审查，具体模块才可以进入 Detail Freeze；即使冻结，也不自动产生 Implementation Authorization。Codex 业务实现仍需要独立明确授权和任务规格。

## 文件职责

- `architecture.md`：唯一总体 Target Architecture 正文。
- `architecture-views.md`：总体 Mermaid 图源，不拥有第二套事实。
- `architecture.html`：图源展示，不维护平行语义。
- `README.md`：状态、边界和阅读入口。
- `../project/project.md`：项目级 Human-first 主叙事。
- `../modules/`：九个责任域的 Deep Design V2 + Detail Design Candidate V1。
- `../decisions/`：仍有效的长期 ADR；ADR-0006 / 0007 / 0015 是当前 Retrieval / Provider / Research-native algorithm refinement 的主要入口。
- `../evidence/`：Current 代码、Migration、Test、Trace、Eval 和运行证据。
- `../history/red-blue/`：审查历史，不拥有当前 Target。

## 一致性与维护

总体架构是当前 Target 的整合表达。模块只能细化它，不能局部重写九模块 Owner、Canonical Kernel、Formal Admission、Knowledge / Domain authority、Retry / Replan / Reconcile、安全政策或 Effect truth。

跨层含义变化才修改 `architecture.md` 或创建 / 更新相应长期 ADR；模块内部细节进 `../modules/`；项目历史和定位进 `../project/`；图形变化同步 `architecture-views.md` 与 `architecture.html`。

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