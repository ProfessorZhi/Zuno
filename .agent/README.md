# Agent Workspace

这个目录承载仓库内 Agent 工作流材料。

## 边界

- `docs/`：给人看的正式文档
- `.agent/`：给 Agent 看的工作流材料
- `agent.md`：Agent 进入仓库的总入口

## 目录

```text
.agent/
  README.md
  references/
  scripts/
  notes/
  templates/
```

## 用法

- `references/`：放给 Agent 快速读取的参考索引
- `scripts/`：放辅助脚本
- `notes/`：放分析和排查记录
- `templates/`：放常用执行模板

正式架构文档统一放：

- `docs/architecture/`

这里不保存正式架构结论，只保存：

- 导航索引
- 本地脚本
- 临时记录
- Agent 工作模板

## 工作流约定

- 允许 Codex 在开发过程中开启多 Agent 模式
- 允许使用目标模式持续追踪任务
- 文档里的验收点可以直接转成目标
- `spec coding` 任务默认追求“验收达成”，不是“分析结束”

## 工作流硬规则

- 复杂开发任务可以直接进入多 Agent 模式
- 需要验收收口的任务应进入目标模式
- 目标优先来源于正式文档中的验收点
- 目标未达成，不视为任务完成
