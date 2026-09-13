# Red Interview Plan — rb-2026-09-13-human-red-016

question_count: 100
seed_question_count: 8
live_followups: DYNAMIC
one_question_one_intent: true
primary_persona: Implementation Interviewer
cross_personas: Forensic Interviewer / Open-source Skeptic / Fundamentals Interviewer
formal_input_head: ca31e3d5595a14e778d14d078a116bfb329c02a1
red_questions_status: DRAFT_REVIEW
revision: 2

> 真正说给候选人的，是 `SPOKEN_SEEDS` 和根据上一答临场长出来的 follow-up。下面的 100 问是备题库，不是一张要照着念完的卷子。

## Red 心里怎么想

先让候选人讲。听他自己暴露最值得追的东西：一个数字、一个技术选择、一个失败、一个“我们做了”、一个“后来优化了”。一次只抓一个。

真正有东西的主线通常会这样往下走：

```text
发生了什么？
→ 你怎么知道问题在这里？
→ 最后具体改了什么？
→ 为什么这么改，不是另一种？
→ 边界条件下还成立吗？
→ 结果怎么证明？
```

不要求固定六步。有时两三问就够；像字节这类偏工程深挖的一面，一条线追 3–5 层很正常，代码、参数、状态、异常和底层原理都可以继续问。关键是后一问来自前一答，而不是第一句把五层问题揉成一段。

面试官可以直接说：

```text
具体一点。
这个怎么实现的？
为什么不用现成的？
这个数怎么来的？
你真遇到过吗？
这里如果超时呢？
那状态放哪？
```

短不等于浅。

## Interview threads

- **T1 — Project / ownership**：先搞清楚候选人真正做过什么。候选人自己挑出最熟的一块后，就跟着那块走。
- **T2 — GraphRAG**：从真实坏例子一路追到 ranking、评测、ablation 和是否值得保留 GraphRAG。
- **T3 — Tool / MCP**：从调用链追到 concrete Tool、用户配置、并发隔离、真实 bug、timeout 和 retry。
- **T4 — Context / Memory**：从本人落地范围追 scope、readback、approval、并发更新和 stale read。
- **T5 — Code / system depth**：候选人愿意讲代码，就顺着 async、状态持久化、大结果、失败恢复、测试继续压。
- **T6 — Evaluation / fundamentals**：精确数字追怎么测；项目线聊透以后可以自然切 Python、网络、DB、检索或算法基础。

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

- 候选人自己选了主线，就顺着这条线追；没新信息了再换。
- 说出精确数字，先问“这个数怎么测的？”，再看要不要追 dataset、metric、baseline、bad case 或成本。
- 说“我们做了”，Ownership 不清才问“这里你自己主要做哪一段？”。
- 说出具体失败，先问怎么定位，再问改了哪里。定位过程很能看出是不是做过。
- 抛出算法或抽象名，往下一层追一个机制；回答扎实再继续数据结构、参数、复杂度或边界。
- 讲自研层，合适时问“为什么没直接用现成的？”。
- 讲 async / timeout / retry / remote call，再进入并发、HTTP/TCP、cancellation、幂等和 unknown outcome。
- 讲评测集或线上效果，可以继续追样本怎么来、怎么更新、线上 log 怎么沉淀成有限线下集。
- 一次回答有四个可追点，只挑一个最值钱的。
- 一条主线回答很好，可以连续追 3–5 层甚至更深。
- 一条主线连续两轮只能讲空泛概念，Controller 记 `KILL_SWITCH: CLAIM_IMPLEMENTATION_NOT_ESTABLISHED`，口头自然换题。
- 候选人纠正面试官前提，就用新前提继续。
- 项目深挖一段后，可以直接切岗位基础题或算法题，不需要每题都编项目故事。

## BRANCH_EXAMPLES

### A. GraphRAG：从坏 query 追到 ranking 和评测

> 你简历里 GraphRAG 那次是指标先掉下去再拉回来的，最开始怎么发现它变差了？

候选人：smoke 里 Recall@5 比 baseline 低，graph 文档把原本命中的文档挤出 Top-K。

> 哪条 query 当时最明显？

候选人讲出具体 query / Top-K。

> 你怎么确认它是排序挤掉了，不是图这边根本没找到？

候选人：目标文档还在更大的候选池。

> 那你第一刀为什么砍 fusion？

候选人：普通 graph noise 不该轻易挤掉 baseline candidate。

> 具体怎么保？硬保 Top-K，还是排序里给 baseline 一个优先级？

候选人讲清 ranking rule。

> 那 graph 真有很强证据的时候，还能不能把 baseline 顶下去？

如果机制还能讲清，可以继续：

> 为什么不是简单把 graph 权重统一调低？

最后才追数字：

> 你简历这个 Recall@5 1.00 是怎么测的？

如果只是小 smoke：

> 四个改动没逐项 ablation 的话，你现在敢说哪个贡献最大吗？

### B. Tool / MCP：从调用链追到并发和 timeout

> Tool Calling 那块，原来 MCPAgent-as-Tool 这条路到底哪里让你觉得该改？

候选人：多套一层 Agent，Tool 绑定和用户 MCP 配置绕一圈。

> 改完以后少了哪一跳？

候选人：`GeneralAgent` 直接绑定具体 Tool。

> 那 Tool 怎么知道自己属于哪个 server？

候选人讲 tool → server mapping。

> 用户自己的 token、endpoint 这些配置什么时候进去？

候选人：调用期注入。

> 两个用户一起调同一个 Tool，会不会串？

如果候选人提 request-local/context-local：

> 这个你当时真实现和测过，还是现在回头看觉得应该这么做？

如果历史确实涉及 async context：

> Python 里你会拿什么保证这类上下文跟着 coroutine 走？

如果继续讲远端 Tool：

> read timeout 了，你能确定远端没执行吗？

回答不能确定以后：

> 那有副作用的 Tool 你敢直接 retry 吗？

再继续才问 idempotency key、unknown outcome 或 reconciliation。

### C. Memory：从本人代码追到一致性

> Memory 这块你自己真正落到代码里的部分是什么？

候选人：contracts、scope、`prepare_context()` readback 和薄 orchestrator。

> 一次 `prepare_context()` 进来的时候，最先拿到什么？

候选人讲 request / scope。

> 哪几个 scope 字段会直接决定一条 memory 能不能被读到？

讲清以后：

> structured memory 为什么只读 `APPROVED`？

如果回答涉及 review / provenance：

> 那 context 刚组完，这条 memory 就被撤掉了呢？

如果能区分历史实现和 Target：

> 两个请求同时更新同一个 scope，你最怕哪类写冲突？

最后再追测试：

> `32 passed` 里面哪两个 negative test 最能说明这套 foundation 没乱读数据？

### D. 共享代码式深挖：看“为什么这么写”

> 这几块里，如果我现在打开一段你写的代码，你最想给我看哪段？

候选人选 Tool Calling。

> 行，你从入口讲，这段代码进来以后第一步干什么？

候选人讲到 async。

> 这里为什么要 async？同步写会出什么问题？

如果回答是并发 I/O：

> 那任务中途挂了，执行到哪一步这件事放哪？

候选人讲多轮 Tool 结果会回模型：

> 如果一个 Tool 一次吐回来几十 MB，你真准备全塞上下文？

如果回答“摘要/截断”：

> 别先说摘要，具体在哪层截？原始结果还留不留？模型下一轮怎么引用？

这类问题可以很深，但每一层都要等上一层回答完。

### E. Evaluation：从一个数字追到评测集维护

候选人主动讲指标提升。

> 这个数怎么测的？

讲清 runner / dataset 后：

> 这批样本怎么来的？

如果是人工挑的开发样本：

> 怎么避免你刚好把看过的问题调到很好？

如果讲 holdout / 新样本：

> 真上线以后，海量 log 你怎么变成下一版有限的线下评测集？

如果讲 failure mining / sampling：

> 那怎么防止高频简单问题把少量严重 bad case 淹掉？

### F. Build / Buy：允许候选人真的删复杂度

> 你现在回头看，Zuno 里面哪一层最可能其实不用自己做？

候选人：通用 Agent Host 应尽量复用。

> 那你们当时自己留这层是缺什么？

给出具体 Delta 后：

> 这个 Delta 现在框架已经补了吗？

如果已经补了：

> 那你会删吗？

候选人说看迁移收益：

> 你会看什么再决定？

最后：

> 到什么线你会真删，而不是嘴上说 reuse-first？

### G. 从项目自然切基础

Tool thread 已经聊到 async、共享状态：

> Python coroutine 之间上下文隔离你熟吗？

答到 `ContextVar`：

> 它和普通 thread-local 最大区别是什么？

再答清楚以后可以换网络：

> HTTP client 超时的时候，TCP 层面你到底知道了什么？

项目线已经给了语境，所以基础题可以很直接。

## PRESSURE_SUITE

> 100 条离线备题。现场不按编号走。

### T1 Project / Ownership
Q001 加入 Zuno 时系统已经有什么？
Q002 最早自己完成的增量是什么？
Q003 最有把握说“我实现了”的是哪条？
Q004 哪些只能说“参与过”？
Q005 团队怎么分工？
Q006 谁 review 你这块代码？
Q007 Pilot 具体指什么？
Q008 Pilot 能证明什么？
Q009 亲眼看到过的真实用户场景？
Q010 客户侧常暴露什么问题？
Q011 自己跟到底的 bad case？
Q012 bad case 最后定位到哪层？
Q013 实际做过什么数据库工作？
Q014 最想给我看哪个 test？
Q015 最想给我看哪个 commit？
Q016 做过最错误的一次判断？
Q017 哪块后来发现做复杂了？
Q018 改动有没有真实使用结果？
Q019 哪些效果没数据不会写简历？
Q020 今天重来第一周先做什么？

### T2 GraphRAG / Retrieval
Q021 regression 最先怎么发现？
Q022 怎么排除 baseline 波动？
Q023 最典型坏结果？
Q024 是没召回还是排位掉了？
Q025 baseline 是什么？
Q026 `limit=5` 限制什么？
Q027 `Recall@5` 怎么理解？
Q028 为什么还要 `MRR@10`？
Q029 `FullChainHit@5` 补什么？
Q030 `fallback_count=1` 意味着什么？
Q031 baseline-preserving fusion 解决什么？
Q032 baseline 信息怎么参与排序？
Q033 graph candidate 什么情况下能前提？
Q034 为什么不统一降低 graph 权重？
Q035 candidate-aware seed expansion 解决什么？
Q036 会不会放大 baseline 偏差？
Q037 alias normalization 处理什么 mismatch？
Q038 最容易误合并什么？
Q039 path-aware ranking 为什么有用？
Q040 path ranking 最重要信号？
Q041 四个改动怎么逐步出现的？
Q042 有逐项 ablation 吗？
Q043 没 ablation 敢说谁贡献最大吗？
Q044 配置怎么保证可比？
Q045 smoke 最容易 overfit 在哪？
Q046 为什么 1.00 还不能算 benchmark？
Q047 下一步扩什么样本？
Q048 多出来的延迟主要在哪？
Q049 Hybrid RAG 够好还留 GraphRAG 吗？
Q050 什么指标触发删除 GraphRAG？

### T3 Tool / MCP
Q051 原调用链什么样？
Q052 direct concrete Tool 后少了什么？
Q053 这层嵌套为什么真有问题？
Q054 tool→server mapping 何时建立？
Q055 用户配置何时注入？
Q056 同名 Tool 怎么区分？
Q057 两用户同时调用怎么隔离配置？
Q058 async request-local state 怎么做？
Q059 direct route 什么时候触发？
Q060 哪类请求不能 direct？
Q061 direct route 误判最坏怎样？
Q062 ReAct fallback 在什么失败后发生？
Q063 custom MCP 名称递归怎么触发？
Q064 怎么定位不是 server 故障？
Q065 天气参数解析错在哪？
Q066 structured-result test 防什么？
Q067 config-gate test 防什么？
Q068 direct-route test 关键 assertion？
Q069 哪些 test 只是 mock？
Q070 schema 不匹配谁报错？
Q071 read timeout 能证明远端没执行吗？
Q072 timeout 后直接 retry 风险？
Q073 有副作用 Tool 怎么幂等？
Q074 asyncio cancel 后远端一定停吗？
Q075 MCP SDK 补齐 Delta 后删哪层？

### T4 Context / Memory
Q076 scope 至少有哪些维度？
Q077 typed Context contract 防什么？
Q078 typed Memory contract 和 dict 差别？
Q079 `prepare_context()` 输入是什么？
Q080 `ContextOrchestrator` 为什么存在？
Q081 task summary 怎么进 context？
Q082 structured memory 怎么筛？
Q083 为什么只读 `APPROVED`？
Q084 source-id trace 解决什么？
Q085 policy 为什么进 Context Pack？
Q086 post-turn write 失败怎样？
Q087 post-turn retry 怎么防重复？
Q088 同 scope 并发更新怎样？
Q089 context 组完 memory 被撤销怎样？
Q090 `32 passed` 最值钱的 negative test？
Q091 这 32 个测试不能证明什么？
Q092 怎么评估 Memory 真提高任务效果？
Q093 一次性问答还要 Memory 吗？
Q094 现成 memory framework 已能存取时自研 Delta？
Q095 什么情况下简化 Memory？

### T5 Architecture / Build-Buy / Fundamentals
Q096 简单条款问答为什么不用完整 Agent Runtime？
Q097 Agent SDK 已能持久执行时还自建什么？
Q098 checkpoint completed 为什么不代表业务结果成立？
Q099 外部 POST timeout 为什么不能简单标 failed？
Q100 这份简历哪句最容易被怀疑夸大？

## Red self-check

- Seed 仍然短、单意图；没有为了“深”退回长复合题。
- Branch 展示了 3–5 层甚至更深的工程追问。
- 深挖可以进入代码、数据结构、async、状态、参数、timeout、幂等、评测集、指标和底层原理。
- 每一层依赖上一答；候选人答法变，下一问也必须变。
- “具体一点”“这个怎么实现”“为什么不用 X”“这个数怎么来的”允许使用，但不能机械套模板。
- Pressure Suite 与 Live Interview 分离。
- Kill Switch / risk / rubric 只属于 Controller。
- Blue 继续 BLOCKED；本修订重新进入 USER_RED_REVIEW。
