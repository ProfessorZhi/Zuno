# Red Wave 1 — Questions Q1–Q100

```text
round: rb-2026-10-08-formal-021
role: Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师
stage: 技术一面 / 项目深挖，连续 30–60 分钟
threads: T01 Tool/MCP · T02 GraphRAG · T03 Memory/Context · T04 Runtime · T05 Security/Effect
         T06 Project History · T07 Pilot/法院 · T08 系统简化/Delete · T09 Knowledge/Retrieval · T10 工程基础
blind: true（仅读 frozen resume `01_simulated_resume.md` + pinned `attack-model.md`）
frozen_against_main: cdd2063b341e6919fafaa1395d1f3bdc837329f6
isolation: PHYSICAL_CONTEXT_ISOLATION
provenance: >
  Q1–Q50 与 Q51–Q100 由两个互不可见的隔离 Red 实例分别生成（各自只读冻结简历与 pinned attack-model），
  本文件仅为按序拼接，未做跨半批改写、未做统一措辞。
firewall_audit: 两个实例均报告「额外打开：无」——除冻结简历与 pinned attack-model 外未读任何仓库文件。
  该报告是自我申报，非沙箱验证；文件系统共享，见 `00_artifact_links.md`「隔离的诚实边界」。
batch_shape: |
  T01 14 · T02 12 · T03 10 · T04 7 · T05 7  = 50
  T06 9 · T07 8 · T08 9 · T09 12 · T10 12   = 50
depth_shape: L1 10 · L2 35 · L3 55（合计 100）
```

## T01 — Tool / MCP

**Q1.** 简历里说「重构单 Agent Tool Calling 与 Workspace 路由」，这次重构中你亲手写的是哪一段，重构之前那块是谁写的、长什么样？
> `intent`: 个人 Ownership 与 before 状态 ｜ `callback`: — ｜ `depth`: L1

**Q2.** 重构之前 MCP Tool 经子 Agent 转发具体是几层调用，每一层各自负责什么？
> `intent`: 原架构的可复现性 ｜ `callback`: Q1 ｜ `depth`: L1

**Q3.** 「用户配置跨层传递」失败时你实际看到的 bad case 是什么，是报错、静默丢配置，还是把 A 用户的配置传给了 B？
> `intent`: 原问题是否真实存在 ｜ `callback`: Q2 ｜ `depth`: L2

**Q4.** 你按 Tool–Server 映射注入用户级配置，这个注入到底发生在哪一层，是构造 tool schema 时，还是真正发起 MCP 调用时？
> `intent`: 注入点机制 ｜ `callback`: Q3 ｜ `depth`: L2

**Q5.** 两个用户同时调用同一个 MCP Server 的同一个 Tool，配置会不会串，你靠什么结构保证不串？
> `intent`: 并发隔离 ｜ `callback`: Q4 ｜ `depth`: L2

**Q6.** 如果配置是放在进程内的共享变量里，Python 里你具体用什么把它绑定到单次请求，为什么不是全局 dict 加锁？
> `intent`: Project → Fundamental Bridge（ContextVar / request-local） ｜ `callback`: Q5 ｜ `depth`: L2

**Q7.** 为什么不是修原来那条配置透传路径让子 Agent 正确转发，而是要把 Tool 直接提到主 Agent 上？
> `intent`: Subtraction Test ｜ `callback`: Q4 ｜ `depth`: L3

**Q8.** direct route 与 ReAct 路径的分流判据具体是什么，「目标与参数明确」由谁来判定，规则、模型还是两者结合？
> `intent`: 路由准入机制 ｜ `callback`: — ｜ `depth`: L2

**Q9.** 回归测试里「自定义 MCP 名称递归」这条断言到底固定了什么行为，不写它最容易漏掉哪种回归？
> `intent`: Evidence Escalation（测试粒度） ｜ `callback`: Q8 ｜ `depth`: L2

**Q10.** ReAct 一侧为什么暂时没有回归断言，补它的代价是什么，你打算什么时候补？
> `intent`: 证据缺口与计划 ｜ `callback`: Q9 ｜ `depth`: L2

**Q11.** 一个 MCP Tool 调用超时之后，你怎么判断远端到底执行了没有？
> `intent`: timeout 语义 ｜ `callback`: — ｜ `depth`: L3

**Q12.** 一个有副作用的 Tool 调用超时后你重试，远端被调用了两次，你靠什么把它收敛成幂等？
> `intent`: idempotency ｜ `callback`: Q11 ｜ `depth`: L3

**Q13.** 本地判定超时、但远端其实已经执行成功时，你的 Agent 状态和远端 effect 哪个算真值，谁来收敛这个分歧？
> `intent`: remote effect 归属 ｜ `callback`: Q11 ｜ `depth`: L3

**Q14.** 为什么不直接用一个现成的 MCP Host 或 Gateway，而是自研这层配置注入与准入，Zuno 真正补的 Delta 是什么？
> `intent`: Build / Buy ｜ `callback`: Q4 ｜ `depth`: L3

## T02 — GraphRAG

**Q15.** 你发现 graph candidates 把 `Ed Wood`、`Shirley Temple` 挤出 top5，当时那条 query 的候选集里 vector、BM25、graph 三路各自的 rank 分别是什么？
> `intent`: bad case 的可复核细节 ｜ `callback`: — ｜ `depth`: L1

**Q16.** 这个排序回退是你自己跑 smoke 发现的，还是别人反馈给你、你只负责修的？
> `intent`: Ownership Interrupt ｜ `callback`: Q15 ｜ `depth`: L1

**Q17.** baseline-preserving fusion 里「保留 Vector/BM25 原始 rank」具体怎么实现，是在融合分数里加权，还是把原始 rank 当成不可被挤出的下限？
> `intent`: 修复机制 ｜ `callback`: Q15 ｜ `depth`: L2

**Q18.** 「按图证据强度分层晋升候选」的分层门槛是怎么定的，为什么是这些档位而不是连续加权？
> `intent`: threshold 来源 ｜ `callback`: Q17 ｜ `depth`: L2

**Q19.** 这 5 条 smoke query 具体是什么类型，baseline 是在同一天、同一模型、同一 `limit=5`、同一索引下跑的吗？
> `intent`: 实验同条件性 ｜ `callback`: Q15 ｜ `depth`: L3

**Q20.** 「不再低于 baseline」用的是哪个 metric，是 Recall@5、命中率还是别的，这个数是谁算的？
> `intent`: Evidence Escalation（指标定义与来源） ｜ `callback`: Q19 ｜ `depth`: L3

**Q21.** 5 条样本只能证明一次修复，独立 holdout 为什么还没跑，跑它需要什么代价？
> `intent`: 证据强度边界 ｜ `callback`: Q20 ｜ `depth`: L3

**Q22.** 如果做 leave-one-out ablation，把 candidate-aware seed expansion、别名归一化、path-aware ranking 逐个删掉，你预期哪个会让指标掉得最多？
> `intent`: 复杂度举证 / 机制归因 ｜ `callback`: — ｜ `depth`: L3

**Q23.** candidate-aware seed expansion 具体怎么选 seed，实体别名归一化用的是字典、规则还是模型？
> `intent`: 实现细节 ｜ `callback`: — ｜ `depth`: L2

**Q24.** 在中文法律实体上做别名归一化最容易出的错是什么，会不会把「子公司与母公司」这类不同实体误合并？
> `intent`: 机制在真实域上的失效 ｜ `callback`: Q23 ｜ `depth`: L3

**Q25.** 多跳图检索这一套给一次查询增加了多少额外延迟与 token 成本，你实测过吗？
> `intent`: latency / cost 代价 ｜ `callback`: Q22 ｜ `depth`: L3

**Q26.** 出现什么结果时你会判定 GraphRAG 这一层不该继续保留，把它降回普通向量检索？
> `intent`: kill condition ｜ `callback`: Q22 ｜ `depth`: L3

## T03 — Memory / Context

**Q27.** 如果没有 Context/Memory 这一层，Agent 直接拼 prompt 会在哪个具体场景上失败？
> `intent`: 必要性 ｜ `callback`: — ｜ `depth`: L1

**Q28.** Scoped Context/Memory V2 里的 V1 原来是什么样，从 V1 到 V2 你自己改了哪部分？
> `intent`: Ownership / before-after ｜ `callback`: Q27 ｜ `depth`: L1

**Q29.** 这条 scope 约束用普通的 `where user_id = ? and project_id = ?` 为什么不够，多出来的 scope 语义到底是什么？
> `intent`: Subtraction Test ｜ `callback`: Q28 ｜ `depth`: L2

**Q30.** 一条 memory 由谁写入，写入权在 Agent 手里还是有一个独立入口，谁拥有这个入口？
> `intent`: record owner ｜ `callback`: Q29 ｜ `depth`: L2

**Q31.** 谁拥有「这条 memory 可以被读回 Agent」的最终判断权，是写入方、检索层还是审核流程？
> `intent`: recall authority ｜ `callback`: Q30 ｜ `depth`: L3

**Q32.** 一条审核通过的 memory 后来被撤回，已经写入的历史回合怎么让它不再被读回？
> `intent`: revocation ｜ `callback`: Q31 ｜ `depth`: L3

**Q33.** 同 scope 的 task summary 已经过期但状态还没刷新，你怎么避免把 stale 内容注入到调用前读取路径？
> `intent`: stale memory ｜ `callback`: Q31 ｜ `depth`: L3

**Q34.** 同一 Domain 里两条互相冲突的 structured memory 同时存在时谁赢，靠什么仲裁，会不会退化成并发写覆盖？
> `intent`: Domain conflict（桥接事务隔离 / CAS） ｜ `callback`: Q33 ｜ `depth`: L3

**Q35.** 你怎么证明加了 scoped Memory 比不加更好，有没有做过 A/B 或者至少一个可复现的对照 case？
> `intent`: A/B 证据 ｜ `callback`: Q33 ｜ `depth`: L3

**Q36.** 出现什么条件时你会把 Memory 这一层整个删掉，只留 Context 组装？
> `intent`: Delete condition ｜ `callback`: Q35 ｜ `depth`: L3

## T04 — Runtime

**Q37.** 固定 workflow 在哪一类请求上会失效，能不能给一个让固定流程明确不够用的 case？
> `intent`: 必要性 ｜ `callback`: — ｜ `depth`: L2

**Q38.** 一个 PlanVersion 里到底冻结了什么，是工具集、prompt、模型版本，还是连路由规则一起冻结？
> `intent`: 状态对象定义 ｜ `callback`: Q37 ｜ `depth`: L2

**Q39.** 一个旧 PlanVersion 的执行结果在新版本已经生效之后才返回，你会丢弃、合并还是照常提交？
> `intent`: late result ｜ `callback`: Q38 ｜ `depth`: L3

**Q40.** checkpoint 已经 stale 的情况下提交 Domain 变更会发生什么，你怎么检测到它是 stale 的？
> `intent`: Domain commit / stale checkpoint ｜ `callback`: Q39 ｜ `depth`: L3

**Q41.** 崩溃恢复之后谁拥有「从哪一步继续」的最终判断权，是 checkpoint、Runtime 还是 Domain 侧？
> `intent`: recovery authority ｜ `callback`: Q40 ｜ `depth`: L3

**Q42.** LangGraph 自带 checkpointer 和 interrupt，为什么还不够，纯 LangGraph 在哪一步明确做不到？
> `intent`: Build / Buy ｜ `callback`: Q41 ｜ `depth`: L3

**Q43.** 如果 LangGraph 以后补齐了你现在自研的这部分，这一层什么时候可以删掉，删除判据是什么？
> `intent`: Delete condition ｜ `callback`: Q42 ｜ `depth`: L3

## T05 — Security / Effect

**Q44.** 授权在计划生成之后、effect 执行之前发生了变化，你是在哪一刻重新校验的，还是根本不再校验？
> `intent`: authorization freshness ｜ `callback`: — ｜ `depth`: L3

**Q45.** 一次 effect「现在仍然被授权」的最终判断权在谁手里，是 Runtime、Domain 还是下游 Tool 自己？
> `intent`: Authority 归属 ｜ `callback`: Q44 ｜ `depth`: L3

**Q46.** 审计记录是在 effect 之前写还是之后写，你怎么保证这个次序在崩溃时不被打乱？
> `intent`: audit-before-effect ｜ `callback`: Q44 ｜ `depth`: L3

**Q47.** 审计已经落盘但 effect 还没发生（或者反过来）的那段窗口里系统状态是什么，谁负责收敛？
> `intent`: crash window ｜ `callback`: Q46 ｜ `depth`: L3

**Q48.** effect 执行结果未知时，你的系统对外呈现的是什么状态，能不能继续走下一步？
> `intent`: unknown effect ｜ `callback`: Q47 ｜ `depth`: L3

**Q49.** 对账由谁做、多久做一次，对不上的时候是自动修复还是必须人工介入？
> `intent`: reconciliation ｜ `callback`: Q48 ｜ `depth`: L3

**Q50.** 远端真实世界已经变化、本地记录还是旧的，这种情况下谁是真值，你的系统怎么发现自己在骗自己？
> `intent`: external reality ｜ `callback`: Q49 ｜ `depth`: L3

## T06 — Project History

**Q51.** 你 2026.03 加入 Zuno 时，这条 Agent 链路已经存在多少——是接近空仓库起步，还是已经有一个能跑通 Tool Calling 的版本？
> `intent`: before-state 归属 ｜ `callback`: — ｜ `depth`: L1

**Q52.** 你加入后写的第一笔、能明确算作你个人而非团队的改动，具体改了哪个文件或哪段逻辑？
> `intent`: 个人第一笔改动 ｜ `callback`: Q51 ｜ `depth`: L1

**Q53.** 简历说「重构单 Agent Tool Calling」，这个重构之前的实现是谁写的，为什么需要你来重构而不是原作者继续做？
> `intent`: 改动动因与 ownership ｜ `callback`: Q52 ｜ `depth`: L2

**Q54.** 现在系统里 LangGraph 的图结构、MCP Server 接入、PostgreSQL schema，哪几部分是你亲手写的，哪几部分是团队已有、你只做扩展的？
> `intent`: 个人 vs 团队模块切分 ｜ `callback`: — ｜ `depth`: L1

**Q55.** 简历里的 ContextOrchestrator，是代码里真实存在的组件，还是你为了描述这轮工作归纳出来的名字？
> `intent`: 抽象是否真实落地 ｜ `callback`: — ｜ `depth`: L2

**Q56.** 你说的 direct route 与 ReAct 的分流规则，是产品、Leader 定的，还是你自己拍的；这条边界由谁拥有最终解释权？
> `intent`: 决策 Authority 归属 ｜ `callback`: Q53 ｜ `depth`: L2

**Q57.** 你写的那批回归测试，是在你改动之前就已有 CI 在跑，还是这轮才第一次被接进流水线？
> `intent`: 测试基建归属 ｜ `callback`: Q52 ｜ `depth`: L2

**Q58.** 如果我现在打开提交历史，哪一个 diff 最能代表你这段工作——它是一个独立 PR，还是一次混在一起的大重构？
> `intent`: Evidence Escalation 到 diff 粒度 ｜ `callback`: Q52 ｜ `depth`: L2

**Q59.** 简历里的「法院侧测试」和「Pilot Validation」，你本人具体参与到哪一层——写代码、配环境，还是现场看别人跑？
> `intent`: Ownership Interrupt，定性个人参与深度 ｜ `callback`: — ｜ `depth`: L1

## T07 — Pilot / 法院

**Q60.** 你说的 Pilot Validation，具体是法院的人拿真实案子在用，还是你们演示、他们在旁边看？
> `intent`: Pilot 的定义 ｜ `callback`: Q59 ｜ `depth`: L2

**Q61.** 这次 Pilot 一共跑了多少条 case、持续多少天，有没有留下可复核的记录，比如日志、表格或邮件？
> `intent`: Evidence Escalation 到样本与记录 ｜ `callback`: Q60 ｜ `depth`: L2

**Q62.** 简历只写到「内部 Demo、法院侧测试与 Pilot Validation」，是谁、基于什么把边界定在这里而不写 Production？
> `intent`: 边界的来源与定性 ｜ `callback`: Q60 ｜ `depth`: L3

**Q63.** 法院侧测试里有没有出现过一次你以为对、当场却跑错的情况，那次具体错在哪？
> `intent`: bad case 真实性 ｜ `callback`: Q61 ｜ `depth`: L3

**Q64.** 这次 Pilot 有没有一个明确的通过/不通过判据，还是跑完就算完成；如果有判据，是谁定的？
> `intent`: Pilot 退出条件 ｜ `callback`: Q61 ｜ `depth`: L3

**Q65.** 如果 Pilot 做完了却没有进 Production，卡点是模型质量、合规、法院内部流程，还是根本没人接手？
> `intent`: 未落地的真实原因 ｜ `callback`: Q62 ｜ `depth`: L3

**Q66.** 到今天为止，这套东西还在法院环境里跑着吗，还是已经停机或回滚了？
> `intent`: 当前真实状态 ｜ `callback`: Q65 ｜ `depth`: L2

**Q67.** 换一类真实卷宗（不是 HotpotQA 那种问答），你这套 GraphRAG 检索还能用吗——你测过没有？
> `intent`: 泛化证据缺口 ｜ `callback`: Q64 ｜ `depth`: L3

## T08 — 系统简化 / Delete

**Q68.** 如果今天从零重做，GraphRAG 这整层你会第一个删掉吗；删掉之后哪个具体 query 会明确变差？
> `intent`: Subtraction Test 打 GraphRAG ｜ `callback`: Q67 ｜ `depth`: L3

**Q69.** baseline-preserving fusion 只是把 vector/BM25 的原始 rank 保留下来，那为什么不直接把图权重调到 0，而要写这层 fusion？
> `intent`: 更简单方案为何不够 ｜ `callback`: Q68 ｜ `depth`: L2

**Q70.** Memory V2 这层如果只用「按 user_id + project_id 加 where 条件查一张表」，哪个场景会失败到必须上 scope 抽象？
> `intent`: Subtraction Test 打 Memory ｜ `callback`: — ｜ `depth`: L3

**Q71.** ContextOrchestrator 作为统一入口，它多出来的这层抽象今天带来了什么；删掉它、直接调底层组装函数会损失什么？
> `intent`: 抽象层举证 ｜ `callback`: Q55 ｜ `depth`: L3

**Q72.** 你新建的 typed contracts 和 scope 约束，LangGraph 自带的 state/channel 或一个普通 Pydantic model 是不是就够了？
> `intent`: Build vs Extend 框架能力 ｜ `callback`: Q70 ｜ `depth`: L2

**Q73.** candidate-aware seed expansion、别名归一化、path-aware ranking 这三个机制里，哪个是你今天看来收益最不确定、最该删的？
> `intent`: 三机制中挑最弱 ｜ `callback`: Q68 ｜ `depth`: L2

**Q74.** 如果只能把一个机制留到下一个 round，你留哪个，删掉另两个的代价分别是什么？
> `intent`: 减法优先级 ｜ `callback`: Q73 ｜ `depth`: L3

**Q75.** 你们自研的这套 Tool 准入与配置注入，如果换成成熟的 MCP Host 或框架自带 gateway，真正非你做不可的 delta 是什么？
> `intent`: Build/Buy 真实 delta ｜ `callback`: Q70 ｜ `depth`: L3

**Q76.** 记忆 readback 上这层 review/provenance 约束，什么条件满足时你会把它整个删掉、回退到最朴素的写入？
> `intent`: 删除条件 ｜ `callback`: Q75 ｜ `depth`: L3

## T09 — Knowledge / Retrieval 基础

**Q77.** 一份文档更新之后，你靠什么判断检索侧已经切到新版本，而不是还在用旧的 embedding？
> `intent`: DocumentVersion 与失效 ｜ `callback`: — ｜ `depth`: L2

**Q78.** 你简历里的 KnowledgeGeneration，在代码里对应的是什么——一个版本号、一张表，还是一个状态机？
> `intent`: 概念能否落地 ｜ `callback`: Q77 ｜ `depth`: L2

**Q79.** 如果一份文档被删了，指向它的 Citation 应该变成什么，你系统里有没有一条路径会因此读到悬空引用？
> `intent`: 引用完整性 ｜ `callback`: Q77 ｜ `depth`: L3

**Q80.** Readiness——你怎么知道一条知识已经可以被检索、而不是还在索引中；这个门是阻塞读还是最终一致？
> `intent`: readiness 语义 ｜ `callback`: Q78 ｜ `depth`: L3

**Q81.** Citation 里你存的是文档 ID、chunk ID 还是精确到字符区间；如果原文被改了，引用还指得准吗？
> `intent`: Citation 粒度与漂移 ｜ `callback`: Q79 ｜ `depth`: L2

**Q82.** 如果用户问的东西「全案都没有」，你怎么向用户证明是真的没有，而不是你根本没检索到？
> `intent`: 「全案没有」如何证明 ｜ `callback`: Q81 ｜ `depth`: L3

**Q83.** 你的检索 Top-K 里这个 5 是怎么定的——固定值还是按 query 类型变，为什么偏偏是 5？
> `intent`: Evidence Escalation 到 K 的来源 ｜ `callback`: — ｜ `depth`: L2

**Q84.** HotpotQA 那 5 个 query 的 smoke，baseline 和你 graph 版是不是同一批次、同一参数、同一天跑的？
> `intent`: baseline 是否同条件 ｜ `callback`: Q83 ｜ `depth`: L2

**Q85.** 「不再低于 baseline」是 5 条里持平还是反超；如果只是持平，你怎么区分是 fusion 在起作用还是噪声？
> `intent`: 结果强度核实 ｜ `callback`: Q84 ｜ `depth`: L3

**Q86.** 你自己说 holdout 和 leave-one-out ablation 都还没做，那你现在凭什么保留这三个多跳机制而不是先 Defer 掉？
> `intent`: 无 ablation 下的保留理由 ｜ `callback`: Q85 ｜ `depth`: L3

**Q87.** 实体别名归一化如果不做，具体哪一类跨文档的多跳问题会失败；这种 bad case 你真见过，还是推演出来的？
> `intent`: 机制必要性的 bad case ｜ `callback`: Q73 ｜ `depth`: L2

**Q88.** path-aware ranking 里的「path 证据强度」是怎么算出来的——一个分数、一条规则，还是让模型打的；这个打分本身你怎么验证？
> `intent`: 算法核心可落地性 ｜ `callback`: Q81 ｜ `depth`: L3

## T10 — 工程基础

**Q89.** 你把用户级配置注入主 Agent 的调用，如果同一进程里两个用户并发请求，这两份配置会不会串？
> `intent`: per-request state 隔离 ｜ `callback`: Q75 ｜ `depth`: L2

**Q90.** Python 里你用什么把「用户级配置」绑到当前这次调用——函数参数、ContextVar，还是线程/协程本地；为什么选它？
> `intent`: ContextVar / 协程上下文传播 ｜ `callback`: Q89 ｜ `depth`: L2

**Q91.** 如果 MCP Tool 调用走了 asyncio.gather 并发，其中一个超时你 cancel 了本地 coroutine，远端那个 Tool 会不会还在跑？
> `intent`: cancellation 是否等于远端终止 ｜ `callback`: Q89 ｜ `depth`: L3

**Q92.** 一个 MCP Tool 请求 timeout 了，你在客户端怎么区分「远端没执行」和「执行了但结果没回来」这两种情况？
> `intent`: timeout 的语义模糊 ｜ `callback`: Q91 ｜ `depth`: L3

**Q93.** 既然这两种情况分不清，你的 Tool 调用有没有做 idempotency key 或去重，防止 retry 造成重复副作用？
> `intent`: retry 幂等 ｜ `callback`: Q92 ｜ `depth`: L3

**Q94.** Memory 回合后写入，如果两个请求同时写同一个 scope，你用的是 PostgreSQL 什么隔离级别，有没有上乐观锁或 SELECT FOR UPDATE？
> `intent`: 并发写 lost update ｜ `callback`: Q90 ｜ `depth`: L3

**Q95.** 你会不会拿着数据库行锁去等模型调用返回；如果会，为什么这是问题？
> `intent`: 长事务反模式 ｜ `callback`: Q94 ｜ `depth`: L3

**Q96.** 记忆读回里「审核通过的 structured memory」这个审核状态，是数据库里的一列还是应用层判断；并发下 review 刚通过、读回却读到旧状态，你怎么防？
> `intent`: TOCTOU / 状态一致性 ｜ `callback`: Q94 ｜ `depth`: L3

**Q97.** 你保留 Vector/BM25 原始 rank 做融合，用的是哪种融合——RRF、加权和，还是先加权再重排；为什么不直接用 RRF？
> `intent`: IR 融合基础 ｜ `callback`: Q69 ｜ `depth`: L2

**Q98.** 你说的「按图证据强度分层晋升」，是硬覆盖原 rank 还是只做 tie-break；它和 RRF 的 rank 融合在本质上冲突在哪？
> `intent`: 排序算法冲突 ｜ `callback`: Q97 ｜ `depth`: L3

**Q99.** 你们的向量检索是精确 KNN 还是 ANN；如果是 ANN，limit=5 这种小 K 下的 recall 损失你靠什么衡量？
> `intent`: ANN vs exact 的 recall 代价 ｜ `callback`: Q83 ｜ `depth`: L2

**Q100.** 最后一个根本问题：这套系统里「这条记忆/这个引用是可信的」最终由谁判断——模型、review 流程，还是数据库约束；三者冲突时听谁的？
> `intent`: Authority 归属总收口 ｜ `callback`: Q96 ｜ `depth`: L3
