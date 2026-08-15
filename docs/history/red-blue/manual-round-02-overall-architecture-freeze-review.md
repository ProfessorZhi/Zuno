series: ARCHITECTURE_INTERVIEW
round_id: 02
round_name: Overall Architecture Freeze Review
execution_mode: MANUAL
status: ARCHIVED
architecture_baseline_sha: a9fa3834c1dd95bdc13caa85b7188d49fc55b1b5
archive_task_base_sha: b287d6c3d2c9f5051d37e6d66e29f61633126a3c
qar_complete_through: Q38
follow_up_status: COMPLETE
red_findings_status: FINAL
qar_packet_complete: YES
main_judgment: COMPLETED
main_judgment_outcome: ACCEPTED_WITH_REQUIRED_ARCHITECTURE_REVISION
architecture_revision: COMPLETED
overall_architecture_freeze: YES
module_decomposition_gate: OPEN
architecture_revision_sha: 7ce987f5d747395d4926622f42ac4f0013bc53ed
canonical_revision_gate: PASS
source_boundary: manually coordinated Red / Blue / Main workflow

---

> This file is an append-only historical Red / Blue Q/A/R archive. Q1–Q38 preserve the supplied source, including the completed follow-up round.
> It is not a Current Fact, Canonical Target Architecture, ADR, or implementation authorization. Main Judgment remains pending post-archive discussion.

---

# Zuno Architecture Interview — Round 02 Formal Q/A/R Packet

```yaml
series: ARCHITECTURE_INTERVIEW
round_id: 02
round_name: Overall Architecture Freeze Review
execution_mode: MANUAL
status: ARCHIVED
architecture_baseline_sha: a9fa3834c1dd95bdc13caa85b7188d49fc55b1b5
archive_task_base_sha: b287d6c3d2c9f5051d37e6d66e29f61633126a3c
qar_complete_through: Q38
follow_up_status: COMPLETE
red_findings_status: FINAL
qar_packet_complete: YES
main_judgment: COMPLETED
main_judgment_outcome: ACCEPTED_WITH_REQUIRED_ARCHITECTURE_REVISION
architecture_revision: COMPLETED
overall_architecture_freeze: YES
module_decomposition_gate: OPEN
architecture_revision_sha: 7ce987f5d747395d4926622f42ac4f0013bc53ed
canonical_revision_gate: PASS
```

> Source note: This packet preserves the Round 02 material in strict Q/A/R order. Q33–Q38 and the Red Final Findings were supplied as the completed follow-up source packet.

---

## Q1 — Red Question

先从最简单的一条链开始。

用户只问：“这份合同第 8 条的违约责任是什么？把原文和出处给我。”

当前 FLOW A 是：

Question → Scope → Authorization → Knowledge Readiness → Retrieval → Citation → Final Gate → Response

这里看起来根本不需要复杂 Agent Runtime；但同一份 Architecture 又说任何任务都不能绕过 Plan、Trace、Budget、AnswerPolicy 和 RunOutcome。

那这条请求到底有没有 AgentRun、PlanVersion 和 Runtime Checkpoint？

如果没有，Final Gate、Answer Proposal 和这次执行结果究竟由谁拥有；如果有，那我为什么不能直接用普通 RAG Host 做完这件事？

## A1 — Blue Answer

这条请求我会直接允许普通 RAG Host 做，不需要为了统一形式强行启动完整 LangGraph Runtime。

如果它进入 Zuno Runtime，可以有一个很薄的 AgentRun + deterministic single-step Plan，但不等于必须创建有恢复价值的 Runtime Checkpoint。Plan、Budget、Trace、AnswerPolicy、Outcome 是执行约束，不应该反过来变成“必须自研 Runtime”的理由。

所以我会把“任何任务不能绕过”收窄为“进入 Zuno Agent Runtime 的任务不能绕过”。Simple QA 如果 Host 已经能满足这些约束，就复用 Host。

另外这里确实有一个 Freeze Gap：当前 Ownership Matrix 没把 AnswerProposal 和 Simple QA 的 FinalGate 唯一 Owner 写清。我不会假装这已经解决。Formal WorkProduct 的资格判断可以归 Domain Admission，但普通聊天答案不能硬塞给 Domain。

## R1 — Red Review

**Status:** ARCHITECTURE_CONCERN

这个回答方向我认可，但它实际上修改了当前总体原则。

Blue 现在说的是：

> 只有进入 Zuno Agent Runtime 的任务才必须经过 Zuno 的 Plan / Budget / AnswerPolicy / RunOutcome；Simple QA 可以完全由 Generic Host 完成。

这比当前“任何任务不能绕过”的表述更合理，但它意味着 FLOW A 不再天然属于 04 Runtime，甚至可能没有 Zuno AgentRun。

这不是 Runtime Module 内部细节，而是产品入口和执行边界发生了变化。Freeze 前必须承认 Host-owned Simple QA 是一条正式合法路径，而不是把所有请求都伪装成 AgentRun。

**Freeze Impact:** ARCHITECTURE_REVISION_REQUIRED

**Follow-up:** Q33

---

## Q2 — Red Question

沿着这条 Simple QA 继续。

Retrieval 时绑定的是 KnowledgeGeneration=41，引用也已经生成；就在 Final Gate 前，后台重新解析了一份材料，Knowledge View 变成了 Generation 42，而且旧 Chunk 的位置发生了变化。

这个答案还能发吗？

谁发现 Generation 变了？是重新检索、重新做 Citation Validation，还是直接 Reject？

我尤其想知道：Answer 本身和 Final Gate 到底是谁的责任，因为当前 Ownership Matrix 对 Knowledge、Runtime、Domain 都写得很细，但这两个东西我还没有看到一个让我完全放心的唯一 Owner。

## A2 — Blue Answer

Generation 变成 42 不代表 41 立刻无效。这个 Run 已经绑定 41，首先要问的是 41 还能不能作为不可变 Snapshot 被验证。

如果 DocumentVersion 没变、41 仍可读取，而且引用最终锚定的是原始 DocumentVersion 的 Source Span，而不是脆弱的 Chunk ID，我会重新做 Citation Validation，但不必重新检索。

如果 41 已被判定 STALE、无法重现，或者 Final Policy 要求必须使用最新 Generation，那就不能把 41 的答案直接发出去，要在 42 上重新检索并重新生成引用。

Generation 是否仍有效由 Knowledge 判断；Final Gate 消费这个判断。至于 Simple Answer 和 Final Gate 的唯一 Owner，我同意目前还没冻结清楚，这是边界缺口，不应该靠“大家都检查一下”糊过去。

## R2 — Red Review

**Status:** OPEN

Blue 正确识别了 Generation 41 与 42 的问题，也正确指出 Snapshot 是否继续有效应该由 Knowledge 判断。

但真正关键的问题没有解决：

> Simple Answer Proposal 和 Simple Final Gate 到底是谁拥有？

Blue 两次明确说“目前还没冻结清楚”。

这是标准的 Overall Architecture Ownership Gap，不允许推到后面的模块设计。

尤其当 FLOW A 可以完全绕开 Zuno Runtime 后，更不能再默认由 Controller 拥有 Final Gate。

这题没有关闭。

**Freeze Impact:** FREEZE_BLOCKER

**Follow-up:** Q33

---

## Q3 — Red Question

现在跑 FLOW B。

一个案件有起诉状、答辩状和两份证据材料。系统抽取出两个 Event，发现双方对付款时间的陈述冲突，检索到相关法条，最后形成一个 Finding，交给法官助理修改后生成 WorkProduct。

你不要讲模块名字，按这条实际链路告诉我：

DocumentVersion → EvidenceCandidate → Event → Conflict → Finding → HumanDecision → WorkProduct

每一步谁可以创建候选，谁可以修改，谁可以提交正式版本？

我只接受一个最终事实 Owner。两个地方都可以说“这个对象归我”就算这题没过。

## A3 — Blue Answer

DocumentVersion 是正式业务材料版本，解析器可以处理它，但不能改它的业务身份；正式版本只能由业务状态 Owner 提交。

EvidenceCandidate 是检索产生的候选，检索侧可以创建和替换，它不是正式 Evidence。

Event 和 Conflict 在当前最小设计里我不会默认 Canonical。抽取模型、算法或者 Specialist 只能产生 Proposal，可以重新计算、覆盖或废弃。

Finding 也是先产生 Proposal，只有经过证据、权限、质量和必要人工审核后，业务状态 Owner 才能提交正式 FindingVersion。

HumanDecision 只能来自被授权的人类决定，系统负责记录，模型不能修改已经提交的决定。

WorkProduct 可以由模型起草、法官助理修改，但正式版本仍然只有业务状态 Owner 提交。

所以最终 Canonical Fact 只有一个 Owner；Knowledge 和模型只有 Candidate / Proposal 权限。

## R3 — Red Review

**Status:** CLOSED

这个回答是清楚的。

它把：

- DocumentVersion：Canonical；
- EvidenceCandidate：Knowledge candidate；
- Event / Conflict：默认 Proposal；
- Finding：Proposal → Admission → Canonical FindingVersion；
- HumanDecision：人类授权决定；
- WorkProduct：可起草、可人工修改，但 Canonical Version 只有 Domain Owner 能提交；

分开了。

这里没有出现两个模块同时声称拥有 Canonical State。

关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q4 — Red Question

这里我看到一个明显需要你解释的地方。

ADR-0008 冻结的最小 Canonical Kernel 是 Matter / DocumentVersion / Claim / Evidence / Finding / HumanDecision / WorkProduct；它明确说 Fact / Event / Conflict / Dispute / LegalIssue 默认可以只是 Proposal、Projection 或 Derived View。

但当前 Overall Architecture 的 Domain State 和 Owner Matrix 又直接把 Fact / Event / Conflict / Dispute 放进了 Domain State。

所以现在到底是哪一个？

比如 Event Extraction 返回一个 Event Proposal，什么条件下它升级成 Canonical Event？还是实际上根本没有 Canonical Event 这个概念？

如果这件事今天都没确定，我为什么应该同意 Freeze Domain 边界？

## A4 — Blue Answer

这里我认为确实存在不一致，而且我不会替它辩护。

当前最小边界应该以更窄的规则为准：Event、Conflict、Dispute 默认不是 Canonical State。 Event Extraction 返回的是 Event Proposal，没有一个自动“升级成 Canonical Event”的步骤。

真要增加 Canonical Event，至少要先证明它有独立 Identity、Version、Provenance、Mutation Authority、Dependency、Staleness、Review 和 Audit 生命周期，然后明确 Admission Contract；不能因为流程图里画了 Event 就获得正式状态资格。

所以按现在这两个表述，我不会同意 Domain 边界已经达到 Freeze。总体架构里把这些对象直接列成 Domain State 的文字需要先收敛。ADR-0008 本身明确采用的是最小 Kernel。

## R4 — Red Review

**Status:** ARCHITECTURE_CONCERN

这个回答我认可，而且 Blue 没有替现有文档硬圆。

问题也因此被确认了：

ADR-0008 的最小 Kernel 和当前 architecture.md 的 Domain State 描述并不一致。

ADR-0008 明确把 Event / Conflict / Dispute 等保持为 Proposal / Derived View 候选，而当前 Architecture 又把它们直接列入 Domain State。

这不是措辞小问题。

它影响：

Canonical Object Set；

Admission；

Version；

Staleness；

Dependency；

Ownership；

Persistence。

Freeze 前必须收敛。

**Freeze Impact:** FREEZE_BLOCKER

**Follow-up:** NONE

---

## Q5 — Red Question

再看 Evidence 和 Citation。

Knowledge 拥有 EvidenceCandidate 和 CitationLineage，Domain 又拥有正式 Evidence business reference，最终 WorkProduct 也必须带引用。

假设 Knowledge Index 被完全重建了，Chunk ID 全变，但是原始 DocumentVersion 没变。

昨天已经提交的 WorkProduct 引用还能不能稳定打开原文？

Domain 是复制 Citation，还是只保存对 Knowledge CitationLineage 的引用？

如果 Knowledge 可以重建，我要知道哪一层的信息必须永远足以恢复历史引用，否则这里很容易形成双主或者悬空引用。

## A5 — Blue Answer

历史 WorkProduct 的引用不能依赖 Chunk ID。Chunk、Vector Index、Graph Projection 都是可重建投影。

真正稳定的引用至少要落到：

DocumentVersion + immutable source object/hash + SourceSpan + span hash

页码、段落、字符区间之类可以作为定位信息，Chunk ID 最多是检索辅助信息。

Knowledge 仍然拥有 CitationLineage；Domain 不应该复制出第二套“Citation 真相”。但 WorkProductVersion 必须固化一个不可变的 Citation Binding/Snapshot，至少能从它回到 DocumentVersion 和原始 Span。这样 Knowledge Index 全删重建也不影响历史引用。

如果当前实现只持有一个可能随 Index 重建消失的 CitationLineage ID，那我认为还不满足历史可审计要求。

## R5 — Red Review

**Status:** PARTIAL

“历史引用绝不能依赖 Chunk ID”这一点回答得很好。

DocumentVersion + immutable source object/hash + SourceSpan + span hash 也是合理的稳定锚点。

但这里又出现了一个新的边界对象：

> WorkProductVersion 固化一个 immutable Citation Binding / Snapshot。

问题是这个 Binding 到底是谁的 Canonical Artifact？

Blue 一边说 Domain 不复制 Citation 真相，一边又说 WorkProduct 必须固化一个独立 Snapshot。

这并非矛盾，但目前 Ownership 还没说到底。

如果 Knowledge 被完全重建甚至 Provider 被替换，Domain 是否单独拥有足够恢复历史 Citation 的不可变 Binding，是 Freeze 级问题。

**Freeze Impact:** ARCHITECTURE_REVISION_REQUIRED

**Follow-up:** Q34

---

## Q6 — Red Question

现在攻击 Ingestion + Retrieval 合并。

一份 5GB 案卷上传后：

OCR 已完成 99%，一页失败； BM25 已 Ready； Vector 已 Ready； Graph Projection 还停在旧版本。

这时一个简单关键词 QA 来了，另一个跨文档争议焦点分析也来了。

对这两个任务，Knowledge 到底分别算 READY、PARTIAL 还是 STALE？

如果 Readiness 本来就必须根据 Query Class、Scope 和 Projection 类型分别判断，那么 Parse/OCR/Index 这条异步数据流水线和在线 Retrieval 为什么仍然构成一个稳定的逻辑模块，而不只是暂时放在一起？

## A6 — Blue Answer

Readiness 不能只看“这个知识库完成了百分之几”，要带 Query Class 和 Declared Scope。

如果关键词 QA 的 Scope 明确只覆盖已经 OCR 成功的材料，而且它只要求 lexical/vector，那么可以是 READY；如果声明的是整份 5GB 案卷，那缺一页也应该是 PARTIAL，不能假装全量覆盖。

跨文档争议分析如果明确依赖当前 Graph Projection，而 Graph 还是旧版本，就是 STALE；如果 Graph 只是优化项，系统也可以走 BM25 + Vector + Alignment，但必须记录 Degradation，不能自动获得 Full-Scope Formal Result 资格。

Ingestion 和 Retrieval 能放在一个逻辑边界，真正的理由不是“它们都跟知识库有关”，而是同一个 Owner 必须回答：某个 DocumentVersion 到底被发布成了哪个可查询 Generation，以及这个 Generation 对什么 Scope 是 Ready。 OCR、Embedding、Graph Build 完全可以是不同 Worker。

## R6 — Red Review

**Status:** CLOSED

这题 Blue 给出了足够强的逻辑模块理由。

它没有说“OCR 和 Retrieval 技术相似”，而是把共同边界放在：

> DocumentVersion → KnowledgeGeneration → Scope-sensitive Readiness → Query

也就是说：

异步 OCR、Embedding、Graph Build 可以是完全不同 Worker，但它们共同形成一个由 Knowledge Owner 发布和解释的可查询 Projection。

这个理由足以让 Ingestion + Retrieval 继续作为一个 Logical Module Candidate 经受本轮攻击。

物理拆分以后再谈。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q7 — Red Question

进入 FLOW C。

Zuno 向法院外围系统执行一个 POST，外部系统实际上已经成功创建记录，但响应返回之前网络断了。

一分钟后 Worker 重启，同一个 Step 被 Queue redelivery。

现在本地只有：

PreparedAction、idempotency_key、旧 Checkpoint，没有成功 EffectReceipt。

谁第一步去查什么？

什么时候允许 Retry，什么时候绝对不能 Retry？

如果这个外部 Provider 根本没有状态查询 API，也不支持幂等键，这条 Runtime 最后怎么结束？

## A7 — Blue Answer

第一步不是重新 POST，而是先看 Tool Attempt / Idempotency Claim 的持久状态，再去外部系统按 Provider Operation ID、幂等键或者目标资源查询实际结果。

只有确认 NOT_DISPATCHED，或者确认外部没有发生操作，才允许 Retry。

如果查到已经创建成功，就补 Effect Reconciliation / Receipt，再修本地状态。

如果外部结果无法确认，就保持 outcome_unknown，绝对不能因为 HTTP Timeout 就 Retry。

最麻烦的就是 Provider 既不能查询、又不支持幂等。这种情况下系统没有技术手段证明现实世界状态，只能停止自动执行，进入 Human Review / Manual Reconciliation。RunOutcome 应明确表示有未解决 External Effect，而不是伪造成 FAILED 或 SUCCESS。

## R7 — Red Review

**Status:** CLOSED

回答成立。

关键顺序正确：

不要 POST → 先查 Attempt / Claim → Reconcile External Reality → 再决定 Retry

并且 Provider 无查询、无幂等时明确停止自动化，进入 Manual Reconciliation，而不是编一个“失败”。

这是正确的 Unknown External Effect 语义。

关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q8 — Red Question

还是这个 Tool，但这次没有立刻执行。

用户批准了一个 PreparedAction，然后它在审批队列里等了十分钟。

这十分钟内发生两件事中的任意一件：

工具 Schema 从 V3 升成 V4； 或者用户对这个资源的权限被撤销。

旧 Approval 还有效吗？

谁负责宣布这个 PreparedAction 已经不能执行？

如果重新解析参数产生了新的 Action，这是不是必须重新审批，而不是 Runtime 自己把旧 Approval 搬过去继续用？

## A8 — Blue Answer

旧 Approval 不能直接继续用。

Approval 应该绑定具体的 Tool Definition Version、参数 Hash、目标资源、Policy Snapshot、Security Epoch 和有效期。Schema V3→V4 或权限撤销，至少有一个绑定条件已经变了。

权限变化由 Security 给出新的 Authorization 结果；Tool Runtime 在执行前重新解析当前 Tool Definition，发现旧 PreparedAction 不兼容后把它变成不可执行/obsolete。

如果 V4 需要重新 canonicalize 参数，那得到的是新的 PreparedAction。新的参数 Hash 就意味着新的审批对象，必须重新审批，Runtime 不能把旧 Approval 平移过去。当前共享 Contract 本身也是按这个原则绑定 Approval 的。

## R8 — Red Review

**Status:** CLOSED

回答清楚。

Approval 不是“批准过这个 Tool 名字”就永久有效，而应绑定具体 Action / parameters / resource / authorization context。

Schema 或 Security 条件变化以后原 PreparedAction 失效，新参数形成新的审批对象。

这里 Retry、Replan、Approval 和 Security 没有混在一起。

关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q9 — Red Question

现在看 Agent Portfolio。

一个 AgentVersion 里面配置：

Prompt、Model Role、Capability Set、Permission、Memory Policy、Knowledge Scope。

问题是这些东西的真实 Owner 分别落在 Product、Model Gateway、Capability、Security、Memory、Knowledge。

那 Product 所谓“拥有 Agent Definition / Version / Configuration”，到底是在拥有这些配置本身，还是只拥有一份不可变引用集合？

AgentVersion 发布以后，Capability V4 被禁用，或者权限策略变化了。

AgentVersion 本身还是原来的 Version，但它还能不能 Invocation？

谁做最终兼容性判断？

## A9 — Blue Answer

我会把 AgentVersion 理解成不可变的组合清单和约束，而不是把其他模块的事实复制一份过来。

比如它可以说“需要 Capability X@兼容范围、需要某 Model Role、使用某 Knowledge Scope 和 Memory Policy”，但 Capability 当前是否 Available、用户现在是否有权限，仍由各自的权威 Owner 判断。

所以 AgentVersion 发布后本身不变，但 published != currently invocable。

Invocation 前必须重新做 compatibility resolution：Capability 是否可用、当前权限是否允许、模型角色是否还有合法路由、Knowledge Scope 是否 Ready。最终可以由 Invocation Boundary 汇总成一个 InvocationEligibility，但它只是组合判断，不能篡改 Security 或 Capability 的原始事实。

这个最终 Eligibility 目前在 Ownership Matrix 里也没有单独冻得很清楚，我认为要补。

## R9 — Red Review

**Status:** PARTIAL

Blue 对 AgentVersion 的定义比当前 Candidate Module 更干净：

> AgentVersion 是不可变的组合要求 / reference set，不复制 Capability、Security、Model、Knowledge 的事实。

这个我认可。

但是它随后自己承认：

> InvocationEligibility 的唯一 Owner 没冻结。

这是重要的。

因为：

Published AgentVersion != Currently Invocable AgentVersion

谁把多个 Owner 的事实组合成最终 Invocation Decision，决定 01 Product 到底只是 Catalog，还是拥有真正的 Agent lifecycle control。

仍需追问。

**Freeze Impact:** ARCHITECTURE_REVISION_REQUIRED

**Follow-up:** Q33

---

## Q10 — Red Question

再制造 Embedded Mode。

法院已经有自己的 Host，Session、用户登录、前端、审批页面和对话历史全部由现有系统负责；它只通过 API 调 Zuno 的法律能力。

这时候 Product Surface & Agent Portfolio 还有多少东西真正属于 Zuno？

Session 谁拥有？Identity 如何映射？Human Review 是在法院 Host 做，还是 Zuno 做？

如果 Native Mode 和 Embedded Mode 下这个候选模块的形态差别这么大，我想知道它到底是一个稳定 Module，还是一组 Host Adapter / Product Integration Responsibility。

## A10 — Blue Answer

Embedded Mode 下这个模块会明显缩水。

Session、Conversation History、登录态和 UI 都可以由法院 Host 拥有。Zuno 只接收一个经过认证的外部 Principal Context，再映射到自己的 Tenant/Matter/Resource Scope，由 Zuno 的 Security 做最终资源授权，不能信任前端传来的 allowed=true。

Human Review 的页面完全可以在法院 Host；但如果这个 Review 决定会改变 Zuno 保存的正式 Finding 或 WorkProduct，Zuno 必须接收一个可验证的 HumanDecision/Approval Contract 后再提交业务版本。

所以我不会把完整 Product Surface 当成不可替换核心。稳定的是 Host/API Integration Contract；Native Workbench、Session UI、甚至部分 Agent Portfolio 都是可选产品形态。如果 Embedded 是主要模式，01 更像 Integration Responsibility，而不一定值得独立 Module。

## R10 — Red Review

**Status:** ARCHITECTURE_CONCERN

这题是本轮第一个明显的 Module Map Blocker。

Blue 最后的判断实际上是：

> Embedded Mode 下，稳定的是 Host / API Integration Contract；Native Workbench、Session、UI、甚至部分 Agent Portfolio 都是可选的。01 可能只是 Integration Responsibility，不一定值得独立 Module。

这不是 01 内部怎么实现的问题。

这是：

> 01 到底是不是 Module？

当前 Freeze 的目标恰恰就是回答这个问题。

所以 01 目前没有经受住 Freeze Test。

**Freeze Impact:** FREEZE_BLOCKER

**Follow-up:** NONE

---

## Q11 — Red Question

回到 Legal Domain & Work Product。

现在它同时有 Matter、DocumentVersion、Evidence、Fact、Event、Conflict、Dispute、LegalIssue、Finding、HumanDecision、WorkProduct、Admission、Staleness、Supersede。

为什么这些东西应该由一个逻辑模块拥有？

给我一个能长期成立的业务不变量，而不是“它们都是法律相关”。

尤其是 Domain Admission：如果所有 Capability Proposal、Evidence、Quality、Security、Human Review 最后都要经过这里，它怎么避免逐渐变成一个“什么都能否决、什么都要知道”的 God Module？

## A11 — Blue Answer

能长期成立的不变量只有一个：

正式业务世界的版本变化只能由一个 Owner 提交，而且任何正式结论都必须能说明它依赖哪个材料版本、经过什么授权和 Review，以及何时失效。

这也是为什么我不会把 Event、Conflict、Dispute 全部默认做成 Canonical State。第一版 Domain 应该尽量窄。

Domain Admission 也不应该重新做 Retrieval、Security、Eval 或模型判断。它只消费这些 Owner 已经给出的 typed decision/reference，然后检查 Domain 自己的不变量，例如 expected version、dependency、required review、supersede 关系。

如果 Admission 开始自己判断“这个模型够不够好”“这个用户有没有权限”“Graph 是否 Ready”，它就已经变成 God Module 了。

## R11 — Red Review

**Status:** CLOSED

这个回答很好。

它给 Domain 的不变量不是“这些都是法律对象”，而是：

> Canonical Business State 只有一个提交权威，并维护 Version、Dependency、Review、Staleness。

同时 Domain Admission 消费 Security / Eval / Knowledge 等 Owner 的决定，而不是重新实现这些判断。

这足以防止把 Admission 设计成 God Module。

前提仍然是 Q4 的 Canonical Object Set 先收敛。

这一题本身关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q12 — Red Question

现在攻击 Capability / Skill & Tool Runtime。

同样是 Provider Timeout：

一个 Event Extraction Provider 超时，它没有产生外部副作用；

另一个 Tool Provider 超时，但外部转账或者通知可能已经执行。

前一个大概率是在判断“这个能力有没有得到结果”；后一个是在判断“现实世界到底发生没发生”。

这两类 Failure、Retry 和 Recovery 语义完全不同。

所以它们现在为什么应该是一个 Module？

除了 Catalog、Discovery、Version、Invocation 这些公共表面之外，它们到底共享了什么值得共同拥有的稳定状态？

如果回答只是“现在先少一个模块”，我不会接受。

## A12 — Blue Answer

按 Freeze Test 来看，我认为这两者不应该因为共享 Provider Catalog 就强行冻结成一个逻辑模块。

Capability 的稳定状态主要是 CapabilityVersion、Provider Conformance、Evaluation、Availability 和 Proposal。

有副作用 Tool 的稳定状态则是 PreparedAction、Approval Binding、ToolAttempt、Idempotency、EffectReceipt、Outcome Unknown 和 Reconciliation。

它们甚至连“成功”的定义都不同：Extraction 超时通常只是没拿到结果；外部 POST 超时可能已经改变现实世界。

所以 Catalog / Resolution / Invocation Envelope 可以共用一个库或 Provider Framework，但这不足以证明共享一个状态与恢复边界。当前设计自己也承认“模块合并、语义分离”；如果现在要真正 Freeze，我倾向于把 Capability Governance 和 External Effect Runtime 拆开。

## R12 — Red Review

**Status:** ARCHITECTURE_CONCERN

这是第二个明确的 Module Map Blocker。

Blue 基本接受了 Red 的攻击：

Capability Governance 与 External Effect Runtime：

State 不同；

Success semantics 不同；

Failure 不同；

Retry 不同；

Recovery 不同；

Security 风险不同。

它们只共享 Catalog / Resolution / Invocation Framework，不足以证明是同一个 cohesive Logical Module。

这正好击中了当前 Architecture 自己写的：

> “模块合并，语义仍分离”。

如果语义、状态机和恢复边界都分离，Blue 就必须解释为什么还能算同一个模块；本轮没有得到这样的理由。

05 当前边界没有通过 Freeze。

**Freeze Impact:** FREEZE_BLOCKER

**Follow-up:** NONE

---

## Q13 — Red Question

看 Budget。

一个 Run 总预算 100k tokens，Controller 一次派出四个并行 Branch。

Architecture 一方面把 Budget 放在 Agent Runtime，另一方面 Model Gateway 又负责 Budget / Quota / Token / Cost 和 Usage Receipt。

那谁是钱真正花到哪一步的权威？

Runtime 是做业务预算预留，Model Gateway 是做 Provider Quota 和实际 Usage Settlement，对吗？如果不是，请给我另一条清晰边界。

再假设 Provider 两小时后补来一张 Usage Correction，把一个 Branch 的实际费用翻倍。

Run Budget 怎么修正？已经完成的其他 Branch 会不会因此变成“事后超预算”？

## A13 — Blue Answer

我会按你说的这个边界分。

Runtime 拥有的是 Run Budget Ledger：这个任务最多允许花多少、每个 Branch 预留多少、还能不能继续派任务。

Model Gateway 拥有的是 Provider 侧的 Quota、Model Attempt 和实际 Usage/Cost Receipt。Runtime 消费 Usage Receipt 做结算，但不能自己发明 Provider 实际用了多少 Token。

Correction 应该追加新的 Usage Receipt，并 supersede 原结算，不覆盖历史。共享 Contract 也是这么定义的。

如果 Run 还在执行，Correction 导致余额不足，就阻止新的预算预留并尽可能取消未开始任务。

如果 Run 两小时前已经结束，我会把它记录为 actual over budget / settlement correction，而不会把已经完成的 Branch  retroactively 变成“当时非法执行”。预算控制失败和事后账单修正要分开。

## R13 — Red Review

**Status:** CLOSED

Budget 双主问题回答清楚了。

Runtime：Run Budget / reservation / scheduling authority；

Model Gateway：Provider quota、attempt、actual usage/cost receipt；

Runtime 消费 Usage Receipt，而不是重新计算 Provider 事实。

Correction 作为追加 settlement，而不是篡改历史执行合法性，这个语义也合理。

关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q14 — Red Question

Model Gateway 还有另一个边界问题。

它写着负责 Egress Policy，Security 又明确拥有 Model Egress 和 Authorization。

假设当前模型挂了，Gateway 想 fallback 到另一个境外 Provider，但这个 Matter 的数据策略不允许出境。

到底是谁做 Decision，谁做 Enforcement？

再往前一步：Fallback 模型虽然合规，但能力明显更弱，不再满足这个 Step 原先的质量假设。

这是 Retry、继续降级，还是原 Plan 假设已经失效，需要 Replan？

## A14 — Blue Answer

能不能出境这个 Decision 应该只有 Security 做。

Gateway 负责在 Security 已允许的 Provider 集合里做 Routing/Fallback，并在真正发请求时执行这个约束；网络层还可以再做 allowlist，属于防御性 Enforcement，但不能反过来替 Security 决策。

所以境外 Provider 即使技术上可用，只要 Matter Policy 不允许，就根本不能成为 fallback candidate。

第二种情况要看质量假设。弱模型如果仍满足这个 Step 已声明的能力下限，就是 Provider Retry/Fallback；如果已经明显不满足 Planner 当时依赖的能力假设，那计划假设失效，我会 Replan，而不是偷偷降级后继续。

## R14 — Red Review

**Status:** CLOSED

这里 Security Decision 和 Gateway Enforcement 分得比较干净：

Security 决定哪些 Provider 合法；

Gateway 只能在合法集合内 Routing；

Infrastructure/network 可以做防御性 Enforcement；

弱 fallback 若破坏 Step capability assumption，则不是普通 Retry，而是 Replan。

这个边界可以 Freeze 到总体层。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q15 — Red Question

现在我直接把整个 Memory Module 删掉。

Simple QA 还能不能跑？

Complex Legal Analysis 能不能用 Domain Snapshot + 当前 Run Context 跑？

Specialist Agent 能不能只拿自己的输入 Context 工作？

如果答案大部分是“可以”，那 Memory 为什么现在应该冻结成独立 Module，而不是一个可选 Context Provider？

我想听它拥有哪一类别的模块不能自然拥有的长期状态和生命周期。

## A15 — Blue Answer

这三个基本都可以跑。

Simple QA 完全不需要长期 Memory；Complex Legal Analysis 可以靠当前 Domain Snapshot、Knowledge Evidence 和 Run Context；一次性的 Specialist 也可以只拿显式输入。

Memory 真正独有的只有一类东西：跨 Run、非权威、允许遗忘的可复用上下文，比如用户偏好、可复用 Summary、经验、Reflexion Candidate，以及它们自己的 Scope、Retention、Expiry、Deletion 生命周期。

但这不代表它一定值得独立 Module。长期 Memory 本来就是待证明收益的能力。如果 OpenViking 或 Host 已经满足这些 Contract，或者消融发现没有收益，我会让它退化为可选 Context Provider，而不是为了架构完整性保留一个模块。

## R15 — Red Review

**Status:** ARCHITECTURE_CONCERN

这是第三个 Module Map 问题。

Blue 事实上证明了：

删除 Long-term Memory 后：

Simple QA 成立；

Complex Legal Analysis 成立；

Ephemeral Specialist 也成立。

它进一步承认：

> 如果 Host / OpenViking 能满足 Contract，或者消融无收益，Memory 应退化为可选 Context Provider。

这和 ADR-0008 的条件性定位是一致的。

所以问题不是 Memory Concept 有没有用。

问题是：

> 07 现在有没有足够理由被冻结为一级 Logical Module？

Blue 的回答是：还没有。

**Freeze Impact:** FREEZE_BLOCKER

**Follow-up:** Q35

---

## Q16 — Red Question

Memory 再来一个具体冲突。

长期 Memory 说：“这个用户习惯用旧版合同模板。”

当前 Matter 的最新 DocumentVersion 明确是新版模板。

用户这一次又明确说：“不要沿用以前的习惯。”

Context Assembly 怎么排序这三者？

另外，Reflexion Candidate 是模型产生的，它什么时候才能进入长期 Memory？

谁批准？

如果用户要求删除这条长期记忆，它已经进入旧 Checkpoint 或 Trace 里的副本怎么办？

## A16 — Blue Answer

这里不能用一个永久的“来源优先级表”。

“用户喜欢旧模板”是偏好；“Matter 当前是新版 DocumentVersion”是业务事实；“这次不要沿用旧习惯”是当前任务约束。

所以这次任务明确不用旧习惯，同时真正处理哪个版本仍然以 Matter 当前 DocumentVersion 为准。Memory 两边都不能覆盖。

Reflexion Candidate 也只是 Candidate，模型不能自己写进长期 Memory。至少必须经过 Memory Policy 的 Promotion Gate；高风险内容是否再要求人工批准，我认为目前还没有冻结到可以声称已经确定。

删除 Memory 后，新的 Context Assembly 必须再也召回不到它。旧 Checkpoint/Trace 中已经存在的副本属于 Runtime/Audit retention 问题，不应该继续当 Memory 使用；如果合规策略要求真正物理删除，还需要单独的 retention/redaction/purge 规则。目前这部分我不会说已经完全闭合。

## R16 — Red Review

**Status:** PARTIAL

业务事实、当前任务约束、Memory Preference 三者没有被混淆，这部分回答正确。

但两个跨层问题仍未闭合：

第一，Reflexion Candidate → Durable Long-term Memory 的 Promotion Authority 还没冻结。

第二，Delete / Retention 发生以后：

Memory Store；

Runtime Checkpoint；

Trace；

Audit；

中已经复制的数据如何处理，目前只有“不能继续当 Memory 使用”，但没有完整生命周期边界。

这是 Memory、Runtime、Observability、Security 之间真正的跨层问题。

**Freeze Impact:** ARCHITECTURE_REVISION_REQUIRED

**Follow-up:** Q35

---

## Q17 — Red Question

现在攻击 Security。

Security 说自己拥有 Policy Decision；但是实际 Enforcement 分布在 Knowledge Read、Model Egress、Tool Execute、Domain Commit 等多个地方。

那 Security 到底是一个独立 Module，还是所有模块共同遵守的一套 Cross-cutting Contract？

假设 Knowledge 在执行前正确检查权限，但 Tool Runtime 忘了检查。

这是 Security Module 的 Bug，还是 Tool Runtime 的 Bug？

我想知道 Policy Decision、Policy Distribution 和 Policy Enforcement 三者的责任边界，而不是一句“所有地方都要做安全校验”。

## A17 — Blue Answer

Security 可以是独立的 Decision Authority，同时安全又是 Cross-cutting Enforcement。

我会这样分：

Policy/Grant/SecurityEpoch 和 Authorization Decision 由 Security 唯一拥有；Decision 的传输、缓存和版本校验可以走共享基础设施；真正的 Enforcement 则必须由资源 Owner 在自己的危险边界执行。

所以 Knowledge Read 由 Knowledge Enforcement，Model Egress 由 Gateway Enforcement，Tool Effect 由 Tool Enforcement，Domain Commit 由 Domain Enforcement。

如果 Tool Runtime 忘了检查，直接 Bug 是 Tool Runtime 的，因为它没有执行必须遵守的安全 Contract。Security 可能还有测试覆盖不足的问题，但它不能为了避免别人漏检查而接管所有业务调用。

## R17 — Red Review

**Status:** CLOSED

这是一个成熟的回答。

Security 同时具有：

central decision authority + distributed enforcement

并不冲突。

Blue 清楚区分：

Policy / Grant / SecurityEpoch / Authorization：Security Owner；

Distribution：共享机制；

Enforcement：资源边界 Owner。

Tool 忘记校验首先是 Tool 的 enforcement bug，这一点也说得对。

关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q18 — Red Question

开始看 Single Controller。

两个 Runtime Worker 同时因为超时接管了同一个 Run，它们都认为自己是 Controller。

“Single Controller”到底是逻辑上每个 Run 只有一个控制权，还是物理上只有一个进程？

如果是前者，谁提供 Lease / Fencing / Generation，怎么保证旧 Controller 恢复网络以后不能继续提交控制决策？

如果 Controller 进程彻底挂掉，新的实例从什么状态判断“我可以接管”？

## A18 — Blue Answer

Single Controller 应该是每个 Run 逻辑上只有一个有效控制权，绝对不是整个系统只能有一个进程。

底层需要 Infrastructure 提供 Lease、权威 Clock、CAS 和单调递增的 fencing token / controller generation。新的 Worker 只有在旧 Lease 到期或被明确撤销后才能取得更高 Generation。

之后每次 Plan 激活、Dispatch、Checkpoint 控制写入都要带当前 fencing token，存储侧做条件写。旧 Controller 网络恢复以后拿着旧 token，不能靠“它自己觉得还活着”继续提交。

新实例接管前应该读取最新 Run durable state、checkpoint、当前 Domain Version 和未决 Effect，再取得新的 Lease 后继续。

目前仓库里有 execution epoch、replan barrier 和 Infrastructure fencing 概念，但我不会把它说成已经证明完整 Controller HA；Current baseline 本身也明确不是 production readiness。

## R18 — Red Review

**Status:** CLOSED

Single Controller 已被解释为：

> 每个 Run 只有一个逻辑控制权，而不是全系统一个进程。

Lease、CAS、clock、fencing/generation 属于 Infrastructure primitive；Runtime 消费这些 primitive 保证 control authority。

这是总体架构层足够的答案。

是否真的实现 HA 属于 Current Evidence 问题，不阻止 Target Boundary Freeze。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q19 — Red Question

复杂任务里有两个 Specialist A 和 B。

PlanVersion 2 下，它们并行研究两个争议点。

A 先发现一个关键假设错误，申请 Replan；此时 B 还在用 V2 跑一个十分钟任务。新 PlanVersion 3 已经激活后，B 才返回一个质量很高的结果。

这个结果怎么处理？

直接丢掉、重新验证后复用，还是允许进入 V3？

所谓 Replan Barrier 到底阻止的是“新 Step 发出”，还是连旧 Branch Result 的 Admission 也阻止？

## A19 — Blue Answer

我不会直接丢，也不会直接让它进入 V3。

B 的结果必须继续带着 PlanVersion=2 + execution epoch + input/dependency refs 保存成 Late Branch Result。V3 想复用它，要重新检查它依赖的 Domain Snapshot、Knowledge Generation、Security Scope 和那个被 A 推翻的假设有没有受影响。

全部仍成立，可以把它作为 V3 的已有 Proposal/Evidence 复用；有一个核心依赖失效，就标 obsolete。

所以 Replan Barrier 不只是停止旧 Plan 新 Dispatch，还必须阻止旧结果未经重新 Admission 就污染新 Plan。

当前 barrier 实现已经区分冻结新 dispatch、取消/排空运行中 Step 和 late result，但“late result 是否能进入新 Plan”的兼容性判断仍然不能等同于简单收到了结果。

## R19 — Red Review

**Status:** CLOSED

这题回答合理。

旧 PlanVersion 的 late result：

不能直接扔，也不能直接进入新 Plan。

必须重新检查其绑定的：

Domain Snapshot；

Knowledge Generation；

Security Scope；

被 Replan 推翻的 assumption。

这说明 Replan Barrier 不仅是停止新 Dispatch，也保护新 Plan 不受旧结果污染。

剩余兼容性算法可以留到 Runtime Module Design。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q20 — Red Question

再问 Specialist 本身。

如果 Specialist 有自己的长期运行、Interrupt、Resume、独立 Context，并需要崩溃恢复，它有没有自己的 Checkpoint？

如果有，父 Controller Checkpoint 和 Specialist Checkpoint 的一致性怎么恢复？

如果没有，它和一个有状态的 LangGraph Subgraph / Parallel Step 到底差在哪里，为什么需要叫 Agent？

LangGraph 官方当前已经提供 checkpoint、subgraph persistence、parallel execution 和 pending-write recovery；per-thread subgraph 同时并行调用还存在同 namespace checkpoint conflict，需要调用方明确控制。

所以这里我尤其想听：Zuno 自己增加的控制语义究竟是哪一层，而不是重复实现框架已经有的东西。

## A20 — Blue Answer

大部分 Specialist 我不会给它再造一套 Checkpoint。

LangGraph 当前已经支持父图 Checkpointer、Subgraph persistence、interrupt/resume、parallel execution 和 pending writes；默认 per-invocation subgraph 还能继承父 checkpointer 并保持每次调用隔离。真正的 per-thread subgraph 才涉及跨调用状态，而且同一个 stateful subgraph 并行调用确实需要额外约束。

所以一次性 Specialist 更像一个有独立 Context/Permission/Capability 的 Subgraph，durability 直接交 LangGraph。

只有它真的有跨父 Run 的独立生命周期，才值得独立 thread/checkpoint；这时父子不追求 checkpoint 2PC，而通过 invocation ID、结果版本和 Admission Receipt 对账。

Zuno 真正增加的应该是 Domain Snapshot、Security、Budget、Knowledge Generation、Effect Reconciliation 和 Formal Admission，不是重新实现 checkpoint。

## R20 — Red Review

**Status:** CLOSED

这里 Blue 没有继续创造一套“Zuno Specialist Checkpoint”。

这一点很重要。

当前 LangGraph 官方文档确实支持 parent checkpointer 下的 subgraph persistence；per-invocation 是多数独立 subagent 场景的推荐形态，而 per-thread stateful subgraph 在同一实例并行调用时存在 checkpoint namespace 冲突。

因此 Blue 把 Zuno 增量收缩到：

Domain / Security / Budget / Knowledge / Effect / Admission

而不是重做 checkpoint，我认可。

关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q21 — Red Question

三个并行 Branch：

A 成功； B 明确失败； C 调了一个外部 Provider，结果是 outcome_unknown。

Join 现在怎么办？

它是一个 deterministic reducer，还是 LLM 来判断？

如果 reducer 因恢复被执行两次，结果是否严格幂等？

如果 LLM 参与冲突裁决，它产生的只是一个 Proposal，还是能够决定整个 Run 已经可以 Final Synthesis？

## A21 — Blue Answer

第一层一定是 deterministic reducer。

它先按 Branch identity 聚合：A=success，B=failed，C=outcome_unknown。C 没 Reconcile 完之前，只要这个 Effect 可能影响任务结果，就不能进入正式 Final Synthesis。

Reducer 必须按 BranchResult/StepRun 唯一键幂等，恢复执行两次不能重复累计。

LLM 可以在“多个已经合格的结果发生语义冲突”时参与 Join Reflection，但它得到的只能是 Proposal 或 Control Recommendation，不能把 outcome_unknown 改成 success，也不能直接宣布正式业务结果可提交。

Controller 可以据此决定继续、Replan 或等待；Formal Result 仍然要过后面的资格和 Admission。

## R21 — Red Review

**Status:** CLOSED

正确。

deterministic reducer first，LLM 只对已经合法进入 Join 的语义冲突做 Reflection。

特别是：

> LLM 不能把 outcome_unknown “判断”为 success。

这个边界很重要。

Reducer 重放幂等也已经明确。

剩余 reducer 编码细节可以进入模块设计。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q22 — Red Question

还是并行，但这次攻击 Budget 和 Security。

四个 Branch 启动时都合法，也都做了预算预留。

运行过程中：

Branch A 把 Run 剩余 Budget 全部吃光； 与此同时 Branch C 的材料权限被撤销。

谁向其他正在运行的 Branch 传播这两个变化？

已经发给模型的 Context 能不能追回？不能追回的话，系统至少还能阻止什么？

一个 Branch 因权限撤销 Cancel，另一个 Branch 因预算不足 Cancel，这两种 Cancel 最后在 Join / RunOutcome 中应该被当成同一种失败吗？

## A22 — Blue Answer

传播控制应该由 Controller 消费 Budget Ledger 和 Security Epoch 的变化，然后向仍在运行的 Branch 发 cancellation / stop signal；但每个新的 Model、Retrieval、Tool、Commit 边界仍然要自己重新检查当前授权或预算。

已经送进模型 Provider 的 Context 一般追不回来。能做的是 best-effort cancel 请求，并且阻止之后的 Tool、Retrieval、模型续调用和 Domain Admission；权限已经撤销的 Branch 返回结果也不能重新进入 Join 的合格结果集。

两种 Cancel 不能揉成一个错误。

SECURITY_REVOKED 是授权条件消失；BUDGET_EXHAUSTED 是资源控制。Join 可以都看成 terminal branch，但 RunOutcome 必须保留不同 Cause，因为前者不能靠加钱重试，后者可能可以。

## R22 — Red Review

**Status:** CLOSED

Budget exhaustion 和 Security revocation 都可能导致 branch terminal，但原因绝不能抹平。

这个回答同时给出了：

Controller 传播 cancellation；

每个危险边界自行重新检查；

已发往 Provider 的 Context 无法追回；

但可以阻止新的 access / effect / admission。

这是现实的 Continuous Authorization 答案。

关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q23 — Red Question

LangGraph 自己已经有 durable checkpoint、interrupt/resume、pending writes 和失败后从成功节点恢复的机制；官方文档还明确说明 replay 可能重新执行后续 LLM/API/interrupt，而带副作用的操作必须设计成幂等。

所以我给你一个删除题：

把 DispatchGroup、DispatchItem、BranchResultRef、自定义 Recovery 辅助机制都先拿掉，只保留 LangGraph 能提供的执行持久化。

Zuno 哪几个跨层语义会真正丢失？

如果回答不出一个 LangGraph 不应该拥有的 Domain / Security / Effect 语义，那这部分自研 Runtime 复杂度为什么值得 Freeze？

## A23 — Blue Answer

这几个对象我不认为神圣，能删就应该删。

LangGraph 已经能保存 Graph State、并行节点 pending writes，并从成功节点继续；Replay 后面的 API/LLM 仍可能重新执行，所以副作用本身还是要求应用层幂等。

真正不能丢的是：Branch 当时绑定的 DomainVersion、KnowledgeGeneration、PlanVersion、SecurityEpoch、Budget Reservation，以及 Tool 的 PreparedAction、Idempotency 和 EffectReceipt/Reconciliation。

这些不是 LangGraph 应该拥有的业务事实。

所以如果直接用 Send + reducer + checkpoint 仍然能完整携带这些引用，我会删掉 DispatchGroup/DispatchItem。Custom Recovery 也只应该负责 Domain/Effect/Security 与 checkpoint 的跨系统对账，而不是重新实现 LangGraph 已有的 crash recovery。

## R23 — Red Review

**Status:** CLOSED

这个回答通过了 Delete Test。

LangGraph 官方本身已经提供 checkpoint fault tolerance 和 pending writes；在同一个 superstep 中，成功节点的 pending writes 可在失败恢复时复用。Replay 也确实会重新执行 checkpoint 之后的 LLM / API / interrupt。

因此 DispatchGroup / DispatchItem / BranchResultRef 如果没有额外语义，就应该可以删。

Zuno 真正需要保留的是框架之外的 Domain、Security、Budget 和 External Effect Contract。

关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q24 — Red Question

现在做最关键的双写故障。

FindingVersion V7 已经在 PostgreSQL Commit 成功。

紧接着 Runtime 保存 Checkpoint 失败，进程崩溃。

重启后 Checkpoint 仍然认为“Domain Commit 还没执行”。

文档现在写的是 Domain State wins。

这四个字不够。

新的 Runtime 实例具体先读什么、比较什么？

怎么知道 V7 就是这个 Step 提交的，而不是另一个并发 Run 提交的？

它怎么避免重新 Admission、重复触发后续 Tool，最后又怎么把 Runtime Control State 修到一个合法状态？

## A24 — Blue Answer

只比较“现在最新是 V7”肯定不够。

Domain Commit 必须同时保存能证明因果关系的字段，例如 run_id、step_run_id、proposal/admission ref、idempotency_key、expected prior version、commit/admission id。共享 Envelope 已经有 run、step、correlation、causation、idempotency 和 aggregate version 这些基础字段，但 Finding Commit 本身也必须把关联保留下来。

恢复时先读当前 Domain Version 和对应 Admission/Commit 记录，再读 EffectReceipt/Outbox，最后对比 Checkpoint。

如果找到“这个 Step 的同一个 idempotency/admission 已经提交 V7”，就不再 Admission，直接把 Runtime 修成 completed-by-reconciliation。

后续 Tool 最好由同一事务产生的 Outbox/causation record 驱动，而不是看到 checkpoint 落后就再触发一次。

如果 V7 无法证明与这个 Step 的因果关系，我不会猜。当前总体文字还没有把这条具体 Commit Contract 冻结到这个程度，所以这是实际 Freeze Gap。

## R24 — Red Review

**Status:** OPEN

这是本轮最重要的 Freeze 问题之一。

Blue 回答方向对，但最后明确承认：

> 当前总体架构还没有把 Finding Commit 的 causation / admission reconciliation contract 冻结到足够精确。

这正是问题所在。

“Domain State wins”只是原则。

真正恢复必须能证明：

> 这个 Domain Commit 就是这个 Run / Step / Proposal / Admission 的结果。

否则看到 V7 根本不能判断：

我提交过；

另一个 Run 提交过；

同一幂等请求提交过；

还是完全不同的业务更新。

这是跨 Domain / Runtime / Persistence 的恢复锚点。

不能推给模块内部。

**Freeze Impact:** FREEZE_BLOCKER

**Follow-up:** Q36

---

## Q25 — Red Question

反过来。

Runtime Checkpoint 已经写着某 Step 成功，随后 Domain Admission 因 CAS Conflict 没有提交。

服务器这时重启。

Runtime 看起来完成，Domain 世界里结果不存在。

哪个状态是事实？

这是 Retry、Replan、Reconcile 还是重新 Domain Admission？

如果 CAS Conflict 是因为另一个 Run 已经提交了更新版本，这时候原 Plan 的 Domain Snapshot 也已经过期了，你还会把它当普通 Retry 吗？

## A25 — Blue Answer

如果这个 Step 的完成条件包含正式 Domain Commit，那么 Domain 没有结果就是事实，Checkpoint 的 success 是过早提交的控制状态。

恢复第一步是 Reconcile，而不是立即 Retry：读当前 Domain Version，确认 CAS 为什么冲突。

如果只是同一结果已经被另一个幂等路径提交，可以把当前 Step 对账成 satisfied。

如果另一个 Run 提交的是不同的新版本，那原 Plan 绑定的 Domain Snapshot 已经过期，这时就不是普通 Retry，而是 Replan。

所以正确协议应该让“执行成功”和“Formal Admission 成功”成为两个状态；需要 Admission 的 Step 在拿到 Admission Receipt 以前不应该被写成最终成功。

## R25 — Red Review

**Status:** PARTIAL

Blue 的故障分类正确：

如果 Domain Admission 是完成条件，那么 Checkpoint 的 success 只是错误的控制状态。

先 Reconcile；

若发现另一路径已幂等满足 → satisfied；

若发现 Domain 已被不同的新 Version 改变 → 原 Snapshot 失效 → Replan。

问题是 Blue 实际又引入了一个 Freeze 级状态区别：

> execution succeeded != formal admission succeeded

当前总体 Runtime 的 Step / RunOutcome 是否正式包含这个区别，还不够明确。

Q24 和 Q25 本质上是同一组跨存储 commit semantics。

**Freeze Impact:** ARCHITECTURE_REVISION_REQUIRED

**Follow-up:** Q36

---

## Q26 — Red Question

新 Evidence 再打一次长期状态。

昨天 WorkProduct V3 已经完成 Human Review，并且 PDF 已下载给用户。

今天新 Evidence 进来，Finding 被标成 STALE，WorkProduct V3 也不再应该被当成最新正式结论。

数据库里改状态不难。

但用户手里的 PDF 已经出去了，外部法院系统可能也缓存了 V3。

谁负责“已发布结果后来失效”这件事？

Domain 只负责状态，Product 只负责 Surface，那通知、撤回、版本查询、消费者看到 stale 状态的跨层责任现在闭合了吗？

## A26 — Blue Answer

已经下载到别人电脑里的 PDF，系统实际上无法“收回来”，所以不能把撤回设计成物理删除。

Domain 应该负责把 V3 保留为历史版本，同时标记 stale/superseded，并产生一个带 WorkProduct ID 和新状态的可靠变更事实。

Product / Host Integration 负责把这个变化通知给用户和外部法院系统，并提供一个稳定的 Version/Status 查询接口。外部系统如果支持 webhook 或 acknowledgement，可以进一步确认同步。

以后打开 V3，应该明确看到“这是历史版本，当前已被 V4 或 review_required 替代”。

但目前总体架构主要写到了 Domain Staleness，没有把 external consumer invalidation / notification / acknowledgement 完整闭环写清。所以我认为这题今天不能回答成“已经闭合”。

## R26 — Red Review

**Status:** OPEN

Blue 说得很现实：

PDF 下载以后无法“收回来”。

Domain 能做的是把 V3 标成历史 / stale / superseded。

真正没有闭合的是：

> 已发布结果失效如何传播到外部消费者。

谁拥有：

Invalidation notification；

Consumer acknowledgement；

Status query；

Embedded Host 同步；

未成功通知时的状态？

Blue 自己明确承认 Overall Architecture 目前只覆盖了 Domain Staleness，没有覆盖 external consumer invalidation。

这是跨层产品闭环，而不是某个类怎么实现。

**Freeze Impact:** FREEZE_BLOCKER

**Follow-up:** Q37

---

## Q27 — Red Question

我给你六个实际故障，不要先讲定义，直接分类。

1. Model HTTP 503，但当前模型仍符合 Plan 假设；

2. LLM Structured Output 第一次 Schema Invalid；

3. Retrieval 返回 0 个证据，但任务要求必须有证据；

4. Tool Schema 已发生不兼容变化；

5. 外部 POST Timeout，无法判断有没有成功；

6. 用户权限在等待期间被撤销。

分别应该进入：

Retry / Replan / Reconcile / Human Review / Abstain / Fail / Cancel

中的哪一个？

允许一个案例有“先 A，再 B”，但我要听清楚触发转换的事实是什么。

## A27 — Blue Answer

1. Retry。503 是瞬时执行失败，模型能力假设没变；超过 Retry Policy 后才考虑 fallback，fallback 不再满足能力假设时转 Replan。

2. Retry。第一次 Schema Invalid 先做 structured-output repair / parameter retry；连续失败导致当前执行方式不可用时再升级模型或 Replan。

3. 先做一次有边界的补检索；如果仍然 0 且任务硬性要求证据，Abstain。如果还有新的来源或检索策略需要改变计划，则先 Replan → 最终仍无证据再 Abstain。

4. Replan。旧 Capability Assumption 已失效；没有安全兼容 Provider 时再 Human Review / Fail。

5. Reconcile。确认成功才补状态，确认没执行才 Retry；始终确认不了就 Human Review。

6. Cancel 当前未授权执行；如果任务允许合法缩小 Scope，可以 Cancel branch → Replan，否则 Run 终止。

## R27 — Red Review

**Status:** CLOSED

这组六分类总体成立：

1. 503 → Retry；

2. first schema invalid → repair / Retry；

3. zero evidence → bounded retrieval / Replan → Abstain；

4. incompatible Tool Schema → Replan；

5. unknown POST outcome → Reconcile；

6. permission revoked → Cancel，合法缩 Scope 才 Replan。

这里已经足以证明 Blue 真正区分了 Retry / Replan / Reconcile，而不是背定义。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q28 — Red Question

现在我拿到一次出错 Run，只允许你看四类数据：

Domain State； Runtime Checkpoint； EffectReceipt； Trace。

我问你：

当时用了哪个 DocumentVersion？ 哪个 KnowledgeGeneration？ 哪个 PlanVersion？ 为什么 Retry？ 为什么 Replan？ 谁批准了 Tool？ 为什么 Final Gate Reject？ 最终有没有真实 External Effect？

这套数据今天理论上能不能把这些问题全部回答出来？

如果 Trace 恰好没送成功，还能不能回答其中必须审计的部分？

## A28 — Blue Answer

不能保证全部回答。

DocumentVersion 应该从 Domain Snapshot/Run binding 找到；KnowledgeGeneration、PlanVersion 应该在 Runtime State；最终 External Effect 要看 EffectReceipt/Reconciliation。

但是“为什么 Retry / Replan”“谁批准 Tool”“为什么 Final Gate Reject”不能只依赖一条可能丢失的 Trace。尤其 Approval 本来是 Security 的 Durable Decision，不应该因为 Trace exporter 挂了就不存在。

所以给我这四类数据，Trace 正常时大部分问题理论上能还原；Trace 丢失以后，不足以证明所有强审计问题。

真正必须审计的 Approval、Policy Decision、Mandatory Audit 等还需要 Durable Audit/Security Decision Store。Trace 是诊断视图，不能成为唯一法律证据。

## R28 — Red Review

**Status:** PARTIAL

Blue 正确指出了一个关键问题：

仅仅：

Domain + Checkpoint + EffectReceipt + Trace

在 Trace 丢失以后，不能证明所有强审计事实。

Approval / Authorization / mandatory audit 本身必须是 Durable State。

这其实和当前 ADR-0003 的三层 Audit 设计一致：Security Audit Requirement、Infrastructure durability receipt、Observability AuditEvent 本来就不是同一个东西。

但这意味着当前 Freeze Gate 里的：

> “Observability 可以重建关键 Run 和关键决策”

需要精确定义。

究竟是“Observability 单独重建”，还是“通过 Domain + Runtime + Security/Audit + Effect + Telemetry 联合重建”？

目前 Blue 的答案支持后者。

**Freeze Impact:** ARCHITECTURE_REVISION_REQUIRED

**Follow-up:** Q38

---

## Q29 — Red Question

Observability 这里我不接受“LangSmith 能看 Trace”作为回答。

OpenTelemetry 本身允许 Sampling，未采样的 Span 可以不进入 Exporter；LangSmith 当前确实支持 tracing、offline eval 和 online eval，但这些都只是 Provider 能力。

所以：

Tool Effect、权限变更、Human Approval 这种关键 Audit 能不能因为 Trace Sampling 或 LangSmith Delivery Failure 而消失？

如果不能，它们的 Durable Audit Path 在哪里？

LangSmith Cloud 被法院禁止、OTel Backend 又临时不可用时，业务 Run 哪些可以 fail-open，哪些必须 fail-closed？

Audit 和 Observability 到底是不是两种不同事实？

## A29 — Blue Answer

关键 Audit 不能依赖 Trace Sampling。

OTel 的 Sampling 本来就允许不把未采样 Span 交给 Exporter，所以它天然不能充当必须 100% 留存的审计账本。

高风险动作应该走独立 Durable Audit Path：Security 先给 Audit Requirement；Infrastructure 本地 durable commit，并拿到 AuditPersistenceReceipt / Outbox；之后 Observability 再把它形成 AuditEvent、异步送外部 Sink。现有共享 Contract 已经区分了这些事实。

普通性能 Trace、Metrics Exporter 挂掉可以 fail-open 或 degrade。

但 MANDATORY_BEFORE_EFFECT 的 Tool Effect、策略指定的权限变更、Credential 使用、Break-glass 等，没有本地 Durable Audit Receipt 就必须 fail-closed。

所以 Audit 和 Observability 是两种不同事实：前者要求完整性、留存和合规证明；后者可以 Sampling，主要用于诊断和评测。

## R29 — Red Review

**Status:** CLOSED

这一题回答非常清楚。

OpenTelemetry 官方规范明确允许 Sampling 导致未 sampled span 不发送给 Span Exporter，因此 OTel Trace 天然不能充当要求 100% durability 的审计事实源。

所以：

ordinary telemetry 可以 fail-open/degrade；

mandatory audit 必须先本地 durable；

MANDATORY_BEFORE_EFFECT 没 durable receipt 就 block effect；

LangSmith / OTel sink 只是后续消费端。

这和 ADR-0003 的设计一致。

关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q30 — Red Question

再把 Eval 和 Runtime Gate 分开。

LangSmith 支持 offline evaluation，也支持针对真实 traces 的 online evaluation。

现在一个 AgentVersion 在离线 Benchmark 没过 Release Gate，这是“这个版本不能发布”。

另一个已经发布的 Agent，在某次真实任务里证据不足，这是“这一次 Result 不能正式 Admission”。

这两个 Gate 谁分别拥有？

Eval Result 能不能直接改变 Domain State？

如果在线 Evaluator 晚了五分钟才给出低分，而 WorkProduct 已经 Admission，系统怎么解释这个结果？

## A30 — Blue Answer

这是两个完全不同的 Gate。

离线 Benchmark / Release Gate 属于 Evaluation：决定某个 AgentVersion、CapabilityVersion 有没有发布/使用资格。LangSmith 官方也把 offline evaluation 定位在发布前 Dataset/Experiment，把 online evaluation 定位在真实生产 traces 的持续监测。

单次任务证据不足，则是这个 Result 的 Formal Eligibility / Domain Admission 问题。

Eval 只能产生 Eval Result / Release Decision，不能直接改 Domain State。

如果 Online Evaluator 五分钟后才说低分，那它只能触发 Review、Incident 或新的 Staleness/Reevaluation 流程，不能偷偷把五分钟前提交的 WorkProduct 从数据库里抹掉。

如果某个 Evaluator 的结果必须阻止 Admission，它就必须成为同步 Final Gate 的输入，而不能依赖异步 online evaluator。

## R30 — Red Review

**Status:** CLOSED

Release Eval 和 per-run Formal Eligibility 已经明确拆开。

LangSmith 当前官方定义也确实把 offline evaluation 用于 pre-deployment dataset / experiment，把 online evaluation 用于生产 traces 的持续监测；online evaluator 还可以配置 sampling。

因此 asynchronous online score 不能事后偷偷成为五分钟前 Domain Commit 的同步前置条件。

如果某 evaluator 必须阻止 Admission，它就必须进入当时的 synchronous Gate。

关闭。

**Freeze Impact:** NONE

**Follow-up:** NONE

---

## Q31 — Red Question

最后攻击 Infrastructure & Persistence 本身。

它现在一口气装了：

PostgreSQL、Checkpointer、Object Store、Vector、Graph、Queue、Worker、Deployment、Backup / DR 和连接原语。

这些东西大部分并不共享业务状态，只共享“它们都是基础设施”这个标签。

为什么这是一个满足 Freeze Test 的 Logical Module，而不是一个 Platform / Physical Responsibility Layer？

它拥有什么统一、稳定的 Contract 和 Failure / Recovery Boundary？

如果答案最终仍然是“各自的 DB、Queue、Checkpoint、Object Store 都有自己的故障语义”，那这个候选到底是模块，还是一个文档分类桶？

## A31 — Blue Answer

按这个 Freeze Test，我更愿意把它叫 Platform / Infrastructure Responsibility Layer，而不是和 Legal Domain 一样意义上的逻辑业务模块。

它确实有一些稳定公共 Contract：transaction、CAS、lease/fencing、durability、queue delivery、object integrity、backup/restore、connection primitive。但 PostgreSQL Commit、Queue Redelivery、Object Visibility、Checkpointer Recovery 的状态机并不是同一套。

所以“都属于基础设施”不足以证明一个 cohesive logical module。

可以有统一的 Platform Owner、统一代码边界和统一运维责任，但这和“它是 10 个业务逻辑模块之一”不是一回事。当前 ADR 把这些物理能力集中到 platform/** 是合理的工程组织方式；是否继续把它算成 Logical Module，我认为还没有通过这轮 Freeze Test。

## R31 — Red Review

**Status:** ARCHITECTURE_CONCERN

这是第四个非常直接的 Module Map Blocker。

Blue 认为：

> Infrastructure 更像 Platform / Infrastructure Responsibility Layer，而不是和 Legal Domain 同类型的 Logical Module。

我同意这个攻击已经成立。

PostgreSQL、Queue、Object Store、Checkpoint、Vector、Backup/DR 并没有一套共同业务状态机。

可以有：

Platform owner；

shared primitives；

统一 code organization；

统一运维责任；

但这并不自动证明：

> 10 Infrastructure & Persistence

应该占一个与 Domain、Knowledge 对等的 Logical Module 槽位。

当前 10-Module Map 因此还不稳定。

**Freeze Impact:** FREEZE_BLOCKER

**Follow-up:** NONE

---

## Q32 — Red Question

我最后给你一个真正的 Freeze Test。

ADR-0008 现在仍然明确说：

Native Runtime 是 DEFERRED / HYPOTHESIS； Persistent Multi-Agent 不默认保留； Long-term Memory 只有消融证明收益才启用； Tool Runtime 优先现有 MCP/API/Sandbox + 薄 Adapter； Generic Host 可以负责交互、任务入口和一般编排。

但当前 10-Module Candidate 又把 Product Surface、Agent Runtime、Multi-Agent、Tool Runtime、Model Gateway、Memory 都提升成了一等候选模块。

所以今天如果我签字：

OVERALL_ARCHITECTURE = FROZEN_BASELINE

我到底是在冻结不可替代的责任边界，还是已经偷偷把一批尚未证明需要存在的实现责任冻结进去了？

请你最后告诉我：这 10 个候选里，哪些即使未来完全交给 Generic Host / LangGraph / OpenViking / MCP / LangSmith，Zuno 仍然必须保留自己的 Contract；哪些候选一旦外置后，本身就不应该继续作为 Zuno 的独立 Module。

如果这个问题现在还回答不稳定，我认为 Module Decomposition Gate 就还没有资格打开。

## A32 — Blue Answer

我今天不会直接签这 10 个候选为最终 Frozen Modules。

我认为真正值得冻结的是不可替代的 Contract，而不是当前实现形状。

即使底层全部换 Provider，Zuno 如果这个产品命题还成立，仍然需要保留：最小 Legal Domain / Admission / Version / Staleness Contract；DocumentVersion—KnowledgeGeneration—Readiness—Citation 的 Evidence Contract；法律 Capability 的版本、Conformance 和 Proposal Contract；Security 的 Authorization / Approval / Audit Requirement；Formal Result 与 Release Eval 的 Gate Contract；只要存在外部副作用，就必须保留 Effect / Idempotency / Reconciliation Contract。ADR-0008 本身也是把 Native Runtime、长期 Memory、Persistent Multi-Agent 和自研 Tool Runtime 放在条件性位置，而不是产品前提。

反过来，Product Surface / Native Agent Portfolio、Agent Runtime / Multi-Agent、Model Gateway、Long-term Memory、通用 Tool Execution Engine、Observability Transport、Infrastructure，如果 Generic Host、LangGraph、OpenViking、MCP、LangSmith 或托管基础设施已经完整满足 Zuno 所需 Contract，它们就不应该为了“十模块完整”继续作为 Zuno 独立 Module存在。

Knowledge 也一样：底层 Parse、BM25、Vector、Graph 都可以外置，但 Scope、Version、Readiness、Evidence 和 Citation 的业务 Contract 不能丢。

另外，这一轮已经暴露出几个还没收干净的边界：Canonical Event 到底存不存在；Simple Answer / Final Gate 的唯一 Owner；Capability 和有副作用 Tool 是否应该拆开；Embedded Mode 下 Product 是否还是模块；Infrastructure 是否只是 Platform Layer；以及双写恢复和已发布 WorkProduct 失效通知的具体 Contract。

所以我的判断是：可以冻结这些不可替代的责任原则，但还不能把当前 10-Module Candidate 原样冻结成最终模块分解。Module Decomposition Gate 现在还不应该打开。

## R32 — Red Review

**Status:** ARCHITECTURE_CONCERN

Blue 最后的结论我接受：

> 现在不能把 10-MODULE CANDIDATE 原样冻结。

而且原因不是 Measurement 没跑。

是仍然存在真正的 Architecture Boundary 问题。

ADR-0008 本来就明确：

Native Runtime = deferred hypothesis；

Persistent Multi-Agent = 非默认；

Long-term Memory = conditional；

Tool Runtime = reuse-first；

Generic Host = 可以承担通用 Host / orchestration。

所以不能一边说这些能力可以整体外置，一边又为了模块图整齐，把它们全部先冻结成 Zuno 一级 Module。

这会把：

> Contract 必须存在

偷偷升级成：

> Zuno Module 必须存在。

两者不是一回事。

**Freeze Impact:** FREEZE_BLOCKER

**Follow-up:** Q33-Q38

---

# Pending Follow-up Questions

## Q33 — Red Question
### Simple Answer / Invocation Ownership

把 Q2 和 Q9 合在一起。

现在有两个组合型决定都没有 Owner：

SimpleAnswer FinalGate

和

Agent InvocationEligibility

假设 Generic Host 提交一个请求，Zuno 只提供 Knowledge / Legal Capability，但不启动 Native Runtime。

请明确回答：

哪个责任边界拥有“这个请求现在允许执行”和“这个普通答案现在允许返回”这两个最终组合决定？

不要回答“各模块一起判断”。

我要一个最终 decision authority，同时说明它为什么不会重新拥有 Security、Knowledge、Model 的原始事实。

## A33 — Blue Answer

当前架构**没有冻结**这两个组合决定的唯一 Owner。`CURRENT ARCHITECTURE DOES NOT FREEZE THIS YET.`

先说明基线状态：实际 `main` 已前进到 `b287d6c3...`，但 Round 02 Archive 仍明确把 Architecture Baseline 固定为 `a9fa3834...`，Q1–Q32 已归档、Q33–Q38 Pending、Main Judgment Pending、Architecture Revision `NOT_STARTED`、Module Decomposition Gate `NOT_OPEN`。因此这里仍按 `a9fa3834...` 回答。

Host-owned Simple QA 在 ADR 的 Host Boundary 里是成立的 Target 方向：Generic Host 可以负责交互、任务入口、一般编排，Native Runtime 本身还是 deferred/hypothesis。所以一个只调用 Zuno Knowledge / Legal Capability 的请求，**原则上可以完全不启动 Zuno Native Runtime**。但 Overall Architecture 同时又保留了“任何任务不能绕过 Plan / Trace / Budget / AnswerPolicy / RunOutcome”的表述，两者目前还没有正式收敛。

“允许执行”和“允许返回”也不是同一个决定。前者回答的是：当前身份、权限、Scope、Knowledge Readiness、Capability/Model Availability 是否允许开始这次调用；后者回答的是：已经得到的 Answer 是否满足当前证据、Citation、Degradation 和 Answer Policy，可以交给用户。这两个阶段可能一个通过、另一个失败。

目前能明确的是原始事实 Owner 没有歧义：Security 拥有 Authorization Decision；Knowledge 拥有 KnowledgeGeneration / Readiness / CitationLineage；Model Gateway 拥有 Provider Availability、Usage 等模型事实。这些 Owner 应该只输出自己的决定或 Receipt，而不是谁都能宣布最终综合结果。总体 Owner Matrix 对这些底层事实有定义，但没有为 `SimpleAnswer FinalGate` 和 `InvocationEligibility` 指定唯一的最终组合 Decision Authority。

**THIS IS AN OVERALL ARCHITECTURE GAP.**

**PROPOSED RESOLUTION：**可以让现有的请求/响应 Application Boundary 只做“组合裁决”：消费 Security、Knowledge、Model/Capability 的权威结果，自己不重新计算这些事实。它可以同时拥有“是否允许发起本次调用”和“是否允许返回本次普通答案”两个不同的最终决定。但这只是本轮可考虑的收敛方向，`a9fa3834...` 并没有把这个 Owner 冻结下来。

## R33 — Red Review

**STATUS:** ARCHITECTURE_CONCERN

**REVIEW:**
Blue 没有回答出一个已经存在的唯一 Decision Authority，而是明确确认当前 Architecture 尚未冻结 `InvocationEligibility` 和 `SimpleAnswer FinalGate` 的 Owner，这个判断可信。更严重的是，它再次确认 Generic Host 可以合法绕开 Native Runtime，而旧总体原则仍有“任何任务都不能绕过 Plan / Trace / Budget / AnswerPolicy / RunOutcome”的表述，所以这里同时存在 **Ownership Gap + Execution Boundary inconsistency**。

Blue 提出的“Application Boundary 组合裁决”可以成为后续候选，但它现在只是 Proposal，不能拿来关闭问题。Freeze 时不能留下“原始事实 Owner 都清楚，但最终谁有权说 yes/no 不清楚”的状态。

**FREEZE_IMPACT:** FREEZE_BLOCKER

**FOLLOW_UP:** NONE

---

## Q34 — Red Question
### Historical Citation Authority

昨天的 WorkProduct V3 保存了引用。

今天 Knowledge Provider 被彻底替换，原 CitationLineage Store 也迁移掉了。

只保留 Domain DB 和原始 Object Store。

这时候 V3 必须仍然能够独立恢复历史引用吗？

如果是：

究竟哪一个 Canonical Artifact 保存足够的信息？

它归谁拥有？

如果不是：

那 Zuno 所谓长期可审计 WorkProduct 到底凭什么成立？

## A34 — Blue Answer

是，从 Zuno 当前“长期可审计 WorkProduct”的产品目标看，历史 V3 **不应该因为今天换掉 Knowledge Provider 就失去原文回溯能力**。但关键问题是：当前 Architecture 还没有冻结一个足以保证这件事的 Canonical Historical Citation Artifact。

现在已经冻结的 Ownership 是两层：Knowledge 拥有 `EvidenceCandidate / CitationLineage`；Domain 拥有正式 `Evidence business reference / WorkProduct`。CitationLineage 描述检索和引用是如何形成的，它属于 Knowledge 事实；WorkProduct 则是长期业务版本。

因此 CitationLineage 与“昨天已经正式发布的 WorkProduct 的历史引用绑定”并不能自动视为同一个东西。如果 WorkProduct V3 只保存一个 `citation_lineage_id`，而这个 ID 的唯一事实存储跟着旧 Knowledge Provider 一起迁掉，那么 Domain DB + 原始 Object Store **不一定足够**恢复 V3。Object Store 还能给你文件 bytes，但系统可能已经不知道 V3 当时引用的是文件里的哪一段。

当前 ADR 对正式 Evidence 强调来源、版本和引用位置，对长期 Domain State 也强调版本和可审计性，这支持“历史引用需要稳定锚定”的方向；但 Owner Matrix 仍只明确了 CitationLineage 属于 Knowledge，没有另外冻结一个 Domain-owned Historical Citation Snapshot/Binding。

所以答案是：

**CURRENT ARCHITECTURE DOES NOT FREEZE THIS YET.**

缺失的是一个明确的 **historical citation authority / immutable source anchor ownership**。也因此，现在不能声称“只留下 Domain DB + Object Store 就必然足以独立审计 V3”。

**PROPOSED RESOLUTION：**正式 WorkProductVersion 在 Admission 时应固化足以独立回到 `DocumentVersion + immutable source object/hash + stable source location/span` 的历史证据锚点；Knowledge 的 CitationLineage 继续描述检索形成过程，而不是成为历史 WorkProduct 唯一的生存依赖。因为这个锚点证明的是已提交 WorkProduct 的历史内容，它若被采用，其最终 Ownership 应落在 Domain 一侧。这个归属目前仍是 Proposal，不是已经冻结的 Architecture。

## R34 — Red Review

**STATUS:** OPEN

**REVIEW:**
这个回答把问题说透了：`CitationLineage` 的生命周期和已经 Admission 的 `WorkProductVersion` 生命周期并不相同，而当前 Architecture 没有冻结一个在 Knowledge Provider 被替换后仍然存活的 Historical Citation Authority。

这是长期可审计 WorkProduct 的核心，不是 Knowledge 模块内部怎么存 Chunk 的问题。只要历史正式结果仍可能依赖一个可以随着 Projection / Provider 被删除的 ID，就不能证明“版本化 WorkProduct 可长期复核”。

Blue 提出的 Domain-owned immutable source anchor 是合理候选，但仍然只是 Proposal。

**FREEZE_IMPACT:** FREEZE_BLOCKER

**FOLLOW_UP:** NONE

---

## Q35 — Red Question
### Memory Delete Across Copies

用户要求删除一条长期 Memory。

这条内容已经：

进入一次旧 Runtime Checkpoint；

被记录在一次 redacted Trace；

并且成为昨天 WorkProduct 的推理上下文之一。

现在请不要讲具体表设计。

只回答整体语义：

Delete Memory 是只删除“以后可召回的 Memory Fact”，还是要求传播删除到 Runtime / Trace / Audit / WorkProduct Evidence？

谁决定哪些副本必须删除、哪些因为 Audit / Legal Hold 必须保留？

如果不同 Store 得到不同结论，最终是谁的 policy 生效？

## A35 — Blue Answer

当前 Architecture 可以明确的一点是：**Delete Memory 不等于把所有出现过这段内容的地方物理抹除。**

Memory Fact、Runtime copy、Trace copy、Audit record 和 WorkProduct historical context 是不同 Owner 下的不同事实。Memory 已明确不能覆盖 Domain State，也不能把 Runtime Checkpoint 或 Audit 当成自己的存储。因此删除长期 Memory，至少意味着这条 Memory 不再作为可召回 Memory 参与未来 Context Assembly；它不能凭一个 Memory Delete 命令直接重写昨天的 WorkProduct、Runtime 历史或者合规 Audit。

Runtime Checkpoint 中的副本属于 Runtime durable/control history；redacted Trace 属于 Observability；正式 WorkProduct 的历史上下文属于 Domain 历史；Audit 则还有更强的独立规则。ADR-0003 已经明确由 Security 拥有 `SecurityAuditRequirement`，其中包含 `retention_policy_ref` 和 `legal_hold_policy_ref`，Infrastructure 负责持久化执行，Observability 接收 AuditEvent。也就是说，Audit 数据至少已经存在“Policy Owner 与 Persistence/Telemetry Owner 分离”的边界。

但这并没有解决整个系统的删除冲突。Memory 自己又拥有 Retention / Expiry / Deletion，而当前文档没有冻结一个**跨 Memory、Runtime、Trace、Audit、Domain 的最高级 Retention/Delete/Legal-Hold Policy Authority 及冲突优先级**。

所以，如果不同 Store 对“必须删除”和“必须保留”得到不同结论，目前不能回答“最终一定听谁的”。

**CURRENT ARCHITECTURE DOES NOT FREEZE THIS YET.**

Store 也不应该因此成为全局 Policy Owner。它只能 Enforcement 自己收到的有效策略。例如 Audit Store 可以因 Legal Hold 保留历史记录，但这个保留副本不能因此重新获得“可作为长期 Memory 召回”的资格；Memory 删除之后，未来 Memory Retrieval 仍然必须看不到它。

**PROPOSED RESOLUTION：**由现有 Security / Governance 责任统一裁决跨存储的 Retention、Deletion、Legal Hold 和合规例外，各事实 Store 只负责执行属于自己的决定；Memory 删除控制未来 Recall，而保留历史副本是否物理清除由其各自 retention/legal-hold 决定。这个全局 policy authority 在当前 baseline 尚未冻结。

## R35 — Red Review

**STATUS:** OPEN

**REVIEW:**
Blue 正确关闭了一半问题：删除 Memory 不应该自动重写 Domain History、Audit 或 Runtime History，而且“保留副本”也绝不能让旧数据重新获得 Memory Recall 资格。

但真正的跨层 Owner 仍然不存在：当 Memory deletion、Runtime retention、Trace retention、Audit legal hold、Domain history 的政策发生冲突时，谁拥有最终 Policy Authority，目前 Architecture 没有答案。

这不是每个 Store 自己配置 TTL 就能解决的问题。既然系统声明支持 Governance、Retention、Deletion 和 Legal Hold，那么冲突决策权必须在总体层唯一。

**FREEZE_IMPACT:** FREEZE_BLOCKER

**FOLLOW_UP:** NONE

---

## Q36 — Red Question
### Domain Commit / Checkpoint Recovery Invariant

把 Q24 和 Q25 合在一起。

我要一个非常简单的、不涉及数据库实现的全局不变量：

> Runtime 在什么事实 durable 以后，才允许宣布一个“要求 Formal Admission 的 Step”真正完成？

然后告诉我：

如果 Domain Commit 和 Runtime Checkpoint 永远不存在跨库事务，

系统恢复时唯一凭什么证明一个 Domain Version 已经满足了某个 Step，而不是碰巧存在？

这里如果仍然只能回答“Domain wins”，就还没有过。

## A36 — Blue Answer

最简单的不变量应该是：

> **一个要求 Formal Admission 的 Step，只有在“该 Step 导致的正式 Domain Commit”已经 durable 并且可以证明两者的因果绑定后，Runtime 才能把它宣布为真正完成。**

但我要马上区分：前半部分“Checkpoint 不能冒充 Domain Truth、Domain Commit 成功后以 Domain State 为准”已经是当前架构原则；后半部分这个**完整 causation invariant 还没有被冻结**。

Domain Version 本身不够。恢复时看到 `FindingVersion V7`，只能证明 V7 存在，不能证明它就是这个 `run_id / step_run_id` 的 Admission 结果；V7 完全可能是另一个并发 Run 提交的。

Runtime Checkpoint 也不够。Checkpoint 只能说明执行控制认为走到了哪里；Architecture 明确规定 Checkpoint 不是 Canonical Domain Fact。

现有跨模块 Envelope 已经提供了 `run_id、step_run_id、correlation_id、causation_id、idempotency_key、aggregate_id/version` 这些建立因果链所需要的字段，这是重要基础。 但“这些字段存在”并不等于 Architecture 已经冻结了：

`Step → Formal Admission → resulting DomainVersion`

这一条 durable proof。

当前文档写了 `Domain State wins` 和恢复时读取 Domain State、Receipt、Checkpoint 对账，但没有明确冻结一个 **Domain-owned Admission/Commit Receipt**，也没有规定 Runtime 只有拿到这个因果证明之后才能进入 terminal success。

因此：

**CURRENT ARCHITECTURE DOES NOT FREEZE THIS YET.**

**PROPOSED RESOLUTION：**如果采用一个 durable Admission/Commit fact，它必须由 Domain Owner 拥有，因为它证明的是“Domain 接受并提交了什么”，而不是 Infrastructure 或 Runtime 的成功。它至少需要把调用方 Step 的 causation identity 与最终 Domain Version 绑定。恢复时 Runtime 用自己的 Step identity 去查询这个事实：匹配则修正落后的 Checkpoint；找不到则不能因为“数据库里恰好有一个更新版本”就宣告完成，而要继续 Reconcile；若发现 Domain Snapshot 已被其他 Run 改变，则再进入现有 Replan 语义。这个 Receipt/Invariant 目前仍属于 proposed resolution。

## R36 — Red Review

**STATUS:** OPEN

**REVIEW:**
这是本轮最明确的 Recovery Freeze Blocker 之一。

Blue 给出的不变量是对的：

> Formal Admission 是 Step 完成条件时，只有 Domain Commit durable，并且能够 durable 证明 `Step → Admission → DomainVersion` 的因果绑定后，Runtime 才能宣告完成。

但 Blue 同时确认当前 Architecture **并没有冻结这个因果证明**。现有 Envelope 有 `run_id / step_run_id / causation_id / idempotency_key` 只能说明“字段可用”，不能证明某个 Canonical Version 就是某个 Step 的 Admission 成果。

因此当前的 `Domain State wins` 仍然不足以恢复。没有 Durable Causation Fact，Runtime 在 crash recovery 时只能猜，而这是不能接受的。

**FREEZE_IMPACT:** FREEZE_BLOCKER

**FOLLOW_UP:** NONE

---

## Q37 — Red Question
### Published Result Invalidation

WorkProduct V3 已经通过 API 发给两个法院系统。

第二天 V3 变成 stale。

法院 A 成功收到失效通知。

法院 B 三天离线，没有收到。

此时 Zuno 查询接口已经显示 V3 stale，但法院 B 仍然在使用本地缓存。

请明确：

发布结果的 Invalidation Fact 谁拥有？传播动作谁负责？Consumer 是否已经获知又是谁的事实？

这三个事实能不能被混成一个 WorkProduct.status = stale？

## A37 — Blue Answer

这三个事实不能混成一个 `WorkProduct.status = stale`。

第一个事实——**V3 已经 stale**——当前边界是清楚的：这是 Domain Truth。新 Evidence 使 Finding / WorkProduct 的依赖失效后，Domain Owner 可以保存 V3 历史版本，同时把它标记 stale、review_required 或 superseded。Consumer 是否在线不影响这个事实成立。

第二个事实——**失效通知有没有被发出去、发送是否成功**——不是 Domain Staleness 本身。这属于外部集成/交付执行事实。当前 Product Surface 候选确实包含 Court / Generic Host Integration，但 `a9fa3834...` 并没有冻结“Published Result Invalidation Delivery”的唯一 Owner、Retry/Outbox/Delivery Receipt 语义。

第三个事实——**Consumer 是否已经知道**——更不能从“Zuno 发过通知”推出。真正的远端状态属于法院系统；Zuno最多只能在对方协议返回 acknowledgement 时保存“我观察到对方确认了”的事实。法院 B 离线时，Zuno Domain 仍然可以确定 V3 stale；但对 B 来说只能说“尚未获得 Consumer acknowledgement”，不能把它写成“B 已经知道”。

所以法院 A 和 B 可以同时满足：

V3 在 Zuno Domain 中已经 stale；A 已经收到并确认；B 仍可能在用旧缓存。

`WorkProduct.status = stale` 只覆盖第一件事，无法表达第二和第三件事。

**CURRENT ARCHITECTURE DOES NOT FREEZE EXTERNAL CONSUMER INVALIDATION SEMANTICS YET.**

缺失的是 propagation owner、delivery/retry fact，以及 acknowledgement/consumer-observation fact 的长期边界。

**PROPOSED RESOLUTION：**继续让 Domain 只拥有 Invalidation Truth；现有 Host/Product Integration Responsibility 负责传播，而远端 acknowledgement 作为独立集成事实保存。Domain Truth 永远不等待 Consumer 上线。但这一传播与 acknowledgement 语义还没有进入当前 Architecture Freeze。

## R37 — Red Review

**STATUS:** OPEN

**REVIEW:**
回答正确地区分了三个事实：

`Domain invalidation truth ≠ delivery attempt/success ≠ consumer acknowledgement`

这正说明当前 Architecture 的 WorkProduct Lifecycle 还没有真正闭环。

`WorkProduct.status = stale` 只能说明 Zuno 自己知道结果失效；它绝不能证明外部系统已经收到，更不能证明外部系统停止使用旧结果。对于 Embedded Product Mode，这个缺口尤其重要，因为 Zuno 明确允许法院已有系统成为消费者。

Blue 已确认 propagation owner、delivery fact 和 acknowledgement fact 都还未冻结，所以这是总体跨系统状态语义，不是后续某个 webhook 类怎么实现的问题。

**FREEZE_IMPACT:** FREEZE_BLOCKER

**FOLLOW_UP:** NONE

---

## Q38 — Red Question
### Reconstruction Boundary

最后收 Q28。

一次高风险 Tool Run 之后，LangSmith 和 OTel 后端全部丢失，但：

Domain、Runtime、Security Decision Store、Durable Audit、EffectReceipt 都还在。

系统还能不能证明：

谁批准了、为什么允许、执行了什么、最终现实世界是否发生 Effect？

反过来，如果 Durable Audit Store 丢了，但 LangSmith Trace 还完整，能不能作为同等级证明？

我想确认：

> Critical Reconstruction 的架构事实源到底是什么组合，Observability 在里面到底是事实源还是 Projection / Diagnostic View。

## A38 — Blue Answer

当前 Architecture 的基本方向很明确：**Critical Reconstruction 应建立在 Durable Fact Sources 上，而不是建立在 LangSmith / OTel Trace 上。Observability 是 Projection / Diagnostic View，不是业务事实主权。**

Domain 提供正式业务世界发生了什么，例如哪个 WorkProduct / Finding Version 最终存在；Runtime durable state 提供 Run、PlanVersion、Step、Interrupt、控制决策和恢复位置，但不能替代 Domain Truth；Security Decision Store 提供当时的 Principal、Policy/Security Epoch、Authorization Decision 和 Approval，回答“谁批准、依据什么策略允许”；Durable Audit 提供高风险动作必须留存的不可变审计链及其持久化证明；EffectReceipt / Reconciliation 则回答 Tool Runtime 实际观察到的外部 Effect 是 Success、Unknown，还是后来通过 reconciliation 被确认。ADR-0003 明确把这些 Receipt 分开，并明确 `AuditPersistenceReceipt != Tool Effect Success`、`Checkpoint Commit != Domain Commit`。

因此 LangSmith 和 OTel 后端全部丢失，**不应该自动破坏关键事实证明**。谁批准、为什么允许，可以从 Security Decision / Approval 恢复；最终是否发生 External Effect，要看 EffectReceipt / Reconciliation，而不是看一条 Trace 显示 Tool node “completed”。

但“执行了什么”这里还有一个精度问题。ADR-0003 的 Tool 边界实际上还拥有 `PreparedToolAction / ToolAttempt`，Approval 绑定 action hash、tool definition、operation、canonical args hash。 如果 Q38 所说的持久数据把这些 Tool durable facts 也一起丢掉，只剩一个很薄的 EffectReceipt，那么当前 Architecture **不能保证还能恢复完整 canonical action payload**。Durable Audit 可能保存 action reference/hash，但 raw args 又可能因为 Secret/PII policy 本来就不能完整进入 Audit。因此当前并没有冻结一个名字叫“Critical Reconstruction Bundle”的完整最小集合。

反过来，如果 Durable Audit 丢失，只剩完整 LangSmith Trace，**不能把 Trace 当成同等级替代品**。当前架构已经明确 LangSmith 只是 preferred Agent Trace/Eval Provider，OTel-compatible telemetry 可以 Sampling、redaction、delivery failure；Security 的 mandatory audit persistence 是另一条 durable path。外部 Trace 即使碰巧这次很完整，也不能 retroactively 获得 Canonical Audit Authority。

所以现在能够冻结级别地说的是：

**Durable Domain / Runtime / Security Decision / Tool Effect / Mandatory Audit facts 是 Reconstruction 的权威来源；LangSmith / OTel 是诊断、关联、评测和可视化层。**

而“为了完整重建一次高风险 Tool Run，最小必须保留哪些 durable artifacts，以及这些 artifacts 的完整性条件”——**CURRENT ARCHITECTURE DOES NOT FREEZE THIS YET.** 这仍然是一个 Reconstruction Source Gap。

## R38 — Red Review

**STATUS:** PARTIAL

**REVIEW:**
核心边界已经回答清楚：

**LangSmith / OTel Trace 不是 Critical Reconstruction 的权威事实源。**

Domain、Runtime、Security Decision、Mandatory Audit、External Effect 等 Durable Facts 才是事实来源；Trace 是用于关联、诊断、评测和展示的 Projection。反过来，只有 LangSmith Trace、Durable Audit 已丢失时，也不能把 SaaS Trace 临时升级成同等级合规证明。这个原则我认可。

没有关闭的是“执行了什么”这一项。Blue 正确指出，仅有薄 `EffectReceipt` 未必能够恢复 canonical action，而 raw args 又可能因为 PII / Secret policy 不能进入 Audit。因此 **高风险 Run 最低需要保留哪些 Durable Facts，才能完整证明 Action / Authorization / Effect**，当前总体架构还没有冻结。

这不是 exporter 或 trace schema 的模块内部细节，它直接决定 Critical Reconstruction 是否成立。

**FREEZE_IMPACT:** FREEZE_BLOCKER

**FOLLOW_UP:** NONE

---

## Red Pre-Review Baseline Drift Note

**BASELINE_DRIFT**

当前 `main` 实际 HEAD 已前进到 `b287d6c3d2c9f5051d37e6d66e29f61633126a3c`。

但 Round 02 的归档文件明确冻结 `architecture_baseline_sha = a9fa3834c1dd95bdc13caa85b7188d49fc55b1b5`，并记录 `Q33_Q38_PENDING`、`architecture_revision = NOT_STARTED`、`module_decomposition_gate = NOT_OPEN`。因此下面 **只审查 A33–A38 相对于 Round 02 固定 Baseline 的充分性，不用新 HEAD 反向改写本轮判断**。

# RED FINAL FINDINGS — ROUND 02

**ROUND:**
02 — Overall Architecture Freeze Review

**BASELINE:**
`a9fa3834c1dd95bdc13caa85b7188d49fc55b1b5`

**QAR_COMPLETE:**
YES

## CLOSED AREAS

1. **Canonical Domain State 与 Proposal/Candidate 的基本边界成立。**
   `DocumentVersion / Finding / HumanDecision / WorkProduct` 等正式业务状态不能由模型、Knowledge、Specialist 或 Capability Provider 直接提交；模型和 Provider 只产生 Proposal / Candidate / Observation。
   **来源：Q3 / R3，Q11 / R11**
2. **Legal Domain 的核心不变量成立。**
   Domain Admission 不应重新执行 Retrieval、Security、Eval 或模型判断，而应消费其他 Owner 的 typed decision/reference，只负责 Domain 自身的 Version、Dependency、Review、Supersede 等不变量。
   **来源：Q11 / R11**
3. **Ingestion 与 Retrieval 作为同一 Knowledge Responsibility 的理由经受住本轮攻击。**
   共同责任不是“都与知识库有关”，而是 `DocumentVersion → KnowledgeGeneration → Scope-sensitive Readiness → Retrieval`。OCR、Embedding、Graph Build 可以是不同 Worker，不要求成为同一物理服务。
   **来源：Q6 / R6**
4. **Unknown External Effect 的恢复原则成立。**
   外部 POST timeout 不能解释为失败；必须先 Reconcile。只有确认未执行时才能 Retry；无法查询且无幂等能力时必须停止自动执行并进入人工对账，而不能 Blind Retry。
   **来源：Q7 / R7**
5. **Approval 与执行时最新条件绑定的原则成立。**
   Tool Schema、参数、资源、权限或 Security Epoch 改变以后，旧 PreparedAction / Approval 不能被 Runtime 静默复用；新 Action 需要重新满足当前授权及审批条件。
   **来源：Q8 / R8**
6. **Run Budget 与 Model Usage 的 Ownership 可以区分。**
   Runtime 管理 Run Budget、Branch Reservation 和是否允许继续调度；Model Gateway 管理 Provider Attempt、Quota、Usage / Cost Receipt。后到的 Usage Correction 不会把过去合法执行的 Branch 事后改造成非法执行。
   **来源：Q13 / R13**
7. **Security 的 Model Egress Decision 与 Gateway Enforcement 可以区分。**
   Security 决定哪些 Provider 合法；Gateway 只能在合法集合中 Routing/Fallback。Fallback 若破坏原 Step 的能力假设，则不再是普通 Retry。
   **来源：Q14 / R14**
8. **Security Decision Authority 与 Distributed Enforcement 的总体原则成立。**
   Policy / Grant / SecurityEpoch / Authorization Decision 归 Security；Knowledge、Model、Tool、Domain 等资源 Owner 在自己的危险边界执行 Enforcement。
   **来源：Q17 / R17**
9. **Single Controller 已明确为逻辑控制权，而不是单进程。**
   每个 Run 只能有一个有效 Controller Generation；Lease、CAS、Clock、Fencing 等可以作为底层 primitive 防止旧 Controller 恢复后继续写入。
   **来源：Q18 / R18**
10. **Replan Barrier 与 Late Branch Result 的总体语义成立。**
    新 PlanVersion 激活后，旧 Branch Result 不能直接污染新 Plan；必须重新检查其 Domain Snapshot、Knowledge Generation、Security Scope 和失效假设后才可能复用。
    **来源：Q19 / R19**
11. **Specialist Agent 不应默认复制 LangGraph 已有的持久化能力。**
    一次性 Specialist 可以优先使用 Subgraph / Parent Checkpointer；只有真正拥有跨父 Run 生命周期时才有理由引入独立持久控制状态。
    **来源：Q20 / R20**
12. **Join 的第一层必须是确定性且可幂等重放。**
    LLM 可以参与语义冲突 Reflection，但不能把 `outcome_unknown` 判断成 success，也不能绕过 Formal Result Gate。
    **来源：Q21 / R21**
13. **并行 Branch 的 Security Cancel 与 Budget Cancel 不能丢失原因。**
    二者都可能终止 Branch，但 Cause 不同，不能在 Join / RunOutcome 中合并成同一种 Failure。
    **来源：Q22 / R22**
14. **LangGraph 原生持久化、Subgraph、Pending Writes 等能力应优先复用。**
    `DispatchGroup / DispatchItem / BranchResultRef` 等自定义机制没有独立价值时应该可删除；Zuno 自身只保留 Domain、Security、Budget、Effect 等框架不应拥有的语义。
    **来源：Q23 / R23**
15. **Retry / Replan / Reconcile 已经能够在具体故障中区分。**
    503、Structured Output Invalid、Zero Evidence、Tool Schema Drift、Unknown POST Outcome、Permission Revocation 等案例没有被统一塞进 Retry。
    **来源：Q27 / R27**
16. **Telemetry 与 Durable Audit 的原则边界成立。**
    Sampling / exporter failure 不得导致 Mandatory Audit 消失；高风险 Effect 可以要求 durable audit receipt 后才能执行。
    **来源：Q29 / R29，Q38 / R38**
17. **Offline Release Eval 与单次 Runtime Result Eligibility 已分离。**
    Offline Eval 可以决定版本是否允许 Release；某次 Run 的证据不足则决定该次 Result 是否能够 Admission。异步 Online Eval 不能事后伪装成已经发生过的同步 Final Gate。
    **来源：Q30 / R30**

---

## ARCHITECTURE CONCERNS

1. **Simple QA 的执行边界与旧“所有任务必须进入完整 Runtime 约束”的表述不一致。**
   Generic Host-owned Simple QA 被 Blue 明确认可为合法路径，但当前 Baseline 尚未正式收敛这一点。
   **来源：Q1 / R1，Q33 / R33**
2. **Canonical Legal Object Set 自相矛盾。**
   ADR 最小 Kernel 将 `Event / Conflict / Dispute / Fact / LegalIssue` 默认视为 Proposal / Derived View，而 Overall Architecture 又把其中部分直接列为 Domain State。
   **来源：Q4 / R4**
3. **AgentVersion 的“配置组合”与其他事实 Owner 的关系基本清楚，但最终 Invocation Eligibility Authority 尚未冻结。**
   **来源：Q9 / R9，Q33 / R33**
4. **Embedded Mode 对 Product Surface Candidate 的 Cohesion 构成实质挑战。**
   Session、Conversation、UI、Login、Human Review Surface 等均可能由外部法院 Host 拥有，稳定留下的可能主要是 Integration Contract。
   **来源：Q10 / R10**
5. **Capability Governance 与 Side-effecting Tool Runtime 的模块合并缺少足够 Cohesion。**
   两者 Failure、Success、State、Retry、Recovery 和 Security Semantics 明显不同，仅共享 Catalog / Resolution / Invocation Framework。
   **来源：Q12 / R12**
6. **Long-term Memory 的一级 Module 必要性未成立。**
   Simple QA、Complex Legal Analysis、Ephemeral Specialist 在删除 Long-term Memory 后仍可成立；Memory 可能退化为可替换 Context Provider。
   **来源：Q15 / R15**
7. **Infrastructure & Persistence 的 Logical Module 身份受到挑战。**
   PostgreSQL、Queue、Checkpoint、Object Store、Vector/Graph Store、Backup/DR 可以共享 Platform Ownership，却没有统一的业务状态机与恢复语义。
   **来源：Q31 / R31**
8. **当前 10-Module Candidate 将“Contract 必须存在”与“Zuno 必须拥有独立 Module”混在一起的风险尚未解除。**
   Native Runtime、Long-term Memory、Persistent Multi-Agent、Generic Tool Execution 等本身仍属于 conditional / externalizable responsibility。
   **来源：Q32 / R32**

---

## FREEZE BLOCKERS

1. **Simple Answer / Invocation 的最终组合 Decision Authority 未冻结。**
   Security、Knowledge、Capability、Model 等底层 Owner 虽然明确，但当前没有唯一 Owner 能正式宣布“请求允许执行”以及“普通答案允许返回”。这同时暴露 Generic Host Simple QA 与 Native Runtime 强制约束之间的不一致。
   **来源：Q2 / R2，Q9 / R9，Q33 / R33**
2. **Canonical Domain Object Set 尚未收敛。**
   `Event / Conflict / Dispute / Fact / LegalIssue` 到底只是 Proposal / Derived View，还是可以成为 Canonical Domain State，目前 Baseline 内存在冲突。该差异直接影响 Admission、Version、Persistence、Dependency 与 Staleness。
   **来源：Q4 / R4**
3. **Historical Citation Authority 未冻结。**
   已 Admission 的 WorkProduct 不能因为 Knowledge Provider、Chunk、Index 或 CitationLineage Store 被替换就失去原文回溯能力，但当前没有冻结一个可以跨 Knowledge 生命周期长期存活的 Canonical Historical Citation Artifact / Authority。
   **来源：Q5 / R5，Q34 / R34**
4. **Cross-store Retention / Delete / Legal Hold 的最终 Policy Authority 未冻结。**
   Memory Delete、Runtime History、Trace Retention、Durable Audit、Domain History 发生策略冲突时，目前不能回答最终哪一个 Policy Authority 生效。
   **来源：Q16 / R16，Q35 / R35**
5. **Formal Admission 与 Runtime Step Completion 之间缺少 Durable Causation Invariant。**
   `FindingVersion V7` 的存在不能证明它就是 `Run R / Step S / Proposal P` 的结果；现有 Envelope 字段不足以自动构成这种证明。没有 durable `Step → Admission → DomainVersion` 因果事实，就无法安全处理 Domain Commit / Checkpoint 双写故障。
   **来源：Q24 / R24，Q25 / R25，Q36 / R36**
6. **Published WorkProduct 的失效传播链未闭合。**
   当前只能明确 Domain 中“V3 已 stale”；尚未冻结“失效通知是否已发送”“Consumer 是否确认知晓”的长期事实 Owner、传播责任和 acknowledgement 语义。
   **来源：Q26 / R26，Q37 / R37**
7. **Critical Reconstruction 的最小 Durable Fact Set 未冻结。**
   已经明确 Trace 不能替代 Durable Facts，但当前仍无法完整说明高风险 Tool Run 至少必须保留哪些 Action、Authorization、Approval、Audit、Effect 等 durable artifacts，才能在 Telemetry 全丢失后重建“执行了什么、为什么允许、现实世界发生了什么”。
   **来源：Q28 / R28，Q38 / R38**
8. **Product Surface & Agent Portfolio 作为独立 Logical Module 尚未通过 Freeze Test。**
   Embedded Mode 下大部分 Product Surface 可以由 Generic Host 承担，当前稳定剩余责任与独立 Module 的 Cohesion 尚未证明。
   **来源：Q10 / R10**
9. **Capability / Skill 与 Side-effecting Tool Runtime 当前合并边界未通过 Freeze Test。**
   两者没有共享足够强的状态、失败与恢复不变量来证明应当冻结为一个 Logical Module。
   **来源：Q12 / R12**
10. **Memory & Context 作为一级 Logical Module 的必要性尚未成立。**
    本轮已经证明核心 E2E 可以在无长期 Memory 情况下成立，而长期 Memory 仍可能完全由 Provider/Host 提供。
    **来源：Q15 / R15**
11. **Infrastructure & Persistence 作为与 Domain/Knowledge 对等的 Logical Module 尚未通过 Cohesion Test。**
    当前更明确的是 Platform / Physical Responsibility，而非共享一套业务状态与 Failure Boundary 的模块。
    **来源：Q31 / R31**
12. **因此当前 10-Module Candidate 本身还不是稳定的 Final Module Map。**
    本轮仍在讨论“这个 Candidate 到底是不是 Module”“两个 Candidate 为什么合在一起”“哪些责任可以完全外置”，说明 `MODULE_DECOMPOSITION_GATE` 所要求的总体边界尚未稳定。
    **来源：Q32 / R32，以及 Q10 / R10、Q12 / R12、Q15 / R15、Q31 / R31**

---

## FACT GAPS

1. **Single Controller HA / takeover / fencing 的 Current 实现与运行证据尚不能由 Target 回答。**
   本轮已经关闭其目标架构原则，但是否当前仓库已完整实现并通过 failover/fencing 验证属于 Current Evidence 问题，不属于新的 Target Architecture Gap。
   **来源：Q18 / A18 / R18**
2. **本轮没有发现需要依赖历史项目事实才能决定上述 Freeze Blocker 的新问题。**
   当前主要阻塞来自 Target Ownership、Boundary 和 Recovery Contract，而不是“历史 Pilot 到底怎么实现”的事实缺失。

---

## MEASUREMENT GAPS

1. **Native Runtime 相对 Generic Host + Zuno Legal Backend 的额外价值仍需 A/B/C Benchmark 或 Integration Spike 验证。**
   本轮只证明 Runtime 应保留哪些不可外包 Contract，没有证明 Zuno 必须拥有完整 Native Runtime。
   **来源：Q1 / R1，Q23 / R23，Q32 / R32**
2. **Long-term Memory 对法律任务的增益仍需 Ablation / Eval。**
   Architecture 可以在没有长期 Memory 时成立，因此是否保留其额外复杂度属于 Measurement Gap。
   **来源：Q15 / R15**
3. **Specialist / Multi-Agent 相对普通 Parallel Step / LangGraph Subgraph 的额外收益仍需测量。**
   本轮保留了受控 Specialist 的语义可能性，但没有提供它相对更简单执行模型的质量、成本或恢复收益证明。
   **来源：Q20 / R20，Q23 / R23，Q32 / R32**

这些 Measurement Gap **不是**当前 Ownership / Recovery Freeze Blocker 的替代解释。

---

## MODULE BOUNDARY CONCERNS

### Product Surface

Embedded Mode 显著压缩其稳定责任。Session、Conversation、UI、Login、Review Surface 等均可能由 Host 承担；同时 `InvocationEligibility` 与 Simple Answer Final Decision 的最终 Authority 尚未冻结。
**来源：Q9 / R9，Q10 / R10，Q33 / R33**

### Legal Domain

Legal Domain 的“唯一 Canonical Commit Authority”原则经受住攻击，但当前 Canonical Object Set 尚有 ADR / Architecture 冲突；Historical Citation、Admission Causation 和 Published Result Invalidation 也尚未形成完整长期事实边界。
**来源：Q4 / R4，Q11 / R11，Q34 / R34，Q36 / R36，Q37 / R37**

### Knowledge

`Ingestion + Retrieval` 的责任 Cohesion 本轮成立；但 Knowledge-owned CitationLineage 与 Domain-owned historical WorkProduct citation authority 的长期边界仍未闭合。
**来源：Q6 / R6，Q34 / R34**

### Agent Runtime

Single Controller、Replan Barrier、Join、Retry/Replan/Reconcile 与 LangGraph reuse 原则基本稳定；但 Simple QA 不一定进入 Native Runtime，且 Formal Admission Step 的 durable completion causation 尚未闭合。Native Runtime 本身的必要性仍需验证。
**来源：Q18–Q23 / R18–R23，Q36 / R36，Q32 / R32**

### Capability / Tool

这是本轮受到最强 Cohesion 挑战的候选之一。Capability Proposal 与 External Effect 拥有不同成功定义、状态机、Security、Retry、Recovery 和 Reconciliation 需求，目前共享 Provider Framework 不足以证明共同 Logical Module。
**来源：Q12 / R12**

### Memory

作为“非权威、可遗忘、跨 Run context”的概念仍成立，但独立一级 Module 的必要性没有成立；同时跨 Store Delete / Retention / Legal Hold Authority 尚未闭合。
**来源：Q15 / R15，Q16 / R16，Q35 / R35**

### Security

Policy Decision Authority + Distributed Enforcement 原则经受住攻击。但跨 Memory / Runtime / Trace / Audit / Domain 的 Retention、Deletion 与 Legal Hold 冲突尚缺最终治理 Authority。
**来源：Q17 / R17，Q35 / R35**

### Observability

OTel / LangSmith 作为可替换 Telemetry / Eval Provider 的边界成立，`Telemetry != Durable Audit` 也成立；但 Critical Reconstruction 的最小权威 Durable Fact Set 尚未完全冻结。
**来源：Q28–Q30 / R28–R30，Q38 / R38**

### Infrastructure

作为 Platform / Physical Responsibility 的价值没有被否定；受到攻击的是它是否应该与 Domain、Knowledge 等以同样含义被冻结为一个 Logical Module。其内部各 primitive 并不存在统一业务状态机。
**来源：Q31 / R31**

---

## PRESERVED PRINCIPLES

- **Single Controller = 每个 Run 的单一逻辑控制权，不等于单进程。**
  **Q18 / R18**
- **Domain State != Runtime Checkpoint。** Checkpoint 不能证明 Canonical Business Commit。
  **Q24–Q25 / R24–R25，Q36 / R36**
- **LLM / Specialist / Capability 输出 Proposal，不得直接 Canonical Commit。**
  **Q3 / R3，Q11 / R11，Q21 / R21**
- **Retry != Replan != Reconcile。**
  执行瞬时失败、计划假设失效和外部现实状态未知必须分别处理。
  **Q7 / R7，Q14 / R14，Q27 / R27**
- **Unknown External Effect 不允许 Blind Retry。**
  **Q7 / R7**
- **Approval 不能脱离当前 Action Version、参数、资源与 Security 条件永久有效。**
  **Q8 / R8**
- **Security Decision 与资源侧 Enforcement 分离。**
  **Q14 / R14，Q17 / R17**
- **Replan 后旧 Branch Result 不能直接污染新 PlanVersion。**
  **Q19 / R19**
- **Join 首层优先 deterministic / idempotent reducer；LLM Reflection 不能修改客观 Effect State。**
  **Q21 / R21**
- **LangGraph 已提供的 Checkpoint / Subgraph / Pending-write Recovery 能力优先复用，不重复自研。**
  **Q20 / R20，Q23 / R23**
- **Run Budget 与 Provider Usage Receipt 是不同 Ownership。**
  **Q13 / R13**
- **Knowledge Readiness 必须绑定 Scope / Query Requirement / Generation，而不是单个“知识库完成百分比”。**
  **Q6 / R6**
- **Telemetry / LangSmith Trace != Durable Audit。**
  Trace 可以 Sampling、Redaction、Delivery Failure；Mandatory Audit 不能依赖它成为事实源。
  **Q29 / R29，Q38 / R38**
- **Offline Release Eval != 单次 Runtime Result Admission Gate。**
  **Q30 / R30**
- **Contract 必须存在 != Zuno 必须自建对应 Runtime / Module。**
  Reuse、Externalize 和 Delete 仍然是有效选择。
  **Q23 / R23，Q32 / R32**

---

## RED RECOMMENDATION

**READY_FOR_MAIN_JUDGMENT**

Round 02 的 Red Q/A/R 已经穷尽到足以形成判断材料。现有未解决项中有多个真实 Freeze Blocker，但它们已经被明确识别并定位，不再需要通过新增 Q39+ 才能确认其性质。

`READY_FOR_MAIN_JUDGMENT` **不表示 Architecture Accepted，也不表示 Overall Architecture Frozen。**

**FOLLOW_UP_REQUIRED:**
NO

**RED_QAR_STATUS:**
COMPLETE

# MAIN JUDGMENT — ROUND 02


正式结论：

ROUND_OUTCOME:
ACCEPTED_WITH_REQUIRED_ARCHITECTURE_REVISION


QAR_STATUS:
COMPLETE


RED_FINDINGS:
ACCEPTED_AS_REVIEW_INPUT


OVERALL_ARCHITECTURE_FREEZE:
NOT_YET


ARCHITECTURE_REVISION_REQUIRED:
YES


MODULE_BOUNDARY_DECISION:
TARGET_DIRECTION_ACCEPTED_PENDING_CANONICAL_REVISION


MODULE_DECOMPOSITION_GATE:
NOT_OPEN


原因：

Round 02 没有推翻 Zuno 的核心产品与架构方向，
但证明当前 canonical architecture
仍缺少若干跨边界 Ownership、
Durable Recovery Invariant
以及稳定 Module Taxonomy。

这些问题已经不需要继续 Q39+，
而应由 Main Judgment 做架构裁决，
再通过单独的 Canonical Architecture Revision
落实。


==================================================
五、Main Judgment — Accepted Principles
==================================================

正式接受以下经 Round 02 保留下来的原则。


1. Domain State 与 Runtime State 分离

PostgreSQL 中的 Canonical Domain State
和 LangGraph Checkpoint / Runtime Control State
是不同事实。

Checkpoint 不能证明 Domain Commit。


2. Proposal != Canonical Fact

LLM、Specialist、Knowledge、
Capability Provider、Tool Observation
只能产生：

Proposal
Candidate
Observation
Reference
Receipt

不能直接提交 Canonical Legal Result。


3. Retry != Replan != Reconcile

执行方式仍正确、只是瞬时失败：

Retry。

计划依赖、假设或 Capability 已失效：

Replan。

现实世界 Effect 是否发生未知：

Reconcile。


4. Unknown External Effect 禁止 Blind Retry。


5. Single Controller 表示：

每个 Run 只有一个有效逻辑控制权，

不是：

全系统只有一个进程。


6. LangGraph 原生：

Checkpoint
Subgraph
Pending Writes
Parallel Execution
Reducer

优先复用。

Zuno 不重复建设框架已经可靠提供的控制能力。


7. Security Decision Authority
与 Resource-side Enforcement 分离。


8. Telemetry / LangSmith / OTel
不等于 Durable Audit。


9. Offline Release Eval
不等于 Runtime Result Eligibility。


10. Contract 必须存在
不代表 Zuno 必须自建对应：

Module
Runtime
Provider
Network Service。


==================================================
六、Architecture Decision 01
Simple QA / Invocation / Publication
==================================================

ACCEPTED。


旧原则：

“任何任务都不能绕过
Plan / Trace / Budget / AnswerPolicy / RunOutcome”

必须在下一次 canonical revision 中收窄。


新原则：

只有进入：

Zuno Native Agent Runtime

的任务，

才必须满足 Native Runtime 的：

Plan
Budget
AnswerPolicy
RunOutcome
Runtime Trace / Control requirements。


Host-owned Simple QA：

可以完全不进入 Zuno Native Runtime。


Simple QA 可以采用：

Question
→ Scope / Authorization
→ Knowledge Readiness
→ Retrieval
→ Grounded Answer
→ Answer Eligibility
→ Response


不默认需要：

Dynamic Plan
Multi-Agent
Reflection
Long-term Memory
GraphRAG。


--------------------------------------------------
Final Decision Authority
--------------------------------------------------

“是否允许执行请求”

和：

“是否允许发布普通答案”

是两个不同决定。


最终组合 Decision
属于：

Application / Integration Boundary。


它消费各 Canonical Owner 的 typed decisions：

Security
→ Authorization Decision

Knowledge
→ Readiness / Evidence Decision

Capability
→ Capability Eligibility

Model Gateway
→ Provider / Model Eligibility

Runtime when applicable
→ Budget / Run Control State


Application / Integration
只拥有：

composition decision。


它不得重新拥有或重新计算：

Security Fact
Knowledge Fact
Model Fact
Domain Fact。


--------------------------------------------------
Publication Authority
--------------------------------------------------

最终发布答案的边界
拥有 publication authority。


如果 Zuno 发布：

Zuno Application / Integration Boundary
拥有最终 Answer Publication Decision。


如果 Generic Host 发布：

Host 拥有最终 UI / Response Publication。


Zuno 只能提供：

typed result
eligibility evidence
citation
policy refs


不能宣称控制外部 Host
最终显示了什么。


==================================================
七、Architecture Decision 02
Canonical Legal Domain Kernel
==================================================

ACCEPTED。


ADR-0008 的 Minimal Domain Kernel
作为 canonical direction。


第一阶段 Canonical Domain Kernel：

Matter
DocumentVersion
Claim
Evidence
Finding
HumanDecision
WorkProduct


以下对象默认不是新的 Canonical Aggregate：

Fact
Event
Conflict
Dispute
LegalIssue
StatuteVersion
LegalElement
ApplicableLaw
SimilarCase


它们默认属于：

Typed Proposal
Projection
Derived View
Capability Provider Output。


只有未来证明具有独立：

Identity
Version
Provenance
Ownership
Mutation Authority
Dependency
Staleness
Review
Audit

才允许升级为 Canonical Domain Object。


下一次 canonical architecture revision
必须消除当前 Architecture
与 ADR-0008 的冲突。


==================================================
八、Architecture Decision 03
Historical Citation Authority
==================================================

ACCEPTED。


正式 WorkProduct
不得把当前 Knowledge Projection
作为历史引用唯一依赖。


冻结两个不同概念：


Knowledge-owned:

CitationLineage


回答：

系统当时如何：

retrieve
rerank
select
form citation。


Domain-owned:

Historical Citation Binding


回答：

某个已经正式 Admission 的
WorkProductVersion

究竟引用了：

哪一个 DocumentVersion
哪一个 immutable source
哪一个 stable source span。


Formal WorkProduct Admission
必须保留足够稳定的历史 Citation Binding。


至少语义上绑定：

DocumentVersion

immutable source reference / hash

stable source location / span

source representation identity / hash

必要 citation evidence hash


Knowledge CitationLineage：

可以作为 provenance reference，

但不能成为：

Historical WorkProduct 唯一生存依赖。


禁止：

Chunk ID
Vector ID
Graph Node ID

成为长期唯一 Citation Authority。


==================================================
九、Architecture Decision 04
Global Data Lifecycle Policy
==================================================

ACCEPTED。


Delete Memory

不等于：

Global Physical Erasure。


冻结：

Security & Governance

拥有跨存储：

Retention
Deletion
Legal Hold
Compliance Exception

的最终：

Effective Lifecycle Policy Decision。


各 Store：

Memory
Runtime
Domain
Audit
Observability
Infrastructure

是：

Enforcement Owner。


不是：

最高 Policy Authority。


重要不变量：

Retention
does not imply
Recall Eligibility。


Memory Delete 后：

Future Memory Recall
必须被禁止。


但：

Runtime History
Audit
Domain History

是否必须继续保留，

由当前有效的：

Retention
Legal Hold
Audit
Compliance Policy

决定。


保留下来的历史副本
不得因此重新成为：

Recallable Memory。


下一次 canonical revision
需要将 ADR-0003 已有 Audit-specific：

retention_policy_ref
legal_hold_policy_ref

提升为统一 lifecycle policy boundary，

但本任务不要修改 ADR。


==================================================
十、Architecture Decision 05
Formal Admission Causation Invariant
==================================================

ACCEPTED。


冻结全局不变量：

如果一个 Step 的完成条件包含
Formal Domain Admission，

那么：

没有 durable Admission Causation Fact，

Runtime 就不能宣布：

Step = COMPLETED。


推荐 canonical concept：

AdmissionReceipt

但具体 Contract 名称
由后续 canonical revision / ADR
正式冻结。


语义必须证明：

Step
→ Proposal
→ Domain Admission
→ resulting Domain Version


至少必须能够关联：

run identity

plan version

step run identity

proposal / admission identity

idempotency identity

expected prior domain version

resulting domain version。


--------------------------------------------------
Atomicity Boundary
--------------------------------------------------

Domain mutation

和：

证明该 Domain mutation 的 Admission Receipt

必须在：

同一个 Domain transactional durability boundary

内提交。


不要求：

PostgreSQL
↔
LangGraph Checkpointer

之间建立 2PC。


--------------------------------------------------
Recovery
--------------------------------------------------

如果：

Domain Commit 成功
Receipt 成功
Checkpoint 失败

Runtime 恢复后：

读取 Receipt
并修复自己的 Control State。


如果：

Checkpoint 显示成功
但不存在匹配 Admission Receipt

不能推断 Domain Admission 已完成。


如果数据库存在更高 DomainVersion：

但 causation identity 不匹配，

也不能认作当前 Step 的结果。


这正式取代模糊的：

“Domain wins”

作为完整 Recovery 判断。


==================================================
十一、Architecture Decision 06
Published Result Invalidation
==================================================

ACCEPTED。


必须区分三个不同事实：


A. Domain Invalidation Truth

例如：

WorkProduct V3 = STALE


Canonical Owner:

Legal Domain。


Consumer 是否在线
不影响该事实成立。


B. Invalidation Delivery Fact

例如：

PENDING
SENT
FAILED
RETRYING


Owner:

Application / Integration。


C. Consumer Acknowledgement Observation

例如：

ACKNOWLEDGED
NO_ACK
UNKNOWN


Owner:

Application / Integration。


它表示：

Zuno 观察到远端 Consumer
是否返回 acknowledgement。


它不是：

Consumer 内部世界的绝对事实。


禁止把三者压成：

WorkProduct.status = stale


一个字段。


--------------------------------------------------
Delivery Model
--------------------------------------------------

Target 支持：

push invalidation

+

pull current-validity query。


Consumer 离线：

不得阻塞 Domain staleness 成立。


恢复在线后：

可以：

接收 retry delivery

或：

主动查询 WorkProduct 当前有效状态。


==================================================
十二、Architecture Decision 07
Critical Reconstruction Boundary
==================================================

ACCEPTED。


不创建一个新的万能：

CriticalReconstructionBundle

作为默认 architecture object。


冻结的是：

Durable Reconstruction Chain Invariant。


高风险 Tool / External Effect
必须能够通过 Durable Facts
重建至少四个问题：


做了什么？

为什么允许？

谁批准？

现实世界发生了什么？


权威事实来自：


Prepared Action / Tool Attempt facts

Security Authorization Decision

Approval Decision when required

Mandatory Audit Persistence

Effect Receipt

Reconciliation Receipt when needed

Domain Admission Receipt when applicable。


这些通过稳定：

action identity
action hash
run / step causation
idempotency identity

关联。


LangSmith / OpenTelemetry：

只能是：

Diagnostic View
Trace Projection
Correlation
Evaluation Input
Visualization


不能成为：

Canonical Reconstruction Source。


如果 Durable Audit 丢失，

完整 LangSmith Trace

不能自动升级为：

同等级 Audit Authority。


Secret Material
不得为了 Reconstruction
而写入 Trace / Audit / ordinary DB。


可以持久保存：

credential version reference
action hash
canonical non-secret arguments
tool definition version
operation identity。


==================================================
十三、Module Boundary Decision
==================================================

Main Judgment 接受：

当前 10 Candidate
不作为 Final Module Map。


Target 方向收敛为：

9 个 Logical Responsibility Modules

+

1 个 Platform / Infrastructure Responsibility Layer

+

Optional Context Provider Boundary。


--------------------------------------------------
Target 9 Logical Modules
--------------------------------------------------

01 Application & Integration

02 Legal Domain & Work Product

03 Knowledge & Evidence

04 Agent Runtime & Control

05 Capability & Skill

06 Tool Runtime & Effects

07 Model Gateway

08 Security & Governance

09 Observability & Evaluation


注意：

这是：

TARGET MODULE DIRECTION

已由 Main Judgment 接受。


但是：

Canonical Architecture 还未 Revision。


所以：

MODULE_DECOMPOSITION_GATE
继续：

NOT_OPEN。


只有 canonical architecture
完成相应 Revision + Verification 后，

才允许打开 Gate。


==================================================
十四、Module Decision — Application & Integration
==================================================

原候选：

Product Surface & Agent Portfolio


不直接保留。


重构为：

Application & Integration。


它负责稳定的：

External Task Intake

Agent Definition / Agent Version surface

Invocation Decision Composition

Response Publication

Generic Host / Court Integration

WorkProduct Delivery

Invalidation Delivery

Consumer Ack Observation。


UI
Session
Conversation
Login
Workbench

不是这个逻辑模块必须自行拥有的能力。


它们可以：

由 Zuno 实现

或：

由 Generic Host / Court System 提供。


Embedded Mode
因此成为 first-class deployment / integration mode。


==================================================
十五、Module Decision — Legal Domain
==================================================

保留：

Legal Domain & Work Product。


它是：

Canonical Legal Business State
的唯一 Owner。


但按照 ADR-0008
收缩 Canonical Kernel。


它同时拥有：

Historical WorkProduct Citation Binding

Domain Invalidation Truth

Formal Admission durability fact。


==================================================
十六、Module Decision — Knowledge
==================================================

保留：

Knowledge & Evidence。


Ingestion + Retrieval
继续作为同一 Logical Responsibility。


原因：

共同拥有：

DocumentVersion input interpretation
KnowledgeGeneration
Scope-sensitive Readiness
Retrieval
Evidence Candidate
CitationLineage。


OCR
Embedding
Graph Build
Vector Store

可以是不同 Worker / Provider。


逻辑模块
不等于物理服务。


==================================================
十七、Module Decision — Runtime
==================================================

原：

Agent Runtime & Multi-Agent Orchestration


改为：

Agent Runtime & Control。


核心责任：

Single Controller

Plan DAG

Step Execution

Budget

Parallel Dispatch

Join

Retry

Replan

Reconcile

Interrupt

Checkpoint / Recovery Control。


Specialist / Multi-Agent：

只是可选执行方式。


不再作为：

模块存在的核心理由。


Native Runtime 仍然：

CONDITIONAL
MEASUREMENT-GATED。


Host-owned Simple QA
不需要进入该模块。


==================================================
十八、Module Decision — Capability / Tool Split
==================================================

ACCEPTED。


当前：

Capability / Skill & Tool Runtime

必须拆成两个逻辑责任。


05 Capability & Skill


回答：

系统能够完成什么专业分析能力。


典型：

EVENT_EXTRACTION
EVENT_ALIGNMENT
CONFLICT_DETECTION
FACT_ARTICLE_MAPPING
LEGAL_APPLICABILITY
SIMILAR_CASE_RETRIEVAL
EVIDENCE_REASONING


主要输出：

Proposal
Candidate
Observation
Reference。


06 Tool Runtime & Effects


回答：

系统如何安全执行
可能改变外部世界的操作。


主要责任：

Tool Definition

Prepared Action

Approval Binding

Tool Attempt

Idempotency

Effect Receipt

OUTCOME_UNKNOWN

Reconciliation。


核心理由：

Capability failure

与：

External Effect uncertainty

拥有不同：

success semantics
failure semantics
retry semantics
recovery semantics
security semantics。


因此不再冻结为同一个模块。


==================================================
十九、Module Decision — Memory
==================================================

ACCEPTED。


Memory & Context

不再作为：

first-class logical module。


降级为：

Optional Context Provider Boundary。


Working Context
Session Context

优先由：

Runtime / Host

管理。


Long-term Memory：

只有 Ablation / Eval
证明真实收益后
才允许提升复杂度。


Provider 可以是：

OpenViking
Generic Host
External Memory Provider
Zuno Adapter。


Memory Contract 可以存在，

不代表 Memory 必须成为一级模块。


==================================================
二十、Module Decision — Infrastructure
==================================================

ACCEPTED。


Infrastructure & Persistence

不再与：

Legal Domain
Knowledge
Runtime

以同一种意义称为：

Logical Business Module。


改为：

Platform / Infrastructure Responsibility Layer。


提供：

PostgreSQL primitives

Object Store

Queue / Worker primitives

Checkpoint adapter

CAS
Lease
Fencing
Clock

Vector / Graph / Lexical physical adapters

Cache

Backup / Restore

Network

Secret delivery

Release primitives。


上层逻辑模块：

通过 typed ports 使用 Platform。


Platform 不拥有：

Domain success

Knowledge success

Runtime success

Tool effect success。


--------------------------------------------------
ADR Conflict
--------------------------------------------------

ADR-0003 当前写有：

“Infrastructure 是逻辑模块”

因此后续 canonical revision
必须通过新的 ADR 或明确 superseding decision：

只 supersede ADR-0003
关于 Infrastructure taxonomy 的部分。


ADR-0003 中有效的：

Cross-module Contracts
Security Epoch
Audit durability
Receipt boundaries
Model Gateway contracts
Infrastructure primitives

继续保留。


本任务：

不得修改 ADR-0003。


==================================================
二十一、Module Decision — Model / Security / Observability
==================================================

以下保留一级逻辑责任：


Model Gateway


Security & Governance


Observability & Evaluation


但 Observability：

不得拥有：

Canonical Domain
Security Decision
Effect Truth
Mandatory Audit durability fact。


它消费并投影这些事实。


==================================================
二十二、Physical Deployment
==================================================

继续保留 ADR-0012。


Target 默认：

Python Modular Backend

+

Independent Workers where justified。


Logical Module：

不自动等于：

Process
Container
Database
Network Service
Microservice
Team。


Network Service 拆分继续：

EVIDENCE-GATED。


不得因为新的 9-module map

生成：

9 个微服务。


==================================================
二十三、Measurement Gaps
==================================================

以下不因为 Main Judgment
而变成已证明能力。


继续保留 Measurement Gap：


1. Generic Host

vs

Generic Host + Zuno Legal Backend

vs

Zuno Native Runtime


A/B/C Benchmark。


2. Long-term Memory Ablation。


3. Specialist / Multi-Agent

vs

Parallel Step / LangGraph Subgraph

增益验证。


4. Runtime HA / fencing / takeover
Current Evidence。


这些 Measurement Gap：

不阻止 Target Responsibility Boundary
被定义，

但阻止：

production ready
measured advantage
runtime necessity

等结论。


==================================================
二十四、Rejected / Not Accepted
==================================================

Main Judgment 明确不接受：


1. 当前 10 Candidate
直接冻结为最终模块。


2. 所有请求都必须启动 Native Runtime。


3. 所有法律抽取对象
自动成为 Canonical Domain Entity。


4. Chunk / Index / CitationLineage ID
作为 WorkProduct 长期唯一引用依据。


5. Memory Delete
等于所有历史副本立即物理删除。


6. DomainVersion 存在
就证明某 Step 已完成。


7. WorkProduct.status=STALE
同时代表：

Domain invalidation
delivery
consumer awareness。


8. LangSmith / OTel Trace
作为 Durable Audit 的替代事实源。


9. Capability 与 Side-effecting Tool Runtime
继续因为“都能被 Agent 调用”而合并。


10. Memory 因为存在 Contract
就必须是一级 Module。


11. Infrastructure 因为重要
就必须是与 Domain 同类的 Logical Module。


12. 9 Logical Modules
自动对应 9 Microservices。


==================================================
二十五、Main Judgment 后状态
==================================================

Round 02 History metadata
更新为等价状态：


status: ARCHIVED

qar_complete_through: Q38

qar_packet_complete: YES

follow_up_status: COMPLETE

red_findings_status: FINAL

main_judgment: COMPLETED

main_judgment_outcome:
ACCEPTED_WITH_REQUIRED_ARCHITECTURE_REVISION

architecture_revision:
COMPLETED

architecture_revision_sha:
7ce987f5d747395d4926622f42ac4f0013bc53ed

canonical_revision_gate:
PASS

overall_architecture_freeze:
YES

module_decomposition_gate:
OPEN


Architecture Baseline：

继续保持：

a9fa3834c1dd95bdc13caa85b7188d49fc55b1b5


Archive Task Base：

不要覆盖历史值。


可以增加：

main_judgment_recorded_at
main_judgment_recording_base_sha

如果当前 History Governance
已有同类字段。


不要发明不必要 schema。

---

# ARCHITECTURE REVISION AND FREEZE RESULT

CANONICAL_REVISION_SHA:
7ce987f5d747395d4926622f42ac4f0013bc53ed

CANONICAL_REVISION_GATE:
PASS

OVERALL_ARCHITECTURE_FREEZE:
YES

TARGET_LOGICAL_MODULE_COUNT:
9

MODULE_DECOMPOSITION_GATE:
OPEN

FREEZE_SCOPE:
TARGET_ARCHITECTURE

IMPLEMENTATION_STATUS:
NOT_IMPLIED

PRODUCTION_READINESS:
NOT_ESTABLISHED

MEASUREMENT_STATUS:
OPEN

本次 Freeze 只表示总体责任、Owner、状态边界、Recovery、Security、Build / Buy 和模块分类已经稳定到可以进入 Module Design。它不表示所有 Contract、Migration、Runtime、Benchmark 已完成，也不表示 Production Ready、Quality Proven 或 Measured Advantage Proven。
