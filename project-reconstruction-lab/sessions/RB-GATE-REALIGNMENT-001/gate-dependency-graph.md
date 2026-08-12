# Gate Dependency Graph

## 已证实的死锁

旧规则同时存在以下边：

```text
Final P0 = 0
  → User Architecture Gate
  → Canonical Target Sync
  → Implementation Task
  → Current implementation
  → V4 closure-grade evidence
  → Red ACCEPT_EVIDENCE
  → Counter Retest PASS
  → Final P0 = 0
```

对 Q005、Q053、Q061、Q097，V4 记录明确写出当前没有对应实现；因此这四项至少需要先
产生实现级证据才能进入原来的闭环。若 Implementation Task 又被 `Final P0 = 0` 约束，
就形成：

```text
没有实现 → 没有 Closure Evidence → P0 不能关闭
       → 不能过 Architecture Gate → 不能生成 Implementation Task
       → 永远没有实现
```

这是 Governance Deadlock，不是一次测试失败，也不是理由把 P0 改成 P1。

## 修正后的无环路径

```text
Fact / Product Baseline
  → Red Attack
  → Blue Repair
  → Design Counter Attack
  → Closure Class
  → A-P0 Burn-down
  → User Architecture Gate
  → Canonical Target Sync
  → Active Implementation Program
  → V4 Evidence
  → Red Evidence Review
  → Counter Retest
  → I-P0 Closure
  → V5 Benchmark
  → E-P0 Closure
  → External Qualification
  → X-P0 Closure
```

其中 `I/E/X` 在 User Gate 后继续作为并行风险轨道，不能倒过来阻止“接受一个尚未实现
但已设计清楚的 Target”。

## Gate 语义分离

| Gate | 它批准什么 | 它不批准什么 |
|---|---|---|
| Closure Class | 判断 P0 阻塞 Architecture、Implementation、Measurement 还是 External Qualification | 不改变 Severity，不关闭 P0 |
| User Architecture Gate | 用户接受已设计清楚的方案作为下一阶段 Target | 不证明实现、质量、安全或生产 |
| Canonical Sync | 将用户批准的 Target 写入正式 Owner 文档 | 不把 Target 变成 Current |
| Implementation Gate | 允许创建并执行有边界的 implementation Program | 不关闭 I-P0 |
| Red Evidence Review | 判断证据是否达到声明范围 | 不替代 Counter Retest |
| Counter Retest | 在变异条件下复测已接受的 Evidence | 不替代 V5 或外部资格测试 |
| Measurement Gate | 允许 `MEASURED`/质量声明 | 不替代生产资格 |
| External Qualification Gate | 允许安全/部署/Provider 资格声明 | 不等于质量优于竞品 |

## 不变量

1. 原始 P0 数量仍为 12，Q039 的派生记录必须回链原始 Q039。
2. `A-P0 = 0` 是 User Architecture Gate 的硬条件。
3. I-P0 必须有 Target Contract 和 Implementation Task Candidate，但 I-P0 仍为 OPEN。
4. E-P0 必须有 Benchmark/Eval Plan，但不能因此成为 `MEASURED`。
5. X-P0 必须有 Qualification Plan，但不能因此成为 `SECURITY_QUALIFIED` 或生产证明。
6. 用户 Gate 必须由用户明确记录 `APPROVE`、`REJECT` 或 `REQUEST_REVISION`；模型不得代签。
   本次用户已经明确 `APPROVE`，批准范围仅为 `ACCEPTED_TARGET`。
