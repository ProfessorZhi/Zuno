# Architecture Red Team Drill Taxonomy

红队 QA 按真实面试的连续追问方式组织，而不是按名词表堆题。每个 Drill Chain 从 Why/Definition 进入 Trigger/Mechanism，再进入 Failure、Trade-off、Consistency、Evidence 或 Future 边界。这里的目标不是覆盖更多名词，而是让一个核心机制能够经受连续五层以上追问。

```text
概念是什么
→ 为什么需要它
→ 运行时什么时候触发
→ 输入、状态和 Owner 是什么
→ 失败、版本、权限和并发怎么处理
→ 如何验证设计真的有效
```

## 难度层级

| Level | 关注点 |
| --- | --- |
| L1 | Definition：概念和 Owner |
| L2 | Why：为什么这样设计、为什么不用更简单方案 |
| L3 | Mechanism：输入、步骤、状态和 Contract |
| L4 | Failure：失败分类、传播和恢复 |
| L5 | Trade-off：成本、延迟、质量、安全和降级 |
| L6 | Consistency / Concurrency：版本、Generation、并发和幂等 |
| L7 | Evidence / Eval：如何用 Test、Trace、Eval 证明 |
| L8 | System Stress：长任务、部分失败和跨模块压力 |

Q001–Q267 按连续编号轮换 L1–L8，每个 Domain 的 Chain 均覆盖多层追问。新增内容应优先补进现有 Chain；题目数量不是质量指标。

## 主题模式族

### Agentic GraphRAG / Evidence

Control/Data Plane、Hybrid Recall、BM25/Vector、RRF、Rerank、Top-N/Top-K、CitationChunk、SourceSpan、DocumentVersion、SearchAction、Local、Global、DRIFT、Materialization、Dedup、EvidenceRequirement、QuerySpec、Ledger、Quality、Failure Diagnosis、Corrective Retrieval、Replan、Stop、Snapshot、Eval、Current/Target。

### Tool / MCP / Security

Function Calling、Capability/Skill/Tool、PreparedToolAction、Canonicalization、TargetResourceSet、Effective Scope、User Ceiling、Task Downscope、Security Epoch、Approval、Replay、MCP Version、Capability Snapshot、list_changed、Schema Change、Timeout、UNKNOWN、Idempotency、Reconciliation、Compensation、SecretLease、Sandbox、Prompt Injection、Audit、Concurrency、Crash、Eval。

### Memory / Context

Working/Session/Long-term、Episodic/Semantic/Procedural、SessionSummaryVersion、Recent Raw Tail、Compression、Protected Set、ContextPack、Budget、MemoryCandidate、Governance、Version、Supersede、Stale、Dormant、Quarantine、Revoke、Delete、Poisoning、Conflict、Privacy、Scope、Utility、Negative Transfer、Recall、Projection、Eval。

### Memory / Information Extraction

TaskUnderstandingSnapshot、StructuredObservation、ExtractionProposal、Entity Resolution、Temporal Normalization、occurred_at/observed_at/recorded_at、valid_from/valid_to、Capture Policy、MemoryWriteDecision、ConflictType、Provenance、Revalidation、Knowledge/Memory Authority、Effective Memory Scope、Memory Poisoning、Deletion Propagation、Extraction/Memory Eval。

### Agent Core / Planning & Control

Single Controller、固定 AgentRunGraph、动态 Plan DAG、StepExecutionGraph、五种控制机制、Plan mandatory、ReAct、Acceptance、Reflection、Retry、Repair、Fallback、Replan、PlanVersion、Replan Barrier、ReadySet、ResourceClaim、Send、Durable Dispatch、BranchResult、JoinPolicy、Interrupt、Resume、Budget、PostgreSQL、Checkpointer、Final Gate、RunOutcome、Reflexion。

### Cross-module / System Design

统一合同案例、Knowledge/Agent Replan、Graph Mandatory、MCP 审批、UNKNOWN Effect、Memory/User Instruction、Epoch 撤销、Snapshot/Index、Ablation、Target→Current、Tool Output、Final Citation、长任务、Crash、权限和未来代码证据。

## Source 分层

真实来源先提取问题和追问顺序；DERIVED 只向当前 Contract 合理延伸；ARCHITECTURE_STRESS 只能测试已存在的 Target 边界，不得为了答题凭空增加技术。
