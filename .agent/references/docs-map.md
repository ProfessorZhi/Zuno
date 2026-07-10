# 文档同步 Skill

## When To Use

当任务触碰 `docs/`、`.agent/`、AGENTS.md、history、README、架构叙事或术语边界时使用本 skill。

## Mental Model

```text
docs/ = formal human truth
.agent/references/ = local skills and lessons
.agent/templates/ = execution skeletons
.agent/programs/ = active execution plan
.agent/architecture/ = generated architecture mirror
docs/history/ = archive and evidence
```

## Current Truth

正式人类入口：

- `README.md`：仓库总览和首读路径。
- `docs/README.md`：文档入口。
- `docs/architecture/architecture.md`：Lean Complete Agentic GraphRAG Product 的详细实施蓝图事实源，包含六个运行域、黄金链路、owner、contract、配置、状态、失败、trace、测试和验收。
- `docs/architecture/architecture.html`：由四张 canonical Mermaid 图生成的展示摘要。
- `docs/architecture/production-readiness.md`：Current、Short-term Closure Gap、Measurement Blocked、Completed、Future Optional。
- `docs/architecture/document-ingestion-foundation.md`、`agent-core-runtime.md`、`capability-and-skill-layer.md`、`agentic-retrieval-planner.md`、`eval-observability-and-cost.md`、`input-layer-and-document-processing.md`、`knowledge-space-product-configuration.md`：六运行域专题细化。
- `docs/architecture/repo-ownership-matrix.md`：代码目录 ownership 辅助事实表。
- `docs/evidence/public-demo.md`：精选公开证据入口。
- `docs/history/`：历史档案。

Agent 工作流入口：

- `AGENTS.md`：仓库级 Agent bootloader。
- `.agent/README.md`：Zuno Local Agent Skill System 说明。
- `.agent/system.yaml`：路径到 skills、templates、docs_sync、verify 的路由。
- `.agent/references/`：本地项目 skills、lessons、playbooks。
- `.agent/templates/`：执行骨架。
- `.agent/programs/`：当前执行入口。
- `.agent/architecture/architecture.md`：必须与正式总架构文档一致的 Agent 镜像。

## Must Preserve

- Current 只描述代码、测试、trace/eval 或 verifier 已证明事实。
- Target 只描述近期目标，不等于完成声明。
- Future Optional 不得成为短期 blocker。
- History 保留旧材料原文，不为了新叙事改写证据。
- `architecture.md` 可以详细，但必须结构化、范围收敛、可实施。
- HTML 是展示摘要，不承担完整目标架构事实源。

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

修改架构或文档入口时检查：

- `README.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/document-ingestion-foundation.md`
- `docs/architecture/agent-core-runtime.md`
- `docs/architecture/capability-and-skill-layer.md`
- `docs/architecture/agentic-retrieval-planner.md`
- `docs/architecture/eval-observability-and-cost.md`
- `docs/architecture/input-layer-and-document-processing.md`
- `docs/architecture/knowledge-space-product-configuration.md`
- `docs/architecture/architecture.html`
- `.agent/architecture/README.md`
- `.agent/architecture/architecture.md`
- `.agent/architecture/architecture.html`
- `.agent/references/diagram-inventory.md`
- `.agent/programs/current.md`

## Lessons Learned

文档同步的本质不是“所有地方都写一遍”，而是每个 surface 只承载自己的事实层级，并且入口之间不互相矛盾。
