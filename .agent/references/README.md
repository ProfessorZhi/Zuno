# Agent 参考索引

`.agent/references/` 是 Agent 的精简导航层。它指向 source-of-truth 文件和命令，不承载长篇目标架构设计。

## 当前文件

```text
.agent/references/
  README.md
  current-program.md
  docs-map.md
  task-routing.md
  workflow.md
  code-map.md
  runtime-call-chain.md
  verification-map.md
  command-catalog.md
  known-pitfalls.md
```

## 用途

- `current-program.md`：当前可执行 Agent program。
- `docs-map.md`：正式 docs、history 和 Agent 工作流入口。
- `task-routing.md`：任务类型到参考和流程的路由表。
- `workflow.md`：通用执行流程、文档维护流程、仓库卫生流程和验证基线。
- `code-map.md`：当前代码 owners 和受保护 runtime 边界。
- `runtime-call-chain.md`：当前后端调用路径。
- `verification-map.md`：verifier、pytest、grep 和 closure 命令地图。
- `command-catalog.md`：常用命令片段。
- `known-pitfalls.md`：常见错误和禁止恢复的旧路径。

## 归档

旧详细 map 归档在：

- `docs/history/agent-reference-fragments/`

未来需要历史细节时，只把最小当前事实提升回 active reference。
