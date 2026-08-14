<!-- Archive metadata: normalized without rewriting the historical record. -->
series: ARCHITECTURE_INTERVIEW
round_id: 004
execution_mode: AUTOMATED
status: ARCHIVED
base_sha: 166a54d51aba0a822c3b5c539d1c43435f8c203f
archive_commit: RECORDED_IN_FINAL_HANDOFF
architecture_revision_commit: NOT_CHANGED_IN_THIS_TASK
round_format: LEGACY_SESSION_COMPRESSION
source_session: RB-WORKFLOW-V3-ROUND-004
# ARCHITECTURE_INTERVIEW — 004

本文件是正式 Red / Blue 对抗记录的单文件归档。它保留当时的核心问题、回答、Review/Score、决策和收口结果；不拥有今天的 Current Facts、Target Architecture 或实现授权。

## Session README: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/README.md`

# RB-WORKFLOW-V3-ROUND-004

本 Session 是 V3.1.2 Human Writing Contract 下的 Architecture Consistency、Failure Semantics
与 Component Survival 审查。它不是 Runtime 集成测试、法律质量证明或 Production Readiness 证据。

## Status

- Baseline: `166a54d51aba0a822c3b5c539d1c43435f8c203f`
- Result: COMPLETE
- Questions / Answers / Scores / Decisions: 100 / 100 / 100 / 100
- Novel / Regression: 80 / 20
- Facts / Runtime / Schema / Migration / Dependencies: NONE / NONE / NONE / NONE / NONE
- Human Writing Review: WARNING; manual review package completed, no automatic PASS claim
- Round-005: READY_NOT_STARTED

## Scope

本轮检查 Product workflow closure、Domain concurrency、stale propagation、PlanVersion 与
DomainVersion、parallel branch、Reducer/Join、Replan Barrier、Memory contamination/promotion、
Graph stale projection、Citation lineage、Tool unknown outcome、Approval race、duplicate effect、
Queue duplicate/cancellation、service partial failure、rolling upgrade、Checkpoint compatibility、
provider substitution 和 A/B/C measurability。

Canonical Sync 只吸收稳定 Target clarification，使用 `SECTION_REWRITE` 或 `FULL_PART_REWRITE`；
没有使用 APPEND。Round-specific trace 保留在本 Session。

## Files

- `manifest.yaml`：Round-004 machine-readable contract。
- `questions.md`、`blue-answers.md`、`red-scores.md`、`blue-decisions.md`：100Q chain。
- `architecture-deltas.md`、`canonical-sync-record.md`：12 个 11+1 Delta 与同步记录。
- `human-writing-audit.md`、`review-package.md`：Human Writing 与人工复核边界。
- `scorecard.md`、`round-report.md`：结果、Gate 和 Open Evidence Gaps。

## Session Manifest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/manifest.yaml`

protocol_version: ZUNO-RED-BLUE-WORKFLOW-V3.1.2
session_id: RB-WORKFLOW-V3-ROUND-004
round_id: RB-WORKFLOW-V3-ROUND-004
baseline_sha: 166a54d51aba0a822c3b5c539d1c43435f8c203f
final_sha: recorded in final handoff
source_canonical_state: ACCEPTED_TARGET
question_budget: 100
actual_question_count: 100
answer_count: 100
score_count: 100
decision_count: 100
novel_question_count: 80
regression_question_count: 20
novelty_threshold_percent: 80
regression_max_percent: 20
theme: Architecture Consistency / Failure Semantics / Component Survival
human_writing_review: WARNING
architecture_integrity: PASS
part_a_quality_gate: PASS
part_b_quality_gate: PASS
canonical_sync_status: APPLIED
round_status: COMPLETE
new_a_p0: 0
round_005_status: READY_NOT_STARTED
facts_changed: NONE
runtime_changed: NONE
schema_or_migration_changed: NONE
dependencies_changed: NONE
production_infra_changed: NONE
adr_escalation_count: 0
user_gate_escalation_count: 0
implementation_program: READY_FOR_TASK_DEFINITION
category_distribution:
  "00 Overall Architecture": 12
  "01 Product Surface": 6
  "02 Input / Document Ingestion": 7
  "03 Knowledge / Agentic GraphRAG": 11
  "04 Model Gateway": 6
  "05 Memory & Context": 8
  "06 Agent Core / Planning & Control": 14
  "07 Capability / Skill": 6
  "08 Tool Runtime": 10
  "09 Security": 8
  "10 Observability & Eval": 6
  "11 Infrastructure": 6

## Questions / Transcript: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/questions.md`

# Round-004 Questions

每行是一个独立的 scenario-based Red Question。`Target Scenario` 只表示目标设计，不表示历史事实。

| ID | Type | 11+1 Lens | Canonical Owner Doc | Scenario | Question | Attack Intent | Required Evidence | Kill Condition |
|---|---|---|---|---|---|---|---|---|
| Q001 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | D12 上同时有新证据和旧 Run | 谁决定旧 Finding 能否继续交付？ | 检查 Domain/Runtime authority | version trace | Runtime 可直接发布旧结论 |
| Q002 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Host 与 Native Runtime 同时处理 Matter | 两条路径如何避免产生两个 Canonical Truth？ | 检查 Host boundary | admission log | Host 直接写 Finding |
| Q003 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Domain Commit 成功而消息发布失败 | 恢复时先看 Queue 还是 Domain State？ | 检查事实优先级 | outbox/replay trace | ACK 覆盖业务事实 |
| Q004 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Agent Checkpoint 停在 Tool 前 | 如何判断外部动作是否已经发生？ | 检查 checkpoint/reconciliation | EffectReceipt | 盲目 retry 不可避免 |
| Q005 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | 两个服务都宣称拥有 Evidence | 谁能改变版本和 Provenance？ | 检查 owner registry | owner contract | 双写成立 |
| Q006 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Graph projection 落后于文档版本 | Planner 能否把旧边当事实？ | 检查 projection boundary | index version | stale graph 被静默使用 |
| Q007 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Service 拆分后网络失败 | 哪些结果可重试，哪些只能对账？ | 检查 failure taxonomy | fault test | 所有错误统一 retry |
| Q008 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Human Review 修改 Finding | Runtime 如何知道旧 Plan 已过期？ | 检查 review feedback | domain generation | Resume 覆盖人工决定 |
| Q009 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | Provider 被替换 | 如何证明语义没有随 Provider 漂移？ | 检查 provider contract | substitution benchmark | Provider 直接拥有业务状态 |
| Q010 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | A/B/C 结果 C≈B | 哪一层复杂度应先撤回？ | 检查 reversal discipline | benchmark report | 复杂度默认保留 |
| Q011 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | 旧 11 模块与新服务名冲突 | 阅读者从哪里获得唯一边界？ | 检查 taxonomy drift | docs verifier | 两套 Canonical truth |
| Q012 | NOVEL | 00 Overall Architecture | docs/project/architecture/architecture.md | 长 Run 跨部署版本恢复 | 哪个版本拥有 Resume 权？ | 检查 deployment/runtime contract | compatibility test | 不兼容 checkpoint 被执行 |
| Q013 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | 用户上传新证据后查看旧报告 | UI 如何解释 stale WorkProduct？ | 检查 product closure | review trace | 旧报告仍显示当前 |
| Q014 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | Reviewer A 已批准 Reviewer B 修改 | 谁拥有最终 HumanDecision？ | 检查 review authority | decision audit | 多个最终决定无序 |
| Q015 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | Host 提交 Run 后断线 | 用户如何知道 Run 与 Matter 版本？ | 检查 async UX contract | status trace | 只能靠聊天历史恢复 |
| Q016 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | 解析失败但部分页已可检索 | 产品显示什么可用范围？ | 检查 partial ingestion UX | document status | 部分材料伪装完整 |
| Q017 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | Finding 被人工驳回 | 是否重跑、保留候选还是删除？ | 检查 review state | rejection trace | 驳回被当成功 |
| Q018 | NOVEL | 01 Product Surface | docs/project/product/product-architecture.md | WorkProduct 导出时发现新冲突 | 导出动作如何被阻止或标注？ | 检查 delivery gate | export audit | stale 结果可交付 |
| Q019 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 同一 PDF 重传但内容 hash 相同 | 如何避免重复 DocumentVersion？ | 检查 identity/idempotency | hash trace | 重复版本污染引用 |
| Q020 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | OCR 完成一半 Worker 崩溃 | 重试从哪里开始？ | 检查 stage checkpoint | worker replay | 半成品被当完整 |
| Q021 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 页码映射在解析后变化 | SourceSpan 如何保持可追溯？ | 检查 citation lineage | span test | 引用漂移不被发现 |
| Q022 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 文档权限在索引后撤销 | 已生成的 Candidate 是否还能返回？ | 检查 ACL at retrieval | access trace | 索引绕过权限 |
| Q023 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 上传取消发生在对象存储写入后 | 如何清理或标记孤儿 Artifact？ | 检查 cancellation semantics | storage audit | 孤儿材料成为可见事实 |
| Q024 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | 两个 parser 对同一版本给出不同 span | 谁能选择结果？ | 检查 provider proposal | comparison trace | parser 直接覆盖来源 |
| Q025 | NOVEL | 02 Input / Document Ingestion | docs/project/knowledge/knowledge-evidence-architecture.md | ingestion queue 重复投递 | Job 如何幂等并报告次数？ | 检查 queue contract | duplicate test | 重复 chunk/index |
| Q026 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Graph edge 来自旧 DocumentVersion | Retrieval 如何拒绝 stale edge？ | 检查 graph freshness | index generation | 旧边支持新 Finding |
| Q027 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Claim 需要跨三份材料闭环 | Evidence Sufficiency 在哪里判断？ | 检查 evidence gate | sufficiency report | 只返回 top-k |
| Q028 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Exact Statute 查询被 Graph 改写 | 为什么不走 Lexical/Hybrid？ | 攻击 always-Graph | ablation | Graph 无收益仍默认启用 |
| Q029 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Scope 选错 Matter | 检索层如何 fail closed？ | 检查 scope isolation | denied trace | 跨案召回 |
| Q030 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Rerank Provider 超时 | 返回 no_evidence 还是降级？ | 检查 typed failure | fallback test | 超时伪装空结果 |
| Q031 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Citation 指向 chunk 但非原文 span | 谁校验引用？ | 检查 citation owner | citation test | CitationCorrectness 不可测 |
| Q032 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | 新材料只影响 Graph projection | 是否重建全图？ | 检查 targeted rebuild | rebuild trace | 全量重建无界成本 |
| Q033 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Hybrid 与 Graph 返回冲突候选 | Agent 能直接挑一个吗？ | 检查 candidate semantics | conflict review | retrieval result 变事实 |
| Q034 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | IndexVersion 与 DomainVersion 不同 | 哪个版本可进入 Plan？ | 检查 version barrier | barrier test | 版本混用 |
| Q035 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | 召回结果来自被删除材料 | Citation 如何处理 tombstone？ | 检查 deletion lineage | deletion test | 删除后仍引用 |
| Q036 | NOVEL | 03 Knowledge / Agentic GraphRAG | docs/project/knowledge/knowledge-evidence-architecture.md | Graph 成本高但质量不增 | 谁触发降级？ | 检查 component survival | kill report | Graph 永久锁定 |
| Q037 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | Model timeout 后换 Provider | 如何保持预算和语义边界？ | 检查 gateway contract | provider trace | fallback 无限重试 |
| Q038 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | Provider 返回不同 tool schema | 谁做归一化？ | 检查 adapter owner | schema test | Agent 处理供应商分支 |
| Q039 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | 同一 Run 发生 fallback | Token/cost 如何归属？ | 检查 usage receipt | cost trace | 预算不可解释 |
| Q040 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | Model Gateway 暂时不可用 | Runtime 能否使用缓存计划？ | 检查 degraded mode | outage test | 隐式改变安全策略 |
| Q041 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | Provider 版本升级 | Plan compatibility 如何保证？ | 检查 model policy | compatibility report | 旧 Run 无法解释 |
| Q042 | NOVEL | 04 Model Gateway | docs/project/agents/agent-platform.md | A/B 比较使用不同 fallback | 如何避免把供应商差异当架构收益？ | 检查 benchmark controls | A/B manifest | 归因失真 |
| Q043 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Memory 写入一条被 Domain 拒绝的经验 | 下次 Recall 能否使用？ | 检查 promotion boundary | memory trace | 候选污染事实 |
| Q044 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Run crash 后重放 | working context 是否重复追加？ | 检查 replay idempotency | replay test | context 越跑越长 |
| Q045 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Matter 权限撤销后 Recall | Provider 如何过滤旧 Memory？ | 检查 scoped access | access trace | Memory 绕过 ACL |
| Q046 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | OpenViking Provider 被替换 | 哪些语义必须保持？ | 检查 memory provider contract | substitution test | Provider 成为事实源 |
| Q047 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | User preference 与 Case Fact 冲突 | Planner 信谁？ | 检查 memory/domain precedence | precedence test | 偏好覆盖案件事实 |
| Q048 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Memory stale 但索引仍命中 | 如何降权或拒绝？ | 检查 staleness | stale recall test | 旧经验无标记复用 |
| Q049 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | 多 Agent 共享 context | 谁能写入共享空间？ | 检查 delegation permission | write audit | 任意 Agent 污染共享记忆 |
| Q050 | NOVEL | 05 Memory & Context | docs/project/agents/agent-platform.md | Memory 召回使计划偏离 EvidenceRequirement | 是否需要 Replan？ | 检查 memory influence | plan trace | 隐式规划不可审计 |
| Q051 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | P7 基于 D12 创建后用户提交 D13 | Join 如何处理旧分支？ | 检查 replan barrier | generation trace | 旧结果直接合并 |
| Q052 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 必需 Worker 超时、可选 Worker 成功 | Run 是否结束？ | 检查 join policy | timeout matrix | 空结果伪装成功 |
| Q053 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 两个 BranchResult 同时提交 | Reducer 如何保证确定性？ | 检查 reducer authority | reducer replay | 顺序决定事实 |
| Q054 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Replan 发生时已有 Step 仍运行 | 哪些 Step 可取消？ | 检查 cancellation | cancel trace | 新旧计划同时提交 |
| Q055 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Reflection 发现权限不足 | 是否修改 Plan 还是停在 Review？ | 检查 permission boundary | deny trace | Reflection 提升权限 |
| Q056 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Budget 在并行分支耗尽 | 谁裁剪剩余工作？ | 检查 budget owner | budget trace | 分支无限运行 |
| Q057 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Coordinator 重启且 Checkpoint 半写 | Resume 从哪里开始？ | 检查 checkpoint atomicity | crash replay | 重复不可逆动作 |
| Q058 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Worker 返回未声明的 ReplanRequest | Coordinator 是否采纳？ | 检查 contract validation | schema rejection | 任意 Worker 改图 |
| Q059 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Plan 已激活但 Domain Review 修改事实 | 如何标记 Plan stale？ | 检查 domain generation | review replay | 旧计划继续写候选 |
| Q060 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 同一 Step 被队列投递两次 | 两次结果如何去重？ | 检查 step idempotency | duplicate job test | 双写 Proposal |
| Q061 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Join 缺一个证据分支但有足够候选 | 谁判断“足够”？ | 检查 evidence gate | sufficiency evidence | Coordinator 自行认定 |
| Q062 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | Tool 调用 outcome_unknown | Plan 能否直接重试？ | 检查 effect reconciliation | operation id | 重复副作用 |
| Q063 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | 用户取消 Run 后 Worker 返回结果 | 结果丢弃还是保留候选？ | 检查 cancellation state | cancel race test | 取消后提交事实 |
| Q064 | NOVEL | 06 Agent Core / Planning & Control | docs/project/agents/agent-platform.md | LangGraph State 与 Domain State 不一致 | Recovery 谁先读？ | 检查 state separation | reconciliation trace | checkpoint 当业务事实 |
| Q065 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Event Provider 输出新字段 | Agent 是否需要改业务代码？ | 检查 capability contract | contract compatibility | 算法写死 Agent |
| Q066 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Conflict Provider 置信度下降 | 是否自动形成 ConflictVersion？ | 检查 proposal admission | admission test | Provider 直写事实 |
| Q067 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Fact-Article Provider 返回不同法条版本 | 谁校验 ApplicableLaw？ | 检查 statute version | version test | 版本混淆 |
| Q068 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Similar Case Provider 不可用 | Agent 如何降级？ | 检查 provider failure | fallback evidence | 伪造类案 |
| Q069 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | Skill 指示与 Security Policy 冲突 | 以谁为准？ | 检查 policy precedence | denied tool trace | Skill 提升权限 |
| Q070 | NOVEL | 07 Capability / Skill | docs/project/agents/agent-platform.md | 同一 Capability 有 LLM 与本地实现 | 如何公平替换和评估？ | 检查 provider resolution | capability benchmark | 供应商差异隐藏 |
| Q071 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | 外部写操作已成功但响应丢失 | Runtime 如何避免第二次写？ | 检查 unknown outcome | provider op id | 盲重试 |
| Q072 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Approval 在执行前被撤销 | Sandbox 是否仍执行？ | 检查 execute-time auth | revocation test | 旧批准有效 |
| Q073 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Tool 参数被文档注入污染 | 谁做参数校验？ | 检查 untrusted input boundary | injection trace | 文档控制 Tool |
| Q074 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | 同一 EffectReceipt 被重复消费 | Tool 如何幂等？ | 检查 receipt identity | duplicate effect test | 重复副作用 |
| Q075 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Sandbox 崩溃但外部 Provider 未知 | 如何进入 reconciliation？ | 检查 crash boundary | receipt lookup | 直接 retry |
| Q076 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Tool timeout 与 network deny 同时发生 | 错误类型如何区分？ | 检查 typed failure | failure taxonomy | 所有错误同路径 |
| Q077 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Secret rotation 发生在长 Run 中 | 下一个 Tool Call 用哪个 Secret？ | 检查 secret epoch | rotation trace | 旧 Secret 继续使用 |
| Q078 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Tool Provider 版本不兼容 | 能否安全降级？ | 检查 provider compatibility | compatibility test | 结果格式静默变化 |
| Q079 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | 用户取消不可逆 Effect | 取消点在哪里？ | 检查 cancellation boundary | cancel/effect trace | 取消承诺虚假 |
| Q080 | NOVEL | 08 Tool Runtime | docs/project/security/security-architecture.md | Effect 成功后 Domain Commit 失败 | 业务状态如何对账？ | 检查 effect/domain split | reconciliation report | EffectReceipt 被删除 |
| Q081 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | 用户失去 Matter 权限但 Run 尚未结束 | 下一次 Retrieval 如何重新授权？ | 回归 ACL 传播 | policy trace | 只在 Run 创建时授权 |
| Q082 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Prompt Injection 要求外传案件 | Security 如何阻断？ | 回归 untrusted content | no-egress test | 文档改变 policy |
| Q083 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Tenant A 的索引被 Tenant B 查询 | 哪一层做隔离？ | 回归 tenant boundary | cross-tenant test | 只靠 Prompt 隔离 |
| Q084 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Approval 与 SecurityEpoch 不一致 | 旧批准能否使用？ | 回归 approval epoch | revocation evidence | 旧批准继续执行 |
| Q085 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Tool 失败后错误信息含 Secret | Audit 如何脱敏？ | 回归 secret hygiene | audit scan | Trace 泄漏 Secret |
| Q086 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | Sandbox 进程访问未授权文件 | 谁强制边界？ | 回归 sandbox isolation | escape test | 只做代码约束 |
| Q087 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | 权限撤销后重复 Job 到达 | Job 是否重新授权？ | 回归 retry auth | deny/retry trace | Retry 绕过撤权 |
| Q088 | REGRESSION | 09 Security | docs/project/security/security-architecture.md | 外部 Host 发送越权 Proposal | Domain 如何拒绝？ | 回归 host boundary | admission denial | Host 被信任 |
| Q089 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | C 与 B 使用不同 Token Budget | 结果还能归因吗？ | 回归 fairness | eval manifest | 不可比仍发布 |
| Q090 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Retrieval 失败但最终答案存在 | 指标如何记录？ | 回归 failure visibility | raw trace | 只看最终文本 |
| Q091 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Reviewer 分母因 blocked case 改变 | 如何报告？ | 回归 denominator integrity | metric report | blocked 折零 |
| Q092 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Graph 只改善一个 QueryClass | 是否全局启用？ | 回归 conditional provider | kill graph report | 局部收益变全局锁定 |
| Q093 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Multi-Agent 多花一倍 Token 无质量增益 | 是否保留？ | 回归 component survival | ablation | 成本不进入结论 |
| Q094 | REGRESSION | 10 Observability & Eval | docs/project/eval/legal-eval-and-benchmark.md | Service 拆分降低延迟但增加失败 | 如何权衡？ | 回归 service evidence | latency/fault report | 单指标发布 |
| Q095 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Rolling upgrade 遇到旧 Checkpoint | 新 Worker 如何读取？ | 回归 compatibility | upgrade replay | 任务静默丢失 |
| Q096 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Queue drain 时新 Run 持续进入 | 如何 backpressure？ | 回归 drain semantics | queue trace | drain 假成功 |
| Q097 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Knowledge GPU worker 饥饿 API | 如何隔离资源？ | 回归 resource profile | load test | 用户数成为唯一依据 |
| Q098 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Shared PostgreSQL 出现 schema drift | 谁阻止不兼容发布？ | 回归 schema compatibility | migration gate | 共享库随意改表 |
| Q099 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | Worker 重启与消息重试同时发生 | 如何避免 retry storm？ | 回归 retry/backpressure | fault injection | 无限重试 |
| Q100 | REGRESSION | 11 Infrastructure | docs/project/deployment/microservice-deployment.md | 生产证据只有 Compose 文件 | 能否宣称 HA？ | 回归 Current/Target boundary | deployment evidence | 配置冒充运行证据 |

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/blue-answers.md`

# Round-004 Blue Answers

答案先给可执行结论，再说明边界。`Target` 表示目标设计，不是 Current 证据。

| ID | Blue Answer | Current / Target / Future / History | Owner | State Transition | Failure / Recovery | Tradeoff | Evidence | Document Impact |
|---|---|---|---|---|---|---|---|---|
| Q001 | 不能直接交付旧 Finding；Domain 校验 D13 后必须重新评估 | Target | Domain Owner | Finding fresh→stale→review | 旧 WorkProduct blocked，创建 bounded re-evaluation | 版本检查增加延迟 | stale propagation test | BOTH |
| Q002 | 两条路径都只能提交 Proposal，唯一 Admission 形成 Canonical Version | Target | Domain Owner | Proposal→admission | 冲突进入 review，不双写 | Host 集成少一步自由度 | host/native A-B trace | BOTH |
| Q003 | 先读 Domain State，再由 Outbox/Reconciliation 补发消息 | Target | Domain + Data | commit→outbox_pending→published | 重试按 idempotency key，不重复事实 | Outbox 增加存储和运维 | crash replay | BOTH |
| Q004 | Checkpoint 只说明控制位置，EffectReceipt 和 ProviderOperationId 决定是否已执行 | Target | Tool + Data | unknown→reconcile→resume/review | 无法确认时人工介入 | 对账比直接 retry 慢 | fault injection | BOTH |
| Q005 | 只有 Domain Owner 可写 EvidenceVersion，其他边界发布 Reference/Proposal | Target | Domain Owner | candidate→admission | 双写检测并拒绝 | 需要明确 owner registry | contract test | BOTH |
| Q006 | Planner 必须携带 IndexVersion 并拒绝超出 freshness policy 的 Graph | Target | Knowledge | indexed→stale/denied | 退回 Hybrid 或 no_evidence | freshness 检查减少召回 | graph stale test | BOTH |
| Q007 | 按 typed failure 分类；可重试错误 retry，不确定副作用先 reconcile | Target | Runtime Coordinator | failed→retry/reconcile | 超过预算进入 review | 错误分类增加协议复杂度 | failure matrix | BOTH |
| Q008 | HumanDecision 提升 DomainGeneration，旧 Plan 只能结束或 replan | Target | Domain + Runtime | reviewed→new generation | Resume 发现 generation mismatch | 人工反馈会打断长任务 | review replay | BOTH |
| Q009 | Provider 只实现 Capability Contract，输出 Proposal/Receipt，替换用同一数据集验证 | Target | Capability Owner | provider candidate→validated | schema/quality 不兼容拒绝 | 适配层增加维护成本 | substitution benchmark | BOTH |
| Q010 | C≈B 时缩减 Native Runtime，保留已经证明有价值的 Legal Backend | Target | Eval Owner | accepted→deferred/deleted | 保留回滚开关但不声称收益 | 删除会损失未测的探索空间 | A/B/C report | PART_A |
| Q011 | 新 taxonomy 是唯一 Canonical；旧 11 模块只作为 History | Current/Target | Architecture Owner | legacy→superseded | verifier 阻止双入口 | 迁移期间需维护链接 | docs boundary test | PART_A |
| Q012 | 只在 checkpoint compatibility window 内 Resume；否则 replan 或人工恢复 | Target | Runtime + Deployment | paused→compatible_resume/replan | 不兼容状态不得执行 | 兼容窗口延长发布成本 | upgrade replay | BOTH |
| Q013 | UI 显示 stale 原因、受影响版本和 Review 入口，不继续显示为当前结果 | Target | Product Owner | deliverable→stale→review | 导出 gate 阻止旧结果 | 状态更多但责任清楚 | product flow test | PART_A |
| Q014 | Review Policy 决定顺序和冲突；最终 HumanDecision 有版本和审计记录 | Target | Domain Owner | pending→approved/rejected | 并发冲突进入 review merge | 多 Reviewer 需要额外协调 | decision audit | BOTH |
| Q015 | Run Status 关联 MatterSnapshot 和 RunId，断线后从状态接口恢复 | Target | Product + Runtime | submitted→running→resumable | status read 不改变事实 | 需要异步状态面 | status trace | PART_A |
| Q016 | 只展示已完成页和明确 partial 状态，未解析页不能进入完整证据集 | Target | Knowledge + Product | uploading→partial/failed | 重试解析，保留原始 Artifact | 部分可用性增加 UX 分支 | document status | BOTH |
| Q017 | 驳回形成显式 Decision，不删除候选；是否重跑由 Review Policy 决定 | Target | Domain Owner | proposed→rejected/revise | 重跑使用新 generation | 保留历史增加存储 | rejection trace | BOTH |
| Q018 | Export 前重新检查 DomainGeneration、Review 和 stale；不满足则阻止或带清晰警告 | Target | Product + Domain | ready→blocked/exported | 新冲突触发 review | 交付多一次检查 | export gate | BOTH |
| Q019 | 内容 hash 用于幂等识别，但来源、上传者和权限变化可产生新版本引用 | Target | Knowledge + Domain | upload→dedup/new version | 重复 job 返回已有 receipt | identity 规则需要解释 | hash test | BOTH |
| Q020 | Stage checkpoint 记录已完成页和 parser version，从最后幂等边界恢复 | Target | Knowledge | parsing→partial→resumed | 半成品不可作为完整 index | checkpoint 增加状态量 | worker replay | BOTH |
| Q021 | SourceSpan 绑定 DocumentVersion 和 parser mapping，映射变化生成新 lineage | Target | Knowledge | span→remapped/stale | 旧引用标 stale，不静默移动 | 版本化引用更复杂 | citation test | BOTH |
| Q022 | Retrieval 时重新校验 ACL，已索引内容也不能绕过当前授权 | Target | Security + Knowledge | visible→denied | 返回 scope_denied 并审计 | 每次检索增加授权成本 | ACL trace | BOTH |
| Q023 | 取消产生可审计 cancel state；孤儿 Artifact 延迟清理但不可见 | Target | Knowledge + Data | uploading→cancelled/garbage_pending | 清理失败进入 maintenance queue | 垃圾回收增加运维 | storage audit | PART_B |
| Q024 | Parser 结果是 Candidate，按版本、质量和策略选择后再 Admission | Target | Knowledge Owner | candidates→selected/review | 冲突保留供人工比较 | 多 Provider 增加评估成本 | parser comparison | BOTH |
| Q025 | JobId 加内容/version/idempotency key，重复投递返回同一 receipt | Target | Knowledge + Queue | queued→processing→completed | duplicate 进入 no-op 或 reconcile | key 管理增加协议字段 | duplicate test | PART_B |
| Q026 | Graph edge 携带 source version 和 projection generation，过期就降级或拒绝 | Target | Knowledge | fresh→stale | 回退 Hybrid/no_evidence | 新鲜度降低召回 | graph freshness | BOTH |
| Q027 | Evidence Sufficiency 由 Claim 与 Requirement 检查，不由 top-k 数量决定 | Target | Knowledge + Domain | candidate→sufficient/insufficient | insufficient 触发补证据或 review | 需要结构化 requirement | sufficiency report | BOTH |
| Q028 | Exact Statute 默认走 Lexical/Hybrid，Graph 只有实验或条件路径 | Target | Knowledge | query→provider resolution | Graph 失败不影响基础检索 | provider routing 更复杂 | ablation | PART_A |
| Q029 | Scope 在检索入口和索引过滤同时执行，失败 closed | Target | Security + Knowledge | request→allowed/denied | denied 不返回候选 | 过滤成本增加 | isolation test | BOTH |
| Q030 | Rerank timeout 是 typed provider_unavailable，可用明确降级，不伪造 no_evidence | Target | Knowledge | rerank→fallback/unavailable | retry 有预算和 deadline | 降级质量需测量 | timeout matrix | BOTH |
| Q031 | Citation 必须落到 SourceSpan，chunk 只能作为中间投影 | Target | Knowledge | candidate→citable/non_citable | 不可定位则拒绝引用 | 精确 span 建设成本高 | citation correctness | BOTH |
| Q032 | 依据受影响 projection 定向重建，不默认全量建图 | Target | Knowledge | changed→affected rebuild | backlog 可观测并阻止 stale 使用 | dependency graph 维护成本 | rebuild trace | PART_B |
| Q033 | 冲突候选回到 Agent/Review，不由检索层替业务选择 | Target | Domain + Knowledge | candidates→comparison/review | 无法选择则 insufficient | 交互增加但语义不漂移 | conflict test | BOTH |
| Q034 | Plan 记录可接受 IndexVersion 范围，超界触发 refresh 或 replan | Target | Runtime + Knowledge | planned→barrier_pass/replan | 不混合版本 | 等待索引会增加 latency | barrier test | BOTH |
| Q035 | 被删除材料保留 tombstone 和 lineage，引用显示不可用而非静默移除 | Target | Knowledge + Domain | visible→deleted/stale | Finding 进入复核 | 历史追踪增加存储 | deletion test | BOTH |
| Q036 | Graph 只在关系型任务的 Kill Test 有增益时保留为条件 Provider | Target | Eval + Knowledge | provider→conditional/deferred | 无增益撤回 | 删除可降低能力覆盖 | kill graph report | PART_A |
| Q037 | Fallback 受同一 Run deadline、budget 和 model policy 约束 | Target | Model/Runtime | primary→fallback/exhausted | exhausted 进入 typed failure | 可用性换来成本 | provider trace | PART_B |
| Q038 | Gateway 归一化 schema，Agent 只看稳定 Tool Contract | Target | Model Gateway | provider schema→normalized | 不兼容拒绝 | 适配器有维护成本 | schema test | BOTH |
| Q039 | Usage Receipt 记录 provider、model、tokens、latency 和 fallback chain | Target | Model Gateway + Eval | call→receipt | 缺 receipt 不计为可比结果 | 观测字段增加 | cost trace | PART_B |
| Q040 | Gateway outage 只能进入显式 degraded mode，不能偷偷改变安全或预算 | Target | Runtime | running→degraded/blocked | deadline 到达则 review | 降级策略需要预演 | outage test | PART_A |
| Q041 | Model policy 和 PlanVersion 记录模型契约，升级需兼容测试 | Target | Model Gateway | versioned→compatible/replan | 不兼容旧 Run 停止 | 发布速度降低 | compatibility report | PART_B |
| Q042 | A/B 固定 fallback policy 或单独分层报告，否则不能归因 | Target | Eval | run→comparable/incomparable | incomparable 不发布结论 | 控制变量更严格 | eval manifest | PART_A |
| Q043 | Memory 先标 candidate/experience，只有显式 promotion 才能进入 Domain | Target | Domain + Memory | candidate→promoted/rejected | rejected 不得作为事实 Recall | promotion 流程增加延迟 | memory trace | BOTH |
| Q044 | Replay 使用 context item idempotency key，working context 不重复追加 | Target | Runtime + Memory | active→replayed | 重复 item no-op | 去重元数据增加 | replay test | PART_B |
| Q045 | Recall 按当前 Matter/Tenant/Policy Epoch 过滤，撤权立即生效 | Target | Security + Memory | visible→denied | 不可恢复到旧授权 | 召回多一次 policy check | access trace | BOTH |
| Q046 | Provider 只承诺 scoped context、expiry、lineage 和 deletion semantics | Target | Memory Owner | provider→contract-compatible | 不兼容替换或降级 | Provider 选择减少 | substitution test | BOTH |
| Q047 | Matter Fact 优先于 User Preference；冲突进入解释或 Review | Target | Domain Owner | context→conflict/review | 不让偏好覆盖事实 | Planner 需要 precedence | precedence test | PART_A |
| Q048 | Stale Memory 降权或拒绝，必须携带 captured_at 和 source generation | Target | Memory Owner | recalled→fresh/stale | stale 不进入 evidence gate | 新鲜度维护成本 | stale recall | PART_B |
| Q049 | 共享 Context 由 Coordinator 按 capability 和 permission 写入 | Target | Runtime + Security | private→shared candidate | 越权写入拒绝并审计 | 协调成本增加 | write audit | BOTH |
| Q050 | Memory 只能影响候选计划；改变 EvidenceRequirement 必须显式 Replan | Target | Runtime | recall→plan_candidate/replan | 隐式影响不被采纳 | 可追踪性优先于简洁 | plan trace | BOTH |
| Q051 | D12 与 D13 的 BranchResult 不能直接 Join，先过 Replan Barrier | Target | Runtime + Domain | join_pending→barrier/replan | 旧分支保留 receipt 但不提交 | 重新计算增加 latency | generation trace | BOTH |
| Q052 | 必需分支失败阻止成功；可选分支可带 degraded outcome | Target | Runtime | waiting→degraded/blocked | deadline 后 review | 任务完成率下降但不造假 | timeout matrix | BOTH |
| Q053 | Reducer 按 BranchId 和输入 generation 做确定性归并 | Target | Runtime | branch_result→reduced | duplicate result no-op | reducer 规则更严格 | replay test | PART_B |
| Q054 | Replan 先冻结旧 Plan，新 Plan 继承可复用 receipt，未安全取消的 Step 对账 | Target | Runtime + Tool | active→replan_pending | effect unknown 不重发 | 状态管理复杂 | cancel trace | BOTH |
| Q055 | 权限不足是 hard stop 或 Review，不是 Reflection 的自助升级 | Target | Security + Runtime | proposing→denied/review | 保留原因，不能 retry 绕过 | 任务可能中断 | deny trace | BOTH |
| Q056 | Coordinator 拥有预算裁剪，记录未运行分支和原因 | Target | Runtime | running→budget_limited | 不以缺失分支伪装完成 | 成本可控但覆盖减少 | budget trace | PART_B |
| Q057 | Checkpoint 与 Step lease 原子记录；恢复从最后安全边界开始 | Target | Runtime | crashed→resume/reconcile | 未知 Effect 先对账 | 原子写和存储成本 | crash replay | BOTH |
| Q058 | 未声明 ReplanRequest 按 schema 拒绝并作为 worker failure | Target | Runtime | result→rejected | 不改变 Plan | 合约验证增加延迟 | schema rejection | PART_B |
| Q059 | Review 形成新 DomainGeneration，旧 Plan 只能 replan 或结束 | Target | Domain + Runtime | planned→stale | 不允许旧 Plan Admission | 人工介入增加等待 | review replay | BOTH |
| Q060 | StepId 加 PlanVersion 和 input generation，重复消费返回已有 result | Target | Runtime | queued→completed/no-op | duplicate 不触发第二 Proposal | key 设计复杂 | duplicate job | PART_B |
| Q061 | Evidence Gate 依据 Claim、Requirement 和 source lineage，不由 Coordinator 主观判断 | Target | Knowledge + Domain | candidate→sufficient/research_more | 不足则补 Step 或 review | gate 需要标注数据 | sufficiency evidence | BOTH |
| Q062 | outcome_unknown 先进入 Effect reconciliation，不能直接 retry | Target | Tool + Runtime | tool_call→unknown/reconciled | Provider id 显示已执行则 no-op | 速度让位于安全 | operation id | BOTH |
| Q063 | 取消后完成的结果可保留为候选 Receipt，但不得自动提交 Canonical | Target | Runtime + Domain | cancelled→late_result/quarantined | 用户重新发起时显式采用 | 需要清理策略 | cancel race | PART_B |
| Q064 | Recovery 先读 DomainGeneration 与 EffectReceipt，再读 Checkpoint 控制位置 | Target | Data + Runtime | recover→resume/replan/review | 两者矛盾进入 reconciliation | 恢复路径更长 | reconciliation trace | BOTH |
| Q065 | Agent 绑定 Capability Contract，不绑定算法内部字段 | Target | Capability Owner | request→resolved provider | provider schema 变化由 adapter 吸收 | Adapter 维护成本 | contract test | PART_B |
| Q066 | 置信度只影响 Review/排序，不能绕过 Admission | Target | Domain Owner | proposal→review/admitted | 低置信度拒绝或人工确认 | 自动化率下降 | admission test | BOTH |
| Q067 | ApplicableLaw 必须绑定 StatuteVersion，版本不一致退回研究 | Target | Domain + Capability | mapping→version_checked | 不得混用新旧法条 | 需要版本数据 | version test | BOTH |
| Q068 | 类案 Provider 不可用时返回 unavailable，Agent 可继续无类案路径但标记缺口 | Target | Capability Owner | call→unavailable/degraded | 不伪造 SimilarCase | 结果覆盖减少 | fallback evidence | PART_A |
| Q069 | Security Policy 优先于 Skill；冲突记录 denied Tool intent | Target | Security | intent→denied | 不能由 Skill retry 改写 | 灵活性下降 | denied trace | BOTH |
| Q070 | Provider resolution 记录实现、版本和指标，比较时固定变量 | Target | Capability + Eval | candidate→selected/compared | 不可比则阻塞结论 | 记录成本增加 | capability benchmark | PART_B |
| Q071 | EffectReceipt 与 ProviderOperationId 是 unknown outcome 的唯一重试依据 | Target | Tool Owner | prepared→unknown→reconciled | 已执行则 no-op | 对账需要 Provider 支持 | fault injection | BOTH |
| Q072 | 执行时重新校验 SecurityEpoch，撤权立即阻断 | Target | Security + Tool | approved→revoked/execute | 旧批准不再有效 | 每次动作有延迟 | revocation test | BOTH |
| Q073 | 文档内容只能作为 untrusted input，Tool 参数由 schema/policy 重新生成 | Target | Tool + Security | content→proposal→validated | 注入字段丢弃并审计 | 参数校验更严格 | injection trace | BOTH |
| Q074 | Effect identity 加幂等键，重复 receipt 只返回既有结果 | Target | Tool | attempted→completed/no-op | 不重复外部副作用 | Provider 适配复杂 | duplicate effect | PART_B |
| Q075 | Sandbox crash 后读取 receipt 和 operation id，再决定 reconcile/retry | Target | Tool + Data | crashed→unknown/reconciled | 无证据不重发不可逆动作 | 恢复等待更久 | crash test | BOTH |
| Q076 | timeout、network_denied、provider_error 分开编码并分别定义 retry | Target | Tool | attempted→typed_failure | 只有安全失败可直接 retry | 错误分类维护成本 | failure taxonomy | PART_B |
| Q077 | Secret Scope 绑定 SecurityEpoch，rotation 后新动作必须重新取 Secret | Target | Security | authorized→epoch_changed | 旧凭据失效 | rotation 传播复杂 | secret trace | BOTH |
| Q078 | ToolVersion 与输入输出 schema 做兼容性检查，不兼容进入 provider_unavailable | Target | Tool | resolved→compatible/blocked | 不能静默解析不同结果 | 发布需兼容窗口 | compatibility test | PART_B |
| Q079 | 取消只阻止尚未开始的 Effect；已开始的动作必须走 unknown/reconcile | Target | Tool + Runtime | prepared→cancelled/started | 不承诺不可能的撤销 | 用户体验更复杂 | cancel trace | PART_A |
| Q080 | EffectReceipt 保留，即使 Domain Commit 失败；后台对账补状态或人工处理 | Target | Tool + Domain | effect_success→domain_pending/reconciled | 不删除副作用证据 | 数据清理更难 | reconciliation | BOTH |
| Q081 | Retrieval 和 Tool 每次使用当前 Policy Epoch，Run 创建时授权不够 | Target | Security | authorized→recheck/denied | denied 不再 retry | 长 Run 延迟增加 | policy trace | BOTH |
| Q082 | Prompt Injection 无权修改 Grant 或 egress policy，外发动作需要独立 Approval | Target | Security | untrusted→blocked/review | no-egress 与审计保留 | 安全边界牺牲便利 | no-egress test | BOTH |
| Q083 | Tenant/Matter/Scope 在索引、API 和 Tool 三层校验 | Target | Security | request→allowed/denied | 任一层失败 closed | 多层策略成本 | cross-tenant test | BOTH |
| Q084 | Approval 必须带 SecurityEpoch，epoch 变化后重新审批 | Target | Security | approved→invalid/reapproved | 旧审批不能执行 | 审批次数增加 | epoch test | PART_B |
| Q085 | Secret 和敏感材料进入 Trace 前脱敏，原始值不进入 Error | Target | Security + Observability | error→redacted_audit | 泄漏事件进入 security review | 调试信息减少 | audit scan | BOTH |
| Q086 | Sandbox 由 OS/container/network boundary 强制，代码约束只是补充 | Target | Tool/Security | job→isolated/escaped | escape fail closed 并隔离 | 隔离运维成本高 | escape test | PART_A |
| Q087 | Retry 前重新做权限检查，撤权后的旧 Job 进入 denied | Target | Security + Queue | retry→recheck/denied | 不绕过 epoch | 重试吞吐下降 | retry auth trace | BOTH |
| Q088 | External Host 与 Native Runtime 使用同一 Domain Admission，不信任 Host 身份 | Target | Domain + Security | external proposal→admission/reject | 越权只产生拒绝记录 | 集成需要明确 Contract | admission denial | BOTH |
| Q089 | A/B/C 固定模型、工具、数据和预算；fallback 差异单独记录 | Target | Eval | run→comparable/incomparable | 不可比阻塞结论 | 试验设计成本高 | eval manifest | BOTH |
| Q090 | Retrieval failure 作为 Trace FailureClass，最终文本不能掩盖 | Target | Eval | run→failed_with_output | 结果可展示但不计为无错误 | 指标更保守 | raw trace | PART_A |
| Q091 | blocked/unavailable/incomparable 单独报告，不改变有效分母 | Target | Eval | result→classified | 报告保留原因 | 分析复杂度增加 | metric report | PART_B |
| Q092 | Graph 只对通过 QueryClass Kill Test 的任务启用 | Target | Eval + Knowledge | graph→conditional | 无收益回 Hybrid | 路由配置增加 | graph report | BOTH |
| Q093 | Token、Latency 与质量一起评估，成本无收益则撤回 Multi-Agent | Target | Eval + Agents | component→keep/defer/delete | 结论受预算约束 | 更少自动化 | ablation | PART_A |
| Q094 | Service evidence 同时报告 latency、failure、resource 和 recovery | Target | Eval + Services | boundary→validated/rejected | 失败增益不足则合并 | 测试矩阵较大 | fault report | BOTH |
| Q095 | 新 Worker 先做 Checkpoint compatibility read，再逐步切换 writer | Target | Deployment + Runtime | old→compatible→rolled | 不兼容暂停 rollout | 双读窗口增加成本 | upgrade replay | BOTH |
| Q096 | Queue drain 先停止接收或设置 backpressure，Job 状态可查询 | Target | Deployment | running→draining→drained | 新 Job 不静默丢失 | 发布期间吞吐下降 | queue trace | BOTH |
| Q097 | API、Knowledge 和 Agent 使用不同 resource profile/queue，避免 GPU 饥饿 API | Target | Deployment | shared→isolated pools | starvation 触发 backpressure | 资源利用率可能下降 | load test | PART_A |
| Q098 | Shared PostgreSQL 仍按逻辑 ownership 和 compatibility gate 管理 schema | Target | Data + Deployment | schema→compatible/blocked | drift 阻止发布 | 集中库治理成本 | schema check | BOTH |
| Q099 | Retry 有 deadline、attempt 上限、DLQ 和 backpressure，重启不放大风暴 | Target | Deployment + Queue | retrying→dead_letter/reconciled | unknown effect 不自动重试 | 失败恢复更慢 | fault injection | BOTH |
| Q100 | Compose 只能证明运行配置，HA 需要真实故障和恢复证据 | Current/Target | Deployment | configured→measured/unproven | 无证据保持 NOT_ESTABLISHED | 不夸大生产状态 | deployment evidence | PART_A |

---

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/red-scores.md`

# Round-004 Red Scores

Score is a 0–5 defense score. Severity is the remaining documentation/architecture risk, not runtime quality. I-* is the closure note used by this Round.

| ID | 11+1 Lens | Score | Severity | Closure | Blue Decision | Document Impact | Part A | Part B | Delta |
|---|---|---:|---|---|---|---|---|---|---|
| Q001 | 00 Overall Architecture | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D001 |
| Q002 | 00 Overall Architecture | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D001 |
| Q003 | 00 Overall Architecture | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D001 |
| Q004 | 00 Overall Architecture | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D001 |
| Q005 | 00 Overall Architecture | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D001 |
| Q006 | 00 Overall Architecture | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D001 |
| Q007 | 00 Overall Architecture | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D001 |
| Q008 | 00 Overall Architecture | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D001 |
| Q009 | 00 Overall Architecture | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D001 |
| Q010 | 00 Overall Architecture | 3 | P1 | I-DEFER | DEFER | PART_A | YES | NO | D001 |
| Q011 | 00 Overall Architecture | 3 | P1 | I-KEEP | KEEP | PART_A | YES | NO | D001 |
| Q012 | 00 Overall Architecture | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D001 |
| Q013 | 01 Product Surface | 3 | P1 | I-REFINE | REFINE | PART_A | YES | NO | D002 |
| Q014 | 01 Product Surface | 3 | P1 | I-REFINE | REFINE | BOTH | YES | YES | D002 |
| Q015 | 01 Product Surface | 3 | P1 | I-REFINE | REFINE | PART_A | YES | NO | D002 |
| Q016 | 01 Product Surface | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D002 |
| Q017 | 01 Product Surface | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D002 |
| Q018 | 01 Product Surface | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D002 |
| Q019 | 02 Input / Document Ingestion | 4 | P2 | I-KEEP | KEEP | BOTH | YES | YES | D003 |
| Q020 | 02 Input / Document Ingestion | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D003 |
| Q021 | 02 Input / Document Ingestion | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D003 |
| Q022 | 02 Input / Document Ingestion | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D003 |
| Q023 | 02 Input / Document Ingestion | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D003 |
| Q024 | 02 Input / Document Ingestion | 4 | P2 | I-KEEP | KEEP | BOTH | YES | YES | D003 |
| Q025 | 02 Input / Document Ingestion | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D003 |
| Q026 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D004 |
| Q027 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D004 |
| Q028 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-DEFER | DEFER | PART_A | YES | NO | D004 |
| Q029 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D004 |
| Q030 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D004 |
| Q031 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D004 |
| Q032 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D004 |
| Q033 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D004 |
| Q034 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D004 |
| Q035 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D004 |
| Q036 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | I-DEFER | DEFER | PART_A | YES | NO | D004 |
| Q037 | 04 Model Gateway | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D005 |
| Q038 | 04 Model Gateway | 4 | P2 | I-KEEP | KEEP | BOTH | YES | YES | D005 |
| Q039 | 04 Model Gateway | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D005 |
| Q040 | 04 Model Gateway | 4 | P2 | I-DEFER | DEFER | PART_A | YES | NO | D005 |
| Q041 | 04 Model Gateway | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D005 |
| Q042 | 04 Model Gateway | 4 | P2 | I-REFINE | REFINE | PART_A | YES | NO | D005 |
| Q043 | 05 Memory & Context | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D006 |
| Q044 | 05 Memory & Context | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D006 |
| Q045 | 05 Memory & Context | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D006 |
| Q046 | 05 Memory & Context | 4 | P2 | I-KEEP | KEEP | BOTH | YES | YES | D006 |
| Q047 | 05 Memory & Context | 4 | P2 | I-REFINE | REFINE | PART_A | YES | NO | D006 |
| Q048 | 05 Memory & Context | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D006 |
| Q049 | 05 Memory & Context | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D006 |
| Q050 | 05 Memory & Context | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D006 |
| Q051 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D007 |
| Q052 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D007 |
| Q053 | 06 Agent Core / Planning & Control | 4 | P2 | I-KEEP | KEEP | PART_B | NO | YES | D007 |
| Q054 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D007 |
| Q055 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D007 |
| Q056 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D007 |
| Q057 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D007 |
| Q058 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D007 |
| Q059 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D007 |
| Q060 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D007 |
| Q061 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D007 |
| Q062 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D007 |
| Q063 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D007 |
| Q064 | 06 Agent Core / Planning & Control | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D007 |
| Q065 | 07 Capability / Skill | 4 | P2 | I-KEEP | KEEP | PART_B | NO | YES | D008 |
| Q066 | 07 Capability / Skill | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D008 |
| Q067 | 07 Capability / Skill | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D008 |
| Q068 | 07 Capability / Skill | 4 | P2 | I-DEFER | DEFER | PART_A | YES | NO | D008 |
| Q069 | 07 Capability / Skill | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D008 |
| Q070 | 07 Capability / Skill | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D008 |
| Q071 | 08 Tool Runtime | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D009 |
| Q072 | 08 Tool Runtime | 4 | P2 | I-KEEP | KEEP | BOTH | YES | YES | D009 |
| Q073 | 08 Tool Runtime | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D009 |
| Q074 | 08 Tool Runtime | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D009 |
| Q075 | 08 Tool Runtime | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D009 |
| Q076 | 08 Tool Runtime | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D009 |
| Q077 | 08 Tool Runtime | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D009 |
| Q078 | 08 Tool Runtime | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D009 |
| Q079 | 08 Tool Runtime | 4 | P2 | I-REFINE | REFINE | PART_A | YES | NO | D009 |
| Q080 | 08 Tool Runtime | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D009 |
| Q081 | 09 Security | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D010 |
| Q082 | 09 Security | 4 | P2 | I-KEEP | KEEP | BOTH | YES | YES | D010 |
| Q083 | 09 Security | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D010 |
| Q084 | 09 Security | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D010 |
| Q085 | 09 Security | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D010 |
| Q086 | 09 Security | 4 | P2 | I-REFINE | REFINE | PART_A | YES | NO | D010 |
| Q087 | 09 Security | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D010 |
| Q088 | 09 Security | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D010 |
| Q089 | 10 Observability & Eval | 4 | P2 | I-KEEP | KEEP | BOTH | YES | YES | D011 |
| Q090 | 10 Observability & Eval | 4 | P2 | I-REFINE | REFINE | PART_A | YES | NO | D011 |
| Q091 | 10 Observability & Eval | 4 | P2 | I-REFINE | REFINE | PART_B | NO | YES | D011 |
| Q092 | 10 Observability & Eval | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D011 |
| Q093 | 10 Observability & Eval | 4 | P2 | I-DEFER | DEFER | PART_A | YES | NO | D011 |
| Q094 | 10 Observability & Eval | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D011 |
| Q095 | 11 Infrastructure | 4 | P2 | I-KEEP | KEEP | BOTH | YES | YES | D012 |
| Q096 | 11 Infrastructure | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D012 |
| Q097 | 11 Infrastructure | 4 | P2 | I-REFINE | REFINE | PART_A | YES | NO | D012 |
| Q098 | 11 Infrastructure | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D012 |
| Q099 | 11 Infrastructure | 4 | P2 | I-REFINE | REFINE | BOTH | YES | YES | D012 |
| Q100 | 11 Infrastructure | 4 | P2 | I-REFINE | REFINE | PART_A | YES | NO | D012 |

---

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/review-package.md`

# Round-004 Review Package

## Review Scope

本轮同时执行 V3.1.2 Human Writing Contract 和 Round-004 100Q。审查对象是 Canonical Architecture
是否能把状态、失败、恢复、取舍和删除出口讲清楚，而不是证明产品已经生产可用。

## Strongest findings

1. Domain State、Runtime Checkpoint 和 External Effect Receipt 必须分别恢复，任何一个 ACK 都不能替代另一个。
2. New Evidence、Human Review 和 PlanVersion 变化必须形成显式 generation barrier。
3. Memory、Graph、Capability Provider 只能提供候选或投影，不能绕过 Domain Admission。
4. Tool unknown outcome、Approval revocation 和 duplicate effect 是同一条安全恢复链上的不同状态。
5. Service 与 Worker 的选择必须由资源、故障、安全、可用性或生命周期证据推动。
6. Rolling upgrade 需要 Checkpoint compatibility 和 queue drain，而不是只更新镜像。
7. Graph、Multi-Agent、Native Runtime 的保留条件都是可测收益，不是默认复杂度。

## Most natural documents

Product、Multi-Agent、Service、Deployment、Eval 的 Part A 经过 FULL_PART_REWRITE 后，开始从具体
工作或失败路径推导设计；它们没有添加历史项目故事，也没有把 Target Scenario 写成事实。

## Remaining human-writing concerns

Architecture、Domain、Knowledge、Agent、Eval 和 Deployment 的 Part A 仍然包含较多英文 Contract
名词。Part B 的精确性需要这些术语，但第一次阅读时仍应由高级工程师检查术语密度和上下文是否足够。
因此 Human Writing 结论是 `WARNING`，不是机器 PASS。

## Canonical sections rewritten

- `docs/project/product/product-architecture.md`
- `docs/project/agents/multi-agent-runtime.md`
- `docs/project/services/service-architecture.md`
- `docs/project/eval/legal-eval-and-benchmark.md`
- `docs/project/deployment/microservice-deployment.md`

Supporting governance/protocol and cross-layer wording was updated only where the Round-004 Delta required it。

## Integrity and status

- New A-P0: 0
- Architecture integrity: PASS
- Part A / Part B: PASS / PASS
- Facts changed: NONE
- Runtime changed: NONE
- Production readiness: unchanged, `NOT_ESTABLISHED`
- Round-005: `READY_NOT_STARTED`
- Full CI: NOT RUN

---

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/scorecard.md`

# Round-004 Scorecard

```yaml
question_count: 100
answer_count: 100
score_count: 100
decision_count: 100
novel_question_count: 80
regression_question_count: 20
raw_score: 385
normalized_score: 77.0
p0_count: 0
p1_count: 15
p2_count: 85
p3_count: 0
closure_class_counts:
  A: 0
  I: 100
  E: 0
  X: 0
architecture_integrity: PASS
part_a_quality_gate: PASS
part_b_quality_gate: PASS
human_writing_review: WARNING
canonical_sync_status: APPLIED
round_status: COMPLETE
new_a_p0: 0
round_005_status: READY_NOT_STARTED
```

数值分数只表示本轮防守质量，不表示 Runtime、法律答案质量、安全证明或 Production Readiness。
所有原始 P0 继续遵守历史会话的 closure 状态，本轮没有将其关闭。

| Lens | Questions | Raw | Normalized |
|---|---:|---:|---:|
| 00 Overall Architecture | 12 | 36 | 60.00 |
| 01 Product Surface | 6 | 21 | 70.00 |
| 02 Input / Document Ingestion | 7 | 28 | 80.00 |
| 03 Knowledge / Agentic GraphRAG | 11 | 44 | 80.00 |
| 04 Model Gateway | 6 | 24 | 80.00 |
| 05 Memory & Context | 8 | 32 | 80.00 |
| 06 Agent Core / Planning & Control | 14 | 56 | 80.00 |
| 07 Capability / Skill | 6 | 24 | 80.00 |
| 08 Tool Runtime | 10 | 40 | 80.00 |
| 09 Security | 8 | 32 | 80.00 |
| 10 Observability & Eval | 6 | 24 | 80.00 |
| 11 Infrastructure | 6 | 24 | 80.00 |

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/blue-decisions.md`

# Round-004 Blue Decisions

The table is the structured decision record. The natural-language answer is in blue-answers.md; document_impact is kept next to the decision so a later Canonical Sync cannot silently change only one half of the contract.

| ID | Red Score | Severity | Red Finding | Blue Decision | Architecture After | Complexity Added | Complexity Removed | Document Impact | Canonical Owner Doc | Delta Ref | Sync Mode | Part A / Part B Required |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| Q001 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q002 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q003 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q004 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q005 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q006 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q007 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q008 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q009 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q010 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q011 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q012 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q013 | 3/5 | P1 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / NO |
| Q014 | 3/5 | P1 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / YES |
| Q015 | 3/5 | P1 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / NO |
| Q016 | 4/5 | P2 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / YES |
| Q017 | 4/5 | P2 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / YES |
| Q018 | 4/5 | P2 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / YES |
| Q019 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q020 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q021 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q022 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q023 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q024 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q025 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q026 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q027 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q028 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q029 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q030 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q031 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q032 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q033 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q034 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q035 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q036 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q037 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q038 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q039 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q040 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q041 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q042 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q043 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q044 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q045 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q046 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q047 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q048 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q049 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q050 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q051 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q052 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q053 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | NO / YES |
| Q054 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q055 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q056 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | NO / YES |
| Q057 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q058 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | NO / YES |
| Q059 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q060 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | NO / YES |
| Q061 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q062 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q063 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | NO / YES |
| Q064 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q065 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q066 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q067 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q068 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q069 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q070 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q071 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q072 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q073 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q074 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q075 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q076 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q077 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q078 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q079 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q080 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q081 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q082 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q083 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q084 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q085 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q086 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q087 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q088 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q089 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | YES / YES |
| Q090 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | YES / NO |
| Q091 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | NO / YES |
| Q092 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | YES / YES |
| Q093 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | YES / NO |
| Q094 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | YES / YES |
| Q095 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / YES |
| Q096 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / YES |
| Q097 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / NO |
| Q098 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / YES |
| Q099 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / YES |
| Q100 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / NO |

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/gap-register.md`

# Round-004 Gap Register

| Gap | Type | State | Next Evidence |
|---|---|---|---|
| Court QA protocol | External / Measurement | OPEN | obtain dataset and reviewer protocol |
| Domain/Runtime crash replay | Implementation / Measurement | OPEN | fault injection |
| Tool unknown outcome | Implementation / External | OPEN | ProviderOperationId emulator and provider contract |
| Graph freshness | Measurement | OPEN | conditional Graph Kill Test |
| Multi-Agent benefit | Measurement | OPEN | L0/L1/L2 ablation |
| Service boundary benefit | Measurement | OPEN | worker vs service latency/failure/resource test |
| Checkpoint compatibility | Implementation / Measurement | OPEN | rolling upgrade replay |
| Human writing | Review | WARNING | manual review of five priority docs |

这些 Gap 没有改变 Facts、Runtime 或 Production Status。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/architecture-deltas.md`

# Round-004 Architecture Deltas

本表只记录经过 Red → Blue → Counter reasoning 后可进入 Canonical Target 的稳定澄清。没有
把任何一项写成 Current，也没有关闭历史 P0。

## D001 Overall Architecture

- Source Questions: Q001–Q012
- Affected Canonical Docs: architecture.md、domain-state-lifecycle.md、data-ownership-and-recovery.md
- Part A Impact: reviewed Domain/Runtime/Host closure and recovery narrative; existing text remains sufficient
- Part B Impact: existing version、receipt、reconciliation contracts remain sufficient
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D002 Product Surface

- Source Questions: Q013–Q018
- Affected Canonical Docs: product-architecture.md
- Part A Impact: rewrite product narrative around stale WorkProduct and Review delivery
- Part B Impact: retain delivery/review contract
- Document Impact: PART_A
- Apply Mode: FULL_PART_REWRITE

## D003 Input / Document Ingestion

- Source Questions: Q019–Q025
- Affected Canonical Docs: knowledge-evidence-architecture.md
- Part A Impact: no independent stable narrative delta
- Part B Impact: retain identity、partial parsing、ACL and job idempotency
- Document Impact: PART_B
- Apply Mode: NO_CHANGE

## D004 Knowledge / Agentic GraphRAG

- Source Questions: Q026–Q036
- Affected Canonical Docs: knowledge-evidence-architecture.md
- Part A Impact: conditional Graph and citation freshness remain explicit
- Part B Impact: preserve projection generation and evidence gate
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D005 Model Gateway

- Source Questions: Q037–Q042
- Affected Canonical Docs: agent-platform.md
- Part A Impact: no new stable narrative claim
- Part B Impact: keep provider normalization and budget receipt
- Document Impact: PART_B
- Apply Mode: NO_CHANGE

## D006 Memory & Context

- Source Questions: Q043–Q050
- Affected Canonical Docs: agent-platform.md、data-ownership-and-recovery.md
- Part A Impact: keep Memory as candidate context, not Domain truth
- Part B Impact: promotion、expiry、scope and replay idempotency
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D007 Agent Core / Planning & Control

- Source Questions: Q051–Q064
- Affected Canonical Docs: agent-platform.md、multi-agent-runtime.md、domain-state-lifecycle.md
- Part A Impact: rewrite was not required because existing narrative already states single control authority
- Part B Impact: explicit Replan Barrier and Domain/Checkpoint reconciliation
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D008 Capability / Skill

- Source Questions: Q065–Q070
- Affected Canonical Docs: agent-platform.md、legal-domain-model.md
- Part A Impact: provider remains replaceable and proposal-only
- Part B Impact: preserve capability contract and admission
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D009 Tool Runtime

- Source Questions: Q071–Q080
- Affected Canonical Docs: security-architecture.md、data-ownership-and-recovery.md
- Part A Impact: no new stable narrative claim
- Part B Impact: retain EffectReceipt、unknown outcome and reconciliation
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D010 Security

- Source Questions: Q081–Q088
- Affected Canonical Docs: security-architecture.md
- Part A Impact: no new stable narrative claim
- Part B Impact: preserve execute-time authorization and SecurityEpoch
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D011 Observability & Eval

- Source Questions: Q089–Q094
- Affected Canonical Docs: legal-eval-and-benchmark.md
- Part A Impact: rewrite evaluation narrative around causal claims and incomparable outcomes
- Part B Impact: preserve A/B/C and failure classification
- Document Impact: BOTH
- Apply Mode: FULL_PART_REWRITE

## D012 Infrastructure

- Source Questions: Q095–Q100
- Affected Canonical Docs: microservice-deployment.md、service-architecture.md
- Part A Impact: rewrite deployment narrative around rolling upgrade and queue drain
- Part B Impact: keep compatibility、backpressure and evidence boundary
- Document Impact: BOTH
- Apply Mode: FULL_PART_REWRITE

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/round-report.md`

# Round-004 Report

Round-004 完成 100 Questions / 100 Answers / 100 Scores / 100 Decisions，保持 11+1 固定配额。
80 题为 NOVEL，20 题为 REGRESSION；Raw Score 385/500，Normalized 77.00。P0/P1/P2/P3 为
0/15/85/0，New A-P0 为 0。

本轮保留或澄清了 Domain State、Evidence Semantics、Single Controller、受控并行、Review、
Security/Eval floors；Graph、Memory Provider、Native Runtime、Service Boundary 的保留都继续
受替换、消融、恢复和安全证据约束。没有新增 ADR、事实或实现任务。

Canonical Sync 使用 SECTION_REWRITE/FULL_PART_REWRITE/NO_CHANGE，禁止 APPEND。Round-005 为
READY_NOT_STARTED。Human Writing Review 为 WARNING，原因是机器只能识别确定性信号，英文术语密度
仍需要人工阅读；这不是失败，也不是自动 PASS。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/canonical-sync-record.md`

# Round-004 Canonical Sync Record

- Status: APPLIED
- Baseline SHA: `166a54d51aba0a822c3b5c539d1c43435f8c203f`
- After SHA: recorded in final handoff
- Sync mode: SECTION_REWRITE / FULL_PART_REWRITE / NO_CHANGE；APPEND forbidden
- Facts changed: NONE
- Runtime changed: NONE
- ADR escalation: NONE

| Delta | Canonical Docs | Decision | Sync Mode | Result |
|---|---|---|---|---|
| D001 | architecture/domain/data | reviewed cross-layer failure and recovery; no rewrite required | NO_CHANGE | RECORDED |
| D002 | product | stale WorkProduct、Review、Host boundary | FULL_PART_REWRITE | APPLIED |
| D003 | knowledge | ingestion contracts already sufficient | NO_CHANGE | RECORDED |
| D004 | knowledge | conditional Graph/citation already sufficient | NO_CHANGE | RECORDED |
| D005 | agents | provider/budget contracts already sufficient | NO_CHANGE | RECORDED |
| D006 | agents/data | memory promotion boundary already sufficient | NO_CHANGE | RECORDED |
| D007 | agents/domain | existing single-controller narrative retained | NO_CHANGE | RECORDED |
| D008 | agents/domain | proposal-only capability boundary retained | NO_CHANGE | RECORDED |
| D009 | security/data | receipt/reconciliation contracts retained | NO_CHANGE | RECORDED |
| D010 | security | execute-time authorization retained | NO_CHANGE | RECORDED |
| D011 | eval | causal benchmark narrative | FULL_PART_REWRITE | APPLIED |
| D012 | deployment/services | upgrade/drain/resource narrative | FULL_PART_REWRITE | APPLIED |

Canonical Sync 是稳定 Target clarification，不是 Current、Measured 或 Production promotion。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/canonical-snapshot.md`

# Round-004 Canonical Snapshot

本文件记录本轮开始时的 Canonical 边界，而不是复制 12 份正文。

| Layer | Canonical Owner | Round-004 concern |
|---|---|---|
| Product | `docs/project/product/product-architecture.md` | Review、stale WorkProduct、Host closure |
| Domain | `docs/project/domain/legal-domain-model.md` | version、admission、ownership |
| Lifecycle | `docs/project/domain/domain-state-lifecycle.md` | new evidence、stale、re-evaluation |
| Runtime | `docs/project/agents/agent-platform.md` | Join、Replan、Checkpoint、Budget |
| Knowledge | `docs/project/knowledge/knowledge-evidence-architecture.md` | graph freshness、citation、scope |
| Services | `docs/project/services/service-architecture.md` | partial failure、worker/service boundary |
| Data | `docs/project/data/data-ownership-and-recovery.md` | recovery、receipt、outbox |
| Security | `docs/project/security/security-architecture.md` | epoch、approval、sandbox |
| Eval | `docs/project/eval/legal-eval-and-benchmark.md` | fair A/B/C、component survival |
| Deployment | `docs/project/deployment/microservice-deployment.md` | rolling upgrade、drain、resource |

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/adr-escalations.md`

# Round-004 ADR Escalations

- ADR escalation count: 0
- User gate escalation count: 0
- Reason: 本轮只澄清既有 Accepted Target 的一致性、失败语义和可逆出口，没有改变重大原则、安全信任边界或事实。
- Reversal conditions remain in the Canonical Owner documents and Delta records。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/11-plus-1-coverage-map.md`

# Round-004 11+1 Coverage Map

| Lens | Count | Questions | Delta |
|---|---:|---|---|
| 00 Overall Architecture | 12 | Q001–Q012 | D001 |
| 01 Product Surface | 6 | Q013–Q018 | D002 |
| 02 Input / Document Ingestion | 7 | Q019–Q025 | D003 |
| 03 Knowledge / Agentic GraphRAG | 11 | Q026–Q036 | D004 |
| 04 Model Gateway | 6 | Q037–Q042 | D005 |
| 05 Memory & Context | 8 | Q043–Q050 | D006 |
| 06 Agent Core / Planning & Control | 14 | Q051–Q064 | D007 |
| 07 Capability / Skill | 6 | Q065–Q070 | D008 |
| 08 Tool Runtime | 10 | Q071–Q080 | D009 |
| 09 Security | 8 | Q081–Q088 | D010 |
| 10 Observability & Eval | 6 | Q089–Q094 | D011 |
| 11 Infrastructure | 6 | Q095–Q100 | D012 |

Total: 100 questions。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/baseline-audit.md`

# Round-004 Baseline Audit

- Baseline SHA: `166a54d51aba0a822c3b5c539d1c43435f8c203f`
- Source state: Canonical Architecture `ACCEPTED_TARGET`; V3.1.1 normalization complete。
- Scope: Human Writing V3.1.2 and Architecture Consistency / Failure Semantics / Component Survival。
- Historical Round-003: immutable；不重算、不改写。
- Facts / Runtime / UI / Schema / Migration / Dependencies / Production Infra: unchanged。
- Existing Part A scorecard: Product、Multi-Agent、Services、Eval、Deployment 低于 Strong，作为本轮优先阅读输入。

本审计把“读起来像人写的”和“Contract 是否完整”分开。Part A 关注推导、场景和代价；Part B
继续由已有结构 verifier 检查。确定性 warning 不自动升级为人工 PASS。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/human-writing-audit.md`

# Human Writing Audit

## Deterministic signal boundary

`tools/scripts/verify_human_writing_v312.py` 只产生 warning。它不输出 Human Writing PASS；人工结论
由 Blue self-review、Red documentation review 和 ChatGPT review 共同完成。

| Canonical Doc | Template Phrase Density | Heading Density | English Density | Scenario | Failure Story | Tradeoff | Narrative Result | Rewrite |
|---|---|---|---|---|---|---|---|---|
| architecture.md | low | moderate | high | strong | strong | strong | CLEAR / DENSE | SECTION |
| product-architecture.md | low | moderate | moderate | strong | strong | strong | CLEAR | FULL_PART |
| legal-domain-model.md | low | moderate | high | strong | strong | strong | CLEAR / DENSE | NO |
| domain-state-lifecycle.md | low | moderate | high | strong | strong | strong | CLEAR / DENSE | NO |
| agent-platform.md | low | moderate | high | strong | strong | strong | CLEAR / DENSE | NO |
| multi-agent-runtime.md | low after rewrite | moderate | high | strong | strong | strong | CLEAR | FULL_PART |
| knowledge-evidence-architecture.md | moderate | moderate | high | strong | strong | strong | DENSE | NO |
| service-architecture.md | low after rewrite | moderate | moderate | strong | strong | strong | CLEAR | FULL_PART |
| data-ownership-and-recovery.md | low | moderate | moderate | strong | strong | strong | CLEAR / DENSE | NO |
| security-architecture.md | low | moderate | moderate | strong | strong | strong | CLEAR | NO |
| legal-eval-and-benchmark.md | low after rewrite | moderate | high | strong | strong | strong | CLEAR | FULL_PART |
| microservice-deployment.md | low after rewrite | moderate | high | strong | strong | strong | CLEAR | FULL_PART |

## Human review result

- Overall: `WARNING`
- Most natural: Product、Multi-Agent、Service、Deployment、Eval after rewrite。
- Most template-like before rewrite: Product、Multi-Agent、Service、Deployment、Eval。
- English-density concern: Architecture、Domain、Knowledge、Agent、Eval、Deployment remain dense；Part B precision justifies technical terms, but Part A should be reread by a human reviewer。
- Weak scenario risk: no structural failure remains；real-world user validation is still absent。
- Weak failure-story risk: all Part A sections contain a failure path, but no claim that the scenario happened historically。
- Part A regressions: none detected by structural verifier。
- Part B regressions: none detected by existing normalization and deep-dive verifiers。
- Human Writing Gate: `WARNING`, not automatic PASS。
