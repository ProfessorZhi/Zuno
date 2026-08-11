# 03 Memory & Context QA

> Architecture Verification Corpus；不是canonical architecture。答案只从正式架构文档重生成。

### Interview Drill Chain 1：Q124–Q132

连续追问从概念进入机制、失败、取舍和证据。

## Q124 Working、Session、Long-term Memory分别解决什么？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: memory
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、layers
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 2. 三个正交维度
  - docs/project/modules/05-memory-context.md — § 4. 模块职责
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-001
- status: Target

### 面试官问题

Working、Session、Long-term Memory分别解决什么？

### 他真正想考什么

检验是否能把 layers 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

它们按生命周期区分活多久，不是三种互斥存储技术；Working由Agent Core控制，Session/Long-term由Memory治理。

### 深挖回答

它们按生命周期区分活多久，不是三种互斥存储技术；Working由Agent Core控制，Session/Long-term由Memory治理。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 2. 三个正交维度
- docs/project/modules/05-memory-context.md — § 4. 模块职责

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q125 为什么生命周期维度和内容类型维度要正交？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: memory
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、layers
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 2. 三个正交维度
  - docs/project/modules/05-memory-context.md — § 4. 模块职责
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-002
- status: Target

### 面试官问题

为什么生命周期维度和内容类型维度要正交？

### 他真正想考什么

检验是否能把 layers 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Working/Session/Long-term回答存活时间，Episodic/Semantic/Procedural回答长期记什么；混在一起会把策略提示误当事实。

### 深挖回答

Working/Session/Long-term回答存活时间，Episodic/Semantic/Procedural回答长期记什么；混在一起会把策略提示误当事实。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 2. 三个正交维度
- docs/project/modules/05-memory-context.md — § 4. 模块职责

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q126 Memory 与 Knowledge 的唯一边界是什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: memory
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、boundary
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
  - docs/project/modules/05-memory-context.md — § 5. Cross-module Ownership
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-003
- status: Target

### 面试官问题

Memory 与 Knowledge 的唯一边界是什么？

### 他真正想考什么

检验是否能把 boundary 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Knowledge拥有企业文档事实和SourceSpan，Memory拥有可复用的用户/任务上下文；Memory最多引用Knowledge证据，不能复制权威事实。

### 深挖回答

Knowledge拥有企业文档事实和SourceSpan，Memory拥有可复用的用户/任务上下文；Memory最多引用Knowledge证据，不能复制权威事实。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
- docs/project/modules/05-memory-context.md — § 5. Cross-module Ownership

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q127 Working Memory 谁拥有？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_QA整理.md
- primary_domain: memory
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、boundary
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
  - docs/project/modules/05-memory-context.md — § 5. Cross-module Ownership
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Working Memory 谁拥有？

### 他真正想考什么

检验是否能把 boundary 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Agent Core拥有Run、Goal、Plan和Working控制语义；Memory模块只提供受治理的ContextPack和长期记忆读取。

### 深挖回答

Agent Core拥有Run、Goal、Plan和Working控制语义；Memory模块只提供受治理的ContextPack和长期记忆读取。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
- docs/project/modules/05-memory-context.md — § 5. Cross-module Ownership

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q128 Working 如何进入 Session？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: memory
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、consolidation
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 9. Working Memory 如何进入 Session Memory
  - docs/project/modules/05-memory-context.md — § 10. Session Memory 如何进入 Long-term Memory
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-005
- status: Target

### 面试官问题

Working 如何进入 Session？

### 他真正想考什么

检验是否能把 consolidation 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Run结束或阶段性compact在策略触发时形成SessionSummaryVersion，保留必要Raw Tail、引用和压缩trace，不直接生成长期Active Memory。

### 深挖回答

Run结束或阶段性compact在策略触发时形成SessionSummaryVersion，保留必要Raw Tail、引用和压缩trace，不直接生成长期Active Memory。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 9. Working Memory 如何进入 Session Memory
- docs/project/modules/05-memory-context.md — § 10. Session Memory 如何进入 Long-term Memory

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q129 Session Summary Version 为什么要版本化？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: memory
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、consolidation
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 9. Working Memory 如何进入 Session Memory
  - docs/project/modules/05-memory-context.md — § 10. Session Memory 如何进入 Long-term Memory
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Session Summary Version 为什么要版本化？

### 他真正想考什么

检验是否能把 consolidation 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

摘要是可审计的派生事实，版本化才能知道输入、模型角色、保留信息、冲突和后续supersede，避免原地覆盖。

### 深挖回答

摘要是可审计的派生事实，版本化才能知道输入、模型角色、保留信息、冲突和后续supersede，避免原地覆盖。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 9. Working Memory 如何进入 Session Memory
- docs/project/modules/05-memory-context.md — § 10. Session Memory 如何进入 Long-term Memory

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q130 Recent Raw Tail 为什么不能总被压缩？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: memory
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、compression
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 16. 四类压缩如何交互
  - docs/project/modules/05-memory-context.md — § 19. Protected Set 与预算
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Recent Raw Tail 为什么不能总被压缩？

### 他真正想考什么

检验是否能把 compression 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

它保留最近未被结构化总结的上下文、用户纠正和未完成状态；只有满足安全和预算条件才可裁剪。

### 深挖回答

它保留最近未被结构化总结的上下文、用户纠正和未完成状态；只有满足安全和预算条件才可裁剪。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 16. 四类压缩如何交互
- docs/project/modules/05-memory-context.md — § 19. Protected Set 与预算

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q131 什么时候压缩而不是裁剪？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_QA整理.md
- primary_domain: memory
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、compression
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 16. 四类压缩如何交互
  - docs/project/modules/05-memory-context.md — § 19. Protected Set 与预算
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-008
- status: Target

### 面试官问题

什么时候压缩而不是裁剪？

### 他真正想考什么

检验是否能把 compression 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

确定性裁剪先去除低价值重复；需要保留语义、约束或决策链时使用结构化压缩，并由Protected Set与Validation保护关键内容。

### 深挖回答

确定性裁剪先去除低价值重复；需要保留语义、约束或决策链时使用结构化压缩，并由Protected Set与Validation保护关键内容。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 16. 四类压缩如何交互
- docs/project/modules/05-memory-context.md — § 19. Protected Set 与预算

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q132 为什么不能按70%阈值简单裁历史？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: memory
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、compression
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 16. 四类压缩如何交互
  - docs/project/modules/05-memory-context.md — § 19. Protected Set 与预算
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-009
- status: Target

### 面试官问题

为什么不能按70%阈值简单裁历史？

### 他真正想考什么

检验是否能把 compression 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Token占用不是价值；必须结合来源、任务相关性、未完成动作、用户指令、安全标签、Atomic Group和Context Budget。

### 深挖回答

Token占用不是价值；必须结合来源、任务相关性、未完成动作、用户指令、安全标签、Atomic Group和Context Budget。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 16. 四类压缩如何交互
- docs/project/modules/05-memory-context.md — § 19. Protected Set 与预算

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

### Interview Drill Chain 2：Q133–Q141

连续追问从概念进入机制、失败、取舍和证据。

## Q133 哪些信息属于 Protected Set？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: memory
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、compression
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 16. 四类压缩如何交互
  - docs/project/modules/05-memory-context.md — § 19. Protected Set 与预算
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

哪些信息属于 Protected Set？

### 他真正想考什么

检验是否能把 compression 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

当前用户指令、Goal/Plan、Approval、Security限制、未完成Step、强制Evidence、失败状态和必须保留的Citation等不能任意丢弃。

### 深挖回答

当前用户指令、Goal/Plan、Approval、Security限制、未完成Step、强制Evidence、失败状态和必须保留的Citation等不能任意丢弃。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 16. 四类压缩如何交互
- docs/project/modules/05-memory-context.md — § 19. Protected Set 与预算

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q134 Tool Result 怎么压缩？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: memory
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、compression
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 16. 四类压缩如何交互
  - docs/project/modules/05-memory-context.md — § 19. Protected Set 与预算
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Tool Result 怎么压缩？

### 他真正想考什么

检验是否能把 compression 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

先保留schema、状态、错误、Effect certainty、关键字段、引用和业务键，再按Result分类做lossless或structured compact；不能丢UNKNOWN语义。

### 深挖回答

先保留schema、状态、错误、Effect certainty、关键字段、引用和业务键，再按Result分类做lossless或structured compact；不能丢UNKNOWN语义。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 16. 四类压缩如何交互
- docs/project/modules/05-memory-context.md — § 19. Protected Set 与预算

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q135 ContextPack 是什么？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_QA整理.md
- primary_domain: memory
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、context
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 13. Context 构建完整流程
  - docs/project/modules/05-memory-context.md — § 47. ContextPackVersion
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-012
- status: Target

### 面试官问题

ContextPack 是什么？

### 他真正想考什么

检验是否能把 context 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

ContextPackVersion是一次模型调用/Step的不可变、预算化、只读上下文视图，引用Policy、Plan、Memory、Knowledge和Tool Observation但不拥有它们。

### 深挖回答

ContextPackVersion是一次模型调用/Step的不可变、预算化、只读上下文视图，引用Policy、Plan、Memory、Knowledge和Tool Observation但不拥有它们。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 13. Context 构建完整流程
- docs/project/modules/05-memory-context.md — § 47. ContextPackVersion

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q136 Context Budget 如何分配？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: memory
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、context
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 13. Context 构建完整流程
  - docs/project/modules/05-memory-context.md — § 47. ContextPackVersion
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Context Budget 如何分配？

### 他真正想考什么

检验是否能把 context 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

按Protected Set、输入/输出Contract、证据、任务状态、记忆候选和模型窗口分层装配，超预算进入明确压缩/裁剪策略而非静默截断。

### 深挖回答

按Protected Set、输入/输出Contract、证据、任务状态、记忆候选和模型窗口分层装配，超预算进入明确压缩/裁剪策略而非静默截断。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 13. Context 构建完整流程
- docs/project/modules/05-memory-context.md — § 47. ContextPackVersion

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q137 Atomic Group 为什么重要？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: memory
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、context
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 13. Context 构建完整流程
  - docs/project/modules/05-memory-context.md — § 47. ContextPackVersion
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Atomic Group 为什么重要？

### 他真正想考什么

检验是否能把 context 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

相互依赖的Claim、Citation、Approval或Action状态不能只保留一半；Packing必须整组保留或显式降级，避免产生看似完整的错误上下文。

### 深挖回答

相互依赖的Claim、Citation、Approval或Action状态不能只保留一半；Packing必须整组保留或显式降级，避免产生看似完整的错误上下文。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 13. Context 构建完整流程
- docs/project/modules/05-memory-context.md — § 47. ContextPackVersion

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q138 Episodic、Semantic、Procedural分别记什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: memory
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、types
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 2. 三个正交维度
  - docs/project/modules/05-memory-context.md — § 39. Typed Payload
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-015
- status: Target

### 面试官问题

Episodic、Semantic、Procedural分别记什么？

### 他真正想考什么

检验是否能把 types 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Episodic记发生过什么，Semantic记经过治理的相对稳定事实，Procedural记可复用策略提示；三者都需Candidate和Governance。

### 深挖回答

Episodic记发生过什么，Semantic记经过治理的相对稳定事实，Procedural记可复用策略提示；三者都需Candidate和Governance。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 2. 三个正交维度
- docs/project/modules/05-memory-context.md — § 39. Typed Payload

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q139 为什么 Entity 不是第四种长期Memory？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_QA整理.md
- primary_domain: memory
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、types
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 2. 三个正交维度
  - docs/project/modules/05-memory-context.md — § 39. Typed Payload
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么 Entity 不是第四种长期Memory？

### 他真正想考什么

检验是否能把 types 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Entity是Semantic Projection或索引形态，不是独立生命周期/内容类型；Canonical事实仍是MemoryVersion，Vector/Graph只是可重建Projection。

### 深挖回答

Entity是Semantic Projection或索引形态，不是独立生命周期/内容类型；Canonical事实仍是MemoryVersion，Vector/Graph只是可重建Projection。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 2. 三个正交维度
- docs/project/modules/05-memory-context.md — § 39. Typed Payload

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q140 一次 Run 为什么不能直接形成 Procedural Memory？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: memory
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、types
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 2. 三个正交维度
  - docs/project/modules/05-memory-context.md — § 39. Typed Payload
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-017
- status: Target

### 面试官问题

一次 Run 为什么不能直接形成 Procedural Memory？

### 他真正想考什么

检验是否能把 types 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

单次经历可能是偶然或错误泛化；Procedural需要多次Episode、验证或人工/Eval证据，并且只能作Strategy Hint。

### 深挖回答

单次经历可能是偶然或错误泛化；Procedural需要多次Episode、验证或人工/Eval证据，并且只能作Strategy Hint。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 2. 三个正交维度
- docs/project/modules/05-memory-context.md — § 39. Typed Payload

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q141 Reflexion 与 Procedural Memory 的关系是什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: memory
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、types
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 2. 三个正交维度
  - docs/project/modules/05-memory-context.md — § 39. Typed Payload
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Reflexion 与 Procedural Memory 的关系是什么？

### 他真正想考什么

检验是否能把 types 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Reflexion生成经验候选，可能提出Procedural Candidate，但必须经过Validation、Conflict和Governance，不能直接改权限、Skill或Plan。

### 深挖回答

Reflexion生成经验候选，可能提出Procedural Candidate，但必须经过Validation、Conflict和Governance，不能直接改权限、Skill或Plan。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 2. 三个正交维度
- docs/project/modules/05-memory-context.md — § 39. Typed Payload

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

### Interview Drill Chain 3：Q142–Q150

连续追问从概念进入机制、失败、取舍和证据。

## Q142 MemoryCandidate 为什么存在？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: memory
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、candidate
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 26. MemoryCandidate 状态机
  - docs/project/modules/05-memory-context.md — § 38. MemoryCandidate
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-019
- status: Target

### 面试官问题

MemoryCandidate 为什么存在？

### 他真正想考什么

检验是否能把 candidate 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

它把模型总结、用户反馈和Run经验与Active Memory隔开，允许去重、脱敏、冲突检测、Scope审查和人工治理。

### 深挖回答

它把模型总结、用户反馈和Run经验与Active Memory隔开，允许去重、脱敏、冲突检测、Scope审查和人工治理。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 26. MemoryCandidate 状态机
- docs/project/modules/05-memory-context.md — § 38. MemoryCandidate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q143 为什么模型不能直接写 Active Memory？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/02_则知科技_Agent开发实习/01_面试_QA整理.md
- primary_domain: memory
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、candidate
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 26. MemoryCandidate 状态机
  - docs/project/modules/05-memory-context.md — § 38. MemoryCandidate
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-020
- status: Target

### 面试官问题

为什么模型不能直接写 Active Memory？

### 他真正想考什么

检验是否能把 candidate 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

模型输出可能有幻觉、越权、提示注入或错误泛化；确定性Write Policy和Governance必须在激活前审查来源、Scope、confidence和冲突。

### 深挖回答

模型输出可能有幻觉、越权、提示注入或错误泛化；确定性Write Policy和Governance必须在激活前审查来源、Scope、confidence和冲突。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 26. MemoryCandidate 状态机
- docs/project/modules/05-memory-context.md — § 38. MemoryCandidate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q144 MemoryVersion 为什么不可变？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: memory
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、version
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 27. MemoryVersion 状态机
  - docs/project/modules/05-memory-context.md — § 41. MemoryRecord 与 MemoryVersion
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

MemoryVersion 为什么不可变？

### 他真正想考什么

检验是否能把 version 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

不可变版本保留provenance、时间、Scope、supersedes和审计，修正通过新版本替代，而不是把历史事实悄悄改掉。

### 深挖回答

不可变版本保留provenance、时间、Scope、supersedes和审计，修正通过新版本替代，而不是把历史事实悄悄改掉。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 27. MemoryVersion 状态机
- docs/project/modules/05-memory-context.md — § 41. MemoryRecord 与 MemoryVersion

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q145 SUPERSEDED 和 STALE 有什么区别？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: memory
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、states
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 27. MemoryVersion 状态机
  - docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

SUPERSEDED 和 STALE 有什么区别？

### 他真正想考什么

检验是否能把 states 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

SUPERSEDED表示有新的显式版本替代；STALE表示时间或事实有效性不足，可能待验证，不等于已经有替代版本。

### 深挖回答

SUPERSEDED表示有新的显式版本替代；STALE表示时间或事实有效性不足，可能待验证，不等于已经有替代版本。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 27. MemoryVersion 状态机
- docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q146 DORMANT 何时使用？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: memory
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、states
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 27. MemoryVersion 状态机
  - docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

DORMANT 何时使用？

### 他真正想考什么

检验是否能把 states 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Memory仍可恢复但长期Utility低或暂不适合默认召回时进入Dormant；它不是删除，也不能绕过Scope和Freshness验证。

### 深挖回答

Memory仍可恢复但长期Utility低或暂不适合默认召回时进入Dormant；它不是删除，也不能绕过Scope和Freshness验证。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 27. MemoryVersion 状态机
- docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q147 QUARANTINED 处理什么？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/02_则知科技_Agent开发实习/01_面试_QA整理.md
- primary_domain: memory
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、states
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 27. MemoryVersion 状态机
  - docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-024
- status: Target

### 面试官问题

QUARANTINED 处理什么？

### 他真正想考什么

检验是否能把 states 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

发现污染、冲突、Prompt Injection或来源异常时隔离MemoryVersion/Projection，禁止默认Recall，保留证据等待修复或Revoke。

### 深挖回答

发现污染、冲突、Prompt Injection或来源异常时隔离MemoryVersion/Projection，禁止默认Recall，保留证据等待修复或Revoke。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 27. MemoryVersion 状态机
- docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q148 REVOKED 和 DELETED 的边界是什么？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: memory
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、states
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 27. MemoryVersion 状态机
  - docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

REVOKED 和 DELETED 的边界是什么？

### 他真正想考什么

检验是否能把 states 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Revoked表示不可继续使用但保留必要审计/法务事实；Deleted是按Privacy/Retention规则移除可删除内容，二者受Legal Hold和lineage约束。

### 深挖回答

Revoked表示不可继续使用但保留必要审计/法务事实；Deleted是按Privacy/Retention规则移除可删除内容，二者受Legal Hold和lineage约束。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 27. MemoryVersion 状态机
- docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q149 Memory Poisoning 可能怎样发生？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: memory
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、poison
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染
  - docs/project/modules/05-memory-context.md — § 56. Freshness 与 Verify-before-use
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-026
- status: Target

### 面试官问题

Memory Poisoning 可能怎样发生？

### 他真正想考什么

检验是否能把 poison 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

不可信Tool Output、用户输入、模型错误总结或跨Workspace引用可能把错误内容写成候选；必须做Trust Label、Scope、Conflict和Governance。

### 深挖回答

不可信Tool Output、用户输入、模型错误总结或跨Workspace引用可能把错误内容写成候选；必须做Trust Label、Scope、Conflict和Governance。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染
- docs/project/modules/05-memory-context.md — § 56. Freshness 与 Verify-before-use

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q150 旧错误偏好如何纠正？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: memory
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、poison
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染
  - docs/project/modules/05-memory-context.md — § 56. Freshness 与 Verify-before-use
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

旧错误偏好如何纠正？

### 他真正想考什么

检验是否能把 poison 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

将旧MemoryVersion标为QUARANTINED/REVOKED或SUPERSEDED，创建新Candidate和新Version；不原地修改，也要重建Projection和失效Cache。

### 深挖回答

将旧MemoryVersion标为QUARANTINED/REVOKED或SUPERSEDED，创建新Candidate和新Version；不原地修改，也要重建Projection和失效Cache。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 55. Prompt Injection 与记忆污染
- docs/project/modules/05-memory-context.md — § 56. Freshness 与 Verify-before-use

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

### Interview Drill Chain 4：Q151–Q159

连续追问从概念进入机制、失败、取舍和证据。

## Q151 User Prompt 与旧 Memory 冲突怎么办？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/02_则知科技_Agent开发实习/01_面试_QA整理.md
- primary_domain: memory
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、conflict
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
  - docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-028
- status: Target

### 面试官问题

User Prompt 与旧 Memory 冲突怎么办？

### 他真正想考什么

检验是否能把 conflict 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

当前明确用户指令只影响本次Intent/ContextPack，不必篡改长期偏好；记录UseTrace或负迁移信号，长期变更仍走Candidate治理。

### 深挖回答

当前明确用户指令只影响本次Intent/ContextPack，不必篡改长期偏好；记录UseTrace或负迁移信号，长期变更仍走Candidate治理。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

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

## Q152 User Assertion 与 Knowledge 冲突怎么办？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: memory
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、conflict
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
  - docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-029
- status: Target

### 面试官问题

User Assertion 与 Knowledge 冲突怎么办？

### 他真正想考什么

检验是否能把 conflict 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

当前用户意图优先于旧偏好，但企业Domain Fact要按Authority、Version、Time和Scope使用Knowledge Evidence，不把用户陈述直接当权威规则。

### 深挖回答

当前用户意图优先于旧偏好，但企业Domain Fact要按Authority、Version、Time和Scope使用Knowledge Evidence，不把用户陈述直接当权威规则。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

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

## Q153 Memory 与 Knowledge 冲突怎么办？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: memory
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、conflict
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
  - docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Memory 与 Knowledge 冲突怎么办？

### 他真正想考什么

检验是否能把 conflict 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Knowledge拥有企业事实，Memory拥有可复用上下文；按事实类型、来源权威、时间和任务Scope解决，Memory不能覆盖有权威证据的合同事实。

### 深挖回答

Knowledge拥有企业事实，Memory拥有可复用上下文；按事实类型、来源权威、时间和任务Scope解决，Memory不能覆盖有权威证据的合同事实。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

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

## Q154 Memory 与 Security 冲突怎么办？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: memory
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、conflict
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
  - docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Memory 与 Security 冲突怎么办？

### 他真正想考什么

检验是否能把 conflict 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Security优先；Memory只能在当前授权Scope和Epoch内被召回，任何偏好或Procedural Hint都不能扩大数据、Tool或Recipient权限。

### 深挖回答

Security优先；Memory只能在当前授权Scope和Epoch内被召回，任何偏好或Procedural Hint都不能扩大数据、Tool或Recipient权限。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

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

## Q155 跨Workspace Memory 如何隔离？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/02_则知科技_Agent开发实习/01_面试_QA整理.md
- primary_domain: memory
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、security
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
  - docs/project/modules/05-memory-context.md — § 57. Procedural Memory 安全边界
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

跨Workspace Memory 如何隔离？

### 他真正想考什么

检验是否能把 security 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Canonical MemoryVersion、ContextPack、Projection和Recall都携带Tenant/Workspace/Subject Scope，跨域引用需显式授权和审计。

### 深挖回答

Canonical MemoryVersion、ContextPack、Projection和Recall都携带Tenant/Workspace/Subject Scope，跨域引用需显式授权和审计。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
- docs/project/modules/05-memory-context.md — § 57. Procedural Memory 安全边界

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q156 Privacy Delete 如何影响Projection？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: memory
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、privacy
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 25. Privacy Delete、Revoke 与 Legal Hold
  - docs/project/modules/05-memory-context.md — § 64. Index 与 Projection
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Privacy Delete 如何影响Projection？

### 他真正想考什么

检验是否能把 privacy 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

删除/撤销请求先形成治理事实，再使Vector、Graph、Manifest、Cache和Context Projection失效或重建；Projection不能反向保留被删除权威。

### 深挖回答

删除/撤销请求先形成治理事实，再使Vector、Graph、Manifest、Cache和Context Projection失效或重建；Projection不能反向保留被删除权威。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 25. Privacy Delete、Revoke 与 Legal Hold
- docs/project/modules/05-memory-context.md — § 64. Index 与 Projection

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q157 为什么不能只用 TTL 淘汰 Memory？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: memory
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、forgetting
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 24. Consolidation
  - docs/project/modules/05-memory-context.md — § 70. Compression Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么不能只用 TTL 淘汰 Memory？

### 他真正想考什么

检验是否能把 forgetting 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

新鲜度不是唯一价值；还要考虑Utility、冲突、权威、隐私、Scope、用户纠正、Legal Hold和负迁移。

### 深挖回答

新鲜度不是唯一价值；还要考虑Utility、冲突、权威、隐私、Scope、用户纠正、Legal Hold和负迁移。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 24. Consolidation
- docs/project/modules/05-memory-context.md — § 70. Compression Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q158 Memory Utility 如何评估？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 48. MemoryUseTrace 与 MemoryUtilityProjection
- primary_domain: memory
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、utility
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 48. MemoryUseTrace 与 MemoryUtilityProjection
  - docs/project/modules/05-memory-context.md — § 77. Eval Gate
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Memory Utility 如何评估？

### 他真正想考什么

检验是否能把 utility 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

记录Recall、UseTrace、任务帮助、重复命中、冲突和negative transfer，按类型、Scope、时间和任务slice分析，不凭单次成功宣称价值。

### 深挖回答

记录Recall、UseTrace、任务帮助、重复命中、冲突和negative transfer，按类型、Scope、时间和任务slice分析，不凭单次成功宣称价值。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 48. MemoryUseTrace 与 MemoryUtilityProjection
- docs/project/modules/05-memory-context.md — § 77. Eval Gate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q159 negative transfer 是什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 48. MemoryUseTrace 与 MemoryUtilityProjection
- primary_domain: memory
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、utility
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 48. MemoryUseTrace 与 MemoryUtilityProjection
  - docs/project/modules/05-memory-context.md — § 77. Eval Gate
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

negative transfer 是什么？

### 他真正想考什么

检验是否能把 utility 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

旧记忆被召回后让当前任务更差，例如过期偏好覆盖当前指令；要通过UseTrace、冲突标签和Eval检测并降低Utility或隔离。

### 深挖回答

旧记忆被召回后让当前任务更差，例如过期偏好覆盖当前指令；要通过UseTrace、冲突标签和Eval检测并降低Utility或隔离。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 48. MemoryUseTrace 与 MemoryUtilityProjection
- docs/project/modules/05-memory-context.md — § 77. Eval Gate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

### Interview Drill Chain 5：Q160–Q167

连续追问从概念进入机制、失败、取舍和证据。

## Q160 长期 Memory 如何召回？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 11. Long-term Memory 如何重新进入 Working Context
- primary_domain: memory
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、recall
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 11. Long-term Memory 如何重新进入 Working Context
  - docs/project/modules/05-memory-context.md — § 64. Index 与 Projection
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

长期 Memory 如何召回？

### 他真正想考什么

检验是否能把 recall 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

先按Scope、Policy、Freshness、类型和任务相关性过滤，再从Canonical MemoryVersion的Projection中召回，最终进入只读ContextPack。

### 深挖回答

先按Scope、Policy、Freshness、类型和任务相关性过滤，再从Canonical MemoryVersion的Projection中召回，最终进入只读ContextPack。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 11. Long-term Memory 如何重新进入 Working Context
- docs/project/modules/05-memory-context.md — § 64. Index 与 Projection

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q161 Vector DB 是不是 Memory 事实源？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 11. Long-term Memory 如何重新进入 Working Context
- primary_domain: memory
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、recall
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 11. Long-term Memory 如何重新进入 Working Context
  - docs/project/modules/05-memory-context.md — § 64. Index 与 Projection
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-05-038
- status: Target

### 面试官问题

Vector DB 是不是 Memory 事实源？

### 他真正想考什么

检验是否能把 recall 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

不是。Vector、Graph、Lexical都是可重建Projection，Canonical事实是不可变MemoryVersion和其治理/lineage。

### 深挖回答

不是。Vector、Graph、Lexical都是可重建Projection，Canonical事实是不可变MemoryVersion和其治理/lineage。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 11. Long-term Memory 如何重新进入 Working Context
- docs/project/modules/05-memory-context.md — § 64. Index 与 Projection

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q162 压缩错误怎么办？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 36. 恢复与 Reconciliation
- primary_domain: memory
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、recovery
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 36. 恢复与 Reconciliation
  - docs/project/modules/05-memory-context.md — § 29. ContextPackBuild 状态机
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

压缩错误怎么办？

### 他真正想考什么

检验是否能把 recovery 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

保留原始Version和CompressionTrace，验证失败则回退到上一个合法ContextPack/SessionSummary，重新选择压缩策略，不能静默覆盖。

### 深挖回答

保留原始Version和CompressionTrace，验证失败则回退到上一个合法ContextPack/SessionSummary，重新选择压缩策略，不能静默覆盖。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 36. 恢复与 Reconciliation
- docs/project/modules/05-memory-context.md — § 29. ContextPackBuild 状态机

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q163 用户反复纠正某条记忆怎么办？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
- primary_domain: memory
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、conflict
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
  - docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

用户反复纠正某条记忆怎么办？

### 他真正想考什么

检验是否能把 conflict 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

把纠正作为高优先级Source Fact/Candidate，累积Conflict和provenance，创建新版本并让旧版本Superseded/Quarantined；不能只改一个向量。

### 深挖回答

把纠正作为高优先级Source Fact/Candidate，累积Conflict和provenance，创建新版本并让旧版本Superseded/Quarantined；不能只改一个向量。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

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

## Q164 Procedural Hint 建议的策略与当前Task不一致怎么办？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
- primary_domain: memory
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、security
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
  - docs/project/modules/05-memory-context.md — § 57. Procedural Memory 安全边界
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Procedural Hint 建议的策略与当前Task不一致怎么办？

### 他真正想考什么

检验是否能把 security 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

它只能作为低权重Strategy Hint，必须服从当前用户指令、Security、Skill、Tool Permission、Plan和Approval。

### 深挖回答

它只能作为低权重Strategy Hint，必须服从当前用户指令、Security、Skill、Tool Permission、Plan和Approval。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 54. Security 与 Privacy
- docs/project/modules/05-memory-context.md — § 57. Procedural Memory 安全边界

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q165 如何评测 Memory 是否有价值？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 80. 设计依据与取舍
- primary_domain: memory
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、eval
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 80. 设计依据与取舍
  - docs/project/modules/05-memory-context.md — § 77. Eval Gate
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

如何评测 Memory 是否有价值？

### 他真正想考什么

检验是否能把 eval 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

测Recall Precision、Task Utility、negative transfer、污染率、纠正延迟、跨Workspace泄露和Projection一致性，分层比较有/无Memory及不同Policy。

### 深挖回答

测Recall Precision、Task Utility、negative transfer、污染率、纠正延迟、跨Workspace泄露和Projection一致性，分层比较有/无Memory及不同Policy。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 80. 设计依据与取舍
- docs/project/modules/05-memory-context.md — § 77. Eval Gate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q166 Memory 文档哪些是Current，哪些是Target？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 78. 完成证据
- primary_domain: memory
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、current
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 78. 完成证据
  - docs/project/modules/05-memory-context.md — § 80. 设计依据与取舍
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Memory 文档哪些是Current，哪些是Target？

### 他真正想考什么

检验是否能把 current 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

生命周期、Candidate、Governance和Version是Target Contract；Current只能由代码、测试、Trace/Eval和证据提升，不能凭文档名或Projection存在宣称完成。

### 深挖回答

生命周期、Candidate、Governance和Version是Target Contract；Current只能由代码、测试、Trace/Eval和证据提升，不能凭文档名或Projection存在宣称完成。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 78. 完成证据
- docs/project/modules/05-memory-context.md — § 80. 设计依据与取舍

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q167 Checkpoint 和 MemoryVersion 如何避免互相冒充？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
- primary_domain: memory
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Memory、ContextPack、boundary
- architecture_refs:
  - docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
  - docs/project/modules/05-memory-context.md — § 5. Cross-module Ownership
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Checkpoint 和 MemoryVersion 如何避免互相冒充？

### 他真正想考什么

检验是否能把 boundary 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Checkpoint只恢复控制状态和已提交Generation，MemoryVersion是独立领域事实；两者通过引用和Generation一致性协作，不能用Checkpoint伪造记忆。

### 深挖回答

Checkpoint只恢复控制状态和已提交Generation，MemoryVersion是独立领域事实；两者通过引用和Generation一致性协作，不能用Checkpoint伪造记忆。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/project/modules/05-memory-context.md — § 3. Context、Memory、Knowledge 和 Checkpoint 的边界
- docs/project/modules/05-memory-context.md — § 5. Cross-module Ownership

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。
