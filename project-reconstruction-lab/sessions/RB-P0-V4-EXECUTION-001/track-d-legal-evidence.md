# Track D — Legal Evidence / Citation

## Q039 Scope Split

Red 接受 Q039 拆分为：

- `Q039-C`：Claim → Evidence → Citation 的 Critical Invariant；
- `Q039-B`：法院 QA、A/B/C、Citation Correctness、Evidence Sufficiency 和 Unsupported Claim Rate 的 V5 Product Benchmark Gap。

## Q039-C execution

当前 `GroundedSynthesisEngine` 在 retrieval observation 没有 citation 时生成 unsupported claim
并保留 insufficient 结果，fixture 通过。另一个 wrong-span fixture 被标记 XFAIL：当前
`RuntimeCitationBinder` 按位置取 citation，没有文档/Span provenance 校验，因此不能拒绝错绑。

## Q039-B

没有真实法院 QA、参考答案、评价人、固定预算或 A/B/C 结果。本项保持
`V5_BENCHMARK_REQUIRED`，不得生成历史项目质量结论。

## Track D result

```text
Q039-C: executed, invariant gap exposed
Q039-B: V5_BENCHMARK_REQUIRED
Accepted: 0
```
