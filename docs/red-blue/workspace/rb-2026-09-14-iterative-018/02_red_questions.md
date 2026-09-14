# Red Interview Plan — rb-2026-09-14-iterative-018

question_count: 100
seed_question_count: 8
live_followups: DYNAMIC
one_question_one_intent: true
primary_persona: 大厂 Agent / AI 应用工程一面，偏项目工程深挖
cross_personas:
- skeptical backend engineer
- RAG / retrieval engineer
- agent systems engineer
formal_input_head: 4fbea3f76dd0e9ff863028e67c0a0fdcbaee92ba
red_questions_status: DRAFT_REVIEW

## Interview threads

- **A — Tool/MCP call-chain simplification**; risk: HIGH. 简历声称从 MCP Tool 经子 Agent 转发改为主 Agent 直接绑定 Tools。重点判断候选人是否真的理解旧链路、配置注入位置、并发隔离、工具规模与 Build/Buy，而不只会说“少一层更简单”。
- **B — deterministic direct route / ReAct fallback**; risk: HIGH. 重点判断路由判定是否真实存在、两类请求的边界如何划分、bad case 如何复现、测试到底锁住了什么。
- **C — GraphRAG ranking regression / baseline-preserving fusion**; risk: VERY_HIGH. 重点判断候选人能否讲清“加 graph 后反而变差”的诊断、candidate ordering、baseline rank、graph evidence、Top-K displacement 与小样本证据边界。
- **D — multi-hop graph retrieval**; risk: HIGH. 重点判断 seed expansion、alias normalization、path ranking 各自解决什么问题，以及扩展噪声、路径偏置、延迟和启用条件。
- **E — scoped Context / Memory**; risk: HIGH. 重点判断 scope 是真实状态边界还是命名包装，pre-call read / post-turn write 如何工作，并发、stale read、token budget 怎么处理。
- **F — Memory readback / review / provenance**; risk: HIGH. 重点判断为什么 Memory 需要准入、APPROVED 语义是什么、来源追踪做到哪、撤销和污染怎么办。
- **G — Agent architecture / Build-Buy / evolution**; risk: HIGH. 简历明确写“单 Agent”。从候选人的理由自然追问：什么时候单 Agent 足够，什么时候应该拆 Specialist / Subgraph / Multi-Agent，新增协调复杂度由什么问题证明值得。
- **H — Ownership / evidence / Pilot boundaries**; risk: MEDIUM-HIGH. 判断上述强 Claim 哪些是候选人本人改动，哪些是团队基础；Pilot / smoke / focused test 是否被说大。

## SPOKEN_SEEDS

S001. Zuno 这段你挑一块自己做得最深的讲吧。

S002. 你这里把 MCP Tool 从子 Agent 里拿出来直接给主 Agent，最开始为什么要改？

S003. direct route 和 ReAct 两条路同时留着，你是怎么判断一个请求该走哪条的？

S004. GraphRAG 那次为什么会出现加了 graph 以后反而检索变差？

S005. 你写了 baseline-preserving fusion，这个 preserve 具体是怎么做到的？

S006. Memory 这块你自己最主要改的是哪一段？

S007. 你这里一直写单 Agent，这个是刻意的设计选择，还是当时先这么做？

S008. 如果现在让我打开一段最能代表你这段经历技术深度的代码，你会选哪一段？

## FOLLOWUP_POLICY

1. 每次 Blue 回答后只抽取 1–3 个 observable handles：具体技术名、数字、失败、选择、Ownership、状态或参数。
2. 下一问只选择当前信息增益最高的一个 handle，不按 Pressure Suite 编号继续。
3. 候选人给出精确数字，先问“这个数怎么来的”；得到样本/指标后再决定是否追 dataset、holdout、ablation。
4. 候选人说“我们”，在不打断技术主线的前提下自然确认“这块你自己主要做哪段”。
5. 候选人说出真实 bad case，优先停留在该 failure：现象 → 定位 → 改动 → 验证。
6. 候选人把某层说成“为了简化”，继续追“简化掉了什么状态/调用/失败面”，避免接受抽象口号。
7. 候选人提到 single Agent / specialist / subgraph / multi-Agent 时，围绕问题规模、状态共享、失败隔离和协调成本追问；不预设某种架构正确。
8. 同一 Claim 连续两轮无法建立个人实现或具体机制时，触发 `KILL_SWITCH: CLAIM_IMPLEMENTATION_NOT_ESTABLISHED`，自然换 thread。
9. 项目线足够深以后，可以自然下钻 Python async、DB isolation、HTTP/TCP timeout、Recall/MRR/Top-K 等基础。
10. Red 不使用 Zuno docs 或隐藏答案纠正候选人；候选人若合理纠正前提，更新理解后继续。

## BRANCH_EXAMPLES

### Branch A — Tool Calling，从“少一层”追到并发隔离

candidate_answer_summary: 旧链路要先进入 MCP 子 Agent，再由它选择和调用 Tool，用户级 Server 配置也要跨 Agent 传递，所以改成主 Agent 直接绑定具体 Tools。
next_spoken_question: 多这一层最具体的问题是什么？
why_this_handle: 候选人给出了“多一层”和“配置跨层”两个可验证 handle，先要求具体 failure / complexity。

candidate_answer_summary: 候选人说明 Tool schema、调用上下文和用户配置需要在两层之间同步，排查调用问题也更绕。
next_spoken_question: 那直接绑到主 Agent 以后，用户配置具体在哪一层注入？
why_this_handle: 从抽象简化进入实际调用边界。

candidate_answer_summary: 候选人说配置在 Tool call 时按 Tool–Server 关系注入，而不是初始化时全局写死。
next_spoken_question: 同一个进程里两个用户并发调用同一个 Tool，会不会串配置？
why_this_handle: call-time user config 自然产生并发隔离风险。

candidate_answer_summary: 候选人解释请求级上下文或显式参数传递，不依赖共享可变全局状态。
next_spoken_question: 这个隔离你是怎么测的？
why_this_handle: 从机制进入 evidence。

candidate_answer_summary: 候选人能说出并发/不同用户配置 regression test 或明确承认未测。
next_spoken_question: 如果工具数量涨到两百个，你还会把它们都直接暴露给主 Agent 吗？
why_this_handle: 已建立当前实现后，进入扩展性和架构删除/演化条件。

### Branch C — GraphRAG，从 regression 追到 ranking semantics

candidate_answer_summary: graph 扩出来的新文档进入候选集后，把 baseline 已经命中的文档挤出了 Top-K。
next_spoken_question: 你怎么确认这是排序问题，不是 graph 本身没召回到东西？
why_this_handle: 区分 recall failure 与 ranking regression。

candidate_answer_summary: 候选人能对比 baseline candidate、graph-added candidate 和最终 Top-K。
next_spoken_question: 你所谓 preserve baseline，代码里到底 preserve 的是什么？
why_this_handle: 把 marketing term 压到 ranking state。

candidate_answer_summary: 候选人提到 baseline rank / candidate group / graph signal。
next_spoken_question: graph-only candidate 在什么情况下可以超过 baseline candidate？
why_this_handle: 直接测试 fusion rule 是否只是“baseline 永远优先”。

candidate_answer_summary: 候选人描述需要足够 graph evidence 才晋升。
next_spoken_question: 这样会不会把真正有价值的多跳证据压住？
why_this_handle: 从 correctness 进入 trade-off。

candidate_answer_summary: 候选人提到 Recall/MRR/chain metric 或小样本 smoke。
next_spoken_question: 你这组样本一共多少条，能证明到什么程度？
why_this_handle: 检查 evidence honesty，不允许小样本升级成 benchmark。

### Branch F — Memory，从 scope 追到 read-time authority

candidate_answer_summary: Memory 按 scope 读取，只把审核通过的 structured memory 放进上下文。
next_spoken_question: 这个 scope 具体由什么决定？
why_this_handle: scope 是核心边界，需要落到 key / state，而不是停留在名词。

candidate_answer_summary: 候选人说明用户、workspace、task 等作用域关系。
next_spoken_question: 同一个用户开两个不同任务时，什么信息允许互相看见？
why_this_handle: 用具体隔离场景验证 scope 语义。

candidate_answer_summary: 候选人区分 task summary 和更长期 structured memory。
next_spoken_question: 为什么 structured memory 还要审核，写进去就直接读不行吗？
why_this_handle: 进入 admission / poisoning 风险。

candidate_answer_summary: 候选人解释模型提取可能错误，APPROVED 才进入 readback。
next_spoken_question: 已经取出来以后又被撤销了，这一轮请求怎么办？
why_this_handle: 从静态 gate 进入时序与 freshness。

### Branch G — 单 Agent 是否值得保留

candidate_answer_summary: 候选人说单 Agent 当时更简单，Tool 和 Memory 都集中在一条执行链里。
next_spoken_question: 什么情况出现以后，你会觉得单 Agent 不够了？
why_this_handle: 让候选人自己给复杂度出现条件，而不是面试官预设方案。

candidate_answer_summary: 候选人提到专业角色差异、上下文过大、并行任务或权限隔离。
next_spoken_question: 这个问题你会先拆 Agent，还是先拆 Tool / Subgraph？
why_this_handle: 测试是否把“多 Agent”当默认答案。

candidate_answer_summary: 候选人给出选择标准。
next_spoken_question: 如果拆成多个 Agent，它们共享什么状态？
why_this_handle: 多 Agent 的真正成本从角色数量转向 coordination / state ownership。

candidate_answer_summary: 候选人描述共享 context / durable state / message handoff。
next_spoken_question: 一个子 Agent 超时或者重复返回结果，谁决定下一步？
why_this_handle: 从拓扑进入 failure ownership 和 recovery。

## PRESSURE_SUITE

### Tool / MCP strategy
Q001. [A] 当时旧 Tool Calling 链路具体长什么样？ trigger: candidate claims strategy refactor
Q002. [A] 多一层 MCP 子 Agent 给你带来的第一个真实问题是什么？ trigger: extra-hop claim
Q003. [A] 直接绑定具体 Tool 后，Tool schema 是什么时候暴露给模型的？ trigger: direct binding detail
Q004. [A] 用户级 Server 配置为什么不在 Agent 初始化时一次性绑定？ trigger: call-time injection
Q005. [A] 两个用户并发调用同一个 Tool 时，配置怎么隔离？ trigger: per-user config
Q006. [A] 一次长任务中途 Server 配置变了，你使用哪一版？ trigger: mutable config
Q007. [A] MCP Tool discovery 结果过期时，你怎么处理？ trigger: discovery freshness
Q008. [A] Tool 数量很多以后，全部直接给主 Agent 会发生什么？ trigger: scale
Q009. [A] 两个 MCP Server 暴露同名 Tool 怎么办？ trigger: naming collision
Q010. [A] 不同 MCP Tool 返回格式差异很大时，你在哪一层收敛结果？ trigger: result handling
Q011. [A] remote Tool timeout 时，你怎么区分“没执行”和“执行了但没回包”？ trigger: remote failure
Q012. [A] 这层为什么没有直接交给 LangGraph / MCP SDK 自带能力？ trigger: build-buy

### Workspace routing
Q013. [B] direct route 的判定条件到底是什么？ trigger: routing claim
Q014. [B] 一个请求参数缺了一半时为什么不直接 route？ trigger: incomplete parameters
Q015. [B] 错把复杂请求判成 direct route，最坏会怎样？ trigger: false direct
Q016. [B] 错把简单请求送进 ReAct，成本体现在哪？ trigger: false ReAct
Q017. [B] 天气自然语言参数抽取最开始错在哪里？ trigger: weather bad case
Q018. [B] 自定义 MCP 名称为什么会出现递归？ trigger: recursion bad case
Q019. [B] 你给这两个 bug 写的 regression test 分别锁什么行为？ trigger: tests
Q020. [B] 线上如果 route 选错，你准备看什么日志判断？ trigger: observability
Q021. [B] direct route 会不会绕过 Agent 原本的安全或上下文逻辑？ trigger: bypass risk
Q022. [B] 多轮对话里的“继续查刚才那个城市”还能走 direct route 吗？ trigger: conversational state
Q023. [B] ReAct fallback 自己进入循环时怎么停？ trigger: fallback loop
Q024. [B] 新增一种 Tool 以后，route rule 谁来维护？ trigger: extensibility
Q025. [B] 什么测量结果出现时你会删掉 direct route，只留 ReAct？ trigger: deletion condition

### GraphRAG ranking regression / fusion
Q026. [C] 你最早从什么现象判断 GraphRAG 变差了？ trigger: regression signal
Q027. [C] 你当时 baseline 和 GraphRAG 是怎么对比的？ trigger: baseline
Q028. [C] 为什么你判断是 ranking regression，不是 recall 不足？ trigger: diagnosis
Q029. [C] fusion 前你手里有哪些 candidate group？ trigger: candidate model
Q030. [C] baseline rank 在后续融合里怎么保存？ trigger: preserve semantics
Q031. [C] 你说的 graph evidence 具体是什么信号？ trigger: graph signal
Q032. [C] graph-only candidate 满足什么条件才允许晋升？ trigger: promotion rule
Q033. [C] 两个候选分数相同怎么打破平局？ trigger: deterministic ranking
Q034. [C] Vector、BM25 和 graph score 不在同一尺度时怎么处理？ trigger: score normalization
Q035. [C] fusion 里有没有人工权重？ trigger: parameter
Q036. [C] graph 噪声最常见是从哪一步进来的？ trigger: noise source
Q037. [C] baseline-preserving 会不会压制真正重要的 graph-only 文档？ trigger: trade-off
Q038. [C] 同一文档从多个路径召回时怎么去重？ trigger: duplicate candidate
Q039. [C] 你怎么避免某一路 score 天然更大把其他路吞掉？ trigger: cross-retriever comparability
Q040. [C] Top-K 从 5 改成 20 后，你预期这个 regression 还明显吗？ trigger: top-k sensitivity
Q041. [C] Recall 和 MRR 在这个问题上分别告诉你什么？ trigger: metrics
Q042. [C] 为什么开发 smoke 只有 5 条？ trigger: sample scope
Q043. [C] 这 5 条是修之前就固定的吗？ trigger: holdout/leakage
Q044. [C] 没做 ablation 的情况下，你敢把收益归因给哪一项改动？ trigger: causality
Q045. [C] fallback 出现一次意味着什么？ trigger: fallback metric
Q046. [C] GraphRAG 这套增强带来了多少延迟成本？ trigger: latency
Q047. [C] 什么 query 分布下你会直接关掉 GraphRAG？ trigger: deletion condition

### Multi-hop graph retrieval
Q048. [D] seed expansion 最开始拿什么作为 seed？ trigger: seed expansion
Q049. [D] seed 选错以后后面的图扩展会发生什么？ trigger: error propagation
Q050. [D] candidate-aware 具体比原来的 seed 逻辑多了什么判断？ trigger: implementation
Q051. [D] expansion 深一层就多很多节点时怎么控噪声？ trigger: graph explosion
Q052. [D] entity alias normalization 最容易误合并哪类实体？ trigger: alias collision
Q053. [D] 同名但不同实体怎么避免被 alias 合并？ trigger: disambiguation
Q054. [D] path-aware ranking 到底给 path 哪些信息加分？ trigger: path features
Q055. [D] 长路径是不是天然吃亏？ trigger: path length bias
Q056. [D] 图里有 cycle 时你怎么避免重复扩展？ trigger: cycles
Q057. [D] path evidence 和单个文档相关性冲突时你信谁？ trigger: evidence conflict
Q058. [D] 你怎么判断一条多跳 chain 算“完整命中”？ trigger: chain metric
Q059. [D] 图更新以后旧的 alias / path cache 怎么失效？ trigger: staleness
Q060. [D] 你会怎么判断一个 query 值得进入 graph expansion？ trigger: query gating
Q061. [D] 为什么不把 GraphRAG 永远作为默认检索路径？ trigger: complexity cost

### Context / Memory
Q062. [E] 你这里的 scope 到底是什么意思？ trigger: scope claim
Q063. [E] scope 由哪些 key 组成？ trigger: state key
Q064. [E] scope 写错一次最严重会造成什么？ trigger: isolation failure
Q065. [E] 同一用户两个 workspace 的 Memory 能互相读吗？ trigger: tenant/workspace boundary
Q066. [E] pre-call readback 在模型调用前哪一步发生？ trigger: call chain
Q067. [E] post-turn write 是同步还是异步？ trigger: write path
Q068. [E] ContextOrchestrator 自己真正拥有哪类决策？ trigger: ownership
Q069. [E] Memory 太多超过 token budget 时怎么选？ trigger: context budget
Q070. [E] task summary 和 structured memory 冲突时哪个优先？ trigger: conflict
Q071. [E] 同一个 scope 两个并发 turn 同时写会怎样？ trigger: concurrent writes
Q072. [E] 一次请求读到旧 Memory 后，新写入刚好提交，当前请求怎么办？ trigger: stale read
Q073. [E] 用户要求删除一条 Memory 后，已有缓存怎么处理？ trigger: revocation
Q074. [F] structured memory 为什么必须 APPROVED 才能 readback？ trigger: admission
Q075. [F] APPROVED 这个状态是谁产生的？ trigger: authority
Q076. [F] Memory 取出来以后 approval 被撤销，你如何保证 freshness？ trigger: TOCTOU
Q077. [F] provenance 最少要能追到哪一级？ trigger: provenance depth
Q078. [F] source trace 是为了 debug，还是会影响业务判断？ trigger: purpose
Q079. [F] 如果模型把错误事实写成 Memory，系统靠什么阻止污染扩散？ trigger: poisoning
Q080. [F] 你怎么证明加 Memory 比不加更好？ trigger: evaluation

### Agent architecture / evolution
Q081. [G] 当时为什么选择单 Agent？ trigger: single-agent claim
Q082. [G] 什么信号出现时你会考虑拆成多个 Agent？ trigger: split condition
Q083. [G] 多 Agent 之间最难共享的状态是什么？ trigger: coordination
Q084. [G] Supervisor 自己会不会变成新的单点和瓶颈？ trigger: supervisor
Q085. [G] 一个 Specialist 应该做成 Agent 还是普通 Tool，你怎么判断？ trigger: agent-vs-tool
Q086. [G] Subgraph 和独立 Agent 的边界你会怎么划？ trigger: topology
Q087. [G] 多 Agent 共用 Memory 时如何避免互相污染上下文？ trigger: shared memory
Q088. [G] 子 Agent 超时重试导致重复工作时谁负责去重？ trigger: failure coordination
Q089. [G] 如果通用 Agent Host 已经能做 orchestration，Zuno 还需要自己保留什么？ trigger: build-buy
Q090. [G] 哪一层复杂度如果测不出收益，你会最先删？ trigger: deletion condition

### Ownership / evidence / fundamentals
Q091. [H] 这六条里哪一条是你个人代码改动最多的？ trigger: ownership
Q092. [H] 你接手之前已经有的东西和你新增的东西怎么分？ trigger: before/after
Q093. [H] 你写 Pilot Validation，具体到什么程度你才会叫它 Pilot？ trigger: pilot boundary
Q094. [H] 这个项目哪些东西你明确不会说成 Production？ trigger: evidence honesty
Q095. [H] 除了 focused unit/regression test，你做过什么跨组件验证？ trigger: test depth
Q096. [H] Python async 场景里，请求级状态为什么容易串？ trigger: fundamentals pivot
Q097. [H] 如果你用 ContextVar 做请求上下文，它在新 Task 里怎么传播？ trigger: Python fundamentals
Q098. [H] Memory 并发写入时数据库 isolation level 会影响什么？ trigger: DB fundamentals
Q099. [H] HTTP 请求 timeout 为什么不能直接等价于远端没执行？ trigger: network fundamentals
Q100. [H] 如果今天重新做一次，你最想推翻当前哪一个设计决定？ trigger: engineering judgment

## Red self-check

- Seeds 都能直接从冻结简历自然产生，没有读取 Zuno docs。
- Spoken question 保持一个主要意图；Pressure Suite 中的标签和 trigger 只属于离线 Controller metadata。
- Branch A / C 都能自然连续追到 5 层，Branch F / G 能进入状态边界和架构选择。
- GraphRAG 数字不作为预设攻击答案；Red 只看到简历里的 `5-query smoke` 和“恢复 baseline 水平”，会通过追问确认证据边界。
- Single Agent 线程是开放设计攻击：允许继续 single Agent、拆 Tool/Subgraph、拆 Specialist/Multi-Agent 或复用通用 Host，只看候选人能否从约束推导选择。
- Ownership、Build/Buy、failure、evaluation、Python/DB/network fundamentals 都有入口，但不会在现场平均覆盖。
- `KILL_SWITCH` 只作为内部 policy，不会说给候选人。
- Live Interview 不逐题朗读本 Pressure Suite；每个正式 follow-up 必须等上一答 commit 后再生成。
