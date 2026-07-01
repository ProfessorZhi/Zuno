# Workflow Update Policy

## When To Use

当用户提出新的长期要求、纠正 Agent 行为、改变文档维护方式、改变模板输出、改变 program 生命周期或指出工作流应自我更新时，使用本策略。

## Mental Model

```text
new user requirement
  -> classify requirement type
  -> choose update targets
  -> update docs/templates/programs/verifiers
  -> record workflow-change-log
  -> future agents inherit rule
```

## Current Truth

必须更新工作流的触发条件：

- 用户定义新的长期规则。
- 用户纠正 Agent 的项目维护行为。
- 新增或调整权威文档入口。
- 新增 `.agent` 子目录职责。
- 架构文档同步规则变化。
- Codex 轮次输出规则变化。
- 模板不能覆盖最新输出格式。
- plan / program 生命周期规则变化。
- Current / Target / Future / History 定义被细化。
- AGENTS.md、`.agent/references`、`docs/architecture`、`architecture.html` 之间出现不一致。

每次工作流规则变化都必须留下两类证据：

- 规则分类证据：说明新要求属于 one-time instruction、reusable project rule、architecture governance rule、Codex execution rule、documentation template rule 或 long-term workflow rule 中哪一类，以及为什么不是一次性任务噪音。
- 写回路径证据：说明是否需要更新 `AGENTS.md`、`.agent/references/`、`.agent/templates/`、`.agent/programs/`、`docs/architecture/`、verifier / tests；不更新的路径也要写明原因。

## Update Targets

| Target | When to update |
| --- | --- |
| `AGENTS.md` | 入口规则、强制读取顺序、全仓硬规则、停止条件变化 |
| `.agent/references/*` | 详细 workflow、architecture governance、maps、policies、inventories、long-term requirements 变化 |
| `.agent/templates/*` | 新规则影响未来生成内容的格式 |
| `.agent/programs/*` | 当前状态、queued program、收口清单、执行计划变化 |
| `docs/architecture/*` | 人类可读架构结论变化 |
| `docs/architecture/architecture.html` | 展示页内容或十类架构视图聚合变化 |
| verifier / tests | 规则需要机器检查或防漂移 |

## Target Direction

Agent Workflow Self-Maintenance 的最终效果是：用户提出长期规则后，后续 Agent 不需要读旧对话，也能自动继承最新规则。

## Must Preserve

- 一次性用户指令不必沉淀成长期规则。
- 长期规则必须写进 `.agent/references`。
- AGENTS.md 只写简短入口和强制路由。
- 影响输出形状的规则必须更新 `.agent/templates`。
- 影响一致性的规则必须更新 verifier 或 tests。

## Before Editing

1. 用一句话写出触发原因。
2. 标记 requirement type：one-time instruction、reusable project rule、architecture governance rule、Codex execution rule、documentation template rule、long-term workflow rule。
3. 选择 update targets。
4. 准备规则分类证据和写回路径证据。
5. 准备 workflow change log。

## Allowed Changes

- 更新工作流规则、模板、计划状态和验证脚本。
- 删除或替换过时规则时必须说明原因。

## Forbidden Changes

- 不要把每个用户偏好都永久化。
- 不要在没有验证的情况下宣称工作流已自我维护完成。

## Common Failure Patterns

- 更新 requirements 但忘记 change log。
- 更新 templates 但 system.yaml 没引用。
- 更新 reference set 但 exact-set test 没改。
- 只说“长期规则已沉淀”，但没有留下规则分类证据和写回路径证据。

## Debug Playbooks

- 不确定是否长期：如果它会影响未来 Agent 如何执行同类任务，就是长期。
- 不确定是否 AGENTS.md：如果没有它 Agent 进仓库就会走错路，才放 AGENTS.md。

## Focused Tests

```powershell
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

## Docs Sync

修改本文件时检查：

- `.agent/references/workflow-requirements.md`
- `.agent/references/workflow-change-log.md`
- `.agent/templates/workflow-change-note-template.md`
- `.agent/templates/phase-closure-report.md`

## Lessons Learned

工作流更新策略要少而硬：只有会改变未来执行的规则才进入长期系统。
