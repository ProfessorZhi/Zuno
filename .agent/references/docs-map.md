# 文档同步 Skill

## When To Use

当任务触碰 `docs/`、`.agent/`、`AGENTS.md`、history、README、架构叙事或术语边界时使用本 skill。

## Mental Model

```text
docs/ = formal human truth
.agent/references/ = local skills and lessons
.agent/templates/ = execution skeletons
.agent/programs/ = active execution plan
.agent/architecture/ = target design workspace
docs/history/ = archive and evidence
```

## Current Truth

正式人类入口：

- `README.md`：仓库总览和首读路径。
- `docs/README.md`：文档入口。
- `docs/architecture/architecture.md`：总架构文档，文字说明当前事实、目标分层、主链路和实施落点。
- `docs/architecture/architecture.md`：当前仓库事实。
- `docs/architecture/architecture.md`：近期目标摘要。
- `docs/architecture/architecture.md`：当前状态和下一步。
- `docs/evidence/public-demo.md`：精选公开证据入口。
- `docs/evidence/eval-baselines.md`：Eval baseline 状态。
- `docs/reference/terminology.md`：公共术语表。
- `docs/architecture/decisions/`：仍然有效的正式 ADR。
- `docs/history/`：历史档案。

Agent 工作流入口：

- `AGENTS.md`：仓库级 Agent bootloader。
- `.agent/README.md`：Zuno Local Agent Skill System 说明。
- `.agent/system.yaml`：路径到 skills、templates、docs_sync、verify 的路由。
- `.agent/references/`：本地项目 skills、lessons、playbooks。
- `.agent/templates/`：执行骨架。
- `.agent/programs/`：当前执行入口；有 active program 时放平铺 phase，当前也可以处于无 active 的等待状态。
- `.agent/architecture/architecture.md`：Agent 侧总架构维护文档，必须和正式总架构文档一致。
- `docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/near-term/`：近期目标架构详细设计。
- `.agent/scripts/`：过渡期验证器。

## Target Direction

前台保持小而清楚：正式结论进入 `docs/`，可执行项目知识进入 `.agent/references/`，旧材料进入 `docs/history/`。不要用更多前台目录解决叙事不清。

## Must Preserve

- Current 只描述代码和测试已证明事实。
- Target 只描述近期目标，不等于完成声明。
- History 保留旧材料原文，不为了新叙事改写证据。
- `.agent/architecture/architecture.md` 是 Target / Proposed 视觉蓝图，不是 Current truth。

## Before Editing

1. 读 `docs/architecture/README.md`、`current-architecture.md`、`target-architecture.md`、`roadmap.md`。
2. 架构任务先读 `docs/architecture/architecture.md` 和 `.agent/architecture/architecture.md`。
3. 读 `.agent/README.md`、`.agent/system.yaml`、`task-routing.md`、`workflow.md`。
4. 判断修改属于 Current、Target、Program、Skill、Template、History 哪一类。
5. 搜索同一术语的前台命中，避免只改一个入口。

## Allowed Changes

- 同步 docs entrypoints、`.agent` maps、verifier/test 的路径和术语。
- 将完成或被替换材料归档到 `docs/history/`。
- 精简前台说明，保留决策所需信息。

## Forbidden Changes

- 不把一次性调查流水账写进 `docs/` 或 `.agent/references/`。
- 不把模板改成项目知识库。
- 不把 history 文件重写为当前事实。
- 不恢复 `docs/architecture/phases/`、`docs/architecture/plans/`、`docs/architecture/programs/` 当前前台目录。

## Common Failure Patterns

- `docs/architecture/architecture.md` 已更新，但 `.agent/references/current-program.md` 仍旧。
- `AGENTS.md` 路由变了，但 `.agent/system.yaml` 未同步。
- references skill 改了，但 `.agent/templates/README.md` 仍暗示模板保存项目知识。
- HTML 蓝图被引用成 Current proof。

## Debug Playbooks

- Current/Target 冲突：以 runtime code、tests、trace evidence 决定 Current；未证明内容保留 Target。
- 路径漂移：用 `git grep -n "<path-or-term>"` 找前台命中，历史目录只在必要时保留原文。
- 归档不清：先建或使用 `docs/history/` 下明确目录，再更新入口和 verifier。

## Architecture Documentation Governance

架构文档和展示页的专门索引已经拆到：

- `.agent/references/architecture-docs-map.md`
- `.agent/references/documentation-governance.md`
- `.agent/references/architecture-update-policy.md`
- `.agent/references/diagram-inventory.md`
- `.agent/references/current-target-future-rules.md`

这些文件说明 `docs/architecture/`、`docs/architecture/architecture.html`、`.agent/references/`、`.agent/templates/` 和 `.agent/programs/` 如何同步。涉及 architecture.html 或十类 Mermaid 架构视图时，不要只读本 docs map。

## Agent Workflow Self-Maintenance

工作流自我维护规则已经拆到：

- `.agent/references/workflow-governance.md`
- `.agent/references/workflow-update-policy.md`
- `.agent/references/workflow-requirements.md`
- `.agent/references/workflow-change-log.md`
- `.agent/references/workflow-maintenance-checklist.md`

当用户提出新的长期工作方式要求时，先用这些文件判断是否需要更新 AGENTS.md、`.agent/references/`、`.agent/templates/`、`.agent/programs/`、`docs/architecture/`、`docs/architecture/architecture.html`、verifier 或 tests。

## Focused Tests

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Docs Sync

修改文档边界时检查：

- `AGENTS.md`
- `.agent/README.md`
- `.agent/system.yaml`
- `.agent/references/current-program.md`
- `.agent/references/task-routing.md`
- `.agent/references/workflow.md`
- `.agent/references/verification-map.md`
- `.agent/templates/README.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `.agent/architecture/architecture.md`
- `docs/history/README.md`

## Lessons Learned

文档同步的本质不是“所有地方都写一遍”，而是每个 surface 只承载自己的真相层级，并且入口之间不互相矛盾。
