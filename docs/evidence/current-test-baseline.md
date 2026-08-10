# Current Test Baseline

状态：`CURRENT / QUALITY_NOT_ESTABLISHED`

本轮已执行的 canonical checks：

- Product Application boundary：3 passed（组合运行共 39 passed）；
- Product/API layering boundary：32 passed；
- Agent Run runtime behavior：Graph、checkpoint、restart、approval interrupt、
  recovery、plan/replan、idempotency、tool fail-closed；
- Retrieval canonical mode composition：29 passed；
- Multihop evaluator public modes（`normal` / `enhanced` / `auto`）：12 passed；
- Python compile：`python -m compileall -q src/backend/zuno tests`；
- docs/repository verifiers：docs entrypoints、doc boundaries、repo hygiene、repo
  structure、tool bypass guard。

必须持续保留的行为覆盖：文件 hash / tenant boundary、durable ingestion handoff、
Run submit、restart recovery、Security fail-closed、approval binding、cancel
幂等、artifact authorization、event streaming、retrieval observability、tenant
isolation、persistence failure stop、duplicate command idempotency 和未知外部效果
reconciliation。

旧 phase-named 测试不再作为当前架构验收入口；行为被删除前必须有对应的 canonical
behavior test。测试通过不等于 Production Readiness 已证明。
