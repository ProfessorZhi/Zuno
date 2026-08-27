# Zuno Local Agent System

`.agent/` 只保存 Agent 如何在 Zuno 中正确工作的**机器路由、规则、Program、Red / Blue Harness、模板和验证入口**；不保存项目故事、研究正文、架构正文或模块镜像。

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
├── programs/         一般 implementation / design Program 状态
├── red-blue/         Interview / Architecture Stress-Test 专用运行中心
├── templates/        通用任务模板
└── scripts/          Agent 与文档边界验证器
```

`docs/maintenance/agent-workflow/` 是给人看的通用 ChatGPT / Claude Code / GitHub 协作说明；`docs/maintenance/red-blue/` 是给人看的 Red / Blue Interview Harness 工作流。二者都不能复制或覆盖 `.agent/system.yaml`。

## Red / Blue

Red / Blue 不再借用 `.agent/programs/` 作为运行态工作空间。专用入口是：

```text
.agent/red-blue/                         Machine harness / active Round state
docs/maintenance/red-blue/              Human workflow
docs/maintenance/history/red-blue/      Closed Round history
```

只有用户明确启动 Red / Blue 时才切换 `.agent/red-blue/current.md`；`main` 默认保持 `no-active`。Red 可以读取批准的真实面试 / 研究资料校准 interviewer pressure，Blue 只使用固定简历快照和允许的 Zuno canonical docs，尤其优先从 Part A 组织回答。历史 Round、面经题库和 Red hidden intent 不进入 Blue 上下文。

修改任务必须先确认目标 SHA 和任务范围，完成后运行 focused validation、Commit 和 Push。不要把一次性聊天、Research Snapshot、旧施工材料、历史 Round 或 Target 方案复制为新的 `.agent` 事实源。