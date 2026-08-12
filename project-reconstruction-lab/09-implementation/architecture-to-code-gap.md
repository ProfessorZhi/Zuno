# Architecture-to-Code Gap

## Canonical Question

Survived Target 与当前代码、进程、数据和测试之间还差什么？

## Gap Template

```text
Gap ID：
Current：代码/迁移/运行证据
Target：Canonical Doc / ADR
Why：解决什么事实或风险
Risk：
Migration：Expand / Migrate / Verify / Contract
Dependencies：
State Transition：
Error / Retry / Recovery：
Idempotency：
Security：
Observability：
Tests：
Rollback：
Evidence Required：
```

## 初始 Gap

| Gap | Current | Target | Evidence Needed |
|---|---|---|---|
| Domain Kernel | 通用代码表面，法律闭环未证明 | Legal Domain Owner | schema/mutation/review/staleness E2E |
| Runtime Boundary | Agent control surface 存在 | Domain State 与 Runtime State 分离 | reconciliation trace |
| Service Boundary | 当前包/Compose 表面 | 少量独立服务 | workload/failure/security evidence |
| Knowledge | Graph/RAG 表面 | Conditional Evidence Retrieval | A/B/C benchmark |
| Historical OpenViking | Current 未发现 | 历史 Memory/Context 接入 | old artifact |
