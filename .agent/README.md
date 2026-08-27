# Zuno Local Agent System

`.agent/` 只保存 Agent 如何在 Zuno 中正确工作的**机器路由、规则、Program、模板和验证入口**；不保存项目故事、研究正文、架构正文或模块镜像。

## 先读什么

先读根目录 `AGENTS.md`，再读 `docs/README.md`。项目/架构任务按需进入：

- `docs/project/`：真实项目故事；
- `docs/research/`：研究谱系、平台 baseline、Research→Engineering；
- `docs/architecture/` / `docs/modules/`：Target 设计；
- `docs/evidence/`：Current Evidence；
- `docs/decisions/`：长期 ADR；
- `docs/maintenance/history/red-blue/`：需要复盘历史审查时再读。

机器可读路由见 `system.yaml`。

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

`docs/maintenance/agent-workflow/` 是给人看的 ChatGPT / Claude Code / GitHub 协作说明；它不能复制或覆盖 `.agent/system.yaml`。

Red / Blue 不是当前 Agent 的默认上下文。只有任务明确要求复盘架构演进或历史攻击时，才读取 `docs/maintenance/history/red-blue/` 的相关 Round。它们不是 Canonical Architecture，也不会自动授权实现。

修改任务必须先确认目标 SHA 和任务范围，完成后运行 focused validation、Commit 和 Push。不要把一次性聊天、Research Snapshot、旧施工材料或 Target 方案复制为新的 `.agent` 事实源。
