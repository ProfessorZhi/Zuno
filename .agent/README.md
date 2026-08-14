# Zuno Local Agent System

`.agent/` 只保存 Agent 如何在 Zuno 中正确工作的路由、规则、Program、模板和验证入口；不保存项目故事、架构正文或模块镜像。

## 先读什么

先读根目录 `AGENTS.md`，再读 `docs/README.md` 和与任务相关的 `docs/project/`、`docs/architecture/`、`docs/evidence/`、ADR 或 `docs/history/red-blue/` 指定记录。机器可读路由见 `system.yaml`。

## 目录

```text
.agent/
├── README.md
├── system.yaml
├── references/       路由、工作流、代码地图、验证地图和已知坑
├── programs/         当前 active / queued 执行状态
├── templates/        通用任务模板
└── scripts/          Agent 与文档边界验证器
```

Red / Blue 不是当前 Agent 的默认上下文。只有任务明确要求复盘架构演进或历史攻击时，才读取 `docs/history/red-blue/` 的相关 Round。它们不是 Canonical Architecture，也不会自动授权实现。

修改任务必须先确认工作树和用户未提交文件，完成后运行 focused validation、Commit 和 Push。不要把一次性聊天、旧施工材料或目标方案复制为新的 `.agent` 事实源。
