# Architecture Consolidation Workflow

status: working-material
canonical_boundary: `docs/architecture/architecture.md` is the only current cross-layer architecture surface; this Lab file is not a Canonical Architecture document.

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

`PROJECT-ARCHITECTURE-RECONSTRUCTION-V1` 当前停在 `Fact Depth Recovery + Product/Architecture
Reconstruction`。Canonical Facts 分类已经足够，不以增加更多 Facts 文件作为前置条件。

## 双轨回流

```text
Track A: 事实恢复
  → 真实问题、Ownership、QA、Incident、协作、复用证据

Track B: 架构重构
  → Product、Domain、Runtime、Knowledge、Service、Data、Security、Eval

Red/Blue 或 Interview 发现无法解释的事实
  ↘ 回到 Track A

事实恢复出新的真实约束
  ↘ 重新攻击 Track B
```

## 进入下一阶段的闸门

### Fact Readiness Gate

以下主链可解释即可开始架构，不要求关闭所有 `UNKNOWN`：

```text
为什么做 → 谁在用 → 团队怎么做 → 我做了什么 → 请求怎么跑
→ 真实问题 → 修改 → 验证 → 客户反馈 → 架构为何演进
```

### Architecture Complexity Gate

保留任何复杂度前，必须回答：

```text
Problem / Evidence / Alternative / Owner / State
Failure / Retry / Recovery / Idempotency
Security / Observability / Test / Replacement / Reversal
```

`ACCEPTED_TARGET` 不跳过 Red/Blue；`SURVIVED` 只有在 Counter Attack 后才能使用。
`A-P0` 阻塞 User Gate；`I/E/X-P0` 分别阻塞实现完成、测量和外部资格，不自动阻塞对已
设计清楚 Target 的用户审阅。完整规则见 `docs/governance/architecture-gate-policy.md`。

## Canonical Sync Rules

- Domain、Runtime、Service 和 Data 的跨层 Owner 统一进入 `docs/architecture/architecture.md`；状态与证据分别进入 `docs/facts/` 和 `docs/evidence/`。
- Security、Eval、Deployment 分别进入对应专题。
- Lab 只保留攻击、证据、候选和迁移记录。

## Reversal Criteria

如果 Benchmark、Spike 或实际部署证明复杂度无收益，必须回写 `DEFERRED` 或 `REJECTED`，并更新 ADR 的 reversal criteria；不能为了保持架构漂亮而保留。
