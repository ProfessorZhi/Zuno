# Round #013 — Batch 002 — Red

Status: `FROZEN_AND_ARCHIVED`  
Question count: **100**

Batch 002 is reweighted from Batch 001 findings. It attacks personal implementation depth and naturally derived backend fundamentals rather than repeating the broad Target architecture review.

## A. Tool / MCP / Agent implementation deep dive

### B2-Q001
- **claim_under_test:** PF-032 / resume Tool Calling refactor.
- **red_question:** 你先画出改造前的调用链：用户请求进来以后，`GeneralAgent`、`MCPAgent-as-Tool`、MCP Server、具体 Tool 之间分别是谁调用谁？每一跳输入输出是什么？
- **red_hidden_intent:** Force concrete pre-refactor call topology.
- **expected_evidence:** Resume + PF-032; exact call-chain detail if preserved.

### B2-Q002
- **claim_under_test:** Same refactor.
- **red_question:** 改造后“直接绑定具体 MCP Tools”到底少掉了哪一层？少掉的只是一个 Python wrapper，还是少了一次模型决策 / schema 转换 / context 回注？
- **red_hidden_intent:** Distinguish structural simplification from cosmetic wrapper removal.
- **expected_evidence:** Historical implementation detail.

### B2-Q003
- **claim_under_test:** Same refactor.
- **red_question:** 你为什么没有保留 MCPAgent 作为一个 Specialist Agent，只把它做薄？为什么一定要让 GeneralAgent 看见具体 Tool schema？
- **red_hidden_intent:** Test alternative analysis.
- **expected_evidence:** Design decision or explicit unknown.

### B2-Q004
- **claim_under_test:** Direct Tool binding.
- **red_question:** GeneralAgent 直接绑定多个 MCP Tools 后，Tool 数量增长会不会让 prompt/schema 变大、工具选择变差？你当时怎么控制，还是根本没测？
- **red_hidden_intent:** Expose scalability/trade-off of direct exposure.
- **expected_evidence:** Historical implementation and measurement boundary.

### B2-Q005
- **claim_under_test:** MCP user config injection.
- **red_question:** “调用期注入用户级 MCP 配置”具体发生在什么 middleware/hook 上？为什么不在 Agent 初始化时注入？
- **red_hidden_intent:** Test lifecycle choice.
- **expected_evidence:** PF-032-level code detail.

### B2-Q006
- **claim_under_test:** User config isolation.
- **red_question:** 两个用户并发调用同一个 GeneralAgent 实例，如果 MCP config 是调用期注入，怎样保证不会串用户？是参数显式传递、ContextVar、request-local state 还是复制 Tool 实例？
- **red_hidden_intent:** Probe concurrency/isolation.
- **expected_evidence:** Exact implementation or unknown.

### B2-Q007
- **claim_under_test:** User config isolation.
- **red_question:** 如果用户配置缺失、配置格式错误、某个 MCP Server 不存在，当时是 fail fast、跳过该 Tool、还是回到 ReAct fallback？
- **red_hidden_intent:** Test failure semantics.
- **expected_evidence:** Exact historical behavior.

### B2-Q008
- **claim_under_test:** Tool discovery.
- **red_question:** 具体 MCP Tool schema 是什么时候发现的？应用启动、Agent 初始化、每次请求还是调用前？Server schema 变化时历史实现怎么刷新？
- **red_hidden_intent:** Test discovery/version mechanics.
- **expected_evidence:** Historical implementation or explicit gap.

### B2-Q009
- **claim_under_test:** Tool naming.
- **red_question:** 多个 MCP Server 暴露同名 Tool 时怎么消歧？你们有没有 namespace 规则？如果没有，custom MCP name recursion 的修复会不会引入别的 collision？
- **red_hidden_intent:** Probe naming design beyond one bug.
- **expected_evidence:** Implementation detail.

### B2-Q010
- **claim_under_test:** Custom MCP recursion bug.
- **red_question:** 不看代码的话，请你按“输入字符串 → 哪个函数 → 递归条件 → 为什么无法收敛 → 修复后 invariant”完整复现 custom MCP name 自递归问题。
- **red_hidden_intent:** Verify actual debugging memory.
- **expected_evidence:** PF-032 supports bug/fix; exact mechanics may be missing.

### B2-Q011
- **claim_under_test:** Custom MCP recursion fix.
- **red_question:** 你怎么证明修复不是“碰巧对这一个名字有效”？有没有 property/invariant，比如 normalize(normalize(x)) = normalize(x)？
- **red_hidden_intent:** Test test-design maturity.
- **expected_evidence:** Regression assertion or unknown.

### B2-Q012
- **claim_under_test:** Weather parameter parsing bug.
- **red_question:** “高德天气自然句 naive city extraction”具体错误例子是什么？比如“帮我查南京明天天气”当时解析成了什么？
- **red_hidden_intent:** Demand concrete repro input/output.
- **expected_evidence:** Historical bug detail.

### B2-Q013
- **claim_under_test:** Weather parsing fix.
- **red_question:** 为什么不让模型直接按 MCP schema 产出 `city` 参数，而要在 Workspace 层做解析？这是不是重复逻辑？
- **red_hidden_intent:** Test layering trade-off.
- **expected_evidence:** Historical decision or gap.

### B2-Q014
- **claim_under_test:** Weather regression test.
- **red_question:** 你的 regression test 是固定 `maps_weather(city="南京")` 这种 deterministic 断言，还是完整跑一次 LLM Tool Calling？为什么选这种粒度？
- **red_hidden_intent:** Test deterministic testing strategy.
- **expected_evidence:** Historical test artifact.

### B2-Q015
- **claim_under_test:** Direct route / ReAct fallback.
- **red_question:** 给我三个例子：必须 direct route、必须 ReAct、两者都可但你选择 direct 的任务。每个例子的判定条件是什么？
- **red_hidden_intent:** Force route semantics beyond buzzwords.
- **expected_evidence:** Historical route logic.

### B2-Q016
- **claim_under_test:** Direct route safety.
- **red_question:** deterministic direct route 如果调用的是有副作用 Tool，会不会绕过 Agent 的 reasoning/approval？当时实现有没有风险控制，还是今天 Target 才补这层？
- **red_hidden_intent:** Current/Target security split.
- **expected_evidence:** Historical Tool path + later Effects/Security Target.

### B2-Q017
- **claim_under_test:** ReAct fallback.
- **red_question:** fallback 是在 direct route 无法匹配时才进入 ReAct，还是 direct route 调用失败后也会进入？如果是后者，副作用 Tool 会不会重复执行？
- **red_hidden_intent:** Probe retry/route interaction.
- **expected_evidence:** Exact historical route behavior.

### B2-Q018
- **claim_under_test:** Tool selection.
- **red_question:** 父代码里如果存在 Tool selector scaffolding，但 middleware 没真正挂上，你面试时能说“我们移除了二次 selector model”吗？准确说法是什么？
- **red_hidden_intent:** Prevent overclaim from dormant scaffolding.
- **expected_evidence:** PF-032 bounded wording.

### B2-Q019
- **claim_under_test:** Tool schema exposure.
- **red_question:** MCP Tool schema 进入模型上下文前有没有做裁剪、类型转换或 description 重写？如果 schema 很长，你怎么处理？
- **red_hidden_intent:** Test schema plumbing details.
- **expected_evidence:** Historical implementation or unsupported.

### B2-Q020
- **claim_under_test:** Tool result handling.
- **red_question:** Tool result 回给模型时是原样字符串、结构化 JSON、还是做过 truncate/sanitize？这块 Zuno 和你 Coding Agent 的实现不要混。
- **red_hidden_intent:** Detect cross-project claim leakage.
- **expected_evidence:** Zuno-specific implementation only.

### B2-Q021
- **claim_under_test:** MCP server errors.
- **red_question:** MCP Server timeout、断连、返回 schema 不匹配时，历史 Zuno 的错误是怎样穿过 Tool → Agent → Workspace 返回用户的？
- **red_hidden_intent:** Test error propagation.
- **expected_evidence:** Historical path or gap.

### B2-Q022
- **claim_under_test:** Async / concurrency.
- **red_question:** 多个 Tool 并发调用时 GeneralAgent 有没有并发执行？如果有，结果顺序怎么合并；如果没有，为什么？
- **red_hidden_intent:** Test execution model depth.
- **expected_evidence:** Historical code detail.

### B2-Q023
- **claim_under_test:** Tool idempotency.
- **red_question:** 你本人 4 月那条 Tool Calling 链有没有 idempotency key？如果没有，面试官问“网络重试导致重复写外部系统怎么办”时，你怎么把历史实现和后来的 Target 分开？
- **red_hidden_intent:** Prevent backporting Effects Target.
- **expected_evidence:** PF-032 + Effects Target.

### B2-Q024
- **claim_under_test:** Observability.
- **red_question:** 这次 MCP refactor 有没有 trace/log 能证明请求走 direct route 还是 ReAct？如果排查一次错误调用，你看什么字段？
- **red_hidden_intent:** Test operability of owned code.
- **expected_evidence:** Historical trace/log detail or gap.

### B2-Q025
- **claim_under_test:** Performance outcome.
- **red_question:** 去掉 MCPAgent-as-Tool 理论上可能少一次模型调用。你真的测过 token/latency 吗？没测过的话，面试时能不能说“降低了开销”？
- **red_hidden_intent:** Enforce measurement honesty.
- **expected_evidence:** No unsupported metric claim.

### B2-Q026
- **claim_under_test:** Regression test value.
- **red_question:** 如果 regression tests 只验证函数输入输出，没有跑真实 MCP Server，它们能防住什么，防不住什么？
- **red_hidden_intent:** Test test-scope reasoning.
- **expected_evidence:** Test artifact scope or bounded answer.

### B2-Q027
- **claim_under_test:** Tool version drift.
- **red_question:** MCP Server 改了参数名，旧 regression 还绿，但真实调用失败。你今天会怎样设计 contract/version test？这能不能说成你当时已经做了？
- **red_hidden_intent:** Current vs proposed improvement.
- **expected_evidence:** Capability Target and historical limit.

### B2-Q028
- **claim_under_test:** Alternative architecture.
- **red_question:** 如果今天重做 4 月这段，你会继续让 GeneralAgent 直接看到所有 Tool，还是加 Tool retrieval / capability router？决定点是什么？
- **red_hidden_intent:** Test evolved judgment.
- **expected_evidence:** Current product strategy, not historical fabrication.

### B2-Q029
- **claim_under_test:** Build/Buy.
- **red_question:** MCP SDK 已经负责协议、discovery、执行。你本人那段代码真正“自研”的是什么？哪些只是 glue code？
- **red_hidden_intent:** Force honest ownership of integration layer.
- **expected_evidence:** PF-032 boundaries.

### B2-Q030
- **claim_under_test:** Resume prioritization.
- **red_question:** 如果面试官只给你 3 分钟讲这条 Tool Calling，你会选择“架构重构”“两个 bug”“user config injection”中的哪一个做主故事，为什么？
- **red_hidden_intent:** Test strongest evidence-backed narrative.
- **expected_evidence:** Resume/PF-032.

### B2-Q031
- **claim_under_test:** Personal code ownership.
- **red_question:** 两个历史 commit 都是你的 GitHub author/committer 就等于所有 diff 都是你做的吗？broad platform commit 里哪些部分不能认领？
- **red_hidden_intent:** Attack commit-level ownership inflation.
- **expected_evidence:** PF-032 bounded diff attribution.

### B2-Q032
- **claim_under_test:** Team review.
- **red_question:** 这两个改动有没有 code review、同事反馈或任务分配记录？没有的话，你如何证明“这是项目需要”而不只是自己改着玩？
- **red_hidden_intent:** Project-reality evidence.
- **expected_evidence:** Issue/review unknown.

### B2-Q033
- **claim_under_test:** Failure reproduction.
- **red_question:** 你能否在面试白板上写一个最小复现，证明旧 custom MCP name 会递归、修复后不会？如果 canonical docs 不够，你准备靠什么记住这个实现？
- **red_hidden_intent:** Interview readiness of personal task evidence.
- **expected_evidence:** Historical code/test if recovered.

### B2-Q034
- **claim_under_test:** Boundary to later Effects.
- **red_question:** 今天文档有 PreparedAction、EffectReceipt、Reconcile。你 4 月的 GeneralAgent/MCP 改造和这些对象之间是什么关系？有没有直接 lineage？
- **red_hidden_intent:** Stop retrospective ownership inflation.
- **expected_evidence:** PF-032 vs Target Effects.

### B2-Q035
- **claim_under_test:** Strongest technical lesson.
- **red_question:** 这段 Tool Calling 工作真正让你学到的一个可迁移工程原则是什么？不要回答“MCP 很方便”。
- **red_hidden_intent:** Test synthesis from real work.
- **expected_evidence:** Evidence-backed engineering insight.

## B. Context / Memory implementation deep dive

### B2-Q036
- **claim_under_test:** PF-029 `prepare_context()`.
- **red_question:** `GeneralAgent.prepare_context()` 的输入参数有哪些？它从哪里拿当前 task / scope / memory query 条件，最后返回什么结构？
- **red_hidden_intent:** Force function-level implementation detail.
- **expected_evidence:** PF-029 / historical PR.

### B2-Q037
- **claim_under_test:** Same-scope summary.
- **red_question:** “同 scope task summary”里 scope 的最小组成是什么？如果你现在说不出来，这条简历为什么还能写得这么具体？
- **red_hidden_intent:** Test evidence depth behind resume wording.
- **expected_evidence:** Exact scope predicate or honest gap.

### B2-Q038
- **claim_under_test:** Scope isolation.
- **red_question:** 两个 Task 属于同一 Workspace 但不同 Matter，summary 能互相读到吗？两个 Matter 属于同一用户呢？给出实际过滤规则。
- **red_hidden_intent:** Probe cross-matter leakage.
- **expected_evidence:** Historical predicate/tests.

### B2-Q039
- **claim_under_test:** Structured memory schema.
- **red_question:** `structured memory` 当时至少有哪些字段？status、source id、scope、content、version 里哪些真实存在，哪些是今天文档抽象？
- **red_hidden_intent:** Current/history schema distinction.
- **expected_evidence:** PF-029/030 or unknown.

### B2-Q040
- **claim_under_test:** APPROVED filter.
- **red_question:** 你是在 SQL/query 层过滤 `APPROVED`，还是加载后 Python 过滤？这会影响什么安全/性能语义？
- **red_hidden_intent:** Test concrete data path.
- **expected_evidence:** Historical implementation detail.

### B2-Q041
- **claim_under_test:** Approval lifecycle.
- **red_question:** `APPROVED` 之前有哪些状态？谁写 status？如果这个生命周期不是你做的，你的 slice 如何依赖它又不越权？
- **red_hidden_intent:** Ownership boundary.
- **expected_evidence:** Historical dependency / unknown.

### B2-Q042
- **claim_under_test:** Task summary source.
- **red_question:** Task summary 是 LLM 生成、规则摘要还是已有字段？生成失败时 `prepare_context()` 怎么办？
- **red_hidden_intent:** Test source/failure semantics.
- **expected_evidence:** Historical implementation.

### B2-Q043
- **claim_under_test:** Summary freshness.
- **red_question:** 原 Task 后来追加新消息，但旧 summary 没更新，Context Builder 如何知道 summary stale？当时做了吗？
- **red_hidden_intent:** Probe stale summary problem.
- **expected_evidence:** Historical implementation or target-only.

### B2-Q044
- **claim_under_test:** Source provenance.
- **red_question:** `source-id trace` 是写到 Context Pack item 上、日志里、还是单独表？它是为了 debug 还是会影响下游业务判断？
- **red_hidden_intent:** Clarify provenance implementation and authority.
- **expected_evidence:** PF-029 detail.

### B2-Q045
- **claim_under_test:** Source provenance.
- **red_question:** 如果一个 summary 合并了 10 条消息，source-id 是一个还是 10 个？以后原消息删除/更正怎么办？
- **red_hidden_intent:** Test provenance cardinality and lifecycle.
- **expected_evidence:** Historical contract or gap.

### B2-Q046
- **claim_under_test:** Context Pack policy.
- **red_question:** `Context Pack policy` 当时具体限制了什么：来源类型、最大条数、顺序、scope、approval、token？请把真实项和后来 Target 项分开。
- **red_hidden_intent:** Prevent vague “policy” claim.
- **expected_evidence:** PR/test artifacts.

### B2-Q047
- **claim_under_test:** Context ordering.
- **red_question:** task summary 和 structured memory 谁先进入 prompt？顺序会不会影响模型？你们有没有固定格式？
- **red_hidden_intent:** Test prompt assembly details.
- **expected_evidence:** Historical code detail.

### B2-Q048
- **claim_under_test:** Duplicate context.
- **red_question:** 同一个事实既在 task summary 又在 structured memory 里，Context Builder 会去重吗？不去重有什么风险？
- **red_hidden_intent:** Probe context quality.
- **expected_evidence:** Current slice or missing behavior.

### B2-Q049
- **claim_under_test:** Conflicting context.
- **red_question:** summary 说 A，APPROVED memory 说 not-A，当时谁优先？如果没有冲突机制，为什么还能安全注入两者？
- **red_hidden_intent:** Stress semantic conflict handling.
- **expected_evidence:** Historical behavior vs later Target.

### B2-Q050
- **claim_under_test:** Context failure isolation.
- **red_question:** Memory DB 查询失败时，Agent 请求整体失败还是降级为没有 Memory？这个选择会不会让用户在不知情下得到质量更差的结果？
- **red_hidden_intent:** Test failure/degradation policy.
- **expected_evidence:** Historical path or gap.

### B2-Q051
- **claim_under_test:** Context latency.
- **red_question:** 每次模型调用前都查 summary + memory，会增加多少数据库/网络开销？你测过吗？有没有 cache？
- **red_hidden_intent:** Measurement / performance reality.
- **expected_evidence:** Historical measurement or no claim.

### B2-Q052
- **claim_under_test:** Context token budget.
- **red_question:** 如果两类上下文加起来超过 context window，当时是截断、排序、报错还是让模型 API 失败？
- **red_hidden_intent:** Expose unimplemented budget control.
- **expected_evidence:** Historical behavior.

### B2-Q053
- **claim_under_test:** Context relevance.
- **red_question:** 除了 same-scope 和 APPROVED，你当时有没有 relevance ranking？如果没有，长期 Memory 多起来以后为什么不会把 Context 塞满？
- **red_hidden_intent:** Test scaling limitation.
- **expected_evidence:** Historical slice scope.

### B2-Q054
- **claim_under_test:** Memory review.
- **red_question:** 你简历写 review gate。这个 gate 是 UI 人工审核、后端 status check 还是测试中的 contract？具体哪部分是你实现的？
- **red_hidden_intent:** Clarify gate meaning.
- **expected_evidence:** PF-029 exact boundary.

### B2-Q055
- **claim_under_test:** Review bypass.
- **red_question:** 有没有代码路径可以绕过 review gate 直接写 APPROVED？如果没有证据，你能不能说“保证只有审核记忆进入模型”？
- **red_hidden_intent:** Test strength of guarantee.
- **expected_evidence:** Tests/constraints or bounded wording.

### B2-Q056
- **claim_under_test:** Post-turn write.
- **red_question:** PF-030 说有 post-turn write integration。模型输出后写的是什么：原对话、candidate memory、summary 还是事件？和你后来 PF-029 的 readback 是什么时间关系？
- **red_hidden_intent:** Test timeline and data flow.
- **expected_evidence:** PF-030 chain.

### B2-Q057
- **claim_under_test:** ContextOrchestrator.
- **red_question:** minimal `ContextOrchestrator` 和 `GeneralAgent.prepare_context()` 分别负责什么？为什么两层都需要？
- **red_hidden_intent:** Probe architecture detail.
- **expected_evidence:** PF-030 or gap.

### B2-Q058
- **claim_under_test:** Typed contracts.
- **red_question:** PF-030 提到 typed Context / scoped Memory contracts。typed 在这里解决了什么？只是 dataclass/Pydantic，还是防止来源/类型混用？
- **red_hidden_intent:** Test whether type abstraction had semantic value.
- **expected_evidence:** Historical design evidence.

### B2-Q059
- **claim_under_test:** Testing scope.
- **red_question:** `32 passed` 里至少说出三个最重要的测试场景：scope、approval、provenance 分别怎样构造正反例？
- **red_hidden_intent:** Test hands-on test ownership.
- **expected_evidence:** Focused tests.

### B2-Q060
- **claim_under_test:** Test robustness.
- **red_question:** 这些 focused tests 用真实 PostgreSQL / Memory store 还是 mock/in-memory？它们能证明什么，不能证明什么？
- **red_hidden_intent:** Evidence strength.
- **expected_evidence:** Test environment detail.

### B2-Q061
- **claim_under_test:** Context leakage.
- **red_question:** 如果测试只验证 same-scope 正例，有没有 cross-scope negative test？没有的话，最危险的隐私 bug 是什么？
- **red_hidden_intent:** Security testing depth.
- **expected_evidence:** Test artifact or gap.

### B2-Q062
- **claim_under_test:** Prompt injection.
- **red_question:** APPROVED memory 也可能包含恶意文本。你当时有没有将 memory 明确包成 data block、做 instruction stripping 或其他隔离？如果没做，今天该在哪层解决？
- **red_hidden_intent:** Historical vs target security design.
- **expected_evidence:** PF-029 + Security/Runtime Target.

### B2-Q063
- **claim_under_test:** Memory freshness.
- **red_question:** Memory 被批准以后，新的 DocumentVersion 推翻它。谁让它 stale？你的 `prepare_context()` 会不会继续读到它？
- **red_hidden_intent:** Test cross-owner invalidation gap.
- **expected_evidence:** Historical implementation vs target Domain authority.

### B2-Q064
- **claim_under_test:** OpenViking relation.
- **red_question:** OpenViking 接入和 PF-030/PF-029 这条 V2 Context/Memory chain 是同一条实现演进吗？文档为什么明确说不能用后者替代前者证据？
- **red_hidden_intent:** Test evidence lineage discipline.
- **expected_evidence:** PF-011 / PF-029 / PF-030.

### B2-Q065
- **claim_under_test:** OpenViking alternative.
- **red_question:** 如果今天面试官问“为什么用 OpenViking，不直接 pgvector/向量库”，你有历史决策证据吗？没有时怎么回答？
- **red_hidden_intent:** Prevent invented build/buy rationale.
- **expected_evidence:** PF-011 boundary.

### B2-Q066
- **claim_under_test:** Memory vs Case Workspace.
- **red_question:** 最新架构强调事件、证据、Fact–Article Map 放 Knowledge/Domain，而不是 Long-term Memory。那你早期 Memory 工作是不是方向错了？
- **red_hidden_intent:** Test ability to explain evolution without defensiveness.
- **expected_evidence:** Product strategy + Runtime memory boundary.

### B2-Q067
- **claim_under_test:** Memory necessity.
- **red_question:** 如果用户每次都能从 Matter/Document/Task state 重建 Context，Long-term Memory 还剩什么不可替代价值？
- **red_hidden_intent:** Simplification/deletion condition.
- **expected_evidence:** Runtime/Application product framing.

### B2-Q068
- **claim_under_test:** Personal ownership.
- **red_question:** Context/Memory V2 foundation chain里哪些 commit 是你 author/committer？“第一批重要工作”和“从零引入 Memory”为什么必须区分？
- **red_hidden_intent:** Ownership precision.
- **expected_evidence:** PF-010/PF-030.

### B2-Q069
- **claim_under_test:** Project requirement.
- **red_question:** 这条 Context/Memory 工作的原始产品需求、Issue 或真实 Bad Case 恢复了吗？如果没有，为什么不把它降成纯技术探索？
- **red_hidden_intent:** Project causality evidence.
- **expected_evidence:** PF-029/030 explicitly missing product cause.

### B2-Q070
- **claim_under_test:** Resume result.
- **red_question:** 你能证明这条工作“解决了上下文污染”吗？如果只能证明 gate/trace 行为，你的 30 秒说法应该怎么收缩？
- **red_hidden_intent:** Outcome claim discipline.
- **expected_evidence:** Resume + PF-029.

## C. Project reality and personal ownership under skeptical hiring manager

### B2-Q071
- **claim_under_test:** Real project participation.
- **red_question:** 你在 Zuno 2026.03 加入，简历里最强两条代码证据却集中在 4 月和 6 月。3 月到这两个节点之间你具体在做什么？哪些事实能恢复？
- **red_hidden_intent:** Timeline continuity.
- **expected_evidence:** Project history/provenance.

### B2-Q072
- **claim_under_test:** Team ownership.
- **red_question:** 7–8 人团队里技术负责人是谁、你的任务怎么分下来、谁 review？这些组织事实目前哪些是确认、哪些只是回忆？
- **red_hidden_intent:** Project reality / ownership.
- **expected_evidence:** Project team section / PF-006.

### B2-Q073
- **claim_under_test:** Court-side relevance.
- **red_question:** 你本人做的 Tool Calling 和 Context/Memory 改动有没有确定进入法院侧测试或 Pilot 的版本？没有版本映射时能不能说“用于法院场景”？
- **red_hidden_intent:** Prevent personal work → Pilot causality inflation.
- **expected_evidence:** Historical version unknown.

### B2-Q074
- **claim_under_test:** Customer quality.
- **red_question:** 客户说回答质量不够，你本人修过任何能直接对应这条反馈的 Bad Case 吗？PF-031 为什么不能拿来顶替？
- **red_hidden_intent:** Separate customer feedback from later GraphRAG eval.
- **expected_evidence:** PF-017/PF-031.

### B2-Q075
- **claim_under_test:** Architecture review ownership.
- **red_question:** 今天这套 Project/Architecture/Modules 文档大量由后续重构形成。面试官问“这是不是 ChatGPT 帮你设计的架构”，你怎么区分个人理解、模型辅助和历史团队实现？
- **red_hidden_intent:** AI-assistance ownership honesty.
- **expected_evidence:** Project ownership/governance boundaries.

### B2-Q076
- **claim_under_test:** Research engineering value.
- **red_question:** 项目真正“工程化了葛季栋论文”的历史证据不完整。那你现在把研究资产放到产品战略中心，会不会只是一个漂亮故事？
- **red_hidden_intent:** Challenge post-hoc product thesis.
- **expected_evidence:** Lineage vs Current distinction.

### B2-Q077
- **claim_under_test:** Candidate's unique value.
- **red_question:** 如果把导师论文、团队已有系统、LangGraph/MCP/OpenViking 都扣掉，你个人给 Zuno 留下的可证明资产是什么？
- **red_hidden_intent:** Force irreducible personal contribution.
- **expected_evidence:** PF-029/PF-032 plus DB/debug participation.

### B2-Q078
- **claim_under_test:** DB debugging.
- **red_question:** “进入 PostgreSQL 查看和调试实际数据”太泛。你看过什么表/状态、解决过什么问题？如果具体 SQL/Issue 没恢复，这条为什么还值得写？
- **red_hidden_intent:** Attack vague resume bullet.
- **expected_evidence:** PF-013 only user-confirmed.

### B2-Q079
- **claim_under_test:** Current vs historical code.
- **red_question:** 你现在能打开 main 解释很多 Runtime/Effects/Security 代码，但这些是不是你当时写的？面试官怎么防止你拿“熟悉仓库”冒充“个人实现”？
- **red_hidden_intent:** Ownership under current-code knowledge.
- **expected_evidence:** Provenance boundaries.

### B2-Q080
- **claim_under_test:** Production claim.
- **red_question:** 如果 HR/面试官顺口问“上线了吗”，你用一句话怎么答，既不把 Pilot 说成生产，也不让项目听起来像纯 Demo？
- **red_hidden_intent:** Communication under evidence constraints.
- **expected_evidence:** PF-019/PF-020.

### B2-Q081
- **claim_under_test:** Real-user workflow.
- **red_question:** 法院侧人员测试到底测什么任务、怎么给反馈，目前没恢复。那你所谓 Case Workspace 第一产品切口为什么选择“争议焦点 + 证据—法条审查”，依据是什么？
- **red_hidden_intent:** Product hypothesis vs user evidence.
- **expected_evidence:** Research strategy as Target, not historical fact.

### B2-Q082
- **claim_under_test:** Resume title.
- **red_question:** “Zuno：法律智能 Agent 平台”会不会诱导面试官以为你做了完整 Agent 平台？你为什么不改成“智慧司法 AI 应用 / Legal Backend”？
- **red_hidden_intent:** Resume claim-risk framing.
- **expected_evidence:** Resume + updated product thesis.

### B2-Q083
- **claim_under_test:** Business outcome.
- **red_question:** 你没有用户量、质量提升、延迟指标。大厂面试官问“这个项目最后结果怎样”，你最强的证据排序是什么？
- **red_hidden_intent:** Build an honest evidence hierarchy.
- **expected_evidence:** Pilot, focused tests, fault probes, eval regression.

### B2-Q084
- **claim_under_test:** Failure ownership.
- **red_question:** Slice C 发现 mandatory audit 没接上、reconcile replay 错判 completed。这些问题是谁实现的并不重要；面试官问“你参与架构复盘为什么没直接修”，你怎么回答 implementation_authorization:NO？
- **red_hidden_intent:** Test governance vs action trade-off.
- **expected_evidence:** Governance review/authorization boundary.

### B2-Q085
- **claim_under_test:** Simplification.
- **red_question:** 今天让你接手这个项目，只给两个月，你会先删哪些历史复杂度、先补哪三个证据缺口？
- **red_hidden_intent:** Prioritization under constraints.
- **expected_evidence:** Eval deletion conditions + known Current gaps.

## D. Backend / distributed-systems fundamentals derived from personal claims

### B2-Q086
- **claim_under_test:** Python request isolation.
- **red_question:** 如果 MCP user config 放在全局对象上，async 并发为什么会串用户？Python asyncio 下共享可变状态的典型 race 是什么？
- **red_hidden_intent:** Derive concurrency fundamental from Tool claim.
- **expected_evidence:** General engineering knowledge consistent with claim.

### B2-Q087
- **claim_under_test:** Context-local state.
- **red_question:** `contextvars.ContextVar` 和普通全局变量 / thread-local 在 async Python 中有什么区别？如果你要做 request-scoped MCP config 会怎么选？
- **red_hidden_intent:** Test Python concurrency fundamentals.
- **expected_evidence:** Fundamental knowledge; not necessarily historical implementation.

### B2-Q088
- **claim_under_test:** Database scope filtering.
- **red_question:** same-scope memory 用 SQL 查时，如果 scope 是多列组合，你怎么设计索引？`WHERE user_id=? AND workspace_id=? AND status='APPROVED'` 这种查询索引顺序怎么考虑？
- **red_hidden_intent:** DB fundamentals from Context claim.
- **expected_evidence:** Database/index reasoning.

### B2-Q089
- **claim_under_test:** Transactions.
- **red_question:** Memory status 从 Candidate 改 APPROVED，同时写 audit/provenance，为什么可能需要一个事务？如果两步之间 crash 会怎样？
- **red_hidden_intent:** Transaction atomicity fundamental.
- **expected_evidence:** Backend reasoning.

### B2-Q090
- **claim_under_test:** Isolation levels.
- **red_question:** 两个 reviewer 同时审批/拒绝同一 MemoryCandidate，PostgreSQL 默认 Read Committed 下可能发生什么？你会用 version/CAS 还是更高隔离级别？
- **red_hidden_intent:** Concurrency control fundamental.
- **expected_evidence:** DB reasoning aligned with owner/version principles.

### B2-Q091
- **claim_under_test:** At-least-once queue semantics.
- **red_question:** RabbitMQ Worker 消费一个任务，业务写库成功但 ACK 前崩溃，消息会怎样？为什么消费者要幂等？
- **red_hidden_intent:** Message queue fundamental derived from project stack.
- **expected_evidence:** Backend fundamental.

### B2-Q092
- **claim_under_test:** Idempotency.
- **red_question:** 幂等 key 应该绑定“请求重试”还是“业务动作”？如果两个 HTTP request body 一样但用户确实想做两次，怎么避免误去重？
- **red_hidden_intent:** Idempotency semantics.
- **expected_evidence:** Application/Effects reasoning.

### B2-Q093
- **claim_under_test:** HTTP/TCP uncertainty.
- **red_question:** 客户端收不到 HTTP response 时，TCP FIN/RST/timeout 分别能不能证明服务端业务事务没提交？为什么？
- **red_hidden_intent:** Network fundamental from Effects.
- **expected_evidence:** Fundamental understanding.

### B2-Q094
- **claim_under_test:** Cache semantics.
- **red_question:** 如果 Memory/Knowledge 用 Redis cache，cache miss、cache stale、Redis down 分别应该是质量降级还是业务错误？Source of Truth 谁决定？
- **red_hidden_intent:** Cache authority fundamental.
- **expected_evidence:** Architecture owner hierarchy.

### B2-Q095
- **claim_under_test:** Optimistic concurrency.
- **red_question:** 你们 DomainVersion / PlanVersion 都强调版本。如果 SQL 用 `UPDATE ... WHERE version = ?`，怎样判断并发冲突？失败后为什么不能无脑 retry？
- **red_hidden_intent:** CAS/version fundamental.
- **expected_evidence:** Domain/Runtime reasoning.

### B2-Q096
- **claim_under_test:** Distributed locks.
- **red_question:** Single Controller 如果用 Redis lease，旧 Controller STW/网络分区后 lease 过期，新 Controller 接管，旧的又恢复，为什么需要 fencing token？
- **red_hidden_intent:** Distributed lock fundamental.
- **expected_evidence:** Runtime control reasoning.

### B2-Q097
- **claim_under_test:** Eventual consistency.
- **red_question:** PostgreSQL 已提交 Domain fact，但 UI projection 还没更新。用户看到旧状态是允许的吗？你如何区分 eventual consistency 和业务错误？
- **red_hidden_intent:** Projection consistency fundamental.
- **expected_evidence:** Application/Domain owner model.

### B2-Q098
- **claim_under_test:** Schema migration.
- **red_question:** Tool/MCP schema 或 DB schema 升级时，为什么“代码先发还是 migration 先发”会影响兼容性？expand/contract migration 怎么做？
- **red_hidden_intent:** Deployment/migration fundamental.
- **expected_evidence:** Backend fundamentals; current Alembic blocker context.

### B2-Q099
- **claim_under_test:** Backpressure.
- **red_question:** 模型 Provider 限流导致队列堆积，增加 Worker 为什么可能更糟？你会把 backpressure 放在哪一层？
- **red_hidden_intent:** Capacity control fundamental.
- **expected_evidence:** Architecture deployment/backpressure reasoning.

### B2-Q100
- **claim_under_test:** Interview close on implementation credibility.
- **red_question:** 假设我已经接受 Zuno 的大架构，但现在只看你本人：给我一个 5 分钟白板故事，从一条真实 bug/需求开始，画代码路径、状态、测试、trade-off、结果；你选 Tool/MCP 还是 Context/Memory？为什么另一个不选？
- **red_hidden_intent:** Force candidate to choose the strongest implementation story under evidence pressure.
- **expected_evidence:** PF-032 vs PF-029 evidence depth.

## Red Batch Freeze

- Question count: 100
- Questions frozen after this commit.
- No unsupported #212 premise is used.
- Broad Target-architecture questions are intentionally downweighted.
- Follow-up from Blue belongs to Batch 003.
