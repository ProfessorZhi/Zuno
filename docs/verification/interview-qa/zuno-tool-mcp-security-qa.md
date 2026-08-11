# 02 Tool / MCP / Permission / Effect Safety QA

> Architecture Verification Corpus；不是canonical architecture。答案只从08、09及其正式跨模块Contract重生成。

### Interview Drill Chain F：Q066–Q076

连续追问从工具边界进入权限、MCP版本、Effect、恢复和评测。

## Q066 Function Calling 到真实代码执行之间发生了什么？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: tool
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、flow
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
  - docs/project/modules/08-tool-runtime.md — § 46. 固定执行顺序
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-001
- status: Target

### 面试官问题

Function Calling 到真实代码执行之间发生了什么？

### 他真正想考什么

检验是否能把 flow 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

模型只提出带名称和参数的 ActionProposal；Capability Resolution、Prepare、Security Gate、Approval、Idempotency、Adapter Dispatch 和 Observation 才把它变成可治理执行。

### 深挖回答

模型只提出带名称和参数的 ActionProposal；Capability Resolution、Prepare、Security Gate、Approval、Idempotency、Adapter Dispatch 和 Observation 才把它变成可治理执行。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
- docs/project/modules/08-tool-runtime.md — § 46. 固定执行顺序

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q067 Capability、Skill 和 Tool 的边界是什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+B站+面试+001/正文.md
- primary_domain: tool
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、boundary
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 4. Capability、Skill、Tool、API、SDK 和 MCP
  - docs/project/modules/08-tool-runtime.md — § 7. Cross-module Ownership
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-002
- status: Target

### 面试官问题

Capability、Skill 和 Tool 的边界是什么？

### 他真正想考什么

检验是否能把 boundary 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Capability描述系统能做什么，Skill描述如何完成任务，Tool Runtime负责具体外部动作的准备、执行和效果确认；三者不能互相冒充授权。

### 深挖回答

Capability描述系统能做什么，Skill描述如何完成任务，Tool Runtime负责具体外部动作的准备、执行和效果确认；三者不能互相冒充授权。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 4. Capability、Skill、Tool、API、SDK 和 MCP
- docs/project/modules/08-tool-runtime.md — § 7. Cross-module Ownership

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q068 Planner 是如何看见可用 Tool 的？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: tool
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、flow
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
  - docs/project/modules/08-tool-runtime.md — § 46. 固定执行顺序
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Planner 是如何看见可用 Tool 的？

### 他真正想考什么

检验是否能把 flow 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Capability/Skill层通过版本化 Capability Snapshot 和 Conformance 过滤暴露候选；Planner只拿到受限描述，Action-time仍要重新 Prepare 和 Security preflight。

### 深挖回答

Capability/Skill层通过版本化 Capability Snapshot 和 Conformance 过滤暴露候选；Planner只拿到受限描述，Action-time仍要重新 Prepare 和 Security preflight。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
- docs/project/modules/08-tool-runtime.md — § 46. 固定执行顺序

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q069 ToolDefinition、ToolVersion、ToolOperation分别是什么？

- source_type: REAL
- source_ref: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_QA整理.md
- primary_domain: tool
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、version
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 24. ToolDefinition、ToolVersion 与 ToolOperation
  - docs/project/modules/08-tool-runtime.md — § 40. Definition / Version / Installation 生命周期
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

ToolDefinition、ToolVersion、ToolOperation分别是什么？

### 他真正想考什么

检验是否能把 version 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Definition是工具语义，Version固定schema和实现语义，Operation是具体操作；PreparedToolAction必须绑定精确版本和operation。

### 深挖回答

Definition是工具语义，Version固定schema和实现语义，Operation是具体操作；PreparedToolAction必须绑定精确版本和operation。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 24. ToolDefinition、ToolVersion 与 ToolOperation
- docs/project/modules/08-tool-runtime.md — § 40. Definition / Version / Installation 生命周期

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q070 为什么需要 PreparedToolAction？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: tool
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、prepared
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 30. PreparedToolAction
  - docs/project/modules/08-tool-runtime.md — § 53. 两阶段 Security Gate
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-005
- status: Target

### 面试官问题

为什么需要 PreparedToolAction？

### 他真正想考什么

检验是否能把 prepared 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

它把canonical args、TargetResourceSet、ToolVersion、effect profile、deadline和hash冻结，给Security Approval、幂等和审计一个不可变绑定点。

### 深挖回答

它把canonical args、TargetResourceSet、ToolVersion、effect profile、deadline和hash冻结，给Security Approval、幂等和审计一个不可变绑定点。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 30. PreparedToolAction
- docs/project/modules/08-tool-runtime.md — § 53. 两阶段 Security Gate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q071 canonical arguments 为什么重要？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+B站+面试+001/正文.md
- primary_domain: tool
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、prepared
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 30. PreparedToolAction
  - docs/project/modules/08-tool-runtime.md — § 53. 两阶段 Security Gate
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

canonical arguments 为什么重要？

### 他真正想考什么

检验是否能把 prepared 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

同一语义参数必须规范化、稳定序列化并计算hash，否则等价请求可能绕过approval binding或产生重复副作用。

### 深挖回答

同一语义参数必须规范化、稳定序列化并计算hash，否则等价请求可能绕过approval binding或产生重复副作用。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 30. PreparedToolAction
- docs/project/modules/08-tool-runtime.md — § 53. 两阶段 Security Gate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q072 TargetResourceSet 要绑定什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: tool
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、prepared
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 30. PreparedToolAction
  - docs/project/modules/08-tool-runtime.md — § 53. 两阶段 Security Gate
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

TargetResourceSet 要绑定什么？

### 他真正想考什么

检验是否能把 prepared 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

要绑定资源身份、动作、范围、接收者/域名约束和数据分类；Tool不能只凭工具名判断目标。

### 深挖回答

要绑定资源身份、动作、范围、接收者/域名约束和数据分类；Tool不能只凭工具名判断目标。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 30. PreparedToolAction
- docs/project/modules/08-tool-runtime.md — § 53. 两阶段 Security Gate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q073 用户权限是不是全部继承给 Agent？

- source_type: REAL
- source_ref: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_QA整理.md
- primary_domain: tool
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、permission
- architecture_refs:
  - docs/project/modules/09-security.md — § 12. Agent、Task、Session 与用户权限交集
  - docs/project/modules/09-security.md — § 15. Authorization 算法与 Decision Explanation
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-008
- status: Target

### 面试官问题

用户权限是不是全部继承给 Agent？

### 他真正想考什么

检验是否能把 permission 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

不是。User Permission是ceiling，Effective Tool Scope还要交叠AgentVersion、Task Downscope、Installation、Resource Policy和Security Epoch。

### 深挖回答

不是。User Permission是ceiling，Effective Tool Scope还要交叠AgentVersion、Task Downscope、Installation、Resource Policy和Security Epoch。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/09-security.md — § 12. Agent、Task、Session 与用户权限交集
- docs/project/modules/09-security.md — § 15. Authorization 算法与 Decision Explanation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q074 为什么 Effective Permission 取交集？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: tool
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、permission
- architecture_refs:
  - docs/project/modules/09-security.md — § 12. Agent、Task、Session 与用户权限交集
  - docs/project/modules/09-security.md — § 15. Authorization 算法与 Decision Explanation
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么 Effective Permission 取交集？

### 他真正想考什么

检验是否能把 permission 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

交集保证任何下游层都不能扩大上游边界；用户可访问Repo B不代表当前Agent或Task可读写Repo B。

### 深挖回答

交集保证任何下游层都不能扩大上游边界；用户可访问Repo B不代表当前Agent或Task可读写Repo B。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/09-security.md — § 12. Agent、Task、Session 与用户权限交集
- docs/project/modules/09-security.md — § 15. Authorization 算法与 Decision Explanation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q075 AgentVersion Capability Ceiling 解决什么问题？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+B站+面试+001/正文.md
- primary_domain: tool
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、permission
- architecture_refs:
  - docs/project/modules/09-security.md — § 12. Agent、Task、Session 与用户权限交集
  - docs/project/modules/09-security.md — § 15. Authorization 算法与 Decision Explanation
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

AgentVersion Capability Ceiling 解决什么问题？

### 他真正想考什么

检验是否能把 permission 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

它限制某个Agent版本即使由高权限用户运行也只能使用声明的能力和资源范围，防止用户权限自动放大产品行为。

### 深挖回答

它限制某个Agent版本即使由高权限用户运行也只能使用声明的能力和资源范围，防止用户权限自动放大产品行为。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/09-security.md — § 12. Agent、Task、Session 与用户权限交集
- docs/project/modules/09-security.md — § 15. Authorization 算法与 Decision Explanation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q076 Task Downscope 是什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: tool
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、permission
- architecture_refs:
  - docs/project/modules/09-security.md — § 12. Agent、Task、Session 与用户权限交集
  - docs/project/modules/09-security.md — § 15. Authorization 算法与 Decision Explanation
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Task Downscope 是什么？

### 他真正想考什么

检验是否能把 permission 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

它把Agent可用能力进一步缩小到当前Goal、Resource和副作用需要，保证长期能力不变成本次任务的隐式授权。

### 深挖回答

它把Agent可用能力进一步缩小到当前Goal、Resource和副作用需要，保证长期能力不变成本次任务的隐式授权。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/09-security.md — § 12. Agent、Task、Session 与用户权限交集
- docs/project/modules/09-security.md — § 15. Authorization 算法与 Decision Explanation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

### Interview Drill Chain G：Q077–Q087

连续追问从工具边界进入权限、MCP版本、Effect、恢复和评测。

## Q077 Security Epoch 为什么要进入执行链？

- source_type: REAL
- source_ref: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_QA整理.md
- primary_domain: tool
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、permission
- architecture_refs:
  - docs/project/modules/09-security.md — § 12. Agent、Task、Session 与用户权限交集
  - docs/project/modules/09-security.md — § 15. Authorization 算法与 Decision Explanation
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-012
- status: Target

### 面试官问题

Security Epoch 为什么要进入执行链？

### 他真正想考什么

检验是否能把 permission 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Epoch是撤销和策略变更的版本事实；执行前必须检查最新Epoch，变化会使旧Decision/Approval失效并要求重新授权。

### 深挖回答

Epoch是撤销和策略变更的版本事实；执行前必须检查最新Epoch，变化会使旧Decision/Approval失效并要求重新授权。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/09-security.md — § 12. Agent、Task、Session 与用户权限交集
- docs/project/modules/09-security.md — § 15. Authorization 算法与 Decision Explanation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q078 Approval 需要绑定哪些事实？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: tool
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、approval
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
  - docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-013
- status: Target

### 面试官问题

Approval 需要绑定哪些事实？

### 他真正想考什么

检验是否能把 approval 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

至少绑定principal、scope、PreparedToolAction hash、canonical args、TargetResourceSet、risk/effect profile、PolicyVersion、Epoch、expiry和replay rule。

### 深挖回答

至少绑定principal、scope、PreparedToolAction hash、canonical args、TargetResourceSet、risk/effect profile、PolicyVersion、Epoch、expiry和replay rule。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
- docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q079 为什么 Approval 不能只绑定 tool name？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+B站+面试+001/正文.md
- primary_domain: tool
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、approval
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
  - docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么 Approval 不能只绑定 tool name？

### 他真正想考什么

检验是否能把 approval 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

同名Tool可能换schema、参数、收件人、资源或effect profile；只绑定名称会允许把旧批准复用到新副作用。

### 深挖回答

同名Tool可能换schema、参数、收件人、资源或effect profile；只绑定名称会允许把旧批准复用到新副作用。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
- docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q080 Approval replay 怎么防？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: tool
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、approval
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
  - docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Approval replay 怎么防？

### 他真正想考什么

检验是否能把 approval 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

使用single-use或明确复用策略、expiry、approval id、action hash和持久化状态；重复消费必须确定性拒绝并留下审计。

### 深挖回答

使用single-use或明确复用策略、expiry、approval id、action hash和持久化状态；重复消费必须确定性拒绝并留下审计。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
- docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q081 审批等待期间权限被撤销怎么办？

- source_type: REAL
- source_ref: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_QA整理.md
- primary_domain: tool
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、approval
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
  - docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-016
- status: Target

### 面试官问题

审批等待期间权限被撤销怎么办？

### 他真正想考什么

检验是否能把 approval 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Security Epoch变化使Pending Approval失效，Tool Runtime重新Prepare/Authorize；不能因为用户之前点过确认就继续Dispatch。

### 深挖回答

Security Epoch变化使Pending Approval失效，Tool Runtime重新Prepare/Authorize；不能因为用户之前点过确认就继续Dispatch。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
- docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q082 金融系统不能让 Agent 自己真实操作，怎么设计？

- source_type: REAL
- source_ref: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: tool
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、high-risk
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
  - docs/project/modules/08-tool-runtime.md — § 46. 固定执行顺序
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-017
- status: Target

### 面试官问题

金融系统不能让 Agent 自己真实操作，怎么设计？

### 他真正想考什么

检验是否能把 high-risk 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Agent只能提出Action或Simulation/Dry-run结果；真实Effect必须经过Prepare、授权、Approval、审计、幂等和受限Adapter执行，必要时转Human Required。

### 深挖回答

Agent只能提出Action或Simulation/Dry-run结果；真实Effect必须经过Prepare、授权、Approval、审计、幂等和受限Adapter执行，必要时转Human Required。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
- docs/project/modules/08-tool-runtime.md — § 46. 固定执行顺序

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q083 Dry-run 和真实执行的边界是什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+B站+面试+001/正文.md
- primary_domain: tool
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、high-risk
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
  - docs/project/modules/08-tool-runtime.md — § 46. 固定执行顺序
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Dry-run 和真实执行的边界是什么？

### 他真正想考什么

检验是否能把 high-risk 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Dry-run只能返回计划、权限和可能影响的预览，不产生外部Effect；切换真实执行必须创建新的PreparedAction并重新过Gate。

### 深挖回答

Dry-run只能返回计划、权限和可能影响的预览，不产生外部Effect；切换真实执行必须创建新的PreparedAction并重新过Gate。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
- docs/project/modules/08-tool-runtime.md — § 46. 固定执行顺序

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q084 MCP 和 Function Calling 有什么区别？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: tool
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、mcp
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
  - docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-019
- status: Target

### 面试官问题

MCP 和 Function Calling 有什么区别？

### 他真正想考什么

检验是否能把 mcp 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Function Calling是模型输出Tool Proposal的接口形态；MCP是Provider/Server发现和调用能力的协议，Zuno仍用自己的Capability、Security和Tool Runtime治理。

### 深挖回答

Function Calling是模型输出Tool Proposal的接口形态；MCP是Provider/Server发现和调用能力的协议，Zuno仍用自己的Capability、Security和Tool Runtime治理。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
- docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q085 MCP Tool 和本地 Tool 的执行Owner相同吗？

- source_type: REAL
- source_ref: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_QA整理.md
- primary_domain: tool
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、mcp
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
  - docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

MCP Tool 和本地 Tool 的执行Owner相同吗？

### 他真正想考什么

检验是否能把 mcp 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

都必须进入唯一ToolInvocationGateway；MCP只是Adapter/协议来源，执行事实仍归08，Approval和OAuth安全归09。

### 深挖回答

都必须进入唯一ToolInvocationGateway；MCP只是Adapter/协议来源，执行事实仍归08，Approval和OAuth安全归09。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
- docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q086 MCP Protocol Version、Server Version、Capability Snapshot、Zuno ToolVersion如何区分？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: tool
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、mcp
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
  - docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-021
- status: Target

### 面试官问题

MCP Protocol Version、Server Version、Capability Snapshot、Zuno ToolVersion如何区分？

### 他真正想考什么

检验是否能把 mcp 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

协议版本决定握手语义，Server Version是实现发布，Capability Snapshot是tools/list时刻的能力事实，Zuno ToolVersion是内部绑定的可执行契约。

### 深挖回答

协议版本决定握手语义，Server Version是实现发布，Capability Snapshot是tools/list时刻的能力事实，Zuno ToolVersion是内部绑定的可执行契约。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
- docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q087 tools/list 的结果应该怎样进入 Agent？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+B站+面试+001/正文.md
- primary_domain: tool
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、mcp
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
  - docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

tools/list 的结果应该怎样进入 Agent？

### 他真正想考什么

检验是否能把 mcp 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

先形成不可变McpCapabilitySnapshot，保存schema、annotations、hash和来源，再生成McpToolBinding；不能实时把裸列表直接喂给模型执行。

### 深挖回答

先形成不可变McpCapabilitySnapshot，保存schema、annotations、hash和来源，再生成McpToolBinding；不能实时把裸列表直接喂给模型执行。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
- docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

### Interview Drill Chain H：Q088–Q098

连续追问从工具边界进入权限、MCP版本、Effect、恢复和评测。

## Q088 list_changed 到来后发生什么？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: tool
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、mcp
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
  - docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-023
- status: Target

### 面试官问题

list_changed 到来后发生什么？

### 他真正想考什么

检验是否能把 mcp 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

刷新Capability Snapshot；尚未Dispatch的旧PreparedAction和Approval变为OBSOLETE/INVALID，必须重新Prepare、授权和审批。

### 深挖回答

刷新Capability Snapshot；尚未Dispatch的旧PreparedAction和Approval变为OBSOLETE/INVALID，必须重新Prepare、授权和审批。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
- docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q089 MCP schema 在审批后、Dispatch前改变怎么办？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_QA整理.md
- primary_domain: tool
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、mcp
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
  - docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

MCP schema 在审批后、Dispatch前改变怎么办？

### 他真正想考什么

检验是否能把 mcp 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

旧Action的schema hash与Snapshot不再匹配，确定性Reject；重新解析参数、计算Scope、Prepare和Approval。

### 深挖回答

旧Action的schema hash与Snapshot不再匹配，确定性Reject；重新解析参数、计算Scope、Prepare和Approval。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
- docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q090 MCP schema 在已经Dispatch后改变怎么办？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: tool
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、mcp
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
  - docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

MCP schema 在已经Dispatch后改变怎么办？

### 他真正想考什么

检验是否能把 mcp 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

不能回溯改变已发生的Attempt；若Provider结果未知进入EffectReconciliation，后续新调用使用新Snapshot，不能blind retry。

### 深挖回答

不能回溯改变已发生的Attempt；若Provider结果未知进入EffectReconciliation，后续新调用使用新Snapshot，不能blind retry。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
- docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q091 Tool 被删除或改名怎么办？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+B站+面试+001/正文.md
- primary_domain: tool
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、mcp
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
  - docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Tool 被删除或改名怎么办？

### 他真正想考什么

检验是否能把 mcp 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

旧Binding只能进入不可执行/Obsolete状态，不能按名称猜测替代；Capability Resolution必须给出新的明确版本或报告不可用。

### 深挖回答

旧Binding只能进入不可执行/Obsolete状态，不能按名称猜测替代；Capability Resolution必须给出新的明确版本或报告不可用。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
- docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q092 Zuno 能否 rollback 外部 MCP Server？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: tool
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、mcp
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
  - docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Zuno 能否 rollback 外部 MCP Server？

### 他真正想考什么

检验是否能把 mcp 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

如果Zuno不拥有Provider部署，就只能停止使用旧Binding、选择兼容Snapshot或请求Owner回滚；不能声称自己执行了外部部署回滚。

### 深挖回答

如果Zuno不拥有Provider部署，就只能停止使用旧Binding、选择兼容Snapshot或请求Owner回滚；不能声称自己执行了外部部署回滚。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 16. MCP Tool
- docs/project/modules/08-tool-runtime.md — § 38. MCP 领域对象

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q093 Dispatch前 timeout 和 Dispatch后 timeout 有何不同？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_QA整理.md
- primary_domain: tool
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、effect
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
  - docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-028
- status: Target

### 面试官问题

Dispatch前 timeout 和 Dispatch后 timeout 有何不同？

### 他真正想考什么

检验是否能把 effect 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Dispatch前可确定未发送并按规则Retry；Dispatch后可能已产生Effect，必须区分CONFIRMED_NOT_EXECUTED与UNKNOWN并走Reconciliation。

### 深挖回答

Dispatch前可确定未发送并按规则Retry；Dispatch后可能已产生Effect，必须区分CONFIRMED_NOT_EXECUTED与UNKNOWN并走Reconciliation。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
- docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q094 Provider返回2xx是否等于Effect成功？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: tool
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、effect
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
  - docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Provider返回2xx是否等于Effect成功？

### 他真正想考什么

检验是否能把 effect 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

不等于。HTTP/Provider receipt只是Adapter观察，必须由EffectReceipt证明业务效果；未知或部分结果不能自动标成功。

### 深挖回答

不等于。HTTP/Provider receipt只是Adapter观察，必须由EffectReceipt证明业务效果；未知或部分结果不能自动标成功。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
- docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q095 Effect UNKNOWN 为什么禁止盲目Retry？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+B站+面试+001/正文.md
- primary_domain: tool
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、effect
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
  - docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-030
- status: Target

### 面试官问题

Effect UNKNOWN 为什么禁止盲目Retry？

### 他真正想考什么

检验是否能把 effect 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

超时可能发生在Provider已提交之后，盲Retry会重复副作用；先用业务键、查询、回调、人工核实或Reconciliation确认。

### 深挖回答

超时可能发生在Provider已提交之后，盲Retry会重复副作用；先用业务键、查询、回调、人工核实或Reconciliation确认。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
- docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q096 Idempotency Key 防什么？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: tool
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、idempotency
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 47. 幂等和 Effect Assurance
  - docs/project/modules/11-infrastructure.md — § 44. 一致性与幂等原则
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Idempotency Key 防什么？

### 他真正想考什么

检验是否能把 idempotency 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

它把同一业务意图与Attempt绑定，配合Claim、Lease和Provider业务键减少重复Effect，但不承诺所有外部系统通用Exactly Once。

### 深挖回答

它把同一业务意图与Attempt绑定，配合Claim、Lease和Provider业务键减少重复Effect，但不承诺所有外部系统通用Exactly Once。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 47. 幂等和 Effect Assurance
- docs/project/modules/11-infrastructure.md — § 44. 一致性与幂等原则

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q097 重复请求与同意重试如何区分？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_QA整理.md
- primary_domain: tool
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、idempotency
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 47. 幂等和 Effect Assurance
  - docs/project/modules/11-infrastructure.md — § 44. 一致性与幂等原则
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

重复请求与同意重试如何区分？

### 他真正想考什么

检验是否能把 idempotency 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

同一canonical action和业务意图可由幂等状态识别；参数、收件人、ToolVersion或Effect profile改变就是新Action，不能复用旧Claim。

### 深挖回答

同一canonical action和业务意图可由幂等状态识别；参数、收件人、ToolVersion或Effect profile改变就是新Action，不能复用旧Claim。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 47. 幂等和 Effect Assurance
- docs/project/modules/11-infrastructure.md — § 44. 一致性与幂等原则

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q098 EffectReceipt 记录什么？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: tool
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、effect
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
  - docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

EffectReceipt 记录什么？

### 他真正想考什么

检验是否能把 effect 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

它记录已确认的Effect item、provider receipt、业务键、资源影响和证据；若事实无法确认则记录EffectReconciliation，而非伪造成功。

### 深挖回答

它记录已确认的Effect item、provider receipt、业务键、资源影响和证据；若事实无法确认则记录EffectReconciliation，而非伪造成功。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
- docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

### Interview Drill Chain I：Q099–Q109

连续追问从工具边界进入权限、MCP版本、Effect、恢复和评测。

## Q099 EffectReconciliation 的状态目标是什么？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+B站+面试+001/正文.md
- primary_domain: tool
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、effect
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
  - docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

EffectReconciliation 的状态目标是什么？

### 他真正想考什么

检验是否能把 effect 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

把UNKNOWN收敛为CONFIRMED_SUCCESS、CONFIRMED_FAILURE、CONFIRMED_NOT_EXECUTED或HUMAN_REQUIRED，并保留原Attempt和查询证据。

### 深挖回答

把UNKNOWN收敛为CONFIRMED_SUCCESS、CONFIRMED_FAILURE、CONFIRMED_NOT_EXECUTED或HUMAN_REQUIRED，并保留原Attempt和查询证据。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
- docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q100 Compensation 是 rollback 吗？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: tool
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、effect
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
  - docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Compensation 是 rollback 吗？

### 他真正想考什么

检验是否能把 effect 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Compensation是新的ActionProposal和受治理副作用，不是自动回滚承诺；不可补偿Effect必须明确标记并升级人工处理。

### 深挖回答

Compensation是新的ActionProposal和受治理副作用，不是自动回滚承诺；不可补偿Effect必须明确标记并升级人工处理。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
- docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q101 Cancellation 遇到不可中断副作用怎么办？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_QA整理.md
- primary_domain: tool
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、effect
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
  - docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Cancellation 遇到不可中断副作用怎么办？

### 他真正想考什么

检验是否能把 effect 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

取消控制状态可以停止未Dispatch动作；已经发出的不可中断Effect仍要等待确认/对账，不能把Cancellation伪装成Not Executed。

### 深挖回答

取消控制状态可以停止未Dispatch动作；已经发出的不可中断Effect仍要等待确认/对账，不能把Cancellation伪装成Not Executed。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 20. UNKNOWN Effect 与 Reconciliation
- docs/project/modules/08-tool-runtime.md — § 36. EffectReconciliation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q102 SecretLease 为什么不是把token放进Prompt？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/Agent开发/Agent开发+B站+二面+002/正文.md
- primary_domain: tool
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、secret
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 55. Secret 与 Credential
  - docs/project/modules/09-security.md — § 31. Secret 与 Credential Lease
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-08-037
- status: Target

### 面试官问题

SecretLease 为什么不是把token放进Prompt？

### 他真正想考什么

检验是否能把 secret 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Secret由受控Lease按Tool和Scope短期注入Adapter/Sandbox，模型只看到引用或脱敏结果，避免明文进入Context、Trace或Memory。

### 深挖回答

Secret由受控Lease按Tool和Scope短期注入Adapter/Sandbox，模型只看到引用或脱敏结果，避免明文进入Context、Trace或Memory。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 55. Secret 与 Credential
- docs/project/modules/09-security.md — § 31. Secret 与 Credential Lease

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q103 Tool Output 是可信指令吗？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+B站+面试+001/正文.md
- primary_domain: tool
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、security
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
  - docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Tool Output 是可信指令吗？

### 他真正想考什么

检验是否能把 security 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

不是。Tool Output、Error和MCP返回都视为不可信Data，经过Schema、Prompt Injection、Classification和Redaction Gate后才能进入模型、Knowledge、Memory或Sink。

### 深挖回答

不是。Tool Output、Error和MCP返回都视为不可信Data，经过Schema、Prompt Injection、Classification和Redaction Gate后才能进入模型、Knowledge、Memory或Sink。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
- docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q104 危险SQL如何禁止？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+中厂+面试+001/正文.md
- primary_domain: tool
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、security
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
  - docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

危险SQL如何禁止？

### 他真正想考什么

检验是否能把 security 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

通过ToolDefinition/Operation的只读或副作用分类、参数化Schema、TargetResourceSet、Policy/Approval和Sandbox；模型文本不能绕过确定性执行边界。

### 深挖回答

通过ToolDefinition/Operation的只读或副作用分类、参数化Schema、TargetResourceSet、Policy/Approval和Sandbox；模型文本不能绕过确定性执行边界。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
- docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q105 Sandbox 与 Network Egress 谁决定？

- source_type: DERIVED
- source_ref: derived-from: internship-work/interview/04_丰疆智能_架构培训生(AI工程师)/01_面试_QA整理.md
- primary_domain: tool
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、security
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
  - docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Sandbox 与 Network Egress 谁决定？

### 他真正想考什么

检验是否能把 security 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Tool Runtime提供执行隔离，Security提供Resource/Network Policy和PEP；Adapter不能自行扩大文件、网络或凭据范围。

### 深挖回答

Tool Runtime提供执行隔离，Security提供Resource/Network Policy和PEP；Adapter不能自行扩大文件、网络或凭据范围。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
- docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q106 SSRF如何纳入Tool安全？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
- primary_domain: tool
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、security
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
  - docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

SSRF如何纳入Tool安全？

### 他真正想考什么

检验是否能把 security 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

URL/目标资源先被规范化并由Resource/Network Policy校验，禁止把模型或不可信Tool Output直接当作任意内网目标。

### 深挖回答

URL/目标资源先被规范化并由Resource/Network Policy校验，禁止把模型或不可信Tool Output直接当作任意内网目标。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
- docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q107 Tool Output 写入Memory前要经过什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
- primary_domain: tool
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、security
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
  - docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Tool Output 写入Memory前要经过什么？

### 他真正想考什么

检验是否能把 security 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

先做可信度、敏感性、归属、冲突和MemoryCandidate治理；Tool结果不能直接成为Active Memory。

### 深挖回答

先做可信度、敏感性、归属、冲突和MemoryCandidate治理；Tool结果不能直接成为Active Memory。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
- docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q108 Tool Output 作为Knowledge Evidence有什么限制？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
- primary_domain: tool
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、security
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
  - docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Tool Output 作为Knowledge Evidence有什么限制？

### 他真正想考什么

检验是否能把 security 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

必须作为不可信来源经过独立Evidence Acceptance、SourceSpan/lineage和Security Scope验证，不能凭Tool返回自动成为权威知识。

### 深挖回答

必须作为不可信来源经过独立Evidence Acceptance、SourceSpan/lineage和Security Scope验证，不能凭Tool返回自动成为权威知识。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 57. Tool Input 和 Output Firewall
- docs/project/modules/09-security.md — § 21. Prompt Injection 与 Memory Poisoning 防御

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q109 并发Tool调用什么时候不允许？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 22. 并行与资源冲突
- primary_domain: tool
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、concurrency
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 22. 并行与资源冲突
  - docs/project/modules/09-security.md — § 51. 时间、并发与 TOCTOU
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

并发Tool调用什么时候不允许？

### 他真正想考什么

检验是否能把 concurrency 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

如果共享写资源、排他资源、side-effect policy、Capacity、Security或Approval不允许并行，就必须串行或等待ResourceClaim。

### 深挖回答

如果共享写资源、排他资源、side-effect policy、Capacity、Security或Approval不允许并行，就必须串行或等待ResourceClaim。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 22. 并行与资源冲突
- docs/project/modules/09-security.md — § 51. 时间、并发与 TOCTOU

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

### Interview Drill Chain J：Q110–Q120

连续追问从工具边界进入权限、MCP版本、Effect、恢复和评测。

## Q110 两个Tool写同一个资源如何处理？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 22. 并行与资源冲突
- primary_domain: tool
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、concurrency
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 22. 并行与资源冲突
  - docs/project/modules/09-security.md — § 51. 时间、并发与 TOCTOU
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

两个Tool写同一个资源如何处理？

### 他真正想考什么

检验是否能把 concurrency 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

通过TargetResourceSet、ResourceClaim、generation/fencing和Idempotency判断冲突；不能只依赖模型规划顺序。

### 深挖回答

通过TargetResourceSet、ResourceClaim、generation/fencing和Idempotency判断冲突；不能只依赖模型规划顺序。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 22. 并行与资源冲突
- docs/project/modules/09-security.md — § 51. 时间、并发与 TOCTOU

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q111 Dispatch进程Crash后如何恢复？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 51. Crash Cut Points
- primary_domain: tool
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、recovery
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 51. Crash Cut Points
  - docs/project/modules/08-tool-runtime.md — § 48. Retry、Reconciliation 与 Replan
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Dispatch进程Crash后如何恢复？

### 他真正想考什么

检验是否能把 recovery 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

先根据 durable Dispatch、Attempt、Idempotency和Provider查询确定发送事实；控制重放不等于重新产生外部Effect。

### 深挖回答

先根据 durable Dispatch、Attempt、Idempotency和Provider查询确定发送事实；控制重放不等于重新产生外部Effect。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 51. Crash Cut Points
- docs/project/modules/08-tool-runtime.md — § 48. Retry、Reconciliation 与 Replan

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q112 AuditPersistenceReceipt、AuditEvent和Effect成功有什么区别？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 58. Mandatory Audit
- primary_domain: tool
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、audit
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 58. Mandatory Audit
  - docs/project/modules/09-security.md — § 44. Audit、Trace 与 Evidence
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

AuditPersistenceReceipt、AuditEvent和Effect成功有什么区别？

### 他真正想考什么

检验是否能把 audit 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

Receipt证明安全审计已耐久化，AuditEvent是可查询事实，EffectReceipt证明外部效果；三者不能互相替代。

### 深挖回答

Receipt证明安全审计已耐久化，AuditEvent是可查询事实，EffectReceipt证明外部效果；三者不能互相替代。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 58. Mandatory Audit
- docs/project/modules/09-security.md — § 44. Audit、Trace 与 Evidence

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q113 如何评测Tool成功率而不把2xx当成功？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 63. Observability 与 SLO
- primary_domain: tool
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、eval
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 63. Observability 与 SLO
  - docs/project/modules/09-security.md — § 61. Security Eval 与 Release Gate
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

如何评测Tool成功率而不把2xx当成功？

### 他真正想考什么

检验是否能把 eval 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

按Prepare、Authorization、Approval、Attempt、Observation、Effect certainty、Reconciliation和Human Required分别计数，并用故障注入覆盖未知效果。

### 深挖回答

按Prepare、Authorization、Approval、Attempt、Observation、Effect certainty、Reconciliation和Human Required分别计数，并用故障注入覆盖未知效果。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 63. Observability 与 SLO
- docs/project/modules/09-security.md — § 61. Security Eval 与 Release Gate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q114 只读Tool是否需要Approval？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
- primary_domain: tool
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、approval
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
  - docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

只读Tool是否需要Approval？

### 他真正想考什么

检验是否能把 approval 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

是否需要由Risk/Effect Policy决定；只读不等于无安全边界，仍须Scope、Secret、Network、Output治理和Audit。

### 深挖回答

是否需要由Risk/Effect Policy决定；只读不等于无安全边界，仍须Scope、Secret、Network、Output治理和Audit。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
- docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q115 Tool、API和MCP Adapter为什么不能各自执行？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
- primary_domain: tool
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、flow
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
  - docs/project/modules/08-tool-runtime.md — § 46. 固定执行顺序
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Tool、API和MCP Adapter为什么不能各自执行？

### 他真正想考什么

检验是否能把 flow 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

多个入口会产生绕过Security、幂等和审计的旁路；所有外部效果必须汇入唯一ToolInvocationGateway。

### 深挖回答

多个入口会产生绕过Security、幂等和审计的旁路；所有外部效果必须汇入唯一ToolInvocationGateway。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 9. 唯一 Tool Invocation Boundary
- docs/project/modules/08-tool-runtime.md — § 46. 固定执行顺序

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q116 Tool Execution Failure Namespace有什么价值？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 49. Failure Namespace
- primary_domain: tool
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、failure
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 49. Failure Namespace
  - docs/project/modules/08-tool-runtime.md — § 48. Retry、Reconciliation 与 Replan
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Tool Execution Failure Namespace有什么价值？

### 他真正想考什么

检验是否能把 failure 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

把准备、授权、Approval、Adapter、Timeout、Effect和Reconciliation失败分层，支持正确选择Retry、Repair、Replan或人工升级。

### 深挖回答

把准备、授权、Approval、Adapter、Timeout、Effect和Reconciliation失败分层，支持正确选择Retry、Repair、Replan或人工升级。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 49. Failure Namespace
- docs/project/modules/08-tool-runtime.md — § 48. Retry、Reconciliation 与 Replan

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q117 高并发下Tool Runtime如何保护Provider？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 22. 并行与资源冲突
- primary_domain: tool
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、concurrency
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 22. 并行与资源冲突
  - docs/project/modules/09-security.md — § 51. 时间、并发与 TOCTOU
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

高并发下Tool Runtime如何保护Provider？

### 他真正想考什么

检验是否能把 concurrency 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

通过Capacity、Quota、Lease、Admission、Deadline、ResourceClaim和受控并行；不把无限并发交给模型。

### 深挖回答

通过Capacity、Quota、Lease、Admission、Deadline、ResourceClaim和受控并行；不把无限并发交给模型。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 22. 并行与资源冲突
- docs/project/modules/09-security.md — § 51. 时间、并发与 TOCTOU

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q118 多Approver场景如何防止权限放大？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
- primary_domain: tool
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、approval
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
  - docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

多Approver场景如何防止权限放大？

### 他真正想考什么

检验是否能把 approval 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

每个Approval都绑定同一PreparedAction、Policy、Scope和Epoch，并由Policy规定门槛、顺序、expiry和single-use；多签不能改变Action事实。

### 深挖回答

每个Approval都绑定同一PreparedAction、Policy、Scope和Epoch，并由Policy规定门槛、顺序、expiry和single-use；多签不能改变Action事实。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
- docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q119 Tool Version变化是否必然触发Agent Replan？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 24. ToolDefinition、ToolVersion 与 ToolOperation
- primary_domain: tool
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、version
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 24. ToolDefinition、ToolVersion 与 ToolOperation
  - docs/project/modules/08-tool-runtime.md — § 40. Definition / Version / Installation 生命周期
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Tool Version变化是否必然触发Agent Replan？

### 他真正想考什么

检验是否能把 version 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

先由Tool Runtime/Security重新Prepare和Authorize；只有能力、计划步骤或任务前提变化时，才由Agent Core决定Replan。

### 深挖回答

先由Tool Runtime/Security重新Prepare和Authorize；只有能力、计划步骤或任务前提变化时，才由Agent Core决定Replan。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 24. ToolDefinition、ToolVersion 与 ToolOperation
- docs/project/modules/08-tool-runtime.md — § 40. Definition / Version / Installation 生命周期

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q120 如何证明Tool安全边界有效？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 63. Observability 与 SLO
- primary_domain: tool
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、eval
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 63. Observability 与 SLO
  - docs/project/modules/09-security.md — § 61. Security Eval 与 Release Gate
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

如何证明Tool安全边界有效？

### 他真正想考什么

检验是否能把 eval 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

用Contract、fault/E2E和Security Eval测试schema变化、replay、epoch撤销、prompt injection、sandbox、unknown effect、审计背压和恢复。

### 深挖回答

用Contract、fault/E2E和Security Eval测试schema变化、replay、epoch撤销、prompt injection、sandbox、unknown effect、审计背压和恢复。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 63. Observability 与 SLO
- docs/project/modules/09-security.md — § 61. Security Eval 与 Release Gate

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

### Interview Drill Chain K：Q121–Q123

连续追问从工具边界进入权限、MCP版本、Effect、恢复和评测。

## Q121 哪些Tool事实是Current，哪些只是Target？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 68. Current 证据
- primary_domain: tool
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、current
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 68. Current 证据
  - docs/project/modules/08-tool-runtime.md — § 75. 完成证据
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

哪些Tool事实是Current，哪些只是Target？

### 他真正想考什么

检验是否能把 current 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

PreparedAction、MCP Snapshot、Effect/Reconciliation等在文档中是Target Contract；Current必须由代码、测试、Trace/Eval和运行证据证明，不能凭类名宣称完成。

### 深挖回答

PreparedAction、MCP Snapshot、Effect/Reconciliation等在文档中是Target Contract；Current必须由代码、测试、Trace/Eval和运行证据证明，不能凭类名宣称完成。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 68. Current 证据
- docs/project/modules/08-tool-runtime.md — § 75. 完成证据

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q122 Tool Runtime 与 Security 的唯一边界是什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 4. Capability、Skill、Tool、API、SDK 和 MCP
- primary_domain: tool
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、boundary
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 4. Capability、Skill、Tool、API、SDK 和 MCP
  - docs/project/modules/08-tool-runtime.md — § 7. Cross-module Ownership
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Tool Runtime 与 Security 的唯一边界是什么？

### 他真正想考什么

检验是否能把 boundary 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

08拥有准备、Attempt、Observation和Effect事实；09拥有Authorization、Approval、Epoch和Information Flow事实；双方通过不可变Contract协作。

### 深挖回答

08拥有准备、Attempt、Observation和Effect事实；09拥有Authorization、Approval、Epoch和Information Flow事实；双方通过不可变Contract协作。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 4. Capability、Skill、Tool、API、SDK 和 MCP
- docs/project/modules/08-tool-runtime.md — § 7. Cross-module Ownership

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q123 用户批准后收件人改变还能执行吗？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
- primary_domain: tool
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Tool Runtime、MCP、Permission、Effect、approval
- architecture_refs:
  - docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
  - docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

用户批准后收件人改变还能执行吗？

### 他真正想考什么

检验是否能把 approval 连接到外部Effect的完整生命周期，而不是停留在Function Calling名词。

### 30 秒回答

不能。收件人属于canonical args和TargetResourceSet，hash变化使旧PreparedAction/Approval失效，必须重新授权。

### 深挖回答

不能。收件人属于canonical args和TargetResourceSet，hash变化使旧PreparedAction/Approval失效，必须重新授权。 08拥有执行事实，09拥有授权事实，11提供事务、Lease、Inbox/Outbox等原语；模型不能直接执行、批准或确认Effect。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、Version、Epoch或幂等事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Fault/E2E/Eval证明？

### Architecture Evidence

- docs/project/modules/08-tool-runtime.md — § 12. 需要审批的副作用
- docs/project/modules/09-security.md — § 29. PreparedToolAction 与 Approval

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。
