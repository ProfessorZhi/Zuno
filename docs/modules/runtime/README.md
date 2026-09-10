# 04 Agent Runtime & Control（智能体运行与控制）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 一个能跑完的 Agent，还不是一个能长期恢复的 Runtime

简单 Agent 最自然的实现，是把当前上下文交给模型，让模型决定下一步调用哪个 Tool，再把结果放回上下文，直到模型给出最终答案。任务只有几秒钟、没有外部副作用、失败后从头再跑也无所谓时，这种 ReAct 式循环已经足够。把所有任务都提前建模成复杂状态机，没有必要。

问题出现在一项法律工作开始持续十几分钟甚至更久以后。系统要等材料处理、做多路检索、调用专业能力、并行比较不同观点，途中可能等待人工，还可能提交正式业务结果或触发外围系统。运行期间新的证据会进入，模型和外部服务会失败，权限会变化，进程也会重启。此时 message history 还能记录“发生过什么”，却很难稳定回答“现在应该继续什么”。

设想一个争议分析正在并行执行三个分支：合同义务、付款事实和抗辩理由。前两个已经返回，第三个仍在运行。就在此时，用户补入一份补充协议，付款日期发生变化。旧计划里第三个分支几分钟后返回，而且结果本身写得很好。

如果 Runtime 只看“这个任务成功完成了”，它很容易把晚到结果直接拼进新答案；如果看到计划已经变化就把所有旧结果一律丢弃，又会浪费仍然基于相同材料、仍然有效的计算。04 的职责正是在这种变化里维持控制因果：一次 Run 当前采用哪套计划，哪些工作已经派发，哪些结果仍有资格被当前计划接受，什么时候重试，什么时候需要重规划，什么时候必须等待其他 Owner 给出更强事实。

### 计划一旦派发，就不能假装它从未存在过

长任务需要一个显式计划，但“显式计划”不意味着每一步都由 LLM 临时重新规划。稳定任务完全可以一次形成 DAG，再用确定性调度执行；只有原有前提失效时，才值得让 Planner 重新组织后续工作。

真正重要的是计划版本。一个分支被派发以后，它已经绑定当时的输入、材料、能力和依赖关系。如果 Controller 原地修改同一个 Plan 对象，后来返回的结果就失去了“我是基于哪套前提算出来的”这一身份。Target 因而让已经激活的 PlanVersion 保持不可变；需要调整时创建新版本，并明确旧工作哪些可以继续、哪些要取消、哪些结果回来以后必须重新验收。

这也是 `Single Controller` 出现的原因。专业计算可以由多个 Worker、Specialist、模型或 Capability 并行完成，但全局计划版本的激活、ready queue、Join、Budget、Replan、取消和 late-result acceptance 需要一个逻辑写者维持顺序。否则两个自治 Agent 同时改全局计划时，很难回答某个结果究竟属于哪次决定，也很难在重启后恢复一致视图。

Single Controller 是逻辑控制权，不要求所有计算都串行，更不要求把 Runtime 部署成一个永远单实例的进程。Lease、fencing 或队列可以让不同 Worker 接管执行；只要同一个控制事实在某一时刻有明确写者即可。吞吐瓶颈如果未来真实出现，再考虑分区控制，而不是为了“Multi-Agent 更先进”提前放弃统一因果。

外层运行生命周期、任务级动态计划和单个 Step 的执行边界也不必混成一张巨图。Target 用稳定的 Run 宿主管启动、恢复和结束，用动态 Plan DAG 表达当前任务依赖，再让每个 Step 在稳定执行边界内调用模型、Capability 或 Tool。工程参考把它压缩成 `Fixed AgentRunGraph + dynamic Plan DAG + fixed StepExecutionGraph`。这套结构的意义是把“会随任务改变的东西”限制在 Plan，而不是让每次 Replan 都重建整个运行框架。

### 恢复时，Checkpoint 只能告诉 Runtime 自己记到了哪里

计划控制解决了变化，崩溃又会暴露另一种问题。

假设一个 Step 已经把专业人员确认的结果交给 02。Domain transaction 成功，新 DomainVersion 和正式准入证明都已经落盘；04 正准备写下一份 Checkpoint 时进程崩溃。新的 Worker 启动以后，只看到旧的控制进度。如果它把 Checkpoint 当作整个系统的唯一真相，就会再次执行正式提交。

所以恢复不能机械地“从上一个节点继续”。Runtime 先判断当前 Step 涉及哪类外部事实，再去相应 Owner 查询。纯计算没有更强外部状态时可以重算；正式业务提交先查 02 的耐久完成证明；现实副作用先查 06 的 Effect / Reconciliation；等待人工的工作要重新确认 Approval 和当前安全条件。Owner fact 已经成立时，04 修复自己的 projection；Owner fact 不存在时，才决定重新执行。

Checkpoint 的角色由此变得很清楚：它保存控制面为了恢复所需的 Run、Plan、Step、等待和预算进度，减少重复计算，但不会因为自己写了 completed 就创造正式法律事实或现实效果。它可以比 Domain、Effect 或 Security 更旧，因此恢复顺序不能反过来让业务世界服从 Checkpoint。

同一个原则也适用于 Worker 接管。Lease 或 fencing 可以防止两个 Controller 同时修改运行控制，却不能证明某个远端 POST 没有发生，也不能证明某个 Domain transaction 没提交。基础设施原语只保护它负责的并发边界，跨责任域完成仍然要读对应 Owner 的事实。

### Retry、Replan 和 Reconcile来自三种不同失败

模型 Provider 临时 503 时，原计划、输入和动作语义都没有变化，有限 Retry 通常合理。新材料进入以后，旧计划的前提已经变化，再重复相同调用只会得到基于旧世界的更多结果，此时应该形成新的 PlanVersion。外部 POST 已经发出却 timeout 时，问题更不同：系统不知道过去的现实动作到底发生没有，继续执行之前必须由 06 查清结果。

这三类故障之所以需要分开，不是为了多造状态，而是因为恢复动作方向不同。Retry 重做同一个仍然有效的尝试；Replan 改变未来执行方式；Reconcile 回头确认一个可能已经发生的现实结果。把三者都实现成“失败后再跑一次”，会在最危险的副作用窗口制造重复动作。

Replan 期间还需要处理旧计划的在途工作。Controller 创建新 PlanVersion 后，不一定要粗暴停止所有旧 Worker；某些纯计算如果输入版本没变，回来以后仍可能有价值。Target 通过 Replan Barrier 记录切换边界：哪些旧工作应取消，哪些可以完成，晚到结果回来后按什么 freshness 和 causation 重新验收。是否“晚到”只是时间属性，最终能不能用仍取决于它现在是否满足当前前提。

Join 也因此不只是“等三个 future 都完成”。一个并行分支可能来自旧 Plan，一个可能已经被取消，一个可能 schema 正确但专业验收失败。Controller 只有在确认结果属于当前 barrier、仍满足输入新鲜度和 acceptance 条件后，才把它计入后续计划。并行提高吞吐，不改变结果资格。

### 等待、预算和取消让 Runtime 只控制未来

法律任务常需要等待人工数小时甚至数天。恢复后直接从暂停行的下一行继续，看起来最简单，却忽略了等待期间世界已经变化：材料可能更新，Capability 或 Model 资格可能改变，SecurityEpoch 可能推进，原 Approval 也可能失效。

因此 resume 本身就是一次重新验收。04 恢复 Plan 和 Step 的控制上下文，再消费当前 Knowledge、Capability、Security 和 Domain facts；原条件仍成立才继续，否则进入 Replan、重新申请 Approval 或重新计算。等待不是冻结世界，只是暂停控制进程。

预算也属于控制事实。一次调用失败后连续 retry、fallback 或 reflection，会不断消耗 token、时间和 Provider 费用。每个 Provider 记录自己真实发生的 Usage，04 根据 Run Budget 决定继续、降级、换路线、请求人工还是停止。不能让每个下游模块各自无限重试，因为局部“再试一次”累积起来可能让全局任务失控。

取消同样只约束还没有不可逆发生的未来工作。Controller 可以停止新的 Step 派发、请求 Worker 取消并忽略不再有资格的晚到计算，但已经完成的 Domain commit、已确认的外部 Effect 和已经产生的模型费用仍然是历史事实。把 Run 标成 CANCELLED 不等于回滚整个世界。

### Runtime 应尽量站在成熟框架之上

LangGraph 一类框架已经提供图执行、checkpoint、interrupt、并发调度等通用能力，Zuno 没有理由重复实现这些基础设施。04 只需要保留通用框架不会替法律业务拥有的那部分控制语义：计划版本怎样绑定当前前提，正式准入结果怎样被验收，现实 Effect unknown 时为什么暂停等待 Reconcile，权限和材料变化后怎样重新判断 late result。

Native Runtime 也不应该成为身份象征。如果 Generic Agent Host 加 Zuno Legal Backend 已经能够满足长期状态、恢复和控制需求，自研 Runtime 应保持很薄，甚至退出主路径。只有真实任务证明通用 Host 无法提供所需的恢复正确性、控制可解释性、成本或吞吐，才值得继续扩大 04。

同理，动态规划、Specialist 并行和复杂 Join 都应该按任务需要启用。大量简单工作如果使用固定 workflow 就能稳定解决，就继续使用固定 workflow。Agentic 的价值在于在少数前提真正变化的地方做语义重构，而不是让每一步都重新问模型“下一步怎么办”。

### Current / Target / Gap

**Target：** 04 拥有 AgentRun、PlanVersion、StepRun、Checkpoint、ready / join、等待、Budget、取消和 Replan 等控制事实；它以 Single Controller 维持计划因果，并在恢复时优先消费 Domain、Effect、Security、Knowledge 等 Owner 已经成立的更强事实。

**Current：** 完整三层运行图、不可变 PlanVersion、Replan Barrier、跨 Owner recovery、长期人工等待恢复和 Native Runtime 取舍属于 Target 设计。Current 代码中已有的 Agent、checkpoint、tool calling 或 runtime foundation 只能按 `docs/evidence/`、代码和测试实际证明的范围描述。

**Gap：** 仍需要长任务故障注入、Domain commit / Checkpoint crash-window、late-result acceptance、Controller 接管、真实等待恢复、预算收敛和 Generic Host 对照实验。没有这些证据时，不能把设计完整度写成恢复能力已经被生产验证。

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。