# 04 Agent Runtime & Control（智能体运行与控制）

<!-- status: design-baseline-v1; implementation: not-authorized; native-runtime: measurement-gated -->

## Part A — Human Narrative

### 为什么复杂任务才需要运行控制

简单问答没有必要启动一套复杂 Agent Runtime：确认材料和权限、检索原文、生成带依据答案并检查即可。运行控制真正有价值的场景，是任务需要跨多个步骤、等待人工、并行调用能力、在失败后继续，或者因为材料、能力和假设变化而调整剩余计划。

这个模块解决的是“这次任务现在应该做什么、做到哪里、失败以后怎样继续”，不是“法律业务世界最终承认什么”。如果简单路径已经足够，就不应该为了架构统一强迫它进入复杂运行时。

### 进入原生运行时的任务一定有计划

只要任务进入 Zuno Native Agent Runtime（原生智能体运行时），就必须有 Plan（计划）。简单但仍需要运行时能力的任务使用 Deterministic Single-Step Plan（确定性单步计划）；复杂任务使用 Dynamic DAG Plan（动态有向无环计划）。

这意味着不能通过 `direct_answer` 或类似旁路绕过 Plan、Trace、Budget、AnswerPolicy 和 RunOutcome。简单任务可以有简单计划，但不能在已经进入原生运行时后突然失去控制、预算和可审计边界。

### 固定运行图和动态计划各负责什么

总体形态保持为：固定 AgentRunGraph 管整次运行，动态 Plan DAG 表达任务目标、依赖和可并行关系，固定 StepExecutionGraph 管单个步骤怎样执行。Plan-and-Execute 负责“先做什么、后做什么、哪些可以一起做”；ReAct 只负责一个 Step 内部的 Action 与 Observation；Reflection 负责质量判断和控制决策；Replan 在原计划结构或假设失效时修改剩余计划；任务结束后的 Reflexion 只能产生长期经验候选，不能直接提交长期记忆。

Planner 必须知道执行器和 Capability 的真实能力边界，不能把一个超大、不可验收的任务塞成单个 Step。Step 应该小到能够明确输入、输出、证据、预算和接受条件，又不需要为了追求“原子化”把每个普通函数调用都变成图节点。

### 并行的目标是安全吞吐，不是并行数量

Ready Step 只有在依赖、输入、资源冲突、副作用、预算、配额和安全门禁都允许时才并行。数据依赖、写同一资源、不可逆副作用、排他资源、Replan 和 Final Synthesis 默认串行。

优先使用 LangGraph 自带的动态分发和状态归并原语，例如 `Send`、Reducer、Subgraph 和 Checkpointer；只有实际证据证明这些原语不足时，才引入自定义 DispatchGroup、复杂锁或额外分布式调度。逻辑上的九个模块也不意味着要为运行时先建设一个独立分布式调度平台。

### 质量控制不是“每一步都再问一次大模型”

每个 Action 都要有 Evaluation（行动评估），每个 Step 都要有 Acceptance（步骤验收），但不是每个 Step 都调用模型 Reflection。确定性 Schema 校验、Citation Check、测试、预算、安全门禁等能由代码完成时，优先使用确定性能力。

Acceptance 失败、证据冲突、关键决策、重复失败或高风险时，才触发 Step Reflection；并行结果部分失败或互相冲突时触发 Join Reflection；简单任务默认使用确定性 Final Gate；复杂任务和严格有据回答才使用模型级 Final Reflection。这样把“质量控制”从“每一步多调用一次模型”变成明确的触发式机制。

### 重试、重规划和对账为什么必须分开

模型服务 503 但任务结构仍正确，是 Retry（重试）；Capability / Tool 语义变化导致原来的参数、依赖或假设失效，是 Replan（重规划）；外部请求已经发出但现实结果未知，是 Reconcile（对账恢复）。

把三者混在一起很危险：把计划错误当临时故障会无限重试，把外部未知结果当失败重试可能重复产生副作用。运行控制拥有“下一步应该采取哪种控制动作”的决定，但现实副作用的最终确认仍由工具运行与外部效果负责。

### PlanVersion 为什么激活以后不能原地改

复杂任务运行到一半可能需要重规划。如果直接修改正在运行的 Plan，已经派出去的并行分支就无法知道自己属于旧假设还是新假设。

因此 PlanVersion 激活后不可变；重规划创建新版本。并行环境里进入 Replan 前需要 Replan Barrier：停止继续基于旧版本派发新工作，等待或标记旧分支，再激活新计划。晚到的旧分支结果必须携带原 PlanVersion 和 causation identity，不能污染新计划。

### 运行状态和领域状态怎样分开

AgentRun、PlanVersion、StepRun、Branch / Join、Budget、Interrupt、ControlDecision 和 Checkpoint 属于运行控制状态。正式 Matter、Finding、HumanDecision 和 WorkProduct 属于法律领域。

如果某个 Step 的完成条件要求 Formal Admission（正式准入），没有匹配的正式准入回执，运行时不能宣布该 Step 正式完成。PostgreSQL 保存领域事实，LangGraph Checkpointer 保存图控制状态，两者通过耐久回执对账，而不是共享一个“总状态”或做跨存储 2PC。

### 人工中断为什么要求副作用幂等

LangGraph 的 `interrupt()` 可以暂停图并在外部输入后恢复，但当前官方语义是恢复时会从发生 interrupt 的 node 起点重新执行，而不是从 Python 代码的那一行继续。因此 interrupt 之前发生的现实副作用必须幂等，或者放进可被 Checkpoint 正确复用的任务边界；否则一次人工审批恢复可能意外重复发送外部请求。

这也是 Zuno 把外部副作用交给工具运行与效果回执管理、而不是直接写在任意 graph node 里的原因。

### Single Controller 和多智能体怎样共存

Zuno 采用 Single Controller（单控制器）作为产品运行时原则，不默认建设自治 Multi-Agent Runtime。Specialist Agent（专家智能体）或子图可以作为某个计划步骤的执行方式，也可以在安全条件允许时并行，但它们只能返回候选、证据、观察或建议，不能直接提交领域事实、批准权限、绕过预算或执行未审批副作用。

一次性专家通常继承父图的 Checkpointer / subgraph persistence 即可；只有专家需要独立于父任务跨调用维持生命周期时，才有理由设计独立 thread / checkpoint。不能为了“多 Agent”先建设一套产品级 Agent Society。

### 为什么原生运行时仍然是条件能力

模块边界已经清楚，但原生运行时是否比“通用宿主 + 法律后端”真正更有价值仍要通过 A/B/C 对照测量。若真实任务证明普通 Host 加后端就能满足持久执行、HITL、领域准入和恢复要求，就应该缩小甚至删除自有运行时，而不是为了架构完整保留它。

### 当前、目标与缺口

Current Runtime Baseline 已证明 AgentRunApplicationService → AgentRuntimeService → AgentRunStore / checkpoint → Agent Core graph 的主路径，以及持久化失败、approval interrupt、duplicate claim、cancel、restart、unknown effect reconcile 等有限语义。正式四 Profile runtime、复杂 DAG 并行故障测试、真实 HA / fencing / takeover、完整 A/B/C benchmark、formal admission recovery E2E 和生产恢复仍未建立。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

**Owns** Single Controller 与任务控制，不拥有业务真相。Native Runtime entrant always has a Plan；Simple = deterministic single-step；Complex = dynamic DAG。PlanVersion immutable after activation；Retry != Replan != Reconcile；Formal Admission-required Step 必须消费 matching AdmissionReceipt；direct-answer bypass 不允许绕过 Plan / Trace / Budget / AnswerPolicy / RunOutcome。

### B2 Responsibility / Ownership

**Owns**：AgentRun、Plan / PlanVersion、Step / StepRun、Branch / Join、Budget control、parallel dispatch、Action / Step control evaluation、Retry / Replan / Reconcile control decision、Interrupt / Resume、Checkpoint-based control recovery、RunOutcome。

**Does not own**：Canonical Domain State、Authorization / Approval、Tool Effect truth、Capability semantics、Model provider policy、long-term Memory truth、final external UI publication。

### B3 Upstream / Downstream

上游主要接收 01 的 task goal / scope、02 的 domain refs、03 的 readiness / evidence、05 的 capability metadata、07 的 model eligibility、08 的 security decisions 和 budget constraints。下游调度 05 / 07 / 06，必要时向 02 请求正式准入，并向 01 返回 RunOutcome 和类型化结果。

### B4 Authoritative Facts / Core Objects

核心控制对象族：AgentRun、PlanVersion、Step / StepRun、Branch / Join state、Dispatch / control references、Budget state、Interrupt、ControlDecision、Checkpoint、RunOutcome。Plan DAG 是某次运行的控制事实，不是产品 Agent Definition，也不是法律领域状态。

### B5 Cross-boundary Contracts

核心引用包括 task / scope、Readiness / Evidence refs、Capability eligibility、Model routing / usage refs、Authorization / Approval refs、PreparedAction / Effect receipts、AdmissionReceipt 和 HumanDecision refs。Runtime 只保存必要引用，不复制其他模块的权威对象。

### B6 Normal Flow

task analyze → create deterministic or dynamic PlanVersion → activate immutable plan → calculate Ready Steps → security / budget / resource gate → dispatch StepExecutionGraph → ReAct actions → Action Evaluation → Step Acceptance → conditional Reflection → join / conflict evaluation → Retry or Replan when needed → Final Synthesis → Final Gate / optional Final Reflection → consume AdmissionReceipt where required → RunOutcome。

### B7 State / Lifecycle

至少覆盖 Run lifecycle、active PlanVersion、StepRun attempt、Branch / Join、Interrupt / Resume、Budget consumption、ControlDecision、Retry attempt、Replan barrier、reconciliation wait、late / stale branch 和 terminal RunOutcome。具体 enum 后续冻结，但必须能表达“当前激活计划”和“旧分支结果不可再写入当前控制状态”。

### B8 Failure Taxonomy

主要失败包括 transient model / provider failure、step validation failure、evidence conflict、capability drift、budget / quota exhausted、security revoked、parallel partial failure、late branch、checkpoint failure、domain admission mismatch、external effect unknown 和 controller crash / takeover ambiguity。

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

Retry：计划仍成立，仅执行失败；同一 StepRun / action identity 的重试必须保持幂等边界和预算累计。

Replan：依赖、能力、材料、假设或结构失效；创建新 PlanVersion，经过 Replan Barrier 后激活。

Reconcile：外部现实结果未知；Runtime 等待 06 的确认结果，不自己猜测。

Restart：从 Checkpointer 恢复控制状态，再用 Domain / Effect / Audit receipts 对账。Late branch 必须携带原 PlanVersion / causation identity。

### B10 Security / Approval / Audit

受保护材料读取、模型外发、秘密使用、工具执行和正式准入前消费当前安全决定。Resume / Retry / Replan 不复用过期授权。Budget 和 AnswerPolicy 不能被模型输出绕过。高风险 effect 的强制审计要求由 08 决定，06 / 对应持久化边界证明是否完成。

### B11 Persistence / Transaction Boundaries

LangGraph Checkpointer 保存图控制状态；PostgreSQL Domain Store 保存业务事实；06 保存 Effect / Reconciliation receipts；08 / durable audit boundary 保存关键安全与审计事实。默认不做跨 Store 2PC，通过稳定 causation / idempotency identity 和 receipts 恢复。

### B12 Observability / Evaluation

Trace 至少关联 run、plan version、step run、action、model call、retrieval、tool attempt、admission 和 budget。评测关注 task completion、step acceptance、replan frequency、retry amplification、parallel efficiency、stale branch rejection、recovery correctness、latency / token / cost，并和通用 Host + Legal Backend 做 A/B/C 对照。

### B13 Current / Target / Gap / Evidence

Current 见 [`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md)。Target 是 Single Controller + fixed AgentRunGraph + dynamic Plan DAG + fixed StepExecutionGraph。Gap：A/B/C benchmark、复杂并行 fault injection、HA / fencing / takeover、真实四 Profile runtime、AdmissionReceipt recovery E2E、security epoch drift 和 Specialist benefit measurement。

### B14 Code / Database / Migration Constraints

优先使用 LangGraph 原生 persistence、interrupt、`Send`、Reducer 和 Subgraph 机制，不默认新建自定义调度器、分布式锁或 Agent Runtime 服务。当前 LangGraph 官方文档明确：`Send` 支持动态 map-reduce 分发；subgraph 默认可继承父 checkpointer 以支持单次调用的持久执行；`interrupt()` 恢复会重新执行 node，因此 interrupt 前副作用必须幂等。实现时应以当前官方文档再次验证版本语义：

- https://docs.langchain.com/oss/python/langgraph/graph-api
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://docs.langchain.com/oss/python/langgraph/interrupts
- https://docs.langchain.com/oss/python/langgraph/use-subgraphs

本设计不冻结 LangGraph node 名称、数据库表或服务数量；只有详细设计和测量证据才能继续下沉。
