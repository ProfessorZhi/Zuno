# Round Improvement Ledger — rb-2026-09-14-iterative-018

status: DRAFT_REVIEW
user_improvement_review_status: PENDING

## IMP-001 — Automated Round 默认改为 Batch Duel

signal: 用户明确要求 Blue/Red 不在聊天里逐题等待人工回答，而是批量写 GitHub。
root_cause: Harness 把 automated calibration 和真人 live interview 混成同一种 turn-by-turn execution。
primary_class: HARNESS_GAP
owner: `.agent/red-blue` protocol / system / templates / tests
proposed_change: 新增 `execution_mode: BATCH_DUEL | LIVE_INTERVIEW`；CHATGPT_AUTO 自动 Round 默认 BATCH_DUEL。Wave 1 批量攻击/回答，Wave 2 必须读取上一波回答后再生成；Pressure Suite 继续是离线覆盖库，不要求 Blue 全答。
evidence_needed: 下一轮两波 GitHub artifact + Wave2 对 Wave1 的 handle trace。
risk_if_changed: Batch 模式适应粒度低于逐题 live；通过 wave-level adaptation 和较小 Wave size 控制。
status: APPLY
approval_basis: explicit user instruction in current round
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest: 自动 Round 不要求用户逐题回答；Red Wave2 必须引用 Blue Wave1 的具体缺口。

## IMP-002 — Blue Skill 增加 Historical / Current / Target mode switch

signal: Blue 能讲清个人历史实现，但在 current architecture 问题上有时仍围绕旧 InMemory / 4 月 Tool route 推演，遗漏当前 `ToolInvocationGateway`、DatabaseMemoryStore 等现有 surface。
root_cause: Defense Skill 强调 ownership/evidence boundary，但没有先分类当前问题的时间层。
primary_class: BLUE_SKILL_GAP
owner: `.agent/red-blue/defense-model.md`
proposed_change: 每题内部先分类 `HISTORICAL_OWNERSHIP / CURRENT_ARCHITECTURE / TARGET_DESIGN / FUNDAMENTAL`；Historical 只讲本人证据，Current 重新读取 `zuno_base_sha` Current evidence，Target 才允许设计推演。Artifact 分离 `spoken_answer` 与 `source_support/boundary`。
evidence_needed: 下一轮同一个 Tool/Memory thread 同时出现“我当时做的”和“今天项目已经演化到”的自然切换。
risk_if_changed: 回答可能过长；要求只在面试官切时间层时展开。
status: NEEDS_OWNER_DECISION
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest: Red 明确从 historical diff 切 current design，看 Blue 是否切 source layer。

## IMP-003 — 补 Project evolution bridge，不把 Current 冒充个人历史成果

signal: 当前 Tool/Memory architecture 已明显超过 Resume 所述历史增量，但项目叙事没有给候选人一个自然的演化桥。
root_cause: History 与 Current 被严格分离后，缺少“后来怎么演化”的连续叙事。
primary_class: NARRATIVE_GAP
owner: `docs/project/README.md` / relevant module Part A
proposed_change: 在项目正文增加少量演化段：历史 Agent-side Tool/Memory 工作 → 当前统一 Tool Runtime / durable Memory surface；明确这些 Current 能力是项目后续演化，不归入用户历史 Ownership。
evidence_needed: Current source/evidence links + provenance boundary.
risk_if_changed: 容易把“今天理解/维护”写成“当时个人实现”；必须保留时间标签。
status: NEEDS_OWNER_DECISION
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest: Blue 用 30–60 秒讲出 historical delta → current system evolution。

## IMP-004 — Effects Reconciliation convergence 实现缺口

signal: Red 追 remote Tool timeout / unknown outcome；Blue 只能讲 target reconcile。
root_cause: Current 已有 UNKNOWN durable ledger / escalation，但缺 conclusive ReconciliationReceipt / resolved effect truth writer。
primary_class: IMPLEMENTATION_GAP
owner: Effects + Runtime integration
proposed_change: 独立 Implementation Program 实现 remote-query/manual conclusion → resolved Reconciliation / EffectReceipt / ExecutionReceipt convergence，并验证 restart replay。
evidence_needed: current readiness review blocker、failure injection、resolved receipt trace/tests。
risk_if_changed: 真实外部副作用和人工结论错误收敛风险高，需要独立 implementation authorization。
status: NEEDS_OWNER_DECISION
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest: remote success + lost local response + restart 后最终收敛到唯一 Effect truth。

## IMP-005 — Tool user-config version binding 文档/语义检查

signal: call-time user config 在长任务中可能改变，retry/replay 到底相信哪版不清楚。
root_cause: Runtime 已有 PlanVersion/StepRun/input refs/SecurityEpoch，但 mutable MCP/server user config 的 authoritative version binding 在本轮 canonical source 中不够明确。
primary_class: DOC_GAP
owner: Capability / Tool Runtime docs
proposed_change: 先审计 Current 是否已有 ConfigVersion / prepared action hash 对用户配置的完整绑定；有则补文档，无则单独升级 Architecture Review。
evidence_needed: code/schema/receipt fields + replay test。
risk_if_changed: 过早新建 ConfigVersion object 可能重复已有 PreparedAction semantics。
status: NEEDS_OWNER_DECISION
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest: 配置在 run 中途变化时，旧 Step retry 行为可唯一解释。

## IMP-006 — GraphRAG formal evaluation before more architecture

signal: threshold=6、candidate groups、path scoring 都是 heuristic；现有 5-query smoke 无 holdout/ablation。
root_cause: 开发 regression 已修，但没有回答 GraphRAG 对哪些法律 query 值得默认存在。
primary_class: EVIDENCE_GAP
owner: Evaluation + Knowledge
proposed_change: 建立 query-class benchmark：single-hop / semantic / multi-hop relation / ambiguous entity / freshness；对 BM25、Vector、Hybrid+rerank、GraphRAG 比较 Recall/MRR/chain/citation quality + p50/p95 latency + cost/fallback；dev tuning 与 holdout 分离。
evidence_needed: frozen dataset/runner/config、A/B、threshold sensitivity、ablation、failure analysis。
risk_if_changed: Benchmark 设计不当会把简单 query 淹没真实多跳收益。
status: NEEDS_OWNER_DECISION
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest: 能明确给出 GraphRAG enable/disable query class 和 kill condition。

## IMP-007 — Stable Graph Entity Identity（条件性 Architecture Gap）

signal: lightweight alias normalization 会把 parenthetical/hyphen 等差异抹掉；同名当事人、公司、法规版本存在误合并风险。
root_cause: Current Graph entity match 主要是 normalized string exact；本轮未恢复 stable EntityID/EntityVersion/merge-split lineage。
primary_class: ARCHITECTURE_GAP
owner: Knowledge + Architecture Review
proposed_change: **只有 IMP-006 benchmark 证明 identity-sensitive GraphRAG 值得保留后才执行**。届时设计 stable entity identity、type/source/jurisdiction/version disambiguation、alias lineage 与 merge/split/tombstone semantics。若 GraphRAG 不过 Gate，删除复杂度而不是新建 Entity Service。
evidence_needed: ambiguous-entity bad cases + benchmark gain + current graph model audit。
risk_if_changed: 高复杂度，容易从检索优化膨胀成通用 Knowledge Graph 平台。
status: DEFER
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest: 先过 GraphRAG Evaluation Gate。

## IMP-008 — Memory Approval Authority + in-flight freshness

signal: Current 有 review_status、ReviewDecision、governance ledger、privacy delete，但谁能改变有效 approval state，以及 ContextPacket 已装入后遇到 revocation 怎么 fail-closed，没有形成完整 Authority。
root_cause: Candidate state、review decision、Security authorization、Context freshness 分散，read-time APPROVED gate 不能独自解决 TOCTOU。
primary_class: ARCHITECTURE_GAP
owner: Memory/Context + Security + Runtime Architecture
proposed_change: Architecture Review 明确：ReviewDecision 是否为唯一 approval authority；普通 candidate write 是否禁止直接赋 APPROVED；MemoryReviewEpoch/SnapshotVersion 如何绑定 ContextPacket；强 revocation 如何触发 stale/reprepare/cancel；已经发送 Effect 时如何继续 reconcile。
evidence_needed: current store/write-path audit、Security owner mapping、privacy-delete flow、context invocation timing tests。
risk_if_changed: 容易过度设计成复杂审批系统；只为需要长期 structured memory 的高风险类型启用强 review/freshness。
status: NEEDS_OWNER_DECISION
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest: approval 后撤销发生在 prepare_context 与 model/tool invocation 之间时，系统行为唯一且可测试。

## IMP-009 — Multi-Agent 作为 topology challenger，不新增 Authority 模块

signal: 用户允许 Multi-Agent 改造；Red 追 Specialist state、Supervisor、late result、Memory、recovery 后，现有 Authority primitives 仍能承载这些问题。
root_cause: 当前文档对 “什么时候 Tool/Subgraph/controller+workers 升级到 Specialist/Persistent Multi-Agent” 还不够直观。
primary_class: NARRATIVE_GAP
owner: Runtime + Application architecture narrative
proposed_change: 增加 topology ladder 与 adoption/deletion criteria：Tool → Subgraph → parallel worker → Specialist Agent → Persistent Multi-Agent。所有 Agent result 继续绑定 PlanVersion/StepRun/input versions/SecurityEpoch；Domain/Memory/Effects Authority 不随 topology 复制。
evidence_needed: Generic Host / single Agent / controller+workers / Multi-Agent benchmark design。
risk_if_changed: 文档容易让读者误以为 Target 已决定采用 Multi-Agent；必须明确 optional/measurement-gated。
status: NEEDS_OWNER_DECISION
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest: Red 给一个专业角色隔离/并行任务场景，Blue 能先选最简单 topology 并给退出条件。

## IMP-010 — Resume 暂不加入 Multi-Agent / Production claim

signal: Red 对现有六条 Resume Claim 均达到 PASS，GraphRAG 达 STRONG_PASS；Multi-Agent 讨论主要是设计推演。
root_cause: Resume 当前边界已经比较合适，没有必要为了架构方向提前加入未实现能力。
primary_class: NO_CHANGE
owner: Resume Builder
proposed_change: 当前六条作为下一轮候选 baseline；只有 IMP-006/008/009 等形成真实 Current implementation/evidence 后才考虑新增或替换 bullet。
evidence_needed: none now.
risk_if_changed: 提前写 Multi-Agent 会把 Target 推演伪装成个人实现。
status: APPLY
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest: 同一 Resume 在 Batch Duel 下继续验证 interviewability。

## Proposed apply order

1. IMP-001 — Batch Duel Harness（用户已明确批准）。
2. IMP-002 / IMP-003 — Blue Skill + evolution narrative。
3. IMP-005 — 先 source audit，不新造 ConfigVersion。
4. IMP-006 — GraphRAG formal eval。
5. IMP-008 — Memory Authority Architecture Review。
6. IMP-009 — Multi-Agent topology narrative + benchmark challenger。
7. IMP-004 — 独立业务实现授权后修 Effect convergence。
8. IMP-007 — 仅在 GraphRAG Eval 证明值得保留后启动。

本 Ledger 不把任何 Target Proposal 自动升级为 Current，也不因本轮 PASS 改写 Evidence status。
