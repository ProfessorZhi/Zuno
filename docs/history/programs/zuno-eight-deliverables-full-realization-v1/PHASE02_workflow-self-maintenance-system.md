# PHASE02 Workflow Self-Maintenance System

Program: `zuno-eight-deliverables-full-realization-v1`
status: completed

## 为什么

八交付物的前 3 项决定后续工作不会再次散落到临时提示词、旧 program 或不受验证的文档里。工作流系统必须能自我维护、自我检查，并把新长期规则沉淀到正确位置。

## 范围

覆盖交付物：

- 1. Agent 工作流文档系统。
- 2. 元工作流自我维护系统。
- 3. 模板与执行计划系统。
- 8. 一致性与验证系统。

主要文件：

- `AGENTS.md`
- `.agent/system.yaml`
- `.agent/references/*`
- `.agent/templates/*`
- `.agent/programs/*`
- `.agent/scripts/*`
- `tests/repo/*`

## 执行步骤

1. 审计 AGENTS、system、references、templates 的职责是否重复或漂移。
2. 固定“长期工作流规则写回哪里”的路由：仓库硬规则、Agent operating memory、模板、program、verifier/test。
3. 补齐模板骨架：phase 报告、architecture change note、workflow change note、verification report。
4. 把可机器检查的规则进入 verifier/test。
5. 更新 README 和 docs map 中的入口说明。

## 验收

- 新需求如何从对话沉淀为规则，有明确文件归属。
- `.agent/templates/` 只保存骨架，不保存项目事实。
- `.agent/programs/` lifecycle 有 active、closure、archive 三态。
- 修改 workflow 相关文件会触发 verifier/test 防漂移。

## PR 边界

可以拆成 workflow docs PR 和 verifier/test PR；两者必须一起完成才能关 phase。

## Phase Summary

- Multi-agent: enabled in the main Codex goal-mode thread; Architecture / Docs、Runtime / Code、Verification、Integration Reviewer 工作组均已完成并关闭。
- Result: rule writeback route、template skeleton boundary、program lifecycle、workflow change log schema、phase closure self-review 和 verification report template 已进入 verifier/test guard。
- Current / Target / Future / History: 本 phase 只更新 workflow、`.agent`、architecture roadmap 状态面和 repo guard；未把 Target/Future runtime 能力写成 Current。
- Runtime boundary: 未修改 runtime/API/DB/frontend/dependency；Codex 多 agent 仅作为执行协作，不写成 Zuno runtime 多 Agent 架构。
- Validation: full base verifier stack、workflow verifier 和 repo tests passed before commit.
- PR: to be created as stacked PHASE02 PR after commit and push.
