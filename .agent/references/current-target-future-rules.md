# Current Target Future Rules

## When To Use

当写 `docs/`、`.agent/`、README、architecture HTML、program、roadmap 或最终汇报时，用本规则判断事实层级。

## Mental Model

```text
Current = implemented and verified
Target  = near-term intended architecture
Future  = long-term direction
History = completed, replaced, or retired material
```

## Current Truth

- Current 必须由代码、测试、trace、eval、public demo 或可复现运行结果支撑。
- Target 可以描述近期设计，但必须明确尚未完全实现。
- Future 是非近期方向，不能进入当前验收。
- History 是完成、过时、被替换或归档的方案。

## Target Direction

Zuno 的目标架构可以写清楚，但必须避免“目标已经实现”的假成熟。最稳的表达是：Current 负责证明，Target 负责方向，Future 负责边界，History 负责证据。

## Must Preserve

- Single GeneralAgent mainline 是当前 runtime 主线。
- 产品级默认多 Agent、微服务拆分、事件驱动 worker、Coding Agent mode 属于 Future，除非用户明确打开未来方向实现 program。
- Architecture Documentation Governance 和 Agent Workflow Self-Maintenance 属于当前工作流规则，一旦写入并通过 verifier，就可以作为 Current workflow truth。

## Before Editing

1. 写每段架构结论前先标出 Current、Target、Future 或 History。
2. 没有代码和验证证据的实现不要写进 Current。
3. 被替换方案不要删除，按需要归档到 `docs/history/`。

## Allowed Changes

- 给文档增加状态标签。
- 把混写内容拆到正确文件。
- 把历史计划移到 history。

## Forbidden Changes

- 禁止 “will be” 和 “is” 混写。
- 禁止用 README 或 HTML 展示语言覆盖正式 Current 文档证据。
- 禁止把 queued draft 写成 active program。

## Common Failure Patterns

- Target Architecture 写得像 Current Architecture。
- Roadmap 没说明 queued / not active。
- History 还留在前台入口。

## Debug Playbooks

- 不确定是 Current：找代码路径、测试名和验证输出；找不到就是 Target 或 Future。
- 不确定是 History：如果它已完成、被替换或不再作为前台工作入口，就进入 History。

## Focused Tests

```powershell
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_agent_system.py
```

## Docs Sync

修改本文件时检查：

- `AGENTS.md`
- `docs/architecture/README.md`
- `docs/architecture/current-architecture.md`
- `docs/architecture/target-architecture.md`
- `docs/architecture/roadmap.md`

## Lessons Learned

Zuno 文档最值钱的纪律，就是 Current 和 Target 不混写。
