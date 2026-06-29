# Workflow Governance

## When To Use

当任务涉及 Agent 工作方式、长期规则、文档维护规则、模板、program 生命周期、Codex 多线程/多 agent 执行方式或用户纠正规则时，使用本文件。

## Mental Model

```text
AGENTS.md
  -> boot entry and route map
.agent/references/
  -> Agent operating memory
.agent/templates/
  -> generation contracts
.agent/programs/
  -> execution state
docs/architecture/
  -> human-facing architecture source
docs/architecture.html
  -> presentation page
README.md
  -> project entry summary
```

## Current Truth

AGENTS.md 和 `.agent/references/` 共同组成 Zuno 的 Agent 工作流系统。它不是静态规则；当用户长期要求变化时，工作流必须自我维护。

当前工作流包括：

- Agent 工作流文档系统：`AGENTS.md`、`.agent/references/*`、`.agent/templates/*`、`.agent/programs/*`。
- 元工作流自我维护系统：`workflow-governance.md`、`workflow-update-policy.md`、`workflow-requirements.md`、`workflow-change-log.md`、`workflow-maintenance-checklist.md`。
- 正式架构文档系统：`docs/architecture/*`。
- 架构 HTML 展示系统：`docs/architecture.html`。
- 代码和目录清理系统：`src/backend/zuno`、`tools/`、`tests/`、verifier 和 repo hygiene rules。

## Target Direction

最终成品对外讲五个成熟系统；内部验收拆成八大交付物。五个系统让面试/展示不乱，八大交付物让工程验收不漏。

## Must Preserve

- AGENTS.md 保持入口和路由，不承载所有细节。
- `.agent/references` 保存长期规则和可复用 operating memory。
- `.agent/templates` 保存输出骨架；如果新规则影响未来生成内容，必须更新模板。
- `.agent/programs` 保存当前状态；完成或替换的 program 进入 `docs/history/programs/`。
- 工作流变更要写入 `workflow-change-log.md`。

## Before Editing

1. 判断用户要求是一次性指令还是长期规则。
2. 判断它影响哪个系统：workflow、architecture docs、HTML、templates、programs、code/verifier。
3. 查 `workflow-update-policy.md` 选择更新目标。
4. 查 `workflow-maintenance-checklist.md` 做收口。

## Allowed Changes

- 新增长期规则、更新规则路由、修正模板边界、补充 change log。
- 同步 verifier 和 tests，使规则可检查。

## Forbidden Changes

- 不要把对话里的“以后注意”只留在最终回复。
- 不要把临时任务偏好写成永久全仓规则。
- 不要让 `.agent/references` 和 AGENTS.md 表达冲突。

## Common Failure Patterns

- 更新了 workflow requirements，但没有更新 templates。
- 更新了 AGENTS.md，但没有更新 reference 细则。
- 新增了 reference 文件，但 system.yaml 和 tests 不知道它。

## Debug Playbooks

- 规则太长：AGENTS.md 只留入口，细节放 references。
- 规则冲突：以用户最新长期要求为准，更新旧规则并记录原因。
- 规则难检查：把关键词、路径或文件集合写入 verifier/test。

## Focused Tests

```powershell
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

## Docs Sync

修改本文件时检查：

- `AGENTS.md`
- `.agent/references/workflow-update-policy.md`
- `.agent/references/workflow-requirements.md`
- `.agent/references/workflow-maintenance-checklist.md`
- `.agent/system.yaml`

## Lessons Learned

工作流本身也是项目资产。它要能跟着用户长期要求演化，而不是每轮靠记忆临场发挥。
