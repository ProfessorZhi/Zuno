# Blue Answers — rb-2026-09-13-resume-first-014

formal_input_head: f9557c143fc0de333385ec3bf3ab56c5fd8f9b2b
zuno_base_sha: 10869d9176d2ef34b46577478bba62d9e254158a

原则：项目事实只按固定 Zuno sources 回答；文档没有证明的实现细节明确写 Unknown。通用网络 / Python / 数据库原理可以回答，但不会反向补成 Zuno 已实现能力。

## Q001
**Answer**
简单法律问答可以是权限检查 + 受控检索 + 引用 + 一次模型生成，不需要完整 Agent。Zuno 的复杂度只在任务跨越持续变化的材料、长期运行、专业人员正式判断、版本化成果和外部副作用时才有价值；这些场景需要等待、恢复、重规划和多种专业能力协作。

**Source trace:** `docs/project/README.md`; `docs/architecture/architecture.md`.

## Q002
**Answer**
能确认项目经历过 Internal Demo、客户侧 / 智慧法院项目组 Demo、法院侧人员测试和 Pilot Validation。当前资料没有恢复每个阶段的完整参与人、环境、题集、时长和验收标准，所以我不会把 Pilot 解释成 Production 或正式验收。

**Source trace:** `docs/project/README.md`; `docs/governance/project-fact-provenance.md` PF-015–PF-020.

## Q003
**Answer**
我加入时项目已经有代码和一个较简单的自研前端；公开历史还说明 4 月根提交已经存在 Memory 子系统，所以不能说我是从零搭系统。能精确认领的后续增量包括 4 月 Tool/MCP strategy 与 Workspace route hardening、6 月 GraphRAG 质量优化、6 月 Context/Memory V2 与 PR #8；“加入当天 Agent/RAG/Tool 各到什么程度”目前没有完整恢复。

**Source trace:** `docs/governance/project-fact-provenance.md` PF-008–PF-014, PF-029–PF-032.

## Q004
**Answer**
可恢复的核心研发规模约 7–8 人，但正式组织图和每个人的 Owner 没有恢复。Tool Calling、GraphRAG、Context/Memory 的列出提交可以作为我个人实现主故事；完整 Agent Runtime、完整 Memory、整个 GraphRAG 系统不能认领；架构 bullet 应说“参与设计/复盘”。

**Source trace:** `docs/governance/project-fact-provenance.md` PF-006, PF-009–PF-014, PF-029–PF-032.

## Q005
**Answer**
公开证据支持的顺序是：4 月 15/28 Tool Calling；6 月 20 GraphRAG retrieval quality；6 月 25/26 Context/Memory V2 foundation；6 月 29 PR #8 readback hardening；后续再做更系统的架构与证据复盘。它们是同一项目里的演进工作，不应编造成一条每一步都严格依赖前一步的单链路。

**Source trace:** `docs/governance/project-fact-provenance.md` PF-029–PF-032.

## Q006
**Answer**
当前能确认的具体负反馈是客户侧 Demo 曾反馈“回答质量还需要提高”。完整 bad case 和根因没有恢复，所以不能把后来 HotpotQA 的 GraphRAG regression 反写成当时客户问题的根因。

**Source trace:** `docs/project/README.md`; `docs/governance/project-fact-provenance.md` PF-017, PF-031.

## Q007
**Answer**
Pilot 只能证明项目进入过 Pilot Validation 这一历史阶段，不能自动证明生产部署、SLA、用户规模或性能稳定性。真实用户数、QPS、P95、SLA、HA 等目前都应回答 Unknown。

**Source trace:** `docs/governance/project-fact-provenance.md` PF-019–PF-022; `docs/evidence/README.md`.

## Q008
**Answer**
GraphRAG 的量化结果来自 HotpotQA 小样本研发 smoke，不是法院数据。Tool Calling 和 Context/Memory 有历史 commit/test artifact；它们是否在法院侧相同版本、相同路径真实运行，目前没有足够 evidence。架构复盘属于后续设计工作。

**Source trace:** PF-029–PF-032; `docs/evidence/README.md`.

## Q009
**Answer**
项目确实经历过本地研发、Demo、法院侧测试和 Pilot 类阶段，但当前文档没有恢复这些环境的配置、数据权限、Provider、网络和部署差异。我可以讲今天 Target 应怎样隔离，但不能把 Target 配置冒充历史部署事实。

**Source trace:** `docs/project/README.md`; PF-015–PF-022.

## Q010
**Answer**
我会明确说：项目有 Demo、法院侧测试和 Pilot Validation 历史，但 Production 没有证据。至少要有生产 endpoint / 部署证明、正式验收、持续运维监控、SLA/故障证据等，才有资格升级这个 claim。

**Source trace:** PF-019–PF-020; `docs/evidence/README.md`.

## Q011
**Answer**
如果必须选一条，我会选 GraphRAG regression/fix：它同时有失败现象、连续代码改动和同口径小样本 rerun，最能展示“发现退化 → 定位 → 修复 → 测量”的闭环。它的上限也很清楚：样本很小、没有正式 ablation，不能宣传成普遍收益。

**Source trace:** PF-031.

## Q012
**Answer**
按现有文档最容易精确讲的是 `GeneralAgent.prepare_context()` 的 PR #8，或者 4 月 Tool/MCP strategy。前者能讲清 readback 前后差异：same-scope task summary、仅 `APPROVED` structured memory、Context Pack policy/source trace；但完整函数内部每个分支仍需要现场代码才能继续下钻。

**Source trace:** PF-029–PF-030.

## Q013
**Answer**
当前 canonical provenance 没有恢复这些任务的 reviewer 身份和完整 review discussion。能证明的是 commit/PR/test artifact，不应把“存在 PR”自动说成“经过怎样的正式 code review”。

**Source trace:** PF-029–PF-032 的 future evidence / known limits.

## Q014
**Answer**
当前 Zuno canonical docs 没有登记我在这些历史任务里具体用了哪些 Coding Agent、生成了多少代码。这个问题必须回到真实个人过程回答，不能由架构文档代写；本轮只能把它标成 Ownership evidence 未归档。

**Source trace:** project provenance does not establish this fact.

## Q015
**Answer**
一个可核对的失败就是 GraphRAG 初始 local 路径把 baseline 已命中的文档挤出 Top-K，使 sampled `Recall@5` 从 1.00 掉到 0.80。它说明“加图”本身不是提升；复杂机制先要保住 baseline，再用更大评测证明净收益。

**Source trace:** PF-031.

## Q016
**Answer**
能确认修改前存在独立 selector scaffolding、MCPAgent/SkillAgent-as-Tool 路径，修改后 concrete MCP tools 直接绑定 `GeneralAgent`。但当时为什么决定改、是 latency 还是错误传播驱动，目前没有原始 Issue/需求证据，所以不能补成确定根因。

**Source trace:** PF-032.

## Q017
**Answer**
文档能支持的 before/after 是：nested Agent-as-Tool / selector scaffolding → `GeneralAgent` 直接绑定 concrete tools；调用时 middleware 按 tool→server 注入用户 MCP config。Tool schema discovery、模型选择细节、结果回注的完整历史 call graph 没有在 canonical provenance 冻结，现场要回代码讲。

**Source trace:** PF-032.

## Q018
**Answer**
目前没有历史 latency/token/error 指标证明多一层 Agent 的具体成本，因此不能说“因为多一次模型调用所以优化”。我能说的是结构被收口了；为何收口以及收益大小仍缺原始问题和 measurement。

**Source trace:** PF-032; PF-022.

## Q019
**Answer**
现有 provenance 证明 concrete MCP tools 被 `GeneralAgent` 直接绑定，但没有冻结“启动时 / 每请求 / 每 Workspace”的构造生命周期。这个问题属于可追代码的实现细节，当前文档不足。

**Source trace:** PF-032.

## Q020
**Answer**
文档只证明存在 tool→server 映射用于调用期配置注入，没有冻结其数据结构、唯一键或同名 tool 冲突策略。我不会现场编一个 dict key 设计冒充历史实现。

**Source trace:** PF-032.

## Q021
**Answer**
项目级并发隔离实现没有在历史 provenance 中证明，所以不能声称用了 `ContextVar`。原则上用户凭证必须成为 request/task scoped immutable context；`ContextVar` 会随 asyncio task context 复制，但跨线程/显式 executor 需要额外传播，不能把全局可变对象当用户配置容器。

**Source trace:** Project-specific implementation Unknown; general Python reasoning only.

## Q022
**Answer**
历史实现没有足够证据回答并行 Tool Call 的共享状态和 data-race 防护。正确设计应共享只读请求上下文并隔离 attempt-local state / credential lease，但这是设计要求，不是 PF-032 已证明事实。

**Source trace:** PF-032 limit; `docs/modules/effects/reference.md` for Target attempt/credential separation.

## Q023
**Answer**
MCP 通常由 server 暴露 schema，客户端/adapter 做结构化校验；但 Zuno 当时在哪一层校验、怎样处理 JSON/Python 类型漂移没有在 provenance 中冻结。只能回答通用机制，不能认领具体历史行为。

**Source trace:** PF-032 limit; general MCP knowledge.

## Q024
**Answer**
能确认 Workspace Agent 存在 deterministic direct route 与 ReAct fallback，以及 4/28 做过 route hardening；精确 matcher/规则没有在 canonical source 中冻结。这个问题需要回历史代码或 test artifact。

**Source trace:** PF-032.

## Q025
**Answer**
当前文档不足以给出历史 direct-route 的完整判定表，所以我不会制造“参数完整就 direct”的精确规则。能说的是两条路径确实并存；真实边界需要代码/test 恢复。

**Source trace:** PF-032.

## Q026
**Answer**
PF-032 不能证明 4 月 routing 已有副作用去重和 Unknown-outcome recovery，所以不能把后来的 Effect 设计反写进去。今天的 Target 规则是：可能已发送的有副作用动作不能因为 fallback 盲重试，必须靠稳定 action identity / idempotency / reconciliation 收敛。

**Source trace:** PF-032 boundary; `docs/modules/effects/reference.md`.

## Q027
**Answer**
canonical provenance 只把缺陷收敛到 custom MCP 名称“自递归”，没有保留完整 stack/最小输入。可以说这个 bug 有 before/after commit 证据，但更细 call-stack 仍应现场读 diff。

**Source trace:** PF-032.

## Q028
**Answer**
现有证据不能证明历史修复已经推广成通用 alias/route cycle detection；如果面试官追这一层，我应回答 Unknown。设计上可用 canonical name + visited set / bounded hops 做通用防护，但那是建议，不是历史 claim。

**Source trace:** PF-032 limit.

## Q029
**Answer**
PF-032 确认 4/28 修复了高德天气自然句参数抽取，但当前 canonical 摘要没有保留 parser 的逐行 before/after。具体“南京明天天气”怎样错，需要回 commit/test artifact，不能凭印象补。

**Source trace:** PF-032.

## Q030
**Answer**
历史选择理由没有被恢复。一般而言 deterministic extraction 的优势是可预测、低成本和可做精确 regression；LLM parsing 泛化更强但有成本和非确定性。是否因此采用这条路径，仍需要原始 Issue/设计记录才能归因。

**Source trace:** Historical rationale Unknown; general engineering reasoning.

## Q031
**Answer**
这些复杂自然语言例子没有被当前证据覆盖，所以不能声称支持。现有 test artifact 只证明有针对当时缺陷的 regression 资产，不代表自然语言 parser 已成为通用 NLU 层。

**Source trace:** PF-032 limits.

## Q032
**Answer**
provenance 记录了 direct-route、config-gate、structured-result 等 regression test artifact，但没有在文档里冻结每条 assertion。要回答 Tool 名、参数、server、result 的具体断言，需要打开 test。

**Source trace:** PF-032.

## Q033
**Answer**
当前资料只证明 test artifact 存在，不能证明它们是怎样分层的 E2E，也不能证明当时 CI 执行通过。真实 MCP Server / mock 边界需要 test source 或历史 run。

**Source trace:** PF-032.

## Q034
**Answer**
`config gate` 这个 artifact 名称存在，但缺配置时的精确历史行为未被冻结。我不能从名字推断它一定 fail closed 或一定提示用户。

**Source trace:** PF-032.

## Q035
**Answer**
能证明“新增了 regression test artifact”；不能证明当时 CI passed。要升级 claim，需要历史 test run / CI 或可复现实验。

**Source trace:** PF-032 explicit boundary.

## Q036
**Answer**
通用网络语义上，known-not-sent 与可能已发送必须分开；read timeout、connection lost 等通常不能证明远端没执行。Zuno 后续 Target 也明确把 possible-send timeout 记为 Outcome Unknown → Reconcile，但这不证明 4 月历史 Tool path 已实现该机制。

**Source trace:** `docs/modules/effects/reference.md`; PF-032 boundary.

## Q037
**Answer**
客户端只观察本地 socket/response 时序；请求可能已越过网络并在远端提交，只是响应丢失或超时。所以 retry 必须先证明未执行，或依赖远端幂等；否则先 reconcile。

**Source trace:** `docs/modules/effects/reference.md`; general TCP/HTTP semantics.

## Q038
**Answer**
Target 设计会把 idempotency identity 绑定业务 action，而不是 attempt/trace；same key + same action hash 才复用，different hash 应冲突。如果远端无幂等，需要 remote business key/query 或人工 reconciliation，不能声称 exactly-once。历史 4 月实现没有证据证明做了这些。

**Source trace:** `docs/modules/effects/reference.md`; PF-032 boundary.

## Q039
**Answer**
`CancelledError` 只说明本地 coroutine 的取消传播，不能回滚已经离开进程的远端请求；远端可能继续执行。当前 Evidence 也明确 cancel-in-flight orchestration 未证明，所以我不会说 Zuno 已经闭环。

**Source trace:** `docs/evidence/README.md`; general asyncio/network semantics.

## Q040
**Answer**
今天会优先采用成熟 SDK 的连接、schema、tool binding、session 等通用能力。Zuno 值得保留的 Delta 只应是业务 scope、当前安全资格、action identity/effect semantics 等上层 contract；如果平台可靠提供同等语义，绑定 plumbing 应删除。

**Source trace:** `docs/architecture/architecture.md`; `docs/modules/effects/reference.md`.

## Q041
**Answer**
简单 baseline 应先是受控 BM25/Vector/Hybrid retrieval。GraphRAG 只对多跳关系、实体连接等 query class 有潜在价值；Zuno Target 明确把它设成 optional/measurement-gated，而不是所有法律问题默认使用。历史 PF-031 的触发是研发 eval，不等于客户问题已经证明需要 GraphRAG。

**Source trace:** `docs/project/README.md`; PF-026, PF-031.

## Q042
**Answer**
canonical provenance 只写 `HotpotQA limit=5 smoke`，没有在文档里把 `limit=5` 的 runner 参数语义、query 数和 corpus config 冻结下来。这个问题必须回原始 runner/config/raw report；简历虽然保留原词，但 Blue 不能猜它究竟代表 sample limit 还是别的参数。

**Source trace:** PF-031.

## Q043
**Answer**
当前材料不足以证明所有检索配置严格只差 GraphRAG，因此 `1.00→0.80` 只能称 sampled regression observation，不能扩写成 GraphRAG 的独立因果效应。正式 A/B 必须固定 corpus/query/model/index/top-k 等条件。

**Source trace:** PF-031; `docs/evidence/README.md` measurement rules.

## Q044
**Answer**
`Recall@5` 一般表示 top-5 中命中相关 gold 的比例，但 Zuno 这次 provenance 特意写的是 gold-like documents，说明当前材料不足以把它升级成正式 gold-label benchmark。精确 evaluator 定义需要 runner/source。

**Source trace:** PF-031.

## Q045
**Answer**
一般来说 Recall@5 看是否在前 5 找到需要的证据，MRR@10 对首个相关结果的排名位置更敏感。当前文档记录这两个值，但没有冻结 evaluator 的精确定义，所以项目级解释不能超过这个层次。

**Source trace:** PF-031; generic IR metric definitions.

## Q046
**Answer**
`FullChainHit@5` 被记录为 rerun metric，但 canonical provenance 没有冻结“chain”标签构造和计算规则。精确回答需要评测代码/数据集说明；否则会把指标名字当成证据。

**Source trace:** PF-031.

## Q047
**Answer**
能确认两个 sampled case 里 graph-added documents 挤出了 baseline 已命中的 gold-like document；具体 Top-5 文档 ID / score 列表未保存在 canonical prose。机制上说明候选合并和排名缺少 baseline preservation，但现场举精确列表需原始 report。

**Source trace:** PF-031.

## Q048
**Answer**
provenance 证明观察到了“graph-added candidate displacement”，但没有保存完整调试中间件，例如 entity/seed/path/reranker trace。所以我能讲最终判断，不能假装所有排除过程已归档。

**Source trace:** PF-031.

## Q049
**Answer**
能证明实现了名为 baseline-preserving fusion 的改动；具体是 RRF、quota、score normalization 还是其他公式没有在 canonical 文档冻结。这个问题需要代码级 source trace。

**Source trace:** PF-031.

## Q050
**Answer**
这是 baseline-preserving 设计的核心风险：保底不能变成“baseline 永远不可被超过”。现有小样本证据不能证明解决了这个 trade-off；正式 eval 应同时观察 baseline 保持与 graph 新增正确证据的增益。

**Source trace:** PF-031; PF-026 measurement-gated principle.

## Q051
**Answer**
文档证明做了 candidate-aware seed expansion，但没有冻结 seed 算法。不能从名字反推具体 top-N 或 score rule。

**Source trace:** PF-031.

## Q052
**Answer**
top-N、threshold、hop/path budget 的具体值和敏感性分析没有 Current/History evidence。它们正是后续 benchmark/ablation 应补的内容。

**Source trace:** PF-031 future evidence.

## Q053
**Answer**
entity alias normalization 的实现存在，但 canonical provenance 没列出 normalization pipeline。大小写、别名表、fuzzy matching 等只能算候选方案，不能冒充历史实现。

**Source trace:** PF-031.

## Q054
**Answer**
当前没有 false-merge benchmark。设计上必须把 alias resolution 绑定 entity identity/context，并用冲突样本测 precision；目前只能承认风险未证明收敛。

**Source trace:** PF-031 limits; general entity-resolution reasoning.

## Q055
**Answer**
path-aware ranking 已被历史 commit 证实，但 feature/公式/learned-vs-rule 未在 canonical prose 中冻结。需要代码或 frozen eval config 才能进一步回答。

**Source trace:** PF-031.

## Q056
**Answer**
短路径不能天然等于高相关。合理评测要同时看 path semantics、document relevance、coverage 和噪声；现有 evidence 没有证明 path-length bias 已系统处理。

**Source trace:** PF-031; general retrieval reasoning.

## Q057
**Answer**
不能证明四项改动各自都必要。PF-031 明确禁止把最终 rerun 反推成每个 commit 的独立因果贡献；缺少逐项 ablation 是当前证据边界。

**Source trace:** PF-031 explicit limit.

## Q058
**Answer**
没有足够证据排除 overfit。小样本同日修复只能证明这些 sampled failures 被修到不再低于 baseline；需要 holdout/multi-dataset 和冻结配置才能判断泛化。

**Source trace:** PF-031.

## Q059
**Answer**
`fallback_count=1` 被记录，但 canonical provenance 没定义其触发语义，因此不能说它一定代表质量保护或系统失败。后续应把 fallback reason/frequency 纳入 eval。

**Source trace:** PF-031.

## Q060
**Answer**
不能从这一 smoke 外推 Top-K=10。candidate budget 变大可能改变噪声、路径候选和 rerank competition；正式 benchmark 必须覆盖不同 K 或业务实际 K。

**Source trace:** PF-031 future evidence.

## Q061
**Answer**
当前没有 GraphRAG 的稳定 latency/token/cost 数字。应在固定 query set 上同时记录 graph query、retrieval/rerank latency、模型/token 和质量指标，和 Hybrid baseline 做同预算比较。

**Source trace:** PF-022, PF-026; `docs/evidence/README.md`.

## Q062
**Answer**
历史 PF-031 没证明 vector/graph update consistency。Target Architecture 会把知识派生绑定稳定 DocumentVersion / KnowledgeGeneration，使查询能知道自己使用哪版派生视图；这属于后续设计，不应反写为 6 月已实现。

**Source trace:** `docs/architecture/architecture.md`; PF-031 boundary.

## Q063
**Answer**
没有 evidence 证明 PF-031 路径做了 graph poisoning 防护。Target 方向应依赖来源/provenance、scope/security、candidate 与正式证据分离，避免 graph candidate 自动成为业务事实。

**Source trace:** `docs/project/README.md`; `docs/architecture/architecture.md`; PF-031.

## Q064
**Answer**
会删。Zuno 当前设计明确把 GraphRAG 作为 measurement-gated option；如果 Hybrid RAG 在目标 query class 上质量相当而延迟/成本更低，GraphRAG 没有继续默认存在的理由。

**Source trace:** PF-026; `docs/architecture/architecture.md`.

## Q065
**Answer**
我会固定同一 corpus/query/model/预算，对 Hybrid baseline 与 GraphRAG 做 query-class 分层；测 Evidence Sufficiency/Recall、Citation correctness、unsupported claim、full-chain、多跳成功率、latency/cost，并做 fusion/seed/alias/path ablation和 failure review。结果稳定后才决定 default path。

**Source trace:** `docs/evidence/README.md`; `docs/modules/runtime/reference.md` evaluation philosophy; PF-026.

## Q066
**Answer**
设计层面的失效是：recent window/task summary 只能压缩对话，不能提供明确 scope、来源、review 状态和结构化长期事实。历史上是否有某个客户事故直接触发 V2，没有恢复，不能补故事。

**Source trace:** PF-029–PF-030; `docs/project/README.md` context philosophy.

## Q067
**Answer**
provenance 证明 typed Context / Memory contracts 存在，但当前项目事实文档没有冻结完整字段表。我能讲 scope、source/provenance、review state 这些语义；精确 dataclass/schema 字段必须读对应历史代码。

**Source trace:** PF-029–PF-030.

## Q068
**Answer**
canonical provenance 只明确“scoped memory / same-scope readback”，本轮允许来源没有给出完整 scope dimension enum，因此我不会现场背 user/project/thread 等字段当历史事实。需要 contract source 才能精确回答。

**Source trace:** PF-029–PF-030.

## Q069
**Answer**
安全意义上的 scope isolation 应在 durable query/owner boundary enforce，不能只靠 prompt 或 Python 变量。但 PF-029/030 没证明历史实现的最终 enforcement 层，所以项目级答案是 Unknown。

**Source trace:** PF-029–PF-030; `docs/modules/security/reference.md` for Target scope authority.

## Q070
**Answer**
能确认 `GeneralAgent.prepare_context()` 后续读 same-scope task summary 和仅 APPROVED structured memory，并构造带 policy/source-id trace 的 Context Pack。更细的调用栈、函数参数和 prompt composition 没有在 canonical provenance 冻结。

**Source trace:** PF-029.

## Q071
**Answer**
`ContextOrchestrator` 的 minimal callable integration 有历史 commit 证据，但当前 provenance 没冻结其精确接口。它代表把 pre-call context assembly 从 Agent 主循环分离的方向；“删掉后一定怎样”需要代码证明，不能只凭名字推断。

**Source trace:** PF-030.

## Q072
**Answer**
历史资料没有证明 summary 与 structured memory 的冲突优先级和 token budget 算法。PR #8 证明两类 readback 被接入，并不等于 context arbitration 已成熟。

**Source trace:** PF-029.

## Q073
**Answer**
能证明 read path 只消费 APPROVED structured memory；读取后到模型调用前发生状态撤销的 race 是否处理，没有 evidence。这个 gap 不能用“有 review gate”掩盖。

**Source trace:** PF-029.

## Q074
**Answer**
我只能认领 readback hardening、review/provenance contract 和 focused tests，不认领完整 candidate→pending→approved 审核生命周期。简历写“参与”也是为了守住这个边界。

**Source trace:** PF-029 explicit limit.

## Q075
**Answer**
历史 PR #8 没证明 stale memory invalidation 闭环。Target 上正式材料/Domain 事实应拥有 Authority，Memory 只能作为上下文派生；来源版本变化时应失效或重新审核，但这是待实现/验证机制。

**Source trace:** `docs/project/README.md`; `docs/architecture/architecture.md`; PF-029 limit.

## Q076
**Answer**
PR #8 支持 source-id trace 这个 contract，但 granularity 和多来源表达没有在 provenance 冻结。要回答 document/chunk/message 等精确层级，需要历史 schema/test。

**Source trace:** PF-029.

## Q077
**Answer**
现有 Context/Memory历史 evidence 没有证明 prompt-injection isolation。正确边界是把 memory 当数据而不是 instruction，并让高风险动作继续经过独立 Tool/Security gates；但不能把这套 Target 安全模型宣称为 PR #8 已实现。

**Source trace:** PF-029; `docs/modules/security/reference.md`.

## Q078
**Answer**
PF-030 证明早期 V2 有 post-turn scoped raw event / task summary 写入，以及最小 pre-call context integration；PR #8 重点是后续 readback hardening。完整 PostTurnPipeline 并未证明完成。

**Source trace:** PF-029–PF-030.

## Q079
**Answer**
“模型已返回、memory write 前 crash”的恢复没有 implementation evidence。我不会用 Runtime checkpoint 代替 Memory write truth；要闭环需要 turn identity + durable write/idempotency/replay semantics。

**Source trace:** PF-029–PF-030 limits; `docs/modules/runtime/reference.md` owner-first recovery principle.

## Q080
**Answer**
历史 slice 没证明 post-turn idempotency identity。设计上应绑定稳定 turn/event identity，让重放返回已有结果或幂等 append；这是后续实现要求。

**Source trace:** PF-030 limit; general persistence principle.

## Q081
**Answer**
并发 summary 更新策略没有历史证据。若用 PostgreSQL，我会优先 immutable event + versioned summary 或 optimistic version check，而不是无条件 last-write-wins；是否需要 row lock取决于冲突率和事务长度。

**Source trace:** Project-specific behavior Unknown; general DB design.

## Q082
**Answer**
READ COMMITTED 防脏读但可能看到不同快照/产生 lost-update 风险；REPEATABLE READ 提供事务内稳定快照但仍要处理写冲突；SERIALIZABLE 最强但代价更高并可能需要重试。Zuno 历史 Context/Memory 事务边界没有证明，所以这些是原理回答，不是项目 claim。

**Source trace:** general PostgreSQL semantics; PF-029/030 do not establish transaction design.

## Q083
**Answer**
当前证据只到 foundation/readback hardening，不能声称已经有成熟长期 memory retrieval/ranking/consolidation。面试里应该直接把这一点说清楚。

**Source trace:** PF-029 explicit limit.

## Q084
**Answer**
PR 描述确实记录 focused tests `32 passed`，同时还有 repo/legacy tests；但 canonical provenance 没列出这 32 条逐项 assertion。它支持“有 focused validation”这一级，不能自动证明 production Memory DB、真实长期质量或完整审核生命周期。

**Source trace:** PF-029.

## Q085
**Answer**
Zuno 不应为了 Memory 而自己造存储/检索轮子。值得自有的是业务 scope、review eligibility、provenance、与正式业务事实的 Authority 边界；底层 provider 能满足这些 contract 时应复用甚至替换。

**Source trace:** `docs/architecture/architecture.md`; PF-026, PF-029.

## Q086
**Answer**
最短路径是：当前权限检查 → 读取/检索必要材料 → 生成带来源的回答 → 返回。没有长任务、正式结果、外部写操作时，不需要 Native Runtime、Multi-Agent 或复杂 Effect recovery。

**Source trace:** `docs/project/README.md`; `docs/architecture/architecture.md`.

## Q087
**Answer**
材料持续变化迫使稳定版本/来源；机器结论可能错迫使候选与正式结果分离；长任务等待/重启迫使 Runtime control；授权会变化迫使持续授权；外部 POST timeout 可能已执行迫使 Effect/reconcile。每一层都来自一个不同的 failure condition，而不是为了模块数完整。

**Source trace:** `docs/project/README.md`; `docs/architecture/architecture.md`.

## Q088
**Answer**
Target 让候选归 Knowledge/Capability，正式 Evidence/Finding/WorkProduct 由 Domain Owner 在 formal admission 中产生，并用 durable version/receipt 证明。单表 `status` 不是绝对不行，但如果任何调用者都能改它，就无法表达 authority、事务边界、幂等和恢复锚点；重点是 owner/contract，不是表数量。

**Source trace:** `docs/modules/domain/reference.md`.

## Q089
**Answer**
正式新 DocumentVersion/Evidence 进入后，通过依赖关系定位受影响 Finding/WorkProduct，标记 review-required/stale，保留旧版本并产生新版本，而不是覆盖历史。如果依赖图不足，扩大人工复核范围。

**Source trace:** `docs/modules/domain/reference.md` WorkProductInvalidationFact / lifecycle.

## Q090
**Answer**
Checkpoint 只证明 Runtime 控制进度。典型窗口是 Domain commit + AdmissionReceipt 已成功，但 Runtime checkpoint 写失败；重启后必须查 Domain receipt 修 Runtime，而不是重复正式提交。反方向则是 checkpoint 看似完成但 receipt 缺失，正式完成必须拒绝。

**Source trace:** `docs/modules/runtime/reference.md`; `docs/modules/domain/reference.md`.

## Q091
**Answer**
Target 流程是先 canonicalize action，形成 action identity/hash + idempotency，危险 send 前持久化 Attempt；可能已发送却没有确定响应时进入 OUTCOME_UNKNOWN，优先 remote query/business key reconcile，确认未执行才安全 retry；补偿本身是新的受控动作。当前 evidence 仍没有完整 reconciliation convergence。

**Source trace:** `docs/modules/effects/reference.md`; `docs/evidence/README.md`.

## Q092
**Answer**
新受保护读取、模型外发、Secret、Tool Effect、Formal Admission，以及 resume/retry/replan 后的新动作都要消费当前安全事实。入口 allow 只能证明当时允许，不能覆盖等待期间的 policy/security epoch 变化。

**Source trace:** `docs/modules/security/reference.md`; `docs/modules/runtime/reference.md`.

## Q093
**Answer**
Session、Tool binding、checkpointer、sandbox、通用 tracing 等优先 Adopt；法律 Task/Capability、材料 provenance、Domain admission、Effect semantics、安全 contract 更可能 Extend/Build 薄业务层；Native Runtime 在 Generic Host 已足够时 Defer。决定因素是平台是否能承载所需业务 authority/recovery contract，而不是品牌。

**Source trace:** `docs/architecture/architecture.md`; PF-024–PF-026.

## Q094
**Answer**
Multi-Agent 只在可独立拆分、并行研究且收益能覆盖 token/协调/失败成本时有意义。强共享上下文任务优先单 Agent + parallel tools；正式 eval 没有收益就删。

**Source trace:** `docs/project/README.md`; PF-026.

## Q095
**Answer**
GraphRAG 要对简单 retrieval baseline 测检索/引用质量 + latency/cost；Memory 要对 recent-window/summary baseline 测任务质量、污染/泄漏、token/cost；Multi-Agent 对单 Agent + parallel tools 测质量/成本/失败率；Native Runtime 对 Generic Host + legal backend 做 recovery correctness/latency/cost A/B/C。当前这些正式对照还没有建立。

**Source trace:** `docs/evidence/README.md`; PF-025–PF-028.

## Q096
**Answer**
默认可以是模块化 Python 后端 + 少量 Worker。只有吞吐、安全隔离、网络出口、故障半径或独立发布节奏形成真实约束时再拆网络服务；逻辑 Owner 不等于微服务。

**Source trace:** `docs/architecture/architecture.md`.

## Q097
**Answer**
即使共库共进程，也要把写权限收在 owner module/repository/service port 里，跨边界只消费 typed refs/contracts；禁止任意模块直接把别人的表当共享结构改。事务由 authoritative owner 定义，而不是靠 Python package 名称假装边界。

**Source trace:** `docs/modules/domain/reference.md`; `docs/modules/runtime/reference.md`; architecture owner model.

## Q098
**Answer**
Target Trace 至少要串 run/plan/step、Knowledge generation/evidence refs、CapabilityVersion、ModelAttempt、Tool action/attempt/effect、SecurityEpoch/decision、AdmissionReceipt、Budget/Usage 和 RunOutcome。Trace 只是关联这些 owner facts，不能替代它们。

**Source trace:** `docs/modules/runtime/reference.md` B12; `docs/modules/effects/reference.md`; `docs/modules/security/reference.md`.

## Q099
**Answer**
已恢复实现/测试：4 月 Tool/MCP strategy 与 route hardening、6 月 GraphRAG 修改 + 小样本 rerun、6 月 Context/Memory V2 + PR #8 focused validation。后续九责任域、Formal Admission、完整 Effect recovery、持续安全等主要是 Target design；质量/生产优势未证明。最危险的混淆是把“后续设计完整”讲成“历史 Pilot 已经实现且验证”。

**Source trace:** PF-023–PF-032; `docs/evidence/README.md`.

## Q100
**Answer**
我会保留三类 Zuno-specific contract：材料/证据的稳定版本与 provenance；机器候选到人审正式 WorkProduct 的 Domain admission/历史版本；现实副作用的 action identity + unknown/reconcile（安全决定同样保持独立 authority）。我会优先删除或外包通用 Agent harness、默认 Multi-Agent、无收益的 GraphRAG/Memory/Native Runtime plumbing；复杂度只有通过业务任务测量才回来。

**Source trace:** `docs/project/README.md`; `docs/architecture/architecture.md`; `docs/modules/domain/reference.md`; `docs/modules/effects/reference.md`.

## Blue self-boundary summary

本轮最明显的可面试断点不是“架构逻辑说不通”，而是历史实现的细粒度 evidence 不均衡：PF-029–PF-032 已能支撑具体 commit-level story，但 Tool matcher、MCP config isolation、GraphRAG 公式/参数、Context contract 字段、review 人员和真实运行数据等没有冻结到 canonical documentation。Blue 对这些问题保持 Unknown，没有用后续 Target 或通用知识反写历史。
