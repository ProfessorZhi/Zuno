<!-- Archive metadata: normalized without rewriting the historical record. -->
series: ARCHITECTURE_INTERVIEW
round_id: 005
execution_mode: AUTOMATED
status: ARCHIVED
base_sha: 4e3ab8773da4edfaa769d3d2f6c4dce3ea63ea15
archive_commit: RECORDED_IN_FINAL_HANDOFF
architecture_revision_commit: NOT_CHANGED_IN_THIS_TASK
round_format: LEGACY_SESSION_COMPRESSION
source_session: RB-WORKFLOW-V3-ROUND-005
# ARCHITECTURE_INTERVIEW — 005

本文件是正式 Red / Blue 对抗记录的单文件归档。它保留当时的核心问题、回答、Review/Score、决策和收口结果；不拥有今天的 Current Facts、Target Architecture 或实现授权。

## Session README: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/README.md`

# RB-WORKFLOW-V3-ROUND-005

本 Session 执行 `ZUNO-RED-BLUE-WORKFLOW-V3.1.3`，主题是深层失败、恢复、并发和架构生存性。
它是不可变的 Architecture Review 记录，不是 Runtime 集成测试、法院质量证明或 Production Readiness 证据。

## Status

- Baseline: `4e3ab8773da4edfaa769d3d2f6c4dce3ea63ea15`
- Result: COMPLETE
- Questions / Answers / Scores / Decisions: 100 / 100 / 100 / 100
- Novel / Regression: 80 / 20
- Raw / Normalized Score: `400/500` / `80.00`
- P0 / P1 / P2 / P3: 0 / 15 / 85 / 0
- A / I / E / X: 10 / 45 / 30 / 15
- New A-P0 / E-P0 / X-P0: 0 / 0 / 0
- Human Writing Review: WARNING; deterministic signals do not replace human reading
- Closure Classification Audit: PASS
- Canonical Sync: COMPLETE; Target refinement only
- Round-006: READY_NOT_STARTED

## Scope

问题采用场景、状态、时序、失败和 Ownership 冲突，覆盖版本屏障、Recovery、Memory contamination、Graph stale、Citation provenance、未知副作用、撤权竞态、Queue、滚动升级和 A/B/C 归因。Round-004 保持 immutable，历史 P0 仍由原 Evidence Closure Track 管理。

## Boundary

`facts_changed = NONE`。本 Session 不提升 Current、Measured、Verified 或 Production 状态，也不修改 Runtime、UI、Schema、Migration、Dependencies 或 Production Infrastructure。

## Session Manifest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/manifest.yaml`

protocol_version: ZUNO-RED-BLUE-WORKFLOW-V3.1.3
session_id: RB-WORKFLOW-V3-ROUND-005
round_id: RB-WORKFLOW-V3-ROUND-005
baseline_sha: 4e3ab8773da4edfaa769d3d2f6c4dce3ea63ea15
final_sha: recorded in final handoff
question_budget: 100
actual_question_count: 100
answer_count: 100
score_count: 100
decision_count: 100
novel_question_count: 80
regression_question_count: 20
novelty_threshold_percent: 80
regression_max_percent: 20
theme: Deep Failure / Recovery / Concurrency / Architecture Survival
human_writing_review: WARNING
human_continuity_review: WARNING_WITH_NO_STRUCTURAL_FAILURE
architecture_integrity: PASS
part_a_quality_gate: PASS
part_b_quality_gate: PASS
closure_class_audit: PASS
canonical_sync_status: COMPLETE
round_status: COMPLETE
raw_score: 400
normalized_score: 80.0
p0_count: 0
p1_count: 15
p2_count: 85
p3_count: 0
new_a_p0: 0
new_e_p0: 0
new_x_p0: 0
round_006_status: READY_NOT_STARTED
facts_changed: NONE
runtime_changed: NONE
schema_or_migration_changed: NONE
dependencies_changed: NONE
production_infra_changed: NONE
adr_escalation_count: 0
user_gate_escalation_count: 0
implementation_program: READY_FOR_TASK_DEFINITION
round_004_immutable: true
closure_class_distribution:
  A: 10
  I: 45
  E: 30
  X: 15
part_a_rewrite_count: 7
part_b_rewrite_count: 8

## Questions / Transcript: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/questions.md`

# Round-005 Questions

每题都包含场景、问题、攻击意图、证据和 Kill Condition；Target 场景不代表历史事实。

| ID | Type | 11+1 Lens | Canonical Owner Doc | Scenario | Question | Attack Intent | Required Evidence | Kill Condition |
|---|---|---|---|---|---|---|---|---|
| Q001 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | DomainVersion D31 已提交、Checkpoint 仍在 D30、Graph Projection 仍在 D29 | 恢复时谁是真相，谁负责把三个版本重新对齐 | 跨 Owner authority | reconciliation trace | Checkpoint 或 Graph 直接覆盖 Domain |
| Q002 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Host 和 Native Runtime 同时提交同一 Matter 的 FindingProposal | Admission 如何阻止两条路径形成两个事实版本 | external host boundary | admission audit | 任一路径可直接写 Canonical State |
| Q003 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Domain Transaction 成功但 Outbox 发布失败，重启后 Job 重投 | 恢复先看 Domain、Outbox 还是 Queue ACK，为什么 | business truth priority | outbox replay trace | ACK 被当成业务提交 |
| Q004 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Tool EffectReceipt 显示 outcome_unknown，而 Runtime 停在调用前 | Coordinator 如何决定 reconcile、retry 或 review | unknown side effect | provider operation trace | 无条件再次执行外部动作 |
| Q005 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Knowledge 返回带旧 ACL 的 EvidenceCandidate，Domain 已撤权 | 哪一层必须阻断候选进入计划，谁拥有最终拒绝权 | cross-layer security | denied retrieval trace | 检索结果直接进入 Finding |
| Q006 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | 两个 Service 都缓存 Matter Snapshot，版本更新只通知到一个 | 怎样检测并避免旧 Snapshot 继续规划 | snapshot freshness | generation comparison | 缓存命中即视为当前事实 |
| Q007 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | 服务拆分后一个请求跨 Domain、Runtime、Tool 三个失败域 | 哪些结果可以重试，哪些只能保留未知状态 | failure taxonomy | fault injection matrix | 所有错误都走同一 retry |
| Q008 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Reviewer 修改 Finding 后旧 Plan 仍有两个 Worker 在运行 | 人工决定怎样成为新的规划屏障并阻止旧分支提交 | review authority | review generation trace | Resume 覆盖人工决定 |
| Q009 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Model、Graph 和 Memory Provider 依次替换，结果仍要可审计 | 平台如何证明语义契约未被 Provider 状态绑架 | provider substitution | replacement comparison | Provider 直接拥有 Domain State |
| Q010 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | A/B/C 质量接近但 Native Runtime 成本明显更高 | 哪个复杂度先降级，谁拥有撤回决定 | reversal discipline | controlled benchmark | 结果不好仍永久保留全部组件 |
| Q011 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | 旧 11 模块文档与新服务边界对同一 Owner 给出不同说法 | 阅读和实现时哪个文档是唯一事实源 | taxonomy integrity | entrypoint and boundary verifier | 两套 Canonical Truth 并存 |
| Q012 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | 滚动发布中旧 Worker 只能读旧 Checkpoint，新 Worker 已接管队列 | 谁决定兼容、隔离、回滚或人工接管 | deployment/runtime contract | compatibility test | 不兼容 Checkpoint 被盲目执行 |
| Q013 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | 用户上传新证据后打开昨天的 WorkProduct | 界面如何解释 stale、可继续使用的部分和必须复核的部分 | product stale semantics | review and delivery trace | 旧报告仍显示为当前 |
| Q014 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | Reviewer A 接受 Finding，Reviewer B 随新证据拒绝它 | 最终 HumanDecision 如何排序，旧 WorkProduct 是否作废 | review conflict | decision lineage | 多个最终决定没有版本 |
| Q015 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | External Host 提交 Run 后断线，用户重新进入 Matter | 如何恢复 Run、MatterVersion 和权限，而不是依赖聊天记录 | async surface recovery | run status trace | 只能通过重新发起任务恢复 |
| Q016 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | 解析只完成部分页面但其中一页已有引用 | 产品怎样显示部分可用范围，避免把 partial 当 complete | partial delivery | document status audit | 半成品伪装完整 |
| Q017 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | Reviewer 驳回 Finding，但相关 Evidence 仍被另一项任务使用 | 驳回是删除候选、禁止复用还是触发新分析 | rejection propagation | proposal lineage | rejected proposal 被当作事实 |
| Q018 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | 导出 WorkProduct 的瞬间出现新 Conflict | 导出是否阻止、标记版本，或创建新的 immutable 产物 | delivery gate | export decision trace | stale 结果无提示交付 |
| Q019 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 同一 PDF 的内容 hash 相同但上传者和 Matter 不同 | Document identity、权限和幂等键如何同时判断 | document identity | hash and ACL trace | hash 相同即跨 Matter 复用 |
| Q020 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | OCR Worker 在页 40 完成后崩溃，页 1–39 已有临时 Chunk | 重试从哪个阶段开始，谁可以发布可检索版本 | partial parse recovery | stage checkpoint | 临时 Chunk 被当成完整版本 |
| Q021 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | Parser-v3 已发布 span，Parser-v4 改变页码映射 | 旧 Citation 如何保持 lineage，何时必须重新生成 | citation stability | span compatibility test | 新 Parser 静默覆盖旧来源 |
| Q022 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 同一 DocumentVersion 的两个 Parser 并发完成且质量不同 | 谁只能提交 Proposal，谁有权发布 Projection | publication authority | parser comparison receipt | 后完成者直接覆盖先完成者 |
| Q023 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 上传取消发生在 Object Store 写入后、Domain Commit 前 | 孤儿 Artifact 如何标记、清理和防止变成业务事实 | cancellation boundary | artifact audit | 孤儿文件被索引为正式材料 |
| Q024 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | Ingestion Job 重复投递且两个 Worker 都开始 Embedding | Job identity、stage idempotency 和发布门如何协作 | duplicate ingestion | duplicate worker trace | 重复写入不可区分 |
| Q025 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | Parser 升级后旧版本正在被检索，新版本只完成一半 | 检索使用哪个 published generation，如何回滚 | parser rollout | publication generation | 半成品与旧版本混合 |
| Q026 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Graph edge 来自已撤回的 DocumentVersion，Hybrid 仍返回新版本 | Retrieval Gate 如何拒绝 stale edge 并保留可解释降级 | projection staleness | index generation trace | 合法路径支持错误结论 |
| Q027 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | 一个 Claim 需要三份材料共同证明，单个 top-k 都不完整 | Evidence Sufficiency 在检索、Join 还是 Domain Gate 判断 | multi-evidence closure | sufficiency report | top-k 数量被当作充分性 |
| Q028 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Exact Statute 查询被 Graph 改写后召回相邻法条 | QueryClass 如何选择 Lexical/Hybrid，谁阻止错误扩展 | conditional graph | query-class ablation | Graph 永久优先 |
| Q029 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Agent 选择了错误 Matter Scope，但索引返回了相关文本 | ACL 和 Scope 如何 fail closed 并留下拒绝证据 | scope isolation | scope-denied trace | 相关性掩盖越权 |
| Q030 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Rerank Provider 超时，初始候选仍在缓存中 | 系统返回 no_evidence、降级结果还是 blocked，怎样区分 | typed retrieval failure | fallback comparison | 超时伪装成空结果 |
| Q031 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Citation 指向 Chunk，但原文 span 在重切分后已移动 | 谁校验 CitationLineage，旧引用如何失效 | citation provenance | span validation | 引用正确性不可测 |
| Q032 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | 新 DocumentVersion 只影响一组 Graph 边，不影响全图 | Projection 如何做定向重建并声明覆盖范围 | targeted rebuild | rebuild cursor | 每次都全量重建 |
| Q033 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Hybrid 与 Graph 给出互相冲突的 EvidenceCandidate | Agent 能否选择一个，还是必须进入冲突处理 | candidate semantics | candidate conflict record | 候选被升级为事实 |
| Q034 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | IndexVersion 落后 DomainVersion，但召回结果看起来相关 | 哪个版本屏障允许进入 Plan，旧结果如何标记 | version barrier | index-domain comparison | 相关性绕过版本门 |
| Q035 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Graph 成本上升但跨文档任务没有稳定收益 | 谁触发条件降级，如何防止实现惯性 | component survival | graph kill benchmark | 没有收益仍固定部署 |
| Q036 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | Provider-A 超时后切换 Provider-B，B 返回不同 structured output | 这是同一 Attempt 的 fallback 还是新的 Attempt，谁归一化 | provider fallback | attempt and schema trace | Agent 各处处理供应商分支 |
| Q037 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | 长 Run 的预算只剩一个并行 Step，但 fallback 需要更多 token | 预算由谁裁剪，如何避免 fallback 偷渡新预算 | budget accounting | usage receipt | 预算账本无法解释 |
| Q038 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | 模型版本升级后旧 Plan 仍要求旧 Tool Schema | 兼容窗口如何决定继续、转换或重规划 | model contract drift | schema compatibility | 模型升级静默改变计划 |
| Q039 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | Gateway 暂时不可用，但已有可审查的 Plan 和缓存 Observation | 降级能否继续，哪些动作必须停止 | degraded mode | outage policy trace | 缓存结果隐式改变安全策略 |
| Q040 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | A/B 两个架构使用不同 fallback 链和不同 token 上限 | 如何避免把 Provider 差异误归因于 Runtime | benchmark attribution | A/B manifest | 比较结果不可解释 |
| Q041 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Memory Provider 写入一条后来被 Reviewer 拒绝的经验 | 下一次 Recall 如何知道它是 rejected proposal 而非事实 | memory promotion | provenance and promotion trace | 候选污染 Domain Truth |
| Q042 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Run Crash 后重放同一个 Step，working context 被再次追加 | Replay 如何幂等，如何避免上下文越来越长 | context replay | replay ledger | 重放改变输入语义 |
| Q043 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Matter 权限撤销后旧 Memory 仍能被相似度命中 | Recall Gate 在 Provider 前后分别检查什么 | memory ACL | access epoch trace | Memory 绕过权限 |
| Q044 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | OpenViking Provider 被替换，旧 Memory 有不同的分层字段 | 哪些语义必须由 Zuno Contract 保持，哪些可以丢弃 | provider replacement | substitution test | Provider 成为事实源 |
| Q045 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | User preference 与当前 Case Fact 冲突 | Planner 如何按 provenance 和 authority 排序 | precedence | precedence trace | 偏好覆盖案件事实 |
| Q046 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Memory 已 stale 但索引仍然命中 | 是降权、拒绝还是要求重新验证，谁做决定 | staleness gate | stale recall test | 旧经验无标记复用 |
| Q047 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | 多个 Specialist Agent 共享 Matter Context | 谁有写权，如何审计和隔离不同 scope | shared context ownership | write permission audit | 任意 Agent 污染共享记忆 |
| Q048 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Recall 改变 EvidenceRequirement 的排序 | 是否必须显式生成 Replan，而不是让 Memory 隐式改图 | memory influence | plan diff trace | 隐式规划不可审计 |
| Q049 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | PlanVersion P12 基于 DomainVersion D40，用户提交 D41 | Replan Barrier 如何处理已完成、运行中和未派发的 Step | version barrier | generation trace | 旧分支直接合并 |
| Q050 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 必需 Worker 超时、可选 Worker 成功 | Join 是否停止、降级还是进入 Review，谁定义足够 | join policy | join decision matrix | 空结果伪装成功 |
| Q051 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 两个 BranchResult 同时提交且顺序不同 | Reducer 如何保证确定性并拒绝过期输入 | reducer determinism | replay comparison | 到达顺序决定事实 |
| Q052 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Replan 发生时一个 Step 已发出 Tool 请求 | 哪些 Step 可取消，哪些必须进入 unknown outcome | cancellation race | cancel-effect trace | 新旧计划同时产生副作用 |
| Q053 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Reflection 发现权限不足但建议新增 Tool | 它能修改 Plan 还是只能请求人工决定 | permission boundary | denied action trace | Reflection 提升权限 |
| Q054 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 并行分支同时消耗最后一段 Budget | 谁原子化扣减预算，谁裁剪剩余工作 | budget race | budget ledger | 超预算运行 |
| Q055 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Coordinator 重启时 Checkpoint 只写了一半 | Resume 如何找到最后完整控制状态 | checkpoint atomicity | crash replay | 部分 Checkpoint 被执行 |
| Q056 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Worker 返回未声明的 ReplanRequest | Coordinator 如何校验来源、Schema 和权限 | replan admission | schema rejection | 任意 Worker 改图 |
| Q057 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Human Review 修改事实，旧 Plan 仍在队列中 | Plan 如何变 stale，旧 Proposal 如何被拒绝 | review barrier | domain generation | 旧计划继续写候选 |
| Q058 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 同一 Step Job 被投递两次且第一次响应丢失 | Step Attempt 和外部 Receipt 如何去重 | step idempotency | duplicate job trace | 双写 Proposal 或 Effect |
| Q059 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Join 少一个证据分支但已有足够候选 | 谁定义 Evidence Sufficiency，Coordinator 能否自行判断 | evidence gate | sufficiency evidence | Coordinator 代替 Domain Gate |
| Q060 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Tool 返回 outcome_unknown，模型建议立即 retry | Runtime 如何强制先 reconcile | effect reconciliation | operation id lookup | 盲目重复副作用 |
| Q061 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 用户取消 Run 后 Worker 返回成功 Proposal | 结果是否保留为候选，谁阻止它进入 Canonical State | cancel race | cancel admission trace | 取消后提交事实 |
| Q062 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | LangGraph State 显示 Node 完成但 Domain Transaction 未提交 | Recovery 谁先读，如何避免假装业务完成 | state separation | domain-runtime reconciliation | Checkpoint 当业务事实 |
| Q063 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 两个 Coordinator 因网络分区都认为自己拥有 Run | Single Controller 如何以 CAS 或 lease 防止双重 authority | controller split brain | lease and CAS trace | 双 Coordinator 同时提交 |
| Q064 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Event Capability v3 增加字段，旧 Agent 只识别 v2 | Provider 如何兼容，Agent 是否需要业务分支 | capability version | contract compatibility | 算法写死 Agent |
| Q065 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Conflict Provider 置信度下降但仍有新 Evidence | 能否自动形成 ConflictVersion，还是必须 Proposal Admission | proposal admission | admission test | Provider 直写事实 |
| Q066 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Fact-Article Provider 返回不同 StatuteVersion | ApplicableLaw 如何绑定法条版本并阻止混用 | legal version | version trace | 法条版本混淆 |
| Q067 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Similar Case Provider 不可用且任务声明类案不是必需 | 如何降级而不伪造类案结果 | capability failure | fallback evidence | 空结果被写成类案 |
| Q068 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Skill 指示与 Security Policy 冲突 | 执行时谁拥有优先级，Skill 能否请求而非授权 | policy precedence | denied tool trace | Skill 提升权限 |
| Q069 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | 同一 Capability 有本地模型和 LLM Provider | 怎样保持输入输出契约并公平评估替换收益 | provider resolution | capability benchmark | 供应商差异隐藏 |
| Q070 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | 外部写操作已成功但 HTTP 响应丢失 | Runtime 如何用 ProviderOperationId 避免第二次写 | unknown outcome | operation lookup | 盲重试 |
| Q071 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Approval 在执行前被撤销 | Sandbox 是否重新授权，旧 PreparedAction 是否作废 | execute-time auth | revocation test | 旧批准继续有效 |
| Q072 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | 文档中的 Prompt Injection 改写 Tool 参数 | 谁验证参数和 EffectScope，谁把内容标为不可信 | untrusted input | injection trace | 文档控制 Tool |
| Q073 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | 同一 EffectReceipt 被两个 Worker 消费 | Receipt identity 和 IdempotencyKey 如何阻止重复 Effect | receipt idempotency | duplicate effect test | 重复副作用 |
| Q074 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Sandbox 崩溃且 Provider 没有返回结果 | 系统怎样进入 reconciliation，而不是直接 retry | sandbox crash | receipt lookup | 未知结果被当失败 |
| Q075 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Tool timeout 与 network deny 同时发生 | 如何区分 typed failure、未知结果和确定拒绝 | failure typing | failure taxonomy | 所有错误走同路径 |
| Q076 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Secret rotation 发生在长 Run 中 | 下一个调用使用哪个 SecretEpoch，旧 lease 是否可读 | secret lease | rotation trace | 旧 Secret 无期限继续 |
| Q077 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Tool Provider v2 输出字段与 v1 不兼容 | Worker 能否安全降级，何时必须停止执行 | provider compatibility | compatibility test | 结果格式静默变化 |
| Q078 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | 用户取消不可逆 Effect，同时 Provider 已收到请求 | 取消状态如何表达，不能把 cancel 当作未执行 | cancel-effect race | cancel and effect trace | 取消承诺虚假 |
| Q079 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Effect 成功但 Domain Commit 失败 | 谁创建 Effect reconciliation，何时允许再次提交业务状态 | effect/domain split | reconciliation report | Receipt 被删除或重复执行 |
| Q080 | NOVEL | 09 Security | docs/project/security/security-architecture.md | 用户失去 Matter 权限但 Run 尚未结束 | 下一次 Retrieval 和 Tool Call 在哪个 Epoch 重新授权 | authorization race | policy trace | 只在 Run 创建时授权 |
| Q081 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Prompt Injection 要求把案件内容发往外部 API | Security Boundary 如何阻断并留下可审计拒绝 | egress policy | no-egress test | 文档改变策略 |
| Q082 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Tenant A 的索引被 Tenant B 查询且文本相似 | 哪一层做租户隔离，为什么不能只靠 Prompt | tenant isolation | cross-tenant test | 只靠模型自律 |
| Q083 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | PreparedAction 携带旧 Approval 和旧 SecurityEpoch | Queue 中的动作执行前如何失效 | approval epoch | revocation evidence | 旧批准继续执行 |
| Q084 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Tool 失败信息包含 Secret，Trace 采样后上传 | 脱敏在日志、Trace 和 Provider Receipt 哪一层完成 | secret hygiene | audit scan | Trace 泄漏 Secret |
| Q085 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Sandbox 进程尝试读取未授权文件 | 策略拒绝和容器逃逸证据分别由谁记录 | sandbox boundary | escape test | 把隔离声明当证据 |
| Q086 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | 用户切换 Tenant 后复用旧 Session Token | Session、Matter 和 Memory Scope 如何重新绑定 | tenant switching | scope binding trace | 跨租户复用上下文 |
| Q087 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Tool Version 升级后旧 Approval 的 action hash 仍相同 | 是否要求重新授权，兼容性由谁证明 | tool version trust | version approval test | 哈希相同掩盖策略变化 |
| Q088 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Trace 采样丢掉了 Replan 和拒绝 Span | 如何判断一次 Run 是成功、阻塞还是被安全策略拒绝 | trace completeness | missing-span audit | 缺 Span 被计为成功 |
| Q089 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Reviewer 对 Evidence Sufficiency 意见不一致 | 指标如何记录分歧，是否可以直接平均 | reviewer disagreement | adjudication protocol | 分歧被隐藏 |
| Q090 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | A/B/C 中 C 因 Provider outage 没有结果 | 如何区分 blocked、unavailable 和质量失败 | denominator integrity | blocked result manifest | 无结果折成零分 |
| Q091 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | 同一任务发生三次 retry 和一次 replan | Latency、Cost 和 Model Calls 如何归因而不重复计数 | attempt accounting | usage ledger | 成本指标不可解释 |
| Q092 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Graph 与 Hybrid 都提高最终 LLM Judge 分数但引用变差 | 哪个指标阻止错误的总体结论 | multi-metric gate | citation and claim report | 只看 Judge score |
| Q093 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | 故障注入只覆盖 API timeout，未覆盖 crash replay | 怎样证明 Recovery Contract 而不是只证明重试 | fault coverage | fault matrix | 测试覆盖假象 |
| Q094 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Runtime v2 已滚动到 60%，40 分钟 Run 仍只有 v1 Checkpoint | 部署如何选择兼容读取、暂停、回滚或隔离 | checkpoint compatibility | rolling upgrade test | 旧 Checkpoint 被新 Worker 盲读 |
| Q095 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Queue drain 后仍有一个 inflight Tool Job | 升级完成的判定是否等待 Effect 对账 | drain semantics | drain and receipt trace | 排空只看队列长度 |
| Q096 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Schema 向前兼容但旧 Worker 写入缺少新字段 | 服务如何在窗口内读写并最终关闭兼容分支 | schema window | compatibility matrix | 滚动升级产生不可读状态 |
| Q097 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | 备份恢复后 Domain State 已恢复，Projection 和 Object Artifact 未恢复 | 系统何时允许重新开放 Retrieval 和 WorkProduct | restore completeness | restore drill | 数据库恢复即宣称可用 |
| Q098 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Knowledge Worker 占满 CPU，Agent Runtime 长时间饥饿 | 调度和资源隔离如何保护长 Run 与短请求 | resource starvation | load isolation test | 用户数指标掩盖资源竞争 |
| Q099 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | 两个 Worker 都认为自己是队列主消费者 | 如何避免 split-brain-like execution 和重复外部动作 | worker leadership | lease/fencing test | 心跳丢失导致双执行 |
| Q100 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Production 配置存在但没有 HA、故障注入或 RPO/RTO 结果 | 部署状态如何保持 NOT_ESTABLISHED 而不是升级宣传 | qualification boundary | production evidence ledger | 配置文件被当生产证据 |

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/blue-answers.md`

# Round-005 Blue Answers

每个回答先直接回答，再记录 Contract、Owner、Failure、Recovery、Tradeoff、Evidence 和文档影响。

| ID | Direct Answer | Decision | Owner | State | Failure / Recovery | Tradeoff | Evidence / Gap | Document Impact |
|---|---|---|---|---|---|---|---|---|
| Q001 | 不能继续；先在架构层拒绝这条路径，直到唯一 Owner、版本屏障和恢复权威被明确。 | CLARIFY | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | reconciliation trace / gap remains | PART_A |
| Q002 | 不能继续；先在架构层拒绝这条路径，直到唯一 Owner、版本屏障和恢复权威被明确。 | CLARIFY | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | admission audit / gap remains | PART_B |
| Q003 | 不能继续；先在架构层拒绝这条路径，直到唯一 Owner、版本屏障和恢复权威被明确。 | CLARIFY | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | outbox replay trace / gap remains | BOTH |
| Q004 | 不能继续；先在架构层拒绝这条路径，直到唯一 Owner、版本屏障和恢复权威被明确。 | CLARIFY | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | provider operation trace / gap remains | PART_A |
| Q005 | 不能继续；先在架构层拒绝这条路径，直到唯一 Owner、版本屏障和恢复权威被明确。 | CLARIFY | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | denied retrieval trace / gap remains | PART_B |
| Q006 | 不能继续；先在架构层拒绝这条路径，直到唯一 Owner、版本屏障和恢复权威被明确。 | CLARIFY | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | generation comparison / gap remains | BOTH |
| Q007 | 不能继续；先在架构层拒绝这条路径，直到唯一 Owner、版本屏障和恢复权威被明确。 | CLARIFY | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | fault injection matrix / gap remains | PART_A |
| Q008 | 不能继续；先在架构层拒绝这条路径，直到唯一 Owner、版本屏障和恢复权威被明确。 | CLARIFY | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | review generation trace / gap remains | PART_B |
| Q009 | 不能继续；先在架构层拒绝这条路径，直到唯一 Owner、版本屏障和恢复权威被明确。 | CLARIFY | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | replacement comparison / gap remains | BOTH |
| Q010 | 不能继续；先在架构层拒绝这条路径，直到唯一 Owner、版本屏障和恢复权威被明确。 | CLARIFY | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | controlled benchmark / gap remains | PART_A |
| Q011 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | entrypoint and boundary verifier / gap remains | PART_B |
| Q012 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/architecture/architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | compatibility test / gap remains | BOTH |
| Q013 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | review and delivery trace / gap remains | PART_A |
| Q014 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | decision lineage / gap remains | PART_B |
| Q015 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | run status trace / gap remains | BOTH |
| Q016 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | document status audit / gap remains | PART_A |
| Q017 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | proposal lineage / gap remains | PART_B |
| Q018 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | export decision trace / gap remains | BOTH |
| Q019 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | hash and ACL trace / gap remains | PART_A |
| Q020 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | stage checkpoint / gap remains | PART_B |
| Q021 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | span compatibility test / gap remains | BOTH |
| Q022 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | parser comparison receipt / gap remains | PART_A |
| Q023 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | artifact audit / gap remains | PART_B |
| Q024 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | duplicate worker trace / gap remains | BOTH |
| Q025 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | publication generation / gap remains | PART_A |
| Q026 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | index generation trace / gap remains | PART_B |
| Q027 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | sufficiency report / gap remains | BOTH |
| Q028 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | query-class ablation / gap remains | PART_A |
| Q029 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | scope-denied trace / gap remains | PART_B |
| Q030 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | fallback comparison / gap remains | BOTH |
| Q031 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | span validation / gap remains | PART_A |
| Q032 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | rebuild cursor / gap remains | PART_B |
| Q033 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | candidate conflict record / gap remains | BOTH |
| Q034 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | index-domain comparison / gap remains | PART_A |
| Q035 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | graph kill benchmark / gap remains | PART_B |
| Q036 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | attempt and schema trace / gap remains | PART_A |
| Q037 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | usage receipt / gap remains | PART_A |
| Q038 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | schema compatibility / gap remains | PART_B |
| Q039 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | outage policy trace / gap remains | BOTH |
| Q040 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | A/B manifest / gap remains | PART_A |
| Q041 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | provenance and promotion trace / gap remains | PART_B |
| Q042 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | replay ledger / gap remains | PART_A |
| Q043 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | access epoch trace / gap remains | PART_A |
| Q044 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | substitution test / gap remains | PART_B |
| Q045 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | precedence trace / gap remains | BOTH |
| Q046 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | stale recall test / gap remains | PART_A |
| Q047 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | write permission audit / gap remains | PART_B |
| Q048 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | plan diff trace / gap remains | BOTH |
| Q049 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | generation trace / gap remains | PART_A |
| Q050 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | join decision matrix / gap remains | PART_A |
| Q051 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | replay comparison / gap remains | BOTH |
| Q052 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | cancel-effect trace / gap remains | PART_A |
| Q053 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | denied action trace / gap remains | PART_B |
| Q054 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | budget ledger / gap remains | BOTH |
| Q055 | Contract 已经清楚；执行层必须把这个状态、幂等键和恢复动作实现出来，未完成前只能返回受限结果。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | crash replay / gap remains | PART_A |
| Q056 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | schema rejection / gap remains | PART_B |
| Q057 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | domain generation / gap remains | BOTH |
| Q058 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | duplicate job trace / gap remains | PART_A |
| Q059 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | sufficiency evidence / gap remains | PART_B |
| Q060 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | operation id lookup / gap remains | BOTH |
| Q061 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | cancel admission trace / gap remains | PART_A |
| Q062 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | domain-runtime reconciliation / gap remains | PART_B |
| Q063 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | lease and CAS trace / gap remains | BOTH |
| Q064 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | contract compatibility / gap remains | PART_A |
| Q065 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | admission test / gap remains | PART_B |
| Q066 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | version trace / gap remains | BOTH |
| Q067 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | fallback evidence / gap remains | PART_A |
| Q068 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | denied tool trace / gap remains | PART_B |
| Q069 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | capability benchmark / gap remains | BOTH |
| Q070 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | operation lookup / gap remains | PART_A |
| Q071 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | revocation test / gap remains | PART_B |
| Q072 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | injection trace / gap remains | BOTH |
| Q073 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | duplicate effect test / gap remains | PART_A |
| Q074 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | receipt lookup / gap remains | PART_B |
| Q075 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | failure taxonomy / gap remains | BOTH |
| Q076 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | rotation trace / gap remains | PART_A |
| Q077 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | compatibility test / gap remains | PART_B |
| Q078 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | cancel and effect trace / gap remains | BOTH |
| Q079 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | reconciliation report / gap remains | PART_A |
| Q080 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | policy trace / gap remains | PART_B |
| Q081 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | no-egress test / gap remains | BOTH |
| Q082 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | cross-tenant test / gap remains | PART_A |
| Q083 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | revocation evidence / gap remains | PART_B |
| Q084 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | audit scan / gap remains | BOTH |
| Q085 | 可以按既定 Contract 运行，但不能把收益写成结论；先用受控 Benchmark 或故障注入建立可归因证据。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | escape test / gap remains | PART_A |
| Q086 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | scope binding trace / gap remains | PART_B |
| Q087 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/security/security-architecture.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | version approval test / gap remains | BOTH |
| Q088 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | missing-span audit / gap remains | PART_A |
| Q089 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | adjudication protocol / gap remains | PART_B |
| Q090 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | blocked result manifest / gap remains | BOTH |
| Q091 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | usage ledger / gap remains | PART_A |
| Q092 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | citation and claim report / gap remains | PART_B |
| Q093 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | fault matrix / gap remains | PART_A |
| Q094 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | rolling upgrade test / gap remains | PART_A |
| Q095 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | drain and receipt trace / gap remains | PART_B |
| Q096 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | compatibility matrix / gap remains | BOTH |
| Q097 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | restore drill / gap remains | PART_A |
| Q098 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | load isolation test / gap remains | PART_B |
| Q099 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | lease/fencing test / gap remains | BOTH |
| Q100 | Target 可以保留为资格条件，但真实 Sandbox、Provider、HA 或生产环境证据取得前不得升级成熟度。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | proposal/target state | typed failure → bounded retry or reconciliation | explicit cost and reversal condition | production evidence ledger / gap remains | PART_A |

---

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/red-scores.md`

# Round-005 Red Scores

Severity 与 Closure Class 正交；Explanation Quality 不进入 500 分。

| ID | Score | Severity | Primary Closure Class | Closure Class Rationale | Explanation Quality | Document Impact | Risk | Delta Ref |
|---|---:|---|---|---|---|---|---|---|
| Q001 | 3 | P1 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLEAR | PART_A | P1/P2 review | D001 |
| Q002 | 3 | P1 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLEAR | PART_B | P1/P2 review | D001 |
| Q003 | 3 | P1 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLEAR | BOTH | P1/P2 review | D001 |
| Q004 | 3 | P1 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | DENSE | PART_A | P1/P2 review | D001 |
| Q005 | 3 | P1 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLEAR | PART_B | P1/P2 review | D001 |
| Q006 | 4 | P1 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLEAR | BOTH | P1/P2 review | D001 |
| Q007 | 4 | P1 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLEAR | PART_A | P1/P2 review | D001 |
| Q008 | 4 | P1 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | DENSE | PART_B | P1/P2 review | D001 |
| Q009 | 4 | P1 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLEAR | BOTH | P1/P2 review | D001 |
| Q010 | 4 | P1 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLEAR | PART_A | P1/P2 review | D001 |
| Q011 | 4 | P1 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D001 |
| Q012 | 4 | P1 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | BOTH | P1/P2 review | D001 |
| Q013 | 4 | P1 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D002 |
| Q014 | 4 | P1 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D002 |
| Q015 | 4 | P1 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | BOTH | P1/P2 review | D002 |
| Q016 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | PART_A | P1/P2 review | D002 |
| Q017 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D002 |
| Q018 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | BOTH | P1/P2 review | D002 |
| Q019 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D003 |
| Q020 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | PART_B | P1/P2 review | D003 |
| Q021 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | BOTH | P1/P2 review | D003 |
| Q022 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D003 |
| Q023 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D003 |
| Q024 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | BOTH | P1/P2 review | D003 |
| Q025 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D003 |
| Q026 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D004 |
| Q027 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | BOTH | P1/P2 review | D004 |
| Q028 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | PART_A | P1/P2 review | D004 |
| Q029 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D004 |
| Q030 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | BOTH | P1/P2 review | D004 |
| Q031 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D004 |
| Q032 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | PART_B | P1/P2 review | D004 |
| Q033 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | BOTH | P1/P2 review | D004 |
| Q034 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D004 |
| Q035 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D004 |
| Q036 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | PART_A | P1/P2 review | D005 |
| Q037 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D005 |
| Q038 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D005 |
| Q039 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | BOTH | P1/P2 review | D005 |
| Q040 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | PART_A | P1/P2 review | D005 |
| Q041 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D006 |
| Q042 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D006 |
| Q043 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D006 |
| Q044 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | PART_B | P1/P2 review | D006 |
| Q045 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | BOTH | P1/P2 review | D006 |
| Q046 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D006 |
| Q047 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D006 |
| Q048 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | BOTH | P1/P2 review | D006 |
| Q049 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D007 |
| Q050 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D007 |
| Q051 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | BOTH | P1/P2 review | D007 |
| Q052 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | DENSE | PART_A | P1/P2 review | D007 |
| Q053 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_B | P1/P2 review | D007 |
| Q054 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | BOTH | P1/P2 review | D007 |
| Q055 | 4 | P2 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 | CLEAR | PART_A | P1/P2 review | D007 |
| Q056 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | DENSE | PART_B | P1/P2 review | D007 |
| Q057 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | BOTH | P1/P2 review | D007 |
| Q058 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_A | P1/P2 review | D007 |
| Q059 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_B | P1/P2 review | D007 |
| Q060 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | DENSE | BOTH | P1/P2 review | D007 |
| Q061 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_A | P1/P2 review | D007 |
| Q062 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_B | P1/P2 review | D007 |
| Q063 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | BOTH | P1/P2 review | D007 |
| Q064 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | DENSE | PART_A | P1/P2 review | D008 |
| Q065 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_B | P1/P2 review | D008 |
| Q066 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | BOTH | P1/P2 review | D008 |
| Q067 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_A | P1/P2 review | D008 |
| Q068 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | DENSE | PART_B | P1/P2 review | D008 |
| Q069 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | BOTH | P1/P2 review | D008 |
| Q070 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_A | P1/P2 review | D009 |
| Q071 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_B | P1/P2 review | D009 |
| Q072 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | DENSE | BOTH | P1/P2 review | D009 |
| Q073 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_A | P1/P2 review | D009 |
| Q074 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_B | P1/P2 review | D009 |
| Q075 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | BOTH | P1/P2 review | D009 |
| Q076 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | DENSE | PART_A | P1/P2 review | D009 |
| Q077 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_B | P1/P2 review | D009 |
| Q078 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | BOTH | P1/P2 review | D009 |
| Q079 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_A | P1/P2 review | D009 |
| Q080 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | DENSE | PART_B | P1/P2 review | D010 |
| Q081 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | BOTH | P1/P2 review | D010 |
| Q082 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_A | P1/P2 review | D010 |
| Q083 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_B | P1/P2 review | D010 |
| Q084 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | DENSE | BOTH | P1/P2 review | D010 |
| Q085 | 4 | P2 | E | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | CLEAR | PART_A | P1/P2 review | D010 |
| Q086 | 4 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | PART_B | P1/P2 review | D010 |
| Q087 | 4 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | BOTH | P1/P2 review | D010 |
| Q088 | 4 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | DENSE | PART_A | P1/P2 review | D011 |
| Q089 | 4 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | PART_B | P1/P2 review | D011 |
| Q090 | 4 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | BOTH | P1/P2 review | D011 |
| Q091 | 4 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | PART_A | P1/P2 review | D011 |
| Q092 | 4 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | DENSE | PART_B | P1/P2 review | D011 |
| Q093 | 4 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | PART_A | P1/P2 review | D011 |
| Q094 | 4 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | PART_A | P1/P2 review | D012 |
| Q095 | 4 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | PART_B | P1/P2 review | D012 |
| Q096 | 5 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | DENSE | BOTH | P1/P2 review | D012 |
| Q097 | 5 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | PART_A | P1/P2 review | D012 |
| Q098 | 5 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | PART_B | P1/P2 review | D012 |
| Q099 | 5 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | CLEAR | BOTH | P1/P2 review | D012 |
| Q100 | 5 | P2 | X | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | DENSE | PART_A | P1/P2 review | D012 |

---

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/scorecard.md`

# Round-005 Scorecard

| Measure | Result |
|---|---:|
| Raw score | 400 / 500 |
| Normalized | 80.00 |
| P0 / P1 / P2 / P3 | 0 / 15 / 85 / 0 |
| A / I / E / X | 10 / 45 / 30 / 15 |
| Part A / Part B | PASS / PASS |
| Human Writing | WARNING |
| Closure Audit | PASS |
| Canonical Sync | COMPLETE |

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/blue-decisions.md`

# Round-005 Blue Decisions

每题只有一个 Primary Closure Class；Secondary Gaps 记录并行缺口，不改变主要阻塞 Gate。

| ID | Primary Closure Class | Secondary Gaps | Closure Class Rationale | Decision | Canonical Owner | State | Failure / Recovery | Idempotency | Document Impact | Required Evidence | Delta Ref | Sync Mode | Part A / Part B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q001 | A | NONE | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLARIFY | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | reconciliation trace | D001 | FULL_PART_REWRITE | PART_A/YES |
| Q002 | A | NONE | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLARIFY | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | admission audit | D001 | FULL_PART_REWRITE | PART_B/NO |
| Q003 | A | NONE | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLARIFY | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | outbox replay trace | D001 | FULL_PART_REWRITE | BOTH/YES |
| Q004 | A | NONE | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLARIFY | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | provider operation trace | D001 | FULL_PART_REWRITE | PART_A/YES |
| Q005 | A | NONE | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLARIFY | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | denied retrieval trace | D001 | FULL_PART_REWRITE | PART_B/NO |
| Q006 | A | NONE | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLARIFY | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | generation comparison | D001 | FULL_PART_REWRITE | BOTH/YES |
| Q007 | A | NONE | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLARIFY | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | fault injection matrix | D001 | FULL_PART_REWRITE | PART_A/YES |
| Q008 | A | NONE | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLARIFY | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | review generation trace | D001 | FULL_PART_REWRITE | PART_B/NO |
| Q009 | A | NONE | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLARIFY | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | replacement comparison | D001 | FULL_PART_REWRITE | BOTH/YES |
| Q010 | A | NONE | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 | CLARIFY | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | controlled benchmark | D001 | FULL_PART_REWRITE | PART_A/YES |
| Q011 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | entrypoint and boundary verifier | D001 | FULL_PART_REWRITE | PART_B/NO |
| Q012 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/architecture/architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | compatibility test | D001 | FULL_PART_REWRITE | BOTH/YES |
| Q013 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | review and delivery trace | D002 | SECTION_REWRITE | PART_A/YES |
| Q014 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | decision lineage | D002 | SECTION_REWRITE | PART_B/NO |
| Q015 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | run status trace | D002 | SECTION_REWRITE | BOTH/YES |
| Q016 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | document status audit | D002 | SECTION_REWRITE | PART_A/YES |
| Q017 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | proposal lineage | D002 | SECTION_REWRITE | PART_B/NO |
| Q018 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/product/product-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | export decision trace | D002 | SECTION_REWRITE | BOTH/YES |
| Q019 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | hash and ACL trace | D003 | SECTION_REWRITE | PART_A/YES |
| Q020 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | stage checkpoint | D003 | SECTION_REWRITE | PART_B/NO |
| Q021 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | span compatibility test | D003 | SECTION_REWRITE | BOTH/YES |
| Q022 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | parser comparison receipt | D003 | SECTION_REWRITE | PART_A/YES |
| Q023 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | artifact audit | D003 | SECTION_REWRITE | PART_B/NO |
| Q024 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | duplicate worker trace | D003 | SECTION_REWRITE | BOTH/YES |
| Q025 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | publication generation | D003 | SECTION_REWRITE | PART_A/YES |
| Q026 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | index generation trace | D004 | FULL_PART_REWRITE | PART_B/NO |
| Q027 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | sufficiency report | D004 | FULL_PART_REWRITE | BOTH/YES |
| Q028 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | query-class ablation | D004 | FULL_PART_REWRITE | PART_A/YES |
| Q029 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | scope-denied trace | D004 | FULL_PART_REWRITE | PART_B/NO |
| Q030 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | fallback comparison | D004 | FULL_PART_REWRITE | BOTH/YES |
| Q031 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | span validation | D004 | FULL_PART_REWRITE | PART_A/YES |
| Q032 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | rebuild cursor | D004 | FULL_PART_REWRITE | PART_B/NO |
| Q033 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | candidate conflict record | D004 | FULL_PART_REWRITE | BOTH/YES |
| Q034 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | index-domain comparison | D004 | FULL_PART_REWRITE | PART_A/YES |
| Q035 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/knowledge/knowledge-evidence-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | graph kill benchmark | D004 | FULL_PART_REWRITE | PART_B/NO |
| Q036 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | attempt and schema trace | D005 | SECTION_REWRITE | PART_A/YES |
| Q037 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | usage receipt | D005 | SECTION_REWRITE | PART_A/YES |
| Q038 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | schema compatibility | D005 | SECTION_REWRITE | PART_B/NO |
| Q039 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | outage policy trace | D005 | SECTION_REWRITE | BOTH/YES |
| Q040 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | A/B manifest | D005 | SECTION_REWRITE | PART_A/YES |
| Q041 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | provenance and promotion trace | D006 | FULL_PART_REWRITE | PART_B/NO |
| Q042 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | replay ledger | D006 | FULL_PART_REWRITE | PART_A/YES |
| Q043 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | access epoch trace | D006 | FULL_PART_REWRITE | PART_A/YES |
| Q044 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | substitution test | D006 | FULL_PART_REWRITE | PART_B/NO |
| Q045 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | precedence trace | D006 | FULL_PART_REWRITE | BOTH/YES |
| Q046 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | stale recall test | D006 | FULL_PART_REWRITE | PART_A/YES |
| Q047 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | write permission audit | D006 | FULL_PART_REWRITE | PART_B/NO |
| Q048 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | plan diff trace | D006 | FULL_PART_REWRITE | BOTH/YES |
| Q049 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | generation trace | D007 | FULL_PART_REWRITE | PART_A/YES |
| Q050 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | join decision matrix | D007 | FULL_PART_REWRITE | PART_A/YES |
| Q051 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | replay comparison | D007 | FULL_PART_REWRITE | BOTH/YES |
| Q052 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | cancel-effect trace | D007 | FULL_PART_REWRITE | PART_A/YES |
| Q053 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | denied action trace | D007 | FULL_PART_REWRITE | PART_B/NO |
| Q054 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | budget ledger | D007 | FULL_PART_REWRITE | BOTH/YES |
| Q055 | I | NONE | 设计路径可执行，主要缺的是实现、测试或运行接线。 | IMPLEMENTATION_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | crash replay | D007 | FULL_PART_REWRITE | PART_A/YES |
| Q056 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | schema rejection | D007 | FULL_PART_REWRITE | PART_B/NO |
| Q057 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | domain generation | D007 | FULL_PART_REWRITE | BOTH/YES |
| Q058 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | duplicate job trace | D007 | FULL_PART_REWRITE | PART_A/YES |
| Q059 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | sufficiency evidence | D007 | FULL_PART_REWRITE | PART_B/NO |
| Q060 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | operation id lookup | D007 | FULL_PART_REWRITE | BOTH/YES |
| Q061 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | cancel admission trace | D007 | FULL_PART_REWRITE | PART_A/YES |
| Q062 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | domain-runtime reconciliation | D007 | FULL_PART_REWRITE | PART_B/NO |
| Q063 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | lease and CAS trace | D007 | FULL_PART_REWRITE | BOTH/YES |
| Q064 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | contract compatibility | D008 | SECTION_REWRITE | PART_A/YES |
| Q065 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | admission test | D008 | SECTION_REWRITE | PART_B/NO |
| Q066 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | version trace | D008 | SECTION_REWRITE | BOTH/YES |
| Q067 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | fallback evidence | D008 | SECTION_REWRITE | PART_A/YES |
| Q068 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | denied tool trace | D008 | SECTION_REWRITE | PART_B/NO |
| Q069 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/agents/agent-platform.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | capability benchmark | D008 | SECTION_REWRITE | BOTH/YES |
| Q070 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | operation lookup | D009 | FULL_PART_REWRITE | PART_A/YES |
| Q071 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | revocation test | D009 | FULL_PART_REWRITE | PART_B/NO |
| Q072 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | injection trace | D009 | FULL_PART_REWRITE | BOTH/YES |
| Q073 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | duplicate effect test | D009 | FULL_PART_REWRITE | PART_A/YES |
| Q074 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | receipt lookup | D009 | FULL_PART_REWRITE | PART_B/NO |
| Q075 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | failure taxonomy | D009 | FULL_PART_REWRITE | BOTH/YES |
| Q076 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | rotation trace | D009 | FULL_PART_REWRITE | PART_A/YES |
| Q077 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | compatibility test | D009 | FULL_PART_REWRITE | PART_B/NO |
| Q078 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | cancel and effect trace | D009 | FULL_PART_REWRITE | BOTH/YES |
| Q079 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | reconciliation report | D009 | FULL_PART_REWRITE | PART_A/YES |
| Q080 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | policy trace | D010 | SECTION_REWRITE | PART_B/NO |
| Q081 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | no-egress test | D010 | SECTION_REWRITE | BOTH/YES |
| Q082 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | cross-tenant test | D010 | SECTION_REWRITE | PART_A/YES |
| Q083 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | revocation evidence | D010 | SECTION_REWRITE | PART_B/NO |
| Q084 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | audit scan | D010 | SECTION_REWRITE | BOTH/YES |
| Q085 | E | NONE | 设计和实现路径已足够明确，当前 Gate 是测量收益或覆盖率。 | MEASUREMENT_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | escape test | D010 | SECTION_REWRITE | PART_A/YES |
| Q086 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | scope binding trace | D010 | SECTION_REWRITE | PART_B/NO |
| Q087 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/security/security-architecture.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | version approval test | D010 | SECTION_REWRITE | BOTH/YES |
| Q088 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | missing-span audit | D011 | FULL_PART_REWRITE | PART_A/YES |
| Q089 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | adjudication protocol | D011 | FULL_PART_REWRITE | PART_B/NO |
| Q090 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | blocked result manifest | D011 | FULL_PART_REWRITE | BOTH/YES |
| Q091 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | usage ledger | D011 | FULL_PART_REWRITE | PART_A/YES |
| Q092 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | citation and claim report | D011 | FULL_PART_REWRITE | PART_B/NO |
| Q093 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/eval/legal-eval-and-benchmark.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | fault matrix | D011 | FULL_PART_REWRITE | PART_A/YES |
| Q094 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | rolling upgrade test | D012 | FULL_PART_REWRITE | PART_A/YES |
| Q095 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | drain and receipt trace | D012 | FULL_PART_REWRITE | PART_B/NO |
| Q096 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | compatibility matrix | D012 | FULL_PART_REWRITE | BOTH/YES |
| Q097 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | restore drill | D012 | FULL_PART_REWRITE | PART_A/YES |
| Q098 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_B | load isolation test | D012 | FULL_PART_REWRITE | PART_B/NO |
| Q099 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | BOTH | lease/fencing test | D012 | FULL_PART_REWRITE | BOTH/YES |
| Q100 | X | NONE | 设计路径明确，阻塞来自外部环境资格，不应伪装成代码缺口。 | EXTERNAL_GAP | docs/project/deployment/microservice-deployment.md | Target contract; Current evidence not implied | failure is explicit; no blind retry | bounded retry, idempotency, reconciliation | PART_A | production evidence ledger | D012 | FULL_PART_REWRITE | PART_A/YES |

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/gap-register.md`

# Gap Register

| Gap | Class | Closure condition |
|---|---|---|
| Domain/Runtime/Projection reconciliation | I | crash replay and generation comparison test |
| Graph/Hybrid and Memory provider survival | E | controlled ablation and substitution benchmark |
| Sandbox, no-egress and HA qualification | X | real environment evidence and attestation |
| Rolling upgrade and Checkpoint compatibility | I/X | compatibility window and fault-injection run |
| Reviewer disagreement and blocked denominator | E | evaluation protocol with raw results |

这些是 Target/Gap，不是 Current 或 Production 证据。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/architecture-deltas.md`

# Architecture Delta Set

100 道问题先按 Root Cause 聚类，再同步 Canonical；没有把每一道问题直接变成一次追加。

## D001 — 跨 Owner 版本屏障与恢复权威

- Root cause: 跨 Owner 版本屏障与恢复权威。
- Canonical owner: `docs/project/architecture/architecture.md`。
- Document impact: `BOTH`。
- Sync mode: `FULL_PART_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D002 — WorkProduct stale 与 Review 冲突的产品闭环

- Root cause: WorkProduct stale 与 Review 冲突的产品闭环。
- Canonical owner: `docs/project/product/product-architecture.md`。
- Document impact: `PART_A`。
- Sync mode: `SECTION_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D003 — DocumentVersion 发布与解析幂等

- Root cause: DocumentVersion 发布与解析幂等。
- Canonical owner: `docs/project/knowledge/knowledge-evidence-architecture.md`。
- Document impact: `PART_B`。
- Sync mode: `SECTION_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D004 — Projection stale、引用 provenance 与 Graph 降级

- Root cause: Projection stale、引用 provenance 与 Graph 降级。
- Canonical owner: `docs/project/knowledge/knowledge-evidence-architecture.md`。
- Document impact: `BOTH`。
- Sync mode: `FULL_PART_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D005 — Model fallback 的 Attempt、预算和兼容性

- Root cause: Model fallback 的 Attempt、预算和兼容性。
- Canonical owner: `docs/project/agents/agent-platform.md`。
- Document impact: `PART_B`。
- Sync mode: `SECTION_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D006 — Memory promotion、scope 与 stale recall

- Root cause: Memory promotion、scope 与 stale recall。
- Canonical owner: `docs/project/agents/agent-platform.md`。
- Document impact: `BOTH`。
- Sync mode: `FULL_PART_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D007 — Plan/Domain generation、Join、Reducer 与 Replan Barrier

- Root cause: Plan/Domain generation、Join、Reducer 与 Replan Barrier。
- Canonical owner: `docs/project/agents/agent-platform.md`。
- Document impact: `BOTH`。
- Sync mode: `FULL_PART_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D008 — Capability/Skill version 与 Provider admission

- Root cause: Capability/Skill version 与 Provider admission。
- Canonical owner: `docs/project/agents/agent-platform.md`。
- Document impact: `PART_B`。
- Sync mode: `SECTION_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D009 — EffectReceipt、取消竞态与未知副作用对账

- Root cause: EffectReceipt、取消竞态与未知副作用对账。
- Canonical owner: `docs/project/security/security-architecture.md`。
- Document impact: `BOTH`。
- Sync mode: `FULL_PART_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D010 — 撤权、Approval Epoch 与执行时授权

- Root cause: 撤权、Approval Epoch 与执行时授权。
- Canonical owner: `docs/project/security/security-architecture.md`。
- Document impact: `PART_B`。
- Sync mode: `SECTION_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D011 — 可测性、分母完整性与故障注入

- Root cause: 可测性、分母完整性与故障注入。
- Canonical owner: `docs/project/eval/legal-eval-and-benchmark.md`。
- Document impact: `BOTH`。
- Sync mode: `FULL_PART_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

## D012 — 滚动升级、Drain、Checkpoint 兼容与恢复资格

- Root cause: 滚动升级、Drain、Checkpoint 兼容与恢复资格。
- Canonical owner: `docs/project/deployment/microservice-deployment.md`。
- Document impact: `BOTH`。
- Sync mode: `FULL_PART_REWRITE`。
- Decision: 保留清晰的 Target Contract；把未实现、未测量或外部资格缺口分别标记，不提升 Current。
- Reversal: 如果更小的实现或 Host/Provider 替代方案达到相同闭环，撤回该复杂度。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/canonical-sync-record.md`

# Canonical Sync Record

Status: COMPLETE。APPEND forbidden。只记录已应用的 SECTION_REWRITE、FULL_PART_REWRITE 或 NO_CHANGE。

| Delta | Owner Document | Document Impact | Sync Mode | Status | Trace |
|---|---|---|---|---|---|
| D001 | `docs/project/architecture/architecture.md` | BOTH | FULL_PART_REWRITE | APPLIED | 跨 Owner 版本屏障与恢复权威 已合并到该 Owner 文档的完整叙事或契约段落 |
| D002 | `docs/project/product/product-architecture.md` | PART_A | SECTION_REWRITE | APPLIED | WorkProduct stale 与 Review 冲突的产品闭环 已合并到该 Owner 文档的完整叙事或契约段落 |
| D003 | `docs/project/knowledge/knowledge-evidence-architecture.md` | PART_B | SECTION_REWRITE | APPLIED | DocumentVersion 发布与解析幂等 已合并到该 Owner 文档的完整叙事或契约段落 |
| D004 | `docs/project/knowledge/knowledge-evidence-architecture.md` | BOTH | FULL_PART_REWRITE | APPLIED | Projection stale、引用 provenance 与 Graph 降级 已合并到该 Owner 文档的完整叙事或契约段落 |
| D005 | `docs/project/agents/agent-platform.md` | PART_B | SECTION_REWRITE | APPLIED | Model fallback 的 Attempt、预算和兼容性 已合并到该 Owner 文档的完整叙事或契约段落 |
| D006 | `docs/project/agents/agent-platform.md` | BOTH | FULL_PART_REWRITE | APPLIED | Memory promotion、scope 与 stale recall 已合并到该 Owner 文档的完整叙事或契约段落 |
| D007 | `docs/project/agents/agent-platform.md` | BOTH | FULL_PART_REWRITE | APPLIED | Plan/Domain generation、Join、Reducer 与 Replan Barrier 已合并到该 Owner 文档的完整叙事或契约段落 |
| D008 | `docs/project/agents/agent-platform.md` | PART_B | SECTION_REWRITE | APPLIED | Capability/Skill version 与 Provider admission 已合并到该 Owner 文档的完整叙事或契约段落 |
| D009 | `docs/project/security/security-architecture.md` | BOTH | FULL_PART_REWRITE | APPLIED | EffectReceipt、取消竞态与未知副作用对账 已合并到该 Owner 文档的完整叙事或契约段落 |
| D010 | `docs/project/security/security-architecture.md` | PART_B | SECTION_REWRITE | APPLIED | 撤权、Approval Epoch 与执行时授权 已合并到该 Owner 文档的完整叙事或契约段落 |
| D011 | `docs/project/eval/legal-eval-and-benchmark.md` | BOTH | FULL_PART_REWRITE | APPLIED | 可测性、分母完整性与故障注入 已合并到该 Owner 文档的完整叙事或契约段落 |
| D012 | `docs/project/deployment/microservice-deployment.md` | BOTH | FULL_PART_REWRITE | APPLIED | 滚动升级、Drain、Checkpoint 兼容与恢复资格 已合并到该 Owner 文档的完整叙事或契约段落 |

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/canonical-snapshot.md`

# Canonical Snapshot

本轮读取的 Canonical Owner 文档保持唯一事实源：总架构、Product、Domain、Agents、Knowledge、Services、Data、Security、Eval 和 Deployment。Round record 不复制它们的状态机；Delta 只记录为什么需要同步以及同步模式。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/adr-escalations.md`

# ADR and Gate Escalations

- ADR escalation: 0
- User Gate escalation: 0
- Facts changed: NONE
- Historical P0 reclassification: NONE

本轮只是对既有 Target Contract 做可追溯的 refinement；没有改变 Python-only、Microservice Target、Domain/Runtime State 分离或 Security Trust Boundary。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/11-plus-1-coverage-map.md`

# Round-005 11+1 Coverage Map

| Lens | Count | Questions | Delta |
|---|---:|---|---|
| 00 Overall Architecture | 12 | Q001–Q012 | D001 |
| 01 Product Surface | 6 | Q013–Q018 | D002 |
| 02 Input / Document Ingestion | 7 | Q019–Q025 | D003 |
| 03 Knowledge / Agentic GraphRAG | 10 | Q026–Q035 | D004 |
| 04 Model Gateway | 5 | Q036–Q040 | D005 |
| 05 Memory & Context | 8 | Q041–Q048 | D006 |
| 06 Agent Core / Planning & Control | 15 | Q049–Q063 | D007 |
| 07 Capability / Skill | 6 | Q064–Q069 | D008 |
| 08 Tool Runtime | 10 | Q070–Q079 | D009 |
| 09 Security | 8 | Q080–Q087 | D010 |
| 10 Observability & Eval | 6 | Q088–Q093 | D011 |
| 11 Infrastructure | 7 | Q094–Q100 | D012 |

Total: 100 questions。每个问题同时记录 Severity 和 Primary Closure Class。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/baseline-audit.md`

# Round-005 Baseline Audit

- Repository baseline: `4e3ab8773da4edfaa769d3d2f6c4dce3ea63ea15`
- Round-004: immutable, 100Q, 385/500, Human Writing WARNING
- Current/Facts/Runtime/Schema/Migration/Dependencies/Production Infra: unchanged at intake
- Previous automatic result `Round-005 READY_NOT_STARTED` was treated as a gate, not as evidence

本轮只审查 Target Architecture 是否能在并发、崩溃、重复、撤权、旧版本和未知副作用下闭合。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/human-writing-audit.md`

# Human Writing and Continuity Audit

## Result

- Overall: `WARNING`
- Human review result: WARNING_WITH_NO_STRUCTURAL_FAILURE
- Deterministic verifier boundary: only reports density, template signals and required boundaries; it never auto-claims human writing PASS。

## Continuity review

Part A 受影响文档从第一段读到最后一段；已合并补丁式尾巴、重复 Current/Target 声明和突然出现的 Contract 名词。目标场景改用自然叙述，并明确不代表 Historical Current。没有把 Round-specific wording 写入 Canonical 文档。

## Remaining concerns

Architecture、Domain、Knowledge、Agent、Eval 和 Deployment 仍保留必要英文 Contract 名称，局部术语密度较高；这属于 WARNING，不阻塞理解。Part B 保持 precision first。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005/closure-class-audit.md`

# Closure Class Audit

## Distribution

| Class | Meaning | Count |
|---|---|---:|
| A | ARCHITECTURE_BLOCKING | 10 |
| I | IMPLEMENTATION_BLOCKING | 45 |
| E | EVIDENCE_MEASUREMENT_BLOCKING | 30 |
| X | EXTERNAL_QUALIFICATION_BLOCKING | 15 |

没有类别超过 80%，但仍执行了 20 题人工抽查以验证分类流程没有默认归 I。

## Manual audit sample (20 questions)

| ID | Expected primary | Why not another class |
|---|---|---|
| Q001 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 |
| Q002 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 |
| Q003 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 |
| Q004 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 |
| Q005 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 |
| Q006 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 |
| Q007 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 |
| Q008 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 |
| Q009 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 |
| Q010 | A | 当前阻塞来自未解决的架构矛盾，不是等待实现或测量。 |
| Q011 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 |
| Q012 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 |
| Q013 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 |
| Q014 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 |
| Q015 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 |
| Q016 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 |
| Q017 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 |
| Q018 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 |
| Q019 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 |
| Q020 | I | 设计路径可执行，主要缺的是实现、测试或运行接线。 |

## Five representative samples per class

- A: Q001, Q002, Q003, Q004, Q005。
- I: Q011, Q012, Q013, Q014, Q015。
- E: Q056, Q057, Q058, Q059, Q060。
- X: Q086, Q087, Q088, Q089, Q090。

## Borderline classifications

Q010、Q055、Q085 同时存在实现或测量缺口，但 Primary 仍按第一阻塞 Gate 选择；它们没有被机械地全部归为 I。

## Reclassified questions

Round-004 的历史分类不重写。本轮没有进行 Historical Correction 或 Gate Reclassification。

## Potential default-bias findings

抽查覆盖 A/I/E/X 四类；未发现把“未实现”自动当作 I 的结构性偏差。该结论只适用于本 Session 的分类记录，不代表 Runtime 已实现。
