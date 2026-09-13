# Red Questions — rb-2026-09-13-resume-first-014

question_count: 100
primary_persona: Implementation Interviewer
cross_personas: Forensic Interviewer / Open-source Skeptic / Fundamentals Interviewer
formal_input_head: 5861c7df860b538e49a7188b9c78493a52c30a54

## Attack Chain A — Project reality, causality and ownership

Q001. 用 30 秒讲清 Zuno 解决的原始业务问题。为什么这件事需要 Agent，而不是一个带引用的法律 RAG 问答页？

Q002. 简历写“内部 Demo、客户侧 / 法院侧测试与 Pilot Validation”。这四个阶段分别由谁使用、在什么环境使用、验证了什么？“Pilot Validation”在你这里具体意味着什么？

Q003. 你明确写“在已有系统基础上参与”。你加入当天已经有什么：前端、Agent、RAG、Memory、Tool、数据库分别到什么程度？你的增量从哪一个 commit / 类 / 数据流开始？

Q004. 团队大概多少人？导师、其他同学、平台框架和你分别拥有哪部分？四条简历 bullet 里哪些可以用“我实现”，哪些只能说“我参与”？

Q005. 把 Tool Calling、GraphRAG、Context / Memory、架构复盘按时间排出来。它们之间有什么真实依赖，哪些只是并行发生的工作？

Q006. 既然项目进入过客户侧和法院侧测试，讲一个最具体的负反馈或 bad case。你当时看到的原始现象是什么，最终有没有定位根因？

Q007. Pilot 能证明哪些工程事实，不能证明哪些？如果我追问真实用户数、QPS、P95、SLA、故障率，你现在能拿出什么，哪些必须明确说没有？

Q008. 你这四条成果里，哪些在真实法律数据上跑过，哪些只在公开数据集、测试或本地研发环境验证过？为什么简历把它们放在同一个项目里仍然合理？

Q009. 这个项目有哪些环境：本地开发、CI、内部 Demo、客户测试、Pilot？配置、数据权限和外部依赖有什么关键差异？

Q010. 现在如果面试官问“这个系统生产上线了吗”，你会怎么回答？什么证据出现以后你才会把 Pilot 升级成 Production claim？

Q011. 四条 bullet 里你认为最能证明自己达到 Agent 开发工程师要求的是哪一条？为什么不是另外三条？

Q012. 如果现场让我打开一段你最熟的代码，你会选哪个类 / 函数 / test？请说出入口、主要分支、关键状态和你改动前后的差别。

Q013. 这些修改是谁 review 的？如果没有正式 review，你用什么方式证明不是“代码能跑但自己也解释不清”的一次性修改？

Q014. 你开发过程中使用过 Codex、Claude Code 或其他 Coding Agent 吗？如果用了，哪些工作是模型辅助生成的，你怎样验证自己真正掌握最终实现和故障语义？

Q015. 整个 Zuno 经历里，你做过的最失败、最值得推翻的一次技术判断是什么？如果没有失败案例，我为什么相信你真的做过复杂工程而不是只整理了成功结果？

## Attack Chain B — Agent / Tool Calling / MCP

Q016. 最初的 MCPAgent-as-Tool 嵌套方案解决什么问题？它具体在哪里变复杂或失败，以至于值得改成 `GeneralAgent` 直接绑定 concrete MCP Tools？

Q017. 把修改前后的完整调用链画出来：用户请求进入后，Tool schema 从哪里来，模型怎么选 Tool，参数怎么传，MCP Server 怎么被调用，结果怎么回到模型？

Q018. MCPAgent-as-Tool 多一层 Agent 到底带来什么成本：额外模型调用、上下文丢失、错误传播、Tool schema 不透明，还是别的问题？你有证据区分这些原因吗？

Q019. `GeneralAgent` “直接绑定具体 MCP Tools”是启动时静态绑定、每次请求动态发现，还是按 Workspace / 用户动态构造？为什么选这个生命周期？

Q020. 简历写“按 tool → server 映射注入用户级 MCP 配置”。这个映射的数据结构和唯一键是什么？如果两个 server 暴露同名 tool，怎么消歧？

Q021. 用户级配置在 middleware 中注入。并发请求下怎样防止 A 用户的 token / endpoint 泄漏到 B 用户？如果用了 request-local / `ContextVar`，请解释它在 asyncio task 复制和线程切换时的边界。

Q022. 如果一个请求启动了并行 Tool Calls，它们共享哪些上下文、各自隔离哪些状态？配置读取和修改是否可能形成 data race？

Q023. MCP Tool 的参数 schema 谁负责生成和校验？Server schema 与本地 Python / JSON 类型不一致时，在模型调用前、调用时还是结果回注时失败？

Q024. Workspace 的 deterministic direct route 如何判定“这个请求足够确定，可以跳过 ReAct”？是规则、intent、tool name、参数完整性还是别的条件？

Q025. direct route 与 ReAct fallback 的边界是什么？请给一个应该 direct route、一个必须 ReAct、一个最容易误判的例子。

Q026. 如果 direct route 已经调用了一个有副作用的 Tool，但本地在收响应前报错，然后代码进入 ReAct fallback，会不会重复执行？你的 routing 和 retry 设计怎样避免这个问题？

Q027. “custom MCP 名称递归”具体是什么递归：路由函数自调用、名称规范化反复匹配、Agent 把 MCP 当 Tool 再进入自己，还是别的？最小触发输入是什么？

Q028. 修复一个具体递归 bug 以后，怎样把它推广成对 alias cycle / route cycle 的通用防护，而不是只 hard-code 当前名称？

Q029. 高德天气“自然语言参数解析”原来的 bug 是什么？比如“南京明天天气”为什么会被解析错，错误发生在 LLM Tool Calling 之前还是之后？

Q030. 为什么天气参数不全部交给 LLM 按 Tool schema 生成，而要保留 deterministic extraction？你在稳定性、成本、可测试性和泛化之间怎么取舍？

Q031. deterministic parser 遇到“南京市鼓楼区”“南京和上海天气对比”“帮我看下明天南京会不会下雨”时如何处理？从一个中文 demo 扩展到真实语言输入会在哪里失效？

Q032. `structured-result` regression test 实际断言什么？只断言返回 JSON shape，还是会验证 Tool 名、参数、Server、结果字段以及模型回注内容？

Q033. direct-route / config-gate / structured-result 这些 regression tests 是 unit、integration 还是 E2E？哪些依赖 mock，哪些会真的连 MCP Server？为什么选择这个测试粒度？

Q034. config gate 的负例是什么？缺配置时是 fail closed、fallback、提示用户补配置，还是悄悄走默认值？这个行为为什么正确？

Q035. 简历谨慎写的是“test artifact”而不是“CI passed”。如果面试官问这些 tests 当时是否实际跑过、在哪跑过，你能证明到什么程度？

Q036. Tool Call 遇到 connect timeout、read timeout、server 500、连接中断时，你分别能知道什么？哪些错误只能证明“本地没拿到结果”，不能证明远端没执行？

Q037. 从 TCP / HTTP 原理解释：为什么客户端 timeout 不能推出远端业务动作失败？这个结论如何影响 Agent Tool 的 retry 策略？

Q038. 对创建工单、发消息、提交业务记录这类 mutating Tool，你会把 idempotency key 放在哪里，按什么业务身份生成？如果远端根本不支持幂等怎么办？

Q039. Python `asyncio` 中如果用户取消任务，正在进行的 MCP / HTTP 调用一定会被取消吗？`CancelledError`、socket request 和远端动作之间可能出现什么不同步？

Q040. 现在 MCP SDK、LangGraph、OpenAI / Anthropic Agent SDK 都能做 Tool binding。今天重做时，你这层自定义 Tool Calling 里哪些应直接删除，哪些 Delta 仍值得保留？如果成熟框架明天补齐你的 Delta，你删不删？

## Attack Chain C — GraphRAG retrieval quality

Q041. 你为什么在这个项目里需要 GraphRAG？先给最简单 baseline，再说哪一类查询让普通 BM25 / Vector / Hybrid retrieval 不够用。

Q042. `HotpotQA limit=5 retrieval smoke` 到底有多少 query、什么 corpus、什么 index、什么评测入口？这里的 `limit=5` 是样本数、Top-K 还是两者之一？

Q043. baseline 和 local GraphRAG 是否使用同一 corpus、同一 query、同一 embedding / reranker、同一个 Top-K？如果不是，`1.00 → 0.80` 能不能直接归因给 GraphRAG？

Q044. 你这里的 `Recall@5` 怎么定义？简历又写了“gold-like documents”，gold-like 与正式 gold label 有什么差别，会不会让指标看起来比实际可靠？

Q045. 为什么同时报告 `Recall@5` 和 `MRR@10`？一个 cut at 5、一个 cut at 10，它们各自回答什么问题？

Q046. `FullChainHit@5` 的 chain 是什么？一个多跳问题需要命中哪些文档才算 full chain，顺序和重复文档怎么算？

Q047. “graph-added documents 挤出 baseline 已命中的 documents”从排序机制上怎么发生？请用一个 Top-5 列表说明 fusion 前后候选是怎样被替换的。

Q048. 你怎么定位是“新增 graph candidate 挤占”而不是 entity extraction 错、alias 错、seed 错、路径搜索错或 reranker 错？调试时看了哪些中间产物？

Q049. `baseline-preserving fusion` 的核心规则是什么？是 score normalization、rank fusion、quota、保底 slots 还是别的？为什么它不会简单退化成“永远相信 baseline”？

Q050. 如果 baseline 本身召回的是错误文档，baseline-preserving 机制会不会把错误永久保住并压制 graph signal？你的设计怎样允许 GraphRAG 真正超过 baseline？

Q051. `candidate-aware seed expansion` 具体如何选 seed？它为什么比“从 query entity 全量扩图”更合理？

Q052. seed expansion 的 top-N、score threshold、hop count 或 path budget 怎么定？这些参数对 recall、noise、latency 的敏感性测过吗？

Q053. `entity alias normalization` 做了哪些规范化：大小写、空格、别名表、实体链接、字符串相似，还是模型归一化？哪种错误最危险？

Q054. alias normalization 会把不同实体错误合并。比如同名公司 / 人名冲突时怎样避免 false positive graph expansion？

Q055. `path-aware ranking` 用了哪些特征：path length、edge type、seed score、document relevance、entity coverage？最终是规则分数还是 learned ranker？

Q056. 路径越短一定越好吗？如果真正支持答案的证据在较长 path 上，而短 path 只是高频噪声，你怎样防止 path-length bias？

Q057. 你连续做了 fusion、seed expansion、alias normalization、path-aware ranking 四项修改，却只给同日最终 rerun。没有逐项 ablation，你凭什么知道每项都必要，而不是其中一项就解决了问题？

Q058. 同一天对同一小样本调到 `Recall@5=1.00`，非常容易 overfit。你做了什么来防止“看着失败样本改到全对”却对未见 query 退化？

Q059. `fallback_count=1` 具体表示什么？一次 fallback 是质量保护还是系统失败？如果 fallback 频率变高，你会怎样判断 GraphRAG 没有提供净收益？

Q060. 如果把 Top-K 从 5 改成 10，GraphRAG 可能出现什么新问题？为什么一个 `limit=5` smoke 不能代表更大的 candidate budget？

Q061. 这套 GraphRAG 相比 baseline 增加多少 query latency、图查询、embedding / rerank 次数和内存成本？没有数字时你会怎样设计 measurement，而不是口头说“可以接受”？

Q062. corpus 更新以后，vector index 和 graph index 如果不同步会发生什么？你怎样给同一材料版本建立一致的检索视图？

Q063. 如果 graph 中某个实体 / 边来自低质量或恶意文档，它可能把检索扩展到错误区域。你怎样限制 graph poisoning 对最终 candidate set 的影响？

Q064. 假设一个更简单的 Hybrid RAG 在正式业务集上已经达到相同质量，而且延迟更低，你会删掉 GraphRAG 吗？你的 kill condition 是什么？

Q065. 设计一个你愿意拿去决定“GraphRAG 是否进入默认路径”的正式 benchmark：dataset、query class、baseline、指标、ablation、统计方式、latency/cost gate 和 failure analysis 分别怎么做？

## Attack Chain D — Context / Memory

Q066. Context / Memory V2 出现前，最简单的 recent window + task summary 方案哪里失败？请给一个具体长任务例子，而不是泛泛说“上下文会变长”。

Q067. 你说“typed Context / Memory contracts”。请说出核心 contract 至少有哪些字段，哪些字段属于 identity / scope，哪些属于 provenance，哪些属于内容本身？

Q068. `scoped memory` 的 scope 由哪些维度构成？user、workspace/project、agent、thread/task 如果同时存在，读取时怎么匹配，写错一个维度会造成什么后果？

Q069. scope isolation 最终在哪里 enforce：SQL query、repository layer、ContextOrchestrator、Python request-local state，还是多个位置？哪一层是安全边界？

Q070. 从一次模型调用开始，完整讲 `GeneralAgent.prepare_context()` 的调用链：谁传入 task，谁构造 Context Pack，谁读 Memory，谁做 policy，最后什么进入模型 prompt？

Q071. `ContextOrchestrator` 解决了什么不能直接写在 `GeneralAgent` 里的问题？它的输入输出 contract 是什么？如果删掉它，系统会怎样退化？

Q072. pre-call readback 同时读 same-scope task summary 和 `APPROVED` structured memory。两者顺序、优先级、冲突处理和 token budget 怎么决定？

Q073. “只读取 APPROVED structured memory”这个条件在哪里过滤？如果状态在读取后、模型调用前被撤销，会不会把已经失效的 memory 继续喂给模型？

Q074. 谁把一条 structured memory 从 candidate / pending 变成 APPROVED？简历中的 PR #8 是实现了完整审核生命周期，还是只实现 read gate / contract？请把 Ownership 边界说清楚。

Q075. 一条已经 APPROVED 的 memory 写“付款日是 6 月 1 日”，后来权威材料变成 6 月 15 日。系统怎样发现 stale memory，并阻止它持续污染上下文？

Q076. `source-id trace` 粒度是什么：source document、chunk、message、task result 还是更细？如果多个来源支持同一 memory，provenance 怎么表达？

Q077. Memory 内容本身是不可信数据。你怎样防止历史 memory 中的文本被模型当成 system instruction，形成 prompt injection / instruction-data boundary 问题？

Q078. post-turn integration 写什么：raw event、summary、structured memory candidate，还是全部？写入发生在模型返回之后哪个时点？

Q079. 如果模型已经把答案返回给用户，但进程在 post-turn memory write 前 crash，恢复后怎么判断该不该补写？

Q080. 同一个 turn 因 retry 被处理两次，怎样避免重复写 summary / memory event？你的 idempotency identity 放在哪里？

Q081. 同一 thread 有两个并发任务都想更新 task summary，怎样避免 lost update？如果用 PostgreSQL，你会选 optimistic version、row lock 还是 append-only event，为什么？

Q082. 从数据库基础解释：READ COMMITTED、REPEATABLE READ、SERIALIZABLE 对“读取 scope memory + 更新 summary”各能防什么，不能防什么？你会把事务边界放在哪里？

Q083. structured memory 如果很多，召回是全量塞进 Context Pack 还是有 ranking / limit？如果目前只有 foundation，没有成熟 retrieval，你会怎样诚实描述这一边界？

Q084. PR 记录 focused tests `32 passed`。这 32 个 test 最关键的正例和负例是什么？它们能证明 scope / approval / provenance 到什么程度，又不能证明什么真实运行能力？

Q085. 为什么自己做 Context / Memory contracts，而不是直接采用 LangGraph Store、Mem0、OpenViking 或其他 memory provider？你真正需要自有的是存储检索，还是 scope / review / provenance contract？成熟 provider 补齐以后哪些代码应该删除？

## Attack Chain E — Architecture, Build/Buy, failure and simplification

Q086. 你的架构复盘先把最简单方案说清楚：如果只是一次性的法律问答，一条从权限检查、检索、引用到模型返回的最短链路是什么？

Q087. 从这个 baseline 往上增加复杂度时，分别是什么具体业务条件迫使你引入材料版本、机器候选 / 正式成果分离、长任务恢复、持续权限检查和外部副作用管理？

Q088. “机器候选与正式工作成果分开”在数据模型和写入权限上应该怎么体现？如果都只是同一张表一个 `status` 字段，为什么可能不够？

Q089. 一份新材料进入以后，旧分析可能失效。系统如何知道哪些结果受影响、哪些历史结果只能标记失效而不能直接覆盖？

Q090. 长任务有 checkpoint 以后，为什么还需要单独的业务状态？举一个“checkpoint 显示未完成，但业务提交其实已经成功”或相反的 crash window。

Q091. 外部 POST timeout 后，你不知道远端是否成功。设计一条恢复链：稳定 action identity、attempt、unknown outcome、reconcile、retry / compensate 分别在什么条件下发生？

Q092. 权限在长任务运行中途被撤销。哪些动作必须重新鉴权？如果入口鉴权已经通过，为什么仍不能把 authorization 缓存到整条任务结束？

Q093. 你说通用 Agent Host 应优先复用。请给出 Adopt / Extend / Build / Defer 的决策表：会话、长任务、Tool、Memory、法律业务状态分别倾向哪一类，决定因素是什么？

Q094. Multi-Agent 在什么任务上比“单 Agent + parallel tools”真正有优势？如果没有质量收益或只增加 token / failure surface，你的删除条件是什么？

Q095. 你写“只有评测证据支持时才保留复杂度”。GraphRAG、Memory、Multi-Agent、原生 Runtime 各自至少需要什么 baseline 和指标才能过 gate？

Q096. 你描述的是责任边界，不一定是微服务。什么时候模块化单体就够，什么时候真的应该拆独立 Worker / Network Service？请用吞吐、隔离、故障半径、网络出口或发布节奏给触发条件。

Q097. 如果多个逻辑模块仍在同一个 PostgreSQL 和 Python 进程里，模块边界怎样避免退化成“大家都能直接改彼此表”？你会用 repository/API、schema、transaction owner 还是别的约束？

Q098. 设计一条端到端 Trace：从用户请求到 retrieval、model call、tool call、正式工作成果和外部 effect，哪些 correlation / causation id 必须贯穿，才能在事故后还原发生了什么？

Q099. 简历同时有具体历史实现和“后续架构设计”。请逐条标出 Tool Calling、GraphRAG、Context / Memory、架构复盘中哪些是你已经实现并测试过，哪些只是参与设计，哪些效果仍未测量。面试官最应该防你把哪一类混在一起？

Q100. 如果今天从头重做 Zuno，同时允许直接采用最新成熟 Agent 平台，你会保留哪三个 Zuno-specific contract，删掉哪三类自研复杂度？你的答案怎样证明你是在解决法律工作问题，而不是维护已经写出来的架构？

## Red explicit quality metadata

### High-risk claims covered
- Project reality / Pilot / personal ownership: Q001–Q015
- Tool Calling / MCP implementation: Q016–Q040
- GraphRAG regression / ranking / eval: Q041–Q065
- Context / Memory contracts / persistence / isolation: Q066–Q085
- Reuse-first architecture / failure / measurement / deletion: Q086–Q100

### Attack-angle coverage
- Resume grounding: all questions
- Implementation / data flow / state: Q017–Q039, Q047–Q056, Q067–Q083, Q088–Q098
- Build / Buy / Extend / Defer: Q040, Q064–Q065, Q085, Q093–Q096, Q100
- Failure / recovery / security: Q026, Q036–Q039, Q062–Q063, Q073–Q081, Q089–Q092, Q098
- Evidence / measurement: Q002, Q006–Q010, Q035, Q042–Q046, Q057–Q065, Q084, Q095, Q099
- Fundamentals derived from project: Q021–Q023, Q036–Q039, Q044–Q046, Q062, Q077, Q080–Q082
- Simplification / deletion: Q040, Q064, Q071, Q085, Q086, Q093–Q096, Q100

### Duplicate check
No question is intended as a synonym-only repeat. Repeated concepts appear only when they move to a different chain position: e.g. GraphRAG metrics → overfit / ablation → production gate; Memory scope → database isolation → stale authority; Tool routing → network uncertainty → idempotency / cancellation.

### Firewall note
This is a `CHATGPT_AUTO` round with `LOGICAL_GITHUB_MEDIATED` isolation, not strict blind-Red certification. Formal Red inputs for this stage were limited to the frozen resume, manifest role configuration, attack-model and general technical knowledge.
