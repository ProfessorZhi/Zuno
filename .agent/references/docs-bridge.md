# Docs Bridge

## 目的

这个文件告诉 Agent：

- `docs/` 是给人看的正式文档系统
- `.agent/` 是给 Agent 看的工作流系统
- Agent 可以通过这里跳到正式文档，但不要把两者混成一个目录体系

## 读取顺序

1. 先看 `agent.md`
2. 再看 `.agent/references/`
3. 再跳到 `docs/architecture/`
4. 需要工程信息时再看 `docs/reference/` 和 `docs/development/`

## 正式文档入口

- `docs/architecture/README.md`
- `docs/architecture/zuno_refactor_plan.md`
- `docs/reference/`
- `docs/development/`

## 规则

- 正式结论写回 `docs/`
- Agent 私有流程留在 `.agent/`
- `.agent/` 可以引用 `docs/`，但不替代 `docs/`
