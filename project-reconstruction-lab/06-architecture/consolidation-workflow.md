# Architecture Consolidation Workflow

## Gate

```text
Facts stable enough
→ Product thesis explicit
→ Candidate registered
→ Red Attack
→ Blue Response
→ Counter Attack
→ KEEP / SIMPLIFY / EXTERNALIZE / DEFER / DELETE
→ ADR candidate
→ User architecture gate
→ Canonical Docs
```

## Canonical Sync Rules

- Domain fact Owner 进入 `docs/project/domain/`。
- Runtime control Owner 进入 `docs/project/agents/`。
- Service boundary 进入 `docs/project/services/`。
- Data/recovery 进入 `docs/project/data/`。
- Security、Eval、Deployment 分别进入对应专题。
- Lab 只保留攻击、证据、候选和迁移记录。

## Reversal Criteria

如果 Benchmark、Spike 或实际部署证明复杂度无收益，必须回写 `DEFERRED` 或 `REJECTED`，并更新 ADR 的 reversal criteria；不能为了保持架构漂亮而保留。
