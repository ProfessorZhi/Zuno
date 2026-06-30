# Project Map

## When To Use

当任务涉及仓库入口、目录职责、文档归属、Agent 工作入口、架构展示页或当前 program 状态时，先读本文件。它回答“Zuno 的东西应该放在哪里”，不替代代码阅读。

## Mental Model

```text
AGENTS.md
  -> boot entry and routing contract
.agent/references/
  -> Agent-facing operating memory
.agent/templates/
  -> generation contracts
.agent/programs/
  -> current execution state and program lifecycle
docs/architecture/
  -> human-facing architecture source
docs/architecture/architecture.html
  -> generated presentation page
src/backend/zuno/
  -> backend runtime code
apps/
  -> frontend and desktop applications
tools/ and tests/
  -> verification, migration, eval and automation support
```

## Current Truth

- `AGENTS.md` 是仓库唯一 Agent 入口。
- `.agent/references/` 是当前唯一 Agent operating memory 目录；不要新增 `.agent/reference/` 单数目录。
- `.agent/programs/` 是当前执行计划和状态入口；仓库当前不启用 `.agent/plans/`。
- `docs/architecture/` 是正式架构文档源。
- `docs/architecture/architecture.html`、`docs/architecture/architecture.html`、`docs/architecture/architecture.html` 由 `tools/agent/render_architecture.py` 从 `docs/architecture/architecture.md` 生成。
- `src/backend/zuno` 当前顶层只保留 `api / agent / memory / capability / knowledge / platform` 加 `__init__.py` 和 `main.py`。
- `docs/` 应少而精，保留稳定的人类正式结论；`.agent/` 保留更细、更常变化的 Agent 操作记忆、计划、模板和治理细则。

## Target Direction

Zuno 最终按五个成熟系统对外表达：

1. Agent 工作流文档系统。
2. 元工作流自我维护系统。
3. 正式架构文档系统。
4. 架构 HTML 展示系统。
5. 干净清晰且可验证的代码结构。

内部验收拆成八大交付物：

1. Agent 工作流文档系统。
2. 元工作流自我维护系统。
3. 模板与执行计划系统。
4. 正式架构文档系统。
5. 架构 HTML 展示系统。
6. 完善的 Zuno 目标架构。
7. 清晰干净的代码和目录。
8. 一致性与验证系统。

## Must Preserve

- 文档和代码结论不能互相打架。
- `docs/` 和 `.agent/` 不能重复展开同一批高频变化细节。
- Current 必须由代码、测试、trace、eval 或可复现结果支撑。
- Target 和 Future 不能冒充 Current。
- 展示页不是唯一事实来源，必须能回到 `docs/architecture/`。
- Agent workflow 规则不能只留在对话里。

## Before Editing

1. 查 `git status --short --branch`，保护用户未提交改动。
2. 读 `AGENTS.md`、`.agent/system.yaml`、`.agent/references/task-routing.md`。
3. 架构或文档任务继续读 `.agent/references/architecture-docs-map.md`、`documentation-governance.md`、`architecture-update-policy.md`。
4. 工作流规则变更继续读 `.agent/references/workflow-governance.md`、`workflow-update-policy.md`、`workflow-maintenance-checklist.md`。
5. 代码任务读 `.agent/references/code-map.md` 和对应模块规则。

## Allowed Changes

- 追加或修正文档职责、同步规则、验证规则和项目地图。
- 在用户明确要求时更新模板和 verifier。
- 在正式 program 打开前，只把未来实现计划写成 queued draft / not active。

## Forbidden Changes

- 不要新增 `.agent/reference/` 单数目录。
- 不要把 `.agent/plans/` 写成当前已启用入口。
- 不要把未实现目标架构写成 Current。
- 不要为整理目录顺手改业务 runtime 行为。

## Common Failure Patterns

- 只改 HTML，不改 `docs/architecture`。
- 只改 `.agent/references`，没有把人类可读结论写入 `docs/architecture`。
- 新增长期规则但没更新模板和 verifier。
- 把多 agent 执行工作流误写成 Zuno runtime 当前架构。

## Debug Playbooks

- 找不到文档归属：先查本文件，再查 `architecture-docs-map.md`。
- 不知道是否要更新架构图：查 `diagram-inventory.md`。
- 不知道用户新要求是否长期规则：查 `workflow-update-policy.md` 和 `workflow-maintenance-checklist.md`。

## Focused Tests

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```

## Docs Sync

修改本文件时检查：

- `AGENTS.md`
- `.agent/system.yaml`
- `.agent/references/README.md`
- `.agent/references/docs-map.md`
- `.agent/references/workflow-governance.md`
- `docs/architecture/README.md`

## Lessons Learned

项目地图的价值不是列目录，而是让下一次 Agent 少猜一个归属判断。
