# Local Agent Workflow

这个文件只服务本地开发 Agent 工作流，不属于仓库正式文档，不上传 GitHub。

## 文档边界

- `docs/`：给人看的正式文档系统
- `.agent/`：给 Agent 看的本地工作流系统
- `.agentmd`：Agent 进入仓库时的总入口，负责告诉 Agent 先看什么、怎么连接 `.agent/` 和 `docs/`

## 目标

为本地开发 Agent 提供统一入口：

- 先看哪里
- 先用什么参考
- 遇到什么任务走什么路径
- 哪些本地脚本和材料在 `.agent/`

## Spec Coding 约定

这个仓库的本地 Agent 开发流程允许并鼓励使用 `spec coding`：

- 可以开启多 Agent 模式
- 可以使用目标模式
- 可以把文档里的验收点直接作为目标
- 目标未达成前，不应主动停止在“只分析不落地”的状态

这里的核心规则是：

```text
先用文档明确目标和验收标准，
再把目标转成执行过程中的真实约束，
直到验收点达成为止。
```

## 工作流硬规则

1. 开发任务允许开启多 Agent 模式。
2. 复杂任务优先考虑目标模式，不只停留在普通对话推进。
3. 文档里的验收点可以直接提升为目标。
4. 目标未达成前，不把任务标记为完成。
5. 目标模式下，停止条件不是“解释完了”，而是“验收点满足了”。

## 优先参考

### 人类正式文档入口

- `docs/architecture/README.md`
- `docs/architecture/zuno_refactor_plan.md`
- `docs/architecture/specs/`
- `docs/architecture/plans/`
- `docs/architecture/decisions/`

### 人类工程文档入口

- `README.md`
- `docs/reference/`
- `docs/development/`
- `infra/docker/`
- `launchers/`
- `tools/`

### 历史正式设计资料

- `docs/superpowers/README.md`
- `docs/superpowers/specs/`
- `docs/superpowers/plans/`

说明：

- `docs/architecture/` 是当前和未来的人类架构主入口。
- `docs/superpowers/` 视为历史正式设计资产，后续能迁则迁，不能迁也要在新文档里引用。
- `.agent/` 不重复承载正式结论，只做 Agent 导航、索引、脚本和临时工作流。
- Agent 默认先读 `docs/architecture/`，只有需要历史背景时再读 `docs/superpowers/`。

## 默认工作流

### 做架构或重构前

1. 先看 `.agent/references/`
2. 再通过 `.agent/` 的索引跳到 `docs/architecture/README.md`
3. 再看当前总方案和相关 `ADR`
4. 再确认代码里现有实现，不凭文档想象重做

### 做 spec coding 任务前

1. 先确认是否已有 `spec / plan / decision / README` 可作为目标来源
2. 把文档里的验收点提炼成目标
3. 如果任务复杂，允许开启多 Agent 模式拆分子问题
4. 如果需要持续推进，优先使用目标模式跟踪是否真正达成
5. 直到目标满足前，不把“分析完成”当作任务完成

### 做 spec coding 任务时

1. 每个主要动作都应能对应到某个目标或验收点
2. 如果发现验收点不清楚，先补清楚目标来源再继续开发
3. 如果单线程推进效率低，允许切换到多 Agent 模式并行处理
4. 如果已经进入目标模式，就持续对照目标检查偏差
5. 任何“先停在这里”都必须以目标已达成为前提

### 做实现前

1. 先确认任务属于哪条主线
2. 先读 `.agent/references/` 中对应索引
3. 再跳转到 `docs/` 下正式文档
4. 再决定是补丁式改动还是结构性改动

### 做评估或验证前

1. 优先找 `tests/`
2. 再找 `src/backend/zuno/evals/`
3. 必要时用 `.agent/scripts/` 下的本地脚本辅助

## 主线分类

### 架构主线

- LangGraph runtime
- GraphRAG
- Domain Pack
- retrieval / orchestration
- future multi-agent

### 工程主线

- Docker / launcher
- backend config
- frontend workspace
- tests / evals

## `.agent/` 约定

- `.agent/references/`：给开发 Agent 的本地参考索引
- `.agent/scripts/`：本地辅助脚本，不进入仓库
- `.agent/notes/`：临时分析、排查、执行记录
- `.agent/templates/`：可复用的本地提示模板、执行模板

## 注意事项

- `.agentmd` 和 `.agent/` 都是本地工作流资产，不上传 GitHub。
- `docs/` 是给人看的正式文档，不要把 Agent 私有流程塞进去。
- `.agent/` 是给 Agent 看的操作层材料，不要把正式架构结论只留在这里。
- 架构相关正式结论要写进 `docs/architecture/`。
- `.agent/` 负责“Agent 怎么工作”，`docs/` 负责“人怎么理解系统与决策”。
- 允许 Codex 在开发过程中开启多 Agent 模式。
- 允许使用目标模式把验收点作为持续目标，不达成不停止。
- 以上两点属于工作流规则，不是可有可无的建议。
