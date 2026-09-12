# Round #013 — Batch 002 — Blue

Status: `CLOSED_BOOK_ANSWERED_AND_ARCHIVED`  
Answer count: **100**

Blue uses the exact resume plus the manifest allowlist. General backend fundamentals are answered as general engineering reasoning and are never presented as historical Zuno implementation facts.

## A. Tool / MCP / Agent implementation deep dive

### B2-Q001
**answer:** Canonical PF-032 能恢复到：父提交里的 `GeneralAgent` 有 `tool_invocation_model`、`available_tools` / `LLMToolSelectorMiddleware` 选择脚手架；MCP Server 先通过 `MCPAgent` 包装成 Tool，Skill 通过 `SkillAgent` 包装成 Tool。`77346758...` 移除这些 nested Agent / selector scaffolding，把实际 MCP tools 和 Skill guidance tools 直接绑定到一个 `GeneralAgent`。更细的每跳 payload/返回对象没有在 canonical prose 中冻结。

**source_trace:** `docs/governance/project-fact-provenance.md` PF-032.

### B2-Q002
**answer:** 可证明少掉的是 nested MCPAgent/SkillAgent-as-Tool 与独立 selector scaffolding，使 GeneralAgent 直接看到实际 Tool。不能从 canonical 证据声称一定少了一次“在线第二模型调用”，因为文档只证明脚手架存在/被移除，没有证明 selector middleware 当时实际运行。

**source_trace:** PF-032.

### B2-Q003
**answer:** 历史原始决策记录/Review 没恢复，所以我不能说“当时证明 Specialist Agent 一定更差”。今天合理的工程解释是：如果 MCPAgent 只做协议转发而没有独立专业语义，把它再包装成 Agent 会增加层级；但这是对 diff 的架构解释，不应冒充原始需求。

**source_trace:** PF-032; `unknown_or_unsupported: original design rationale not recovered`.

### B2-Q004
**answer:** 直接暴露 Tool 的确会有 schema/context 膨胀风险。历史材料没有 Tool 数量、token、selection quality 测量，因此不能说当时已经解决。今天如果 Tool 数量扩大，应由 capability/tool retrieval 或按任务缩小暴露集合来处理，而不是把“直接绑定所有 Tool”永久化。

**source_trace:** PF-032 historical boundary; `docs/modules/capability/README.md` / Runtime Target for current design principle.

### B2-Q005
**answer:** PF-032 明确记录 user config 注入进入 `EmitEventAgentMiddleware`，由 tool name 映射回 MCP server，在 tool-call 前按调用注入。为什么不初始化时注入的原始设计讨论没有恢复；从机制上看 call-time injection 能保留调用上下文，但不能把这个推理写成历史会议结论。

**source_trace:** PF-032.

### B2-Q006
**answer:** Canonical 资料没有冻结 MCP user config 在并发请求中的实际承载方式（显式参数、request-local state、ContextVar 或 Tool 实例）。因此不能宣称已经证明不会串用户；当前只能证明“按调用注入”的代码策略存在。

**source_trace:** PF-032; `unknown_or_unsupported: exact concurrency storage/isolation`.

### B2-Q007
**answer:** PF-032 说明 04-28 regression artifact 覆盖 “platform-ready MCP 无需 user config” 和 config gate，但没有在 canonical prose 中完整列出所有缺失/错误配置的返回语义。可以说存在 config gate 测试，不能补造 fail-fast / skip / fallback 的精确行为。

**source_trace:** PF-032.

### B2-Q008
**answer:** MCP Tool discovery 的刷新时点和 schema 变更策略没有被 PF-032 恢复。今天 Target 会把 Provider/Tool version 与 compatibility/qualification 分开处理，但这不能反写到 4 月 Current。

**source_trace:** PF-032; `docs/modules/capability/README.md` as Target only.

### B2-Q009
**answer:** Canonical 资料没有给出多 MCP Server 同名 Tool 的完整 namespace/collision 规则。PF-032 只证明 custom MCP server name normalization 的递归 bug 被修复；不能据此推导一套完整命名体系。

**source_trace:** PF-032.

### B2-Q010
**answer:** 父版本 `WorkSpaceSimpleAgent._canonical_mcp_target()` 对 custom MCP server name 会再次调用自身；当 normalized query 已经等于该 server name 时，递归没有收敛条件，会无限自调用。04-28 改为识别该情况后直接返回 normalized server name，并加 `test_canonical_mcp_target_handles_custom_server_name_without_recursion`。

**source_trace:** PF-032 Tool Calling Strategy 取证边界.

### B2-Q011
**answer:** 当前证据能证明的是一个针对 custom server name 不递归的 regression test，并没有记录更一般的 property-based invariant。可以从设计上希望 normalization 幂等，但不能说当时已有 property test。

**source_trace:** PF-032.

### B2-Q012
**answer:** 父版本的高德天气 direct route 只用 `cleaned.replace("天气", "")` 生成 city；新版本增加 `_extract_gaode_weather_city()`，并用“请用高德地图查询南京今天天气，并简短回答。”锁定为 `maps_weather(city="南京")`。Canonical 文档没有保存父版本对该句的精确最终 city 字符串，我不会自行补一个。

**source_trace:** PF-032.

### B2-Q013
**answer:** 为什么历史上选择 Workspace 侧 extraction 而不是完全依赖模型 structured tool call，没有原始 ADR/Review。能确认的是该 direct route 本身就是 deterministic short path，所以为了让自然句稳定映射到已知 Tool 参数，代码增加了 extraction；这只能算实现解释，不能升级成经比较后的最优方案。

**source_trace:** PF-032; original rationale unknown.

### B2-Q014
**answer:** Canonical 证据说明 04-28 同一 test file 固定 direct route 到 `maps_weather(city="南京")`、custom name 不递归、platform-ready MCP 无需 config、direct structured result 呈现等行为。这类 artifact 是 deterministic regression，不等于完整跑外部 LLM/MCP Server E2E。

**source_trace:** PF-032.

### B2-Q015
**answer:** PF-032 给出的原则是：目标/参数明确的一步 Tool 可走 deterministic direct route；开放式、多步或参数不完整任务进入 ReAct。已确认的 direct 示例是高德天气。Canonical 资料没有列出三类完整历史样例，因此我不会为“必须 ReAct”编一个当时 case。

**source_trace:** PF-032 + exact resume wording.

### B2-Q016
**answer:** 4 月历史材料不能证明 direct route 已经拥有今天 Target 的 Approval/SecurityEpoch/PreparedAction 保护。若 direct Tool 有现实副作用，今天应由 Security/Effects send boundary 约束；不能说当时 direct route 因为 deterministic 就天然安全。

**source_trace:** PF-032; `docs/modules/security/README.md`; `docs/modules/effects/README.md` as later Target/Current boundary.

### B2-Q017
**answer:** Canonical PF-032 没有冻结“direct route 执行失败后是否自动进入 ReAct”的精确分支，因此无法承诺不会重复副作用。今天架构要求外部副作用在结果 Unknown 时 Reconcile 而不是换路线盲重试，但这是后来更强语义。

**source_trace:** PF-032; Effects Target.

### B2-Q018
**answer:** 不应说“移除了已在线运行的第二 selector model”。准确说法是父代码存在 `tool_invocation_model` / `available_tools` / `LLMToolSelectorMiddleware` 选择脚手架以及 nested Agent-as-Tool 路径，`77346758...` 把这些 scaffold/nesting 收口到单一 GeneralAgent 直接绑定实际 Tool。

**source_trace:** PF-032.

### B2-Q019
**answer:** Tool schema 在进入模型前是否裁剪、重写 description 或做特定类型转换没有在 canonical PF-032 中记录。只能确认 MCP 具体 tools 被暴露给 GeneralAgent，不能扩写 schema engineering 细节。

**source_trace:** PF-032; unsupported exact detail.

### B2-Q020
**answer:** Zuno 这段可证明 direct structured result 的最终呈现有 regression artifact，但没有 canonical 证据证明 Tool result 做了像 Coding Agent 那样的截断/摘要/安全清洗。因此不能借另一个项目的 Tool Result 管理来补 Zuno。

**source_trace:** PF-032 + exact resume separation.

### B2-Q021
**answer:** 历史 MCP timeout / disconnect / schema mismatch 的完整 error propagation 没有恢复。我可以讲今天 Capability/Effects 应怎样区分 transport、semantic acceptance 和 side-effect uncertainty，但不能说 4 月代码已经如此。

**source_trace:** PF-032; current Target docs only for proposed semantics.

### B2-Q022
**answer:** 4 月 GeneralAgent 是否并发执行多个 Tool、如何 join/order，没有 canonical 事实支持，属于 implementation detail not recovered。

**source_trace:** PF-032; unsupported exact detail.

### B2-Q023
**answer:** PF-032 没有证明 4 月链路有 PreparedAction/idempotency key。面对网络重试我会明确说：当时个人工作是 Agent-side Tool exposure/routing；今天 Target 的 idempotency/reconcile 是后来 Tool Runtime/Effects 语义，不能算入个人历史实现。

**source_trace:** PF-032; Project provenance boundary; Effects module.

### B2-Q024
**answer:** PF-032 没有恢复可用于判断 direct/ReAct 的具体 trace/log 字段，因此不能声称有完整可观测路由证据。现有历史代码/test 能解释行为，但真实运行 Trace 是未来可补证据。

**source_trace:** PF-032 evidence-needed column.

### B2-Q025
**answer:** 没有 latency/token 对照，不能说“降低了多少开销”，甚至不应把“少一次模型调用”写成已测事实。可以说调用层次被收口、nested Agent/selector scaffolding 被移除，这是代码结构事实。

**source_trace:** PF-032; historical performance evidence absent.

### B2-Q026
**answer:** deterministic function/integration-level tests能防 custom-name recursion、参数 extraction、config gate、structured-result presentation 这些具体回归；它们防不了真实 MCP Server 协议漂移、网络异常、外部 Provider、真实 LLM trajectory 和法院 E2E。

**source_trace:** PF-032.

### B2-Q027
**answer:** 今天可以给 Tool/Provider 建版本化 contract/schema compatibility tests，并让旧 Plan 在版本变化后重新验收；但 PF-032 没有证明 4 月已经做 schema drift governance。

**source_trace:** `docs/modules/capability/README.md` Target; PF-032 historical limit.

### B2-Q028
**answer:** 今天不会把“所有 Tool 永久直接塞给 GeneralAgent”当教条。如果 Tool 数量小且明确，直接绑定仍最简单；Tool 数量、权限域或专业语义增长后，可以按 Capability/Task Context 检索/缩小候选。是否加 router 应由 Tool selection quality、token 和复杂度测量决定。

**source_trace:** Capability / Runtime simplification principles; no claim this was historical design.

### B2-Q029
**answer:** MCP SDK/Server 继续负责协议连接、Tool discovery 和具体执行。PF-032 能归给 Zuno/个人的主要是 Agent-side Tool/Skill exposure、nested Agent/selector 收口、tool→server user config injection、Workspace route 与两个具体 hardening。协议本身不是自研。

**source_trace:** PF-032.

### B2-Q030
**answer:** 我会以“Tool/MCP 调用层次收口”做主故事，再用 recursion 和天气参数两个可复现 bug 证明不是纯重命名；user config injection 作为关键实现点。这样最符合 PF-032 的证据强度，又不需要虚构性能收益。

**source_trace:** exact resume + PF-032.

### B2-Q031
**answer:** author/committer 只支持我对 commit 有直接贡献，不意味着 broad platform commit 每一行都属于我。`0b5fb350...` 跨 Tool、Knowledge、模型、Docker 等多区域，PF-032 明确只允许认领 WorkSpaceSimpleAgent 中可从前后 diff 和 regression artifact 对齐的几条路径。

**source_trace:** PF-032.

### B2-Q032
**answer:** 当前没有恢复这两段任务的 PR、Review、原始 requirement 或历史 status check，因此不能证明是谁下发需求/谁 review，也不能把它写成客户直接驱动。现有证据只证明 main history 里的工程改动与 test artifact。

**source_trace:** PF-032 evidence-needed column.

### B2-Q033
**answer:** 可以按 canonical 证据写最小逻辑：custom server name 输入 `_canonical_mcp_target()`，normalized query 与 server name 相同，父实现仍自调用导致不收敛；修复分支直接返回 normalized server name。精确源码白板要以历史 commit 为准，但因果已经被 PF-032 保留。

**source_trace:** PF-032.

### B2-Q034
**answer:** 没有证据表明 4 月 GeneralAgent/MCP 代码直接演化出后来 PreparedAction/EffectReceipt/Reconcile。它们面对的是不同层次：4 月是 Tool exposure/routing/config；后来的 Effects 是现实副作用 Authority。不能把后者算作个人 Tool Calling lineage。

**source_trace:** PF-032 + Effects module/provenance boundary.

### B2-Q035
**answer:** 最可迁移的原则是：如果一个嵌套 Agent 没有独立专业 Authority，只是协议/Tool 转发，就优先把调用语义收敛到更少的决策层；同时用 deterministic regression 锁定路由/参数 hardening，而不要把协议 Provider 能力认成业务 Authority。

**source_trace:** PF-032 + current Capability/Effects separation.

## B. Context / Memory implementation deep dive

### B2-Q036
**answer:** PF-029/030 能证明 `GeneralAgent` 有最小 `prepare_context()` integration、后续 PR #8 把 same-scope task summary 和 APPROVED structured memory 接入 pre-call readback，但 canonical prose 没列函数完整签名、所有输入参数和返回类型。因此函数级签名需要回历史代码，不能现场编。

**source_trace:** PF-029 / PF-030.

### B2-Q037
**answer:** Canonical 只写 `same-scope`，没有冻结 exact scope key。简历之所以可以写，是因为 PR/test evidence 支持 scope boundary 本身；如果被追到具体字段，我必须说“需要回 commit/test，当前面试文档没有保留字段级定义”，不能猜 User/Workspace/Matter。

**source_trace:** PF-029.

### B2-Q038
**answer:** 两个 Workspace/Matter 的具体 cross-scope 过滤规则没有在 canonical prose 中恢复，因此不能给实际 SQL/predicate。能确认 scoped Memory contract 和 focused scope tests 存在，不能从这个扩成完整多租户隔离实现。

**source_trace:** PF-029/PF-030.

### B2-Q039
**answer:** canonical 事实只保留 typed/scoped Memory contract、`APPROVED` status、source trace 等方向，没有列完整字段 schema。不能把今天 DomainVersion/CapabilityVersion 等字段臆测进当时 structured memory。

**source_trace:** PF-029/PF-030.

### B2-Q040
**answer:** `APPROVED` 是在 store query 还是加载后 Python filter，canonical docs 没记录。当前能证明的是 pre-call readback“仅消费 APPROVED”，不能据此声称数据库层强制约束。

**source_trace:** PF-029.

### B2-Q041
**answer:** APPROVED 之前的完整状态机、谁执行 approval，没有被 PF-029 恢复。我的 slice 依赖现有 review/provenance contract并在 read path 上做 gate，不代表我拥有完整 Memory review lifecycle。

**source_trace:** PF-029/PF-030.

### B2-Q042
**answer:** PF-030 证明 post-turn 会写 scoped raw event / task summary，但没有说明 task summary 是哪个模型/规则生成，也没有列失败策略。因此只能确认该 artefact 存在于数据流，不能补生成实现。

**source_trace:** PF-030.

### B2-Q043
**answer:** summary freshness / 更新失配没有 canonical Current 证据。今天架构要求关键状态从 owner facts 重建并做版本/新鲜度判断，但不能说 PF-029 已经自动判 stale summary。

**source_trace:** PF-029/030 + Runtime Target.

### B2-Q044
**answer:** PR #8 增加 Context Pack source trace，但 canonical prose 没说明它具体存放于 pack item、log 还是独立 record。它服务 provenance/debug 的方向可确认；没有证据说它本身拥有业务 Authority。

**source_trace:** PF-029.

### B2-Q045
**answer:** 多源 summary 的 source-id cardinality、原消息删除/更正后的处理没有 canonical 证据，属于 implementation detail not recovered。

**source_trace:** PF-029; unsupported exact detail.

### B2-Q046
**answer:** 能明确的 policy 是 scoped readback、仅 APPROVED structured memory、source trace、review/provenance contract；没有证据证明 PR #8 同时实现 token budget、relevance ranking、最大条数等完整 Context Engineering policy。

**source_trace:** PF-029.

### B2-Q047
**answer:** task summary 与 structured memory 在最终 prompt 的具体顺序/模板未在 canonical docs 中记录，不能编。

**source_trace:** PF-029.

### B2-Q048
**answer:** 没有证据说明这两类上下文做语义去重。风险是重复事实放大模型注意力或造成冲突；今天可在 Context Engineering 层处理，但不能反写成已实现。

**source_trace:** PF-029 + Runtime Target principle.

### B2-Q049
**answer:** 历史 slice 没有恢复 summary vs APPROVED memory 冲突仲裁。今天更强的原则是二者都只是工作上下文，不能覆盖 Domain/Document facts；出现冲突应保留来源并重新确认，而不是给 Memory 固定更高权威。

**source_trace:** PF-029 + Domain/Runtime Target.

### B2-Q050
**answer:** Memory/query failure时是 fail request 还是降级，无 canonical 证据。若做产品化，降级策略必须显式，因为“无 Memory 继续”可能改变回答质量；不能把 silent degradation 当成功。

**source_trace:** PF-029/030; implementation gap.

### B2-Q051
**answer:** 没有该 slice 的 DB/network latency、cache 或 token 成本测量，不能声称性能影响已优化。

**source_trace:** PF-029 evidence boundary; historical performance unknown.

### B2-Q052
**answer:** PR #8 没有 canonical 证据证明 token overflow 处理。Zuno 简历也没有把 Coding Agent 的 truncation/compression 策略写进这条，因此如果上下文超窗的历史行为被追问，只能回代码验证。

**source_trace:** resume + PF-029.

### B2-Q053
**answer:** 除 scope / APPROVED 之外没有明确 relevance ranking 证据，所以长期 Memory 增长后的 selection 是这条历史 slice 的已知上限之一。今天 Runtime 将 Memory 降级成按需工作上下文，并允许没有收益时删除/缩薄。

**source_trace:** PF-029 + Runtime Target.

### B2-Q054
**answer:** “review gate”当前证据最稳的是 review/provenance contract + read-time `APPROVED` gate和 focused tests，不是已经恢复的完整 UI 人审运营。我个人实现边界应讲成 contract/readback hardening，而不是“搭了 Memory 审核平台”。

**source_trace:** PF-029.

### B2-Q055
**answer:** canonical evidence 没有证明所有写路径都无法绕过 review gate，因此“保证只有审核记忆能存在”太强。能说的是 `prepare_context()` 的受测 readback只消费 APPROVED memory。

**source_trace:** PF-029.

### B2-Q056
**answer:** PF-030 的 V2 integration 先落 post-turn scoped raw event / task summary write和最小 pre-call context；当时还没有把历史 summary / structured memory readback 接回模型。PR #8 是后续 hardening，把 same-scope summary 与 APPROVED structured memory 加到 pre-call readback。

**source_trace:** PF-030 + PF-029.

### B2-Q057
**answer:** canonical 资料说明 V2 有 callable pre-call `ContextOrchestrator`，并有 `GeneralAgent` 最小 context/post-turn integration，但没有足够字段级材料描述两者所有职责分配。可以说 orchestrator 提供独立 context orchestration surface、GeneralAgent 消费它；更细需回代码。

**source_trace:** PF-030.

### B2-Q058
**answer:** typed contract 至少把 context/memory artefact 从随意 dict/string提升成可检查的数据边界，便于 scope/source/review 约束；它是否用了 dataclass/Pydantic 以及每个字段不在 canonical prose 中，不能编。

**source_trace:** PF-030.

### B2-Q059
**answer:** Canonical PF-029只记录 PR 描述的 focused tests `32 passed`、repo tests `66 passed`、legacy tests `11 passed` 和三种 profile contract eval `status: ok`，没有列三条具体 test name/input。因此我不能凭文档背出 scope/approval/provenance 的 exact fixtures。

**source_trace:** PF-029 detailed provenance.

### B2-Q060
**answer:** canonical 事实没有说明这 32 个 focused tests 使用真实 PostgreSQL 还是 mock/in-memory，因此不能把它们升级成数据库集成证据。

**source_trace:** PF-029.

### B2-Q061
**answer:** 简历/PF-029 能说 focused tests 验证 scope boundary，但没有列 cross-scope negative test 的具体名称/输入，所以不能声称已证明所有串案路径。最危险风险确实是不同 scope 的 summary/memory 被错误注入另一个任务。

**source_trace:** PF-029; exact negative test unsupported.

### B2-Q062
**answer:** 没有证据证明 PF-029 对 APPROVED memory 做 instruction stripping 或 trust-boundary encoding。今天应把 Memory/Tool 内容视为数据、不赋予 Security Authority，并通过结构化 context / sandbox /权限边界降低风险；这属于 Target hardening，不是历史 Claim。

**source_trace:** PF-029 + Runtime/Security Target.

### B2-Q063
**answer:** PF-029 没证明 DocumentVersion 变化会自动让 Memory stale，所以 `prepare_context()` 是否仍读到旧 APPROVED memory 是历史实现未证明点。今天应该让正式材料/Domain事实拥有更高权威，Memory 不能覆盖它。

**source_trace:** PF-029 + Domain/Knowledge Target.

### B2-Q064
**answer:** 不能把 OpenViking 接入和 6 月 V2/PR #8 自动视为同一连续实现。PF-011 是用户确认但 public artifact 未恢复；PF-029/030 是后来公开 Git 可核验的 Context/Memory chain。用后者替代前者会伪造历史证据。

**source_trace:** PF-011 / PF-029 / PF-030.

### B2-Q065
**answer:** 没有恢复 OpenViking 当时的 Build/Buy 决策材料，所以不能现场声称“因为 X 优于 pgvector 才选它”。最稳回答是确认参与接入，但具体 rationale/artifact 未恢复。

**source_trace:** PF-011.

### B2-Q066
**answer:** 早期 Memory 工作不是“方向错误”，它解决 Agent 工作上下文和跨轮次信息利用；最新架构只是把边界收紧：可从 Matter/Knowledge/Domain 重建的案件事实不应该由 Long-term Memory 独占。也就是说应删除/降级的是错误 Authority，而不是所有 Memory 能力。

**source_trace:** Runtime/Application/Knowledge/Domain Part A + PF-029/030.

### B2-Q067
**answer:** 如果某类信息完全能从权威 store 快速重建，Long-term Memory 的价值就下降；剩余价值更偏用户/工作偏好、开放问题、阶段性工作上下文等不等同于正式案件事实的信息。没有 Eval 证明收益时可以缩薄。

**source_trace:** Runtime simplification + Project product strategy.

### B2-Q068
**answer:** PF-030 明确说用户 GitHub 账号在公开 main ancestry 上连续落了列出的 V2 commits；但“第一批重要 Memory 工作”是参与级历史 Claim，不能说“从零引入 Memory”，因为 4 月 15 日公开根提交已经存在 `services/memory/`、Memory History DAO、Chroma/Milvus store。

**source_trace:** PF-010 / PF-030 + Memory/OpenViking boundary.

### B2-Q069
**answer:** 原始客户/法院需求、真实事故和质量结果没有恢复。PF-029/030 证明的是工程演进和测试，不足以证明产品 Cause→Result，所以不能把它说成客户 Bad Case 直接驱动；“纯技术探索”也过强，因为它位于真实项目主干，但业务原因 Unknown。

**source_trace:** PF-029/030 evidence limits.

### B2-Q070
**answer:** 不能证明“解决了上下文污染”这个产品结果。30 秒表述应是：我在现有 Context/Memory foundation 上把 same-scope summary 和 APPROVED structured memory 接入 pre-call readback，并补 policy/source trace/review-provenance gate，用 focused tests验证 scope/approval/provenance边界。

**source_trace:** exact resume + PF-029.

## C. Project reality and personal ownership

### B2-Q071
**answer:** 目前能恢复的时间锚点包括约 3 月加入、4 月 Tool Calling commits、6 月 GraphRAG/Context-Memory chain等；3 月到这些节点之间的完整任务列表没有恢复，因此不能编一条连续周报式故事。

**source_trace:** PF-007 + PF-012/PF-029–PF-032.

### B2-Q072
**answer:** Project narrative 能确认核心研发约 7–8 人，一名学硕学长承担主要技术负责人/任务协调角色并把我带入项目；正式组织图、职位和每模块 Owner没有恢复。具体谁 review PF-029/PF-032也未恢复。

**source_trace:** `docs/project/README.md` team section; PF-006.

### B2-Q073
**answer:** 没有明确版本映射证明 PF-029/PF-032 进入了某次法院测试/Pilot，因此不能说“我这两个改动被法院验证”。它们发生在面向该场景的真实项目 main history，但是否进入具体试点版本 Unknown。

**source_trace:** Project History + PF-019 + PF-029/PF-032 evidence limits.

### B2-Q074
**answer:** 没有恢复我本人针对 PF-017 客户 Bad Case 的 Cause→Fix→Customer Result。PF-031 是独立的 HotpotQA研发质量闭环，文档明确禁止用它反向解释客户质量反馈。

**source_trace:** PF-017 / PF-031.

### B2-Q075
**answer:** 今天总体架构/文档是后续系统化整理，能证明我现在理解、Review和维护这套 Target，但不能倒推我是历史总体架构 Owner。至于具体哪些句子由 ChatGPT/Codex 辅助、哪些人工起草，canonical sources没有精确 attribution；面试时应讲“我负责理解、审阅和对事实边界负责”，不把 AI 辅助生成文本等同历史代码实现。

**source_trace:** Project ownership boundary; exact AI-authoring attribution unsupported.

### B2-Q076
**answer:** 这是 Target/Product Hypothesis，而不是“历史已完成研究产品化”的事实。它有团队研究谱系和工程问题支撑，但是否形成实际价值仍需 Task Class、Provider qualification、真实专业反馈与 Eval。漂亮故事只有在这些证据形成后才能升级为优势 Claim。

**source_trace:** Project / Research-to-Engineering strategy / Evidence boundary.

### B2-Q077
**answer:** 扣掉团队/框架后，最强可证明个人资产是 PF-032 的 Agent/Tool/MCP 两段 bounded implementation，以及 PF-030→PF-029 的 Context/Memory V2 + PR #8 readback hardening；另有方向级 Agent/Memory参与和数据库调试，但证据强度更低。

**source_trace:** PF-009–PF-013, PF-029/030/032.

### B2-Q078
**answer:** PF-013 目前只有“进入数据库查看或调试过数据”的用户确认，没有表名、SQL、Issue 或结果，因此这条简历只适合作为辅助说明对真实项目数据有接触，不适合做主技术亮点。

**source_trace:** PF-013 + exact resume.

### B2-Q079
**answer:** Current main 代码熟悉度只能证明我现在能分析仓库，不等于 authored。个人 Claim 只回到用户确认 + historical commits/PR/tests等 provenance；当前 Effects/Security等后续代码不能因为我能解释就算个人实现。

**source_trace:** Project provenance rules + PF-029/032.

### B2-Q080
**answer:** 一句话：项目到过法院侧人员测试和 Pilot Validation，但目前没有正式 Production、SLA、稳定用户规模或完整验收证据，所以我把它描述为真实试点项目，不说生产上线。

**source_trace:** PF-018–PF-020.

### B2-Q081
**answer:** “争议焦点 + 证据—事实—法律依据审查”来自 LIPLAB 研究资产和专业结构的产品化匹配，是今天 Target 战略，不是已从法院用户访谈验证出的唯一最优切口。要升级为产品结论需要真实任务/Reviewer测量。

**source_trace:** Project product strategy + History boundary.

### B2-Q082
**answer:** 标题确实可能让人联想到完整 Agent 平台，所以面试第一句必须限定“已有项目基础上参与 Agent/Context/Tool，并做后续架构复盘”。是否改简历标题属于 Resume 决策；当前正文已经用项目简介和 Ownership 限制了强度。

**source_trace:** exact resume + Project product framing.

### B2-Q083
**answer:** 证据强度排序应是：个人 historical commit/PR/test → 当前可复核 fault/test evidence → 独立研发 eval regression（PF-031）→ Demo/Court test/Pilot 只证明阶段存在。用户收益、生产质量、QPS等没有就不放在结果顶部。

**source_trace:** provenance + Evidence.

### B2-Q084
**answer:** 当前 governance 明确 `implementation_authorization:NO`，诊断的目的先是确认 Target violation / implementation gap，而不是边测边偷偷改业务代码。#201/#205等已足以把问题从“需不需要更多测试”转成“需要授权后的实现任务”。因此没直接修不是声称不会修，而是遵守当前 Program gate。

**source_trace:** `docs/governance/effect-security-slice-c-review.md`; architecture metadata.

### B2-Q085
**answer:** 两个月优先级：先修已确认 correctness blocker（unknown-effect replay certainty、mandatory audit wiring、reconciliation convergence / Alembic blocker按授权排序）；同时恢复一个真实客户 Bad Case/Pilot闭环并建立最小业务 Eval。复杂度上默认关闭/延后没有正式收益证据的 GraphRAG default、persistent Multi-Agent、重 Native Runtime。

**source_trace:** Slice C Review; Project/Evaluation simplification rules.

## D. Backend / distributed-systems fundamentals derived from personal claims

### B2-Q086
**answer:** asyncio 并发任务在同一线程也会在 `await` 处交错，如果 user config 放在共享可变全局/单例字段，请求 A 写 config 后挂起，请求 B 可覆盖，A 恢复时读到 B 的配置。历史 PF-032 没证明用了全局，只是这个设计为什么危险。

**source_trace:** general Python concurrency reasoning; historical storage remains unknown.

### B2-Q087
**answer:** `ContextVar` 的值随 async task/context 传播，适合 request-local logical context；普通全局变量所有 coroutine共享，thread-local 在同一 asyncio线程里也无法区分 task。若必须用隐式 request context，ContextVar 比 thread-local 合适；更清楚的方案仍可显式传参。不能据此说 Zuno 历史用了 ContextVar。

**source_trace:** general Python fundamental; no historical claim.

### B2-Q088
**answer:** 对 `user_id/workspace_id/status` 这类查询，应根据高选择性、最常用等值前缀和排序/覆盖需求设计复合索引；例如如果每次都先限定 workspace/user，再取 APPROVED，可考虑 `(workspace_id, user_id, status, ...)`，但真实顺序要看 cardinality/查询计划。PF-029 没恢复实际 SQL/index。

**source_trace:** general DB reasoning; historical implementation unknown.

### B2-Q089
**answer:** 如果 approval 状态变化和 audit/provenance 必须作为一个业务决定同时成立，就应在同一事务中提交；否则 crash 可能出现 status 已 APPROVED 但没有审计，或审计记录存在但状态没变。PF-029 不证明历史实现采用哪种事务。

**source_trace:** general transaction reasoning + current architecture ownership principles.

### B2-Q090
**answer:** Read Committed 下两个 reviewer 都可能先读到同一 Candidate，然后分别写不同决定，后写覆盖前写。可用 version/CAS（`UPDATE ... WHERE version=?`）检测冲突，或在需要时行锁/更高隔离；重点是冲突要显式，而不是 last-write-wins。历史 Memory review实现未恢复。

**source_trace:** general PostgreSQL reasoning; Domain version principles.

### B2-Q091
**answer:** Worker 写库成功后 ACK 前 crash，RabbitMQ 通常会重新投递未 ACK 消息，因此消费者可能再次处理同一逻辑任务。业务写必须靠稳定 identity/idempotency/replay detection吸收至少一次投递；队列 ACK 不能提供跨数据库 exactly-once。

**source_trace:** general MQ reasoning; consistent with Architecture owner/local transaction model.

### B2-Q092
**answer:** idempotency key 应绑定一次逻辑动作/调用身份，而不是仅对 body 做 hash。两个 body 相同但用户明确发起两次，应有不同 invocation/action identity；同一次网络重试复用同一 identity。若同 identity 带不同规范化输入，应报冲突而不是静默去重。

**source_trace:** `docs/modules/application/README.md`; Effects identity principles.

### B2-Q093
**answer:** 客户端 timeout/RST/连接断开只能描述传输观察，通常不能证明服务端业务事务没有提交；请求可能已经到达并提交，只是 response 丢失。只有远端提供可查询状态/idempotency语义或明确未 dispatch 证据，才能提高确定性。

**source_trace:** Effects/Architecture semantics + general network reasoning.

### B2-Q094
**answer:** Cache source of truth 必须仍是 owning store。cache miss 通常触发回源，stale 是否可接受取决于事实类型：UI/派生检索可以短暂 eventual，但授权、正式业务事实不能让旧 cache 扩大权限或覆盖新状态。Redis down 应优先退化性能/缓存能力，而不是凭 cache 决定业务真相。

**source_trace:** Architecture state/recovery hierarchy; Security/Knowledge cache boundaries.

### B2-Q095
**answer:** `UPDATE ... WHERE id=? AND version=?` 受影响行数为 0 表示预期版本已变化，需要重新读取并判断业务前提；不能无脑 retry 同一写入，因为新的版本可能包含改变结论的新 Evidence/决定。CAS 保护的是因果前提，不只是 SQL 冲突。

**source_trace:** Domain/Runtime version semantics + general SQL CAS.

### B2-Q096
**answer:** 只有 lease 不够：旧 Controller 在网络暂停/STW期间 lease 过期，新 Controller 取得 lease 后开始写；旧 Controller恢复时若不知道自己已过期，仍可能写控制状态。单调 fencing token 随 lease 世代推进，让下游拒绝旧 token 的写入。Target提到 lease/fencing作为可选实现，不代表 Current 已完成。

**source_trace:** Runtime Part A + general distributed lock reasoning.

### B2-Q097
**answer:** Domain 已提交而 projection/UI 暂时旧是允许的 eventual-consistency窗口，只要 Domain仍是 Authority、projection 能通过 outbox/rebuild/retry收敛并且 UI 不把旧 projection 反向覆盖 Domain。若用户基于旧 projection执行不可逆动作，则需要重新读当前 owner facts/版本，而不能只信缓存视图。

**source_trace:** Architecture owner-local consistency; Application projection model.

### B2-Q098
**answer:** 不兼容 schema change 若代码和 migration 发布顺序错误，会出现新代码读不到旧列或旧代码读不了新格式。常见 expand/contract 是先添加向后兼容 schema，部署可同时读写新旧的代码，回填/切换，再删除旧字段。当前 Zuno 还有正式 Alembic entrypoint stale import blocker，因此不能声称 migration pipeline生产成熟。

**source_trace:** general migration reasoning + Evidence Alembic blocker.

### B2-Q099
**answer:** Provider限流时加本地 Worker 会让更多并发请求同时撞远端 quota，队列更快积压、重试风暴更严重。backpressure应在 admission/queue consumer concurrency/Model Gateway quota/budget处向上游传播；增加 Worker只适合本地可并行且下游容量允许的瓶颈。

**source_trace:** Architecture deployment/backpressure + Model Gateway.

### B2-Q100
**answer:** 我会选 Tool/MCP 作为 5 分钟白板主故事，因为 PF-032 已恢复更具体的 before/after code path、函数级 bug、commit 和 deterministic regression artifact：nested Agent/scaffolding → direct tools + call-time config injection，再加 custom recursion / weather extraction hardening。Context/Memory 更适合第二故事，它有 PR #8 和测试数量优势，但 exact scope/schema/reviewer runtime 细节在 canonical interview source 中缺失更多。

**source_trace:** PF-032 vs PF-029/030 evidence depth.

## Blue Batch Close

- Answer count: 100
- External interview calibration sources used: 0
- Strongly supported implementation answers: PF-032 recursion/weather/middleware/diff boundary; PF-029/030 V2/readback timeline and test-count boundary.
- Repeated unsupported implementation details: exact MCP concurrency/discovery/error semantics/trace fields; exact Context scope/schema/query/ordering/failure/reviewer operation; historical product requirement and Pilot-version mapping.
- Verifier should distinguish “canonical interview evidence missing” from “historical code definitely lacked the feature”.
