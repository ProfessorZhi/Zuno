# Rationale Duplication Audit

Exact duplicate rationale count: 0

Result: `WARNING_REVIEWED`。没有完全相同的理由；因为每条理由都沿用统一的逻辑顺序，部分相似度较高，但每条都包含具体 Scenario、Object、Unresolved Issue 和 Maturity Gate。

## Highest similarity samples

- Q001 / Q002: similarity=0.71；一个是跨版本恢复权威，一个是 Host/Native Admission authority，Object 和未跨过的 Gate 不同。
- Q014 / Q022: similarity=0.69；一个是 Review 决定版本，一个是 Parser Projection 发布权，均保留了不同的具体场景。
- Q040 / Q069: similarity=0.67；一个测量 fallback 归因，一个测量 Capability Provider 替换，不能合并为同一理由。
