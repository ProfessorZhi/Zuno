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
