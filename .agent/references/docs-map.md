# 文档同步 Skill

## When To Use

当任务触碰 `docs/`、`.agent/`、AGENTS.md、history、README、架构叙事或术语边界时使用本 skill。

## Mental Model

```text
docs/architecture/ = four canonical architecture files
docs/modules/ = formal logical module designs
docs/status/ = current and readiness truth
docs/decisions/ = ADR
docs/governance/ = ownership and documentation governance
docs/evidence/ = reproducible evidence
docs/history/ = archive
.agent/architecture/ = four generated architecture mirrors
.agent/modules/ = selected module design mirrors
.agent/references/ = local skills and lessons
.agent/templates/ = execution skeletons
.agent/programs/ = active execution plan
```

## Current Truth

正式人类入口：

- `README.md`：仓库总览和首读路径。
- `docs/README.md`：文档总入口。
- `docs/architecture/README.md`：总架构目录规则。
- `docs/architecture/architecture.md`：Lean Complete Agentic GraphRAG Product 的重文字目标总架构。
- `docs/architecture/architecture-views.md`：十类 canonical views 的 Mermaid 规范图源。
- `docs/architecture/architecture.html`：读取图源的 Architecture Atlas。
- `docs/modules/README.md`：十一个逻辑模块入口。
- `docs/modules/06-agent-core-planning-control.md`：Agent Core V2 实施级设计。
- `docs/status/production-readiness.md`：Current、Gap、Measurement Blocked、Completed、Future Optional。
- `docs/decisions/README.md`：正式 ADR 入口。
- `docs/governance/repo-ownership-matrix.md`：代码目录 ownership 与迁移边界。
- `docs/evidence/public-demo.md`：精选公开证据入口。
- `docs/history/`：历史档案。

Agent 工作流入口：

- `AGENTS.md`：仓库级 Agent bootloader。
- `.agent/README.md`：Zuno Local Agent Skill System 说明。
- `.agent/system.yaml`：路径到 skills、templates、docs_sync、verify 的路由。
- `.agent/references/`：本地项目 skills、lessons、playbooks。
- `.agent/templates/`：执行骨架。
- `.agent/programs/`：当前执行入口。
- `.agent/architecture/architecture.md`：正式总架构文字镜像。
- `.agent/architecture/architecture-views.md`：正式 Mermaid 图源镜像。
- `.agent/architecture/architecture.html`：正式 HTML Atlas 镜像。
- `.agent/modules/06-agent-core-planning-control.md`：Agent Core 模块镜像。

## Must Preserve

- `docs/architecture/` 和 `.agent/architecture/` 都只能包含 `README.md`、`architecture.md`、`architecture-views.md`、`architecture.html`。
- 模块设计必须进入 `docs/modules/`，不能回到 architecture 目录。
- Current 只描述代码、测试、trace/eval 或 verifier 已证明事实。
- Target 只描述近期目标，不等于完成声明。
- Future Optional 不得成为短期 blocker。
- History 保留旧材料原文，不为了新叙事改写证据。
- `architecture.md` 必须以设计文字为主，只保留少量关键图。
- `architecture-views.md` 承担十类 Mermaid 图源，不承载完整设计解释。
- HTML 是图谱展示，不承担完整目标架构事实源。

## Focused Tests

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Docs Sync

修改总架构时检查：

- `docs/architecture/README.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture-views.md`
- `docs/architecture/architecture.html`
- `.agent/architecture/README.md`
- `.agent/architecture/architecture.md`
- `.agent/architecture/architecture-views.md`
- `.agent/architecture/architecture.html`

修改模块设计时检查：

- `docs/modules/README.md`
- 对应 `docs/modules/<module>.md`
- 存在镜像时同步 `.agent/modules/<module>.md`

修改 Current / readiness 时检查：

- `docs/status/production-readiness.md`
- `README.md`
- `docs/README.md`

修改 ADR 或 ownership 时检查：

- `docs/decisions/`
- `docs/governance/`
- `.agent/references/architecture-docs-map.md`

## Lessons Learned

文档同步的本质不是“所有地方都写一遍”，而是每个 surface 只承载自己的事实层级，并且入口之间不互相矛盾。
