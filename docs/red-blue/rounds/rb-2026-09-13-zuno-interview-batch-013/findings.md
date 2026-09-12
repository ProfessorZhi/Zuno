# Round #013 Findings

Round: `rb-2026-09-13-zuno-interview-batch-013`  
Status: `ACTIVE_AFTER_BATCH_001`  
Batch 001: `100 questions / 85 PASS / 13 PARTIAL / 0 FAIL / 2 UNSUPPORTED_CLAIM`

Findings are deduplicated from the full transcript. They do not own Project, Architecture, Evidence or Resume truth.

## F1 — Tool / MCP 个人任务已经可证明，但最深实现追问仍缺一份可直接引用的任务证据链

- **severity:** S2
- **gap_type:** `EVIDENCE_GAP / RESUME_CLAIM_RISK`
- **trigger_questions:** Q016, Q018, Q019, Q020, Q021, Q022, Q024

PF-032 已经把简历第一条从“参与 Tool Calling”推进到两段具体历史工作：2026-04-15 `GeneralAgent` Tool/MCP strategy 收口，以及 2026-04-28 Workspace MCP direct-route / ReAct fallback 与 recursion / weather-parameter hardening。Blue 能守住 Ownership，也没有把后来的 PreparedAction / Approval / EffectReceipt / Reconcile 反写进 4 月历史。

缺口出现在大厂面试继续向代码级追问时：当前 canonical interview-facing 资料没有同时保存以下因果链：

```text
原需求 / 失败输入
→ 旧调用链实际怎样失败
→ 为什么选择当前改法而不是另一个 wrapper / route
→ 具体改动位置
→ regression test 的粒度与断言
→ 改动后能证明的结果
```

因此 Blue 对 custom MCP recursion、weather 参数解析、user-level config 的精确绑定、direct-route 判定条件和 test granularity 只能诚实回答“canonical source 没有恢复到这一层”。这不会让当前简历 Claim 失真，但会让第一条最亮眼的个人经历在深挖时较早触顶。

### Decision impact

不需要修改 Zuno Architecture。后续如果能从 PF-032 已指向的历史 commits/tests 恢复一份**bounded personal task evidence**，应优先补到项目事实/面试证据层，而不是增加 Target 对象。若恢复不到，简历继续维持当前 bounded wording，不新增性能、稳定性或业务收益 Claim。

### Evidence needed

- 2026-04-15 / 04-28 exact diff；
- 对应 test artifact 的关键断言；
- 若存在，原始 Issue / requirement / bug reproduction；
- 若不存在，明确标记 root-cause detail not recovered。

### Retest scenario

换一种大厂实现深挖：从“为什么不用 MCPAgent-as-Tool”连续追到调用栈、错误输入、测试断言和 alternative，而不提示 PF-032 表述。

---

## F2 — Context / Memory 简历切片有较强 PR 证据，但 Scope、Reviewer 运行方式与安全隔离细节仍会被追穿

- **severity:** S2
- **gap_type:** `EVIDENCE_GAP`
- **trigger_questions:** Q030, Q032, Q033, Q035

PF-029 / PF-030 已经是当前个人证据中最完整的一组：`GeneralAgent.prepare_context()`、同 scope task summary、仅 `APPROVED` structured memory、Context Pack policy、source-id trace、review / provenance gate，以及 focused tests 都有历史 PR/commit/test 佐证。Blue 也正确拒绝把 Coding Agent 项目里的 token compression、裁剪阈值等工作借给 Zuno。

剩余缺口集中在四个实现/运行问题：

1. `same scope` 的 exact key / boundary 没有在 canonical interview source 中冻结；
2. Memory review 在真实产品里由谁处理、没有 reviewer 时如何运行，目前没有 Project Reality 证据；
3. `source-id trace` 能追到的具体 referent chain 只记录了方向，没有面试级细节；
4. PF-029 没有证明 tool/memory 内容的 prompt-injection / instruction-data isolation 已经实现。

这些缺口不能用今天 Target 的 Domain / Security / Memory 原则反写成历史 Current。

### Decision impact

不改 Runtime/Domain Authority。优先从 PF-029 对应 PR #8 / commits / focused tests 恢复 exact scope 与 provenance contract；Reviewer 运营和 prompt-injection isolation 若历史无证据，继续写 Unknown / not proven。

### Evidence needed

- PR #8 exact diff/test names；
- scope key / filtering predicate；
- source-id trace data shape；
- review gate 的实际 owner / storage / workflow（若存在）；
- instruction/data isolation test（若存在）。

### Retest scenario

让面试官只盯 `prepare_context()`：给两个 Matter、同一用户、冲突 APPROVED memory 与恶意 Tool output，要求候选人明确当前历史实现与今天 Target 各能做到哪里。

---

## F3 — OpenViking 仍属于“确认参与、实现 artifact 未恢复”，不适合作为独立强 Claim

- **severity:** S1
- **gap_type:** `EVIDENCE_GAP`
- **trigger_questions:** Q038

PF-011 只能支持用户确认参与 OpenViking 在 Memory / Context 区域的接入；公开 Git 目前没有恢复对应 SDK / Adapter / 数据结构和生产使用方式。Blue 能正确停在“参与接入”，没有用后续 Context / Memory V2 或 PR #8 替代这段历史。

### Decision impact

当前 v5 简历没有把 OpenViking 单独放成主要 bullet，因此不要求立即修改简历。面试中若主动提到，只应作为补充背景；除非恢复 artifact，否则不要把它升级成“主导 OpenViking 集成 / 设计 Memory 架构 / 生产使用”。

### Evidence needed

历史代码、配置、提交、运行记录或私有工作材料。

### Retest scenario

面试官直接问“OpenViking 你改了什么代码，为什么用它而不是自己做 Memory？”观察是否仍能守住 participation-only 边界。

---

## F4 — Batch 001 有两道 Red 问题违反固定来源策略：不能把对话记忆里的 #212 诊断事实当作 Round 已知事实

- **severity:** S2
- **gap_type:** `EVIDENCE_GAP`
- **scope:** `ROUND_PROCESS`, not Zuno Architecture
- **trigger_questions:** Q061, Q062

Red 在 Q061/Q062 使用了“#212 已证明 failed v2 replaces last-good manifest”这一具体 premise。但 Round manifest 固定的 Zuno base `a7b35286...` 的 canonical `docs/evidence/` / allowed Governance facts 中没有 #212，Red calibration sources 也没有这项内容。

Blue 按 closed-book 规则正确拒绝确认这个 premise，只回答 Target 的 generation isolation / activation 尚未 implementation-proven。Verifier 因此将两题判为 `UNSUPPORTED_CLAIM`，不能据此产生 Knowledge implementation finding。

### Decision impact

从 Batch 002 起，Red 的“当前项目材料”必须显式绑定固定 Zuno base 的可访问 source set；不得使用当前聊天记忆、旧 summary、已关闭 diagnostic branch 或未列入 manifest 的事实生成 Current-specific 问题。若未来要攻击 #212，先把对应证据加入允许的 Round source 或 canonical Evidence。

这是一条 Harness / Round source-policy 修正，不修改 Zuno Knowledge Architecture。

### Retest scenario

Batch 002 中换问法，只从当前 Knowledge Target + canonical Evidence 的 `not implementation-proven` 出发，不带 #212 premise，再观察 Blue 是否会自行制造该缺陷。

---

## Batch 001 non-findings worth preserving

以下区域被高压追问后没有形成新文档/架构 Finding：

- History / Current / Target / Unknown 分层；
- Pilot != Production；
- LIPLAB research != personal ownership；
- Research Artifact → Capability → Provider → Qualification → Candidate → Formal Business Fact；
- retrieval miss != absence；
- GraphRAG baseline / ablation / kill condition；
- Checkpoint != Domain completion proof；
- Retry / Replan / Reconcile；
- external timeout → Unknown / Reconcile；
- SecurityEpoch / Secret revoke 的 bounded Current evidence；
- Mandatory Audit violation / Reconciliation convergence gap 的诚实 Current 表述；
- HumanDecision != automatic ground truth；
- Release Eval != Production qualification；
- Generic Agent Harness should be reused and Native Runtime remains measurement-gated；
- logical responsibility != microservice deployment。

这些 PASS 只表示本批问题在允许文档中得到来源支持的回答，不表示对应 Target 已经实现或生产验证。

## Next batch priority

Batch 002 不再平均覆盖九模块。问题预算优先转向：

1. PF-032 Tool/MCP exact implementation / alternative / regression evidence；
2. PF-029 Context/Memory exact scope / provenance / review boundary；
3. personal ownership under code-level questioning；
4. project reality / real user workflow / measurable business outcome；
5. selected backend fundamentals naturally derived from these personal claims。

已经稳定通过的 Target architecture explanation 降权，避免继续生成只会重复文档内容的题目。
