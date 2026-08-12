# Migration Strategy

Target 进入代码时使用：

```text
Expand
  → Migrate
  → Verify
  → Contract
```

## Rules

- 先冻结 Contract，再迁移实现。
- Domain State 与 Runtime Control State 分开迁移。
- 物理服务拆分后保留可回滚路径。
- Queue 不是业务事实源。
- DB schema、公开 API、依赖和安全边界变化属于 Stop Condition。
- 没有用户明确激活，不创建新的 implementation Program。

每个迁移任务必须绑定 Canonical Doc、ADR、测试和 Evidence。
