# Blue Wave 1 Answers — rb-2026-09-15-formal-019

status: `COMPLETE`
answer_count: `100`
visibility: `RED_VISIBLE`

以下回答按候选人口语组织。历史事实、当前系统、开放设计和基础知识分开回答；没有证据的地方不拿今天的 Target 架构反写历史。

## A. 项目真实性、Ownership 与必要性

### R1-Q001
我做得最深、证据也最完整的一块是 GraphRAG 检索质量优化。那次不是“把 GraphRAG 接进去”，而是先发现加图检索后 Top-K 反而退化，再定位到融合排序，把 baseline 已命中的结果保护下来，然后继续做 seed expansion、alias normalization 和 path-aware ranking。Tool/MCP 和后面的 Context/Memory V2 也有明确个人提交，但如果只能选一条最能代表工程深度的，我会选 GraphRAG 这条。

### R1-Q002
我加入时项目已经有代码、简单自研前端、Agent 和 Memory 基础，我不是从零搭项目。公开历史里我第一笔能够明确证明的关键改动是 4 月 15 日的单 Agent Tool Calling 重构：把 nested MCPAgent-as-Tool 路径收掉，让具体 MCP Tool 直接绑定 GeneralAgent，并把用户 MCP 配置放到实际 Tool 调用时注入。

### R1-Q003
目前可恢复的核心研发规模大约是 7–8 人，但完整组织图和每个模块正式 Owner 我不敢编。我的个人边界主要是部分 Agent、Tool/MCP、GraphRAG，以及后续一段 Context/Memory V2；我没有负责整个前后端、数据库总设计或完整 Runtime。

### R1-Q004
如果只看我能明确认领的提交，至少还能剩三条主线：4 月的 Tool/MCP binding 与 Workspace route hardening；6 月的 GraphRAG retrieval quality chain；6 月底的 scoped Context/Memory V2 foundation 和 readback hardening。完整产品、所有 Agent、现有 Tool Control Plane、整个 Memory 系统都不应该算成我个人完成。

### R1-Q005
我把 Pilot 理解成“在受控场景里验证方案和业务流程是否可用”，它不等于正式 Production。我们能确认项目经历过法院侧测试和 Pilot Validation，但没有恢复出生产 Endpoint、SLA、正式验收、长期监控或用户规模，所以简历不会写“已生产上线”。

### R1-Q006
这里我会保守回答：我能确认项目进入过法院侧测试，但现有材料不能证明我本人具体是现场部署、日志分析还是只接收团队反馈，所以我不会把团队经历说成我亲自驻场完成。这个边界如果面试官继续追，我宁可明确说 Unknown。

### R1-Q007
历史上能确认的是法律智能平台场景和回答质量需要继续提升，不能把后来 Target 架构里的所有复杂约束都倒推成当时客户原话。工程上我认为 Agent 真正有价值的地方，是任务需要根据中间结果继续决定下一步、组合检索和 Tool、处理参数不完整或多步骤任务；简单法律问答本身并不需要 Agent，受控 RAG 就可以。

### R1-Q008
固定 Workflow + RAG 能覆盖大量已知、边界稳定的流程，我不会为了 Agent 而否定它。更适合 Agent 的是步骤数量和路径不固定、需要根据检索或 Tool 返回动态决定下一步的任务；如果任务可以被稳定写成一个流程图，我反而更倾向先用 Workflow。

### R1-Q009
最先损失的是开放式任务里的动态编排能力，例如根据第一次检索结果决定是否继续检索、换 Tool、补参数或调用另一个能力。RAG、固定工具入口和业务后端本身不会因为拿掉 Agent 就失效，所以这也是为什么我不会说“整个 Zuno 必须依赖 Agent 才成立”。

### R1-Q010
如果只能给两个 commit，我会先给 4 月 15 日单 Agent Tool/MCP 重构的提交，再给 6 月 20 日 baseline-preserving GraphRAG fusion 的提交。这两条都能直接看到 before/after 调用链或排序逻辑；如果允许第三个，我会补 6 月底 Context/Memory PR，把 scope、review 和 prepare_context readback 这条线补上。

### R1-Q011
我最担心的是“direct route 值不值得长期保留”这一条，因为有代码和 regression test artifact，但没有恢复出延迟、成本或可靠性 benchmark。GraphRAG 也有明显证据边界：5-query smoke 只能证明一次 regression 被修掉，不能证明普遍收益。

### R1-Q012
重构前 GeneralAgent 里还有独立的 Tool 选择脚手架，MCP 能力通过 MCPAgent-as-Tool 这类 wrapper 再转发到具体 Provider；Skill 也有类似 wrapper。重构后具体 MCP Tool 直接进入 GeneralAgent 的 Tool 集合，实际调用时 middleware 根据 tool→server 映射加载该用户的 MCP 配置，然后由底层 MCP Provider 执行。

## B. Tool / MCP

### R1-Q013
我能证明的是结构性问题，而不是已经恢复出的客户事故。nested Agent-as-Tool 让 Tool 选择和用户配置跨了额外一层，调试时很难判断参数是在主 Agent、wrapper 还是 Provider 丢掉；所以我当时主要解决的是调用链和配置注入边界，不会把它包装成“线上故障修复”。

### R1-Q014
只修配置传递也能工作，但会继续保留两层 Tool 选择和两套上下文。我的判断是既然最终执行的还是同一个 MCP Tool，而且 per-user config 应该在实际调用点注入，就把具体 Tool 直接暴露给 GeneralAgent，减少一层 selector/wrapper；这个选择的收益当时没有正式 benchmark，所以它是结构简化，不是性能结论。

### R1-Q015
主要绕过的是独立 `tool_invocation_model` / `available_tools` 选择脚手架，以及 MCPAgent/SkillAgent-as-Tool 这种 nested Tool wrapper。没有删除 MCP Provider 的协议、discovery 和执行能力；只是把“Agent 怎么看到这些能力”和“调用时怎么注入用户配置”收回主 Agent 路径。

### R1-Q016
会，这是直接绑定具体 Tool 的真实代价：Tool 多以后 schema 会占 context，选择错误和 token 成本也可能上升。4 月那版没有正式规模测试，所以如果 Tool 数量继续增长，我会先做 capability/tool gating 或更窄的候选集，而不是因为已经重构过就坚持把所有 Tool 永久塞给模型。

### R1-Q017
当时 GeneralAgent 里有一个 `mcp_tool_server_map: Dict[str, str]`。初始化发现 MCP Tool 时建立 tool name 到 server id 的映射；Tool middleware 收到实际 tool call 后，用 tool name 找 server id，再去取当前用户的对应 Server 配置。

### R1-Q018
是调用时读取，不是在 Agent 初始化时把配置冻结。middleware 持有 `user_id`，实际调用 MCP Tool 时执行 `get_mcp_user_config(user_id, server_id)` 再把配置合入 args；这样用户配置更新后不需要重新构建整套 Agent，但代价是长任务内配置可能漂移。

### R1-Q019
我不能证明“一个共享 Agent 实例同时服务多个 user”这件事在当时已经被严格验证。那版 middleware 把 `user_id` 绑定在 Agent 实例上，所以安全前提更接近“一个实例对应一个用户上下文”；如果要共享实例，我会要求 request-local identity，而不是靠实例字段，并补并发隔离测试。

### R1-Q020
历史实现是 call-time 读取，所以理论上同一长任务的前后两次调用可能看到不同配置；当时没有 `ConfigVersion` 或 frozen snapshot。今天如果这个配置会影响安全或结果一致性，我会在 Run/Step 上固定版本，变化后显式 replan 或使旧调用失效，而不是默默漂移。

### R1-Q021
依赖用户配置的 Server，我倾向 fail closed：拿不到必要配置就返回明确 Tool error，不应该偷偷使用别人的或全局默认 credential。平台级、无需用户配置的 MCP 是另一类，可以通过 config gate 直接执行；这两类要显式区分。

### R1-Q022
4 月的历史实现没有形成我能证明的 Tool schema version / invalidation 机制。Tool discovery 更接近初始化阶段快照，Server 升级后要靠刷新或重建；如果今天做企业级长任务，我会给 ToolVersion/CapabilitySnapshot 明确版本，旧 schema 不能无限期继续执行。

### R1-Q023
这正是历史实现的薄弱点之一。映射主要按 Tool name 组织，我没有证据证明同名 Tool 跨 Server 的 collision semantics 已经彻底解决；更稳妥的做法是使用带 server/provider namespace 的 canonical tool id，让路由、日志和配置都按稳定 ID 走。

### R1-Q024
授权应该在真正产生执行权的边界做，而不是让 LLM 自己决定。Agent 可以选择 Tool，但执行前必须由 Security/Tool execution boundary 根据当前用户、资源、Tool 操作和任务范围重新判断；4 月那次历史改动主要是 binding/config，不应该拿后来的 Approval/Idempotency 体系反写成当时已有。

### R1-Q025
判断不了。客户端只看到“没有在预期时间拿到成功响应”，远端可能没收到、收到后失败，也可能已经执行成功但响应丢了；这种情况应该进入 outcome unknown，而不是直接假设失败。

### R1-Q026
最大的风险是重复现实副作用，比如重复发邮件、重复写案件状态、重复扣费。只要远端第一次实际上已经成功，盲 retry 就可能产生第二次 Effect，所以副作用 Tool 必须有幂等或 reconcile 语义。

### R1-Q027
如果今天设计，我会让 durable Tool/Effect Gateway 拥有幂等键，因为它最接近“一个业务动作是否已经发生”的持久事实；Agent 只提出动作，不应该自己拥有 Effect truth。Provider 支持幂等 key 时继续透传，否则 Gateway 至少要保存 attempt/receipt 并做 reconcile；这不是 4 月历史实现已有的能力。

### R1-Q028
不能。HTTP timeout 只说明客户端没有在 timeout 窗口里拿到完整响应；TCP 连接、代理、应用处理和响应传输任何一层都可能超时，服务端业务事务甚至可能已经提交，所以网络 timeout 和业务未执行是两件事。

### R1-Q029
普通全局变量对并发请求最危险，所有 coroutine 都能看到；thread-local 只按 OS 线程隔离，而 asyncio 的很多 coroutine 会跑在同一线程里，所以也不够；`ContextVar` 能随 async task context 传播，更适合 request-local identity，但仍需要在 task 创建、后台任务和跨线程边界上验证传播语义。

### R1-Q030
我会把它当不可信 Observation。Tool 输出可以成为模型输入材料，但没有资格改变 system instruction、安全策略或 Tool 权限；如果把 Tool 返回里的文本直接提升成指令，就会形成典型的 indirect prompt injection。

### R1-Q031
MCP Host/Provider 已经能做协议、discovery、schema 和实际执行，这些我倾向 Buy/Reuse。Zuno 当时真正增加的是：这些 Tool 怎样进入主 Agent、Tool 到 Server 的映射、用户级配置怎样在调用时注入，以及 Workspace 里何时 direct/何时回 ReAct；更高层的安全和业务 Authority 属于 Zuno，但不是 MCP 协议本身。

### R1-Q032
如果成熟 Host 已经稳定覆盖 binding、per-user config 和 schema lifecycle，我会删掉对应的自研 wrapper 和 discovery 适配，只保留 Zuno 业务必须拥有的 policy：授权、资源范围、审计、幂等、Effect truth，以及法律业务状态的提交边界。自研代码存在本身不是保留理由。

## C. Workspace direct route

### R1-Q033
我不会把“一步”定义成自然语言看起来短，而是定义成：目标 Tool 可唯一识别、所需参数可以确定、无需依赖前序 Tool 结果、对应配置 gate 满足。只要其中任一条件不成立，就回 ReAct/正常 Agent 路径。

### R1-Q034
历史 direct route 其实是很窄的 deterministic matcher，不是通用语义路由器。只有显式、可唯一归到某个 Tool 的请求才直接命中；有多个候选、指代不清或需要补上下文就不应该 direct。

### R1-Q035
当时像天气城市这类参数使用的是规则/轻量自然语言抽取，不是让另一个 LLM 再抽一遍。参数不完整时 direct route 应该退出，让 ReAct 决定是继续推理还是向用户追问；direct route 的目标就是处理“足够确定”的窄请求。

### R1-Q036
这种“刚才那个城市”依赖对话上下文，不应该靠单句 matcher 猜。如果当前 route 没有一个可靠的 context resolution 结果，就回 ReAct；否则 direct route 很容易把缺参数误判成完整参数。

### R1-Q037
不会因为 direct route 就降低风险控制。高风险 Tool 可以跳过“怎么选 Tool”的 ReAct 推理，但不能跳过 execute gate、授权、审批或 Effect 记录；4 月那版 direct route 主要是普通 MCP utility 场景，不能拿它证明高风险 Tool 已经安全直通。

### R1-Q038
理想上必须最终汇合到同一执行边界，否则 direct route 会成为绕过权限、配置或审计的旁路。历史实现能看到 config gate 和 Tool execution 复用，但完整授权/副作用治理当时并不成熟，所以如果两条路分别实现安全逻辑，这是需要修的设计风险。

### R1-Q039
我目前没有恢复出 latency、token、cost 或 success-rate 对照，所以不能说 direct route 已经证明“更值得维护”。它当时有代码级的确定性和 bug fix 价值，但长期是否保留应该靠同任务的 direct-vs-model baseline 测量。

### R1-Q040
父版本 `_canonical_mcp_target()` 在处理自定义 MCP server name 时，会对 normalized name 再调用自己；如果 normalized query 本来就等于 server name，就没有收敛条件，会无限递归。修复后对这种 custom server name 直接返回 normalized name，并补了回归用例。

### R1-Q041
父版本的天气 direct route 本质上只是 `replace("天气", "")`，所以面对“请用高德地图查询南京今天天气，并简短回答”会得到一整段脏参数，而不是城市名。后来增加专门的 city extractor，把这类自然句稳定抽成 `city="南京"`。

### R1-Q042
会删。如果在稳定任务集上 direct route 对 latency/cost/reliability 都没有显著收益，或者安全/维护成本高于收益，我会回到统一 Tool Calling；它属于优化层，不应该变成产品前提。

## D. GraphRAG

### R1-Q043
我不认为法律检索“一定需要” GraphRAG。简单单跳问答、材料内明确事实，Hybrid RAG 加 reranker 往往更便宜；GraphRAG 只在跨文档、多实体关系、多跳证据链这类 query 上有潜在价值，而且还需要正式评测证明。

### R1-Q044
一个典型多跳查询是先从作品找到导演，再从导演找到所在地，例如 HotpotQA 里“《Big Stone Gap》的导演位于纽约哪个城市”。第一跳和最终答案不一定在同一文档或共享强 lexical signal，这类关系链理论上更适合图扩展。

### R1-Q045
先看 5 条 retrieval smoke 的总指标，发现 local GraphRAG 的 Recall@5 从 baseline 的 1.0 掉到 0.8；然后逐条检查 Top-K，定位到两个 case 是 graph-added 文档把 baseline 已命中的 gold-like 文档挤出了前 5。也就是说先有指标异常，再回到单条 candidate/rank 找根因。

### R1-Q046
在那次 regression 里 baseline 已命中的文档还在候选里，问题发生在最终融合排序，不是早期完全没召回。这个区别很重要，因为如果候选根本不存在要修 recall；如果还在却掉出 Top-K，就应该先修 fusion/ranking。

### R1-Q047
核心语义是：已有 baseline 证据不能被弱 graph noise 轻易驱逐；Graph 可以提供增益，但必须带足够强的图证据才能晋升。这样 baseline 是安全底座，图信号是有条件的 promotion，而不是所有来源分数直接混成一个不可解释权重。

### R1-Q048
不是只记日志。每个候选保存 `vector_rank` 和 `bm25/keyword_rank`，`baseline_rank` 取两者最小值；最终 sort key 里 candidate group 后紧接 baseline rank，所以原始 baseline 顺序直接参与最终排序。

### R1-Q049
那版 graph signal 是 `support_count + seed_hit_count + file_focus + path_count`。它们分别代表图候选有多少支持、命中多少 seed、是否聚焦到相关文件，以及是否有多条路径支撑；这是可解释 heuristic，不是训练得到的最优打分。

### R1-Q050
promotion threshold 是 6；graph-only candidate 如果信号达到 9，可以进入和 baseline 更接近的 group。这个阈值是当时针对 dev smoke 的 heuristic，不是通过正式 ablation 或统计优化得到的，所以我不会把 6 说成普适最优参数。

### R1-Q051
简单调低 graph weight 有两个问题：不同来源的 score scale 未必可比，而且一个固定权重同时处理“弱 graph noise”和“很强的 graph-only 证据”。分组策略想表达的是非对称规则：弱图不挤 baseline，强图仍有晋升通道；当然这仍然要靠更大 eval 证明优于简单权重方案。

### R1-Q052
最终 key 是 `(candidate_group, baseline_rank, -graph_tier, -graph_signal, -(local_score + base_score))`。所以先看分组，再看 baseline rank，再用 graph tier、graph signal 和本地/基础相关度做后续 tie-break。

### R1-Q053
主要按 `chunk_id` 去重，同一个 chunk 从多路命中时合并 `matched_by`、各 source rank 和 source score；主 score 会保留较高值，同时把来源信息留在 metadata 里。如果没有 chunk_id 会退化到 source+counter fallback，这个 fallback 的语义明显弱一些。

### R1-Q054
可以。graph-only candidate 信号达到 9 会进入较高 group，达到 6 也能进入次一级，所以设计没有把 baseline 没见过的图候选永久压死；只是它要承担更高的证据门槛。

### R1-Q055
这轮历史证据不足以让我把某个 hop 数说成业务推导的固定真理。我会把 hop limit 当作需要通过 query class、质量和延迟共同调的实现参数；如果没有正式实验，就不能把经验值写成法律业务规律。

### R1-Q056
会，这是 candidate-aware seed 最大的风险。baseline 候选如果本来就错，拿它继续做 seed 可能放大错误图扩展，所以 seed 来源要记录，图候选还要经过支持度和 path evidence 的二次约束，正式评测也必须专门统计“错误 seed 放大”这类 bad case。

### R1-Q057
当时的 alias normalization 只是轻量字符串归一化，不能真正保证同名异人不被合并，所以这块我不会吹成 entity resolution。身份敏感场景应该使用稳定 entity id、来源和上下文 disambiguation；做不到时宁可保留多个候选，也不要强合并。

### R1-Q058
我最看重三个维度：seed coverage，路径里有没有真正的 relation/bridge 线索，以及这个路径是否有足够 support 而不是 generic 节点噪声。实现里还会参考 comparison/title 等 cues 和 generic penalty，但本质是奖励“连接问题两端且有支持”的路径。

### R1-Q059
主要额外成本来自图 seed 扩展、邻接/路径遍历、graph candidate 构造和后续融合。那 5 条 smoke 里 GraphRAG p95 大约 26.6 秒，baseline 大约 19 秒，但样本太小，只能说明方向上更慢，不能据此给正式性能结论；最终值不值要看特定 query 的质量增益能不能覆盖成本。

### R1-Q060
我能确认的是 HotpotQA development smoke，`limit=5`；不能证明这是随机、分层或独立 holdout，所以当然有 selection bias 风险。它适合做一次 regression smoke，不适合证明模型/检索方案的总体优势。

### R1-Q061
简历里的“恢复到 baseline 水平”主要指同一 5-query smoke 的 Recall@5 从 local 0.80 回到 1.00，而 baseline 是 1.00。最终 rerun 里 MRR@10 和 FullChainHit@5 也都是 1.00，但我不会把这些漂亮数字放成简历 headline，因为样本太小。

### R1-Q062
在这次 committed smoke 里，baseline 和 local GraphRAG 是同一 runner、同一批 5 条 query、同一 Top-K 口径下比较，所以能做 regression 前后对照。但它没有达到“冻结大数据集、独立环境、多次重复”的正式 benchmark 级别。

### R1-Q063
没有独立 holdout，所以不能排除针对当前 5 条样本的过拟合。我能说的是“这批 regression 不再低于 baseline”，不能说“GraphRAG 已泛化”；下一步必须把规则冻结后在独立切片重跑。

### R1-Q064
现在不能知道，因为四个改动是连续加入的，没有完整 ablation。根因上 baseline-preserving fusion 最直接针对 ranking displacement，但 seed、alias、path ranking 各自对最终指标的独立贡献没有被正式拆出来，所以这是明确的 Evidence Gap。

### R1-Q065
我会至少做 baseline Hybrid、baseline+fusion、+candidate-aware seed、+alias、+path ranking 的逐层对照，再做 leave-one-out ablation。第一优先验证 fusion，因为它对应已观察到的 ranking displacement；同时记录 latency/cost，避免“质量没涨但复杂度涨了”。

### R1-Q066
单跳、实体明确、baseline 已经高置信命中的 query，我会优先禁止 GraphRAG 默认介入；另外对图索引不新鲜、实体歧义高或关系覆盖不足的 query 也应该回 baseline。GraphRAG 更适合 query-class gated，而不是 always-on。

### R1-Q067
不会为了已有代码保留。如果大 benchmark 证明只有成本没有质量增益，我会删除或默认关闭 GraphRAG；如果只在一小类 multi-hop query 有收益，就做 query gating，而不是让所有请求承担图检索成本。

### R1-Q068
我会冻结 corpus、index、模型、prompt 和预算，按单跳/多跳/实体歧义/跨文档等 query class 分层，比较 Hybrid baseline、reranker baseline、GraphRAG gated 和 always-on；指标同时看 Recall/MRR、最终回答正确性和 citation、延迟/token/cost，再做 ablation 和独立 holdout。最后预注册 kill gate：如果某类 query 的质量收益不能稳定覆盖成本，就关掉该路径。

## E. Context / Memory

### R1-Q069
长期 Memory 只在跨会话仍然需要复用的信息上有意义，例如一个项目长期约束、已经确认的偏好或持续任务状态；conversation history 和 session summary 一旦跨 Session 就不稳定可用。反过来，如果业务只做一次性问答，我不会为了“Agent 完整”去加长期 Memory。

### R1-Q070
V2 的 `MemoryScope` 至少有 `user_id`，以及可选 `agent_id`、`project_id`、`thread_id`。这几维覆盖了当时要解决的用户、Agent、项目和线程隔离，但我不会说它天然足够所有企业场景，tenant/workspace/resource ACL 仍需要上层安全边界。

### R1-Q071
例如同一个用户同时做项目 A 和 B，如果项目 A 里“只允许使用 2025 版材料”的任务约束被当成 user-global memory，项目 B 下次就可能错误继承。这个问题不是相似度能解决的，本质是 scope authority 错了。

### R1-Q072
V2 里 scope 是按对象做等值匹配，`None` 更像一个显式的更宽层级，而不是 SQL wildcard；但调用方如果随手把 project/thread 丢掉，仍然会把信息提升到更宽 scope。所以敏感 structured memory 不应该静默降维，应该由 policy 决定是否允许写入 user-global scope。

### R1-Q073
最小 `ContextOrchestrator` 会合并 system/recent messages、Memory、Knowledge、Capability 等候选，在 token budget 下形成 `ModelContextPacket`，同时输出 trace/source ids。它的价值是把“模型这次到底看到了什么”变成一个可检查入口，而不是每个 Agent 自己拼 prompt。

### R1-Q074
预算由 ContextOrchestrator/policy 层控制。历史 V2 已有 token budget 和 trace contract，但成熟的 priority/compression policy 还没有被证明；原则上当前用户指令、安全约束、关键引用不能随意压缩，长历史、重复 Memory 和低优先级知识可以摘要或裁剪。

### R1-Q075
历史 V2 能证明的是同 scope 过滤，不能证明“调用方传入的 project_id 一定经过完整权限绑定”。真正安全的做法是由已认证的 Request/Workspace owner 构造允许的 MemoryScope，而不是让模型或任意调用方自己填一个 id；这块属于 Security integration，不应该用 scope equality 假装已经解决。

### R1-Q076
当时 `post_turn_commit()` 是回合结束后写 scoped raw event 和 task summary；structured long-term memory 更接近 candidate + review，不是每句话直接变 APPROVED。今天如果抽取要调用模型，我会先耐久保存原始事件，再异步生成 candidate，避免把模型调用放在用户请求事务里。

### R1-Q077
task summary 是当前任务/会话的压缩运行状态，生命周期短、更新频繁；structured memory 是跨会话还值得复用的事实/经验，错误代价更高，所以需要 review/provenance。只保留 structured memory 会丢当前任务细节，只保留 summary 又无法安全复用长期信息。

### R1-Q078
Contract 里有 `MemoryReviewDecision.approve(candidate, reviewer_id, reason)`，candidate 默认需要 review，并保留来源。能不能成为 reviewer 本身应该由权限系统决定；V2 foundation 没有给出我能证明的完整 reviewer RBAC，所以我不会说“任何 Agent 都能自审通过”。

### R1-Q079
V2 foundation 对“下一次 prepare_context 只读 APPROVED”有约束，但一条已经装进当前 ContextPacket 的 Memory 如果随后撤销，就存在 TOCTOU；当时没有我能证明的 MemoryEpoch/freshness token。强一致场景需要在模型调用或关键提交前重新验证 version/status，或者让撤销提升一个 context/security epoch 使旧 packet 失效。

### R1-Q080
这正是 V2 foundation 没有解决到生产级的地方。它当时主要是 contract、scope、readback 和 focused tests，没有 durable CAS/unique/transactional conflict resolver，所以我不能说它已经避免 lost update；企业化版本至少要有 dedupe key 唯一约束、版本/CAS 和冲突状态。

### R1-Q081
会有典型 lost update：两个事务都读到 v1，各自基于 v1 生成不同更新，后提交者覆盖先提交者；如果是多行条件还可能出现 write skew。READ COMMITTED 只保证读已提交，不替你自动解决业务级并发冲突。

### R1-Q082
我会优先用 optimistic version/CAS，因为 Memory 冲突通常适合短事务、低到中等竞争；配合唯一 dedupe key 防重复。只有确实需要串行修改同一条记录时才用 `SELECT FOR UPDATE`，而 SERIALIZABLE 成本更高，应该由冲突频率和一致性要求决定。

### R1-Q083
不会。模型调用是不可控的网络延迟，拿着 DB 行锁等几秒甚至更久会放大锁竞争、死锁和连接占用；应该先在事务外生成 proposal，最后用短事务+version check 提交，冲突就重算或进入 review。

### R1-Q084
如果 Context Pack 已经构建完，单纯删 DB 记录不能收回已经复制进 prompt 的内容，这是 TOCTOU。合规或高风险场景要在真正发模型前检查 MemoryVersion/Epoch 是否仍有效；如果做不到，就只能承认删除从下一次 context build 生效，而不能声称即时撤回。

### R1-Q085
`memory_id` 只告诉我“是哪条记录”，source trace 能回答“它来自哪段对话、哪个事件、哪次工具结果”。这对审计、冲突判断、删除衍生信息、解释为什么模型看到它都很重要；没有 provenance，很难判断一条长期记忆到底可不可信。

### R1-Q086
我倾向保留版本和来源，不直接覆盖。新信息先成为 candidate，冲突时把旧版本标记 superseded/stale 或把新候选 quarantine 待审；这样才能解释“什么时候、基于什么来源发生了变化”。

### R1-Q087
需要显式 freshness 语义，例如 `valid_from/valid_to`、expiry、superseded/stale 状态和来源版本。相似度只回答“像不像当前 query”，不回答“这个事实现在还是真的吗”。

### R1-Q088
抽取、embedding、检索这些能力我愿意直接复用 Mem0/OpenViking/Host；Zuno 真正需要 Own 的是 scope、review/provenance、权限和哪些 Memory 有资格重新进入法律任务上下文。历史上我参与过 OpenViking 相关工作，但公开仓库没有恢复具体 artifact，所以不能把“没找到 artifact”说成“我们技术比较后证明它不适合”。

### R1-Q089
目前没有任务质量 A/B 能证明 Memory 稳定提升。能证明的是 contract、scope、review/readback behavior 和 focused tests；如果要证明产品价值，必须比较 no-memory/session-summary/structured-memory 三组在目标任务上的正确性、污染率、token/cost 和长期一致性。

### R1-Q090
如果 A/B 没稳定收益，我会先删 structured long-term extraction/promotion/retrieval，只保留原始事件、必要的 session/task summary 和可解释 context assembly。长期 Memory 是可选增强，不应该因为已经写了 contract 就永久保留。

## F. Agent 拓扑与基础能力

### R1-Q091
因为当时 Single Agent 已经能完成主要 Tool/RAG 路径，拆 Planner/Researcher/Executor 会立刻增加 context、状态和失败边界，却没有 benchmark 证明收益。我的原则是先把 Tool、Subgraph、parallel worker 用到不够，再升级 Agent 拓扑。

### R1-Q092
我会要求出现至少一种可测失败：同一个 context 被太多专业信息污染、不同角色需要独立权限/Tool 集、任务生命周期明显独立、并行长任务需要独立恢复，且 Tool/Subgraph/worker 不能解决。只是 Prompt 不同、名字不同，不足以证明要 Specialist Agent。

### R1-Q093
共享任务控制状态应该由 Runtime/Controller 的单一逻辑 owner 管，正式法律业务事实由 Domain owner 管；Specialist 只提交 proposal/result，不应该各自维护一份“正式真相”。否则 late result、retry 和恢复时根本不知道哪份状态权威。

### R1-Q094
不能因为内容“看起来正确”就直接提交。开放设计里我会检查它对应的 PlanVersion/InputVersion/SecurityEpoch 是否仍然是 active；旧版本结果可以保留为 evidence 或触发重评，但不能越过当前版本直接写正式结果。

### R1-Q095
Checkpointer 能证明 Runtime 控制进度——执行到了哪个 node、有哪些 state；它不能证明外部系统副作用一定成功。比如 Tool 远端已经写成功，但本地 checkpoint 还没落就崩了，恢复时如果只看 checkpoint 可能重复执行，所以 Effect truth 必须有独立 receipt/idempotency/reconcile。

### R1-Q096
检索场景我不会默认让一个可选 graph source 抛异常就把 Vector/BM25 全部丢掉。更合理的是把三路结果封装成 source-level result/error，保留成功的 baseline source，Graph 失败就降级并记录；只有某个 source 被任务声明为 mandatory 时才让整体 fail closed。

### R1-Q097
不等于。本地 coroutine cancellation 只是停止本地等待/执行路径，HTTP 请求可能已经发出，远端服务也可能继续处理；除非协议和远端明确支持 cancellation 并确认撤销，否则仍然要按“可能已执行”处理。

### R1-Q098
Recall@K 看 relevant item 有没有进前 K，MRR 看第一个 relevant item 排得有多靠前。比如相关文档从 rank1 掉到 rank5，Recall@5 仍然是 1，但 MRR 明显下降，所以只看 Recall 容易掩盖排序退化。

### R1-Q099
BM25 擅长精确词、稀有实体、编号和法律术语，但同义改写容易漏；Vector 擅长语义近似，但可能把相似主题、不同实体或数字边界混在一起。Hybrid 的价值就是让 lexical precision 和 semantic recall 互补，再由统一 ranking/reranker 收敛。

### R1-Q100
我会先上最简单的：Generic Agent Host 或 Single Agent + 受控 RAG + Tool/API/MCP adapter + PostgreSQL 业务后端；能写死的流程就固定 Workflow。GraphRAG 只有 multi-hop eval 证明才 query-gated，长期 Memory 只有跨会话 A/B 证明才开，direct route 只有测到明确收益才留，Multi-Agent 只有 Tool/Subgraph/worker 都不够时再升级。