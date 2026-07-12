# 06 Agent Core / Planning & Control

updated: 2026-07-12  
status: normative-target-module-design  
module_number: 06  
formal_path: `docs/modules/06-agent-core-planning-control.md`  
agent_mirror: `.agent/modules/06-agent-core-planning-control.md`

> 本文是 Zuno 第 06 个逻辑模块——Agent Core / Planning & Control——的正式模块架构设计。
>
> 文档首先说明 Agent Core 为什么存在、五种 Agent 机制如何组合、LangGraph 如何执行动态并行 Plan、Reflection 在什么时机发生，以及不同模型角色如何独立配置；代码结构、PostgreSQL 表和 Alembic Migration 位于后半部分实施规格。
>
> 本文描述 **Target**，不是 Current。当前完成度、Gap、Blocked 和 Measurement 以 `docs/status/production-readiness.md` 为事实源。

---

# Part I：概念架构

# 1. Agent Core 解决什么问题

企业级 Agent 不是“让一个模型不断调用工具，直到它自己说完成”。这种单循环方式在任务变复杂后会出现一系列问题：

```text
任务没有稳定的目标分解
执行顺序只存在于模型上下文里
无法可靠判断哪些工作能够并行
失败后不知道应该重试动作还是修改计划
模型声称完成，但系统无法证明结果合格
进程重启后无法恢复到准确位置
多个并行分支会竞争状态或覆盖结果
模型、检索、工具和审批之间缺少统一治理
每个步骤都使用强模型，成本失控
所有步骤都使用弱模型，关键推理质量不足
```

Agent Core 的作用，是在模型能力之外增加一层**显式、可持久化、可恢复的任务控制系统**：

```text
用户目标
  ↓
任务分析与策略选择
  ↓
Plan DAG
  ↓
最大安全并行调度
  ↓
Step 内 ReAct 执行
  ↓
Acceptance / Reflection
  ↓
继续、重试、等待、Replan 或终止
  ↓
最终综合与 AnswerPolicy
  ↓
RunOutcome
  ↓
Reflexion Candidate
```

一句话定义：

> Agent Core 是领域无关的 Single Controller Runtime，使用 LangGraph 承载控制流，使用 Plan DAG 表达任务结构，通过 Scheduler、ReAct、Reflection、Replan 和 Reflexion 协调 Model、Knowledge、Memory、Capability、Tool、Input 与 Security。

它面向：

```text
企业知识库问答
复杂研究与报告
多文档分析
代码理解、修改、测试与修复
数据分析和 Artifact 生成
外部工具与企业流程
需要审批、等待和恢复的长任务
```

它不绑定合同分析或任何单一场景。领域差异由 Skill、Capability、Knowledge 和 Tool 模块提供。

---

# 2. 模块边界

## 2.1 Agent Core 负责

```text
Runtime Request 校验
ExecutionContextSnapshot
Task Analysis
Complexity Classification
RuntimePolicy / AnswerPolicy 解析
Plan DAG 创建、验证、激活与版本化
Ready Step 判定与默认最大化安全并行
Step 内 ReAct 控制循环
Action 校验与分发
Observation 归一化
Acceptance Evaluation
Action / Step / Join / Final 质量判断
PlanPatch / Replan
Interrupt / Resume
Cancellation / Deadline
RunOutcome
Reflexion Candidate Bridge
RuntimeEvent / Trace 关联
```

## 2.2 Agent Core 不负责

```text
直接解析 PDF、DOCX、PPTX、XLSX 或图片
直接操作 Milvus、Neo4j 或 BM25
直接调用具体模型厂商 SDK
直接执行 Shell、浏览器、邮件或第三方 API
直接写入长期 Memory
直接决定用户是否有权访问某份知识
直接实现领域业务规则
直接保存大型文件、完整日志或完整检索 Payload
```

## 2.3 跨模块关系

```text
Agent Core
├── Model Gateway
├── Memory & Context
├── Knowledge / Agentic GraphRAG
├── Input / Document Ingestion
├── Capability / Skill
├── Tool Runtime
├── Security
├── Artifact Store
└── Observability & Eval
```

Agent Core 只通过 typed Port 与这些模块通信，不导入它们的内部实现。

---

# 3. 五种 Agent 理念如何融合

Zuno 不把 Plan-and-Execute、ReAct、Reflection、Replan 和 Reflexion 设计成五个互斥的 Strategy，也不为每个概念创建一个独立产品 Agent。

它们是同一个 Runtime 中不同时间尺度、不同职责层级的机制：

```text
Plan-and-Execute
    时间尺度：整个任务
    负责：目标分解、依赖、并行关系、输入输出和完成条件

ReAct
    时间尺度：单个 Step 内的若干 Action
    负责：根据最新 Observation 决定下一步具体动作

Reflection
    时间尺度：Action、Step、并行 Join、最终输出
    负责：判断是否合格，以及下一步控制决策

Replan
    时间尺度：任务执行过程中
    负责：当原计划假设失效时修改剩余计划

Reflexion
    时间尺度：任务结束之后、跨任务
    负责：形成可复用经验候选，交给 Memory Governance
```

嵌套关系：

```text
AgentRun
└── Plan-and-Execute
    ├── PlanStep A
    │   └── ReAct
    │       ├── Action → Observation
    │       ├── Action → Observation
    │       └── Acceptance / Step Reflection
    ├── PlanStep B
    │   └── ReAct
    ├── Parallel Join Reflection
    ├── Replan → PlanVersion N+1
    └── Final Reflection

AgentRun 结束
└── Reflexion Candidate
```

核心边界：

```text
Plan 决定“需要完成什么工作”
ReAct 决定“当前 Step 下一步采取什么动作”
Reflection 决定“当前结果是否合格、下一步走哪里”
Replan 决定“剩余计划应该怎样变化”
Reflexion 决定“本次经历有什么值得未来复用”
```

---

# 4. 为什么所有任务都必须有 Plan

Zuno 的 Plan 不等于“复杂任务才生成十几个步骤”。Plan 是任务执行 Contract。

简单问题也创建 Plan：

```text
用户：公司年假是多少天？

Deterministic Single-Step Plan
└── Step 1：检索现行年假制度并生成带引用回答
```

复杂问题创建 DAG Plan：

```text
用户：比较三家供应商过去两年的价格、SLA、交付表现和风险，
      并生成管理层报告。

Step 1：确定比较维度、时间范围和输出结构
  ├── Step 2A：分析供应商 A
  ├── Step 2B：分析供应商 B
  ├── Step 2C：分析供应商 C
  └── Step 2D：检索内部政策和行业风险
          ↓
Step 3：汇总证据并识别缺失、过期和冲突
          ↓
Step 4：形成横向比较与推荐
          ↓
Step 5：生成管理层报告
          ↓
Step 6：最终证据、引用和目标覆盖检查
```

所有任务都有 Plan 的价值：

```text
统一 Trace 和成本统计
统一 Budget 与 Deadline
统一 AnswerPolicy
统一重试与 Replan
统一恢复和取消
统一 RunOutcome
消除 direct_answer 旁路
```

---

# 5. Plan 的概念模型

## 5.1 Plan 不是 Action 清单

PlanStep 应表达稳定的工作目标，而不是预先写死每一个 Tool Call。

不推荐：

```text
Step 1：搜索“供应商 A 合同”
Step 2：搜索“供应商 A SLA”
Step 3：搜索“供应商 A 违约”
Step 4：读取文件 123
Step 5：读取文件 456
```

推荐：

```text
Step：分析供应商 A 的价格、SLA、交付表现和风险

Input Contract：
    时间范围、供应商 ID、可访问 KnowledgeSnapshot

Output Contract：
    结构化供应商分析结果 + EvidenceRefs

Acceptance Criteria：
    价格、SLA、交付和风险四个维度完整
    主要结论有 Evidence
    现行与过期来源已区分
```

具体搜索哪些词、是否追加查询、是否读取更多文档，由 Step 内 ReAct 根据 Observation 动态决定。

## 5.2 Plan 是 DAG

Plan 的顺序由依赖关系决定，不由数组位置决定：

```text
A → B
A → C
B + C → D
```

`sequence_no` 只用于 UI 稳定显示。

DAG 使系统可以表达：

```text
串行依赖
并行分支
多分支汇合
可选 Step
失败后替代路径
Replan 后复用已完成结果
```

## 5.3 PlanStepDefinition 的七个核心问题

每个 Step 必须回答：

```text
1. Objective
   这一步究竟要解决什么问题？

2. Input Contract
   输入来自用户、上下文、前序 Step、Evidence、Memory 还是 Runtime？

3. Output Contract
   产出是文本、结构化数据、EvidenceSet、Artifact、ToolResult 还是 Decision？

4. Acceptance Criteria
   什么条件下才算完成？

5. Execution Policy
   允许使用哪些 Capability、模型角色和工具？

6. Retry / Failure Policy
   失败后重试、升级模型、Fallback、Replan 还是跳过？

7. Budget / Concurrency Policy
   最多多少 Action、Token、成本、时间，能否并行以及需要什么资源？
```

## 5.4 Planner 不绑定基础设施实现

Plan 使用语义能力：

```text
RETRIEVE
TRANSFORM
TOOL
SYNTHESIZE
VERIFY
INTERACT
WAIT
```

Plan 不直接写：

```text
调用 Milvus collection X
查询 Neo4j database Y
使用某个厂商 SDK
执行某个内部 Python 函数
```

具体实现由 Capability Router、Knowledge 和 Tool Runtime 解析。

---

# 6. Planner Pipeline

Planner 不是一个 Prompt，而是一条受治理的流水线：

```text
TaskAnalyzer
→ ComplexityClassifier
→ RuntimePolicyResolver
→ PlannerRouter
→ DeterministicPlanner / SkillPlanner / ModelPlanner
→ PlanNormalizer
→ PlanValidator
→ PlanRepair
→ PlanVersion Activation
```

## 6.1 TaskAnalyzer

提取任务事实：

```text
用户目标与子目标
输出形式
是否需要 Knowledge
是否需要 Tool
是否存在副作用
是否需要 Citation
是否需要 Artifact
是否存在明确时间范围
是否需要用户澄清
风险与敏感度
```

TaskAnalyzer 输出结构化分析，不保存隐藏思维链。

## 6.2 ComplexityClassifier

复杂度不能只按 Step 数判断，还要考虑：

```text
目标数量
依赖深度
语义不确定性
Evidence 要求
副作用风险
输出复杂度
所需 Capability 数量
是否需要动态探索
```

建议级别：

```text
SIMPLE
    单目标、低不确定性、单 Step 可完成

COMPOUND
    多个独立或浅依赖子目标，可明显并行

COMPLEX
    多阶段依赖、动态探索、Evidence 冲突或高风险控制
```

## 6.3 PlannerRouter

```text
确定性规则足够
→ DeterministicPlanner

匹配成熟 Skill Template
→ SkillPlanner

开放式、多目标或动态任务
→ ModelPlanner
```

模型规划不是默认路径。简单任务不应为了“Agent 感”额外调用强模型。

## 6.4 PlanValidator

Plan 激活前至少验证：

```text
SchemaRule
DuplicateStepRule
DependencyExistsRule
AcyclicGraphRule
ReachabilityRule
GoalCoverageRule
TerminalDeliverableRule
StepGranularityRule
CapabilityExistsRule
InputOutputCompatibilityRule
SecurityPolicyRule
BudgetRule
ParallelSafetyRule
JoinPolicyRule
ReuseCompatibilityRule
```

确定性验证优先。只有 Goal Coverage、语义重复或步骤粒度等问题需要模型 Critic。

## 6.5 PlanRepair

```text
机械问题
→ Deterministic Repair

语义问题
→ Model Repair

最多两轮仍不合法
→ Safe Minimal Plan / Ask User / Abstain
```

模型 Planner 与 Repair 均在数据库事务外运行。只有最终合法 PlanVersion 在短事务中持久化和激活。

---

# 7. LangGraph 与动态 Plan 的关系

## 7.1 为什么不把每个 PlanStep 编译成固定节点

Plan 是运行时生成的：

```text
不同用户请求产生不同 Step
并行分支数量运行时才知道
Replan 会创建新的 Step 与依赖
某些 Step 会复用、跳过或等待外部事件
```

因此不能为每一种 Plan 重新定义一套永久静态 Graph。

Zuno 使用：

```text
固定的 AgentRunGraph
+
数据库中的动态 Plan DAG
+
固定的 StepExecutionGraph 子图
```

## 7.2 固定主图负责控制阶段

```text
Plan
→ Schedule
→ Dispatch
→ Step Subgraphs
→ Collect
→ Join
→ Schedule Next
→ Finalize
```

## 7.3 动态 Plan DAG 负责业务步骤

```text
PlanVersion
├── StepDefinition A
├── StepDefinition B
├── StepDefinition C
├── StepDefinition D
└── Dependencies
```

Scheduler 每轮读取 ACTIVE PlanVersion，计算当前 Ready Step。

## 7.4 StepExecutionGraph 是可复用 Worker

所有具体 Step 都进入同一个通用子图：

```text
Load Definition
→ Resolve Inputs
→ ReAct Actions
→ Acceptance
→ Reflection
→ Step Outcome
```

Step 的 Objective、Input、Output、Capability、模型角色和 Policy 来自 PlanStepDefinition，而不是为每个 Step 编写新的 Python Node。

---

# 8. LangGraph 如何并行执行 Plan

LangGraph 可以让多个静态分支同时运行，也可以使用 `Send` 在运行时动态创建 Worker。Zuno 对动态 Plan 使用后者：Scheduler 选择一组 Ready Step，为每个 Step 发送一个独立 StepGraphState。

## 8.1 Ready Step

一个 Step 成为 Ready，需要同时满足：

```text
属于 ACTIVE PlanVersion
execution_disposition = EXECUTE
所有 HARD Dependency 已满足
不存在成功的 StepRun
不存在同 Step 的有效活动 attempt
输入能够解析
Capability 可用
审批前置条件满足
预算能够预留
资源 Lease 能够获取
Deadline 未到期
Run 未取消或进入 Replan Barrier
```

## 8.2 最大安全并行集合

Scheduler 不是简单地执行全部 Ready Step，而是从 ReadySet 选择“最大安全集合”：

```text
ReadySet
→ Dependency Check
→ Input Availability Check
→ Resource Conflict Check
→ Side Effect Check
→ Workspace / Provider Quota Check
→ Budget Reservation
→ Security Gate
→ Selected Dispatch Set
```

默认并行：

```text
读取不同文档
分析多个独立实体
检索不同知识域
生成互相独立的报告章节
执行多个只读工具
从不同维度独立评估同一产物
```

默认串行或互斥：

```text
后一步依赖前一步输出
多个 Step 写同一个文件
多个 Step 修改同一个业务对象
高风险不可逆副作用
共享排他性 Sandbox 或数据库事务
Replan 正在替换剩余计划
Final Synthesis 和最终提交
```

## 8.3 DispatchGroup

一次并行调度形成一个 DispatchGroup：

```text
Scheduler Round 3
└── DispatchGroup
    ├── DispatchItem → StepRun B
    ├── DispatchItem → StepRun C
    └── DispatchItem → StepRun D
```

DispatchGroup 持久化：

```text
这轮选择了哪些 Step
为什么选择或延迟
采用什么 JoinPolicy
分支失败时如何处理
预期分支数和完成计数
```

数据库提交成功后，LangGraph 才执行动态 `Send`。

## 8.4 分支状态必须隔离

每个 Worker 使用独立 StepGraphState，只携带：

```text
run_id
step_run_id
step_definition_id
execution_snapshot_id
dispatch_group_id
必要的小型 Ref
```

分支不能直接修改同一个大型 Plan、ContextPack 或 Observation 列表。

## 8.5 Reducer 只聚合 Ref

并行 Worker 返回：

```text
BranchResultRef
    dispatch_item_id
    step_run_id
    status
    output_ref
    failure_ref
```

Reducer 按稳定 ID 去重，不使用简单列表追加导致 Checkpoint Resume 后重复。

## 8.6 JoinPolicy

```text
ALL_SUCCESS
    所有必要分支成功才继续

ALL_TERMINAL
    等待所有分支结束，允许部分失败交给 Join Reflection

ANY_SUCCESS
    任一成功即可满足

QUORUM
    达到指定成功数量即可继续

BEST_EFFORT
    汇总所有可用结果并允许 Partial
```

## 8.7 分支失败策略

```text
CONTINUE_SIBLINGS
CANCEL_SIBLINGS
FAIL_FAST
JOIN_THEN_REPLAN
JOIN_THEN_REFLECT
```

并行并不意味着失败语义模糊。每个 DispatchGroup 必须在创建时固定 JoinPolicy 和 BranchFailurePolicy。

---

# 9. ReAct：单个 Step 内如何执行

Plan 决定 Step Objective，ReAct 根据当前 Observation 动态选择 Action。

示例：

```text
Step Objective：
    分析供应商 A 的价格、SLA、交付表现和风险

Action 1：
    检索合同、采购单、交付记录

Observation 1：
    找到价格和交付记录，但缺少去年 SLA 违约记录

Action 2：
    使用 SLA、故障、超时、赔偿等关键词追加检索

Observation 2：
    找到三次违约记录和两份赔偿单

Action 3：
    结构化提取价格、SLA、违约次数、赔偿金额和风险 Evidence

Observation 3：
    四个要求维度完整

Acceptance：PASS
Step Outcome：COMPLETED
```

## 9.1 ReAct 不等于无限循环

每个 Step 受 StepBudget 约束：

```text
max_actions
max_model_calls
max_tool_calls
max_retrieval_rounds
token_limit
cost_limit
timeout_ms
```

有效预算是：

```text
min(Step Remaining Budget, Run Remaining Budget)
```

## 9.2 Action 类型

```text
MODEL
RETRIEVE
TOOL
SUBMIT_INGESTION
ASK_USER
REQUEST_APPROVAL
WAIT_EXTERNAL
COMPLETE_STEP
FAIL_STEP
```

## 9.3 并非每个 Step 都需要多轮 ReAct

```text
确定性转换
→ 单 Action

简单 Tool 查询
→ Tool Action + Acceptance

开放式检索与分析
→ 多轮 ReAct

高风险副作用
→ Prepare + Approval + Execute + Reconcile
```

避免把所有 Step 都包装成昂贵的多轮模型 Agent。

---

# 10. 质量控制不是“每步都调用一次强模型”

Agent Core 将质量判断拆成四层：

```text
Action Evaluation
Step Acceptance / Step Reflection
Join Evaluation / Join Reflection
Final Gate / Final Reflection
```

每一层解决不同问题。

## 10.1 Action Evaluation：每个 Action 后都执行

Action Evaluation 判断动作是否按执行 Contract 完成：

```text
模型调用是否成功
Tool 返回 SUCCEEDED、FAILED 还是 UNKNOWN
Retrieval 是否返回可用结果
输出 Schema 是否合法
副作用是否需要 Reconcile
是否超时或耗尽预算
```

它通常是确定性检查，不需要 Critic 模型。

## 10.2 Step Acceptance：每个 Step 准备结束时都执行

每个 Step 都必须验收：

```text
输出是否存在
Output Schema 是否正确
必需字段是否齐全
Evidence 数量和覆盖是否达标
Citation 是否满足要求
Artifact 是否存在
测试是否通过
Tool 状态是否满足条件
```

结论：

> 每个 Step 都必须 Acceptance，但不是每个 Step 都必须调用 Reflection 模型。

## 10.3 Step Reflection：关键或异常 Step 才调用语义 Critic

Step Reflection 判断规则无法完全回答的语义问题：

```text
结果是否真正完成 Objective
证据是否真正支持结论
不同来源是否存在冲突
是否需要继续 ReAct
是否值得用不同参数重试
是否应该升级模型
是否暴露出 Plan 假设错误
```

默认策略：

```text
step_reflection_policy = critical
```

默认触发条件：

```text
Acceptance Failed
结果存在语义不确定性
Evidence Conflict
关键决策 Step
高风险输出
重复 Action 或结果无新意
预算接近上限
弱模型多次失败
Step 请求 COMPLETE 但置信不足
```

通常不触发模型 Reflection：

```text
纯格式转换且 Schema 通过
简单只读 Tool 成功
确定性计算通过
已有明确测试证明完成
低风险单字段提取且规则验收通过
```

## 10.4 Join Evaluation：每次并行汇合都执行

Join Evaluation 检查：

```text
JoinPolicy 是否满足
必要分支是否完成
失败分支是否允许忽略
输出 Ref 是否可读取
是否达到 Quorum
是否存在取消中的分支
```

## 10.5 Join Reflection：部分失败或结果冲突时执行

Join Reflection 重点判断：

```text
各分支结论是否矛盾
是否有关键维度缺失
失败分支是否影响后续结论
是否需要只补跑某个分支
是否可以带着 Partial 继续
是否需要 Replan
```

默认触发：

```text
PARTIAL branch failure
Evidence conflict
结果覆盖不均衡
BEST_EFFORT / QUORUM 继续前
任一分支发出 ReplanRequest
```

## 10.6 Final Gate：所有任务结束前都执行

Final Gate 是确定性最终检查：

```text
用户要求的输出类型是否存在
Plan 的必要目标是否完成
必需 Artifact 是否存在
AnswerPolicy 的 Evidence / Citation 指标是否达标
是否还有运行中的 Step
RunOutcome 是否与实际结果一致
```

## 10.7 Final Reflection：复杂任务和严格知识任务默认执行

Final Reflection 判断：

```text
用户目标是否全部覆盖
最终结论是否与 Step 输出一致
关键 Claim 是否有 Evidence
引用是否准确支持 Claim
是否存在遗漏、自相矛盾或错误综合
是否应该 COMPLETED、PARTIAL、ABSTAINED 或 REFUSED
```

默认策略：

```text
简单单步任务
    Deterministic Final Gate
    默认不调用强模型 Critic

复杂多步骤任务
    Final Gate + Model Final Reflection

strict grounded answer
    Final Gate + Strong Critic

高风险副作用任务
    Deterministic Policy / Audit Gate
    必要时再加 Critic，但 Critic 不能批准权限
```

---

# 11. Reflection 的决策输出

Reflection 不是生成一段自由文本评价，而是返回结构化控制决策：

```text
PASS
CONTINUE_REACT
RETRY_ACTION
RETRY_STEP
ESCALATE_MODEL
RETRIEVE_MORE
REPLAN
WAIT_USER
WAIT_APPROVAL
WAIT_EXTERNAL
PARTIAL_CONTINUE
BLOCK
ABSTAIN
REFUSE
```

模型只产生 `ReflectionProposal`。最终决策必须经过 ReflectionDecisionGuard，确保不绕过：

```text
RuntimePolicy
RetryPolicy
Budget
Security
Approval
AnswerPolicy
Cancellation
Deadline
```

---

# 12. Retry、Replan、Reflection 和 Reflexion 的区别

## 12.1 Retry

Retry 表示目标和计划仍然正确，只是执行方法失败：

```text
网络超时
模型 JSON 格式错误
Retriever 临时失败
Tool 返回可重试错误
查询过窄但 Step Objective 仍然正确
弱模型执行失败，可以升级模型
```

Retry 可以：

```text
SAME_ACTION
ADJUST_PARAMETERS
FALLBACK_CAPABILITY
ESCALATE_MODEL
RETRIEVE_MORE
NO_RETRY
```

Step 级 Retry 创建新的 StepRun attempt，不把失败记录改回 RUNNING。

## 12.2 Replan

Replan 表示原计划的结构、假设或剩余步骤已经不适用：

```text
缺少原计划假设存在的数据
发现必须新增一个调查维度
前序结果改变了后续目标
某 Capability 永久不可用
并行结果暴露出新的关键冲突
用户补充信息改变任务范围
```

示例：

```text
PlanVersion 1
1. 检索内部知识库
2. 汇总结论
3. 生成报告

Reflection：
内部资料缺少 2026 年外部风险数据，无法完成目标。

PlanVersion 2
1. REUSE_COMPLETED：内部知识检索
2. 新增：受治理的外部风险检索
3. 新增：内部与外部证据对齐
4. 汇总结论
5. 生成报告
```

## 12.3 Reflection

Reflection 是判断机制：

```text
当前发生了什么问题？
结果是否合格？
应当 Retry、Replan、等待还是结束？
```

Reflection 自己不修改 Plan。

## 12.4 Reflexion

Reflexion 发生在任务结束之后：

```text
本次失败或成功有什么跨任务价值？
哪些做法值得未来任务复用？
适用范围、证据和失效条件是什么？
```

Reflexion 只产生 Candidate：

```text
PENDING REVIEW
→ APPROVED / REJECTED
→ Procedural / Episodic Memory
```

它不直接写入长期 Memory，也不保存隐藏思维链。

---

# 13. 并行执行中的 Replan Barrier

并行分支不能直接修改全局 Plan。

假设 B、C、D 并行：

```text
B：成功
C：发现计划假设错误，提出 ReplanRequest
D：仍在执行
```

C 不能直接激活 PlanVersion N+1，否则 D 仍按旧计划写入结果，可能造成状态混乱。

正确流程：

```text
ReplanRequest
→ Run Phase = REPLANNING
→ 停止调度新 Step
→ ReplanBarrier
→ 等待或取消旧版本活动分支
→ 汇总已完成 Observation
→ 生成并验证 PlanPatch
→ 激活 PlanVersion N+1
→ 恢复调度
```

Barrier 策略：

```text
WAIT_ALL
    等所有分支结束

DRAIN_SAFE_READ_ONLY
    允许安全只读分支完成，阻止新副作用

CANCEL_OBSOLETE
    取消已无价值且可取消的分支
```

已完成 Step 通过：

```text
execution_disposition = REUSE_COMPLETED
satisfied_by_step_run_id = previous successful StepRun
```

复用时必须验证：

```text
输入 Fingerprint 是否一致
KnowledgeSnapshot 是否兼容
输出 Contract 是否兼容
Artifact / Evidence 是否仍可访问
上游假设是否未被推翻
Security Scope 是否仍有效
```

第一版默认只允许 Exact Input Fingerprint 复用。

---

# 14. Planner、Executor、Critic 和 Synthesizer 模型独立

Plan 模型与实际执行模型不仅可以独立，而且应该独立。

Agent Core 不直接配置某个具体模型名，而是声明模型角色：

```text
TASK_ANALYZER
PLANNER
PLAN_REPAIR
EXECUTOR_FAST
EXECUTOR_REASONING
QUERY_REWRITER
EXTRACTOR
CRITIC
SYNTHESIZER
FINAL_CRITIC
```

Model Gateway 将模型角色解析为实际 Provider 和 Model。

示例：

```yaml
model_role_bindings:
  planner:
    model_ref: strong-reasoning

  plan_repair:
    model_ref: strong-reasoning

  executor_fast:
    model_ref: low-cost-tool-model

  executor_reasoning:
    model_ref: medium-reasoning

  extractor:
    model_ref: small-structured-output-model

  critic:
    model_ref: strong-reasoning

  synthesizer:
    model_ref: long-context-general-model

  final_critic:
    model_ref: strong-reasoning
```

## 14.1 推荐默认分工

| 阶段 | 默认策略 |
| --- | --- |
| 简单 Task Analysis | 规则或中等模型 |
| 复杂 Plan | 强推理模型 |
| 确定性单步 Plan | 不调用模型 |
| 普通 Query Rewrite | 弱模型 |
| 信息提取与格式转换 | 弱模型 |
| 普通 ReAct 决策 | 弱或中等模型 |
| 复杂推理 Step | 中等或强模型 |
| Step Acceptance | 规则优先 |
| 关键 Step Reflection | 强模型 Critic |
| Plan Repair | 强模型 |
| Final Synthesis | 中等或强模型 |
| Final Reflection | 强模型或专用 Critic |

## 14.2 强模型规划、弱模型执行

推荐模式：

```text
强模型
    复杂任务分析
    Plan
    Plan Repair
    关键 Reflection
    Final Reflection

弱模型
    Query Rewrite
    字段提取
    分类
    格式转换
    普通 ReAct 决策
    独立章节初稿

非模型
    Tool Execution
    Retrieval
    Schema Validation
    Citation Count
    Test Execution
    Policy Gate
```

## 14.3 Planner 必须知道 Executor 的能力边界

Planner 如果不知道执行模型能力，可能生成弱模型无法完成的巨大 Step：

```text
一次分析 50 份文档并完成法律、财务、技术和运营风险综合判断
```

PlanningContext 必须包含 `ModelCapabilityProfile`：

```text
context_window
structured_output_reliability
tool_calling_support
reasoning_level
code_capability
multilingual_capability
maximum_output
latency_class
cost_class
```

Planner 应把任务拆成弱模型可执行、可验收的 Step，把真正复杂的综合判断保留给 Synthesizer 或强模型 Executor。

## 14.4 自动模型升级

```text
EXECUTOR_FAST
→ Acceptance Failed
→ 调整参数重试
→ 再次失败
→ EXECUTOR_REASONING
→ 仍失败
→ Critic 判断 Retry / Replan / Abstain
```

模型升级受 StepPolicy、Budget 和 Risk 控制，不能每次失败都无限切换强模型。

## 14.5 Planner 与 Critic 可以使用不同模型

```text
Model A：生成 Plan
Model B：验证和批评 Plan
Model C：执行普通 Step
Model B：关键 Reflection
Model D：长文本 Synthesis
```

是否分离取决于质量收益、延迟、成本、风险和模型可用性，不为了形式上的“多模型”而增加调用。

---

# 15. RuntimePolicy：控制哪些机制被启用

所有机制都存在，但不代表每个任务都以最高强度执行。

```python
class RuntimePolicy(BaseModel):
    planning_mode: Literal["deterministic", "skill", "model"]
    react_policy: Literal["single_action", "dynamic"]
    step_reflection_policy: Literal["none", "critical", "every_step"]
    join_reflection_policy: Literal["none", "on_partial_or_conflict", "always"]
    final_reflection_policy: Literal["deterministic", "critic", "strict"]
    replan_policy: Literal["disabled", "on_failure", "on_material_change"]
    reflexion_policy: Literal["disabled", "meaningful_outcome"]
    model_routing_policy_ref: str
    concurrency_policy_ref: str
    budget_policy_ref: str
    cancellation_policy_ref: str
    retrieval_policy_ref: str | None
    tool_policy_ref: str | None
    approval_policy_ref: str | None
```

建议默认值：

```yaml
planning_mode: deterministic_or_model_by_complexity
react_policy: dynamic_for_open_steps
step_reflection_policy: critical
join_reflection_policy: on_partial_or_conflict
final_reflection_policy:
  simple: deterministic
  complex: critic
  strict_grounded: strict
replan_policy: on_material_change
reflexion_policy: meaningful_outcome
```

---

# 16. AnswerPolicy 与 Final Reflection 的关系

RuntimePolicy 决定“怎样执行”，AnswerPolicy 决定“什么条件下允许输出”。

```python
class AnswerPolicy(BaseModel):
    grounding_mode: Literal["none", "optional", "required", "strict"]
    minimum_evidence_count: int
    minimum_evidence_coverage: float
    minimum_authority_level: str | None
    citation_required: bool
    source_span_required: bool
    allow_model_prior: bool
    allow_partial_answer: bool
    disclose_missing_information: bool
    disclose_conflicting_evidence: bool
    disclose_stale_sources: bool
    insufficient_evidence_action: Literal["partial", "ask_user", "abstain", "fail"]
```

企业知识问答默认：

```text
grounding_mode = strict
allow_model_prior = false
citation_required = true
source_span_required = true
insufficient_evidence_action = abstain
```

Final Reflection 可以发现语义问题，但不能绕过 AnswerPolicy。

例如 Critic 认为答案“看起来合理”，但 Citation Coverage 不达标，最终仍必须 Partial 或 Abstain。

---

# 17. 完整运行示例

用户请求：

> 比较三家供应商过去两年的价格、SLA、交付表现和风险，结合公司采购制度，生成一份带引用的管理层报告。

## 17.1 Task Analysis

```text
任务类型：复杂知识分析 + Artifact
目标数量：价格、SLA、交付、风险、政策符合性、推荐
Knowledge：需要
Citation：严格要求
Artifact：管理层报告
副作用：无
复杂度：COMPLEX
```

## 17.2 RuntimePolicy

```text
Model Planner
Dynamic ReAct
Critical Step Reflection
Join Reflection on conflict/partial
Strict Final Reflection
Default Safe Parallelism
```

## 17.3 模型角色

```text
PLANNER            → 强推理模型
EXECUTOR_FAST      → 低成本结构化模型
EXECUTOR_REASONING → 中等推理模型
CRITIC             → 强推理模型
SYNTHESIZER        → 长上下文模型
FINAL_CRITIC       → 强推理模型
```

## 17.4 PlanVersion 1

```text
S1：定义比较口径、时间范围和输出结构

S2A：分析供应商 A
S2B：分析供应商 B
S2C：分析供应商 C
S2D：提取采购制度与风险规则

S3：Join 后检查覆盖、过期来源和证据冲突

S4：形成横向比较、评分和推荐

S5：生成管理层报告 Artifact

S6：最终 Claim-Evidence-Citation 与目标覆盖检查
```

依赖：

```text
S1
├── S2A
├── S2B
├── S2C
└── S2D
     ↓
    S3
     ↓
    S4
     ↓
    S5
     ↓
    S6
```

## 17.5 并行调度

S1 完成后，S2A、S2B、S2C、S2D 同时 Ready。

Scheduler 检查：

```text
均为只读分析
无共享写资源
预算足够
KnowledgeSnapshot 一致
Security Scope 一致
```

创建 DispatchGroup，并使用动态 Worker 并行执行四个 StepExecutionGraph。

## 17.6 分支内 ReAct

S2B 第一轮只找到价格和交付数据，没有 SLA 违约证据：

```text
Action 1：普通检索
Observation：SLA 维度缺失
Action 2：Query Rewrite + focused retrieval
Observation：找到两份故障通报
Action 3：结构化提取
Acceptance：PASS
```

S2C 找到两份相互矛盾的风险评级：

```text
Acceptance：字段完整
Step Reflection：Evidence Conflict
Step Outcome：COMPLETED_WITH_WARNING
```

## 17.7 Join Reflection

四个分支完成后：

```text
S2A：成功
S2B：成功
S2C：成功但证据冲突
S2D：成功
```

Join Reflection 判断冲突会影响最终推荐，需要补充来源权威与生效时间分析，输出 REPLAN。

## 17.8 Replan

Replan Barrier 已满足，因为四个分支均终止。

PlanVersion 2：

```text
REUSE S1
REUSE S2A
REUSE S2B
REUSE S2C
REUSE S2D

新增 S2E：验证供应商 C 风险来源的权威性、生效时间和 supersede 关系

S3：更新为汇总五个分支
S4：横向比较
S5：报告
S6：最终检查
```

## 17.9 模型升级

S4 使用 EXECUTOR_FAST 首次生成评分解释，但 Acceptance 发现推荐依据未覆盖全部风险证据。

```text
Retry：调整输入摘要
仍失败
→ ESCALATE_MODEL 到 EXECUTOR_REASONING
→ Acceptance PASS
```

## 17.10 Final Reflection

Final Gate：

```text
Artifact 存在
所有必要目标完成
Citation Coverage 达标
没有运行中 Step
```

Final Critic：

```text
目标覆盖完整
推荐与结构化评分一致
供应商 C 的冲突已披露
主要 Claim 均有 Evidence
```

RunOutcome：COMPLETED。

## 17.11 Reflexion

任务结束后生成 Candidate：

```text
“供应商风险来源冲突时，应优先比较 authority、effective time 与 supersedes 关系，
而不是仅按检索相关性选择来源。”
```

Candidate 进入 Memory Review，不能直接成为长期规则。

---

# Part II：运行架构

# 18. 双层 LangGraph

```text
AgentRunGraph
└── StepExecutionGraph
```

## 18.1 AgentRunGraph

```text
START
→ initialize_run
→ input_gate
→ resolve_authorization
→ resolve_execution_snapshot
→ check_input_readiness
   ├── wait_ingestion → interrupt
   └── ready
→ build_context
→ analyze_task
→ resolve_runtime_policy
→ create_plan
→ normalize_plan
→ validate_plan
   ├── repair_plan
   └── activate_plan_version
→ schedule_ready_steps
   ├── COMPLETE_PLAN → final_synthesis
   ├── WAIT → interrupt / await running branches
   ├── REPLAN → replan_barrier
   └── DISPATCH
→ create_dispatch_group
→ dynamic_send_step_workers
→ collect_branch_results
→ evaluate_join
   ├── CONTINUE_PLAN → schedule_ready_steps
   ├── RETRY_BRANCHES → schedule_ready_steps
   ├── PARTIAL_CONTINUE → schedule_ready_steps
   ├── REPLAN → replan_barrier
   ├── WAIT → interrupt
   └── TERMINATE
→ final_synthesis
→ extract_claims
→ bind_claims_and_citations
→ answer_policy_gate
→ final_reflection
   ├── PASS
   ├── REWRITE
   ├── RETRIEVE_MORE
   ├── REPLAN
   ├── ASK_USER
   ├── ABSTAIN
   └── REFUSE
→ finalize_run_outcome
→ build_reflexion_candidate
→ post_turn_commit
→ END
```

## 18.2 StepExecutionGraph

```text
START
→ load_step_definition
→ resolve_step_inputs
→ acquire_resource_leases
→ reserve_budget
→ preflight_gate
→ decide_action
→ validate_action
→ execute_action
→ normalize_observation
→ persist_action_and_observation
→ evaluate_action
→ evaluate_acceptance
→ maybe_step_reflection
→ decide_step_progress
   ├── CONTINUE_REACT → decide_action
   ├── RETRY_ACTION → execute_action
   ├── ESCALATE_MODEL → decide_action
   ├── COMPLETE → complete_step
   ├── RETRY_STEP → finish_attempt
   ├── REPLAN → return_replan_request
   ├── WAIT_USER → interrupt
   ├── WAIT_APPROVAL → interrupt
   ├── WAIT_EXTERNAL → interrupt
   └── FAIL / BLOCK / ABSTAIN → finish_attempt
```

---

# 19. Graph State

Graph State 只保存恢复控制流所需的小型字段。

```python
class AgentRunGraphState(TypedDict, total=False):
    schema_version: str
    run_id: str
    task_id: str
    thread_id: str
    workspace_id: str
    trace_id: str
    phase: str
    execution_snapshot_id: str | None
    active_plan_id: str | None
    active_plan_version_id: str | None
    dispatch_group_id: str | None
    dispatch_item_refs: list[str]
    branch_results: Annotated[list[BranchResultRef], merge_branch_results]
    pending_interrupt_id: str | None
    latest_reflection_id: str | None
    final_answer_ref: str | None
    outcome_ref: str | None
    terminal_status: str | None
```

```python
class StepGraphState(TypedDict, total=False):
    run_id: str
    workspace_id: str
    trace_id: str
    execution_snapshot_id: str
    dispatch_group_id: str
    step_run_id: str
    step_definition_id: str
    resolved_input_ref: str | None
    action_round: int
    model_role: str | None
    latest_action_run_id: str | None
    latest_observation_id: str | None
    latest_acceptance_result_id: str | None
    latest_reflection_id: str | None
    decision: str | None
    output_ref: str | None
    failure_ref: str | None
    terminal_status: str | None
```

禁止保存：

```text
完整 Plan
完整 ContextPack
完整 Observation Payload
完整检索结果
完整 Prompt
工具 stdout / stderr
文件正文
隐藏思维链
```

---

# 20. ExecutionContextSnapshot

每个 Run 固定执行环境：

```python
class ExecutionContextSnapshot(BaseModel):
    snapshot_id: UUID
    run_id: UUID
    authorization_context_ref: str
    authorization_policy_version: str
    security_epoch: int
    runtime_policy_ref: UUID
    answer_policy_ref: UUID
    model_routing_policy_ref: str
    knowledge_snapshot_refs: list[KnowledgeSnapshotRef]
    skill_version_refs: list[str]
    capability_catalog_version: str
    prompt_bundle_version: str
    created_at: datetime
```

作用：

```text
避免并行分支使用不同策略
避免长任务中静默切换知识索引
保证恢复后使用兼容配置
支持审计和结果复现
```

权限规则：

```text
初始正向权限范围固定
+
实时撤销永远优先
```

用户被移出 Workspace 或文档被紧急撤销时，Snapshot 不能绕过实时撤销。

---

# 21. 主要领域对象

## 21.1 AgentRun

代表一次完整用户任务，保存生命周期、阶段、活动 Plan、预算、Deadline、Interrupt 和 Outcome 引用。

## 21.2 Plan

一个 Run 的计划聚合根。Phase 1 每个 Run 只有一个 Plan，但可以有多个 PlanVersion。

## 21.3 PlanVersion

Plan 的不可变快照：

```text
Version 1 → SUPERSEDED
Version 2 → ACTIVE
```

激活后不能原地修改。

## 21.4 PlanStepDefinition

不可变的步骤定义，不保存运行状态。

## 21.5 StepRun

StepDefinition 的一次执行尝试：

```text
Attempt 1 FAILED
Attempt 2 COMPLETED
```

## 21.6 ActionRun

StepRun 中一次真实动作，关联模型、检索、工具或外部任务 Ref。

## 21.7 Observation

Action 执行结果的标准化事实。大型内容保存到 Object Store，只保留 Ref 和 Preview。

## 21.8 AcceptanceResult

一个 AcceptanceCriterion 对某次 StepRun 的确定性或模型评估结果。

## 21.9 ReflectionResult

Action、Step、Join 或 Final 层级的结构化质量判断和路由建议。

## 21.10 DispatchGroup / DispatchItem

一次并行调度批次和其中的各个分支。

## 21.11 PlanPatch / ReplanBarrier

修改剩余计划的操作集合，以及并行计划切换前的安全屏障。

## 21.12 RunOutcome

```text
COMPLETED
PARTIAL
ABSTAINED
REFUSED
BLOCKED
FAILED
CANCELLED
```

---

# 22. 状态机

## 22.1 AgentRun

```text
CREATED
→ RUNNING
↔ WAITING
→ CANCELLING
→ CANCELLED

RUNNING / WAITING
→ COMPLETED
→ PARTIAL
→ ABSTAINED
→ REFUSED
→ BLOCKED
→ FAILED
```

Phase：

```text
INITIALIZING
RESOLVING_CONTEXT
PLANNING
EXECUTING
REPLANNING
FINALIZING
TERMINAL
```

## 22.2 PlanVersion

```text
DRAFT → VALIDATING → ACTIVE → SUPERSEDED
DRAFT / VALIDATING → REJECTED
```

## 22.3 StepRun

```text
QUEUED → RUNNING ↔ WAITING
RUNNING → COMPLETED | FAILED | BLOCKED | CANCELLED
```

## 22.4 ActionRun

```text
PROPOSED → VALIDATED → WAITING_APPROVAL → EXECUTING
EXECUTING → SUCCEEDED | FAILED | UNKNOWN | CANCELLED
```

`UNKNOWN` 表示外部副作用是否成功无法确认，必须 Reconcile 或人工确认，不能自动当作失败重试。

---

# 23. Interrupt、Resume、Replay 与 Cancellation

## 23.1 Interrupt

统一等待场景：

```text
WAIT_USER
WAIT_APPROVAL
WAIT_EXTERNAL
WAIT_INGESTION
```

Interrupt 节点必须幂等。恢复时可能从节点开头重新执行，因此不可逆副作用必须放在 Interrupt 后的独立执行节点。

## 23.2 ReplayPolicy

```text
PURE
READ_ONLY_SNAPSHOT
IDEMPOTENT_WRITE
COMPENSATABLE_WRITE
NON_REPLAYABLE
```

```text
PURE                 → 可重算
READ_ONLY_SNAPSHOT   → 固定 Snapshot 后可重放
IDEMPOTENT_WRITE     → 相同幂等键重放
COMPENSATABLE_WRITE  → 先 Reconcile
NON_REPLAYABLE       → 人工确认
```

## 23.3 Cancellation

```text
Run → CANCELLING
停止新调度
取消 QUEUED StepRun
请求取消 RUNNING Action
释放 BudgetReservation
释放 ResourceLease
等待不可中断副作用收口
汇总 DispatchGroup
RunOutcome → CANCELLED / PARTIAL
```

Cancellation、Deadline、Security Revocation 和 Budget Exhaustion 必须传播到所有并行分支。

---

# 24. Port 与模型调用边界

```python
class ModelGatewayPort(Protocol):
    async def invoke(self, request: ModelInvocationRequest) -> ModelInvocationResult: ...

class KnowledgeQueryPort(Protocol):
    async def retrieve(self, request: KnowledgeQueryRequest) -> KnowledgeQueryResult: ...

class IngestionPort(Protocol):
    async def submit(self, request: SubmitIngestionRequest) -> ExternalJobHandle: ...
    async def get_status(self, job_id: str) -> ExternalJobStatus: ...
    async def cancel(self, job_id: str) -> None: ...

class ToolRuntimePort(Protocol):
    async def prepare(self, request: PrepareToolExecutionRequest) -> PreparedToolExecution: ...
    async def execute(self, request: ExecutePreparedToolRequest) -> ToolExecutionResult: ...
    async def reconcile(self, execution_id: str) -> ToolExecutionResult: ...
```

生产 Port 不返回 `Any`，必需依赖不使用 `None` 代替。测试使用 Fake Port。

Product/API 只调用 Runtime Facade：

```python
class AgentRuntimeService:
    async def start(self, command: StartAgentRunCommand) -> StartAgentRunResult: ...
    async def resume(self, command: ResumeAgentRunCommand) -> StartAgentRunResult: ...
    async def cancel(self, command: CancelAgentRunCommand) -> None: ...
    async def get_snapshot(self, run_id: UUID, workspace_id: str) -> AgentRunSnapshot: ...
    async def stream(self, run_id: UUID, workspace_id: str) -> AsyncIterator[RuntimeEnvelope]: ...
```

---

# Part III：代码与持久化实施规格

# 25. 代码分层

```text
Contracts
    ↓
Domain
    ↓
Application Services
    ↓
LangGraph Orchestration
    ↓
Ports
    ↓
Adapters / PostgreSQL
```

约束：

```text
Graph Node 不直接写 SQL
Domain 不导入 LangGraph
Application 不导入 FastAPI
Port 不返回 Any
ORM Row 不直接作为 Graph State
外部 API 调用不放在数据库事务内
```

## 25.1 目标目录

```text
src/backend/zuno/agent/
├── contracts/
│   ├── common.py
│   ├── requests.py
│   ├── policy.py
│   ├── planning.py
│   ├── execution.py
│   ├── reflection.py
│   ├── interrupt.py
│   ├── outcome.py
│   └── events.py
│
└── runtime/
    ├── service.py
    ├── composition.py
    ├── settings.py
    ├── domain/
    │   ├── run.py
    │   ├── plan.py
    │   ├── step.py
    │   ├── action.py
    │   ├── observation.py
    │   ├── dispatch.py
    │   ├── reflection.py
    │   ├── failure.py
    │   ├── outcome.py
    │   └── errors.py
    ├── application/
    │   ├── run_service.py
    │   ├── snapshot_service.py
    │   ├── planning_service.py
    │   ├── scheduling_service.py
    │   ├── step_execution_service.py
    │   ├── reflection_service.py
    │   ├── replan_service.py
    │   ├── finalization_service.py
    │   ├── interrupt_service.py
    │   ├── recovery_service.py
    │   └── cancellation_service.py
    ├── graph/
    │   ├── run/{state.py,nodes.py,routing.py,builder.py}
    │   └── step/{state.py,nodes.py,routing.py,builder.py}
    ├── planning/
    │   ├── analyzer.py
    │   ├── complexity.py
    │   ├── policy_resolver.py
    │   ├── router.py
    │   ├── normalizer.py
    │   ├── validator.py
    │   ├── repair.py
    │   └── planners/{deterministic.py,skill.py,model.py}
    ├── scheduling/
    │   ├── readiness.py
    │   ├── selector.py
    │   ├── join.py
    │   ├── concurrency.py
    │   ├── resource_leases.py
    │   └── budget_reservations.py
    ├── execution/
    │   ├── action_decider.py
    │   ├── action_validator.py
    │   ├── executor_registry.py
    │   └── executors/{model.py,retrieval.py,tool.py,ingestion.py,interaction.py}
    ├── reflection/
    │   ├── action_evaluation.py
    │   ├── acceptance.py
    │   ├── step_reflection.py
    │   ├── join_reflection.py
    │   ├── final_reflection.py
    │   ├── critic.py
    │   └── decision_guard.py
    ├── replan/
    │   ├── context.py
    │   ├── generator.py
    │   ├── validator.py
    │   ├── barrier.py
    │   └── applier.py
    ├── ports/
    │   ├── model.py
    │   ├── knowledge.py
    │   ├── ingestion.py
    │   ├── memory.py
    │   ├── capability.py
    │   ├── tool.py
    │   ├── security.py
    │   ├── artifact.py
    │   ├── trace.py
    │   └── system.py
    └── persistence/
        ├── unit_of_work.py
        ├── repositories.py
        └── postgres/{base.py,models.py,mappings.py,repositories.py,unit_of_work.py}
```

---

# 26. Repository 与 UnitOfWork

```text
AgentRunRepository
ExecutionSnapshotRepository
PolicySnapshotRepository
PlanRepository
PlanPatchRepository
DispatchRepository
StepRunRepository
ActionRunRepository
ObservationRepository
AcceptanceRepository
ReflectionRepository
FailureRepository
InterruptRepository
OutcomeRepository
RuntimeEventRepository
OutboxRepository
```

规则：

```text
Repository 不自行 commit
UnitOfWork 统一 commit / rollback
所有查询强制 workspace_id
可更新聚合携带 lock_version
Append-only 表不提供 update API
跨 Workspace 未命中返回 NotFound，不泄露对象存在
```

---

# 27. PostgreSQL 总体设计

## 27.1 Schema

```text
agent_runtime
    Agent Core 领域事实

langgraph_checkpoint
    LangGraph Checkpointer 表
```

LangGraph Checkpoint 不是 Agent Domain 事实源。

## 27.2 类型约定

```text
Core 自有 ID       UUID，由应用生成
跨模块 ID / Ref    TEXT
时间               TIMESTAMPTZ
金额               NUMERIC(18,6)
Token              BIGINT
小型不可变配置     JSONB
大型 Payload       Object Store Ref
状态               VARCHAR + CHECK
```

暂不使用 PostgreSQL ENUM，便于 Expand / Contract 和滚动升级。

## 27.3 通用字段

高频领域表：

```text
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

可更新表增加：

```text
updated_at TIMESTAMPTZ NOT NULL
lock_version INTEGER NOT NULL DEFAULT 0
```

---

# 28. PostgreSQL 表清单

```text
Run and Snapshot
├── agent_runs
├── agent_execution_context_snapshots
├── agent_knowledge_snapshot_refs
├── agent_runtime_policy_snapshots
└── agent_answer_policy_snapshots

Plan Definition
├── agent_plans
├── agent_plan_versions
├── agent_plan_steps
├── agent_plan_step_dependencies
└── agent_step_acceptance_criteria

Replan
├── agent_plan_patches
├── agent_plan_patch_operations
└── agent_replan_barriers

Scheduling
├── agent_dispatch_groups
├── agent_dispatch_items
├── agent_step_runs
├── agent_resource_leases
└── agent_budget_reservations

Execution Facts
├── agent_action_runs
├── agent_observations
├── agent_acceptance_results
├── agent_reflection_results
└── agent_failures

Wait and External Jobs
├── agent_interrupts
└── agent_external_job_handles

Grounded Output
├── agent_grounded_answers
├── agent_claims
├── agent_claim_evidence_bindings
└── agent_run_outcomes

Eventing
├── agent_runtime_events
└── agent_outbox_events
```

---

# 29. 关键表结构

## 29.1 agent_runs

```text
run_id UUID PK
workspace_id TEXT NOT NULL
task_id TEXT NOT NULL
thread_id TEXT NOT NULL
user_id TEXT NOT NULL
trace_id TEXT NOT NULL
client_request_id TEXT NOT NULL
goal_ref TEXT NOT NULL
goal_summary TEXT NOT NULL
status VARCHAR(32) NOT NULL
phase VARCHAR(32) NOT NULL
execution_snapshot_id UUID NULL
active_plan_id UUID NULL
active_plan_version_id UUID NULL
pending_interrupt_id UUID NULL
outcome_id UUID NULL
latest_failure_id UUID NULL
scheduler_round INTEGER NOT NULL DEFAULT 0
model_call_count INTEGER NOT NULL DEFAULT 0
tool_call_count INTEGER NOT NULL DEFAULT 0
retrieval_round_count INTEGER NOT NULL DEFAULT 0
input_tokens BIGINT NOT NULL DEFAULT 0
output_tokens BIGINT NOT NULL DEFAULT 0
cost_total NUMERIC(18,6) NOT NULL DEFAULT 0
deadline_at TIMESTAMPTZ NULL
cancel_requested_at TIMESTAMPTZ NULL
cancel_reason TEXT NULL
lock_version INTEGER NOT NULL DEFAULT 0
created_at / started_at / updated_at / finished_at
```

约束与索引：

```text
UNIQUE(workspace_id, client_request_id)
CHECK(status)
CHECK(phase)
INDEX(workspace_id, status, updated_at DESC)
INDEX(thread_id, created_at DESC)
partial INDEX(deadline_at) for active runs
```

## 29.2 agent_execution_context_snapshots

```text
snapshot_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
snapshot_version INTEGER NOT NULL
authorization_context_ref TEXT NOT NULL
authorization_policy_version TEXT NOT NULL
security_epoch BIGINT NOT NULL
runtime_policy_snapshot_id UUID NOT NULL
answer_policy_snapshot_id UUID NOT NULL
model_routing_policy_ref TEXT NOT NULL
capability_catalog_version TEXT NOT NULL
prompt_bundle_version TEXT NOT NULL
skill_version_refs_json JSONB NOT NULL
content_hash TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL
UNIQUE(run_id, snapshot_version)
UNIQUE(run_id, content_hash)
```

## 29.3 agent_plans / agent_plan_versions

```text
agent_plans
    plan_id UUID PK
    workspace_id TEXT NOT NULL
    run_id UUID NOT NULL UNIQUE
    status VARCHAR(24) NOT NULL
    current_version_id UUID NULL
    version_count INTEGER NOT NULL DEFAULT 0
    replan_count INTEGER NOT NULL DEFAULT 0
    lock_version INTEGER NOT NULL DEFAULT 0

agent_plan_versions
    plan_version_id UUID PK
    workspace_id TEXT NOT NULL
    run_id UUID NOT NULL
    plan_id UUID NOT NULL
    version_no INTEGER NOT NULL
    base_version_id UUID NULL
    source_patch_id UUID NULL
    status VARCHAR(24) NOT NULL
    planner_type VARCHAR(24) NOT NULL
    planner_model_call_ref TEXT NULL
    goal_summary TEXT NOT NULL
    assumptions_json JSONB NOT NULL
    planning_context_ref TEXT NULL
    content_hash TEXT NOT NULL
    activation_reason TEXT NULL
    created_at / activated_at / superseded_at
```

约束：

```text
UNIQUE(plan_id, version_no)
UNIQUE(plan_id, content_hash)
partial UNIQUE(plan_id) WHERE status = 'active'
```

## 29.4 agent_plan_steps

```text
step_definition_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_id UUID NOT NULL
plan_version_id UUID NOT NULL
logical_step_id TEXT NOT NULL
origin_step_definition_id UUID NULL
sequence_no INTEGER NOT NULL
title TEXT NOT NULL
objective TEXT NOT NULL
action_type VARCHAR(32) NOT NULL
input_contract_json JSONB NOT NULL
output_contract_json JSONB NOT NULL
evidence_requirements_json JSONB NOT NULL
allowed_capabilities_json JSONB NOT NULL
model_role TEXT NULL
retrieval_policy_ref TEXT NULL
tool_policy_ref TEXT NULL
retry_policy_json JSONB NOT NULL
budget_json JSONB NOT NULL
concurrency_policy_json JSONB NOT NULL
replay_policy_json JSONB NOT NULL
execution_disposition VARCHAR(24) NOT NULL
satisfied_by_step_run_id UUID NULL
optional BOOLEAN NOT NULL DEFAULT FALSE
priority INTEGER NOT NULL DEFAULT 100
content_hash TEXT NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

约束：

```text
UNIQUE(plan_version_id, logical_step_id)
UNIQUE(plan_version_id, sequence_no)
```

## 29.5 agent_plan_step_dependencies

```text
dependency_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_version_id UUID NOT NULL
step_definition_id UUID NOT NULL
requires_step_definition_id UUID NOT NULL
dependency_type VARCHAR(16) NOT NULL
created_at TIMESTAMPTZ NOT NULL
UNIQUE(plan_version_id, step_definition_id, requires_step_definition_id)
CHECK(step_definition_id <> requires_step_definition_id)
```

DAG 无环由 PlanValidator 保证。

## 29.6 agent_dispatch_groups / agent_dispatch_items

```text
agent_dispatch_groups
    dispatch_group_id UUID PK
    workspace_id TEXT NOT NULL
    run_id UUID NOT NULL
    plan_version_id UUID NOT NULL
    scheduler_round INTEGER NOT NULL
    join_policy VARCHAR(24) NOT NULL
    branch_failure_policy VARCHAR(32) NOT NULL
    quorum INTEGER NULL
    expected / completed / succeeded / failed / cancelled counts
    status VARCHAR(24) NOT NULL
    decision_summary TEXT NOT NULL
    created_at / dispatched_at / completed_at / updated_at
    lock_version INTEGER NOT NULL DEFAULT 0
    UNIQUE(run_id, scheduler_round)

agent_dispatch_items
    dispatch_item_id UUID PK
    workspace_id TEXT NOT NULL
    run_id UUID NOT NULL
    dispatch_group_id UUID NOT NULL
    step_definition_id UUID NOT NULL
    step_run_id UUID NOT NULL
    branch_no INTEGER NOT NULL
    status VARCHAR(24) NOT NULL
    result_ref TEXT NULL
    failure_id UUID NULL
    created_at / updated_at
```

## 29.7 agent_step_runs

```text
step_run_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
plan_id UUID NOT NULL
plan_version_id UUID NOT NULL
step_definition_id UUID NOT NULL
logical_step_id TEXT NOT NULL
dispatch_group_id UUID NOT NULL
attempt_no INTEGER NOT NULL
status VARCHAR(24) NOT NULL
resolved_input_ref TEXT NULL
input_fingerprint TEXT NOT NULL
model_role TEXT NULL
output_ref TEXT NULL
acceptance_summary_json JSONB NOT NULL
failure_id UUID NULL
budget_reservation_id UUID NULL
worker_id TEXT NULL
lease_token TEXT NULL
lease_expires_at TIMESTAMPTZ NULL
idempotency_key TEXT NOT NULL
elapsed_ms BIGINT NOT NULL DEFAULT 0
model / tool / retrieval counters
input / output tokens
cost_total NUMERIC(18,6)
started_at / finished_at / created_at / updated_at
lock_version INTEGER NOT NULL DEFAULT 0
```

约束：

```text
UNIQUE(step_definition_id, attempt_no)
UNIQUE(idempotency_key)
```

## 29.8 agent_action_runs

```text
action_run_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NOT NULL
action_round INTEGER NOT NULL
action_kind VARCHAR(32) NOT NULL
model_role TEXT NULL
capability_id TEXT NULL
decision_summary TEXT NOT NULL
expected_observation TEXT NOT NULL
arguments_ref TEXT NULL
arguments_preview_json JSONB NOT NULL
replay_mode VARCHAR(32) NOT NULL
side_effect_class VARCHAR(32) NOT NULL
status VARCHAR(24) NOT NULL
idempotency_key TEXT NOT NULL
model_call_ref TEXT NULL
retrieval_run_ref TEXT NULL
tool_execution_ref TEXT NULL
ingestion_job_ref TEXT NULL
approval_ref TEXT NULL
observation_id UUID NULL
failure_id UUID NULL
retry_of_action_run_id UUID NULL
usage counters
started_at / finished_at / created_at / updated_at
lock_version INTEGER NOT NULL DEFAULT 0
```

## 29.9 agent_observations

Append-only：

```text
observation_id UUID PK
workspace_id TEXT NOT NULL
run_id UUID NOT NULL
step_run_id UUID NOT NULL
action_run_id UUID NOT NULL UNIQUE
kind VARCHAR(40) NOT NULL
status VARCHAR(24) NOT NULL
source_type VARCHAR(32) NOT NULL
source_ref TEXT NULL
summary TEXT NOT NULL
payload_ref TEXT NULL
payload_preview_json JSONB NOT NULL
evidence_refs_json JSONB NOT NULL
citation_refs_json JSONB NOT NULL
failure_id UUID NULL
trace_span_ref TEXT NULL
created_at TIMESTAMPTZ NOT NULL
```

## 29.10 agent_acceptance_results / agent_reflection_results

```text
agent_acceptance_results
    acceptance_result_id UUID PK
    step_run_id UUID NOT NULL
    criterion_id UUID NOT NULL
    passed BOOLEAN NOT NULL
    actual_value_json JSONB NULL
    evaluator_type VARCHAR(24) NOT NULL
    evaluator_ref TEXT NULL
    reason TEXT NOT NULL
    UNIQUE(step_run_id, criterion_id)

agent_reflection_results
    reflection_result_id UUID PK
    workspace_id TEXT NOT NULL
    run_id UUID NOT NULL
    scope VARCHAR(16) NOT NULL
    step_run_id UUID NULL
    dispatch_group_id UUID NULL
    decision VARCHAR(32) NOT NULL
    reason TEXT NOT NULL
    failure_bucket VARCHAR(64) NULL
    unsupported_claim_refs_json JSONB NOT NULL
    missing_evidence_json JSONB NOT NULL
    violated_constraints_json JSONB NOT NULL
    suggested_actions_json JSONB NOT NULL
    confidence NUMERIC(5,4) NULL
    critic_model_call_ref TEXT NULL
    decision_guard_json JSONB NOT NULL
    created_at TIMESTAMPTZ NOT NULL
```

## 29.11 Resource Lease 与 Budget Reservation

```text
agent_resource_leases
    resource_key
    access_mode = read | write | exclusive
    lease_token
    expires_at

agent_budget_reservations
    reserved_input_tokens
    reserved_output_tokens
    reserved_cost
    reserved_model_calls
    reserved_tool_calls
    reserved_retrieval_rounds
    used_* counters
```

并行调度前必须预留预算和资源，完成后结算并释放剩余量。

## 29.12 Interrupt、Outcome、Event 和 Outbox

```text
agent_interrupts
agent_external_job_handles
agent_grounded_answers
agent_claims
agent_claim_evidence_bindings
agent_run_outcomes
agent_runtime_events
agent_outbox_events
```

同一 Run 默认只允许一个 PENDING Interrupt。RuntimeEvent 按 `run_id + sequence_no` 顺序读取。Outbox 使用 `published_at IS NULL` partial index。

---

# 30. 并发控制

## 30.1 乐观锁

```sql
UPDATE ...
SET status = :status,
    lock_version = lock_version + 1,
    updated_at = now()
WHERE id = :id
  AND lock_version = :expected_lock_version;
```

`rowcount != 1` 返回 `OPTIMISTIC_LOCK_CONFLICT`。

## 30.2 Scheduler 锁

```text
SELECT AgentRun FOR UPDATE
SELECT AgentPlan FOR UPDATE
验证 ACTIVE PlanVersion
计算 Ready Step
```

同一个 Run 只允许一个 Controller 进行调度决策。

## 30.3 Resource Lock

第一版使用：

```sql
SELECT pg_advisory_xact_lock(hashtextextended(:resource_key, 0));
```

然后在事务中检查冲突 Lease。不能只依赖进程内 Python Lock。

## 30.4 后台任务抢占

Outbox Publisher、Lease Reconciler 和后台 Job 使用：

```sql
FOR UPDATE SKIP LOCKED
```

---

# 31. 事务边界

## 31.1 创建 Run

```text
BEGIN
幂等检查 workspace_id + client_request_id
创建 AgentRun
写 RUN_CREATED Event
写 Outbox
COMMIT
```

## 31.2 创建和激活 Plan

模型调用和 PlanValidator 在事务外。

```text
BEGIN
锁定 Run
创建 Plan / PlanVersion / Step / Dependency / Acceptance
PlanVersion → ACTIVE
更新 Plan.current_version_id
更新 Run.active_plan_id / active_plan_version_id
写 Event / Outbox
COMMIT
```

## 31.3 创建 Dispatch

```text
BEGIN
锁定 Run 和 Plan
计算 ReadySet
选择最大安全集合
创建 DispatchGroup / DispatchItem
创建 StepRun
预留 Budget
获取 ResourceLease
写 Event
COMMIT

COMMIT 后执行 LangGraph dynamic Send
```

## 31.4 外部 Action

```text
事务 A：创建 ActionRun(EXECUTING) → COMMIT
事务外：调用 Model / Knowledge / Tool / Ingestion
事务 B：写 Observation、更新 ActionRun、结算 Budget、写 Event → COMMIT
```

不得在数据库事务中等待模型或外部工具。

## 31.5 应用 PlanPatch

```text
BEGIN
锁定 Plan
验证 patch.base_version_id == current_version_id
验证 ReplanBarrier satisfied
创建 PlanVersion N+1
复制、替换或新增 Step Snapshot
旧 Version → SUPERSEDED
新 Version → ACTIVE
Patch → APPLIED
更新 Plan.current_version_id
写 Event / Outbox
COMMIT
```

## 31.6 Resume

```text
BEGIN
锁定 Interrupt
验证 workspace / user / client_request_id
写入 response
Interrupt → RESOLVED
Run → RUNNING
写 Event
COMMIT

使用相同 thread_id 执行 Command(resume=...)
```

---

# 32. LangGraph PostgreSQL Checkpointer

```text
使用锁定版本 AsyncPostgresSaver
thread_id = run_id
Step 子图使用稳定 namespace
应用 lifespan 中初始化
首次部署执行 setup()
Checkpoint 不替代 Domain Store
Checkpoint 写失败时不启动下一个副作用 Action
升级 Checkpointer 前执行恢复兼容测试
```

---

# 33. Alembic Migration 规格

```text
ACR-001  Schema Foundation
ACR-002  Run and Policy Snapshots
ACR-003  Plan Definition
ACR-004  Scheduling Runtime
ACR-005  Action and Evaluation Facts
ACR-006  Replan
ACR-007  Interrupt and External Job
ACR-008  Grounded Answer and Outcome
ACR-009  Events and Outbox
ACR-010  Deferred Foreign Keys
ACR-011  Optional RLS Foundation
```

## ACR-001

创建 `agent_runtime` 和 `langgraph_checkpoint` Schema。

## ACR-002

创建 Run、RuntimePolicy、AnswerPolicy、ExecutionContextSnapshot、KnowledgeSnapshotRef。

## ACR-003

创建 Plan、PlanVersion、PlanStep、Dependency、Acceptance，以及 one-active-version partial unique index。

## ACR-004

创建 DispatchGroup、StepRun、DispatchItem、ResourceLease、BudgetReservation。

## ACR-005

创建 Failure、ActionRun、Observation、AcceptanceResult、ReflectionResult。

## ACR-006

创建 PlanPatch、PatchOperation、ReplanBarrier。

## ACR-007

创建 Interrupt 与 ExternalJobHandle。

## ACR-008

创建 GroundedAnswer、Claim、ClaimEvidenceBinding、RunOutcome。

## ACR-009

创建 RuntimeEvent、OutboxEvent 和未发布事件 partial index。

## ACR-010

添加循环依赖 FK：

```text
Run → Snapshot / Plan / Version / Interrupt / Outcome / Failure
Plan → CurrentVersion
PlanStep → Reused StepRun
Action → Observation
```

## ACR-011

P1 后启用 RLS。启用前必须验证连接池 Session Setting Reset，防止 Workspace 泄漏。

Migration 原则：

```text
Expand
→ 发布兼容代码
→ 可恢复 Backfill
→ 验证
→ Contract
```

SQLite 到 PostgreSQL 使用独立 Migration Program，不塞进 Alembic `upgrade()`。

---

# Part IV：验证与迁移

# 34. 测试规格

## 34.1 Domain Unit

```text
AgentRun 状态转换
PlanVersion 不可变
PlanPatch stale detection
StepRun retry creates new attempt
Action UNKNOWN outcome
Reflection Decision Guard
JoinPolicy
ResourceLease conflict
Budget settlement
Model escalation policy
Step reuse fingerprint
```

## 34.2 PostgreSQL Integration

```text
Plan 激活原子性
一个 Plan 只有一个 ACTIVE Version
Dispatch 创建事务
Action 幂等
Interrupt Resume 幂等
Optimistic Lock Conflict
Outbox Claim
Resource Advisory Lock
Workspace Isolation
```

## 34.3 LangGraph Integration

```text
简单任务仍创建 Single-Step Plan
静态并行分支
动态 Send fan-out
幂等 Reducer
并行分支部分失败
Join Reflection
并行 Interrupt
精确 Resume
Step Subgraph Checkpoint
Replan Barrier
```

## 34.4 模型角色测试

```text
Planner 与 Executor 使用不同 ModelRef
弱模型失败后升级 ExecutorReasoning
Critic 不能绕过 AnswerPolicy
Deterministic Step 不调用 Critic
复杂 Plan 触发 Final Critic
模型不可用时按 Role Fallback
```

## 34.5 Fault Injection

```text
Tool 成功后、Observation 写入前崩溃
DispatchGroup 创建事务中崩溃
PlanPatch 应用事务中崩溃
Checkpoint 写失败
Worker Lease 过期
Outbox 重复投递
Security Epoch 变化
并行分支产生重复 BranchResult
```

## 34.6 E2E

```text
简单知识问答创建单步骤 Plan
复杂任务至少两个独立 Step 真实并行
Step 内真实多轮 ReAct
Acceptance 改变路由
Step Reflection 只在 Trigger 下执行
Join Reflection 处理冲突
Replan 创建新 PlanVersion
已完成 Step 跨版本复用
强 Planner + 弱 Executor + 强 Critic
KnowledgeSnapshot 固定
Ingestion Wait / Resume
审批副作用 exactly-once
AnswerPolicy 阻止无证据回答
PARTIAL / ABSTAINED Outcome
Cancellation 传播到并行分支
```

---

# 35. Current Baseline 与 Target Gap

Current Baseline：

```text
LangGraph StateGraph 主图骨架
SQLiteAgentRunStore
Strategy / Plan baseline
单次 ReAct executor baseline
Reflection / Replan / Grounded Synthesis baseline
Tool approval / resume / idempotency baseline
Corrective Retrieval / EvidenceLedger baseline
Memory / Reflexion Candidate baseline
Completion / Workspace Task API baseline
```

仍未达到 Target：

```text
PostgreSQL Runtime Store
Repository + UnitOfWork
强类型 Port
PlanStepDefinition / StepRun / ActionRun 完整分离
动态多轮 StepExecutionGraph
真实 Parallel DispatchGroup + dynamic Send
幂等 Branch Reducer
分层 Action / Step / Join / Final Reflection
独立 Model Role Routing 与自动升级
Immutable PlanVersion + PlanPatch
原生 PostgreSQL Checkpointer 恢复
AnswerPolicy / Partial / Abstain 完整闭环
固定 Benchmark measured proof
```

---

# 36. 实现阶段

```text
Phase 1  Contract Package 与 Typed Port
Phase 2  Domain Model 与 Repository / UnitOfWork
Phase 3  PostgreSQL Schema
Phase 4  Graph State V2 与所有任务统一 Plan
Phase 5  StepExecutionGraph 与多轮 ReAct
Phase 6  分层 Acceptance / Reflection
Phase 7  Model Role Routing 与自动升级
Phase 8  Parallel Scheduler / DispatchGroup / Send / Join
Phase 9  PlanVersion / Replan Barrier / Step Reuse
Phase 10 PostgreSQL Checkpointer / Interrupt / Recovery
Phase 11 Outcome、Cancellation、AnswerPolicy
Phase 12 Cutover、Benchmark 与旧路径清理
```

---

# 37. Requirement IDs

```text
ARCH-AGENT-001  LangGraph 是唯一产品主 Controller。
ARCH-AGENT-002  Plan、ReAct、Reflection、Replan、Reflexion 在同一 Runtime 中按层级协作。
ARCH-AGENT-003  Runtime State 可序列化、可版本化、可恢复。
ARCH-AGENT-004  所有循环受统一 RuntimeBudget 控制。
ARCH-AGENT-005  Completion 与 Workspace Task 共用同一 Runtime。
ARCH-AGENT-006  Interrupt / Resume 跨进程可恢复。
ARCH-AGENT-007  大对象只保存 Ref。
ARCH-AGENT-008  每个控制阶段产生 RuntimeEvent 和 Trace Span。
ARCH-AGENT-009  所有任务都必须创建 Plan，包括简单任务。
ARCH-AGENT-010  Plan 必须表达为 DAG，并默认最大化安全并行。
ARCH-AGENT-011  PlanVersion 激活后不可变，Replan 必须创建新版本。
ARCH-AGENT-012  PlanStepDefinition、StepRun 和 ActionRun 必须分离。
ARCH-AGENT-013  每个 AgentRun 必须固定 ExecutionContextSnapshot。
ARCH-AGENT-014  知识任务必须固定 KnowledgeSnapshot，不得静默混用索引版本。
ARCH-AGENT-015  Grounded Completion 必须通过 AnswerPolicy。
ARCH-AGENT-016  动态 Fan-out 必须通过 DispatchGroup、DispatchItem 和 StepRun 持久化。
ARCH-AGENT-017  副作用 Action 必须声明 ReplayPolicy 和 IdempotencyPolicy。
ARCH-AGENT-018  RunOutcome 必须区分 COMPLETED、PARTIAL、ABSTAINED、REFUSED、BLOCKED、FAILED、CANCELLED。
ARCH-AGENT-019  Cancellation、Deadline、Budget 和 Security 必须传播到所有分支。
ARCH-AGENT-020  Ingestion、Tool Job、用户输入和审批等待必须使用统一 Interrupt Contract。
ARCH-AGENT-021  Graph State 只保存控制 Ref，领域事实存入 PostgreSQL / Object Store。
ARCH-AGENT-022  Action Evaluation、Step Acceptance、Step Reflection、Join Reflection 和 Final Reflection 必须分离。
ARCH-AGENT-023  每个 Step 必须 Acceptance，但默认不是每个 Step 都调用模型 Critic。
ARCH-AGENT-024  并行 Replan 必须经过 Replan Barrier。
ARCH-AGENT-025  PostgreSQL 是 Agent Runtime 结构化事实源；Checkpointer 只保存图控制状态。
ARCH-AGENT-026  所有跨模块 Port 必须使用明确输入输出类型。
ARCH-AGENT-027  外部执行必须明确成功、失败或 UNKNOWN。
ARCH-AGENT-028  领域写入与跨模块事件发布必须使用事务 + Outbox。
ARCH-AGENT-029  Planner、Executor、Critic、Synthesizer 和 Repair 必须使用独立 Model Role，可绑定不同模型。
ARCH-AGENT-030  Planner 必须获得 Executor ModelCapabilityProfile，避免生成不可执行 Step。
ARCH-AGENT-031  弱模型失败后的模型升级必须受 RetryPolicy 和 Budget 控制。
ARCH-AGENT-032  并行 Worker 只返回幂等 BranchResultRef，不直接合并大型可变状态。
```

---

# 38. 最终冻结结论

Agent Core 的核心不是数据库表，也不是一个巨大的 ReAct 循环，而是以下概念共同形成的任务控制系统：

```text
LangGraph Single Controller
+ 所有任务统一 Plan
+ Plan DAG
+ 默认最大化安全并行
+ 动态 Send / 幂等 Reducer / Join
+ Step 内 ReAct
+ 每个 Action Evaluation
+ 每个 Step Acceptance
+ 关键 Step Reflection
+ 部分失败或冲突时 Join Reflection
+ 复杂任务与 Strict Grounding 的 Final Reflection
+ Retry 与 Replan 分离
+ Immutable PlanVersion / Replan Barrier
+ Reflexion Candidate Governance
+ Planner / Executor / Critic / Synthesizer 独立模型角色
+ 强模型规划与反思、弱模型执行、失败后受控升级
+ ExecutionContextSnapshot / KnowledgeSnapshot
+ Interrupt / Resume / Replay / Cancellation
+ PostgreSQL Domain Facts
+ LangGraph PostgreSQL Checkpointer
+ RuntimeEvent / Trace / Outbox
+ Precise RunOutcome
```

默认质量策略冻结为：

```text
每个 Action 都评估
每个 Step 都验收
不是每个 Step 都调用强模型 Reflection
并行结果部分失败或冲突时执行 Join Reflection
简单单步任务默认只做确定性 Final Gate
复杂任务、报告任务和 Strict Grounded Answer 执行模型级 Final Reflection
```

默认模型策略冻结为：

```text
复杂 Plan 和 Plan Repair 使用强模型
普通执行优先使用低成本模型
复杂 Step 可声明 ExecutorReasoning
关键 Reflection 和 Final Reflection 使用强 Critic
弱模型失败后按 Policy 升级，而不是无条件重试或直接 Replan
```

该模块只负责统一规划与控制，不吞并 Knowledge、Input、Model、Memory、Capability、Tool 或 Security 的 Owner 边界。