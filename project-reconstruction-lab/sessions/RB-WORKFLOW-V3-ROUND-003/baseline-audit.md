# PART-A-BASELINE-AUDIT / PART-B-BASELINE-AUDIT

Baseline: f866ca4d748ba189a83a39fe75b92a6ba36f4e9d

本审计在 Part A/B 重构前完成。分数是 Blue/Red 文档审查的结构化判断，不是运行质量、历史事实或生产证据。

| Canonical Owner Doc | Part A Before | Part B Before | Part A After | Part B After | Part A Gate | Part B Gate |
|---|---:|---:|---:|---:|---|---|
| docs/project/architecture/architecture.md | 76 | 82 | 90 | 91 | PASS | PASS |
| docs/project/product/product-architecture.md | 64 | 78 | 88 | 89 | PASS | PASS |
| docs/project/domain/legal-domain-model.md | 68 | 84 | 91 | 93 | PASS | PASS |
| docs/project/domain/domain-state-lifecycle.md | 65 | 86 | 89 | 94 | PASS | PASS |
| docs/project/agents/agent-platform.md | 70 | 83 | 91 | 92 | PASS | PASS |
| docs/project/agents/multi-agent-runtime.md | 61 | 76 | 86 | 88 | PASS | PASS |
| docs/project/knowledge/knowledge-evidence-architecture.md | 67 | 82 | 90 | 93 | PASS | PASS |
| docs/project/services/service-architecture.md | 59 | 77 | 86 | 89 | PASS | PASS |
| docs/project/data/data-ownership-and-recovery.md | 60 | 86 | 87 | 92 | PASS | PASS |
| docs/project/security/security-architecture.md | 63 | 84 | 89 | 93 | PASS | PASS |
| docs/project/eval/legal-eval-and-benchmark.md | 66 | 85 | 88 | 94 | PASS | PASS |
| docs/project/deployment/microservice-deployment.md | 58 | 78 | 85 | 89 | PASS | PASS |

## 主要缺口

- Part A 与 Part B 没有同文件明确分层，读者需要从 Contract 反推 Why。
- Product、Multi-Agent、Service、Deployment 的业务场景和主要失败故事不够连贯。
- Round-002 / Dxxx 过程性追加位于 Canonical 正文末尾，破坏稳定阅读路径。
- Part B 的 version、retry/recovery、idempotency、security、observability 和 evidence 约束分布不均。

## 优先修复

1. 同文件建立 Part A Narrative 与 Part B Specification，不创建镜像文档。
2. 每个 Owner 文档加入一个明确标记的 Target Scenario，并解释 Happy Path、Major Failure 和 Reversal。
3. 将 Round/Dxxx/Qxxx trace 留在 Lab Session 与 Delta，不留在 Canonical 正文。
4. 补齐可实现的 Contract、State、Failure、Recovery、Idempotency、Security、Observability 和 Verification。

## Gate

Part A 最低 80/100，Part B 最低 85/100。After 分数只能在 Round-003 完成并通过质量 verifier 后成立。
