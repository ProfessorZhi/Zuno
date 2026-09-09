# 04 Agent Runtime & Control（智能体运行与控制）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 长任务需要可恢复的控制平面

复杂法律任务可能包含材料检查、检索、专业分析、并行比较、人工等待、外部 Tool 和正式提交。真正困难的不是把这些步骤串起来一次跑通，而是在材料变化、权限变化、部分失败、进程重启和晚到结果同时存在时，仍然知道下一步应该做什么。

04 因此拥有运行控制，而不是所有业务事实。它负责一次 Run 的计划、Step、并行、等待、预算、取消、重规划和 Checkpoint；Domain、Knowledge、Security 和 Effect 仍由各自 Owner 决定更强事实。


最简单 Agent 可以不断把当前上下文交给模型，让模型决定下一步 Tool，直到输出 final answer。短任务和低风险实验完全可以这样实现。

长任务中，这种隐式控制状态很难回答：模型崩溃前已经决定了什么；两个并行 Specialist 的结果属于哪个计划版本；新证据进入后旧任务还能不能接受；外部动作 timeout 后该不该再次执行。把所有历史都塞进 message list，也无法自然得到稳定的并发和恢复语义。

### Single Controller 收敛控制权，三层 Graph 分离稳定拓扑与动态计划

Zuno Target 采用 `Single Controller`：只有一个控制面有权激活计划版本、接受 Step 结果、决定 Retry / Replan、管理 Budget 和发出 cancel。专业执行单元仍然可以并行，甚至可以由不同模型或 Capability 实现。

这样做不是否定 Multi-Agent，而是避免多个自治 Agent 同时修改全局计划。执行可以多写，控制必须单写，才能让计划演进和恢复拥有唯一因果顺序。


长期运行既需要一个稳定宿主生命周期，也需要任务级动态计划，还需要单个 Step 内稳定执行边界。Target 因此保持 `Fixed AgentRunGraph + dynamic Plan DAG + fixed StepExecutionGraph`。

外层 RunGraph 管启动、恢复、终止等稳定阶段；Plan DAG 表达某个任务当前真正的动态依赖；StepExecutionGraph 管一个 Step 内部的执行、验收和必要的模型 / Capability 调用。这样动态计划不会要求每次 Replan 都重建宿主拓扑。

### 不可变 PlanVersion 让并行、Join 与新鲜度共享控制基线

计划一旦开始派发，就已经有 Worker、模型和外部调用绑定到它。如果在原对象上修改 Step、参数或依赖，晚到结果会失去“我当时基于什么计划计算”的身份。

因此保持 `PlanVersion immutable after activation`。需要改变计划时创建新版本，并明确哪些旧工作可以继续、哪些结果必须重新验收。不可变版本保护的是因果，不是为了增加版本号。


一个 Step 是否能执行，不只取决于拓扑前驱结束。它还可能需要当前材料版本仍有效、Capability / Model 当前有资格、预算充足、权限仍允许，以及输入没有因为 Replan 变旧。

所以 Ready 判断本质上是多个 Owner facts 的组合。04 可以消费这些事实形成控制决定，却不能缓存一次 READY 后永久复用。


并行 Specialist 可以提高吞吐或覆盖，但不同分支可能失败、取消、晚到，甚至属于已经被替换的旧 Plan。Join 不能只数“收到几个结果”，还要确认每个结果是否属于当前 barrier、是否通过 Step acceptance、是否满足最小证据和质量要求。

因此并行是控制优化，不是业务真相。一个分支计算成功，如果输入版本或 Plan 已过期，仍然可能被拒绝或重新评估。


Runtime 可以验证 schema、Capability acceptance、模型结果和控制条件，但 Formal Admission-required Step 只有拿到 Domain 的匹配 Receipt 才能被视为正式业务提交完成。

这个边界避免 Checkpoint 抢走 Domain 权威。04 保存“我已经观察到并接受哪个 Owner fact”，而不是自己创造更强成功。

### Retry != Replan != Reconcile

Retry 适用于同一动作假设仍然成立，只是遇到暂时故障，例如模型 503。Replan 适用于计划假设已经失效，例如新材料改变依赖、Tool schema 更新或某条路线长期不可用。

Reconcile 解决的是过去现实动作结果未知，例如 POST 已经发出但 timeout。04 可以暂停等待 06 对账，却不能用 Replan 或 Retry 把未知现实效果覆盖掉。三种机制分开，控制面才能对失败做正确分类。


新 PlanVersion 产生以后，旧计划可能还有并行任务在运行。如果 Controller 一边接受旧结果一边按新计划派发，而没有稳定 barrier，就会产生“半个旧计划 + 半个新计划”的混合状态。

`Replan Barrier` 表达一个控制切换边界：哪些旧工作允许完成、哪些应取消、哪些 late result 需要重新验收，以及新计划从哪个因果点开始。它保护计划版本之间的可解释性，而不是要求停止所有在途工作。


旧 Plan 的纯计算结果如果输入版本仍然相同，也许仍有价值；如果材料、权限或业务预期已经变化，直接接受就会污染新计划。现实 Effect 更不能因为 branch stale 就被否认，因为远端动作可能已经发生。

所以 late result 需要按结果类型重新验收：纯计算检查 causation / freshness；正式 Domain 结果查询 Owner Receipt；现实 Effect 继续由 06 确认。是否“晚”只是时间事实，不自动决定业务资格。

### Checkpoint 记录控制进度，Owner Fact 决定恢复结果

Checkpoint 保存控制面为了恢复需要的 Run / Plan / Step 状态，使进程重启后不必从头重算。但它可以比 Domain、Effect 或 Security 的权威事实更旧。

恢复时先读取相应 Owner durable fact，再修复 Checkpoint projection。尤其 Domain commit 已成功但 Checkpoint 失败时，不能因为控制状态落后就重复正式提交。


人工等待可能持续数小时甚至数天。恢复时，原 Plan、材料、Capability 版本、SecurityEpoch 和 Approval 都可能变化。

因此 resume 不是“从暂停行下一行继续”。Controller 要重新判断仍然适用的条件；无效 Approval 重新申请，过期输入触发 Replan，需要正式提交的结果重新检查 expected DomainVersion。


如果进程崩溃，另一个 Worker 可能接管 Run。Lease / fencing 可以防止两个 Controller 同时写控制状态，但它不能证明某个 Tool Effect 没有发生，也不能替 Domain 判定正式事务。

这类机制应当保持窄：只保护 Runtime 控制面的单写者语义。跨 Owner 的业务完成仍依赖 Receipt、版本和对应恢复规则。


模型、检索和 Tool 重试都会消耗时间与资源。Budget 让 Controller 能决定继续、降级、Replan 或 abstain，而不是让每个 Provider 自己无限 fallback。

取消同样只停止未来还能安全停止的工作。已经提交的 Domain、已确认的 Effect 和已发生的模型 Usage 仍然是真实历史，Controller 不能通过把 Run 标成 CANCELLED 来改写它们。

### Runtime 优先复用框架，复杂度只在长任务约束出现时保留

LangGraph 等框架已经提供图执行、checkpoint、interrupt 等通用原语，Zuno 应优先复用。自定义层只应该承担通用框架不会替法律项目拥有的 PlanVersion、formal admission acceptance、Effect reconciliation 和安全新鲜度等专业语义。

如果 Generic Host + Zuno Legal Backend 已经能满足长期状态和恢复要求，Native Runtime 应缩小甚至退出主路径。自研 Runtime 的价值必须由复杂任务恢复、可控性或成本收益证明。


如果 Planner 一生成下一步就直接执行，模型决策和现实动作之间没有稳定验收点。Zuno 更倾向于让 Controller 先形成计划/Step 意图，再由执行层调用 Capability、Model 或 Tool，结果回到 Controller 验收。

这种分离允许在派发前检查 Budget、Security、Capability eligibility 和输入 freshness，也允许执行并行而控制单写。模型可以提出更聪明的计划，但不能跳过确定性的安全与业务门。

它还使记录更清楚：计划说明当时为什么要做，Attempt 说明实际做了什么，Acceptance 说明结果为什么被当前计划接纳。三者混在一个 message stream 中时，很难在故障后重建因果。


动态意味着计划在证据变化或失败时可以形成新版本，并不意味着每执行一个 Step 都必须调用 Planner。稳定任务完全可以一次生成 DAG 后按确定性调度；只有已知假设失效时才值得 Replan。

过度规划会增加 token、延迟和行为漂移，也会让简单失败被模型放大成新路线。Controller 应尽量用确定性规则处理 ready queue、join、retry budget 和明显错误，把 LLM Planner 留给真正需要语义重构的情况。

这让 Agentic 不等于不可预测：动态性集中在少数明确决策点，其余控制语义保持可测试。


DAG 中多个 Step ready 并不表示应该无限同时执行。模型配额、数据库连接、外部 Tool 限流和同一事项的并发业务约束都可能限制实际 dispatch。

Controller 可以按 task priority、budget 和 provider capacity 做调度，但不得为了吞吐改变依赖语义。需要相同 Domain snapshot 的多个分支在提交前仍要接受版本冲突检查；会产生同一现实 Effect 的分支更不能只靠队列并发限制保证幂等。

因此 scheduler 优化的是“何时执行已经合法的工作”，不负责重新定义“哪些工作彼此可以并发”。


通用 workflow replay 常假设节点是纯函数或安全幂等。Zuno 的 Step 可能已经提交 Domain 或越过外部 send boundary，盲 replay 会重复业务事实或副作用。

恢复时先按 Step 类型确认外部 durable owner fact：纯计算可以依 checkpoint / input 重算；正式提交先查 AdmissionReceipt；现实动作先查 Effect / Reconciliation；等待人工则重新检查 Approval 和 Security freshness。然后 Controller 才决定 projection 修复或继续运行。

这使 Checkpointer 从“唯一恢复真相”回到合适位置：它保存控制状态，但更强的业务事实优先。


如果任务没有动态依赖、长时间等待、正式 Domain commit 或现实副作用，一个普通同步 service / DAG engine 就可能足够。Native Runtime 不应因为已经存在就接管所有请求。

只有当 Replan、late result、multi-owner recovery、长任务 take-over 等机制在真实 task class 上频繁出现，并且通用 Host 很难以薄适配层满足时，Native Runtime 才值得保留完整复杂度。

这也是 04 最重要的删除条件：如果 B 方案——Generic Host + Zuno Legal Backend——已经提供同等正确性和更低维护成本，就应缩小 C 方案，而不是把“自研运行时”当项目身份的一部分。


长任务不一定一直有可执行 Step。关键材料未就绪、Approval pending、Effect outcome unknown、预算不足或人工 Review 都可能让 Run 暂时没有合法下一步。为了让 Dashboard 看起来有进展而强行 Replan 或继续调用模型，反而会绕过真实门禁。

因此 Controller 需要区分 deadlock / bug 和有明确 Owner 条件的合法等待。后者应该保存等待原因和唤醒条件，在对应事实变化后重新判断 freshness；前者才需要超时、告警或人工介入。

一个成熟 Runtime 的表现不是“永远在执行”，而是知道什么时候必须停止自动行动。


Planner 可以生成结构漂亮但实际上不可执行的 DAG：依赖循环、引用不存在的 Capability、预算明显超限、要求当前 Scope 不允许的材料，或者计划了无法安全恢复的 Effect。等运行到一半才发现这些问题，会放大成本和失败面。

因此计划进入 active 状态前，应该先做尽可能确定性的结构与可行性检查，再判断它是否真的比简单路线有用。模型可以负责提出语义方案，Controller / Capability / Security / Budget facts 负责证明当前世界允许它执行。

这不是要求构建万能静态证明器，而是把明显错误挡在派发前。越能在激活前确定的条件，越不应该留给运行中靠 Retry 猜。


即使单个 Run 内并行度受控，系统仍可能同时启动成千上万个复杂 Run，把 Checkpointer、模型 quota 和 Worker pool 压垮。入口 01 可以做产品级限流，04 仍需要知道自己当前能承载多少 active / waiting / runnable 工作。

运行时负载准入可以按 task class、priority、budget 和资源 profile 决定立即激活、排队或拒绝；已经激活的 Run 再由 scheduler 决定哪些 Ready Step 现在派发。两层分开，避免“每个 Run 都守规矩，但所有 Run 加起来把系统打满”。

具体 Queue / scheduler 可以复用成熟基础设施，04 自己需要保护的是控制语义和公平性，而不是自研通用集群调度器。


长 Run 可能产生大量尝试、模型输出和中间结果。如果为了恢复把所有历史都复制进每个 Checkpoint，状态会不断膨胀，恢复延迟和存储成本也会随运行时间增长。

Checkpoint 应保存继续控制所需的最小稳定状态和 Owner refs；不可变的 Domain / Effect / Usage / Audit 历史留在各自 Owner，诊断细节由 09 关联。必要时可以做 checkpoint compaction / snapshot，但不能因为压缩而丢掉 PlanVersion、causation 和尚未收敛的等待条件。

这让 Runtime state 保持“可继续执行”，而不是变成第二套业务历史数据库。

### 当前、目标与缺口

Current 是否已有完整 PlanVersion、parallel join、Replan Barrier、interrupt freshness、lease/fencing 和 crash recovery，需要回到代码与测试证据判断；文档中的 Target 不能当成实现清单。

Target 已明确 Single Controller、三层 Graph、不可变计划版本、Retry/Replan/Reconcile 分离和 Owner-fact-first recovery。Gap 仍包括字段级冻结、并行/晚到 fault injection、真实 Checkpointer 语义、Budget / takeover 测试，以及 Native Runtime 相对更简单 Host 方案是否有稳定收益。

---

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。
