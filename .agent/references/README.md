# Zuno Local Skills

`.agent/references/` 是 Zuno 的本地项目 skill library。它不只是目录索引，而是沉淀“在 Zuno 里怎么正确做事”的 skills、lessons、playbooks、失败模式、测试选择和文档同步规则。

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
- `task-routing.md`：任务类型到 skill 和流程的路由表。
- `workflow.md`：通用执行流程、文档维护流程、仓库卫生流程和验证基线。
- `code-map.md`：当前代码 owners 和受保护 runtime 边界。
- `runtime-call-chain.md`：当前后端调用路径。
- `verification-map.md`：verifier、pytest、grep 和 closure 命令地图。
- `command-catalog.md`：常用命令片段。
- `known-pitfalls.md`：常见错误、禁止恢复的旧路径和可复用失败模式。

## Skill 文件标准

后续新增或重写的 `.agent/references/*.md` 如果承载本地 skill，应使用这个结构：

```text
When To Use
Mental Model
Current Truth
Target Direction
Must Preserve
Before Editing
Allowed Changes
Forbidden Changes
Common Failure Patterns
Debug Playbooks
Focused Tests
Docs Sync
Lessons Learned
```

一次性调查证据归档到 `docs/history/` 或外部结果目录，不写进 skill。

## 归档

旧详细 map 归档在：

- `docs/history/agent-reference-fragments/`

未来需要历史细节时，只把最小当前事实提升回 active reference。
