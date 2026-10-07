# Red Wave 1 — Questions Q1–Q100

```text
round: rb-2026-10-07-formal-020
role: Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师
stage: 技术一面 / 项目深挖，连续 30–60 分钟
threads: T01 Tool/MCP · T02 GraphRAG · T03 Memory/Context · T04 Runtime · T05 Security/Effect
         T06 Project History · T07 Pilot/法院 · T08 系统简化/Delete · T09 Knowledge/Retrieval · T10 工程基础
blind: true（仅读 frozen resume + pinned attack-model）
isolation: PHYSICAL_CONTEXT_ISOLATION
provenance: Q1–Q50 与 Q51–Q100 由两个互不可见的隔离 Red 实例分别生成，本文件仅为拼接，未做跨半批改写
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

## T06 — Project History

**Q51.** 你加入 Zuno 的第一天，仓库里已经有什么东西是能跑起来的？——请说一个你当时能亲眼看到它跑通的入口，而不是文档里写的东西。
> `intent`: 建立入职时的系统存量基线，后面所有 Ownership 判断都以这一答为参照 ｜ `callback`: — ｜ `depth`: L1

**Q52.** 你在这条链路里提交的第一笔改动是什么？改的是哪个文件、哪个函数？
> `intent`: 定位第一笔个人改动，作为「个人贡献时间轴」的起点 ｜ `callback`: — ｜ `depth`: L1

**Q53.** 简历这五条 bullet，逐条说：哪一条是你从零写的，哪一条是你接手别人已有的东西再改的？
> `intent`: 把五条 Claim 逐条切开归属，防止「我们」覆盖个人 ｜ `callback`: — ｜ `depth`: L1

**Q54.** 你说重构了「MCP Tool 经子 Agent 转发」这套 —— 那套转发是谁写的？当时是出于什么考虑才让子 Agent 中转的？
> `intent`: 重构对象的前史与原始动机，验证是否真的理解被重构的东西 ｜ `callback`: Q53 ｜ `depth`: L2

**Q55.** 从你第一笔改动，到「把 MCP Tools 直接绑定主 Agent」这件事落地，中间隔了多长时间？那段时间你主要在做什么？
> `intent`: 时间线与工作密度的交叉校验，检验重构是否突兀出现 ｜ `callback`: Q52 ｜ `depth`: L2

**Q56.** GraphRAG 排序回退这个方向，是你提出来的，还是方向已经定了、交给你执行？你做到哪一层：定位问题、定方案、还是只写实现？
> `intent`: 区分「提出方向 / 设计方案 / 仅实现」，定位该 Claim 的真实 Ownership 层级 ｜ `callback`: Q54 ｜ `depth`: L2

**Q57.** 你今天讲的 typed contract、版本、receipt 这一类机制，在你加入的第一个月存在吗？如果当时没有，那当时靠什么保证同一件事？
> `intent`: 区分「当年具备的能力」与「今天的机制」，追问演进前靠什么兜底 ｜ `callback`: Q51 ｜ `depth`: L2

**Q58.** 你描述的系统分成九个模块 —— 这九个里，哪一个在你加入之前接口就已经定型、你从头到尾没有改过它？
> `intent`: 找出「零改动模块」，作为个人覆盖面的边界证据 ｜ `callback`: Q53 ｜ `depth`: L2

**Q59.** 你在 Q53 说某条 bullet 是你写的、Q56 又说某条是已有方向 —— 如果我现在逐行看 blame，这几条 bullet 的主要贡献者分别是谁？
> `intent`: 用 blame 视角交叉验证 Ownership 归属，逼出团队/学长/框架的三方拆分 ｜ `callback`: Q53, Q56 ｜ `depth`: L3

**Q60.** 如果只允许你留一条 bullet，且必须删掉你个人没有实际做过的部分 —— 你留哪一条，删掉哪四条？为什么是这条？
> `intent`: 收口，逼出「个人净贡献」的自我判断 ｜ `callback`: Q53 ｜ `depth`: L3

## T07 — Pilot / 法院

**Q61.** 「法院侧测试」这件事是谁发起的？当时在场的有哪些角色？
> `intent`: 确认这件事的组织主体和参与方，判断是正式测试还是临时演示 ｜ `callback`: — ｜ `depth`: L1

**Q62.** 你本人当面跑过 demo 吗？那次是现场真跑，还是提前把输入固定好、只走一遍成功路径？
> `intent`: 区分「现场演示」与「预置输入的演出」，直接指向 demo 的真实性 ｜ `callback`: — ｜ `depth`: L1

**Q63.** 法院那边实际使用这个系统持续了多久？是每天用、隔几天用一次，还是只在一个时间窗口内测了一轮？
> `intent`: 用使用时长与频次界定测试的真实规模，不索取百分比 ｜ `callback`: — ｜ `depth`: L1

**Q64.** 「Pilot Validation」这个定性是谁给的？是法院/甲方那边给出的结论，还是你自己在简历里这样写的？
> `intent`: 追「Pilot Validation」这个词的出处与授权方 ｜ `callback`: Q63 ｜ `depth`: L2

**Q65.** 在那段使用期里，有没有收到过真实使用者报回来的具体 bad case？请说一条，以及当时怎么处理的。
> `intent`: 用真实 bad case 的存在与否，检验是否真的有使用闭环 ｜ `callback`: Q63 ｜ `depth`: L2

**Q66.** 你简历里那些效果相关的说法，分别来自哪里 —— 你自己跑的、团队给你的、还是某份文档里写的？说清来源而不是数值。
> `intent`: 为每个数字建立来源归属，不诱导编造数值 ｜ `callback`: Q63 ｜ `depth`: L2

**Q67.** 如果这个系统明天关掉，法院那边会有人发现并来问吗？
> `intent`: 用「依赖是否真实存在」检验它离 production 的距离 ｜ `callback`: Q63 ｜ `depth`: L2

**Q68.** 法院侧测试的用例和验收标准是谁写的？法院有没有出自己的题，还是你们自己出题自己验收？
> `intent`: 检验测试是否存在独立第三方标准，还是自证 ｜ `callback`: Q61 ｜ `depth`: L2

**Q69.** 你在 Q64 说 Pilot 这个定性来自某一方 —— 那按你今天的判断，阻止你把它叫做 Production 的第一位原因是什么？
> `intent`: 收口到「为什么不是生产」，检验候选人的自我诚实度 ｜ `callback`: Q64 ｜ `depth`: L3

**Q70.** 如果面试官直接问你「这个系统在生产环境跑过吗」，你最诚实的一句话回答是什么？那你为什么仍在简历上保留 Pilot Validation？
> `intent`: 收口，检验候选人能否在压力下保持表述一致性 ｜ `callback`: Q64, Q67 ｜ `depth`: L3

## T08 — 系统简化 / Delete

**Q71.** 你那九个模块里，哪些模块的调用方只有一到两个？
> `intent`: 用调用方数量找抽象的可疑层，为后续减法建立清单 ｜ `callback`: — ｜ `depth`: L1

**Q72.** 如果今天从零重做，你第一个删掉的模块是哪个？
> `intent`: 直接执行 Subtraction Test，取候选人的第一直觉 ｜ `callback`: — ｜ `depth`: L1

**Q73.** 九个模块里，哪一个删掉之后主流程仍然能跑完？
> `intent`: 找出「删除无损」的模块，检验复杂度是否真的有支撑 ｜ `callback`: — ｜ `depth`: L1

**Q74.** 这些抽象里，哪一个是你为了架构完整性加的，而不是某个具体 bad case 逼出来的？
> `intent`: 逼出「架构自嗨」的自认，检验复杂度举证责任 ｜ `callback`: Q72 ｜ `depth`: L2

**Q75.** 你说要删 X —— 但 X 当初是为解决什么问题建的？那个问题今天真的不存在了，还是只是你换了个方式绕过去？
> `intent`: 校验删除判断是否建立在问题消失的证据上 ｜ `callback`: Q72 ｜ `depth`: L2

**Q76.** 如果强行把九个模块压成五个，你会怎么合并？合并之后哪一个具体 failure 会回来？
> `intent`: 用合并代价检验模块边界的必要性 ｜ `callback`: Q71 ｜ `depth`: L2

**Q77.** 你自研的这些层里，哪一层其实 LangGraph 或某个成熟框架已经覆盖了，你们只是包了一层？
> `intent`: Build/Buy/Extend 追问，找自研的真实 Delta ｜ `callback`: Q71 ｜ `depth`: L2

**Q78.** Memory V2 的 typed contract 加 scope 约束 —— 如果只允许保留一个 scope 维度，你留哪一个，另一个靠什么替代？
> `intent`: 用「只留一个」压缩 scope 抽象，检验它是否真被需要 ｜ `callback`: — ｜ `depth`: L2

**Q79.** 你在 Q75 说 X 的问题已经不存在了 —— 那今天的判断是「当时该做但做错了」，还是「当时就不该做」？两个结论对应的架构责任完全不同。
> `intent`: 区分「实现错误」与「设计不该存在」，检验反思粒度 ｜ `callback`: Q75 ｜ `depth`: L3

**Q80.** 请给九个模块各写一个删除/合并条件 —— 哪个模块你写不出来？写不出来的那个为什么该继续留着？
> `intent`: 收口，逼出退出条件；写不出条件的模块即复杂度未举证 ｜ `callback`: Q72, Q76 ｜ `depth`: L3

## T09 — Knowledge / Retrieval 基础

**Q81.** 从一份文档进入系统，到用户点得到引用 —— 这中间经过了哪几个状态对象，分别由谁改变？
> `intent`: 建立文档到引用的状态链，检验是否真理解流转而非名词堆叠 ｜ `callback`: — ｜ `depth`: L1

**Q82.** 「Ready」这个状态是给谁看的？谁有权把它从没准备好改成准备好？
> `intent`: 追问 Readiness 的消费方与写权限归属 ｜ `callback`: — ｜ `depth`: L1

**Q83.** 一条引用（Citation）里到底存了什么？是文档 ID、chunk ID，还是字符区间？点进去靠什么定位？
> `intent`: 追引用的数据结构，检验可点击性是真实实现还是说法 ｜ `callback`: — ｜ `depth`: L1

**Q84.** 文档被更新之后，指向旧版本的引用会怎样？是失效、重定向到新版本，还是仍然可以点开旧内容？
> `intent`: 追版本与引用的耦合语义，检验更新是否被认真处理 ｜ `callback`: — ｜ `depth`: L2

**Q85.** 你如何证明「全案里没有这个信息」？是检索不到就断定不存在，还是有一层覆盖度判断？
> `intent`: 追问「否定性结论」的证据来源，检验是否用检索结果冒充全集判断 ｜ `callback`: Q83 ｜ `depth`: L2

**Q86.** Vector、BM25、Graph 三路结果怎么融合、怎么调权？权重是固定常量，还是随 query 变化？
> `intent`: 追融合与调权的真实机制 ｜ `callback`: — ｜ `depth`: L2

**Q87.** baseline-preserving fusion 保留了 baseline 的原始 rank —— 那被挤出 Top-K 的那条图候选，它的证据强度算到哪里去了？
> `intent`: 追晋升/挤出规则的分数去向，检验融合是否只是加权拼接 ｜ `callback`: Q86 ｜ `depth`: L2

**Q88.** 如果 chunk 切在了句子中间，用户点进引用看到的是完整那句，还是一个残句？你们怎么切、怎么补？
> `intent`: 追切分与引用展示的一致性，检验可点击性的表层之下 ｜ `callback`: Q83 ｜ `depth`: L2

**Q89.** 你在 Q85 说检索不到时会如何如何 —— 但如果引用指向的那一段恰好被删掉了，你 Q84 讲的「旧引用仍可用」还成立吗？
> `intent`: 收口，把否定判断与引用时效两条线交叉，逼出自洽性 ｜ `callback`: Q84, Q85 ｜ `depth`: L3

**Q90.** 这条链上的状态对象，你觉得哪一个是可以删掉的？删掉它之后哪一步会变得不可判定？
> `intent`: 收口，把删除思维施加到知识链上，检验状态对象的必要性 ｜ `callback`: Q81 ｜ `depth`: L3

## T10 — 工程基础

**Q91.** GIL 存在的情况下，为什么用线程跑多个 `requests` 请求仍然能提速，而 CPU 密集型任务用线程基本不加速？
> `intent`: GIL 的真实语义与释放时机 ｜ `callback`: — ｜ `depth`: L1

**Q92.** PostgreSQL READ COMMITTED 下，两个事务同时执行 `UPDATE t SET c = c + 1 WHERE id = 1`，会不会丢更新？为什么？
> `intent`: 隔离级别与丢失更新的成因 ｜ `callback`: — ｜ `depth`: L1

**Q93.** 一次 Tool 调用的 HTTP 请求超时了 —— 你能据此断定远端没有执行吗？请举一个不能断定的情况。
> `intent`: 超时的语义边界，检验是否把「本地超时」当「远端未发生」 ｜ `callback`: — ｜ `depth`: L1

**Q94.** 你在 Q86 说三路检索并行、超时就返回 —— `asyncio.gather` 到点取消，被取消的是本地 coroutine，远端那次检索请求真的停了吗？
> `intent`: 从项目机制桥接到 cancellation 语义，追取消是否等于终止 ｜ `callback`: Q86 ｜ `depth`: L2

**Q95.** 简历说 per-user config 在调用时注入 —— 如果用 ContextVar 存这个配置，`asyncio.create_task` 里读得到吗？丢进 `run_in_executor` 里呢？各为什么？
> `intent`: coroutine 上下文传播，检验并发下用户配置会不会串 ｜ `callback`: Q54 ｜ `depth`: L2

**Q96.** 如果失败重试三次的那个 Tool 是写操作，最坏的事态是什么？你靠什么让这次重试是安全的？
> `intent`: 重试放大与幂等语义 ｜ `callback`: Q93 ｜ `depth`: L2

**Q97.** `asyncio.CancelledError` 在 Python 3.8+ 继承自 `BaseException` 而不是 `Exception` —— 这对你写 `except Exception` 的清理逻辑意味着什么？
> `intent`: 异常层级语义，检验是否写过真正的取消安全清理 ｜ `callback`: — ｜ `depth`: L2

**Q98.** 查询条件固定为 `user_id = ? AND project_id = ?` 再按 `created_at DESC` 排前 20 条 —— 复合索引的列顺序你怎么定？为什么反过来会变差？
> `intent`: 复合索引的最左前缀与排序利用 ｜ `callback`: — ｜ `depth`: L2

**Q99.** Memory 是「调用前读取、回合后写入」—— 请描述一个多轮并发下能产生丢失更新的时序，并说明为什么 READ COMMITTED 挡不住它。
> `intent`: 收口，把并发基础落到候选人自己声称做过的 Memory 写入路径 ｜ `callback`: Q92, Q95 ｜ `depth`: L3

**Q100.** 你在 Q53 说路由这条 bullet 是你写的、并用回归测试固定了路由边界 —— 那个回归集里，「该 direct 却走了 ReAct」和「该 ReAct 却走了 direct」会被算成同一个错误吗？哪一个方向对你更致命，为什么？
> `intent`: 收口，把评测指标设计打穿到错误代价不对称性 ｜ `callback`: Q53 ｜ `depth`: L3
