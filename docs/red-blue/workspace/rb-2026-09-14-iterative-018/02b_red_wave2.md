# Red Wave 2 — rb-2026-09-14-iterative-018

mode: BATCH_WAVES
input_blue_wave1_commit: 14faf4c3061e43bebbec788c7766fde0e7f33c15
question_count: 100
adaptive_from_blue_wave1: true

这一波只攻击 Blue Wave 1 自己暴露的薄弱点，不按原 Pressure Suite 顺序补题。所有问题都以 Blue Wave 1 的回答为可见输入，不读取隐藏答案。

## A. Tool / MCP config / routing / failure boundary

### R2-Q001
你说 per-user config lookup 存在，但并发隔离没证明。假设 `GeneralAgent` 实例被两个用户复用，middleware 里的 `user_id` 到底从哪来？如果它是实例字段，你前面的说法还能成立吗？

### R2-Q002
如果 `GeneralAgent` 是 per-request 实例，那创建和销毁成本、Tool discovery 缓存、连接复用分别放在哪里？你怎么避免为了隔离把所有资源都重复初始化？

### R2-Q003
如果 `GeneralAgent` 是 per-user 长生命周期实例，一个用户同时开两个请求时，哪些字段必须 immutable，哪些允许 request-local？

### R2-Q004
你说 call-time 现查配置会产生长任务配置漂移。你要加 version pin 的话，ConfigVersion 由谁创建、存在哪里、一次 Tool retry 用旧版本还是新版本？

### R2-Q005
如果用户在任务执行中撤销某个 MCP Server 授权，但当前 Plan 已经引用了它，下一次 Tool Call 是 fail closed、replan，还是继续使用冻结配置？为什么？

### R2-Q006
两个 MCP Server 暴露同名 Tool，你提出 canonical tool id 要带 server identity。这个 id 进入 LLM schema 后怎么保持可读？display name、routing id、audit id 要不要拆开？

### R2-Q007
如果 Tool display name 为了模型可读进行了重命名，模型生成的 tool name 怎样稳定映射回唯一 server/tool identity？这个 mapping 谁拥有？

### R2-Q008
MCP Server 的 Tool schema 更新了，但 Agent 仍持有旧 schema。你准备让 discovery cache 按 TTL、ETag/version 还是连接事件失效？为什么？

### R2-Q009
旧 schema 已经进入本轮模型上下文，下一步 discovery 又发现新 schema。当前 turn 使用哪一版？如何避免同一 turn 内 contract 漂移？

### R2-Q010
你承认 direct route 可能绕过 Agent policy。authorization/config/audit gate 应该放在 route 之前、Tool execution 之前，还是两处都要？分别防什么？

### R2-Q011
如果 direct route 和 ReAct 最终都调用同一个 Tool，怎样设计才能保证两条路径不各自复制一套安全检查？

### R2-Q012
如果 route 层只做意图识别，Tool Gateway 做最终授权，那 route 层还能依据“当前用户没权限”提前筛掉 Tool 吗？这样会不会造成 policy duplication？

### R2-Q013
天气这种 deterministic route 可以短路 ReAct。如果用户说“查南京天气，如果下雨就帮我提醒同事”，前半段能 direct，后半段有副作用。你怎么拆？

### R2-Q014
“继续查刚才那个城市”缺显式参数。你说可能回 ReAct；如果 recent context 已经能确定 city，你会允许 deterministic parser 读 Context Pack 吗？谁保证它没读错旧值？

### R2-Q015
你说没有完整 ReAct hard max。假设 Tool 连续返回可重试错误，模型每轮都继续调用，谁拥有停止权？Agent prompt、Runtime budget 还是 Tool middleware？

### R2-Q016
如果停止权在 Runtime budget，budget 应该按 tool-call count、model-call count、wall-clock、token、cost 还是组合约束？哪个是 hard stop？

### R2-Q017
Tool timeout 后模型想立即 retry，但远端可能已经执行。你会允许 Agent 自己决定 retry 吗？如果不允许，谁把 unknown outcome 转成可重试或不可重试？

### R2-Q018
你说历史 Tool code 不等于完整 Effect reconcile。那当前简历里讲 Tool Calling 时，怎样避免面试官误以为你已经解决了副作用幂等？

### R2-Q019
如果一个 Tool 明确是 read-only GET，另一个是会修改法院系统状态的 POST，你会在 Tool contract 里增加什么 effect metadata？它会参与 routing 吗？

### R2-Q020
什么条件下你会删除历史 direct route，统一交给通用 Agent Host？给出至少一个质量指标、一个成本指标和一个维护指标。

## B. GraphRAG fusion / ranking / evaluation

### R2-Q021
`GRAPH_PROMOTION_THRESHOLD=6` 是 heuristic。你现在要证明这个 6 不是拍脑袋，最小需要做什么实验？

### R2-Q022
如果 threshold 从 6 调到 4，Recall 上升但 baseline gold 被挤出的概率也上升，你会用什么 objective / constraint 选点？

### R2-Q023
如果 threshold 从 6 调到 9，precision 上升但多跳 query 的 graph-only supporting doc 进不了 Top-K，你会怎么判断哪类 query 需要不同 threshold？

### R2-Q024
你会用全局 threshold，还是按 query class / corpus / graph density 配不同 policy？如果分 policy，配置版本如何进入 eval provenance？

### R2-Q025
你承认没有 explicit final tie-break。相同输入因为输入顺序变化而抖动，会影响 eval、cache、citation、debug 哪几层？你先修哪个？

### R2-Q026
如果加 `chunk_id` 作为最终 tie-break，结果稳定了，但 `chunk_id` 本身在重建索引后变化怎么办？稳定排序键应该依赖什么？

### R2-Q027
Vector、BM25、Graph raw score 不可比，你用 rank-based heuristic 绕开了 calibration。什么情况下 rank fusion 仍然会失败？

### R2-Q028
一个 retriever 只返回 5 个候选，另一个返回 100 个候选，rank 的含义还公平吗？你会不会做 reciprocal-rank 类归一？

### R2-Q029
你说同 chunk 多来源命中会 merge。Vector 和 Graph 指向同一个 chunk 但理由完全不同，merge 后你保留哪些 source-specific evidence 才方便 debug？

### R2-Q030
没有 chunk_id 时 fallback key 按 source+counter，跨 source 不能可靠去重。这个问题会怎样影响 fusion score 和最终 Context Pack？

### R2-Q031
你说 GraphRAG 回退是 Top-K displacement。除了看最终 Top-K，你还会记录什么中间态来证明 displacement 因果链？

### R2-Q032
如果 baseline gold-like 文档被 graph candidate 挤到第 6，而最后生成答案仍然正确，你会把它算 regression 吗？为什么？

### R2-Q033
Recall@5 恢复了，但 MRR 下降，你认为修复成功了吗？什么时候 Recall 比 MRR 更重要？

### R2-Q034
FullChainHit@5 提升但 latency 翻倍，你如何定义“GraphRAG 值得保留”的 release gate？

### R2-Q035
你前面说 p95 约 26.6s 对 19.0s，但样本只有 5 条。这个数字在面试里到底该不该主动讲？怎样讲才不误导？

### R2-Q036
5 条样本里 1 条 fallback，占 20%。你会不会把 fallback rate 当成这个 smoke 的重要风险信号？为什么？

### R2-Q037
开发过程直接围绕这 5 个 bad case 修，rerun 回到 5/5。你下一步怎样设计 holdout，避免 regression set 变成训练集？

### R2-Q038
如果正式 benchmark 只有几十条法律 query，统计波动很大，你会怎样报告置信区间或至少避免过度解释百分点变化？

### R2-Q039
没有 per-commit ablation，fusion/seed/alias/path 四个改动一起上。你怎么设计最小消融来判断哪个机制真正必要？

### R2-Q040
如果消融发现 alias normalization 对当前数据集没收益，你会删代码，还是因为“未来可能有用”继续保留？判据是什么？

## C. Multi-hop graph / entity identity / freshness

### R2-Q041
candidate-aware seed 从 baseline title/file/entity mention 扩展。baseline 本身错了时，这种做法会不会把错误放大？你如何检测 seed poisoning？

### R2-Q042
默认最多 8 个 seed。这个 8 是怎么来的？如果 query 有 20 个实体，你截断后怎样保证关键 bridge entity 没被丢掉？

### R2-Q043
hop limit 2、max paths per entity 10 都是 heuristic。图密度很高时，哪个参数先成为瓶颈？你怎么测？

### R2-Q044
path score 里 seed coverage、relation cue、bridge/comparison bonus 都是规则。不同法律领域 relation type 不同，你准备怎么避免硬编码爆炸？

### R2-Q045
如果 query 是“谁是某公司实际控制人的配偶”，关系链长度可能超过 2。你会动态 hop，还是先让 baseline 找 bridge doc 再局部扩图？

### R2-Q046
alias normalization 去括号后缀会误合并。法律场景里“某公司（北京）”和“某公司（上海）”怎么防止被合并？

### R2-Q047
只加 entity type 不够，因为两个“张三”都是 Person。你认为 stable identity 至少还要绑定哪些字段或来源？

### R2-Q048
如果实体是在 ingestion 时生成 StableEntityID，后来发现两个实体其实同一人，需要 merge。旧 path、citation、cache 和 eval record 怎么迁移？

### R2-Q049
反过来，如果一个实体误把两个人合在一起，需要 split。已经生成的 path evidence 如何重算？旧结果能不能继续引用？

### R2-Q050
你会给 Entity 一个可变 ID 还是不可变 ID + Version？为什么？

### R2-Q051
如果 EntityVersion 变了但 DocumentVersion 没变，Graph IndexVersion 要不要变？谁负责传播 invalidation？

### R2-Q052
一个查询拿到旧 graph path，但新 DocumentVersion 已经生效，谁应该拒绝这个结果：Retriever、Fusion、Context builder 还是 Domain？

### R2-Q053
如果旧 graph path 只是研究候选，不会直接成为业务事实，是否可以允许 eventual consistency？允许到什么程度？

### R2-Q054
Graph cache 按 query 缓存还是按 entity/path 缓存？两种方式分别怎么做版本失效？

### R2-Q055
图里存在 cycle 时你有 seen_paths/seen_chunks。为什么这还不能证明一般意义上的 cycle-proof？

### R2-Q056
如果同一个 chunk 被 5 条 path 支持，path_count 变高就加分。5 条高度相关的重复 path 会不会虚高 evidence？怎么去相关？

### R2-Q057
两个 path 指向相互矛盾的文档，一个来自新版本，一个来自旧版本。ranking 应该先看 relevance 还是 freshness？

### R2-Q058
正式 query-class benchmark 你会怎么分：单跳事实、多跳关系、比较、版本敏感、身份消歧之外还需要什么？

### R2-Q059
什么样的 query class 你会明确禁止 GraphRAG，即使它偶尔能提高 recall？

### R2-Q060
如果正式 benchmark 证明 identity-sensitive GraphRAG 没稳定收益，你会删除 StableEntityID 这套复杂设计吗？哪些最小结构仍可能保留？

## D. Context / Memory scope / approval / freshness / persistence

### R2-Q061
`MemoryScope` 的 project/thread 都是 optional。调用方漏填时 scope 变宽，这不是类型系统能挡住的。你会在什么层把“哪些字段必须存在”变成 policy？

### R2-Q062
不同 Agent 类型是否允许不同最小 Scope？例如通用助手只要 user，法律案件 Agent 必须 project/thread。这个 policy 谁拥有？

### R2-Q063
如果 caller 构造了错误 project_id，但格式合法，exact-scope equality 仍然会读错。你怎么防这种语义错误？

### R2-Q064
你会让 Security 层校验 user 对 project/thread 的 membership，再让 Memory read，还是让 Memory 自己做 authorization？为什么？

### R2-Q065
ContextOrchestrator 负责 selection/token budget，但不拥有 Memory truth。那 Memory item 进入 orchestrator 前需要携带哪些 authority/freshness metadata？

### R2-Q066
task summary 和 approved structured memory 冲突，你说不能靠 priority 决定真值。那谁有 authority 做仲裁？如果两者都只是上下文材料，模型该看到两个还是只看到一个？

### R2-Q067
如果 summary 是“任务进展”，structured memory 是“长期事实”，两者语义不同，你会不会禁止它们直接互相覆盖？如何在 schema 层表达？

### R2-Q068
你说 InMemory store 没 durable concurrency 语义。如果切 PostgreSQL，你会给 dedupe_key 加什么约束？scope 要不要进入 unique key？

### R2-Q069
两个事务同时从同一组 RawMemoryEvent 生成不同 summary，unique constraint 只能防完全重复，不能决定哪个 summary 正确。你怎么收敛？

### R2-Q070
如果 summary 生成是异步的，turn N+1 已经开始，但 turn N 的 summary 还没写完。N+1 应该等、读旧 summary，还是继续不用 summary？

### R2-Q071
APPROVED read gate 有 TOCTOU。你提 version/epoch，那 ContextPacket 需要绑定什么版本？在模型调用前谁再验证一次？

### R2-Q072
如果 approval 在模型调用之后、Tool 调用之前被撤销，模型已经基于旧 Memory 做了计划。你会允许后续 Tool 执行吗？

### R2-Q073
用户要求删除一条 Memory，但它已经进入当前 ContextPacket。你的语义是本轮继续执行、立即取消、还是标 stale 后阻止后续副作用？谁做这个决定？

### R2-Q074
代码允许直接构造 `review_status=APPROVED` 的 candidate。你要把 approval authority 收紧，最小要改 contract、store 还是 service boundary？

### R2-Q075
`MemoryReviewDecision` 带 reviewer_id。谁有资格成为 reviewer？这是业务角色、系统服务还是模型？

### R2-Q076
如果自动规则可以 auto-approve 某类 Memory，它和人工 approval 的 authority level 是否相同？你会怎样记录？

### R2-Q077
source_event_ids 可以追来源。如果源事件后来被纠正，不删除 Memory 而是追加 correction event，可否保证旧 Memory 不再 readback？

### R2-Q078
如果一个 Memory 由 10 个 source_event 聚合而成，其中 1 个被删除，整个 Memory 失效还是重算？谁触发？

### R2-Q079
Memory 进入 Context 后被模型引用到最终回答。你会不会把 Memory source ids 继续传播到 response citation/provenance？什么时候有必要？

### R2-Q080
你怎么做正式 Memory A/B：baseline、task class、质量指标、长期污染率、token/latency/cost 和 kill condition 分别是什么？

## E. Agent topology / Multi-Agent / Runtime authority

### R2-Q081
你说优先 Tool，再 Subgraph，再 Specialist Agent。给一个明确判据：什么时候“独立 context/tool policy”足以让 Subgraph 升级为 Agent？

### R2-Q082
如果一个 Specialist 只调用固定几个 Tool、没有自己的长期目标和 Memory，它为什么不是 Capability/Tool？

### R2-Q083
如果 Specialist 需要独立模型、独立 prompt、独立 eval，但没有独立 durable state，它算 Agent 还是 Provider？你的边界是什么？

### R2-Q084
假设法律任务拆成检索 Agent、事实审查 Agent、文书 Agent。三者都发现需要修改案件状态，谁能写正式 Domain state？

### R2-Q085
如果只有 Domain 能正式写状态，那么 Specialist Agent 的结果应该是什么类型：建议、Candidate、Evidence，还是 Decision？谁定义 contract？

### R2-Q086
Supervisor + Specialist 中，Specialist 返回晚到结果，而 Supervisor 已经 replan 到新版本。这个 late result 是丢弃、存档还是重新评估？你靠什么版本关系判断？

### R2-Q087
如果 late result 质量很高但基于旧 EvidenceVersion，是否允许进入下一 Plan 作为候选材料？谁负责 re-admit？

### R2-Q088
如果 Specialist 自己有 Memory，它和全局 Memory 的边界是什么？同一个事实被两个 Specialist 各自记住，谁负责 dedupe 和撤销？

### R2-Q089
多 Agent 共用一个 Context Pack 会造成上下文污染；完全隔离又会重复检索。你会怎样设计共享最小事实与私有工作上下文？

### R2-Q090
Supervisor 自己成为逻辑单点。如果吞吐成为瓶颈，你先按 case_id 分区 controller，还是让多个 controller 竞争同一 case？为什么？

### R2-Q091
Single logical controller + parallel workers 相对真正 Multi-Agent 多了什么能力，少了什么能力？为什么不直接一直停在这里？

### R2-Q092
如果 Parallel Worker 已能并行检索/分析，但不能自主 replan，你认为这是否已经解决大多数 Multi-Agent 需求？什么剩余需求值得升级？

### R2-Q093
Persistent Multi-Agent 的 benchmark baseline 应该是什么：Single Agent、Single Controller+Workers、Subgraph 还是 Generic Host？为什么可能需要多 baseline？

### R2-Q094
你要证明 Persistent Multi-Agent 值得存在，除了回答质量，还至少要看哪些系统指标：token/cost、latency、recovery、duplicate work、coordination failure、人工介入之外还有什么？

### R2-Q095
多个 Specialist 给出冲突结论时，Supervisor 是投票、按资格、按证据质量还是交给 Domain/Human？为什么不能简单 majority vote？

### R2-Q096
不同 Specialist 使用不同模型版本，结果写回同一任务时，ModelVersion/PromptVersion 是否必须进入 result binding？不记录会导致什么恢复问题？

### R2-Q097
如果通用 Agent Host 已经支持 supervisor、subgraph、checkpoint、parallel worker，你们自研 Runtime 还应该 Own 哪个最小 Delta？

### R2-Q098
如果 Generic Host + Zuno Backend 在质量、成本和恢复上都不差于自研 Multi-Agent Runtime，你会删哪几层？哪些 Authority 仍必须留在 Zuno？

### R2-Q099
反过来，如果 Multi-Agent 只在少数高复杂案件明显更好，你会做全局默认 topology，还是 per-task topology selection？选择器需要什么证据？

### R2-Q100
综合 Blue Wave 1 暴露的所有问题，如果现在只能批准一个下一轮架构实验，你选 Tool config versioning、GraphRAG formal eval、Memory approval freshness，还是 Multi-Agent topology A/B？为什么它的信息增益最高？
