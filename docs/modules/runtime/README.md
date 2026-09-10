# 04 Agent Runtime & Control（智能体运行与控制）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 新证据进入以后，一个成功返回的旧分支仍然可能不能直接使用

简单 Agent 最自然的实现，是把当前上下文交给模型，让模型决定下一步调用哪个 Tool，再把结果放回上下文，直到得到最终答案。任务只有几秒钟、没有现实副作用、失败后从头再跑也没有代价时，这种 ReAct 式循环已经足够。固定 workflow 能解决的任务也应继续使用固定 workflow，没有理由先造复杂运行时。

问题从任务开始持续十几分钟甚至更久以后出现。设想一项合同争议分析同时执行三个分支：合同义务、付款事实和抗辩理由。前两个已经返回，第三个仍在运行。此时用户补入一份新的补充协议，付款日期发生变化；几分钟后，旧的抗辩分支终于返回，而且结果本身写得很好。

系统现在不能只问“这个分支算成功了吗”。它还要知道这份结果基于哪一版材料、当时哪套任务前提、现在这些前提是否仍成立。把所有晚到结果一律丢弃会浪费仍然有效的计算，看到计算成功就直接拼进新答案又可能把旧世界的结论带进当前结果。

04 的职责从这个时间差里出现。它控制一项长任务现在按什么前提继续，哪些工作已经派发，哪些返回结果仍有资格进入当前计划，什么时候只是重试同一件事，什么时候必须改变后续计划，以及什么时候应该停下来等待 Domain、Effects、Security 或 Knowledge 给出更强的事实。

### 计划一旦发出去，旧计划就必须留下可以识别的身份

长任务需要显式计划，但显式不等于每一步都让 LLM 重新规划。稳定任务可以一次形成依赖关系，再由确定性调度执行；只有材料、权限、能力资格或其他关键前提发生变化时，才值得重新组织后续工作。

真正麻烦的是已经派发出去的工作。一个 Worker 开始分析时，已经使用了当时的材料、输入和依赖。如果 Controller 直接在原来的 Plan 对象上改写内容，旧 Worker 回来以后就很难回答“你到底是按改动前还是改动后的世界算的”。

Target 因而让已经激活的计划保持不可变。需要改变未来执行时创建新的 `PlanVersion`，旧任务继续带着原来的版本身份。结果回来以后，Runtime 再根据当前材料和计划前提判断它可以继续使用、需要重新验收，还是应该重做。版本在这里保护的是运行因果，不是为了给每次小调整增加形式化成本。

计划切换还需要一个明确的逻辑写者。假设两个自治 Controller 同时看到新证据：一个准备取消旧分支，另一个却继续激活新的后续 Step；如果两边都能独立改全局计划，重启以后很难还原哪次决定先发生、哪个结果属于哪套计划。

Zuno 因此把当前计划的激活、重规划和全局控制收敛给一个逻辑控制者，工程上称为 `Single Controller`。专业分析仍然可以由多个 Worker、模型和 Specialist 并行执行；这里的“单一”只约束控制事实的写入顺序。Lease、fencing 或队列可以让不同 Worker 接管这份控制责任，也不要求 Runtime 永远只有一个物理进程。只有控制吞吐真的形成瓶颈以后，才值得研究更复杂的分区写者方案。

运行时内部仍可以分成稳定的外层任务生命周期、会随任务变化的计划，以及每个 Step 的稳定执行边界。这样 Replan 只改变真正需要变化的任务依赖，不必为了一个新证据重新发明整个运行框架。更精确的三层运行图和状态约束留在 Engineering Reference；第一次阅读只需要记住一件事：变化集中在计划，恢复仍然有稳定宿主和稳定执行边界。

### Domain 已经提交而 Checkpoint 还没写时，恢复必须先相信业务事实

计划版本解决了“前提变化以后旧结果属于谁”，进程崩溃会继续暴露另一类时间差。

假设一个 Step 已经把专业人员确认的结果提交给 Domain。业务事务成功，新的 DomainVersion 和正式提交证明已经落盘；Runtime 正准备保存下一份 Checkpoint，进程就在这几毫秒里崩溃。新的 Worker 启动以后只能看到旧 Checkpoint。如果它从这里机械恢复，就会以为正式提交还没有发生，并再次写同一份业务事实。

恢复时应该先确认这一步有没有在别的责任域留下更强的耐久结果。正式业务提交先查询 Domain；已经发生就修复 Runtime 自己的控制进度，不再提交。现实副作用先查询 Effects；发送结果仍然未知时先对账。等待人工的工作重新确认当前 Approval 和安全条件。只有纯计算没有留下更强外部事实时，重新计算才通常是最简单的恢复方式。

Checkpoint 仍然很重要。它保存 Run、Plan、Step、等待和预算等控制进度，让系统不必每次重启都从头推导。但它只能证明 Runtime 上一次记录到了哪里，可能比 Domain、Effect 或 Security 的事实更旧。恢复顺序不能反过来要求业务世界服从一份较旧的控制快照。

同样，Lease 或 fencing 可以防止两个 Controller 同时修改运行控制，却不能证明某个远端 POST 没有发生，也不能证明 Domain transaction 没提交。基础设施原语保护自己的并发边界；跨责任域恢复仍然要回到拥有结果的地方确认事实。

### 三种失败会把系统推向三个不同方向

模型 Provider 临时返回 503 时，任务目标、输入和专业含义都没有变化。有限地重新做同一个调用通常合理，这类动作就是 Retry。

新材料进入以后，原计划依赖的前提已经变化。继续重复旧调用只会得到更多基于旧世界的结果，Runtime 需要形成新的计划版本，重新决定哪些后续工作仍然需要做，这属于 Replan。

外部 POST 已经发出但连接在响应前超时时，问题又不同。系统不知道过去的现实动作到底有没有发生，继续发送之前必须由 Effects 查询远端事实并收敛这个不确定结果，这属于 Reconcile。

三者分开的原因是恢复方向不同：Retry 重做仍然有效的当前尝试，Replan 改变未来，Reconcile 回头查清过去。把它们都实现成“失败后再跑一次”，会在最危险的外部副作用窗口制造重复动作。

Replan 时，旧计划可能还有 Worker 在途。新计划形成以后，没有必要粗暴地把所有旧计算都当成垃圾；输入版本没有变化、专业前提仍然成立的结果，回来以后仍可能有用。Target 用一个明确切换边界记录旧计划和新计划的关系，工程上称为 `Replan Barrier`。它帮助 Runtime 判断哪些工作应该取消、哪些可以继续、晚到结果回来以后需要按什么新鲜度和因果重新验收。

并行汇合也服从同样原则。几个 future 都返回，并不自动意味着后续 Step 可以开始：某个结果可能属于旧计划，某个已经被取消，另一个虽然格式正确却没有通过专业验收。Runtime 只把当前仍然有资格的结果计入后续依赖。并行提高吞吐，不会改变结果是否仍然适用。

### 等待和取消只改变未来，不能冻结或回滚已经发生的世界

法律任务可能等待人工数小时甚至数天。恢复后从暂停代码的下一行继续，看起来最简单，却假设等待期间什么都没有变化。现实里材料可能更新，Capability 或模型资格可能变化，SecurityEpoch 可能推进，原来的 Approval 也可能过期。

所以 resume 本身要重新验收当前前提。Runtime 恢复自己的 Plan 和 Step 上下文，再读取当前 Knowledge、Capability、Security 和 Domain facts；条件仍然成立才继续，否则改变计划、重新申请审批或重新计算。等待只是暂停控制过程，不会冻结业务世界。

预算同样属于 Runtime 的控制责任。一次模型调用失败后，SDK retry、Gateway fallback、外层 reflection 如果各自独立决定“再试一次”，很容易把一个异常放大成大量 token、延迟和费用。下游 Provider 记录真实发生的 Usage，Runtime 再从整个 Run 的预算决定继续、换路线、请求人工还是停止。

取消也只控制还没有不可逆发生的未来工作。Controller 可以停止新的 Step 派发、请求 Worker 停止并忽略已经失去资格的晚到计算；已经正式提交的 Domain 事实、已经确认的外部 Effect 和已经产生的模型费用仍然是历史。把 Run 标成 CANCELLED 不会提供时间倒流能力。

### 当成熟框架已经够用时，Runtime 应该尽量薄

LangGraph 一类框架已经提供图执行、Checkpoint、interrupt 和并发调度等通用机制。Zuno 没有理由重写这些基础设施。04 只需要拥有通用框架不会替法律业务决定的控制语义：当前计划基于什么前提，计划变化以后旧结果如何重新判断，Domain 已提交但 Checkpoint 较旧时怎样恢复，Effect unknown 时为什么要停下来对账，以及权限或材料变化后什么时候必须重规划。

Native Runtime 也不是产品身份。如果 Generic Agent Host 加 Zuno Legal Backend 已经可以满足长期状态、恢复正确性和控制可解释性，自研 Runtime 应保持很薄，甚至退出主路径。只有真实任务证明通用 Host 在这些约束上不足，并且额外 Runtime 的收益超过维护成本，才值得继续扩大。

动态规划、Specialist 并行和复杂汇合也按同一原则处理。大量任务使用固定 workflow 就能稳定完成时，应继续使用固定 workflow。Agentic 控制真正有价值的地方，是任务前提在运行过程中发生变化，而系统需要有根据地改变未来，而不是让每一步都重新问模型下一步做什么。

### Current / Target / Gap

**Target：** 04 拥有 AgentRun、PlanVersion、StepRun、Checkpoint、ready / join、等待、Budget、取消和 Replan 等控制事实；它以 Single Controller 维持计划因果，并在恢复时优先消费 Domain、Effect、Security、Knowledge 等 Owner 已经成立的更强事实。

**Current：** 完整三层运行图、不可变 PlanVersion、Replan Barrier、跨 Owner recovery、长期人工等待恢复和 Native Runtime 取舍属于 Target 设计。Current 代码中已有的 Agent、checkpoint、tool calling 或 runtime foundation 只能按 `docs/evidence/`、代码和测试实际证明的范围描述。

**Gap：** 仍需要长任务故障注入、Domain commit / Checkpoint crash-window、late-result acceptance、Controller 接管、真实等待恢复、预算收敛和 Generic Host 对照实验。没有这些证据时，不能把设计完整度写成恢复能力已经被生产验证。

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。
