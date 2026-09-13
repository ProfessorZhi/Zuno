# Red Interview Plan — rb-2026-09-13-human-red-016

question_count: 100
seed_question_count: 8
live_followups: DYNAMIC
one_question_one_intent: true
primary_persona: Implementation Interviewer
cross_personas: Forensic Interviewer / Open-source Skeptic / Fundamentals Interviewer
formal_input_head: 8f3ff3dbdcaee2f49e905eb533f1dadaddc412fa
red_questions_status: DRAFT_REVIEW

> `SPOKEN_SEEDS` 与运行时动态 follow-up 才是面试官真正说出口的问题。`PRESSURE_SUITE` 只是离线覆盖库，不按顺序朗读。

## Interview threads

- **T1 — Project reality / ownership** — 先判断候选人真正做过什么，以及 Pilot / 团队 / 个人贡献的边界。若候选人主动选出一块最深工作，优先跟他走，不平均扫四条 bullet。
- **T2 — GraphRAG regression** — 简历有精确指标、四个算法名和明确前后变化，信息密度最高；如果候选人自己把它选为主线，就沿“怎么发现 → 怎么定位 → 改了什么 → 数怎么来的 → 能声称到哪”自然深入。
- **T3 — Tool / MCP** — 重点听调用链、用户级配置、真实 bug 和回归测试。并发、timeout、幂等只在候选人把调用链讲起来后继续追。
- **T4 — Context / Memory** — 重点听本人实际落地范围、scope / readback / approval / provenance；不默认把 Memory 讲成完整长期记忆系统。
- **T5 — Reuse / simplification / fundamentals** — 适合中后段切换：哪些能力值得自建，哪些应该交给成熟 Host；也可自然切 Python async、网络、DB、检索指标等基础。

## SPOKEN_SEEDS

S001. Zuno 这段你挑一块自己做得最深的讲吧。

S002. 你这个项目已经做到 Pilot 了，实际用起来最让你印象深的一个问题是什么？

S003. 你简历里 GraphRAG 那次是指标先掉下去再拉回来的，最开始怎么发现它变差了？

S004. Tool Calling 那块，原来 MCPAgent-as-Tool 这条路到底哪里让你觉得该改？

S005. Memory 这块你自己真正落到代码里的部分是什么？

S006. 这几块里，如果我现在打开一段你写的代码，你最想给我看哪段？

S007. 你现在回头看，Zuno 里面哪一层最可能其实不用自己做？

S008. 我想确认个基础问题：你们这种异步 Tool 调用里，两个用户的运行时配置怎么隔开？

## FOLLOWUP_POLICY

- **候选人自己选了主线**：顺着他选的 thread 连续追，不因为预写覆盖率中途跳去另一条 bullet。
- **说出一个精确数字**：下一问优先是“这个数怎么测的？”；等他回答以后，再决定追 dataset、metric、baseline 还是 bad case。
- **说“我们做了”**：自然问“这里你自己主要做哪一段？”；如果已经讲清本人边界，不重复查户口。
- **说出具体失败 / bug**：先问“当时怎么定位到这里的？”；候选人讲清定位后再问“最后改了哪一层？”。
- **说出一个算法 / 抽象名**：只向下一层追一个机制，不一次要求公式、输入、异常、测试、指标全讲。
- **说到 framework / 自研层**：合适时问“这个为什么没直接用现成的？”；只有候选人给出 Delta 后再问维护 / 删除条件。
- **说到 timeout / retry / remote call**：再进入 HTTP/TCP 不确定性、幂等或 cancellation；没有出现这条上下文时不硬塞故障题。
- **说到 Pilot / 上线**：只在措辞开始模糊时追“这里 Pilot 具体证明了什么？”；候选人主动收紧边界则停止施压。
- **一次回答暴露多个 handle**：只挑当前最有信息增益的一个，其他留在 interviewer state，不用“一口气四连问”。
- **连续两轮仍无法建立 Ownership / mechanism**：Controller 触发 `KILL_SWITCH: CLAIM_IMPLEMENTATION_NOT_ESTABLISHED`，口头自然换 thread，不向候选人宣告 Kill Switch。
- **候选人纠正面试官前提**：更新当前理解，再基于新前提继续；不坚持隐藏答案。
- **thread 已经证明 / 否证且没有新信息**：pivot 到第二条项目线、岗位基础或场景题。

## BRANCH_EXAMPLES

### Branch A — GraphRAG：从“指标掉了”自然追到实现

**Seed**
> 你简历里 GraphRAG 那次是指标先掉下去再拉回来的，最开始怎么发现它变差了？

**候选人可能回答**
> real_runtime smoke 跑出来 Recall@5 比 baseline 低。我去看返回结果，发现 graph 进来的文档把原来 baseline 里已经命中的文档挤出 Top-K 了。

**下一问**
> 哪条 query 当时最明显？

**如果候选人讲出一个具体 bad case**
> 你当时第一反应是图里没找到，还是排序把它排掉了？

**如果候选人回答“目标文档其实还在候选池，主要是 fusion 排序”**
> 那你先改的是哪一层？

**如果候选人回答“先改 fusion”**
> 为什么不是简单把 graph 权重调低？

**等候选人把机制讲清以后**
> 你简历最后这个 1.00 是怎么测出来的？

这里的深度来自候选人的上一答。Red 不会在第一句就要求他同时讲 query、fusion、四个算法、测试和 ablation。

### Branch B — Tool / MCP：从“哪里别扭”走到并发基础

**Seed**
> Tool Calling 那块，原来 MCPAgent-as-Tool 这条路到底哪里让你觉得该改？

**候选人可能回答**
> 原来多套了一层 Agent，Tool 的绑定和用户自己的 MCP 配置要绕一圈，调用链比较别扭。

**下一问**
> 改完以后调用链少了哪一跳？

**如果候选人说 `GeneralAgent` 直接拿具体 Tool**
> 那用户自己的 server 配置放哪儿？

**如果候选人说“调用时再注入”**
> 两个用户一起进来会不会串？

**如果候选人给出 request-local / context-local 方案**
> 这个你当时真测过，还是现在回头看觉得应该这么做？

只有走到这里，Red 才决定是否继续 asyncio / ContextVar / timeout；不会一开始把生命周期、同名 Tool、并发、side effect 全塞进一个问题。

### Branch C — Memory：先确认“你到底做了哪一段”

**Seed**
> Memory 这块你自己真正落到代码里的部分是什么？

**候选人可能回答**
> 我主要做了 typed contracts、scope、`prepare_context()` 的 readback，以及一个比较薄的 orchestrator；不是完整长期记忆系统。

**下一问**
> 那一次 `prepare_context()` 进来的时候，你先拿到什么？

**如果候选人开始讲 scope / summary / structured memory**
> 为什么 structured memory 只让 `APPROVED` 的进来？

**如果候选人把 review boundary 讲清**
> 那刚读完它就被撤掉，这个你怎么看？

这里故障题由候选人先建立 read path 后才出现，而不是突然拿 stale-read race 审架构。

### Branch D — Ownership：让候选人自己选择最熟的代码

**Seed**
> 这几块里，如果我现在打开一段你写的代码，你最想给我看哪段？

**候选人可能回答**
> 我会选 Tool Calling 那块。

**下一问**
> 行，那你接手它的时候原来是什么样？

**如果候选人能说清 before state**
> 你自己第一笔关键改动是什么？

**如果连续两轮仍然只说“团队做了重构、整体更清晰”**
> 行，那我们换一块。GraphRAG 那次你自己参与得深吗？

Controller 此时记录 Ownership confidence 下降，但不会把“请列函数、Schema、test assertion”一次念给候选人。

### Branch E — Build / Buy：从候选人的删复杂度判断成熟度

**Seed**
> 你现在回头看，Zuno 里面哪一层最可能其实不用自己做？

**候选人可能回答**
> 通用 Agent Runtime / Host 这一层我会尽量复用，法律业务真正特殊的是上层状态和专业能力。

**下一问**
> 那你当时为什么还要保留自己的这一层？

**如果候选人说“成熟方案当时缺某个 Delta”**
> 现在框架把这个 Delta 补上了，你会删吗？

**如果候选人说“还要看效果”**
> 你会看哪个指标再决定？

这条 thread 不要求候选人为现有架构辩护；愿意删复杂度本身可以是好答案。

## PRESSURE_SUITE

> 离线覆盖库。每题仍尽量单意图，但不代表现场会按顺序问。

### T1 — Project reality / Ownership

Q001. 你加入 Zuno 的时候，系统已经有什么了？
Q002. 你最早自己完成的一块增量是什么？
Q003. 这四条经历里你最有把握说“我实现了”的是哪条？
Q004. 哪些内容你只会说“参与过”？
Q005. 你所在团队大概怎么分工？
Q006. 你这块代码平时是谁 review？
Q007. Pilot 在这个项目里具体指什么？
Q008. Pilot 能证明什么、不能证明什么？
Q009. 你亲眼看到过的最真实用户场景是什么？
Q010. 客户或法院侧最常暴露哪类问题？
Q011. 你自己跟到底的一个 bad case 是什么？
Q012. 那个 bad case 最后定位到哪一层？
Q013. 你对数据库实际做过什么？
Q014. 如果现在让我看一个 test，你会选哪个？
Q015. 如果现在让我看一个 commit，你希望它证明什么？
Q016. 这项目里你做过最错误的一次判断是什么？
Q017. 哪一块工作你后来发现其实没必要做那么复杂？
Q018. 你做的改动最后有没有真实使用结果？
Q019. 哪些效果你现在没有数据，不会写进简历？
Q020. 如果今天重新加入这个项目，你第一周会先做什么？

### T2 — GraphRAG / Retrieval

Q021. 这次 GraphRAG regression 最先是谁发现的？
Q022. 你怎么确认问题不是 baseline 自己波动？
Q023. 你看到的最典型坏结果是什么样？
Q024. 当时目标文档是根本没召回，还是排位掉了？
Q025. 你们的 baseline 到底是什么？
Q026. `limit=5` 在你这个 runner 里限制的是什么？
Q027. `Recall@5` 这个指标你怎么理解？
Q028. 为什么还需要 `MRR@10`？
Q029. `FullChainHit@5` 想补什么信息？
Q030. `fallback_count=1` 对你意味着什么？
Q031. baseline-preserving fusion 解决的核心冲突是什么？
Q032. fusion 里 baseline 信息怎么参与排序？
Q033. 什么情况下 graph candidate 仍然值得往前提？
Q034. 你为什么没有直接把 graph 权重降到很低？
Q035. candidate-aware seed expansion 想解决什么？
Q036. seed 从 baseline candidate 来会不会放大 baseline 偏差？
Q037. entity alias normalization 主要处理哪类 mismatch？
Q038. alias normalization 最容易误合并什么？
Q039. path-aware ranking 为什么比普通 score 有用？
Q040. path ranking 里什么信号最重要？
Q041. 四个改动是一次设计出来的，还是边看 bad case 边加的？
Q042. 你有逐项 ablation 吗？
Q043. 没有 ablation 的话，你现在敢说哪个改动贡献最大吗？
Q044. baseline 和 local GraphRAG 的配置怎么保证可比？
Q045. 这组 smoke 最容易 overfit 在哪里？
Q046. 为什么同日 rerun 到 1.00 还不能算 benchmark？
Q047. 下一步你最想扩哪一类样本？
Q048. GraphRAG 相比 baseline 多出来的主要延迟在哪？
Q049. 如果 Hybrid RAG + rerank 已经够好，你还会留 GraphRAG 吗？
Q050. 你会用什么指标决定删掉 GraphRAG？

### T3 — Tool Calling / MCP

Q051. MCPAgent-as-Tool 原来的调用链是什么样？
Q052. 直接绑定 concrete MCP Tools 后少了什么？
Q053. 为什么这一层嵌套会成为实际问题？
Q054. tool 到 server 的映射是什么时候建立的？
Q055. 用户级 MCP 配置是什么时候注入的？
Q056. 两个 server 有同名 Tool 时你准备怎么区分？
Q057. 两个用户同时调同一个 Tool，配置怎么隔离？
Q058. Python async 场景里 request-local state 你会怎么做？
Q059. direct route 的触发条件是什么？
Q060. 哪类请求一定不能 direct route？
Q061. direct route 误判时最坏会怎样？
Q062. ReAct fallback 是在哪种失败后发生？
Q063. custom MCP 名称递归当时怎么触发？
Q064. 你怎么定位到是名称解析而不是 server 本身？
Q065. 天气自然语言参数解析具体错在哪里？
Q066. structured-result test 主要防什么？
Q067. config-gate test 主要防什么？
Q068. direct-route test 最关键的 assertion 是什么？
Q069. 这些 regression test 里哪些只是 mock？
Q070. Tool schema 不符合 server 参数时谁应该报错？
Q071. MCP 调用 read timeout 能证明远端没执行吗？
Q072. timeout 之后直接 retry 有什么风险？
Q073. 有副作用的 Tool 怎么做幂等？
Q074. asyncio task cancel 以后远端请求一定停了吗？
Q075. 如果今天 MCP SDK 已经覆盖你的自研 Delta，你会删哪层？

### T4 — Context / Memory

Q076. 你这里说的 scope 最少包含哪些维度？
Q077. typed Context contract 最想防什么错误？
Q078. typed Memory contract 和普通 dict 最大区别是什么？
Q079. `prepare_context()` 的输入是什么？
Q080. `ContextOrchestrator` 为什么要单独存在？
Q081. task summary 是怎么进入当前 context 的？
Q082. structured memory 是怎么筛出来的？
Q083. 为什么只读 `APPROVED`？
Q084. `source-id trace` 解决的是什么追溯问题？
Q085. policy 信息为什么要进 Context Pack？
Q086. post-turn write 失败会影响已经返回的回答吗？
Q087. post-turn 重试怎么避免重复写？
Q088. 两个请求同时更新同一 scope 会发生什么？
Q089. context 构建完以后 memory 被撤销怎么办？
Q090. `32 passed` 里面你认为最值钱的是哪类 negative test？
Q091. 这 32 个测试明确不能证明什么？
Q092. 你怎么评估 Memory 真正提高了任务效果？
Q093. 如果只做一次性问答，你还需要这套 Memory 吗？
Q094. 现成 memory framework 已经能做存取时，你们自己的 Delta 是什么？
Q095. 你会在什么情况下把这套 Memory 简化掉？

### T5 — Architecture / Build-Buy / Fundamentals

Q096. 一个简单合同条款问答为什么不需要完整 Agent Runtime？
Q097. LangGraph / Agent SDK 已经能做持久执行时，你还会自建什么？
Q098. checkpoint 写 completed 为什么不一定代表业务结果已经成立？
Q099. 外部 POST timeout 后为什么不能简单标 failed？
Q100. 你这份 Zuno 简历里，哪一句最容易被面试官怀疑夸大？

## Red self-check

- Seed 共 8 条，全部是单一主要意图；没有一题要求候选人一次讲完机制 + 测试 + 指标 + Trade-off。
- 第一条 Seed 给候选人选择权；Red 不预设必须先 GraphRAG、Tool 或 Memory。
- 五个 Branch Example 都明确展示“上一答 → 下一问”，并允许候选人的回答改变路径。
- Ownership / Build-Buy / failure / evidence / fundamentals 保留在 interviewer mental map 和 Pressure Suite 中，没有被拼成候选人可见的 rubric。
- Kill Switch 只存在于 Controller policy；口头行为是自然换 thread。
- 100 问 Pressure Suite 与 Live Interview 明确分离。
- 没有使用 Zuno canonical docs、源码、PR diff 或 prior Blue answers 作为 Red 正式输入。
