# 架构文档

这里是 Zuno 的正式架构文档入口。`docs/architecture/` 是人类可读的正式架构说明，应该少而精、相对稳定；`docs/architecture.html` 是面向展示的唯一架构 HTML；`.agent/references/` 是 Agent-facing operating memory，用来维护高频变化的规则、索引、图清单和工作流，不替代正式文档。

## 最终成品定义

Zuno 不只是代码项目，而是代码、架构文档、Agent 工作流、展示页面都能持续同步演化的工程化项目。

对外表达时，Zuno 最终成品是五个成熟系统：

1. Agent 工作流文档系统。
2. 元工作流自我维护系统。
3. 正式架构文档系统。
4. 架构 HTML 展示系统。
5. 干净清晰且可验证的代码结构。

内部验收时，拆成八大交付物：

1. Agent 工作流文档系统。
2. 元工作流自我维护系统。
3. 模板与执行计划系统。
4. 正式架构文档系统。
5. 架构 HTML 展示系统。
6. 完善的 Zuno 目标架构。
7. 清晰干净的代码和目录。
8. 一致性与验证系统。

## 首读顺序

1. `current-architecture.md`：当前实现事实，只写代码和测试已经证明的内容。
2. `target-architecture.md`：近期目标架构，不冒充已完成。
3. `roadmap.md`：当前状态、queued program、下一步和非目标。
4. `../architecture.md`：Obsidian 风格架构总览，也是十类 Mermaid 架构视图的唯一源。
5. `../architecture.html`：面向展示的唯一生成页。
6. `assets/zuno-agentic-rag-graphrag-ideal-architecture.pdf`：目标架构参考 PDF。
7. `../evidence/public-demo.md`：公开证据入口。
8. `decisions/README.md`：仍影响主线的架构决策。

## 当前前台结构

```text
docs/architecture/
  README.md
  current-architecture.md
  target-architecture.md
  roadmap.md
  assets/
  decisions/
```

过时审计、旧规格、旧 phase、旧计划和旧 runbook 不再放在 `docs/architecture/` 前台，统一归档到 `docs/history/`。

## 历史入口

已完成或被替换的程序统一归档到：

- `docs/history/programs/`

常用历史入口包括：

- `docs/history/programs/zuno-target-architecture-migration-v1/`
- `docs/history/programs/official-graphrag-cleanup-v1/`
- `docs/history/programs/zuno-target-runtime-v2/`
- `docs/history/programs/zuno-architecture-surface-cleanup-v1/`
- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`
- `docs/history/programs/zuno-six-layer-internalization-v1/`

## 两套架构理论

Zuno 的架构说明同时使用两套互补视角。

第一套是经典 `4+1 View Model`：

- Logical View：核心领域对象和职责。
- Development View：代码模块、包和组件组织。
- Process View：运行时流程、并发、通信、事件流和性能关注点。
- Physical View：部署节点、数据库、中间件、模型服务。
- Scenarios：关键业务场景，用来贯通和验证前面四个视图。

第二套是 View & Beyond / C&C 视图体系：

- Logical View：系统模块和职责划分。
- Component-and-Connector View：运行时组件如何连接、调用和通信。
- Deployment View：服务、数据库、中间件和外部系统部署关系。
- Quality View：性能、可靠性、安全性、可观测性、可修改性和可评估性如何实现。

两套理论不是冲突关系。`4+1 View Model` 提供经典总框架；`Logical / Component-and-Connector / Deployment / Quality View` 提供更适合工程说明和项目展示的组织方式。

## 十类架构视图

完整十类图由 `docs/architecture.md` 维护，并由 `tools/agent/render_architecture.py` 生成到 `docs/architecture.html`。这里的“十类”指十个不同架构关注面，不是同一张图的多个排版。

1. `Logical View`
2. `Development View`
3. `Process View`
4. `Physical View`
5. `Scenarios View`
6. `V&B Logical View`
7. `Component-and-Connector View`
8. `V&B Deployment View`
9. `Quality View`
10. `Agent Loop View`

Agent Loop 在理论上可以归入 Process View 或 Component-and-Connector View，但 Zuno 的核心价值正是 Agent 如何计划、检索、调工具、观察、反思和重试。因此它作为第十类专题图单独展示，用来放大解释 Zuno 的 Agentic RAG 内核。完整展示放在 `docs/architecture.html`。

## Current / Target / Future / History

- Current：当前代码真实实现，必须由代码、测试、trace、eval 或可复现结果证明。
- Target：近期目标架构，不等于已经实现。
- Future：长期方向，例如微服务拆分、事件驱动 worker、产品级默认多 Agent、Coding Agent mode。
- History：完成、过时或被替换的计划、程序、阶段、审计、规格和旧 Agent 工作流材料。

禁止把 Target / Future 写成 Current。正式结论先进入 `docs/architecture/`；只给 Agent 使用的维护规则进入 `.agent/references/`；历史材料进入 `docs/history/`。

## Architecture Documentation Governance

涉及架构、Agent Runtime、RAG、GraphRAG、Memory、Tool Layer、Hooks、Trace、Eval、部署、中间件或前后端契约时，必须同步检查：

- `docs/architecture/*`
- `docs/architecture.md`
- `docs/architecture.html`
- `.agent/references/architecture-docs-map.md`
- `.agent/references/documentation-governance.md`
- `.agent/references/architecture-update-policy.md`
- `.agent/references/diagram-inventory.md`
- `.agent/references/current-target-future-rules.md`
- `.agent/programs/current.md` 或 `.agent/programs/implementation-roadmap.md`

`docs/architecture.html` 是展示页，不是唯一事实来源。不要只改 HTML；应先更新正式 docs 或 Mermaid source，再重新生成 HTML。高频变化的执行细节、workflow change log、图清单和 Agent 操作规则留在 `.agent/references/`，不要重复堆进 `docs/architecture/`。

## Agent Workflow Self-Maintenance

当用户提出新的长期工作方式要求时，Agent 不能只在本轮照做，必须判断是否要更新：

- `AGENTS.md`
- `.agent/references/*`
- `.agent/templates/*`
- `.agent/programs/*`
- `docs/architecture/*`
- `docs/architecture.html`
- verifier / tests

工作流自我维护规则记录在 `.agent/references/workflow-governance.md`、`.agent/references/workflow-update-policy.md`、`.agent/references/workflow-requirements.md`、`.agent/references/workflow-change-log.md` 和 `.agent/references/workflow-maintenance-checklist.md`。

## 验证

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
```
