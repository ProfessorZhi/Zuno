# Red Wave 2 — Blind Review + 100 Targeted Follow-ups

status: `COMPLETE`
question_count: `100`
visibility: `RED_VISIBLE`
firewall: Red2 read only Frozen Resume, Red1, Blue1 candidate answers, pinned Attack Skill, and target role/stage. It did not read Blue architecture notes or canonical Zuno docs.

## Part A — Blue Wave 1 Blind Evaluation

### Credibility update

Blue1 的整体可信度上升。最明显的加分不是“每题都有答案”，而是多次主动把历史实现、当前事实和今天的开放设计分开：4 月 Tool/MCP 没有被包装成后来 Tool Control Plane；5-query GraphRAG smoke 没有被包装成正式 benchmark；Context/Memory V2 也没有被包装成 production-grade Memory。

目前最可信的三条个人工程主线：
- Tool/MCP：能稳定讲清 nested MCPAgent-as-Tool → concrete MCP Tool、call-time user config injection、tool→server map，以及 custom MCP recursion / weather extraction 两个具体回归点。
- GraphRAG：能讲清 regression 是 ranking displacement，不是 recall absence；baseline-preserving fusion 的排序 key、threshold、dedupe 和后续 seed/alias/path 改动都能落到机制。
- Context/Memory：能讲清 scope、candidate/review、prepare_context readback 与 ContextOrchestrator 的 foundation 边界，并明确 durable concurrency / revocation / quality evidence 尚未闭环。

### 仍然薄弱的地方

1. **项目/Agent 必要性仍缺历史反事实证据。** Blue 能给出“开放式任务适合 Agent”的合理设计解释，但还没有给出一个历史真实任务证明固定 Workflow 当时已经失败。
2. **Tool/MCP 并发隔离没有历史闭环。** Blue 主动承认 user_id 绑定 Agent 实例；共享实例、ConfigVersion、schema lifecycle、同名 Tool collision、outcome unknown 都没有被 4 月实现证明。
3. **direct route 的长期价值未建立。** 现有证据更像 deterministic optimization + bug hardening；没有 latency/cost/reliability benchmark。
4. **GraphRAG 的工程定位清楚，但价值证据很弱。** threshold=6/9、seed cap、alias/path heuristics 都缺 ablation；5-query development smoke 无 holdout，p95 也只是方向性信号。
5. **Memory 的 Authority 与 durability 是最大系统薄弱面之一。** equality scope 不等于 authorization；APPROVED 的写入权限、revocation、TOCTOU、并发 dedupe/conflict、过期/删除传播都没有被历史 V2 foundation 证明。
6. **Multi-Agent 没有被证明必要。** Blue 的复杂度阶梯回答合理，但仍然只有设计原则，没有 single vs specialist 的 measurement。
7. **Pilot / court-side testing 仍只能作为团队项目状态。** Blue 没有冒领，但个人参与深度仍未建立。

### Red1 前提修正

Red1 有些问题故意把今天更成熟的 Tool Effect / Memory / Runtime 语义压回 4–6 月历史。Blue 已正确指出这些不能反写历史。因此 Red2 不再问“当时为什么没有实现今天的对象名”，而是追：当时能力边界因此在哪里、今天最小补法是什么、什么证据才能升级 Claim。

### Red2 攻击权重

优先级：
1. Tool/MCP：并发身份、config/schema version、authorization 与 outcome unknown。
2. GraphRAG：heuristic 跳变、ablation、selection bias、query gating 与 kill gate。
3. Memory：scope authority、approval bypass、revocation/TOCTOU、durable concurrency、provider boundary。
4. Generic Host vs Zuno Backend / Multi-Agent：最小不可替代 contract 与状态 Authority。
5. Resume authenticity：继续检查最脆弱 Claim，但不重复已经建立的实现细节。

## Part B — 100 Targeted Follow-ups

### R2-Q001
你把 GraphRAG 说成最能代表工程深度，但公开可证明的更早个人改动是 Tool/MCP；你为什么认为“最深”而不是“最早”更适合作为主故事？

### R2-Q002
你说只看两个 commit 就能证明简历不是包装，这两个 commit 各自最关键的 before/after 可观察差异是什么？

### R2-Q003
你只能恢复出核心研发约 7–8 人，却没有完整 Owner map；那你如何确认某个设计决定是你个人决策而不是团队既定方案？

### R2-Q004
你说法院侧测试的个人参与细节是 Unknown；那简历项目简介继续写“法院侧测试”时，怎样避免面试官误解成你本人完成了现场验证？

### R2-Q005
你说 Agent 的必要性主要来自开放式动态编排；你手里有没有一个历史任务能证明固定 Workflow 当时真的不够？

### R2-Q006
如果拿不出“固定 Workflow 明确失败”的历史 case，你是否接受把 Agent 必要性降级为产品方向而不是已验证结论？

### R2-Q007
你说 GraphRAG、direct route、长期 Memory 都可能删除；那当前简历为什么同时放这三层复杂度，而不是只保留证据最强的一两条？

### R2-Q008
你说 Tool/MCP、GraphRAG、Memory 都有个人提交；哪一条最能证明你做过问题定位，而不只是按既有方案编码？

### R2-Q009
你在 Blue1 多次区分历史实现和今天设计；如果真实面试只有十分钟项目深挖，你会怎样避免这些边界说明把主线讲散？

### R2-Q010
Blue1 里你没有出现明显前后矛盾；如果 Red 继续质疑真实性，你认为最脆弱的可验证 Claim 具体是哪一个？

### R2-Q011
你承认 4 月 middleware 把 user_id 绑定在 Agent 实例上；如果框架后来把 Agent 实例做成池化复用，最直接的串租户失败路径是什么？

### R2-Q012
要证明共享实例安全，你会写什么并发测试才能真正覆盖两个用户同时调用同名 MCP Tool 的隔离？

### R2-Q013
你说配置是 call-time 读取；如果第一次调用失败后用户旋转了 credential，retry 应该沿用第一次配置还是读取新配置？

### R2-Q014
如果 retry 读取新 credential，怎样保证“同一个逻辑动作”的审计还能解释两次 Attempt 使用了不同配置？

### R2-Q015
你提出 ConfigVersion/frozen snapshot；这个版本应该绑定在 Run、Step、Tool Attempt 还是 Credential 上？

### R2-Q016
配置内容被 merge 进 tool args 时，哪些字段必须禁止进入普通日志或模型可见 Observation？

### R2-Q017
你那版 middleware 在取 MCP 用户配置失败时返回 ToolMessage 而不是抛出异常；模型继续推理时怎样避免把授权/配置失败误当成普通业务结果继续执行？

### R2-Q018
如果 MCP 配置缺失是安全失败，你会给 ToolMessage 增加什么机器可判定的错误类型，而不是只靠自然语言字符串？

### R2-Q019
你承认同名 Tool collision semantics 没证明；如果两个 Server 都叫 `search`，仅加 namespace 能解决哪些问题、解决不了哪些问题？

### R2-Q020
canonical tool id 如果包含 server id，而 server 被重建后 id 变化，历史 Trace 和重试怎样仍指向同一个逻辑能力？

### R2-Q021
你说 schema discovery 更接近初始化快照；长任务执行中 Server schema 变化时，旧 Tool Call 应该失败、迁移还是继续按旧 schema 执行？

### R2-Q022
如果选择继续按旧 schema 执行，Provider 已经不再接受旧参数时，谁负责把这个失败分类成 capability drift 而不是普通 Tool error？

### R2-Q023
Tool schema refresh 和正在进行的 model turn 并发发生时，怎样避免模型看到一版 schema、执行层使用另一版 schema？

### R2-Q024
你说真正授权应在执行边界做；如果 direct route 和 ReAct 都能触发同一个 Tool，怎样证明它们一定经过同一个 authorization gate？

### R2-Q025
4 月历史没有 Approval/Idempotency/Reconcile；如果面试官问“那你这套 Tool Calling 能不能安全改案件状态”，你会给出什么结论而不是设计未来方案？

### R2-Q026
你说 timeout 应进入 outcome unknown；在没有 EffectReceipt 的历史版本里，系统实际上能不能区分 unknown 和 failed？

### R2-Q027
如果历史版本区分不了 unknown/failed，你是否接受当时的 Tool Calling 更适合读操作而不是关键副作用操作？

### R2-Q028
你把幂等键 owner 放在 durable Tool/Effect Gateway；如果远端 Provider 本身提供幂等键，Zuno 还需要保存什么最小状态？

### R2-Q029
如果远端 Provider 完全不支持幂等查询和状态查询，Zuno 能否真正做到 exactly-once？

### R2-Q030
成熟 MCP Host 已经覆盖协议和执行；如果它也补齐 per-user config、schema version 和 tracing，你认为 Zuno Tool 层仍必须保留的最小业务 Authority 是什么？

### R2-Q031
你定义 direct route 的条件包含“目标唯一、参数确定、无需前序 Tool 结果、配置 gate 满足”；历史代码是否真的逐项显式判定了这四个条件？

### R2-Q032
如果历史 direct matcher 只是规则匹配，那你刚才这四条更像今天总结出的设计原则还是当时代码事实？

### R2-Q033
天气 city extractor 修复了一个具体句式；你怎么防止规则继续堆成大量脆弱的自然语言特例？

### R2-Q034
如果需要不断为每个 Tool 写参数 extractor，什么时候你会认定 direct route 已经退化成自研 NLU 层并应该删除？

### R2-Q035
direct route 的优势如果只是少一次模型决策，你会把什么 latency/token 指标设为最小值得维护的门槛？

### R2-Q036
如果 direct route 在简单任务快 200ms，但每月只占极少请求，你还会维护两条执行路径吗？

### R2-Q037
你说高风险 Tool 今天应先过统一安全网关；那 direct route 还有没有必要知道 Tool 风险等级？

### R2-Q038
如果 direct route 不知道风险等级，而统一 Gateway 会拦截，那 direct route 本身应该只负责什么、绝不能负责什么？

### R2-Q039
direct result 直接呈现给用户时，Tool 返回的大文本、恶意文本或敏感字段由谁做输出过滤？

### R2-Q040
如果统一模型 Tool Calling 在后续模型版本上已经足够稳定，你会怎样做迁移实验来证明可以删除 direct route？

### R2-Q041
你说 threshold=6 是 heuristic；给我一个 graph_signal 从 5 变 6 就会改变 candidate group 的具体边界行为，这种跳变为什么合理？

### R2-Q042
vector+graph 且 signal>=6 会进入 group 0；如果这个 vector 本来 baseline rank 很差，强 graph signal 会不会把一个错误候选过度提升？

### R2-Q043
graph-only signal>=9 可以进入 group 1；为什么 9 足以和有 baseline 证据的候选进入同一组？

### R2-Q044
你说固定权重的问题是 source score 不可比；那 `local_score + base_score` 最后仍作为 tie-break，这两个 score 又为什么可相加？

### R2-Q045
baseline_rank 取 vector_rank 和 bm25_rank 的最小值，会不会让只在一路偶然高排的噪声获得过强保护？

### R2-Q046
如果 Vector rank1 和 BM25 rank100，与 Vector rank10 和 BM25 rank10 相比，你的 min-rank 规则会偏向谁；这个偏好有证据吗？

### R2-Q047
同一 chunk 多路命中时主 score 取较高值；不同检索器 score scale 不一致时，“取高”是否有语义问题？

### R2-Q048
没有 chunk_id 时用 source+counter 去重 fallback；同一内容从 Vector 和 Graph 返回但都缺 id 时会发生什么？

### R2-Q049
candidate-aware seed 上限是 8；这个 8 是性能预算、经验值还是数据驱动参数？

### R2-Q050
如果 baseline 错候选进入 seed，你说会记录 seed source；最终评测如何量化“错误 seed 被图扩散放大”的比例？

### R2-Q051
alias normalization 只是字符串归一化；在法律实体里公司简称、同名自然人、法院简称发生碰撞时，你会选择 recall 还是 precision 优先？

### R2-Q052
如果改成稳定 entity id，需要谁生成和维护 id；这会不会把一个检索优化变成完整实体解析系统？

### R2-Q053
path-aware ranking 奖励 bridge/relation/support；你如何防止图中 high-degree 通用节点因为路径多而获得虚假 support？

### R2-Q054
你说有 generic penalty；这个 penalty 又是 heuristic，为什么不会继续形成第二套难以维护的手工打分系统？

### R2-Q055
fusion 最直接修复了 ranking displacement；在没有 ablation 的情况下，为什么 seed、alias、path ranking 不应该先回滚，只保留 fusion？

### R2-Q056
如果只保留 fusion 后独立 holdout 已经恢复 baseline，你会以什么证据决定是否重新加入另外三个复杂改动？

### R2-Q057
你报告 5 条样本 p95 约 26.6 秒；样本只有 5 条时 p95 这个统计量有什么解释风险？

### R2-Q058
正式性能评测你会用哪些分位数和重复方式，避免把单次网络抖动当成 GraphRAG 成本？

### R2-Q059
`fallback_count=1` 说明什么？这个 fallback 是正常降级还是图路径失败的信号？

### R2-Q060
如果 fallback query 的最终结果是正确的，你会把它记成 GraphRAG success 还是 baseline rescue？

### R2-Q061
你计划 query-class gating；分类器把本该单跳的请求错判成 multi-hop 时，最大损失是什么？

### R2-Q062
分类器把真正 multi-hop 请求错判成 baseline 时，怎样检测“需要图但没走图”的漏判？

### R2-Q063
如果 gating 本身需要一次 LLM 调用，GraphRAG 节省的成本会不会被 router 吃掉？

### R2-Q064
你会优先用规则、轻量模型还是主模型做 query gating；选择标准是什么？

### R2-Q065
在正式 benchmark 之前，你认为当前文档最应该写“GraphRAG 已实现”“GraphRAG 可选”还是“GraphRAG 待证明价值”？为什么？

### R2-Q066
你说 `None` scope 更像显式宽层级；谁有权把一条 project memory 写成 user-global memory？

### R2-Q067
如果调用方把 project_id 漏掉，equality match 本身不会报错；你准备在哪一层 fail closed？

### R2-Q068
MemoryScope 只有 user/agent/project/thread，没有 tenant/workspace/resource ACL；多租户企业环境里这个 contract 是否足够？

### R2-Q069
你说安全 scope 应由 authenticated Request/Workspace owner 构造；这属于 Memory 模块还是 Security 模块的 Authority？

### R2-Q070
`MemoryCandidate` 默认需要 review；代码层面能不能有人直接构造一个 status=APPROVED 的对象绕过 reviewer？

### R2-Q071
如果能直接构造 APPROVED，真正的安全边界应该放在数据模型、repository write API 还是权限层？

### R2-Q072
审核人批准一条 structured memory 时，怎样证明 reviewer 对该 scope 有审核权限？

### R2-Q073
APPROVED 后用户撤销权限，但 ContextPacket 已经构建完成；在模型调用前你会不会重新校验 SecurityEpoch/MemoryVersion？

### R2-Q074
如果不重新校验，这是不是一个明确的 TOCTOU 窗口？

### R2-Q075
同 scope 两个 MemoryCandidate 使用相同 dedupe_key 并发写入，没有数据库 unique/CAS 时会发生什么？

### R2-Q076
如果重复候选都被审核通过，readback 层是去重、选最新还是全部注入？

### R2-Q077
你说冲突应该先生成新 candidate 而不是覆盖；那两个相互冲突但都 APPROVED 的 memory 能不能同时进入 Context？

### R2-Q078
如果允许同时进入，模型如何知道哪个更新、哪个已经失效？

### R2-Q079
source_event_ids 能证明来源，但来源本身可能是模型幻觉或错误用户输入；provenance 为什么不等于 truth？

### R2-Q080
时间敏感 Memory 的 expires_at 到期后，是物理删除、逻辑失效还是保留审计但禁止 readback？

### R2-Q081
用户要求“忘掉这条信息”时，原始事件、task summary、structured memory、derived summary 谁负责级联处理？

### R2-Q082
你说 Memory 抽取应异步生成 candidate；异步 worker 处理旧事件时，如何避免用户已经删除/撤销的数据又被重新提炼回来？

### R2-Q083
ContextOrchestrator 有 token budget；如果预算不足时同时存在 system policy、recent user instruction、approved memory、knowledge evidence，谁的优先级最高？

### R2-Q084
如果 compression 模型把法律限定条件摘要掉了，trace 能告诉你发生过压缩，但怎样阻止错误上下文进入模型？

### R2-Q085
你目前没有 Memory 质量 A/B；那当前最小值得保留的 Memory 能力到底是什么？

### R2-Q086
如果 task summary 已能覆盖大部分长期任务，structured long-term memory 在什么测量结果出现前应该默认关闭？

### R2-Q087
Mem0/OpenViking 如果能提供抽取、去重和检索，Zuno 自己还需要拥有 reviewer/provenance/scope contract 的哪一部分？

### R2-Q088
如果以后换 Memory Provider，哪些数据必须保持 provider-independent 才能避免锁定？

### R2-Q089
你说最简单首版是 Generic Host/Single Agent + RAG + Tool + PostgreSQL；这里 PostgreSQL 里最先必须保存的业务状态是什么？

### R2-Q090
如果 Generic Host 能负责会话、workflow、普通 Tool Calling，Zuno Legal Backend 的第一个不可替代 contract 是什么？

### R2-Q091
你说 Multi-Agent 要等 Tool/Subgraph/worker 都不够；什么可测信号能证明“独立 Agent 身份”本身带来收益？

### R2-Q092
Single logical Controller 简化版本收敛，但如果 Controller crash，哪些事实必须从 durable store 恢复而不能只信 checkpoint？

### R2-Q093
Supervisor replan 后旧 Specialist 返回正确结果，你说要看版本；这个版本至少绑定哪些输入才能判断结果是否 stale？

### R2-Q094
如果旧结果不能提交，它能不能作为新计划的只读 evidence 复用？

### R2-Q095
checkpointer 记录控制进度，外部 Tool Effect 已经成功但 checkpoint 还没写就崩溃时，重启后最危险的行为是什么？

### R2-Q096
你说 exactly-once 很难；工程上通常追求的更现实目标是什么？

### R2-Q097
READ COMMITTED 下 lost update 可以用 optimistic version 解决；如果冲突率很高，乐观锁会出现什么问题？

### R2-Q098
`asyncio.gather` 一路失败时你选择 partial success；怎样避免另两路结果和失败一路使用了不同 corpus/index version？

### R2-Q099
取消 coroutine 不等于取消远端请求；如果远端后来成功返回，谁负责消费这个 late result？

### R2-Q100
经过这两轮回答后，如果只能从简历删除一条复杂度最高、证据最弱的 bullet，你会先删哪一条，为什么？
