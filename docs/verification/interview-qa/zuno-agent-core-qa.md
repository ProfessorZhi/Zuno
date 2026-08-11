# 04 Agent Core / Planning & Control QA

> Architecture Verification Corpus；不是canonical architecture。答案只从正式架构文档重生成。

### Interview Drill Chain 1：Q168–Q176

连续追问从概念进入机制、失败、取舍和证据。

## Q168 为什么 Zuno 选择 Single Controller 而不是产品级 Multi-Agent？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: agent
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、control
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 1. 控制权模型
  - docs/modules/06-agent-core-planning-control.md — § 16. Cross-module Ownership
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-001
- status: Target

### 面试官问题

为什么 Zuno 选择 Single Controller 而不是产品级 Multi-Agent？

### 他真正想考什么

检验是否能把 control 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Single Controller统一Run、Plan、Policy、Budget和最终控制；工程上可并行协作但不改变产品Runtime的单一控制权。

### 深挖回答

Single Controller统一Run、Plan、Policy、Budget和最终控制；工程上可并行协作但不改变产品Runtime的单一控制权。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 1. 控制权模型
- docs/modules/06-agent-core-planning-control.md — § 16. Cross-module Ownership

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。
## Q169 为什么不能把多个Agent都当平级Controller？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+一面+001/正文.md
- primary_domain: agent
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、control
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 1. 控制权模型
  - docs/modules/06-agent-core-planning-control.md — § 16. Cross-module Ownership
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么不能把多个Agent都当平级Controller？

### 他真正想考什么

检验是否能把 control 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

平级Controller会造成状态、权限、Plan和Effect ownership冲突；协作能力应作为受控Step/Adapter而非多头事实源。

### 深挖回答

平级Controller会造成状态、权限、Plan和Effect ownership冲突；协作能力应作为受控Step/Adapter而非多头事实源。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 1. 控制权模型
- docs/modules/06-agent-core-planning-control.md — § 16. Cross-module Ownership

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q170 为什么保留固定 AgentRunGraph？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+字节+二面+003/正文.md
- primary_domain: agent
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、graph
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 10. AgentRunGraph
  - docs/modules/06-agent-core-planning-control.md — § 11. StepExecutionGraph
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么保留固定 AgentRunGraph？

### 他真正想考什么

检验是否能把 graph 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

固定图提供生命周期、Gate、恢复和审计的稳定骨架，动态差异放进不可变Plan DAG而不是让模型生成任意控制流。

### 深挖回答

固定图提供生命周期、Gate、恢复和审计的稳定骨架，动态差异放进不可变Plan DAG而不是让模型生成任意控制流。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 10. AgentRunGraph
- docs/modules/06-agent-core-planning-control.md — § 11. StepExecutionGraph

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q171 为什么 Plan DAG 需要动态？

- source_type: REAL
- source_ref: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: agent
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、plan
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 6. 所有任务都必须有 Plan
  - docs/modules/06-agent-core-planning-control.md — § 9. Plan DAG
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-004
- status: Target

### 面试官问题

为什么 Plan DAG 需要动态？

### 他真正想考什么

检验是否能把 plan 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

任务依赖、并行度、工具和证据需求不同，Plan DAG允许按Goal和Capability生成结构，同时仍受固定RunGraph和Policy约束。

### 深挖回答

任务依赖、并行度、工具和证据需求不同，Plan DAG允许按Goal和Capability生成结构，同时仍受固定RunGraph和Policy约束。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 6. 所有任务都必须有 Plan
- docs/modules/06-agent-core-planning-control.md — § 9. Plan DAG

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q172 固定 StepExecutionGraph 解决什么？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: agent
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、graph
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 10. AgentRunGraph
  - docs/modules/06-agent-core-planning-control.md — § 11. StepExecutionGraph
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

固定 StepExecutionGraph 解决什么？

### 他真正想考什么

检验是否能把 graph 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

它把Step的准备、Action、Observation、Evaluation、Acceptance、Retry/Repair和Effect边界固定，避免每个Plan重新发明执行语义。

### 深挖回答

它把Step的准备、Action、Observation、Evaluation、Acceptance、Retry/Repair和Effect边界固定，避免每个Plan重新发明执行语义。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 10. AgentRunGraph
- docs/modules/06-agent-core-planning-control.md — § 11. StepExecutionGraph

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q173 Plan-and-Execute、ReAct、Reflection、Replan、Reflexion为何不是五选一？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+一面+001/正文.md
- primary_domain: agent
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、mechanisms
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 5. 五种机制
  - docs/modules/06-agent-core-planning-control.md — § 13. Reflection、Retry 与 Replan
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-006
- status: Target

### 面试官问题

Plan-and-Execute、ReAct、Reflection、Replan、Reflexion为何不是五选一？

### 他真正想考什么

检验是否能把 mechanisms 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

它们处在不同控制层：Plan定义全局依赖，ReAct执行局部循环，Reflection评估修复，Replan改变计划，Reflexion在Run后形成经验候选。

### 深挖回答

它们处在不同控制层：Plan定义全局依赖，ReAct执行局部循环，Reflection评估修复，Replan改变计划，Reflexion在Run后形成经验候选。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 5. 五种机制
- docs/modules/06-agent-core-planning-control.md — § 13. Reflection、Retry 与 Replan

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q174 为什么简单问题也必须有 Plan？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+字节+二面+003/正文.md
- primary_domain: agent
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、plan
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 6. 所有任务都必须有 Plan
  - docs/modules/06-agent-core-planning-control.md — § 9. Plan DAG
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么简单问题也必须有 Plan？

### 他真正想考什么

检验是否能把 plan 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

简单任务可以是Deterministic Single-Step Plan，但统一Plan让预算、权限、验收、审计、恢复和最终Gate保持一致。

### 深挖回答

简单任务可以是Deterministic Single-Step Plan，但统一Plan让预算、权限、验收、审计、恢复和最终Gate保持一致。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 6. 所有任务都必须有 Plan
- docs/modules/06-agent-core-planning-control.md — § 9. Plan DAG

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q175 复杂任务的 PlanStep 至少包含什么？

- source_type: REAL
- source_ref: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: agent
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、plan
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 6. 所有任务都必须有 Plan
  - docs/modules/06-agent-core-planning-control.md — § 9. Plan DAG
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

复杂任务的 PlanStep 至少包含什么？

### 他真正想考什么

检验是否能把 plan 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

至少需要输入/输出、依赖、Activation、AcceptancePolicy、预算、资源、能力、Effect和失败处置，才能被确定性Runtime调度。

### 深挖回答

至少需要输入/输出、依赖、Activation、AcceptancePolicy、预算、资源、能力、Effect和失败处置，才能被确定性Runtime调度。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 6. 所有任务都必须有 Plan
- docs/modules/06-agent-core-planning-control.md — § 9. Plan DAG

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q176 ReAct 的 Action、Observation 和下一步如何闭环？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: agent
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、react
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 11. StepExecutionGraph
  - docs/modules/06-agent-core-planning-control.md — § 31. Action 生命周期与对账结果
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-009
- status: Target

### 面试官问题

ReAct 的 Action、Observation 和下一步如何闭环？

### 他真正想考什么

检验是否能把 react 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Agent提出ActionProposal，Tool/Knowledge返回Observation，Action Evaluation判断是否满足Step Acceptance；未满足时按Policy继续、Repair、Fallback或退出。

### 深挖回答

Agent提出ActionProposal，Tool/Knowledge返回Observation，Action Evaluation判断是否满足Step Acceptance；未满足时按Policy继续、Repair、Fallback或退出。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 11. StepExecutionGraph
- docs/modules/06-agent-core-planning-control.md — § 31. Action 生命周期与对账结果

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

### Interview Drill Chain 2：Q177–Q185

连续追问从概念进入机制、失败、取舍和证据。

## Q177 为什么不能让 ReAct 无限循环？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+一面+001/正文.md
- primary_domain: agent
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、react
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 11. StepExecutionGraph
  - docs/modules/06-agent-core-planning-control.md — § 31. Action 生命周期与对账结果
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么不能让 ReAct 无限循环？

### 他真正想考什么

检验是否能把 react 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

每个Step受最大Action、No-progress、Budget、Deadline、Policy和Acceptance Gate限制；达到边界必须Stop、Partial、Fail或Replan。

### 深挖回答

每个Step受最大Action、No-progress、Budget、Deadline、Policy和Acceptance Gate限制；达到边界必须Stop、Partial、Fail或Replan。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 11. StepExecutionGraph
- docs/modules/06-agent-core-planning-control.md — § 31. Action 生命周期与对账结果

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q178 Action Evaluation 与 Step Acceptance 有什么区别？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+字节+二面+003/正文.md
- primary_domain: agent
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、evaluation
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract
  - docs/modules/06-agent-core-planning-control.md — § 35. Failure Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Action Evaluation 与 Step Acceptance 有什么区别？

### 他真正想考什么

检验是否能把 evaluation 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Action Evaluation判断一次动作结果；Step Acceptance判断整个Step是否满足预先声明的验收条件，前者不等于后者。

### 深挖回答

Action Evaluation判断一次动作结果；Step Acceptance判断整个Step是否满足预先声明的验收条件，前者不等于后者。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract
- docs/modules/06-agent-core-planning-control.md — § 35. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q179 Reflection 什么时候触发？

- source_type: REAL
- source_ref: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: agent
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、reflection
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 13. Reflection、Retry 与 Replan
  - docs/modules/06-agent-core-planning-control.md — § 14. Finalization 与 Publication
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-012
- status: Target

### 面试官问题

Reflection 什么时候触发？

### 他真正想考什么

检验是否能把 reflection 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

在Acceptance失败、矛盾、低质量、重复无进展或显式Review Policy触发时使用，不是每个Step固定调用模型。

### 深挖回答

在Acceptance失败、矛盾、低质量、重复无进展或显式Review Policy触发时使用，不是每个Step固定调用模型。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 13. Reflection、Retry 与 Replan
- docs/modules/06-agent-core-planning-control.md — § 14. Finalization 与 Publication

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q180 为什么不是每 Step 都做 LLM Reflection？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: agent
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、reflection
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 13. Reflection、Retry 与 Replan
  - docs/modules/06-agent-core-planning-control.md — § 14. Finalization 与 Publication
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么不是每 Step 都做 LLM Reflection？

### 他真正想考什么

检验是否能把 reflection 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

固定反思会增加成本和延迟并制造伪改进；确定性Failure/Acceptance先筛选，只有需要诊断或修复时才调用Reflection。

### 深挖回答

固定反思会增加成本和延迟并制造伪改进；确定性Failure/Acceptance先筛选，只有需要诊断或修复时才调用Reflection。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 13. Reflection、Retry 与 Replan
- docs/modules/06-agent-core-planning-control.md — § 14. Finalization 与 Publication

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q181 Retry、Parameter Repair、Capability Fallback、Model Escalation怎么区分？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+一面+001/正文.md
- primary_domain: agent
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、repair
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan
  - docs/modules/06-agent-core-planning-control.md — § 35. Failure Decision Matrix
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-014
- status: Target

### 面试官问题

Retry、Parameter Repair、Capability Fallback、Model Escalation怎么区分？

### 他真正想考什么

检验是否能把 repair 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Retry重做同动作，Repair改变参数，Fallback换兼容能力，Escalation换模型角色；每种都须有失败码、预算和幂等边界。

### 深挖回答

Retry重做同动作，Repair改变参数，Fallback换兼容能力，Escalation换模型角色；每种都须有失败码、预算和幂等边界。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan
- docs/modules/06-agent-core-planning-control.md — § 35. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q182 Step Repair 与 Replan 的边界是什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+字节+二面+003/正文.md
- primary_domain: agent
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、replan
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 9. Replan Barrier
  - docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-015
- status: Target

### 面试官问题

Step Repair 与 Replan 的边界是什么？

### 他真正想考什么

检验是否能把 replan 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Step仍然合法且目标/依赖未变时Repair；目标、计划依赖、能力结构或强制前提失效时必须Replan。

### 深挖回答

Step仍然合法且目标/依赖未变时Repair；目标、计划依赖、能力结构或强制前提失效时必须Replan。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 9. Replan Barrier
- docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q183 PlanVersion 为什么 immutable？

- source_type: REAL
- source_ref: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: agent
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、version
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 4. PlanVersion 状态机
  - docs/modules/06-agent-core-planning-control.md — § 17. Contract Versioning
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

PlanVersion 为什么 immutable？

### 他真正想考什么

检验是否能把 version 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

激活后不原地修改，才能让已运行Step、Approval、Branch和Trace引用同一计划事实；变化创建新Version并保留supersedes lineage。

### 深挖回答

激活后不原地修改，才能让已运行Step、Approval、Branch和Trace引用同一计划事实；变化创建新Version并保留supersedes lineage。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 4. PlanVersion 状态机
- docs/modules/06-agent-core-planning-control.md — § 17. Contract Versioning

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q184 Replan Barrier 做什么？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: agent
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、replan
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 9. Replan Barrier
  - docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-017
- status: Target

### 面试官问题

Replan Barrier 做什么？

### 他真正想考什么

检验是否能把 replan 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

它冻结旧Plan的继续扩散，等待合法分支收口/失效，创建并激活新PlanVersion，防止旧Epoch晚到结果写入新计划。

### 深挖回答

它冻结旧Plan的继续扩散，等待合法分支收口/失效，创建并激活新PlanVersion，防止旧Epoch晚到结果写入新计划。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 9. Replan Barrier
- docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q185 ReadySet 为什么不等于可以并行？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+一面+001/正文.md
- primary_domain: agent
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、parallel
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
  - docs/modules/06-agent-core-planning-control.md — § 43. Resource Conflict Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

ReadySet 为什么不等于可以并行？

### 他真正想考什么

检验是否能把 parallel 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Ready只说明依赖满足，还要检查输入、Capability、Security、Budget、Quota、ResourceClaim、Side-effect和JoinPolicy。

### 深挖回答

Ready只说明依赖满足，还要检查输入、Capability、Security、Budget、Quota、ResourceClaim、Side-effect和JoinPolicy。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
- docs/modules/06-agent-core-planning-control.md — § 43. Resource Conflict Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

### Interview Drill Chain 3：Q186–Q194

连续追问从概念进入机制、失败、取舍和证据。

## Q186 资源冲突如何阻止并行？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+字节+二面+003/正文.md
- primary_domain: agent
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、parallel
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
  - docs/modules/06-agent-core-planning-control.md — § 43. Resource Conflict Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

资源冲突如何阻止并行？

### 他真正想考什么

检验是否能把 parallel 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

ResourceClaim和互斥/写冲突矩阵在Dispatch前确定性拒绝或串行化有冲突分支，不能靠模型自觉避免。

### 深挖回答

ResourceClaim和互斥/写冲突矩阵在Dispatch前确定性拒绝或串行化有冲突分支，不能靠模型自觉避免。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
- docs/modules/06-agent-core-planning-control.md — § 43. Resource Conflict Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q187 为什么副作用Step通常需要更严格的并行条件？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: agent
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、parallel
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
  - docs/modules/06-agent-core-planning-control.md — § 43. Resource Conflict Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么副作用Step通常需要更严格的并行条件？

### 他真正想考什么

检验是否能把 parallel 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

并行可能产生重复、顺序和补偿问题；必须满足Effect Policy、幂等、资源隔离、Approval和可对账条件。

### 深挖回答

并行可能产生重复、顺序和补偿问题；必须满足Effect Policy、幂等、资源隔离、Approval和可对账条件。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
- docs/modules/06-agent-core-planning-control.md — § 43. Resource Conflict Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q188 LangGraph Send 在架构中是什么？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: agent
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、langgraph
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 41. LangGraph Adapter Contract
  - docs/modules/06-agent-core-planning-control.md — § 8. Dispatch、Fencing 与 Reducer
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

LangGraph Send 在架构中是什么？

### 他真正想考什么

检验是否能把 langgraph 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

它是执行Adapter的并行分发机制，不拥有Plan或业务事实；分发前必须有durable Dispatch和版本/epoch guard。

### 深挖回答

它是执行Adapter的并行分发机制，不拥有Plan或业务事实；分发前必须有durable Dispatch和版本/epoch guard。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 41. LangGraph Adapter Contract
- docs/modules/06-agent-core-planning-control.md — § 8. Dispatch、Fencing 与 Reducer

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q189 为什么要先 commit Dispatch 再 Send？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+一面+001/正文.md
- primary_domain: agent
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、dispatch
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 8. Dispatch、Fencing 与 Reducer
  - docs/modules/06-agent-core-planning-control.md — § 11. Side Effect Protocol
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-022
- status: Target

### 面试官问题

为什么要先 commit Dispatch 再 Send？

### 他真正想考什么

检验是否能把 dispatch 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

先落持久化Dispatch、generation和幂等键，Crash后才能判断是否已派发；否则重启无法区分未发送与已发送Effect。

### 深挖回答

先落持久化Dispatch、generation和幂等键，Crash后才能判断是否已派发；否则重启无法区分未发送与已发送Effect。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 8. Dispatch、Fencing 与 Reducer
- docs/modules/06-agent-core-planning-control.md — § 11. Side Effect Protocol

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q190 BranchResultRef 为什么不直接写共享State？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+字节+二面+003/正文.md
- primary_domain: agent
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、join
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
  - docs/modules/06-agent-core-planning-control.md — § 6. DAG、Condition 与 Disposition
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

BranchResultRef 为什么不直接写共享State？

### 他真正想考什么

检验是否能把 join 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

引用化结果和版本化Reducer避免大Payload、晚到分支和并发写覆盖；Join按PlanVersion、Branch和Generation收集结果。

### 深挖回答

引用化结果和版本化Reducer避免大Payload、晚到分支和并发写覆盖；Join按PlanVersion、Branch和Generation收集结果。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
- docs/modules/06-agent-core-planning-control.md — § 6. DAG、Condition 与 Disposition

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q191 ALL_REQUIRED、BEST_EFFORT、QUORUM、FIRST_VALID有什么差异？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: agent
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、join
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
  - docs/modules/06-agent-core-planning-control.md — § 6. DAG、Condition 与 Disposition
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

ALL_REQUIRED、BEST_EFFORT、QUORUM、FIRST_VALID有什么差异？

### 他真正想考什么

检验是否能把 join 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

它们定义Join的接受条件：全部、允许缺失、达到门槛或首个有效结果；必须由Plan/Policy预先固定而非运行中随意改变。

### 深挖回答

它们定义Join的接受条件：全部、允许缺失、达到门槛或首个有效结果；必须由Plan/Policy预先固定而非运行中随意改变。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
- docs/modules/06-agent-core-planning-control.md — § 6. DAG、Condition 与 Disposition

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q192 部分分支失败时Run怎么处理？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: agent
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、join
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
  - docs/modules/06-agent-core-planning-control.md — § 6. DAG、Condition 与 Disposition
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

部分分支失败时Run怎么处理？

### 他真正想考什么

检验是否能把 join 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

先由JoinPolicy和Acceptance判断可继续、降级、Retry/Repair、Replan或Fail；不能把失败静默当成功。

### 深挖回答

先由JoinPolicy和Acceptance判断可继续、降级、Retry/Repair、Replan或Fail；不能把失败静默当成功。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
- docs/modules/06-agent-core-planning-control.md — § 6. DAG、Condition 与 Disposition

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q193 晚到 BranchResult 如何避免污染新Plan？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+一面+001/正文.md
- primary_domain: agent
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、join
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
  - docs/modules/06-agent-core-planning-control.md — § 6. DAG、Condition 与 Disposition
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-026
- status: Target

### 面试官问题

晚到 BranchResult 如何避免污染新Plan？

### 他真正想考什么

检验是否能把 join 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

结果携带PlanVersion、controller_epoch、execution_epoch和generation；Replan Barrier后的旧Result只能记录/拒绝，不能创建新StepRun。

### 深挖回答

结果携带PlanVersion、controller_epoch、execution_epoch和generation；Replan Barrier后的旧Result只能记录/拒绝，不能创建新StepRun。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 7. ReadySet、Liveness 与 Join
- docs/modules/06-agent-core-planning-control.md — § 6. DAG、Condition 与 Disposition

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q194 Interrupt 适合哪些场景？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+字节+二面+003/正文.md
- primary_domain: agent
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、interrupt
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 10. Interrupt 与 Signal
  - docs/modules/06-agent-core-planning-control.md — § 15. Cancellation 与控制命令
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Interrupt 适合哪些场景？

### 他真正想考什么

检验是否能把 interrupt 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

用户输入、Approval wait、Security Review和External Job等需要外部条件的控制命令进入显式Interrupt/Waiting状态，不是异常抛出后丢失。

### 深挖回答

用户输入、Approval wait、Security Review和External Job等需要外部条件的控制命令进入显式Interrupt/Waiting状态，不是异常抛出后丢失。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 10. Interrupt 与 Signal
- docs/modules/06-agent-core-planning-control.md — § 15. Cancellation 与控制命令

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

### Interview Drill Chain 4：Q195–Q203

连续追问从概念进入机制、失败、取舍和证据。

## Q195 Approval wait 后如何 Resume？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: agent
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、interrupt
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 10. Interrupt 与 Signal
  - docs/modules/06-agent-core-planning-control.md — § 15. Cancellation 与控制命令
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-028
- status: Target

### 面试官问题

Approval wait 后如何 Resume？

### 他真正想考什么

检验是否能把 interrupt 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

持久化Interrupt、Pending Action、Approval binding和Epoch；恢复时重新检查Version、Scope和有效期，满足条件才继续Dispatch。

### 深挖回答

持久化Interrupt、Pending Action、Approval binding和Epoch；恢复时重新检查Version、Scope和有效期，满足条件才继续Dispatch。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 10. Interrupt 与 Signal
- docs/modules/06-agent-core-planning-control.md — § 15. Cancellation 与控制命令

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q196 Cancellation 能否取消已经发出的Tool Effect？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: agent
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、interrupt
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 10. Interrupt 与 Signal
  - docs/modules/06-agent-core-planning-control.md — § 15. Cancellation 与控制命令
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Cancellation 能否取消已经发出的Tool Effect？

### 他真正想考什么

检验是否能把 interrupt 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

只能停止未Dispatch或可中断控制；已发出且不可逆的Effect仍需Observation/Reconciliation，不能把取消当未执行。

### 深挖回答

只能停止未Dispatch或可中断控制；已发出且不可逆的Effect仍需Observation/Reconciliation，不能把取消当未执行。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 10. Interrupt 与 Signal
- docs/modules/06-agent-core-planning-control.md — § 15. Cancellation 与控制命令

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q197 Budget Ledger 由谁控制？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+一面+001/正文.md
- primary_domain: agent
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、budget
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 15. Budget、Admission 与 No-progress
  - docs/modules/06-agent-core-planning-control.md — § 36. Budget Ledger
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Budget Ledger 由谁控制？

### 他真正想考什么

检验是否能把 budget 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Agent Core拥有Run/Step预算仲裁，模块报告实际Usage/Cost；任何Retry、Reflection、Replan和并行扩张都要重新Admission。

### 深挖回答

Agent Core拥有Run/Step预算仲裁，模块报告实际Usage/Cost；任何Retry、Reflection、Replan和并行扩张都要重新Admission。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 15. Budget、Admission 与 No-progress
- docs/modules/06-agent-core-planning-control.md — § 36. Budget Ledger

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q198 Checkpointer 和 PostgreSQL 各自保存什么？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+字节+二面+003/正文.md
- primary_domain: agent
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、persistence
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 18. Checkpoint、Domain Fact 与 Object Payload
  - docs/modules/06-agent-core-planning-control.md — § 3. Domain Store 与 LangGraph Checkpoint 一致性
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-031
- status: Target

### 面试官问题

Checkpointer 和 PostgreSQL 各自保存什么？

### 他真正想考什么

检验是否能把 persistence 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

PostgreSQL保存权威Domain事实、Version、Outbox和可查询Receipt；Checkpointer保存可重建的控制快照/引用，不能替代Domain事实。

### 深挖回答

PostgreSQL保存权威Domain事实、Version、Outbox和可查询Receipt；Checkpointer保存可重建的控制快照/引用，不能替代Domain事实。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 18. Checkpoint、Domain Fact 与 Object Payload
- docs/modules/06-agent-core-planning-control.md — § 3. Domain Store 与 LangGraph Checkpoint 一致性

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q199 Crash 后 Checkpoint 比 Domain 新怎么办？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/03_遥望科技_通用Agent实习/01_HR面_原始逐字稿.md
- primary_domain: agent
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、persistence
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 18. Checkpoint、Domain Fact 与 Object Payload
  - docs/modules/06-agent-core-planning-control.md — § 3. Domain Store 与 LangGraph Checkpoint 一致性
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-032
- status: Target

### 面试官问题

Crash 后 Checkpoint 比 Domain 新怎么办？

### 他真正想考什么

检验是否能把 persistence 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

以已提交Domain Generation为准，回退或重建控制状态；Checkpoint不能伪造不存在的业务事实，异常快照进入quarantine。

### 深挖回答

以已提交Domain Generation为准，回退或重建控制状态；Checkpoint不能伪造不存在的业务事实，异常快照进入quarantine。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 18. Checkpoint、Domain Fact 与 Object Payload
- docs/modules/06-agent-core-planning-control.md — § 3. Domain Store 与 LangGraph Checkpoint 一致性

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q200 Checkpoint 比 Domain 旧怎么办？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: agent
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、persistence
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 18. Checkpoint、Domain Fact 与 Object Payload
  - docs/modules/06-agent-core-planning-control.md — § 3. Domain Store 与 LangGraph Checkpoint 一致性
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Checkpoint 比 Domain 旧怎么办？

### 他真正想考什么

检验是否能把 persistence 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

从最后合法Domain事实和必要引用重建控制状态，重放控制而不是重新产生外部Effect。

### 深挖回答

从最后合法Domain事实和必要引用重建控制状态，重放控制而不是重新产生外部Effect。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 18. Checkpoint、Domain Fact 与 Object Payload
- docs/modules/06-agent-core-planning-control.md — § 3. Domain Store 与 LangGraph Checkpoint 一致性

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q201 Final Gate 在输出前检查什么？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+一面+001/正文.md
- primary_domain: agent
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、final
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
  - docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-034
- status: Target

### 面试官问题

Final Gate 在输出前检查什么？

### 他真正想考什么

检验是否能把 final 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

检查目标/Acceptance、Claim、Evidence/Citation、Policy、权限、敏感信息、Tool Effect certainty、Artifact完整性和Publication条件。

### 深挖回答

检查目标/Acceptance、Claim、Evidence/Citation、Policy、权限、敏感信息、Tool Effect certainty、Artifact完整性和Publication条件。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
- docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q202 Final Reflection 与普通 Reflection 有什么区别？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
- primary_domain: agent
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、final
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
  - docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Final Reflection 与普通 Reflection 有什么区别？

### 他真正想考什么

检验是否能把 final 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

普通Reflection修复Step或Plan内问题；Final Reflection在结束前检查全局目标、证据、冲突、风险和未完成项，但不能绕过Final Gate。

### 深挖回答

普通Reflection修复Step或Plan内问题；Final Reflection在结束前检查全局目标、证据、冲突、风险和未完成项，但不能绕过Final Gate。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
- docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q203 RunOutcome 应包含什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
- primary_domain: agent
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、final
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
  - docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

RunOutcome 应包含什么？

### 他真正想考什么

检验是否能把 final 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

包含最终状态、Plan/Step lineage、SelectedEvidence、Artifact、Effect receipts、未决风险、失败/Partial原因和可审计引用。

### 深挖回答

包含最终状态、Plan/Step lineage、SelectedEvidence、Artifact、Effect receipts、未决风险、失败/Partial原因和可审计引用。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
- docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

### Interview Drill Chain 5：Q204–Q212

连续追问从概念进入机制、失败、取舍和证据。

## Q204 Reflexion 如何进入 Memory？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 16. Cross-module Ownership
- primary_domain: agent
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、memory
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 16. Cross-module Ownership
  - docs/modules/05-memory-context.md — § 23. Reflexion 流程
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Reflexion 如何进入 Memory？

### 他真正想考什么

检验是否能把 memory 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Run结束产生ReflexionCandidate或MemoryCandidate，交给Memory Governance；不能直接写Active Memory，也不能改变当前Run事实。

### 深挖回答

Run结束产生ReflexionCandidate或MemoryCandidate，交给Memory Governance；不能直接写Active Memory，也不能改变当前Run事实。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 16. Cross-module Ownership
- docs/modules/05-memory-context.md — § 23. Reflexion 流程

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q205 模型在 Agent Core 中可以决定什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 8. Planner Pipeline
- primary_domain: agent
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、model
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 8. Planner Pipeline
  - docs/modules/06-agent-core-planning-control.md — § 42. ModelCapabilityProfile 与 StepFeasibility
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

模型在 Agent Core 中可以决定什么？

### 他真正想考什么

检验是否能把 model 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

模型可提出Plan、Action、Query、Reflection或Control Proposal；确定性Runtime决定激活、权限、预算、状态迁移、幂等和最终发布。

### 深挖回答

模型可提出Plan、Action、Query、Reflection或Control Proposal；确定性Runtime决定激活、权限、预算、状态迁移、幂等和最终发布。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 8. Planner Pipeline
- docs/modules/06-agent-core-planning-control.md — § 42. ModelCapabilityProfile 与 StepFeasibility

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q206 为什么 Plan 必须包含 AcceptancePolicy？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract
- primary_domain: agent
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、evaluation
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract
  - docs/modules/06-agent-core-planning-control.md — § 35. Failure Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么 Plan 必须包含 AcceptancePolicy？

### 他真正想考什么

检验是否能把 evaluation 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

没有可执行验收就无法区分Observation、完成、需要Repair还是应该Replan，最终也不能通过Final Gate。

### 深挖回答

没有可执行验收就无法区分Observation、完成、需要Repair还是应该Replan，最终也不能通过Final Gate。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract
- docs/modules/06-agent-core-planning-control.md — § 35. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q207 Replan 期间正在运行的副作用分支怎么办？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 9. Replan Barrier
- primary_domain: agent
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、replan
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 9. Replan Barrier
  - docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-06-040
- status: Target

### 面试官问题

Replan 期间正在运行的副作用分支怎么办？

### 他真正想考什么

检验是否能把 replan 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

先按Side Effect Protocol和Fence处理不可中断Effect，阻止旧Plan继续派发，等待确认/对账后再决定新Plan是否可用。

### 深挖回答

先按Side Effect Protocol和Fence处理不可中断Effect，阻止旧Plan继续派发，等待确认/对账后再决定新Plan是否可用。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 9. Replan Barrier
- docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q208 模型升级是否一定要Replan？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan
- primary_domain: agent
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、repair
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan
  - docs/modules/06-agent-core-planning-control.md — § 35. Failure Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

模型升级是否一定要Replan？

### 他真正想考什么

检验是否能把 repair 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

如果只是同一Step允许的Model Escalation且契约不变，可由Step Repair处理；能力、输出契约或计划前提变化才需要Replan。

### 深挖回答

如果只是同一Step允许的Model Escalation且契约不变，可由Step Repair处理；能力、输出契约或计划前提变化才需要Replan。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 14. Retry、Repair、Fallback 与 Replan
- docs/modules/06-agent-core-planning-control.md — § 35. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q209 如何测试 Agent Core 的No-progress保护？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 20. 验证与完成证据
- primary_domain: agent
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、eval
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 20. 验证与完成证据
  - docs/modules/06-agent-core-planning-control.md — § 29. Target 测试矩阵
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

如何测试 Agent Core 的No-progress保护？

### 他真正想考什么

检验是否能把 eval 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

构造重复Action、重复Observation、无增益Reflection、预算耗尽和循环Plan，验证确定性Stop/Fail/Replan与Trace完整性。

### 深挖回答

构造重复Action、重复Observation、无增益Reflection、预算耗尽和循环Plan，验证确定性Stop/Fail/Replan与Trace完整性。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 20. 验证与完成证据
- docs/modules/06-agent-core-planning-control.md — § 29. Target 测试矩阵

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q210 怎样判断一个ControlDecision没有被旧Epoch污染？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 17. Contract Versioning
- primary_domain: agent
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、consistency
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 17. Contract Versioning
  - docs/modules/06-agent-core-planning-control.md — § 45. Graph、State 与长运行版本升级
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

怎样判断一个ControlDecision没有被旧Epoch污染？

### 他真正想考什么

检验是否能把 consistency 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

每个Command、Plan、Step、Branch和Result都校验controller/execution epoch、generation和Version，旧引用只能拒绝或归档。

### 深挖回答

每个Command、Plan、Step、Branch和Result都校验controller/execution epoch、generation和Version，旧引用只能拒绝或归档。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 17. Contract Versioning
- docs/modules/06-agent-core-planning-control.md — § 45. Graph、State 与长运行版本升级

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q211 Agent Core 文档哪些是Current，哪些是Target？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 47. 架构完成与 Program 入口门槛
- primary_domain: agent
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、current
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 47. 架构完成与 Program 入口门槛
  - docs/status/production-readiness.md — § Production Readiness
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Agent Core 文档哪些是Current，哪些是Target？

### 他真正想考什么

检验是否能把 current 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

Single Controller、Plan mandatory、状态/Contract是Target设计事实；implementation、quality和production结论仍需代码、Migration、测试、Trace和Eval。

### 深挖回答

Single Controller、Plan mandatory、状态/Contract是Target设计事实；implementation、quality和production结论仍需代码、Migration、测试、Trace和Eval。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 47. 架构完成与 Program 入口门槛
- docs/status/production-readiness.md — § Production Readiness

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。

## Q212 为什么 Final Gate 不能只看模型自信度？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
- primary_domain: agent
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agent Core、Plan、ReAct、final
- architecture_refs:
  - docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
  - docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么 Final Gate 不能只看模型自信度？

### 他真正想考什么

检验是否能把 final 连接到 Owner、Trigger、State、Failure、Recovery 和 Evidence，而不是只复述名词。

### 30 秒回答

模型自信不能替代Evidence、权限、Effect certainty、Acceptance和Publication Policy；最终发布必须由确定性Gate裁决。

### 深挖回答

模型自信不能替代Evidence、权限、Effect certainty、Acceptance和Publication Policy；最终发布必须由确定性Gate裁决。 模型只能提出 Proposal 或 Candidate；确定性 Runtime 负责 Scope、Version、状态迁移、幂等和审计。本文只表达 Target，不声称 Current 实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出 Proposal，哪个确定性 Gate 裁决？
3. 状态、版本、Scope 或 Generation 如何变化？
4. 失败时为什么选择 Retry、Repair、Replan 或 Reconciliation？
5. 怎样用 Test、Trace 或 Eval 证明？

### Architecture Evidence

- docs/modules/06-agent-core-planning-control.md — § 12. AnswerPolicy、Final Gate 与 Publication
- docs/modules/06-agent-core-planning-control.md — § 40. Final Gate 路由与 RunOutcome Contract

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回 canonical architecture；本 QA 不新增架构事实。
