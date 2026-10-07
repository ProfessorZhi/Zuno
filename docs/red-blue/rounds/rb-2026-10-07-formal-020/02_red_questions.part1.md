# Red Wave 1 — Questions Q1–Q50

```text
round: rb-2026-10-07-formal-020
role: Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师
stage: 技术一面 / 项目深挖
threads: T01 Tool/MCP · T02 GraphRAG · T03 Memory/Context · T04 Runtime · T05 Security/Effect
blind: true（仅读 frozen resume + attack-model）
```

## T01 — Tool / MCP

**Q1.** 你说你「重构」了单 Agent 的 Tool Calling —— 在你这笔改动之前，一个 MCP Tool 从主 Agent 走到真正被调用，中间要经过哪些步骤？你亲手改的是其中哪一段？
> `intent`: 接手前状态与个人改动边界 ｜ `callback`: — ｜ `depth`: L1

**Q2.** 「将具体 MCP Tools 直接绑定主 Agent」—— 这个绑定是在进程启动时静态注册一次，还是每个会话、每次请求动态装载？「主 Agent 能用哪些 Tool」这张表由谁持有，放在哪里？
> `intent`: 绑定时机与这张表的持有者 ｜ `callback`: — ｜ `depth`: L1

**Q3.** 原来 MCP Tool 要经子 Agent 转发，最直接的原因是什么？如果反过来，把用户配置沿着调用链一层层往下传（不要子 Agent 这一层），会在哪个具体场景下坏掉？
> `intent`: 原设计动因与最简单替代的失效点 ｜ `callback`: — ｜ `depth`: L1

**Q4.** 回看 Q2 的那张表：你说「按 Tool–Server 映射注入用户级配置」—— 这张映射的 key 和 value 分别是什么类型？它是代码里的常量、一份配置文件，还是运行时可变的注册表？谁有权改它？
> `intent`: 映射表的数据结构与所有权 ｜ `callback`: Q2 ｜ `depth`: L2

**Q5.** 基于 Q4 的注入方式：同一个进程里两个用户并发调用同一个 MCP Tool，注入的配置会不会串？你是靠什么让配置跟着请求走、而不是跟着进程走的？
> `intent`: 请求级配置隔离机制（并发） ｜ `callback`: Q4 ｜ `depth`: L2

**Q6.** 主 Agent 直连 MCP Tool 之后，超时设在那一层 —— MCP client、HTTP 层，还是 Agent 循环本身？超时发生的那一刻，主 Agent 拿到的返回值是什么，它据此怎么继续？
> `intent`: timeout 的层级与超时语义 ｜ `callback`: — ｜ `depth`: L2

**Q7.** 接着 Q6 的超时处理：如果一个带副作用的 MCP Tool 超时了，你会不会重试？在决定重试之前，你先靠什么判断它上一次到底执行没执行？
> `intent`: 重试的前提与幂等判据 ｜ `callback`: Q6 ｜ `depth`: L2

**Q8.** 回看 Q3 里被砍掉的子 Agent 层：你说「目标与参数明确的一步请求走 direct route，复杂或参数不完整回落 ReAct」—— 这个判定写在哪儿、由规则还是模型做？「自定义 MCP 名称递归」那类 case 是在哪一步被判错的？
> `intent`: 路由判定的归属与回归边界 ｜ `callback`: Q3 ｜ `depth`: L2

**Q9.** 承 Q7：连接被切断、而你又无法确认远端是否已经执行 —— 这一刻，谁拥有「这次调用到底发生没发生」的最终判断权？系统接下来做什么动作？
> `intent`: unknown effect 的裁决权归属 ｜ `callback`: Q7 ｜ `depth`: L3

**Q10.** 一个成熟的 MCP Host / Gateway 已经能做 Tool 注册、配置注入和超时管理。回看 Q4 那张映射表：你们自研这一层补的 delta 具体是哪一个业务语义？如果这个 delta 哪天真被框架原生覆盖，你删掉自研层的条件是什么？
> `intent`: 自研 vs 成熟 Host 的 delta 与退出条件 ｜ `callback`: Q4 ｜ `depth`: L3

## T02 — GraphRAG

**Q11.** 你说 graph candidates 会把 baseline 已命中的文档挤出 Top-K —— 具体是哪一条 query、被挤出的是哪一篇文档？这个问题是你自己发现的，还是别人定位好了交给你的？
> `intent`: bad case 的具体度与发现归属 ｜ `callback`: — ｜ `depth`: L1

**Q12.** 你说的「baseline 已命中」—— 判定一条 query 命中的口径是什么？Recall@K、MRR，还是别的？这个口径是谁定的？
> `intent`: baseline 的评测口径（IR 基础） ｜ `callback`: — ｜ `depth`: L1

**Q13.** 如果不上 GraphRAG，只用 Vector + BM25，具体是**哪一类** query 会答错？能不能举一个真实用户场景的例子？
> `intent`: 图检索的必要性 ｜ `callback`: — ｜ `depth`: L1

**Q14.** 你在 Q12 给了「命中」的口径 —— 那 baseline-preserving fusion 里「保留 Vector/BM25 原始 rank」具体怎么保留？原始 rank 存在哪个结构里，最终顺序是两路分数相加，还是按名次重排？
> `intent`: fusion 的数据结构与排序算法 ｜ `callback`: Q12 ｜ `depth`: L2

**Q15.** 承接 Q14 的排序结果：「按图证据强度分层晋升候选」—— 图证据强度是一个可比大小的标量吗？怎么算出来的？分成几层？晋升是把候选直接提到最前，还是给它一个能被其他信号反超的位次？
> `intent`: 证据强度的量化与晋升方式 ｜ `callback`: Q14 ｜ `depth`: L2

**Q16.** 这层晋升的 threshold / 分层边界一共几个数？它们是怎么被定下来的 —— 扫参、经验值，还是从数据里统计出来的？
> `intent`: threshold 取值的依据来源 ｜ `callback`: — ｜ `depth`: L2

**Q17.** 你说 5-query smoke 修复后恢复到 baseline 水平 —— 这 5 条 query 是怎么挑的？它能证明什么，又不能证明什么？
> `intent`: smoke 证据的边界 ｜ `callback`: Q11 ｜ `depth`: L2

**Q18.** 承 Q13 说的那类 query：有没有在 holdout 上跑过？有没有做过关掉单个组件（比如只关掉 path-aware ranking）的 ablation？换一类 query 分布，收益还在吗？
> `intent`: holdout / ablation 是否存在 ｜ `callback`: Q13 ｜ `depth`: L2

**Q19.** 接着 Q18 的扩大范围：加了图候选之后，一次检索多出的延迟和成本，这个账是怎么算的？依据是压测、线上日志，还是估算？
> `intent`: latency / cost 的证据来源 ｜ `callback`: Q18 ｜ `depth`: L3

**Q20.** 什么条件下你会把 GraphRAG 整条链路关掉或降级为可选？触发这个决定的观测信号具体是什么？
> `intent`: GraphRAG 的退出条件 ｜ `callback`: Q19 ｜ `depth`: L3

## T03 — Memory / Context

**Q21.** 在 Context/Memory V2 之前，Agent 跨回合是靠什么记住上下文的？「需要一个统一入口按作用域组装上下文」这个需求是谁提的 —— 你、团队，还是业务侧？
> `intent`: Memory 的必要性与需求归属 ｜ `callback`: — ｜ `depth`: L1

**Q22.** scope 的粒度到底是什么 —— user、project、task，还是它们的组合？这个粒度是谁定义的，写在代码的哪里？
> `intent`: scope 的定义与层级 ｜ `callback`: — ｜ `depth`: L1

**Q23.** 「回合后写入」写进去的具体是什么 —— 原始对话、task summary，还是结构化 memory？是谁触发这次写入的？
> `intent`: 写入的内容形态与触发者 ｜ `callback`: — ｜ `depth`: L1

**Q24.** 回看 Q23 写进去的东西：prepare_context() 从哪里把它们读出来？「仅注入同 scope 的 task summary 与审核通过的 structured memory」这个过滤，发生在读取的那一层 —— SQL 的 where、应用层过滤，还是两者都有？
> `intent`: 读取入口与过滤位置 ｜ `callback`: Q23 ｜ `depth`: L2

**Q25.** 承 Q22 的 scope 定义：「同 scope」是否足以防止越权读取？如果两个案件共用同一个 user scope，一个案件的 memory 会不会被另一个案件读到？
> `intent`: scope 作为授权边界的充分性 ｜ `callback`: Q22 ｜ `depth`: L2

**Q26.** 一条 memory 被撤销或标记为无效之后，它此前已经进入过的对话上下文怎么办？已经由它产生的下游结论要不要回滚？
> `intent`: 撤销后已生效记忆的处理 ｜ `callback`: — ｜ `depth`: L2

**Q27.** 承 Q26 的撤销场景：一条旧的 task summary 和最新回合的事实冲突时，读取的时候怎么判断谁更新？有没有时间戳或版本号在比？
> `intent`: stale memory 的判定依据 ｜ `callback`: Q26 ｜ `depth`: L2

**Q28.** 接着 Q27 的冲突：如果 memory 里说「用户要 A」，而 Domain 状态说「当前是 B」，Agent 下一步该信哪个？谁拥有这个冲突的裁决权？
> `intent`: memory 与 Domain 状态冲突时的权威 ｜ `callback`: Q27 ｜ `depth`: L2

**Q29.** 承 Q21 说的那个需求：typed contracts 加 scope 约束这一整套，带来的收益有没有做过对照实验？如果没有 A/B，你拿什么说服别人这层复杂度值得留？
> `intent`: 复杂度收益的证据 ｜ `callback`: Q21 ｜ `depth`: L3

**Q30.** 什么条件下你会把整个 Memory / ContextOrchestrator 这一层删掉，退回每回合拼 prompt？
> `intent`: Memory 层的退出条件 ｜ `callback`: Q29 ｜ `depth`: L3

## T04 — Runtime

**Q31.** 固定 workflow 在你们场景里具体是怎么坏掉的 —— 有没有一次真实的 case，让团队决定必须引入一个「能改计划」的 Runtime？
> `intent`: 固定 workflow 的失效点 ｜ `callback`: — ｜ `depth`: L1

**Q32.** 从用户输入到 Domain 提交，现在这条链上依次经过哪些状态对象？每一步谁写、谁读？
> `intent`: Runtime 调用链与状态对象 ｜ `callback`: — ｜ `depth`: L1

**Q33.** 「当前计划」这份状态由谁拥有、存在哪里 —— 进程内存、DB 表，还是 LangGraph 的 checkpoint？
> `intent`: 计划状态的持有者与存放介质 ｜ `callback`: — ｜ `depth`: L1

**Q34.** 回看 Q33 里那份计划状态：在你们引入计划版本之前，系统只有一个「当前计划」—— 当时你们靠什么判断一个动作是旧计划留下的？那时没有版本号，用的什么信号兜底，这个兜底在哪类情况下会漏？
> `intent`: 版本机制引入前的替代手段与当时风险 ｜ `callback`: Q33 ｜ `depth`: L2

**Q35.** 承 Q34 的旧计划问题：一个属于旧版本的 Tool 结果晚到了，系统怎么保证它不被当成当前计划的产物使用？这个判断发生在结果回来的那一刻，还是提交的那一刻？
> `intent`: late result 的丢弃判定时机 ｜ `callback`: Q34 ｜ `depth`: L2

**Q36.** 承 Q32 的那条链：Domain 状态的提交，和 checkpoint 的写入，是同一个事务吗？如果不是，中间崩了会不会出现「domain 改了但 checkpoint 没改」？
> `intent`: 提交与 checkpoint 的一致性与原子性（DB 基础） ｜ `callback`: Q32 ｜ `depth`: L2

**Q37.** 承 Q36 的不一致：从 checkpoint 恢复时，如果 checkpoint 落后于 Domain 当前状态，恢复逻辑以谁为准？这次恢复是否可接受，由谁决定？
> `intent`: stale checkpoint 的恢复基准 ｜ `callback`: Q36 ｜ `depth`: L2

**Q38.** 恢复流程是人点一下触发的，还是自动的？如果是自动的，自动重放的权限边界在哪 —— 它能不能重放带副作用的动作？
> `intent`: 恢复权限与触发方 ｜ `callback`: — ｜ `depth`: L2

**Q39.** 承 Q37 说的恢复：LangGraph 自带 checkpointer、interrupt 和状态恢复。这些原生能力已经覆盖了你们要的哪些部分？你们自研的 Runtime 真正补的 delta 是什么？
> `intent`: 相对纯 LangGraph 的 delta ｜ `callback`: Q37 ｜ `depth`: L3

**Q40.** 承 Q39：什么条件下这块自研 Runtime 会被收回、直接用框架原生能力？
> `intent`: 自研 Runtime 的退出条件 ｜ `callback`: Q39 ｜ `depth`: L3

## T05 — Security / Effect

**Q41.** 整份简历里没有出现「授权」「权限」「安全」这些词。在这个系统里，「谁被允许调用哪个 Tool、对哪个对象做操作」是在哪一层定义的？
> `intent`: 授权模型所在的层 ｜ `callback`: — ｜ `depth`: L1

**Q42.** 一次 Tool 调用的授权检查发生在什么时刻 —— 计划构建时、Tool 选择时，还是真正执行前？
> `intent`: 授权检查的时机 ｜ `callback`: — ｜ `depth`: L1

**Q43.** 如果一个用户的权限在计划构建之后、执行之前被收回了，这次调用会怎样？系统靠什么知道权限已经变了？
> `intent`: 授权新鲜度 ｜ `callback`: — ｜ `depth`: L1

**Q44.** 承 Q42 说的那个检查点：带副作用的操作在执行之前，有没有留下审计记录？记录里写了什么 —— 谁、什么操作、基于哪一份授权？
> `intent`: effect 前审计的内容 ｜ `callback`: Q42 ｜ `depth`: L2

**Q45.** 承 Q44 的审计记录：在「决定执行」和「真正执行」之间进程崩了，重启后系统怎么知道上次到底做到哪一步？
> `intent`: 崩溃窗口的状态判定 ｜ `callback`: Q44 ｜ `depth`: L2

**Q46.** 承 Q45：当一个副作用操作的远端结果处于「未知」时，系统的默认动作是什么 —— 重试、放弃，还是转人工？这个默认是谁定的？
> `intent`: unknown effect 的默认处置 ｜ `callback`: Q45 ｜ `depth`: L2

**Q47.** 承 Q46：你们怎么确认「系统认为发生的」和「外部现实真的发生的」是一致的？有没有对账机制，多久跑一次，对不上时怎么处理？
> `intent`: 对账机制 ｜ `callback`: Q46 ｜ `depth`: L2

**Q48.** 承 Q47 说的对账：这套系统有没有真的改过外部现实（比如写入法院侧系统、对外发通知）？如果有，有没有出现过重复执行或漏执行？当时是怎么发现的？
> `intent`: 外部现实副作用的真实案例 ｜ `callback`: Q47 ｜ `depth`: L2

**Q49.** 承 Q43 的权限变更：在你们引入更严格的 effect / 授权控制之前，系统靠什么兜底（比如人工复核、只读限制）？当时最大的风险是什么，后来为什么演进成今天这样？
> `intent`: 授权 / effect 语义的演进动因 ｜ `callback`: Q43 ｜ `depth`: L3

**Q50.** 承 Q49 的演进：如果今天重做，effect / 授权这一层的哪些机制你会砍掉或合并到别处？为什么？
> `intent`: effect 控制层的退出与合并条件 ｜ `callback`: Q49 ｜ `depth`: L3
