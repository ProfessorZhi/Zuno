# Architecture Docs Map

## When To Use

当任务涉及 `docs/architecture/`、`architecture.html`、Mermaid 图、README 架构摘要、目标架构或文档同步时，先读本文件。

## Mental Model

```text
docs/architecture/
  -> human-facing formal architecture source
docs/architecture/overall-architecture.md
  -> text-first overall architecture source
docs/architecture/architecture.md
  -> Mermaid source of truth
docs/architecture/architecture.html
  -> generated architecture presentation page
.agent/architecture/overall-architecture.md
  -> agent-facing overall architecture maintenance mirror
.agent/references/
  -> agent-facing governance, maps, policies and inventories
.agent/templates/
  -> reusable generation shapes
.agent/programs/
  -> current execution state
```

## Current Truth

### Human-facing architecture docs

- `docs/architecture/README.md`：架构文档入口、阅读顺序、Current / Target / Future / History 边界、两套理论和十类架构视图说明。
- `docs/architecture/overall-architecture.md`：总架构文档，偏文字说明 Zuno 当前事实、目标分层、主链路和实施落点。
- `docs/architecture/current-architecture.md`：当前实现事实，只写代码和测试已经证明的内容。
- `docs/architecture/target-architecture.md`：近期目标架构，包含 Agentic RAG、GraphRAG、Memory、Tool、Hooks、Evidence / Citation / Trace / Eval 的目标边界。
- `docs/architecture/roadmap.md`：正式人类状态入口，说明 queued program 和非目标。
- `docs/architecture/architecture.md`：十类 Mermaid 架构视图的唯一源。
- `docs/architecture/deliverables.md`：八大交付物、十类架构视图和根目录清洁期望。
- `docs/architecture/architecture.html`：唯一展示页，生成产物。
- `docs/architecture/assets/`：正式架构附件，例如目标架构 PDF。
- `docs/architecture/decisions/`：仍影响主线的正式架构决策。
- `docs/history/`：完成、过时或被替换的历史材料。

`docs/architecture/` 必须少而精。它保留稳定、正式、面向人的架构结论，不保存高频变化的执行计划、workflow change log、细粒度图清单或 Agent 操作规则。

### Presentation page

- `docs/architecture/architecture.html` 是 Zuno Architecture Overview 展示页，图为主。
- 它展示两套理论：`4+1 View Model` 和 `Logical / Component-and-Connector / Deployment / Quality View`。
- 它展示十类架构视图：`Logical View`、`Development View`、`Process View`、`Physical View`、`Scenarios View`、`V&B Logical View`、`Component-and-Connector View`、`V&B Deployment View`、`Quality View`、`Agent Loop View`。
- 前九类来自 4+1 和 View & Beyond 两套理论；`Agent Loop View` 是 Zuno 核心子系统放大图，不是第三套理论。
- 它不是唯一事实来源，必须与 `docs/architecture/` 保持一致。

### Agent-facing docs

- `.agent/architecture/overall-architecture.md`：Agent 侧总架构维护文档，必须和 `docs/architecture/overall-architecture.md` 保持一致。
- `.agent/references/project-map.md`：项目地图和目录职责。
- `.agent/references/documentation-governance.md`：文档治理工作流。
- `.agent/references/architecture-update-policy.md`：哪些变更必须同步哪些架构文档。
- `.agent/references/diagram-inventory.md`：十类架构视图的图名、用途、所属视图和更新触发条件。
- `.agent/references/current-target-future-rules.md`：Current / Target / Future / History 写法。
- `.agent/references/workflow-governance.md`：Agent 工作流系统如何协作和自我维护。

`.agent/references/` 可以比 `docs/architecture/` 更细、更常变化；它用于帮助 Agent 做维护判断，不要求面向外部读者展示。

## Target Direction

后续如果拆分完整 `docs/architecture/00-10` 系列文档，应先更新本文件、`docs/architecture/README.md`、`diagram-inventory.md`、`architecture-update-policy.md`、verifier 和 tests，不要静默新增前台文档。

## Must Preserve

- `docs/architecture/overall-architecture.md` 是文字总架构文档；`.agent/architecture/overall-architecture.md` 是 Agent 维护镜像，不能各写各的。
- `docs/architecture/architecture.md` 是 Mermaid source of truth。
- `architecture.html` 必须由生成器产出。
- `.agent/references` 只保存 Agent operating memory，不替代正式架构文档。
- `.agent/templates` 只保存输出骨架，不复制架构正文。

## Before Editing

1. 判断变更属于 Current、Target、Future 还是 History。
2. 查 `architecture-update-policy.md` 选择受影响文档。
3. 查 `diagram-inventory.md` 判断十类架构视图是否要更新。
4. 如果更新总架构文字，同时更新 `docs/architecture/overall-architecture.md` 和 `.agent/architecture/overall-architecture.md`。
5. 如果更新 Mermaid，运行 `python tools/agent/render_architecture.py --write`。

## Allowed Changes

- 更新文档职责、展示页职责、图清单和同步规则。
- 新增正式架构文档前先登记职责和验证规则。

## Forbidden Changes

- 不要让 HTML 成为唯一事实来源。
- 不要只更新 `.agent/references` 而不更新人类可读 docs。
- 不要把 `docs/history/` 中的旧方案重新放回前台，除非先写明替换理由。

## Common Failure Patterns

- `target-architecture.md` 写了新模式，但 `docs/architecture/architecture.md` 和 HTML 没同步。
- `architecture.html` 手改后与生成器不一致。
- README 引用的架构摘要和正式 docs 不一致。

## Debug Playbooks

- HTML stale：运行 `python tools/agent/render_architecture.py --check`，再用 `--write` 更新。
- 图标题缺失：查 `tools/agent/render_architecture.py` 的 `EXPECTED_DIAGRAMS` 和 `diagram-inventory.md`。

## Focused Tests

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Docs Sync

修改本文件时检查：

- `docs/architecture/README.md`
- `docs/architecture/overall-architecture.md`
- `docs/architecture/architecture.md`
- `.agent/architecture/overall-architecture.md`
- `tools/agent/render_architecture.py`
- `.agent/references/diagram-inventory.md`

## Lessons Learned

架构展示要强，但事实源必须更强。HTML 负责让人一眼看懂，docs 负责让结论站得住。
