# P0 Scope Audit

## 审计结论

12 个原始 P0 均保留。只有 Q039 同时包含 Critical Architecture Invariant 与 Product
Effectiveness Claim，因此执行 `SCOPE_SPLIT`；拆分不删除原始风险。

## Scope Split Registry

| Original P0 | Derived Invariant ID | Derived Benchmark Gap ID | Critical Scope | Effectiveness Scope | Reason | Red Approval |
|---|---|---|---|---|---|---|
| Q039 | Q039-C | Q039-B | Claim → Evidence → Citation 绑定正确；证据不足时 abstain/mark unsupported/request more evidence | 法院 QA 总体回答质量、A/B/C、Citation Correctness、Evidence Sufficiency、Unsupported Claim Rate | Architecture gate 能由 fixture/contract 验证，效果需要代表性法律数据和 V5 benchmark | `SCOPE_SPLIT_ACCEPTED` |

Q039-C 的 wrong-span fixture 已暴露当前实现只按位置绑定 Citation，不能证明文档/Span
provenance 正确；Q039-B 保持 `V5_BENCHMARK_REQUIRED`，不生成历史法院结果。

## 未拆分项目

Q005、Q016、Q033、Q053、Q061、Q063、Q064、Q066、Q067、Q070、Q097 当前仍是 Critical
Architecture Invariant。它们的质量收益、法律效果、生产可靠性不能从本轮 V4 结果推断。

## Traceability rule

每个派生项都回指原始 Q039；原始 P0 不得从矩阵、Repair 或 Closure 记录中消失。
