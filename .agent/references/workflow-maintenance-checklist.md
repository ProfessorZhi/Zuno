# Workflow Maintenance Checklist

## When To Use

每轮任务收口前，尤其是涉及架构、文档、`.agent`、模板、program、用户长期规则或 verifier 时，使用本清单。

## Mental Model

```text
new work
  -> does it change future agent behavior?
  -> does it change architecture docs or presentation?
  -> does it change templates or programs?
  -> can it be verified?
```

## Current Truth

### Before work

- 是否已经确认 `git status --short --branch`？
- 是否存在用户未提交改动需要保护？
- 是否读了 `AGENTS.md` 和任务对应 `.agent/references`？
- 是否需要读 `architecture-docs-map.md` 或 `workflow-update-policy.md`？

### During work

- 是否新增长期规则？
- 是否留下规则分类证据，说明它是一条长期规则还是一次性指令？
- 是否留下写回路径证据，说明哪些入口、reference、template、program、docs、verifier / tests 需要更新？
- 是否影响 AGENTS.md？
- 是否影响 `.agent/references`？
- 是否影响 `.agent/templates`？
- 是否影响 `docs/architecture`？
- 是否影响 `docs/architecture/architecture.html`？
- 是否影响 `.agent/programs`？
- 是否影响 verifier 或 tests？
- 是否在根目录生成了临时图片、截图、PDF 预览、测试报告、本地导出物或缓存？

### After work

- 是否更新 `workflow-requirements.md`？
- 是否更新 `workflow-change-log.md`？
- 是否把规则分类证据和写回路径证据写入收口报告或 workflow change note？
- 是否更新受影响模板？
- 是否重新生成 architecture HTML？
- 是否运行最小有效验证？
- 是否清理根目录临时产物，并确认正式附件进入 `docs/**/assets/`、临时产物进入 `.local/` 或 `tmp/`？
- 是否明确未完成项？

## Target Direction

这份清单应成为 Program Closure 自维护审查的前置工具，让“以后注意”转化为可执行规则。

## Must Preserve

- 不能把用户长期规则只写在最终回复里。
- 能机器检查的规则要进入 verifier 或 tests。
- 不能为了通过清单扩大用户未授权范围。

## Before Editing

更新本清单前，确认它是稳定流程规则，而不是一次性任务步骤。

## Allowed Changes

- 增加新的检查项。
- 调整检查项顺序，让它更贴合当前 workflow。

## Forbidden Changes

- 不要把项目事实或目标架构正文塞进 checklist。

## Common Failure Patterns

- 收尾只跑测试，没有检查 docs/HTML/reference 是否同步。
- 新增模板后没有让 `.agent/system.yaml` 或 program 引用。

## Debug Playbooks

- 如果不确定某项是否适用，用最小原则：会改变未来 Agent 执行同类任务的，适用；只影响本轮操作的，不适用。

## Focused Tests

```powershell
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

## Docs Sync

修改本文件时检查：

- `AGENTS.md`
- `.agent/references/workflow-governance.md`
- `.agent/references/workflow-update-policy.md`
- `.agent/programs/closure-checklist.md`

## Lessons Learned

清单的目标是让遗漏变少，不是让流程变重。
