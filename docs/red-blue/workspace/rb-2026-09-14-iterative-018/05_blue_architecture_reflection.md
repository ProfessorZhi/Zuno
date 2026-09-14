# Blue Architecture Reflection — rb-2026-09-14-iterative-018

status: COMPLETE
zuno_base_sha: ad6e982f218e344100b2dc6b52e2fc939f3de208

本反思重新读取 canonical Zuno source。目标不是替 Blue 把面试回答改漂亮，而是判断 Red 压力究竟暴露了 Resume / Narrative / Docs / Architecture / Implementation / Evidence 中哪一层问题。

## BR-001 — 历史 direct route 与当前 Tool execution architecture 没有被候选人自然连起来

red_signal: Red Wave 2 连续追问 direct route 是否绕过 authorization / config / audit，以及 ReAct/direct 是否复制两套安全逻辑。

source_check:
- 当前 main 已存在真实 `ToolInvocationGateway`，并由 Tool runtime 调用；
- Current 有 PostgreSQL-backed `ToolUnitOfWork / SecurityUnitOfWork / InfrastructureUnitOfWork`；
- Current 持久化 PreparedAction、Attempt、ExecutionReceipt、EffectReceipt、Reconciliation 等表面；
- Security 已有 send 前 `validate_pre_effect_authorization()`，检查 prepared-action hash、SecurityEpoch、DENY、Approval 与 deadline；
- 这些 Current 能力不能反写成用户 4 月历史个人实现，但它们已经回答了“今天 direct/ReAct 应该如何收敛到统一执行边界”。

classification: NARRATIVE_GAP
why_this_classification: 架构方向已经存在，问题是 Resume 历史故事与今天 Current Tool Runtime 的演化没有一条自然叙事连接。若把它误判成 ARCHITECTURE_GAP，会重复设计现有 Gateway。

decision_impact: 不新增 Tool Gateway。后续项目/架构叙事应明确“历史 Agent-side route hardening → 今天统一 Tool execution / Security / Effect boundary”的时间层关系。
recommended_owner: docs/project + Tool/Capability/Effects/Security narrative + Blue Skill
retest_needed: yes

## BR-002 — Unknown Effect 的最终 Reconciliation convergence 仍是真实现缺口

red_signal: Red 从 Tool timeout 追“远端到底执行没执行”“谁决定 retry/reconcile”。

source_check:
- Current Gateway 在 send boundary 后遇到 `ToolEffectUnknownError` 能正确耐久化 UNKNOWN Attempt / ExecutionReceipt 和 OPEN Reconciliation；
- Current 第一次会返回 `reconcile_required / UNKNOWN_EFFECT`；
- canonical readiness review 明确指出尚未找到完整 `ReconciliationReceipt` resolver surface，manual assessment 也未证明能把 Reconciliation / EffectReceipt / ExecutionReceipt 收敛成最终 Effect truth；
- 该项已被标记为 implementation blocker，继续补文档或测试不能替代缺失实现。

classification: IMPLEMENTATION_GAP
why_this_classification: Target Authority / failure semantics 已经清楚，缺的是最终 resolver / convergence implementation。

decision_impact: 维持现有 Effects Architecture；需要独立 implementation authorization，而不是新造一个 Agent 层解决。
recommended_owner: Effects + Runtime integration
retest_needed: yes

## BR-003 — 长任务中的用户级 Tool 配置版本绑定没有形成清楚的 canonical story

red_signal: Blue 承认 4 月实现按 call-time 查用户配置；Red 追问任务中途配置变化时 retry 使用哪一版。

source_check:
- Runtime Target 已经强调 `run → PlanVersion → StepRun / input-version set → Tool/Capability/Security refs` 的可追溯绑定；
- Current Tool Runtime 也已有 PreparedAction / SecurityEpoch 等版本化边界；
- 本轮 source review 没找到一条同样清楚的 canonical 说明，把 mutable per-user MCP/server config 作为稳定 version/ref 绑定到一次 Tool logical action 或 StepRun。

classification: DOC_GAP
why_this_classification: 现有版本化架构很可能可以承载它，但文档没有让 Reviewer 直接回答“用户配置变化后 retry/replay 相信哪一版”。在证明 Owner/state semantics 真缺失前不升级成 Architecture Gap。

decision_impact: 先补 Tool configuration owner/version binding 文档与 Current source check；若确认不存在 authoritative config version，再单独进入 Architecture Revision。
recommended_owner: Capability / Tool Runtime docs
retest_needed: yes

## BR-004 — GraphRAG 目前最大问题仍是 Evaluation，而不是再加 ranking abstraction

red_signal: threshold=6、candidate group、path score 都是 heuristic；Red 追 threshold sweep、holdout、query class、latency/cost gate。

source_check:
- PF-031 只证明 5-query development regression → fixes → rerun；
- 没有正式 holdout、per-commit ablation、threshold calibration、多数据集 A/B；
- PF-026 已明确 GraphRAG 是 measurement-gated complexity，不要求默认开启。

classification: EVIDENCE_GAP
why_this_classification: 当前没有证据说明需要再设计更复杂 ranker。先用正式 benchmark 判断现有 GraphRAG 是否值得保留，以及在哪些 query class 开启。

decision_impact: 暂不把 threshold tuning / learned ranker / deeper graph traversal升级为 Target complexity。优先 formal eval。
recommended_owner: Evaluation + Knowledge
retest_needed: yes

## BR-005 — Graph entity alias 当前只是字符串归一，法律身份敏感场景缺 stable identity 语义

red_signal: Blue 主动指出去 article / parenthetical / hyphen 可能把本应区分的实体合并；Red 进一步问同名当事人、同名公司、法规版本。

source_check:
- Current `entity_alias.py` 是 lightweight normalized exact match；
- 本轮 source search 没恢复 stable graph EntityID / EntityVersion / merge-split lineage contract；
- Knowledge Target 已强调 DocumentVersion / IndexVersion / Evidence dependency / freshness，但 entity identity 本身没有在本轮材料中形成同等强度的 Authority；
- GraphRAG 又是 optional/measurement-gated。

classification: ARCHITECTURE_GAP
why_this_classification: **仅当 Zuno 决定保留 GraphRAG 处理 identity-sensitive 法律关系任务时**，稳定实体身份、版本和 alias lineage 属于 correctness Authority，不应继续由字符串 normalization 承担。若 benchmark 证明 GraphRAG 不值得保留，这个复杂度应直接删除。

decision_impact: 先以 Evaluation Gate 决定是否投资；通过 Gate 后再设计 stable entity identity/version，而不是现在无条件新增 Entity Service。
recommended_owner: Knowledge + Architecture Review
retest_needed: yes

## BR-006 — Blue 对 Memory 的“历史个人贡献”讲清了，但对今天 Current Memory surface 掌握不足

red_signal: Blue Wave 1 多次以 `InMemoryLayerStore` 作为并发/持久化讨论起点，第二波才提出 PostgreSQL target design。

source_check:
- Current main 已有 `DatabaseMemoryStore`、`MemoryRuntimeDao` 和 PostgreSQL memory tables；
- Current 有 durable review decisions、governance ledger、scope delete / privacy-delete evidence surface；
- `DurableMemoryStore` 明确只是 local replay/test surface，但 `DatabaseMemoryStore` 已是 Current adapter；
- 用户历史个人 Resume Claim 仍只能落到 PF-029/PF-030，不可把后续整个 Current Memory 平台改成个人历史成果。

classification: NARRATIVE_GAP
why_this_classification: 这里不是“Memory 还没有数据库”，而是候选人需要同时掌握两条时间线：我当时做了什么，以及项目今天已经演化到哪里。

decision_impact: Blue Skill 增加“Historical Ownership answer 后，如问题转到 current architecture，重新读取 Current Evidence”的切换规则；Project narrative 补 evolution bridge。
recommended_owner: Blue Skill + docs/project + Memory current evidence narrative
retest_needed: yes

## BR-007 — Memory review status 有 durable surface，但 Approval Authority 与 in-flight freshness 仍未闭环

red_signal: Red 追“谁能 approve”“能不能绕过 review”“已经 readback 后撤销怎么办”。

source_check:
- Current 有 `MemoryReviewDecision`、review decision table、governance ledger 和 privacy delete；
- `DatabaseMemoryStore.save_memory_candidate()` 仍能持久化 candidate 的 `review_status` 字段，Current source surface 本身没有在本轮 review 中证明只有受授权 review service 才能改变有效 approval state；
- ContextPacket 能保存 source trace/selection，但本轮没有恢复一个 Memory Review Epoch / Revocation Epoch 在 model invocation 前 fail-closed recheck 的 Current contract；
- 这不是单纯“多写测试”能够回答的权限/时序语义。

classification: ARCHITECTURE_GAP
why_this_classification: 谁拥有有效 Memory Approval、哪些写路径能改变它、in-flight packet 遇到 revocation 如何失效，属于 Authority + freshness semantics。

decision_impact: Architecture Review 应明确 Candidate state 与 Review Decision 的权威关系、授权写边界、有效 review epoch/version 以及 ContextPacket 的 stale/reprepare 规则；再决定 Current implementation 缺口。
recommended_owner: Memory/Context + Security + Architecture
retest_needed: yes

## BR-008 — Late Result / stale Plan 的 Authority 已经比 Blue 现场回答更完整

red_signal: Red Wave 2 问 Specialist late result 在 replan 后如何处理。

source_check:
- Runtime reference 已要求每个 dispatch/result 绑定 `run → PlanVersion → StepRun/Branch → input-version set → Knowledge/Capability/Tool/Model refs → SecurityEpoch`；
- 模块总参考已有统一 Late Result 验收；
- Decision 0015 明确 replan 从未完成剩余任务开始，已提交 Domain fact、已确认 Effect、accepted Step output 不因新 PlanVersion 被重跑抹掉；
- Effect unknown 即使旧 Plan 取消也不能当“未执行”，仍由 Effect owner reconcile。

classification: NO_ZUNO_CHANGE
why_this_classification: 当前 Target 已有这套原则。Multi-Agent Specialist 可以复用同一 dispatch/result identity，不需要因为引入 Agent 再设计另一套 late-result authority。

decision_impact: 如果未来增加 Specialist Agent，要求其 handoff 复用 Runtime 的 PlanVersion / StepRun / input-version / SecurityEpoch，而不是新增 parallel truth model。
recommended_owner: Runtime implementation / future Multi-Agent adapter
retest_needed: yes

## BR-009 — Multi-Agent 不需要成为新的 Authority 模块，应该成为 Runtime 的可测 topology option

red_signal: 用户明确希望允许 Multi-Agent 改造；Red 连续追 Tool vs Subgraph vs Specialist、Supervisor 单点、shared state、retry、Memory、late result。

source_check:
- PF-026 已将 Persistent Multi-Agent 标记为 TARGET_OPTIONAL / MEASUREMENT_GATED；
- 当前 Architecture 的 Domain / Knowledge / Capability / Effects / Security Authority 与执行 topology 是分离的；
- Runtime 已有 Single Controller、PlanVersion、StepRun、parallel dispatch、late-result/recovery 方向；
- 没有证据证明新增一个“Multi-Agent Authority”能解决新的业务真值问题。

classification: NARRATIVE_GAP
why_this_classification: 架构已有足够 ownership primitives，但人类叙事尚可更明确写出 topology ladder：Tool → Subgraph → parallel worker → Specialist Agent → Persistent Multi-Agent，以及每一级的出现条件、额外成本与删除条件。

decision_impact: 不新增第十个 Multi-Agent 模块。把 Multi-Agent 作为 Runtime / Application composition strategy，并要求 benchmark 证明 Specialist autonomy 的增益。
recommended_owner: Runtime + Application Part A narrative
retest_needed: yes

## BR-010 — Generic Host + Zuno Backend 的方向应继续压过“自研 Agent 平台身份”

red_signal: Red 最后追如果 Generic Host 和自研 Runtime 效果相同，删什么。

source_check:
- Project / architecture 已明确 Generic Agent Platform capability 优先复用；
- Native Runtime、Persistent Multi-Agent、GraphRAG、Reflection 都 measurement-gated；
- Zuno differentiating authority 落在 legal material/evidence/version、Capability qualification、Formal Domain admission、Effect/Security correctness 和 legal Evaluation。

classification: NO_ZUNO_CHANGE
why_this_classification: Blue Wave 2 的结论与现有产品/架构方向一致。

decision_impact: 下一轮架构优化应优先证明“哪些 generic orchestration 可以删除/外置”，而不是继续增加 Agent 对象。
recommended_owner: Architecture / Build-Buy review
retest_needed: yes

## Reflection summary

本轮没有得到“Zuno 应全面改成 Multi-Agent”的结论。更有价值的结果是：

1. Current Tool Runtime 已经比简历历史链更成熟，候选人的 Current understanding / narrative 需要跟上；
2. Effects reconciliation convergence 是确定的 Implementation Gap；
3. GraphRAG 下一步首先是正式 Evaluation，只有保留 identity-sensitive GraphRAG 时 stable entity identity 才值得升级成架构复杂度；
4. Memory durable store 已存在，但 review authority + in-flight freshness/revocation 仍是值得真正 Architecture Review 的问题；
5. Multi-Agent 应使用现有 Runtime/Domain/Memory/Effects Authority，不建立第二套 truth；它是 measurement-gated topology option；
6. 下一轮应该用 Multi-Agent/Generic Host challenger benchmark 去攻击当前 execution topology，而不是先画一个更复杂的多 Agent 图。
