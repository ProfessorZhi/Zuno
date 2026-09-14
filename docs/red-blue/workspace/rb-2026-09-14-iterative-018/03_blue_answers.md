# Blue Batch Answers — rb-2026-09-14-iterative-018

execution_override: BATCH_WAVES
wave: BLUE_WAVE_1
answer_mode: simulated-candidate-batch
questions_answered: SPOKEN_SEEDS + Q001-Q100

> `source_support` / `boundary` 供后续 Reflection 使用，不属于候选人口头回答。

## Seed answers

### S001 — 挑一块自己做得最深的讲
**answer:** 我会先讲 GraphRAG 的一次检索回退。HotpotQA 的 5 条 retrieval smoke 里，baseline 能命中的文档被 graph 新增候选挤出 Top-K。我先把问题定位成 fusion/ranking，再做 baseline-preserving fusion，并连续补 candidate-aware seed、entity alias 和 path-aware ranking。同日小样本 rerun 恢复到 baseline 水平。我只把它称为 development smoke，不说正式 benchmark。
**source_support:** PF-031.

### S002 — 为什么把 MCP Tool 从子 Agent 拿出来
**answer:** 代码层能确认原来有 MCPAgent/SkillAgent-as-Tool 和 selector scaffolding，后来改成 concrete MCP Tools 直接绑定 `GeneralAgent`，用户级配置在实际 Tool Call 时按 tool→server 注入。它收掉了一层 Agent 包装和配置传递面；原始 Issue 没恢复，所以我不编造“某次线上事故”作为唯一原因。
**source_support:** PF-032; 77346758...

### S003 — direct route 和 ReAct 怎么分
**answer:** direct route 只适合目标 Tool 能确定、参数能可靠解析、配置条件满足的请求；目标模糊、参数依赖上下文或需要多步决策就回 ReAct。历史 test 能证明天气和 custom MCP name 等具体路径，但不是成熟通用路由引擎。
**source_support:** PF-032.

### S004 — 为什么加 graph 反而变差
**answer:** graph 不是完全没召回，而是新增候选改变最终排序。baseline 已经命中的 gold-like 文档还在候选链里，却在 fusion 后被挤出 Top-K，所以先修 ranking semantics，而不是简单提高 graph recall。
**source_support:** PF-031.

### S005 — baseline-preserving 到底 preserve 什么
**answer:** fusion 会保留 Vector/BM25/Graph source rank，`baseline_rank` 取 Vector/BM25 较优 rank；排序先看 candidate group，再看 baseline rank、graph tier/signal 和本地相关性。graph signal 当时由 support count、seed hit、file focus、path count 组成，promotion threshold 是 6。高证据 graph candidate 仍允许晋升，所以不是“baseline 永远优先”。
**source_support:** 5d9b719e...

### S006 — Memory 自己主要改哪段
**answer:** 我能落到个人代码的是 6 月 Context/Memory V2 foundation 和 PR #8 readback hardening：typed contracts、`MemoryScope`、最小 `prepare_context`/post-turn write、`ContextOrchestrator`，以及 same-scope summary、仅 APPROVED structured memory、source trace/review/provenance。4 月公开根提交已经有旧 Memory，所以我不会说从零做了整个 Memory。
**source_support:** PF-029, PF-030.

### S007 — 单 Agent 是刻意设计还是先这么做
**answer:** 历史单 Agent 更像简单 baseline 和一次 Tool/MCP 调用策略收口，不是永久产品原则。以后如果独立专业角色需要隔离 context/tool policy、长任务需要并行 Specialist 和独立 failure ownership，或者单 Agent tool/context surface 明显退化，我会比较 Tool、Subgraph、Specialist/Multi-Agent 和通用 Host。Persistent Multi-Agent 本来就应 measurement-gated。
**source_support:** PF-026, PF-032.

### S008 — 最想给面试官看哪段代码
**answer:** 检索方向我会打开 `RetrievalFusion` 和 regression tests，因为能直接看到“回退现象—排序语义—测试”；Tool 方向会看 4 月 `GeneralAgent` 的 MCP binding/config middleware，再看 Workspace route 的两个具体 bug。
**source_support:** PF-031, PF-032.

---

## Tool / MCP strategy

### Q001
旧链路关键形态是 `GeneralAgent -> MCPAgent-as-Tool -> concrete MCP Tool`，Skill 也有 `SkillAgent-as-Tool`，旁边还有 tool-selection scaffolding。4 月 15 日后 concrete MCP Tools 和 Skill guidance tools 直接进入同一个 `GeneralAgent` tool set。

### Q002
原始需求/Issue 没恢复，所以不能说第一个真实用户故障是什么。代码能确认额外 Agent 层增加了 tool schema、调用上下文和用户配置的传递/排查面；业务收益没有真实 trace/指标证明。

### Q003
`init_agent()` 先 setup MCP/普通/Skill tools，最终 `create_agent(... tools=...)` 使用这些 BaseTool，所以 Tool schema 在 Agent 构建时成为模型可用工具；用户 Server 配置不是初始化时写死，而是实际 Tool Call middleware 注入。

### Q004
配置是 user-specific。middleware 持有 `user_id`，调用 MCP Tool 时用 tool name 找 server id，再查 `get_mcp_user_config(user_id, server_id)` 并更新当次 args。这样至少不是把某个用户配置永久绑到共享 Tool schema。

### Q005
我不会声称并发隔离已经证明。代码能确认每次按 `user_id + server_id` 查配置，但 canonical evidence 没冻结 Agent instance 是否跨用户共享，也没有两用户并发 regression test。所以 per-user lookup 存在，真正隔离仍是 Evidence gap。

### Q006
这段代码按 Tool Call 时现查配置，更接近调用时当前配置，不是长任务开始时冻结 ConfigVersion。简单但会产生长任务内部配置漂移；若要求可复现，我会补 version pin/snapshot。

### Q007
没有恢复完整 Tool discovery freshness/TTL/invalidation contract。我只能确认 Provider 负责连接/发现/执行，Zuno 当时负责 Agent-side exposure/routing/config injection。Server schema 改变后的失效是未闭环点。

### Q008
全部 Tool 长期暴露给一个 Agent 会放大 schema/context、token/latency、选择精度和权限面的压力。历史没有 200-tool benchmark；如果真到这个规模，我先做 capability/toolset gating，必要时再比较 Specialist/Subgraph，而不是默认拆 Multi-Agent。

### Q009
现有实现主要靠 tool name 到 MCP server mapping。没有证据证明跨 Server 同名 Tool 的 namespace/collision policy；更稳的设计应该把 server identity 纳入 canonical tool id。

### Q010
Agent middleware 会把 Tool 成功/异常转为 ToolMessage/Command 并发事件；Workspace 有 direct structured result 的测试。但没有证据证明所有 MCP Tool 返回都统一成成熟业务 Schema，所以不能说已有完整 result canonicalization layer。

### Q011
timeout 不能区分远端没执行还是执行了但响应丢失。历史 Tool code 的异常处理不等于副作用 reconcile；有现实副作用时 retry 需要 idempotency/reconcile。这是当前 Target Effects 语义，不能倒推成 4 月已实现。

### Q012
MCP SDK/Provider 负责协议连接、discovery 和执行，Zuno 当时补 Agent 侧 Tool 暴露、user config injection 和 Workspace routing。今天通用 Host 越成熟，这些 generic plumbing 越应该下放，Zuno 只保留真正的业务 policy/authority delta。

## Workspace routing

### Q013
历史 direct route 可以概括成：能识别具体 MCP 目标、参数可确定解析、配置 gate 通过，才走短路；否则进入 ReAct。已恢复的是具体天气/custom MCP path，不是一份通用 route DSL。

### Q014
参数缺一半时确定性前提已失效。直接执行等于代码替用户猜参数；回 ReAct 至少允许利用上下文或决定澄清。当前材料没有证明所有缺参语义。

### Q015
最坏是把本应经过推理、上下文或安全检查的请求直接变成具体 Tool invocation，导致错 Tool/错参数甚至绕过 policy。因此 direct route 必须窄，并要证明与 safety/config gate 等价；现在只恢复部分测试。

### Q016
简单请求误进 ReAct 会多模型决策、token/latency 和不确定性，也可能产生额外 Tool step。历史没有前后成本指标，所以我不给百分比。

### Q017
父版本基本用 `cleaned.replace("天气", "")` 生成 city，复杂自然句会把多余文本带进去。新版本加 `_extract_gaode_weather_city()`，回归用例固定“请用高德地图查询南京今天天气，并简短回答。”最终 `maps_weather(city="南京")`。

### Q018
`_canonical_mcp_target()` 旧实现对 custom MCP server name 会继续递归自己；normalized query 已等于该 server name 时没有收敛条件。修复为直接返回 normalized server name，并加 no-recursion test。

### Q019
一条锁 custom MCP name 不递归；一条锁自然语言天气请求正确抽出南京。相同 test artifact 还覆盖 platform-ready MCP 无 user config、config gate 和 direct structured result。

### Q020
历史没有足够 trace 证据让我报具体日志字段。今天至少应记录 route decision、matched tool/server、parsed args 摘要、config gate、fallback reason 和 trace id，用来区分“路由错”和“执行错”。这是改进建议。

### Q021
direct route 有 bypass 风险。它必须复用授权、配置、审计/trace 等边界，不能因为少一次 LLM 就成为旁路。历史只证明部分 config gate，不足以宣布安全等价。

### Q022
“继续查刚才那个城市”没有显式 city。如果 route 层没有从可靠会话状态解析出参数，我会回 ReAct/context path；没有历史证据证明 direct route 支持这类指代。

### Q023
`GeneralAgent` 有 model/tool call state，并在模型不再发 Tool Call 时结束，但简历证据没有冻结完整 hard max/循环恢复策略。我不会编最大步数，这题需要继续看源码。

### Q024
历史 route rule 在 Workspace Agent 产品层维护。长期如果规则变多，我会收敛成 declarative capability/routing policy，或者交给 generic host；不希望每个 Tool 都散落 if/else。

### Q025
如果 A/B 发现 direct route 对 latency/cost/reliability 没稳定收益，或者 bypass/维护风险更大，我会删除 direct route，只留统一 ReAct/Host path。它不是产品身份。

---

## GraphRAG ranking regression / fusion

### Q026
最早的明确工程信号是 5 条 HotpotQA retrieval-only smoke：baseline Recall@5 是 5/5，local GraphRAG 是 4/5。失败样本能看到 graph-added 文档把 baseline 已命中的 gold-like 文档挤出最终 Top-K。

### Q027
是同一 development smoke 对 baseline 和 local GraphRAG 做 retrieval-level 对比，记录 Recall/MRR/chain 类指标和 route diagnostics。runner/config 没完整冻结成正式 benchmark，历史 model-profile 也有不一致记录，所以只算 regression smoke。

### Q028
因为失败样本里 baseline 已经把目标文档召回到候选集合，问题发生在加入 graph 候选并融合以后。如果是 recall failure，目标文档一开始就不在；这里更像 Top-K displacement。

### Q029
baseline 主要是 Vector 和 BM25/keyword 候选，增强路径再加 Graph candidates。融合时同 chunk 的多来源命中会合并，并记录 `matched_by` / source rank。

### Q030
merge 时为 Vector、BM25、Graph 分别写入 rank；`_baseline_rank()` 取 vector_rank 与 bm25_rank 的较小值。排序先看 candidate group，再看 baseline rank，然后才是 graph tier/signal 和本地相关性。

### Q031
那个版本的 `graph_signal` 是 `graph_support_count + graph_seed_hit_count + graph_file_focus + graph_path_count`。它是工程启发式，不是学习出来的 calibrated score。

### Q032
`GRAPH_PROMOTION_THRESHOLD=6`。Vector+Graph 且 signal≥6 会进更高 candidate group；graph-only 达到更强阈值也可以晋升，代码里 graph-only ≥9 可以进入 baseline-like group，≥6 进入下一层。阈值没做正式调参/消融。

### Q033
主要 key 是 candidate group、baseline rank、graph tier、graph signal、local/base score。完全相同 key 时依赖 Python stable sort / 输入顺序，没有看到 chunk id 作为最终 tie-break；如果要求跨运行完全稳定，这是可补的细节。

### Q034
没有直接把 Vector/BM25/Graph 原始 score 当可比数值相加。当前策略用 source rank 和 candidate group 做主排序，把 raw/local score 放后面，绕开一部分跨 retriever calibration 问题，但没有真正统一概率尺度。

### Q035
有人工参数。threshold=6、candidate group、graph tier 都是 heuristic。那轮没有 ablation，所以不能说这些参数最优，只能说它们修掉当时 regression，并有针对性 tests。

### Q036
已观测到的噪声表现是 graph-added candidates 进入 Top-K；后续几个修复分别针对 seed、alias、path relevance，所以噪声可能从多处进入。没有证据把所有 regression 归因给唯一一步。

### Q037
会，所以保留了“高置信 graph candidate 可以晋升”的测试，而不是把 baseline 做成不可突破的墙。真正决定 GraphRAG 是否默认开，需要 query-class benchmark 同时看 quality 和 latency/cost。

### Q038
有 `chunk_id` 时用 chunk_id merge，同一文档来自多个 source 会合并 `matched_by`、source score/rank。没有 chunk_id 时 fallback key 带 source name + counter，不代表跨 source 能可靠去重。

### Q039
主要靠 candidate group + source rank 把 raw score 降为次要因素，所以某一路单纯因为分数尺度大不容易直接吞掉其它路。但这是 rank-based heuristic，不是统一 calibration。

### Q040
Top-K 拉到 20 可能让“被挤出 Top-5”的表面问题弱一些，但不会消除错误 ordering，也会增加后续 context/重排成本。没有 Top-20 sensitivity 结果。

### Q041
Recall@5 看支持文档有没有进入前 5；MRR 更关注第一个相关结果位置。对这次问题，Recall 暴露“被挤出 Top-K”，MRR 看恢复后排序。ChainRecall/FullChainHit 更适合多跳 supporting-chain 覆盖。

### Q042
只能确认 runner 当时 `limit=5`，不能从现有证据证明为什么恰好 5 条。下一步本来就应该扩到 limit=10 / 多数据集。

### Q043
修前和修后用同一小批样本，但不是独立 holdout。既然开发围绕这些 bad cases 修，rerun 只能证明 regression case 被修，不能给无偏泛化结论。

### Q044
一个都不敢单独归因。fusion、seed、alias、path ranking 连续修改，缺 per-commit ablation；只能说初始 bundle 前有 regression、最终 bundle 后该样本恢复。

### Q045
rerun 记录 `fallback_count=1`，说明 5 条里有一次走 fallback，至少不是所有 query 都纯 graph 完成。canonical provenance 没冻结那条具体为什么 fallback。

### Q046
那次小样本记录里 GraphRAG p95 latency 大约 26.6s，baseline 大约 19.0s。样本只有 5 条，不能当稳定性能 benchmark，但足以说明增强不是免费的，质量和延迟必须一起 gate。

### Q047
单跳事实、Hybrid baseline 已稳定命中的 query，或者 latency budget 紧且 graph 没可归因收益时，我会关掉 GraphRAG。长期应 query-gated，而不是默认所有问题进图。

---

## Multi-hop graph retrieval

### Q048
seed 来源不只有 query 文本。candidate-aware 版本从 query、显式 alias/policy term 取 seed，再把 baseline top candidates 的 title/file name/entity mention 补进来，最多默认 8 个，并记录 seed source。

### Q049
seed 错了后面会围绕错误实体扩图，带来无关 path/chunk，再在 fusion 里制造噪声，严重时就是 Top-K displacement。图检索错误会沿扩展放大。

### Q050
关键新增是 `candidate_context`：把 baseline 前几名文档 title/file name 提供给 GraphRetriever；seed 还带 `query / alias / baseline_title / baseline_file / baseline_entity` source，并去 generic entity、去重。

### Q051
当前有 seed 数量上限、graph-worthy query 判断、hop/path 数量限制、generic entity filter，再用 path ranking 压噪。代码入口里能看到 hop limit 2、max_paths_per_entity 10 一类默认参数，但它们仍是 heuristic。

### Q052
alias normalization 会去 article、括号后缀、连字符和部分标点，所以高风险是本来靠 parenthetical 区分的实体被归成同一 normalized key。它是轻量字符串归一，不是真实体消歧。

### Q053
当前不能完整避免同名误合并。normalized map 缺 stable entity id/type/context disambiguation；真正法律场景应引入 entity identity、类型、来源与上下文约束。

### Q054
path score 有 seed coverage、relation cue、bridge query bonus、comparison query bonus、title match、support count 和 generic-entity penalty。随后 chunk 累积 `graph_path_score` / `graph_path_count`，document ranking 使用 path signal。

### Q055
这个版本没有对路径长度本身做通用显式 penalty；主要按 relation/query cue 和支持证据打分。如果扩大更深 hop，长路径偏置和组合爆炸要单独处理。

### Q056
当前有 `seen_paths`、`seen_chunk_ids` 去重，加 hop/path 数量限制，能抑制部分重复扩展。但这不等于一般图算法意义上的全局 cycle-proof。

### Q057
当前不是“path evidence 与文档相关性冲突时做事实裁决”，而是把 path signal 加进 doc score，再进 baseline-preserving fusion。它是 ranking heuristic，不是业务 Authority。

### Q058
那轮 eval 记录 ChainRecall@5 / FullChainHit@5 等 chain-level 指标，用来观察 supporting chain 在 Top-K 的覆盖。精确公式应打开 runner 定义后再讲，不凭记忆编。

### Q059
当前证据没有完整 graph update → alias/path cache invalidation/version 语义。Target 强调 IndexVersion/freshness，但不能反写成这段历史 GraphRAG 已实现。

### Q060
现有 GraphRetriever 有 `graph_worthy` 判断，会看 comparison/bridge/multi-entity 关系特征及 seed/policy signal。长期更应由 query-class eval 驱动 gating。

### Q061
因为 GraphRAG 带来额外 latency、噪声、图索引/实体消歧/失效维护成本，而普通 Hybrid RAG 对大量单跳问题已足够。它应该 measurement-gated。

---

## Context / Memory

### Q062
`MemoryScope` 是明确数据结构：`user_id`，以及可选 `agent_id / project_id / thread_id`；store 读取按整个 scope equality 匹配。

### Q063
字段就是 `user_id, agent_id, project_id, thread_id`。简历中可以说 scope 约束，但不应擅自把 contract 字段改成 workspace/task。

### Q064
最严重是跨用户/项目/线程把不该出现的记忆注入模型上下文，这同时是隐私、权限和事实污染问题，所以 scope 是安全/正确性边界。

### Q065
如果 project_id/thread_id 不同且 caller 正确填入 scope，exact-scope read 不会互相看到；但可选字段留空会扩大 scope。因此隔离强度取决于 caller 正确构造 scope，不能只看 store equality。

### Q066
pre-call 阶段先构造 `ContextPreparationInput`，把 system/recent messages、Memory、Knowledge Evidence、Capability items 组成 candidates；`ContextOrchestrator.prepare()` 应用 token budget，生成带 trace 的 `ModelContextPacket`，之后给模型。PR #8 把 same-scope summary 与 APPROVED structured memory 接回这条链。

### Q067
PF-030 能证明 post-turn scoped raw event / task summary write integration，但 provenance 没冻结历史持久化路径究竟同步还是异步。当前基础 `InMemoryLayerStore` 是同步内存操作，不能反写成当时所有部署行为。

### Q068
`ContextOrchestrator` 真正做 context selection/orchestration：把 system、recent、memory、knowledge、capability candidates 放在一个 packet，应用 token budget 并生成 selected/dropped trace。它不应拥有 Memory 审核、持久化或业务事实 Authority。

### Q069
当前有显式 token-budget policy：candidate 带 token_estimate/priority/reason，budget 选一部分，剩余进入 dropped_items，ContextTrace 保存选择结果。Recent user constraint/tool result 有高 priority。

### Q070
当前没有成熟“task summary 与 structured memory 内容冲突”的事实仲裁器。Context builder 可以选/丢 item，但 factual conflict 应由 freshness/version/policy/authority 解决，不能靠谁 priority 高就认谁真。

### Q071
基础 InMemory store 是 append/save，没有并发事务、唯一约束或 CAS；两个 turn 同时写可能重复 candidate/summary 或顺序不确定。成熟实现需要 durable store、dedupe/unique/versioning 和 transaction policy。

### Q072
一次请求的 context packet 是 pre-call 快照。之后同 scope 新 Memory 正常应影响下一次 prepare，不该悄悄改变当前 prompt；但当前没有跨请求生命周期的 MemoryVersion/freshness token。

### Q073
RetentionPolicy 有 `allow_privacy_delete`，但“删除后所有 cache/context snapshot 如何立即失效”没有被历史实现证明。已组装进当前请求的 packet 是否撤销属于 TOCTOU/freshness 问题。

### Q074
structured memory 往往来自模型/规则抽取，只是 Candidate，可能抽错、过期或把一次对话推成长期事实。默认 `MemoryCandidate` 是 PENDING 且 `requires_review=True`；仅 APPROVED readback 用来阻断污染循环。

### Q075
contract 有 `MemoryReviewDecision.approve(candidate, reviewer_id, reason)`，审核决策带 reviewer_id 和原因。但 PF-029 证明的是 review/provenance contract + read-time gate，不是完整人审 UI、角色权限和运营生命周期。

### Q076
当前没有足够证据证明“取出后撤销还能在同一模型调用前再次 fail-closed”。packet 一旦组装就是请求快照；严格解决需要 version/epoch 或临近模型调用的 freshness check。现在只能说 read-time gate 存在。

### Q077
Task summary 和 MemoryCandidate 都要求 `source_event_ids`；ReviewDecision 也带 source_event_ids，Context item/trace 再保存进入模型的 source ids。这样可以从 context item 回到候选/summary和原始事件，但更深物理 provenance 没完全证明。

### Q078
source trace 用于可解释、debug、审计和删除/更正时追来源；它本身不自动成为业务事实 Authority。不过 policy 可以依据 provenance/freshness/review status 决定 item 是否可进入上下文。

### Q079
默认 candidate 是 PENDING + requires_review，readback 只取 APPROVED，但代码层仍能构造 `review_status=APPROVED` candidate。是否有人能绕过 review 取决于调用权限/写路径，目前没有足够 Security evidence 宣布不存在 bypass。

### Q080
目前不能证明“加 Memory 一定更好”。PF-029/030 证明 contract、integration 和 focused tests，不是长期任务质量 A/B。Memory 应有 baseline + kill test，没收益就关。

---

## Agent architecture / evolution

### Q081
历史上选择单 Agent，从代码演进看是为了收敛 Tool/MCP 调用：拿掉 Agent-as-Tool 层，让一个 GeneralAgent 直接管理具体 Tool。没有恢复原始 ADR，所以不能说做过完整 single-vs-multi benchmark；它更像简单可控 baseline。

### Q082
我会看四类信号：独立专业角色需要不同 context/tool/policy；单 Agent 的 tool/context surface 导致可测选择退化；长任务需要并行 Specialist 且各自有清晰 failure/retry 边界；不同角色需要独立权限或质量资格。Tool/Subgraph 能解决就不先上 Multi-Agent。

### Q083
最难共享的不是聊天文本，而是谁有权修改的 durable state：计划版本、任务进度、Memory/证据版本、正式业务事实。我的倾向是这些状态保持单一 authority，Agent 交换带版本/来源的结果，而不是共同改一个大 mutable state。

### Q084
Supervisor 当然可能成为逻辑单点。中间方案是 Single logical controller + parallel workers，把 authority 收敛但执行并行；只有控制吞吐成为真实瓶颈再考虑按 case/partition 拆 controller。

### Q085
输入输出契约稳定、没有长期规划/上下文生命周期、调用一次结束的优先做 Tool/Capability；需要多步自主推理、独立 toolset/policy、长期 context 或完整子任务自治时才像 Specialist Agent。中间态先用 Subgraph。

### Q086
Subgraph 是父 Runtime 内受控工作流单元，共享父执行上下文和 authority；独立 Agent 有更明显的 context/tool/policy/lifecycle 边界和 handoff contract。没有独立性需求就不另起 Agent。

### Q087
不让多个 Agent 直接读写一份无 scope 的 mutable memory。working context 应 agent/task scoped；长期 memory 通过统一 Memory owner 按 scope、review/provenance/freshness 读取。正式法律事实更不应放在共享 Agent Memory 当真值。

### Q088
如果未来拆 Multi-Agent，我会让 Runtime/controller 给每个派发步骤稳定 StepRun/dispatch identity，任务重试按 idempotency 去重；子任务有现实副作用时 Effect owner 再单独处理 idempotency/reconcile。不能让 Specialist 自己决定全局重复执行。这是目标设计，不是历史已实现事实。

### Q089
通用 Host 可以拥有 conversation、workflow、MCP、tool calling、checkpoint、generic memory/RAG/tracing。Zuno 真正值得保留的是法律材料/证据版本、专业 capability 语义与资格、正式业务事实准入、失效传播、必要的 effect/security authority 和法律 Evaluation。

### Q090
我会先删“测不出增益但一直默认开启”的复杂度，而不是删 domain authority。GraphRAG 默认路径、Persistent Multi-Agent、Reflection、Native Runtime 都可以被删或外置；谁先删取决于 A/B 的质量、延迟、成本和恢复收益。

---

## Ownership / evidence / fundamentals

### Q091
我不敢用“代码量最多”做没统计的结论。证据最完整的一条是 6 月 20 日 GraphRAG 质量链，因为有连续多个本人账号实现 commit、针对性 tests 和前后 smoke；Tool Calling 与 Memory V2 也各有具体 before/after。

### Q092
我加入时项目已经有代码、简单前端、Agent 和旧 Memory 子系统，不是我从零搭。能落到我的具体增量包括 4 月 Tool/MCP strategy + route hardening、6 月 GraphRAG 质量修复链、6 月 Context/Memory V2 foundation/readback hardening。今天九模块 Target 架构是后续系统化整理。

### Q093
我用 Pilot Validation 是因为历史确认项目进入过法院侧测试和 Pilot 阶段，但没有完整恢复用户数、题集、环境和验收协议。我不会因为有 Pilot 就说正式 Production。

### Q094
我不会说正式生产上线、稳定 SLA、全部 22 家法院部署、生产 QPS/latency、GraphRAG 正式 benchmark、Memory production-grade，也不会把后续 Tool Control Plane/Effects Target 反写成 4 月历史实现。

### Q095
GraphRAG 有 retrieval-only `real_runtime` smoke，已经跨纯 unit function；Memory PR #8 描述里有多 profile contract eval，Tool route 有 focused regression artifact。但没有恢复法院环境端到端 CI / production trace。

### Q096
asyncio 并发里多个 coroutine 会在 await 点交错。如果请求级 user/config/state 放在 module global、singleton 可变字段或共享 Agent 实例字段里，另一个请求可能在 await 期间改掉它。应显式参数贯穿或正确使用 request-local context，Tool 实例也不能保存跨请求 mutable state。

### Q097
`ContextVar` 的 context 会在创建新的 asyncio Task 时复制当前上下文，所以子 Task 通常继承创建瞬间值；父 Task 后续修改不会自动改变已创建子 Task。跨线程/executor 不能假设相同传播，需要显式 `copy_context()` 或参数传递。

### Q098
Memory 并发写在弱隔离下可能出现两个事务都认为 dedupe key 不存在、重复插入，读改写还可能 lost update。仅提高 isolation 也不够，通常要 unique constraint、idempotency key/version/CAS。历史 V2 没证明这些 durable DB 语义已完成。

### Q099
timeout 只说明调用方在期限内没收到响应，不说明服务端没收到或没提交。远端可能已经执行，只是响应丢了；retry 会有重复副作用风险，所以需要 idempotency key、查询/reconcile 或 effect receipt。

### Q100
今天重做我最想推翻的是“把自研 orchestration topology 当默认前提”，而不是某个具体类。我会从 Generic Agent Host + Zuno Legal Backend 的更小 baseline 开始：Tool/MCP、workflow、checkpoint 能买就买；GraphRAG、Native Runtime、Persistent Multi-Agent 只有在对应 query/task class 上证明质量、恢复或成本收益后才打开。Multi-Agent 完全可能成为正确答案，但必须由 context/tool isolation、并行 Specialist、权限或 recovery 这些真实约束推出来。

## Blue Wave 1 self-boundary

- Tool/MCP：个人实现 before/after 很强；并发隔离、Tool discovery freshness、完整安全等价和真实业务指标仍是缺口。
- GraphRAG：代码级实现和 regression smoke 很强；正式 benchmark、ablation、entity disambiguation、cache/version invalidation 与稳定性能结论仍不足。
- Context/Memory：contract、scope、ContextOrchestrator、APPROVED read gate 与 provenance 很具体；durable concurrency、review authority、revocation freshness、长期质量收益未闭环。
- Agent topology：当前没有理由把 Single Agent 或 Multi-Agent 当不可变真理。更合理的目标是保留 Authority 边界，把 topology 当 measurement-gated execution choice。
- Evidence：Pilot != Production；5-query smoke != benchmark；Target != 历史实现；团队系统 != 个人从零实现。
