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
