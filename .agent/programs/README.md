# Agent 执行计划

`.agent/programs/` 只保存当前执行状态，不保存历史施工计划、closure checklist
或旧 thread prompt。

当前状态：`active-design-program`。

入口：

- `current.md`
- `current.md`：当前架构重构/审查 Program 的状态、范围和退出条件。
- `queued-programs/`：当前为空；实现 Program 仍须在架构评审和用户 Gate 后另行生成。

当前 Program：`PROJECT-ARCHITECTURE-RECONSTRUCTION-V1`。

它是设计/审查 Program，不是 Runtime implementation Program；不得因为它处于 active
就把 Target、Hypothesis 或 Gap 写成 Current。
