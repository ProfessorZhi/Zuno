# Red Questions — rb-2026-09-13-red-calibration-015

question_count: 100
primary_path_count: 30
reserve_count: 70
primary_persona: Implementation Interviewer
cross_personas: Forensic Interviewer / Open-source Skeptic / Fundamentals Interviewer
formal_input_head: fa4fdbab8692cd4331de59b3999e2782c1020146
red_questions_status: DRAFT_REVIEW

## Claim map

- **Claim A — Project reality / personal ownership / Pilot boundary** — risk: HIGH. 项目有真实 Demo、法院侧测试、Pilot 等高可信度词，但候选人明确是在已有系统上参与，需要尽早确认本人增量与真实落地边界。
- **Claim B — Agent / Tool Calling / MCP** — risk: HIGH. 简历直接出现 `GeneralAgent`、tool→server 配置注入、deterministic direct route / ReAct fallback、具体 bug 和 regression artifacts，天然允许函数级追问。
- **Claim C — GraphRAG retrieval quality** — risk: CRITICAL. 简历同时出现四个具体算法名和精确指标，是本轮最值得优先验证的实现 Claim。
- **Claim D — Context / Memory V2** — risk: HIGH. 简历出现 typed contracts、scope、`prepare_context()`、`ContextOrchestrator`、`APPROVED` gate 和 `32 passed`，需要验证是否真正掌握 contract / data flow / test。
- **Claim E — Architecture / reuse-first / measurement-gated complexity** — risk: MEDIUM. 适合验证 Build/Buy、failure semantics 与删复杂度能力，但 Implementation 一面不应让它压过 B/C/D。

# PRIMARY_PATH

> 目标：模拟约 45–60 分钟技术一面。条件不满足时跳过，不机械执行全部 30 题。

### P001
**question:** 用 60 秒讲 Zuno：谁在什么场景下遇到什么问题，你参与的部分是什么？先不要讲九层架构或框架名。
**claim:** A
**ask_if:** ALWAYS
**kill_switch:** none

### P002
**question:** 你写的是“在已有系统基础上参与”。你加入时已经有什么、最早属于你自己的增量是什么？请落到一个代码对象、测试或数据流，而不是“参与 Agent / RAG”。
**claim:** A
**ask_if:** ALWAYS
**kill_switch:** none

### P003
**question:** 这四条 bullet 里，哪些你敢在面试现场说“我实现了”，哪些只能说“我参与 / 复盘”？如果团队已有代码很多，你怎么界定自己的 Ownership？
**claim:** A
**ask_if:** ALWAYS
**kill_switch:** none

### P004
**question:** 如果我现在只能打开一段你最熟的 Zuno 代码或一个 test file，你选哪一个？入口、主要输入输出、你改了什么、怎么验证，按这个顺序讲。
**claim:** A / B / C / D
**ask_if:** ALWAYS
**kill_switch:** 如果候选人对四条具体 bullet 都无法指出任何本人熟悉的实现对象，标记 `GLOBAL_IMPLEMENTATION_OWNERSHIP_WEAK`，后续每条 Claim 只做最小验证，不做长链深挖。

### P005
**question:** 先讲 GraphRAG 那次失败。`Recall@5` 从 baseline 1.00 到 local 0.80 时，最小的可复现现象是什么？给我一个 query，看 baseline Top-K 和 GraphRAG Top-K 是怎么变坏的。
**claim:** C
**ask_if:** ALWAYS
**kill_switch:** none

### P006
**question:** `baseline-preserving fusion` 到底是什么算法？输入有哪些 candidate / score / metadata，排序或保底规则是什么，Graph candidate 在什么条件下仍然允许超过 baseline candidate？
**claim:** C
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** 如果候选人只能复述“保护 baseline”但无法描述任何实际排序规则、输入信号或 test assertion，标记 `CLAIM_C_IMPLEMENTATION_NOT_ESTABLISHED`；跳过 P007/P008/P010/P012，保留 P009/P011/P013 做 Evaluation / claim-boundary 检查后转 Claim B。

### P007
**question:** 四个改动里任选 `candidate-aware seed expansion`、`entity alias normalization`、`path-aware ranking` 一个，按“改前失败 → 代码怎么改 → 为什么预期有效 → test 怎么断言”完整讲一遍。
**claim:** C
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** 如果仍无法落到实现机制，触发 `CLAIM_C_IMPLEMENTATION_NOT_ESTABLISHED`。

### P008
**question:** 你连续改了 fusion、seed、alias、path ranking。它们之间是四个独立问题还是一条因果链？如果没有逐项 ablation，你凭什么保留四个，而不是其中一个就够？
**claim:** C
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** none

### P009
**question:** 解释你简历里的评测口径：`limit=5` 到底限制什么，Top-K 是多少，`Recall@5`、`MRR@10`、`FullChainHit@5` 分别在判什么？如果这些定义你说不清，精确数字为什么值得写在简历上？
**claim:** C
**ask_if:** ALWAYS
**kill_switch:** none

### P010
**question:** baseline 和 local GraphRAG 的 corpus、query、embedding、rerank、Top-K、route policy 是否同口径？你怎样避免把配置漂移误当成算法收益？
**claim:** C
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** none

### P011
**question:** 同一小样本上从 0.80 调回 1.00 很容易 overfit。你现在最多能声称什么，绝对不能声称什么？下一轮最小的验证应该怎么设计？
**claim:** C
**ask_if:** ALWAYS
**kill_switch:** none

### P012
**question:** GraphRAG 质量恢复以后，成本呢？它相对 baseline 多了哪些图查询、候选、rerank 或延迟；如果没有完整成本数字，你准备怎样测，什么结果会让你直接删掉 GraphRAG？
**claim:** C / E
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** none

### P013
**question:** 为什么这个项目需要 GraphRAG，而不是 Hybrid RAG + rerank 就够了？请给一个真正需要关系/多跳结构的 query class；如果普通检索已经达标，你删不删？
**claim:** C / E
**ask_if:** ALWAYS
**kill_switch:** none

### P014
**question:** 回到 Tool Calling。画出 MCPAgent-as-Tool 改造前后的调用链：用户请求、模型、Tool schema、`GeneralAgent`、MCP Server、结果回注分别经过哪里？你的代码改动发生在哪个边界？
**claim:** B
**ask_if:** ALWAYS
**kill_switch:** none

### P015
**question:** `GeneralAgent` 直接绑定 concrete MCP Tools 的生命周期是什么？用户级配置在什么时刻、通过什么 key 绑定到具体 Tool / Server？两个 Server 有同名 Tool 怎么办？
**claim:** B
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** 如果候选人既讲不清 before/after call graph，也讲不清 tool→server/config injection 的最小数据结构或生命周期，标记 `CLAIM_B_IMPLEMENTATION_NOT_ESTABLISHED`；跳过 P016–P019，保留 P020 做证据检查后转 Claim D。

### P016
**question:** 你写“用户级 MCP 配置在调用期注入”。两个用户并发调用同一个 Tool 时，怎样保证 token、endpoint 或 server config 不串？如果是 async Python，请讲 request-local state 的边界。
**claim:** B
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** none

### P017
**question:** deterministic direct route 什么时候可以跳过 ReAct？给一个应该 direct、一个必须 ReAct、一个最容易误判的例子，并说明判定依据不是靠什么拍脑袋阈值。
**claim:** B
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** none

### P018
**question:** direct route 如果已经发出一个有副作用的 MCP/HTTP 调用，但本地 read timeout，随后 fallback 到 ReAct，会不会执行两次？从 TCP/HTTP 能知道什么、不能知道什么，你的重试边界应该怎么设计？
**claim:** B
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** none

### P019
**question:** 你简历点名了 custom MCP 名称递归和高德天气参数解析。任选一个，给最小触发输入、实际错误路径、修复点，以及为什么这个修复不是只 hard-code 一个 demo case。
**claim:** B
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** none

### P020
**question:** `direct-route`、`config-gate`、`structured-result` 这些 regression artifacts 各自在防什么回归？挑两条说具体 assertion、测试层级、哪些是 mock，哪些真的跨边界；如果当时没有 CI run 证据，也直接说。
**claim:** B
**ask_if:** ALWAYS
**kill_switch:** none

### P021
**question:** Context / Memory 这条你写了 typed contracts 和 scoped memory。先别说“分层记忆”，直接列出最关键的 contract 对象、scope 维度，以及哪些字段决定两条 memory 能不能被同一次调用读到。
**claim:** D
**ask_if:** ALWAYS
**kill_switch:** none

### P022
**question:** 从一次 `GeneralAgent.prepare_context()` 调用开始画数据流：输入是什么，`ContextOrchestrator` 做什么，task summary 和 structured memory 在哪里读取、筛选、合并，最后什么进入模型上下文？
**claim:** D
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** 如果候选人对 contract/scope 和 `prepare_context()` data flow 都只能讲概念，标记 `CLAIM_D_IMPLEMENTATION_NOT_ESTABLISHED`；跳过 P023/P024，保留 P025 做证据检查。

### P023
**question:** 为什么 structured memory 只读 `APPROVED`？如果一条 memory 在 context 构建后、模型调用前被撤销或修改，你如何看这个 stale-read race？历史实现做到了哪一步，哪些只是今天你会补的设计？
**claim:** D
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** none

### P024
**question:** post-turn write 如果发生“模型回答已返回，但 memory write 失败 / 重试 / 重复到达”，你怎样避免重复 summary、覆盖别人更新或产生跨 scope 污染？请把历史实现和你认为正确的设计分开讲。
**claim:** D
**ask_if:** CLAIM_STILL_CREDIBLE
**kill_switch:** none

### P025
**question:** PR 写 `32 passed`。不要只报数字：挑两个最关键的 positive test 和两个 negative test，说它们分别证明什么、不证明什么。为什么这些 test 足以叫 foundation/hardening，却不足以叫 production Memory？
**claim:** D
**ask_if:** ALWAYS
**kill_switch:** none

### P026
**question:** 假设业务只是“上传合同后问第 8 条是什么”，为什么不用受控 RAG 直接回答？什么具体 failure condition 出现后你才会引入 Agent、Memory 或长期 Runtime？
**claim:** E
**ask_if:** ALWAYS
**kill_switch:** none

### P027
**question:** LangGraph、MCP SDK、OpenAI/Anthropic Agent SDK 现在都在提供通用 Tool、Persistence、Tracing。你今天重做 Zuno，会把哪些通用能力直接买/复用，哪些业务 Delta 才值得自己维护？
**claim:** E / B / D
**ask_if:** ALWAYS
**kill_switch:** none

### P028
**question:** 一个长任务 checkpoint 显示 completed，但正式业务数据没有提交；另一个场景是外部 POST timeout。为什么这两个“成功/失败”不能用同一个 status 解决？分别应该信谁的事实？
**claim:** E
**ask_if:** ALWAYS
**kill_switch:** none

### P029
**question:** 从你简历列出的 GraphRAG、Memory、Multi-Agent、原生 Runtime 里选一个，你现在最愿意删掉哪个？给清晰的保留指标和 kill condition，而不是“看情况”。
**claim:** E
**ask_if:** ALWAYS
**kill_switch:** none

### P030
**question:** 如果我是面试官，今天最可能怀疑你哪条简历 Claim？你还缺哪类证据或实现细节才能让它从“参与过”变成“我可以独立维护”？
**claim:** A / B / C / D
**ask_if:** ALWAYS
**kill_switch:** none

# RESERVE_FOLLOWUP

> 只有触发条件成立才使用。Reserve 不是第二份必问题单。

## Claim A — Project reality / Ownership

### R001
**question:** 内部 Demo、客户侧/法院侧测试、Pilot Validation 分别是谁在用、什么环境、验证什么？“Pilot”在你这里不等于什么？
**claim:** A
**trigger:** 候选人把真实落地作为核心卖点，或对 Pilot 描述含糊。

### R002
**question:** 项目团队大概多少人？导师、其他同学、平台已有资产和你各自负责什么？谁能 review 你讲的那段代码？
**claim:** A
**trigger:** Ownership 仍不清楚。

### R003
**question:** 你四条工作按时间怎么排？哪些有真实依赖，哪些只是同一项目内并行发生？
**claim:** A
**trigger:** 候选人把所有成果讲成一条过度顺滑的因果链。

### R004
**question:** 讲一个客户/法院侧真实 bad case。原始输入、错误输出、你当时看到的 trace 或数据是什么？如果根因没恢复就明确说没恢复。
**claim:** A
**trigger:** 候选人声称项目有用户反馈或真实场景经验。

### R005
**question:** 项目有哪些环境：本地、CI、Demo、Pilot？配置、模型、数据权限、网络依赖最可能有哪些差异？哪些你真的知道，哪些只是推测？
**claim:** A
**trigger:** 候选人把测试结果和真实环境混在一起。

### R006
**question:** 你开发时用了 Coding Agent 吗？如果用了，它生成过哪些代码；你怎样证明自己能解释最终实现和 failure semantics？
**claim:** A
**trigger:** 需要进一步验证个人工程 Ownership。

### R007
**question:** 谁 review 了 Tool/GraphRAG/Memory 这些改动？没有正式 review 时，你用什么证据证明修改不是一次性“跑通 demo”？
**claim:** A
**trigger:** 候选人依赖 PR/commit 数量作为质量证明。

### R008
**question:** 你进过 PostgreSQL 调实际项目数据。讲一个你查过的数据问题：你从什么表/关系开始，如何缩小问题范围？不要把“会 SQL”当答案。
**claim:** A
**trigger:** 候选人主动提数据库调试经历。

### R009
**question:** 如果我追问历史 QPS、P95、用户数、SLA、故障率，你哪些能回答，哪些必须说没有？为什么“没有”比猜一个数字更可信？
**claim:** A
**trigger:** 候选人把 Pilot 描述得接近 Production。

### R010
**question:** 你做过的最失败的一次判断是什么？不是“发现 bug 然后修好”，而是你原先的技术假设哪里错了，后来为什么改方向？
**claim:** A
**trigger:** 需要判断反思能力或真实项目复杂度。

## Claim C — GraphRAG

### R011
**question:** `gold-like documents` 是正式 gold label 还是调试时的近似说法？如果不是严格 gold，你为什么还能用 Recall 指标？
**claim:** C
**trigger:** 候选人对 label 口径表述含糊。

### R012
**question:** 你说 graph-added docs “挤出” baseline 文档。它是 candidate pool 本身丢失、fusion 排序、rerank，还是 final truncation 导致？你怎么定位到具体阶段？
**claim:** C
**trigger:** 候选人能讲出 regression query，但根因定位仍粗。

### R013
**question:** `baseline-preserving` 会不会把 baseline 的错误也永久保住？怎样允许真正强的 Graph signal 超过 baseline，而不是把 GraphRAG 退化成装饰？
**claim:** C
**trigger:** 候选人讲清 fusion 机制。

### R014
**question:** fusion 前不同来源 score 是否可比？如果 vector score、graph score、rerank score 分布完全不同，你为什么能直接混排？
**claim:** C
**trigger:** 候选人的 fusion 设计依赖跨源 score。

### R015
**question:** 如果你的 fusion 用 rule/threshold，这些阈值怎么定？来自训练集、smoke、经验还是手工？怎样避免把 five-query sample 写死进规则？
**claim:** C
**trigger:** 候选人说明了明确阈值或 tier 规则。

### R016
**question:** candidate-aware seed expansion 为什么从 baseline candidate 取 seed 不会形成确认偏差？baseline 错了会不会把 Graph 也带偏？
**claim:** C
**trigger:** 候选人解释了 candidate-aware seed。

### R017
**question:** seed 太多会带来什么：Neo4j query 数、路径爆炸、噪声、latency？你怎样设置 seed budget / hop budget？
**claim:** C
**trigger:** seed expansion 机制成立。

### R018
**question:** alias normalization 如何处理 “The X (film)” / “X” 这种简单变体之外的同名人、同名公司？什么时候规则归一化应该拒绝自动合并？
**claim:** C
**trigger:** 候选人说明了 alias 规则。

### R019
**question:** 你的 alias 是 deterministic rules 还是 fuzzy/entity-linking？如果没有真正 fuzzy match，为什么命名为 normalization 而不是 entity linking？
**claim:** C
**trigger:** 候选人可能把简单规则包装成高级实体链接。

### R020
**question:** path-aware ranking 的 path feature 是 learned 还是 heuristic？为什么这些 feature 与 HotpotQA 问题类型相关，迁到法律文档会不会失效？
**claim:** C
**trigger:** 候选人讲清 path ranking。

### R021
**question:** path 越短一定越好吗？一个长路径是真实 bridge、短路径只是热门实体时，你的排序如何避免 shortest-path bias？
**claim:** C
**trigger:** path length 被用作排序信号。

### R022
**question:** 多条 path 指向同一个 document 时，你是累积 support 还是取 max？重复路径会不会人为放大某个 doc？
**claim:** C
**trigger:** path support 会回流 document score。

### R023
**question:** `fallback_count=1` 到底什么事件算 fallback？一次 fallback 是安全保护还是质量失败？什么 fallback rate 会触发禁用 GraphRAG？
**claim:** C
**trigger:** 候选人能解释 runner/runtime route。

### R024
**question:** 为什么同时看 Recall、MRR 和 FullChainHit？如果 Recall@5=1 但 MRR 变差，对最终生成会有什么影响？
**claim:** C
**trigger:** metric discussion深入。

### R025
**question:** 五个 query 的 macro average 很脆。你下一轮怎么做 train/dev split 或 frozen holdout，避免“看失败样本调规则再测同一批”？
**claim:** C
**trigger:** 候选人承认 overfit 风险。

### R026
**question:** 没有逐项 ablation 时，你会如何最小成本补 ablation：四个机制全排列、one-at-a-time removal，还是按因果链分组？为什么？
**claim:** C
**trigger:** 候选人准备正式验证四个机制贡献。

### R027
**question:** 如果 HotpotQA limit=10 通过，但 2Wiki/MuSiQue 退化，你会把 GraphRAG 做 query-class gating，还是继续调一个全局策略？
**claim:** C
**trigger:** 候选人讨论跨数据集扩展。

### R028
**question:** corpus 更新后 graph index 和 vector index 版本不一致，会出现什么 retrieval inconsistency？如何让一次 query 知道自己用的是哪一代数据？
**claim:** C / E
**trigger:** 候选人把 GraphRAG 扩到长期业务系统。

### R029
**question:** 如果 graph query timeout 但 vector baseline 已经拿到结果，你会直接返回 baseline、等待 graph、还是按 query class 决策？怎样把 latency budget 写成策略？
**claim:** C / E
**trigger:** Graph path latency 成为明显成本。

### R030
**question:** 如果最终 benchmark 证明 GraphRAG 只在 8% query 上有净收益，你会怎样产品化：默认关、route gating、specialist tool，还是完全删掉？
**claim:** C / E
**trigger:** 候选人能谈 measurement-gated complexity。

## Claim B — Agent / Tool Calling / MCP

### R031
**question:** MCPAgent-as-Tool 这层最初解决什么问题？去掉它以后丢了什么能力，还是纯粹减少了一层模型/路由？
**claim:** B
**trigger:** 候选人讲清 before/after call graph。

### R032
**question:** concrete MCP Tools 是启动时发现、Workspace 初始化时绑定，还是请求级动态构造？生命周期选择会怎样影响配置热更新和连接复用？
**claim:** B
**trigger:** Tool binding lifecycle 可以继续深挖。

### R033
**question:** Tool schema 来自 MCP Server 时，本地如何验证 schema/version 漂移？Server 升级后模型还拿着旧 schema 会怎样？
**claim:** B
**trigger:** 候选人说明 schema discovery 路径。

### R034
**question:** tool→server mapping 的唯一 identity 应包含什么？只用 tool name 的风险是什么？
**claim:** B
**trigger:** 候选人提到 map/key 设计。

### R035
**question:** 用户级配置注入如果通过全局 mutable dict，会有什么并发问题？`ContextVar` 又在哪些线程/executor 边界会失效？
**claim:** B
**trigger:** 并发隔离实现需要下钻 Python 基础。

### R036
**question:** 一个请求并行触发三个 MCP Tools 时，哪些状态可以共享，哪些必须 attempt-local？取消其中一个会不会影响另外两个？
**claim:** B
**trigger:** 系统支持 parallel tool calls 或 candidate 讨论并发。

### R037
**question:** direct route 的 matcher 如果 false positive，比 false negative 更危险还是相反？为什么？
**claim:** B
**trigger:** 候选人讲清 direct route predicate。

### R038
**question:** direct route 怎样处理缺参数？自己补、规则抽取、让模型补，还是 fallback ReAct？不同选择的风险是什么？
**claim:** B
**trigger:** direct route 参数处理成为重点。

### R039
**question:** 高德天气自然语言 parser 如果从“南京明天”扩到“南京和上海后天温差”，你会继续加规则还是把它交回模型？什么信号说明 deterministic parser 应该停止扩张？
**claim:** B / E
**trigger:** 候选人讲到自然语言参数解析。

### R040
**question:** custom MCP 名称递归如果本质是 route cycle，你会怎么做通用 cycle detection？visited set、depth bound、canonical identity 各解决什么？
**claim:** B
**trigger:** recursion bug 的 root cause 已讲清。

### R041
**question:** MCP connect timeout、read timeout、server 500、JSON schema error，哪些可以安全 retry，哪些不能？
**claim:** B
**trigger:** failure semantics 需要分层。

### R042
**question:** 对 read-only Tool 和 mutating Tool，你会不会使用同一个 retry middleware？为什么？
**claim:** B
**trigger:** 候选人给出统一 Retry 方案。

### R043
**question:** idempotency key 应该由 Agent run id、tool call id 还是业务动作 identity 生成？为什么模型重试不能自动换一个 key？
**claim:** B
**trigger:** mutating Tool reliability 深挖。

### R044
**question:** 如果远端不支持 idempotency，也没有 query-by-business-key，你还能自动重试写操作吗？什么时候必须人工 reconcile？
**claim:** B / E
**trigger:** candidate claims robust external effects.

### R045
**question:** `asyncio.CancelledError` 到达本地 task 时，HTTP request 和远端业务动作可能分别处于什么状态？为什么 cancellation 不是 rollback？
**claim:** B
**trigger:** 需要自然下钻 asyncio/network fundamentals。

### R046
**question:** structured-result test 如果只验证 JSON shape，为什么不够？还应验证哪些 semantic fields 或 routing facts？
**claim:** B
**trigger:** regression tests 只讲结构不讲语义。

### R047
**question:** config-gate 缺配置时应该 fail closed、提示补配置还是 fallback 默认 Server？安全和可用性怎么取舍？
**claim:** B
**trigger:** config gate 行为仍不清晰。

### R048
**question:** 如果今天 MCP SDK / Agent SDK 已经提供稳定 tool discovery、schema binding 和 tracing，你这层自定义实现还有哪三件事值得保留？其余删不删？
**claim:** B / E
**trigger:** Build/Buy 深挖。

## Claim D — Context / Memory

### R049
**question:** Memory scope 最少需要 tenant/user/matter/task/session 中哪些维度？少一个会发生什么串读，多一个又会造成什么召回碎片化？
**claim:** D
**trigger:** 候选人能列出 scope model。

### R050
**question:** scope 是查询 filter、数据库 key、应用层校验，还是三者都有？哪一层才是真正的安全边界？
**claim:** D
**trigger:** scope enforcement 需要下钻。

### R051
**question:** task summary 和 structured memory 冲突时谁优先？还是它们根本不应该竞争同一种事实权威？
**claim:** D
**trigger:** 候选人把多种 memory 混成一段 prompt。

### R052
**question:** Context Pack 有 token budget 时，summary、structured memory、current task materials 如何裁剪？固定配额还是按任务动态？
**claim:** D
**trigger:** context assembly 进入容量/排序讨论。

### R053
**question:** source-id trace 的粒度是什么：memory record、source turn、document span，还是仅一个 opaque id？它怎样帮助 debug 错误 memory？
**claim:** D
**trigger:** provenance / trace 是卖点。

### R054
**question:** `APPROVED` 是谁批准、何时变更、是否可撤销？如果 approval 本身变了，cached Context Pack 怎么处理？
**claim:** D
**trigger:** approval gate 需要生命周期解释。

### R055
**question:** 一条恶意用户文本被错误总结成 structured memory，会不会在未来 turn 变成持久 prompt injection？你会在哪个边界区分 instruction 和 data？
**claim:** D
**trigger:** 安全/长期 memory 风险深入。

### R056
**question:** `prepare_context()` 是纯函数还是会读写状态？如果它同时做读写，重试和并发会有什么问题？
**claim:** D
**trigger:** candidate能讲函数行为。

### R057
**question:** `ContextOrchestrator` 和 `GeneralAgent.prepare_context()` 的职责为什么不直接合并？这个抽象什么时候值得，什么时候只是多一层？
**claim:** D / E
**trigger:** candidate claims orchestrator abstraction has value.

### R058
**question:** post-turn summary 写入前 crash 与写入后 ACK 前 crash 分别会怎样？你有没有稳定 idempotency identity？
**claim:** D
**trigger:** post-turn persistence 深挖。

### R059
**question:** 两个并发 turn 更新同一个 scope memory，最后写入 wins 会有什么问题？你需要 optimistic locking、append-only event 还是别的？
**claim:** D
**trigger:** concurrency concern exposed.

### R060
**question:** 长期 memory 什么时候应该失效或被遗忘？Retention、Recall Eligibility 和物理删除是不是同一件事？
**claim:** D / E
**trigger:** candidate extends foundation to long-term product design.

### R061
**question:** 如果 Memory provider 明天换成成熟服务，你哪些 contract 必须保持稳定，哪些存储/检索实现可以直接扔掉？
**claim:** D / E
**trigger:** Build/Buy / provider replacement discussion.

### R062
**question:** `32 passed` 是 focused tests。为什么不能据此说 Memory 已经 production-ready？还缺哪些 E2E / failure / security / real-user evidence？
**claim:** D
**trigger:** candidate oversells test count.

### R063
**question:** 如果 ablation 发现长期 memory 对主要任务没有稳定收益，但提高了 token 和 stale-risk，你会保留只做 task summary，还是整层删除？
**claim:** D / E
**trigger:** measurement/delete condition needed.

## Claim E — Architecture / reuse / fundamentals

### R064
**question:** 你说机器候选和正式工作成果要分开。一个候选结果什么时候才有资格变成长期业务事实？谁应该拥有这个决定？
**claim:** E
**trigger:** architecture design becomes primary discussion.

### R065
**question:** 长任务权限在执行中途被撤销。Checkpoint 里保存过一次 allow，为什么不能继续用？新的受保护动作应该检查什么？
**claim:** E
**trigger:** continuous authorization claim needs pressure.

### R066
**question:** DB transaction 能不能和外部 HTTP POST 做成一个原子事务？如果不能，你如何表达“远端可能成功、本地不知道”的状态？
**claim:** E / B
**trigger:** external effect/recovery discussion.

### R067
**question:** Runtime checkpoint 写成功和业务正式提交成功分别能证明什么？进程在二者之间 crash 后，恢复应该先信谁？
**claim:** E
**trigger:** candidate uses checkpoint as reliability proof.

### R068
**question:** 为什么逻辑责任域不等于微服务？什么真实约束出现后你才会把某个模块拆成独立进程或网络服务？
**claim:** E
**trigger:** candidate presents architecture diagram as deployment topology.

### R069
**question:** 如果 Generic Agent Host 已经能做长任务恢复和 Tool tracing，Zuno Native Runtime 还剩什么不可替代的 Delta？没有 Delta 时你会怎么简化？
**claim:** E
**trigger:** Build/Buy / Native Runtime discussion.

### R070
**question:** 设计一个你最想补的对照实验：Generic Host + Legal Skills、Generic Host + 专业后端、Native Runtime 三者你会测什么，什么结果会改变架构决策？
**claim:** E
**trigger:** candidate claims measurement-gated architecture maturity.

# Red self-check

- Primary Path = 30，Reserve = 70；100 是压力集，不是逐题必问脚本。
- P001–P004 先建立项目真实性与 Ownership；P005 已在前 10 题进入最高风险 GraphRAG 实现 Claim。
- Claim C / B / D 都有早期 implementation ownership probe 和 `CLAIM_*_IMPLEMENTATION_NOT_ESTABLISHED` Kill Switch。
- Primary 重点分配给 GraphRAG、Tool/MCP、Context/Memory，没有按架构模块平均分题。
- Build/Buy、failure/recovery、metric/evidence、network/async/DB/RAG fundamentals 均从简历 Claim 自然下钻。
- Reserve 每题有 trigger，不作为第二份固定脚本；没有用同义改写凑数。
- 题目只依据冻结模拟简历、岗位、Attack Skill 与通用工程知识；未使用 Zuno canonical docs、源码、PR diff 或 Blue answer key 作为正式出题输入。
- 本文件状态为 `DRAFT_REVIEW`。下一阶段只能是 `USER_RED_REVIEW`；用户未 APPROVE 前 Blue 必须保持 BLOCKED。
