# Current Test Baseline

状态：`CURRENT / CURRENT_HEAD_VERIFICATION_NOT_ESTABLISHED / QUALITY_NOT_ESTABLISHED`

## 当前 HEAD 的证据状态

本页不再把旧 selected-suite 结果描述为当前 HEAD 的 Final Verification。

本次 Evidence review 绑定：

```text
review_snapshot: eca4a7ebcadbc1c964f174e3b2ce620f9ecbdf5e
current_head_runtime_verification: NOT_ESTABLISHED_IN_GITHUB_CI
full_ci: NOT_RUN / NO_CURRENT_RUNTIME_CI
benchmark: BLOCKED_NOT_MEASURED
quality: NOT_YET_PROVEN
production_readiness: NOT_ESTABLISHED
```

当前 GitHub Actions 只保留 `Architecture document set` workflow。它负责 Project / Architecture / Modules / Governance / Evidence 的文档集合、语义一致性、Human Readability、entrypoints 和对应 repository tests；它不运行完整 Product、Runtime、Domain、Knowledge、Capability、Effects、Model Gateway、Security 或真实外部集成测试。

因此，Architecture document-set CI 通过只能证明文档与对应治理约束没有回归，不能升级成“当前 Runtime tests 已验证”或“Full CI 已通过”。

## 历史 selected verification

下面结果仍是有效的历史工程记录，但它绑定的是旧快照：

```text
historical_verified_head: 1ea56a5d61afa27ebda8f8745a6dbc6584796d05
repository_gates: PASS
canonical_runtime_tests: 67 passed
closure_documentation_tests: 23 passed
final_selected_suite: 90 passed
full_ci: NOT_RUN / NO_GITHUB_STATUS
benchmark: BLOCKED_NOT_MEASURED
quality: NOT_YET_PROVEN
production_readiness: NOT_ESTABLISHED
```

当时执行的 canonical checks 包括：

- Product Application boundary：3 passed（组合运行共 39 passed）；
- Product/API layering boundary：32 passed；
- Agent Run runtime behavior：Graph、checkpoint、restart、approval interrupt、recovery、plan/replan、idempotency、tool fail-closed；
- Retrieval canonical mode composition：29 passed；
- Multihop evaluator public modes（`normal` / `enhanced` / `auto`）：12 passed；
- Python compile：`python -m compileall -q src/backend/zuno tests`；
- 当时的 docs/repository verifiers。

这些数字只能回答“`1ea56a5...` 当时跑过什么”。它们不能自动覆盖后来加入或修改的 Domain mutation、Citation provenance、Runtime tests、文档体系和治理入口。

## 当前仍应保护的行为

后续 current-head verification 仍应覆盖：文件 hash / tenant boundary、durable ingestion handoff、Run submit、restart recovery、Security fail-closed、approval binding、cancel 幂等、artifact authorization、event streaming、retrieval observability、tenant isolation、persistence failure stop、duplicate command idempotency、未知外部效果 reconciliation，以及新增的 Domain / Citation / cross-owner recovery 行为。

旧 phase-named 测试不应因为历史存在自动恢复成当前验收入口。若某个旧 verifier 已被当前 canonical gate 取代，应删除或现代化；若仍保护真实不变量，则应进入当前 verification map，并在同一 SHA 上获得可复现结果。

下一步的 current-head verification 与 Module Detail Freeze readiness 见 [`../governance/module-detail-freeze-readiness-review.md`](../governance/module-detail-freeze-readiness-review.md)。
