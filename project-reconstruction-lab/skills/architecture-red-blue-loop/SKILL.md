---
name: architecture-red-blue-loop
description: Run an evidence-driven Red/Blue architecture review with attack, defense, counter-review, proposed judgment, archive-first recording, and optional canonical revision. Use only when the user or an upper Coordinator explicitly invokes architecture-red-blue-loop; it never auto-applies architecture changes.
---

# Architecture Red Blue Loop

## Purpose

把一次架构攻击收口为可审计的历史记录和明确决策；先删除、简化、复用或测量，再考虑新增设计。

## Activation and Modes

```text
DEFAULT ACTIVATION: EXPLICIT_ONLY
MODES: MANUAL_MAIN | AUTOMATED_MAIN
DECISION AUTHORITY: CHATGPT_MAIN_ONLY
```

本 Skill 不是当前 Zuno Manual Workflow 的默认执行路径。用户必须明确说出 Skill 名称或明确要求自动跑一轮架构审查。

- `MANUAL_MAIN`：Skill 组织 Red、Blue、Red Review；Main Judgment 交给用户或外部 ChatGPT Main。
- `AUTOMATED_MAIN`：Skill 可以形成 `PROPOSED_MAIN_JUDGMENT`，只能使用 ACCEPT、REJECT、DEFER、MEASUREMENT、FACT_GAP、NO_CHANGE；它仍是 Proposal，不绕过用户指定的 Canonical Gate。

## Inputs

- 最新 main、BASE SHA、读取范围和禁止范围；
- docs/facts、docs/architecture、ADR、治理、Evidence，以及明确允许的代码或测试；
- Round Theme、最大轮数和 MANUAL_MAIN 或 AUTOMATED_MAIN；
- 是否允许后续 Architecture Revision。默认不允许。

## Workflow

1. Bootstrap：确认分支、基线、Owner、阅读范围、禁止范围和未提交修改；
2. Main Brief：定义 Root Claim，不预设固定模块数量或固定题量；
3. Red Attack：攻击必要性、替代、状态、失败、恢复、安全、成本和反转条件；
4. Blue Defense：用普通语言回答，再补 Contract，并明确未知和证据不足；
5. Red Review：区分答案、事实、架构、测量和实现缺口；
6. Main Judgment：由 ChatGPT Main 选择最终分类；Automated Main 只能输出 Proposal；
7. Archive First：先保存 Question、Answer、Review、Decision、BASE SHA 和状态；
8. Architecture Revision：只有 Main 明确授权时，才在正式 Owner 上进行独立 Revision；
9. Validation：运行受影响的文档、链接、边界和专项测试。

复杂度处置顺序固定为：

```text
DELETE → SIMPLIFY → REUSE → EXTERNALIZE → MEASURE → BUILD
```

MEASURE 不等于 BUILD。证据不足时，优先留下 Measurement，而不是新增设计。

## Archive First

Archive Commit 与 Architecture Revision Commit 必须是两个阶段。无论 MANUAL_MAIN 还是 AUTOMATED_MAIN，不能在生成 Red Finding 的同一步修改 architecture.md。

## Outputs

- Red Findings、Blue Decisions、Main Judgment 或 Proposed Main Judgment；
- KEEP、SIMPLIFY、REUSE、EXTERNALIZE、MEASURE、BUILD、DELETE、DEFER 处置；
- Round Archive、Canonical Delta、验证结果、Open Gaps 和下一步建议；
- 若未获授权，只输出 Review / Proposal，不修改正式文档。

## Boundaries

- Red 只攻击，Blue 不自动写回 Canonical；
- 不把 Red Finding 自动升级为 ADR 或 Architecture Gap；
- 不把代码存在、Mock、Target 文档或分数当作生产证明；
- 不自动创建 Worktree、Branch、Commit、Push，不自动调用 Codex；
- 不自动修改 docs/architecture/、docs/decisions/ 或 Facts；
- 不拥有最终 Architecture Decision，不自动启动下一 Round。

## Failure / Stop Conditions

- BASE SHA、Context、权限边界或用户授权无法证明时停止；
- Blue 需要禁止材料才能回答时记录 CONTEXT_GAP；
- 复杂度收益只能靠口号表达时选择 MEASUREMENT 或 SIMPLIFY；
- 需要修改 API、Schema、Dependency、安全边界或生产环境时停止并请求单独授权；
- Round 中止时保留 ABORTED，不补写不存在的 Answer、Score 或 Candidate。

## Evidence Rules

每个决策至少绑定 Problem、Alternative、Owner、State、Failure/Recovery、Test、Cost 和 Reversal Condition。Current、Target、Hypothesis、History 分开；正式 Round 归档到 docs/history/red-blue/，架构变更回到正确 Canonical Owner。

## Example Invocation

```text
请明确调用 architecture-red-blue-loop，以 MANUAL_MAIN 模式审查“Domain State 是否必须独立于 Runtime Checkpoint”。
先完成 Red、Blue、Review 和 Archive；没有 ChatGPT Main 明确授权，不修改 docs/architecture。
```
