# 05 Cross-module / System Design QA

> Architecture Verification Corpus；不是canonical architecture。答案只从正式架构文档重生成。

### Interview Drill Chain 1：Q213–Q222

连续追问从概念进入机制、失败、取舍和证据。

## Q213 一次合同审查如何跨 Agent Core、Knowledge、Memory、Tool 和 Security？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、case
- architecture_refs:
  - docs/project/architecture/architecture.md — § 1. 产品与领域核心
  - docs/project/modules/06-agent-core-planning-control.md — § 4.1 Deep Dive 04：统一端到端控制案例
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-X-001
- status: Target

### 面试官问题

一次合同审查如何跨 Agent Core、Knowledge、Memory、Tool 和 Security？

### 他真正想考什么

检验是否能把 case 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Agent Core创建Plan和Acceptance，Knowledge满足EvidenceRequirement，Memory装配受治理ContextPack，Security决定Scope/Approval，Tool Runtime确认外部Effect；Observability/Eval提供证明。

### 深挖回答

Agent Core创建Plan和Acceptance，Knowledge满足EvidenceRequirement，Memory装配受治理ContextPack，Security决定Scope/Approval，Tool Runtime确认外部Effect；Observability/Eval提供证明。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/architecture/architecture.md — § 1. 产品与领域核心
- docs/project/modules/06-agent-core-planning-control.md — § 4.1 Deep Dive 04：统一端到端控制案例

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q214 Knowledge Retrieval Replan 和 Agent Core Replan 如何划界？

- source_type: REAL
- source_ref: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、replan
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 18. Retry、Corrective Retrieval 与 Replan
  - docs/project/modules/06-agent-core-planning-control.md — § 9. Replan Barrier
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-X-002
- status: Target

### 面试官问题

Knowledge Retrieval Replan 和 Agent Core Replan 如何划界？

### 他真正想考什么

检验是否能把 replan 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Knowledge在目标/Plan前提仍成立时创建新RetrievalRound；若目标、依赖、能力或前提改变，输出KnowledgeControlProposal，由Agent Core经Replan Barrier创建新PlanVersion。

### 深挖回答

Knowledge在目标/Plan前提仍成立时创建新RetrievalRound；若目标、依赖、能力或前提改变，输出KnowledgeControlProposal，由Agent Core经Replan Barrier创建新PlanVersion。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 18. Retry、Corrective Retrieval 与 Replan
- docs/project/modules/06-agent-core-planning-control.md — § 9. Replan Barrier

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q215 Graph 不可用但 EvidenceRequirement mandatory 怎么办？

- source_type: REAL
- source_ref: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、graph
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Graph 不可用但 EvidenceRequirement mandatory 怎么办？

### 他真正想考什么

检验是否能把 graph 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Knowledge保留mandatory缺口，按Snapshot和Assurance Policy等待或治理降级；若任务无法满足则输出control proposal/abstain，不能静默用文本冒充Graph证据。

### 深挖回答

Knowledge保留mandatory缺口，按Snapshot和Assurance Policy等待或治理降级；若任务无法满足则输出control proposal/abstain，不能静默用文本冒充Graph证据。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q216 MCP 审批等待期间 schema 变化怎么办？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: cross-module
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、mcp
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
  - docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-X-004
- status: Target

### 面试官问题

MCP 审批等待期间 schema 变化怎么办？

### 他真正想考什么

检验是否能把 mcp 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Capability Snapshot变化使未Dispatch的PreparedToolAction和Approval失效，重新Prepare、Scope评估和Approval；已Dispatch的旧Attempt按Effect状态对账。

### 深挖回答

Capability Snapshot变化使未Dispatch的PreparedToolAction和Approval失效，重新Prepare、Scope评估和Approval；已Dispatch的旧Attempt按Effect状态对账。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
- docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q217 Tool effect UNKNOWN 时 Agent Core 如何恢复？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、effect
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
  - docs/project/modules/06-agent-core-planning-control.md — § 11. Side Effect Protocol
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-X-005
- status: Target

### 面试官问题

Tool effect UNKNOWN 时 Agent Core 如何恢复？

### 他真正想考什么

检验是否能把 effect 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Tool Runtime进入Reconciliation并保留业务幂等键，Agent Core暂停普通完成/重试，等待确认或Human Required，再根据EffectReceipt更新ControlDecision。

### 深挖回答

Tool Runtime进入Reconciliation并保留业务幂等键，Agent Core暂停普通完成/重试，等待确认或Human Required，再根据EffectReceipt更新ControlDecision。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
- docs/project/modules/06-agent-core-planning-control.md — § 11. Side Effect Protocol

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q218 Memory 偏好和当前 User instruction 冲突怎么办？

- source_type: REAL
- source_ref: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、memory
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
  - docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Memory 偏好和当前 User instruction 冲突怎么办？

### 他真正想考什么

检验是否能把 memory 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

当前明确指令决定本次Task/ContextPack，不原地修改长期Memory；Memory记录UseTrace/负迁移，长期变化通过Candidate治理。

### 深挖回答

当前明确指令决定本次Task/ContextPack，不原地修改长期Memory；Memory记录UseTrace/负迁移，长期变化通过Candidate治理。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
- docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q219 长任务运行中 Security Epoch 改变怎么办？

- source_type: REAL
- source_ref: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、epoch
- architecture_refs:
  - docs/project/modules/09-security.md — § 16. Decision Cache、一致性与 Epoch
  - docs/project/modules/09-security.md — § 50. Retry、Recovery、Idempotency 与 Reconcile
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-X-007
- status: Target

### 面试官问题

长任务运行中 Security Epoch 改变怎么办？

### 他真正想考什么

检验是否能把 epoch 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

新Epoch使旧Security Decision、Approval或PreparedAction失效；相关数据和Effect重新过Gate，旧结果不能越权进入后续Step。

### 深挖回答

新Epoch使旧Security Decision、Approval或PreparedAction失效；相关数据和Effect重新过Gate，旧结果不能越权进入后续Step。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/09-security.md — § 16. Decision Cache、一致性与 Epoch
- docs/project/modules/09-security.md — § 50. Retry、Recovery、Idempotency 与 Reconcile

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q220 KnowledgeSnapshot 与各索引版本不一致怎么办？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: cross-module
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、snapshot
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 20. 领域状态与 Checkpointer 边界
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 47. 关键数据库约束
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-X-008
- status: Target

### 面试官问题

KnowledgeSnapshot 与各索引版本不一致怎么办？

### 他真正想考什么

检验是否能把 snapshot 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Run只接受与Snapshot lineage兼容的Index；不一致则标记Unavailable/Incompatible，等待重建、换兼容Snapshot或受治理降级，不能混generation。

### 深挖回答

Run只接受与Snapshot lineage兼容的Index；不一致则标记Unavailable/Incompatible，等待重建、换兼容Snapshot或受治理降级，不能混generation。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 20. 领域状态与 Checkpointer 边界
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 47. 关键数据库约束

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q221 如何证明 Agentic GraphRAG 比固定 Hybrid+Graph 更好？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/02_则知科技_Agent开发实习/01_面试_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、eval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 34. Agentic GraphRAG Eval
  - docs/project/modules/10-observability-eval.md — § 29. AgenticGraphRAGTrace
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

如何证明 Agentic GraphRAG 比固定 Hybrid+Graph 更好？

### 他真正想考什么

检验是否能把 eval 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

用固定Dataset、Snapshot、Scope和Budget做ablation，分离Route、Corrective、Stop对质量/Citation/Latency/Cost的增量，禁止编造数字。

### 深挖回答

用固定Dataset、Snapshot、Scope和Budget做ablation，分离Route、Corrective、Stop对质量/Citation/Latency/Cost的增量，禁止编造数字。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 34. Agentic GraphRAG Eval
- docs/project/modules/10-observability-eval.md — § 29. AgenticGraphRAGTrace

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q222 什么证据足以把 Target 升成 Current？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、evidence
- architecture_refs:
  - docs/status/production-readiness.md — § Production Readiness
  - docs/project/modules/06-agent-core-planning-control.md — § 47. 架构完成与 Program 入口门槛
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

什么证据足以把 Target 升成 Current？

### 他真正想考什么

检验是否能把 evidence 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

需要代码、Migration、测试、Fault/E2E、Trace、Eval和可复现运行证据；文档、类名、Mock和目标表不能独立证明实现或生产就绪。

### 深挖回答

需要代码、Migration、测试、Fault/E2E、Trace、Eval和可复现运行证据；文档、类名、Mock和目标表不能独立证明实现或生产就绪。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/status/production-readiness.md — § Production Readiness
- docs/project/modules/06-agent-core-planning-control.md — § 47. 架构完成与 Program 入口门槛

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

### Interview Drill Chain 2：Q223–Q232

连续追问从概念进入机制、失败、取舍和证据。

## Q223 Tool Output 同时想进入 Knowledge 和 Memory，谁先判定？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、output
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
  - docs/project/modules/05-memory-context.md — § 38. MemoryCandidate
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Tool Output 同时想进入 Knowledge 和 Memory，谁先判定？

### 他真正想考什么

检验是否能把 output 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

先按不可信Data经过Security/Redaction/Classification；Knowledge做Evidence Acceptance，Memory做Candidate/Governance，各自不能把对方的投影当权威。

### 深挖回答

先按不可信Data经过Security/Redaction/Classification；Knowledge做Evidence Acceptance，Memory做Candidate/Governance，各自不能把对方的投影当权威。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
- docs/project/modules/05-memory-context.md — § 38. MemoryCandidate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q224 Final Gate 前 SourceSpan 被 Security recheck 过滤怎么办？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: cross-module
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、final
- architecture_refs:
  - docs/project/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
  - docs/project/modules/09-security.md — § 41. Final、Citation 与 Publication
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Final Gate 前 SourceSpan 被 Security recheck 过滤怎么办？

### 他真正想考什么

检验是否能把 final 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

旧Evidence不能继续绑定最终Claim；Run转Partial/Ask/Abstain或重新在当前Scope检索，不能用已失权的Citation完成发布。

### 深挖回答

旧Evidence不能继续绑定最终Claim；Run转Partial/Ask/Abstain或重新在当前Scope检索，不能用已失权的Citation完成发布。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
- docs/project/modules/09-security.md — § 41. Final、Citation 与 Publication

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q225 ToolVersion 变化和 PlanVersion 变化的边界是什么？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/02_则知科技_Agent开发实习/01_面试_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、version
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 24. ToolDefinition、ToolVersion 与 ToolOperation
  - docs/project/modules/06-agent-core-planning-control.md — § 4. PlanVersion 状态机
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

ToolVersion 变化和 PlanVersion 变化的边界是什么？

### 他真正想考什么

检验是否能把 version 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Tool Runtime先处理工具契约变化并重Prepare；只有Step能力、输出Contract或任务前提改变才需要Agent Core创建新PlanVersion。

### 深挖回答

Tool Runtime先处理工具契约变化并重Prepare；只有Step能力、输出Contract或任务前提改变才需要Agent Core创建新PlanVersion。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 24. ToolDefinition、ToolVersion 与 ToolOperation
- docs/project/modules/06-agent-core-planning-control.md — § 4. PlanVersion 状态机

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q226 一个三十分钟长任务如何处理并发、Checkpoint和Approval？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、longrun
- architecture_refs:
  - docs/project/modules/11-infrastructure.md — § 20. CheckpointRecord 与 Domain Boundary
  - docs/project/modules/06-agent-core-planning-control.md — § 3. Domain Store 与 LangGraph Checkpoint 一致性
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

一个三十分钟长任务如何处理并发、Checkpoint和Approval？

### 他真正想考什么

检验是否能把 longrun 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

以Domain Generation为权威，Checkpoint只保存可重建控制状态；Approval和Epoch在Resume/Dispatch前重新校验，副作用通过Durable Dispatch和Reconciliation恢复。

### 深挖回答

以Domain Generation为权威，Checkpoint只保存可重建控制状态；Approval和Epoch在Resume/Dispatch前重新校验，副作用通过Durable Dispatch和Reconciliation恢复。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/11-infrastructure.md — § 20. CheckpointRecord 与 Domain Boundary
- docs/project/modules/06-agent-core-planning-control.md — § 3. Domain Store 与 LangGraph Checkpoint 一致性

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q227 BM25、Vector、Graph、PostgreSQL和Object Store部分失败时如何收口？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_原始逐字稿.md
- primary_domain: cross-module
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、failure
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix
  - docs/project/modules/06-agent-core-planning-control.md — § 35. Failure Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

BM25、Vector、Graph、PostgreSQL和Object Store部分失败时如何收口？

### 他真正想考什么

检验是否能把 failure 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

每个Owner保留自己的Failure/Receipt；Knowledge根据Evidence状态决定Corrective/Partial，Infrastructure处理持久化恢复，Agent Core只在前提改变时Replan。

### 深挖回答

每个Owner保留自己的Failure/Receipt；Knowledge根据Evidence状态决定Corrective/Partial，Infrastructure处理持久化恢复，Agent Core只在前提改变时Replan。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix
- docs/project/modules/06-agent-core-planning-control.md — § 35. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q228 用户批准后 Agent 崩溃，如何避免重复发送？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 51. Crash Cut Points
- primary_domain: cross-module
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、crash
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 51. Crash Cut Points
  - docs/project/modules/11-infrastructure.md — § 44. 一致性与幂等原则
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

用户批准后 Agent 崩溃，如何避免重复发送？

### 他真正想考什么

检验是否能把 crash 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

恢复时从Domain Dispatch、PreparedAction、Approval、Idempotency和Attempt事实判断；不凭Checkpoint重发，不确定时先Reconcile。

### 深挖回答

恢复时从Domain Dispatch、PreparedAction、Approval、Idempotency和Attempt事实判断；不凭Checkpoint重发，不确定时先Reconcile。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 51. Crash Cut Points
- docs/project/modules/11-infrastructure.md — § 44. 一致性与幂等原则

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q229 Memory Procedural Hint 建议某Tool，但当前Task Scope禁止怎么办？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
- primary_domain: cross-module
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、memory
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
  - docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Memory Procedural Hint 建议某Tool，但当前Task Scope禁止怎么办？

### 他真正想考什么

检验是否能把 memory 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Procedural只能是策略提示，Security Effective Scope和Task Downscope优先，禁止因Memory建议扩大权限或跳过Approval。

### 深挖回答

Procedural只能是策略提示，Security Effective Scope和Task Downscope优先，禁止因Memory建议扩大权限或跳过Approval。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
- docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q230 Knowledge发现新依赖但计划中没有对应Step，谁拥有下一步？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/architecture/architecture.md — § 1. 产品与领域核心
- primary_domain: cross-module
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、ownership
- architecture_refs:
  - docs/project/architecture/architecture.md — § 1. 产品与领域核心
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 42. KnowledgeControlProposal
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Knowledge发现新依赖但计划中没有对应Step，谁拥有下一步？

### 他真正想考什么

检验是否能把 ownership 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Knowledge先记录EvidenceFrontier和ControlProposal；Agent Core判断是否需要新增Step/Replan，不能由Knowledge直接修改产品Plan。

### 深挖回答

Knowledge先记录EvidenceFrontier和ControlProposal；Agent Core判断是否需要新增Step/Replan，不能由Knowledge直接修改产品Plan。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/architecture/architecture.md — § 1. 产品与领域核心
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 42. KnowledgeControlProposal

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q231 如何在最终输出中同时保证Citation、权限和Effect一致？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
- primary_domain: cross-module
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、final
- architecture_refs:
  - docs/project/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
  - docs/project/modules/09-security.md — § 41. Final、Citation 与 Publication
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

如何在最终输出中同时保证Citation、权限和Effect一致？

### 他真正想考什么

检验是否能把 final 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Final Gate检查Claim-Evidence绑定、当前Security Scope、Artifact和EffectReceipt/UNKNOWN状态；任何一项不能证明就不发布为完整成功。

### 深挖回答

Final Gate检查Claim-Evidence绑定、当前Security Scope、Artifact和EffectReceipt/UNKNOWN状态；任何一项不能证明就不发布为完整成功。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
- docs/project/modules/09-security.md — § 41. Final、Citation 与 Publication

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q232 未来代码审查如何把这些QA升级为实现证据？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/status/production-readiness.md — § Production Readiness
- primary_domain: cross-module
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Zuno统一端到端案例、future
- architecture_refs:
  - docs/status/production-readiness.md — § Production Readiness
  - docs/project/modules/06-agent-core-planning-control.md — § 47. 架构完成与 Program 入口门槛
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

未来代码审查如何把这些QA升级为实现证据？

### 他真正想考什么

检验是否能把 future 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

逐题把Canonical ref映射到代码、Migration、Test、Trace和Eval；本轮只证明文档覆盖，不宣称Runtime已实现。

### 深挖回答

逐题把Canonical ref映射到代码、Migration、Test、Trace和Eval；本轮只证明文档覆盖，不宣称Runtime已实现。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/status/production-readiness.md — § Production Readiness
- docs/project/modules/06-agent-core-planning-control.md — § 47. 架构完成与 Program 入口门槛

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。
