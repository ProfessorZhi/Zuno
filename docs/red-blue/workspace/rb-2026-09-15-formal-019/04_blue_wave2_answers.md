# Blue Wave 2 Answers — rb-2026-09-15-formal-019

status: `COMPLETE`
answer_count: `100`
visibility: `RED_VISIBLE`

以下回答只使用 Red2 可见问题、pinned Blue Skill 与允许的 canonical truth；没有把 Blue1 sealed architecture notes 当作 coaching。

### R2-Q001
因为面试主故事要优先选能展示完整工程闭环的内容，不是按时间排序。GraphRAG 这条有“发现回退→定位 ranking displacement→改 fusion→继续做 seed/alias/path→复测”的链路；Tool/MCP 更早，但主价值偏调用链重构和 hardening。

### R2-Q002
Tool/MCP 的 before/after 是：nested MCPAgent-as-Tool/独立 selector 路径，变成 concrete MCP Tools 直接绑定 GeneralAgent，并在实际调用点按 tool→server 查用户配置。GraphRAG 的 before/after 是：弱 graph candidate 能把 baseline 命中文档挤出 Top-K，之后排序显式保护 baseline rank，只允许强 graph signal 晋升。

### R2-Q003
我不能只靠口头判断某个决定是我个人原创，所以个人 Ownership 只认能落到 authored commit、具体 diff、测试或设计记录的部分。团队方向和已有框架只说“项目已有/团队决定”，不转成我的个人决策。

### R2-Q004
项目简介里的法院侧测试描述项目阶段，不描述我个人职责；面试时我会主动补一句“这是团队项目状态，我本人具体现场参与深度目前没有完整证据”。如果正式简历容易误导，可以把措辞改成“项目经历法院侧测试与 Pilot Validation”。

### R2-Q005
目前没有恢复出一个历史真实任务能严格证明固定 Workflow 已失败。这个问题我会承认：Agent 必要性在历史证据上没有闭环，只能说项目方向和当时实现支持动态 Tool/RAG 选择。

### R2-Q006
接受。没有反事实 bad case，就不能把“必须用 Agent”写成已验证工程结论；更准确的是固定 Workflow 适合已知流程，Agent 作为开放任务的候选机制，价值需要按任务测。

### R2-Q007
简历放三条不是为了证明三层都长期正确，而是因为它们分别代表我实际做过的三类工程问题：Tool 调用链、检索质量、Context/Memory contract。若要进一步压缩，我会优先删 direct-route 独立 bullet，而保留 Tool 主线、GraphRAG 主线和 Memory 主线。

### R2-Q008
GraphRAG 最能证明问题定位，因为我先看到指标退化，再逐条检查 candidate/rank，把问题定位成 ranking displacement；不是拿到一个设计任务后直接实现。Tool recursion/weather bug 也有定位成分，但闭环更窄。

### R2-Q009
真实面试会先给一句结论，再只讲一层实现；只有面试官继续追时才展开历史/Current/Target 边界。比如先说“4 月没有副作用闭环，所以当时更适合读型 Tool”，而不是一上来解释整套 Target 架构。

### R2-Q010
最脆弱的是 direct route 的价值 Claim：代码和回归行为能证明，但没有 latency/cost/reliability benchmark。其次是法院侧测试的个人参与深度。

### R2-Q011
如果实例池复用，middleware 里的 user_id 可能仍是上一个请求的身份，同名 Tool 调用就可能拿错用户的 MCP config，直接形成跨用户 credential/config 污染。

### R2-Q012
我会让两个用户并发调用同一个 Tool 名，但配置里放不同、可观测且不会泄密的 marker；高并发交错多轮调用，断言每个实际 Provider request 只看到本用户 marker。同时覆盖 cancellation、retry 和实例复用。

### R2-Q013
如果是同一个逻辑动作的 retry，我倾向冻结第一次 Attempt 绑定的 ConfigVersion，除非安全策略明确要求旧 credential 已撤销。凭空切新 credential 会改变同一个动作的执行条件。

### R2-Q014
每个 Attempt 记录自己的 ConfigVersion/CredentialVersion，并通过同一个 Action/Idempotency key 关联。这样能解释“同一逻辑动作，第 1 次用 v1，第 2 次因撤销切到 v2”，而不是把它们混成一次不可审计调用。

### R2-Q015
CredentialVersion 属于 credential/config 自身；Tool Attempt 要引用它。Run/Step 可以持有输入版本集合做一致性判断，但我不建议复制同一个版本号到每层变成多份 Authority。

### R2-Q016
Secret、token、API key、cookie、私有 endpoint credential 和任何 provider auth 参数都不能进入普通日志或模型 Observation。日志只留引用 id、版本、provider/server id 和必要的 redacted metadata。

### R2-Q017
需要把配置/授权类失败变成结构化 terminal tool error，例如 `CONFIG_MISSING`、`AUTH_DENIED`，并由执行层标记不可由模型通过改参数绕过。单纯自然语言 ToolMessage 容易让模型误判为普通业务失败。

### R2-Q018
我会返回机器字段：error_code、retryable、security_relevant、provider、tool_id，模型只看到经过映射的安全文案。决策权仍在执行层，不让模型自己从字符串猜是否可重试。

### R2-Q019
namespace 能解决调用路由、配置查找和日志歧义；解决不了“两个 Tool 语义相同还是不同”“server 重建后的稳定身份”“权限策略是否继承”等生命周期问题。

### R2-Q020
canonical id 不应直接等于一次部署的 server id。更稳的是逻辑 provider/tool identity + version，server instance id 作为运行实例引用，这样历史 Trace 仍能指向同一个逻辑能力。

### R2-Q021
长任务内如果模型是按旧 schema 规划的，我更倾向 fail closed 并要求 replan，而不是自动迁移参数。只有显式声明 backward-compatible 的 schema minor change 才考虑继续。

### R2-Q022
Capability/Tool Gateway 负责把 provider 返回分类成 schema/capability drift，并附当前 ToolVersion；Runtime 再决定 replan。Provider 只报告事实，不拥有任务恢复策略。

### R2-Q023
模型 turn 开始时拿到 CapabilitySnapshot/ToolVersion 集合，执行层校验仍是同一版本；刷新生成新 snapshot，不修改正在使用的旧 snapshot。版本不一致就拒绝或 replan。

### R2-Q024
两条路最终必须进入同一个 ToolInvocation/authorization boundary。direct route 只能决定“候选 Tool 与参数”，不能拥有执行权；否则它就是安全旁路。

### R2-Q025
不能说能安全改关键案件状态。4 月历史只证明 binding/config/direct-route hardening，没有 Approval、Idempotency、OutcomeUnknown/Reconcile 的证据，所以关键副作用操作不能据此宣称闭环。

### R2-Q026
实际上不能可靠区分。没有 durable attempt/effect receipt 时，timeout 后最多知道本地没拿到成功响应，业务结果仍是 unknown；如果实现把它当 failed，那就是语义缺口。

### R2-Q027
接受。4 月那套更适合作为查询、天气、地图这类读型或可容忍重复的 Tool 路径，不能拿它证明关键现实副作用安全。

### R2-Q028
最小保存 Action/Attempt id、idempotency key、provider request id、credential/config version、attempt status、最终 provider receipt/reference，以及 reconcile 结果。远端幂等不代表本地可以不留审计。

### R2-Q029
不能保证真正的 exactly-once。更现实的是 at-least-once delivery + idempotent effect，或者 outcome-unknown 后 reconcile；如果 provider 两者都不给，只能限制副作用能力或要求人工确认。

### R2-Q030
最小 Authority 是：当前用户/资源是否允许执行、Approval binding、Action/Attempt/Effect 的耐久记录、幂等与 Reconcile，以及 Tool 结果如何影响 Zuno 业务事实。协议连接本身可以完全交给 MCP Host。

### R2-Q031
不是逐项显式判定。历史 direct matcher 是窄规则和 config gate；“目标唯一、参数确定、无需前序结果、配置满足”是我今天抽象出的正确边界，不应该反写成当时已有的统一 predicate。

### R2-Q032
更像今天的设计总结。历史事实只能说显式单步请求有 deterministic route、参数不完整/开放任务回 ReAct，以及已有若干具体 gate/test。

### R2-Q033
规则只适合少数结构稳定、参数简单的 Tool；每加一个规则都要有明确覆盖率和回归集。出现大量自然语言 parser 时应回模型 Tool Calling 或专门 parser，不继续堆特例。

### R2-Q034
当 route 规则开始需要维护实体解析、指代、上下文消歧、多语言、复杂参数依赖时，我会删掉它或把它降成极窄 fast path；那已经不再是简单优化。

### R2-Q035
不会预设一个拍脑袋阈值。会先测 p50/p95 latency、model calls、token/cost、success/fallback 和维护错误率，再预注册最小业务收益；收益不足就不保留。

### R2-Q036
大概率不维护。绝对收益只有 200ms 且覆盖率极低时，双路径测试、安全和维护成本可能更高；除非这个低延迟场景本身有明确 SLA 价值。

### R2-Q037
可以知道粗粒度风险等级用于是否允许 fast-path 候选，但不能据此绕过安全检查。最终风险判定和授权仍由统一 Gateway。

### R2-Q038
只负责候选 Tool/参数的确定性解析和路由提示；绝不能负责授权、Approval、credential 选择、幂等、Effect truth 或正式 Domain mutation。

### R2-Q039
执行边界需要做结果规范化、敏感字段 redaction、大小限制和 prompt-injection-safe packaging；最终展示层再做输出政策。Tool 原始文本不能无过滤直接成为高信任上下文。

### R2-Q040
在同一任务集上做 A/B：direct route vs 统一模型 Tool Calling，冻结模型和 Tool 集，比较成功率、延迟、token、错误类型和安全行为。若模型路径已接近或更好，就删除 direct route。

### R2-Q041
signal 5→6 会让 graph-only 从 group3 进入 group2，vector+graph 则可能进入 group0。这个硬跳变没有理论保证，是 heuristic 的典型风险，所以必须通过 ablation/敏感性测试验证，必要时改成连续 score 或 learned reranker。

### R2-Q042
会有这个风险。group0 会先于普通 baseline group1，所以一个 baseline rank 很差但 graph signal 刚过阈值的候选可能被推高；正式 eval 要专门测这种 false promotion。

### R2-Q043
没有充分证据说明 9 是合理分界。它只是“比 6 更强”的手工门槛；在正式系统里应通过 holdout 校准或直接用更简单的 reranker/learned score 替代。

### R2-Q044
也存在问题。它们至少来自同一 `RagHandler` 的本地相关度逻辑，比跨 retrieval source 的原始 score 可比一点，但没有校准证据；作为末级 tie-break 风险较小，仍应该做 sensitivity test。

### R2-Q045
会。min rank 是“任一路强证据即保护”的保守策略，能防止 baseline gold 被挤掉，但也会保护单路噪声；所以它适合作为 regression safety rule，不等于最优 rank fusion。

### R2-Q046
min-rank 会偏向 Vector rank1/BM25 rank100，因为 baseline_rank=1；另一个是10。这个偏好是安全底座的设计选择，不是已经被数据证明的全局最优。

### R2-Q047
有语义问题，所以主 score 不应该跨检索器直接解释。那版真正排序依赖 source rank/group，原始 score 更适合 debug；正式 fusion 应先校准或使用 rank-based 方法。

### R2-Q048
会被当成两个不同候选，造成重复占位和 Top-K 浪费。没有稳定 chunk/document identity 时，dedupe correctness 本身就是数据 contract gap。

### R2-Q049
8 是当时实现里的经验上限，主要为了控制扩展规模，不是数据驱动最优值。它和 threshold 一样需要预算/recall ablation。

### R2-Q050
把 baseline seed 标记来源，统计由错误 seed 触发的 graph expansion 数、进入 Top-K 比例、最终造成 answer/citation 错误的比例；和不使用 candidate seed 的对照组比较。

### R2-Q051
法律场景我会更偏 precision，尤其身份错误会污染证据链。歧义时保留多个 entity candidate + source context，而不是为了 recall 把它们强合并。

### R2-Q052
需要 Knowledge ingestion/entity resolution 层生成稳定 identity，并维护 provenance/version。是的，如果只是为 GraphRAG 排序临时引入完整实体系统，复杂度可能不值；这正是应该优先复用 provider 或保持轻量的理由。

### R2-Q053
对高 degree/generic 节点做 degree normalization、generic-node penalty，并要求路径覆盖多个 query seed/有具体 relation support。更重要的是在 eval 中单独看 generic hub false positive。

### R2-Q054
确实可能。heuristic 越堆越多，维护成本越高；如果规则数量持续增长，我会优先换成更简单的 learned reranker 或直接回 baseline，而不是继续造分数。

### R2-Q055
我认为应该先这么做。fusion 对应明确 regression；另外三个改动没有独立因果证据，所以最小可信修复应先保留 fusion，再用 ablation 决定其它是否值得。

### R2-Q056
只有当独立 multi-hop holdout 显示 baseline+fusion 仍有稳定 recall/path/citation 缺口，而且某个改动单独能补这个缺口、成本可接受，才重新加入。

### R2-Q057
n=5 时 p95 基本由最慢那一两个样本决定，统计不稳定，不能代表尾延迟分布。它只能提示“这条路径可能更慢”。

### R2-Q058
扩大 query 数和重复轮次，报告 p50/p90/p95/p99、均值/方差，同时分 query class；把 warm/cold cache、外部网络和图遍历时间拆开。

### R2-Q059
它说明至少一条请求没有走完整图路径而使用了降级路径，但仅靠计数不知道是预期 gate、图不可用还是异常。需要 fallback_reason 分类。

### R2-Q060
如果结果主要由 fallback baseline 得到，应记 baseline rescue / degraded success，而不是 GraphRAG success；否则会把降级能力错误归功于图路径。

### R2-Q061
主要损失是额外延迟、token和噪声风险，而质量可能不升。若图路径有副作用式昂贵查询，还会放大资源成本。

### R2-Q062
需要基于离线标注 query class 统计 gate recall，外加线上“baseline 低置信/证据不足但未触发图”的 failure log 回灌。不能只看 router accuracy。

### R2-Q063
会，所以 gating 本身也必须算进总成本。优先 deterministic features/cheap classifier；如果要主模型额外调用，GraphRAG 的收益门槛就更高。

### R2-Q064
优先规则 + 轻量分类器，因为 query class 往往可用实体数、关系词、baseline confidence 等特征判断；只有这些方法不够并且质量收益证明值得，才用主模型。

### R2-Q065
文档应该同时写两件事：Current 上“GraphRAG 代码路径已实现”，Target/产品价值上“仅可选且待正式 benchmark 证明”。只写“已实现”容易被误读成价值已成立。

### R2-Q066
写入更宽 scope 必须由 Memory policy + Security authorization 明确允许，不能由抽取模型或普通 caller 自己决定。默认 project memory 不自动升级 user-global。

### R2-Q067
在 write/read API 的 scope-construction boundary fail closed：敏感 memory 声明要求 project scope 时，缺 project_id 直接拒绝。不能指望 equality query 自己发现调用方漏字段。

### R2-Q068
不够。它只是 V2 业务 scope foundation，多租户还需要 tenant/workspace/resource ACL 或上层 security context；否则同 user id 体系变化就可能出问题。

### R2-Q069
Security 拥有“这个 caller 能访问哪个 scope”的 Authority；Memory 拥有 scope contract、存储和 readback 行为。Memory 不能自行发明权限。

### R2-Q070
如果构造器允许显式传 status=APPROVED，就存在 bypass 风险。安全不能只依赖 dataclass 默认值；正式写入必须经过受控 review transition API。

### R2-Q071
优先 repository/service write API + authorization layer，数据库再用约束做防线。数据模型本身只表达状态，不足以证明谁有权改变状态。

### R2-Q072
ReviewDecision 必须带 reviewer identity，并在提交时由 Security 校验 reviewer 对该 memory scope/layer 有审核权限；审核记录和 policy version 一起持久化。

### R2-Q073
对权限撤销这类安全变化，我会在真正调用模型前重新校验有效 SecurityEpoch；MemoryVersion 用于内容新鲜度。仅在 packet build 时检查一次不够。

### R2-Q074
是。packet 构建和模型调用之间存在可见的 TOCTOU 窗口；如果权限/删除能在这期间变化，就需要 epoch/version revalidation 或短生命周期 snapshot。

### R2-Q075
会产生重复 candidate，甚至两个都进入 review。durable store 需要 scoped unique/dedupe key 或 compare-and-swap，不能只靠应用层先查再写。

### R2-Q076
默认不应该全部注入。相同 dedupe key 需要选 authoritative current version；无法判定时标 conflict/review-required，而不是把重复项都塞进 prompt。

### R2-Q077
可以在审计层同时存在，但不应该作为两个“当前有效事实”同时 readback。需要 current/superseded/conflicted 语义或 Domain/Memory conflict policy。

### R2-Q078
需要 version/effective_at/supersedes 等关系决定当前项；若无法自动判断，就把冲突显式暴露给模型/人工，而不是让相似度排序偷偷决定真相。

### R2-Q079
provenance 只证明“这条 memory 从哪里来的”，不证明来源内容为真。用户可能记错，模型也可能抽错，所以正式事实仍需要业务 evidence/review。

### R2-Q080
我倾向逻辑失效 + 保留必要审计引用：过期后禁止正常 readback，但保留 provenance/history；真正隐私删除则按政策做物理或密钥销毁，不能混成同一种 lifecycle。

### R2-Q081
需要一个删除/失效 authority 记录 tombstone/version，并让 raw event、summary、structured memory、derived projection 都检查它。哪些数据依法必须保留由治理政策决定，不能简单全级联物理删。

### R2-Q082
worker 在产出 candidate 前检查 source event 的 current lifecycle/version；如果已删除/撤销，丢弃结果。否则旧任务可能把已删内容重新物化。

### R2-Q083
System/Security policy 和当前用户指令优先；然后是任务必需的 authoritative domain/evidence，recent context；Memory 属于可选增强，应在预算压力下更早裁剪。具体顺序需要 policy 明确。

### R2-Q084
关键法律限定条件不能依赖自由摘要；对高风险 evidence/constraints 使用 extractive/reference-preserving 表示，并做 source-id coverage/validation。trace 只是可观测，不是正确性保证。

### R2-Q085
最小保留 raw event + scoped task summary +可追溯 ContextPack。structured long-term memory 在没有 A/B 收益前可以默认关闭，只保留 contract/实验能力。

### R2-Q086
至少要证明跨会话任务在质量、完成率或交互成本上稳定优于 task-summary baseline，而且错误/过期率可控；否则不默认启用。

### R2-Q087
Zuno 要保留 provider-independent 的 scope、review authority、provenance、lifecycle、delete/revocation 和 readback policy；抽取/embedding/dedupe/retrieval 可以由 Provider 替换。

### R2-Q088
稳定 memory id、scope、source ids、review decision、lifecycle/version、retention/delete state、provider-independent content/provenance。向量索引和 provider 内部 metadata 不应成为业务 Authority。

### R2-Q089
最先保存 Matter/DocumentVersion 这类跨运行仍需稳定引用的业务根与版本，以及正式 Evidence/Decision/WorkProduct 关系；普通会话状态可以留给 Host。

### R2-Q090
第一个不可替代 contract 是跨运行仍需被正式承认和审计的 Domain State/Version，例如 DocumentVersion、Evidence、HumanDecision/WorkProduct 的正式历史。若业务没有这种需求，Legal Backend 也应继续简化。

### R2-Q091
例如独立 Specialist 能在固定模型/预算下显著提高某类任务质量、降低上下文污染或缩短并行长任务 latency，而且 Tool/Subgraph 做不到；必须用 A/B 证明，不以 Agent 数量作证。

### R2-Q092
要从 durable store 恢复当前 Domain version、正式 Admission/Decision、Effect receipt/reconcile、Security epoch，以及可重建 Plan/Step 的控制状态。checkpoint 只说明运行进度，不拥有业务事实。

### R2-Q093
至少绑定 PlanVersion、Step input version set、相关 Domain/Knowledge version、SecurityEpoch，以及必要的 Tool/Capability version。内容正确但输入版本旧，仍可能不能提交。

### R2-Q094
可以作为带 provenance 的 candidate/reference 重新验证后复用，但不能直接继承旧 step 的提交资格。复用和提交 Authority 要分开。

### R2-Q095
最危险的是重启后只相信旧 checkpoint，重复执行已经成功的现实副作用。必须先查 durable effect/action truth，再决定 retry/reconcile。

### R2-Q096
更现实的是 at-least-once execution + idempotent effect + durable dedupe/receipt + reconciliation，目标是 effectively-once business outcome，而不是宣称网络层 exactly-once。

### R2-Q097
高冲突率下会频繁 CAS 失败和重试，吞吐下降、尾延迟升高，甚至活锁；这时需要缩小写热点、串行化单 key writer 或悲观锁，而不是无限重试。

### R2-Q098
所有分支先绑定同一个 KnowledgeGeneration/IndexSnapshot version；结果合并前校验版本一致。若一路因刷新拿到新版本，要整批重跑或明确跨版本降级，不能静默混合。

### R2-Q099
拥有该远端 Effect/Request 的执行边界负责消费和对账；late result 不能直接推回已结束 coroutine。它应落 durable Attempt/Receipt，再由 Runtime/Effect reconciler 判断是否仍可应用。

### R2-Q100
如果必须删一条，我先删“Workspace direct route”独立 bullet。它有真实 hardening 工作，但长期价值证据最弱，而且容易把简历复杂度从核心 Tool/MCP 主线分散出去；可以并回 Tool/MCP 一条里。
