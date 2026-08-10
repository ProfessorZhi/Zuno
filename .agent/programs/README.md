# Agent 执行计划

`.agent/programs/` 只保存当前执行状态，不保存历史施工计划、closure checklist
或旧 thread prompt。

当前状态：`no-active`。

入口：

- `current.md`
- `queued-programs/`：当前为空；新的 Program 只能在架构评审后生成。
