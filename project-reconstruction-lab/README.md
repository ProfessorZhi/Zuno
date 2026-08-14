# Project Reconstruction Lab

`project-reconstruction-lab/` 是项目事实恢复、架构面试和 Red/Blue 决策实验室。它不是
`docs/` 的第二套事实源，也不是简历生成器。今天的正式事实、Target Architecture、ADR 和可复现
证据分别由 `docs/facts/`、`docs/architecture/`、`docs/decisions/` 和 `docs/evidence/` 持有。

## 当前边界

本目录只保留：

- [`WORKFLOW.md`](WORKFLOW.md)：唯一当前 Architecture Interview / Red-Blue 工作流；
- [`archive-map.md`](archive-map.md)：正式历史 Round 的导航；Manual Round 保留完整记录，旧自动化
  程序由 [`docs/history/red-blue/`](../docs/history/red-blue/README.md) 的单一 Legacy Summary 持有；
- [`skills/`](skills/README.md)：三个仓库内、仅显式调用的本地 Skill。

旧的事实恢复、候选架构、流程版本、Bootstrap、Reset、Closure、Prompt、Session Template 和
实验工程材料不再作为当前 Lab 树保存。Git history 仍可用于考古；正式 Round 不从当前 Lab
重复维护。默认未来只新增 `manual-round-NN-<theme>.md`，除非用户明确重新启动自动化程序。

## 读取顺序

```text
docs/facts/
  → docs/architecture/
  → docs/decisions/
  → project-reconstruction-lab/WORKFLOW.md
  → 按需读取 docs/history/red-blue/
```

使用场景：

- 项目事实或个人贡献：先读 `docs/facts/` 和 `docs/history/`；
- 架构攻防：读 `WORKFLOW.md`，再读目标架构和对应事实；
- 大厂深挖：用户明确指定后，读取 `skills/red-team-interviewer/SKILL.md`；
- 自动化架构优化：用户明确指定后，读取 `skills/architecture-red-blue-loop/SKILL.md`；
- JD 到项目设计：用户明确指定后，读取 `skills/jd-enterprise-project/SKILL.md`。

这些 Skill 通过 `.agent/system.yaml` 的 `local_skill_registry` 注册为
`REPOSITORY_LOCAL_EXPLICIT_ONLY`。它们不会根据普通任务自动加载，也不会安装到全局 Skill 目录；
只有用户或上层 Coordinator 明确说出 Skill 名称时，Agent 才读取对应路径。

## 不允许的推断

当前仓库不等于完整历史项目。不得把代码目录、依赖、Compose、Target 文档、论文或面试题
反向升级为历史事实、个人 Ownership、生产部署或质量指标。所有输出必须区分 `CURRENT`、
`HISTORY`、`TARGET`、`HYPOTHESIS` 和 `UNKNOWN`。

Lab 的输出只有在经过对应 Owner 审查后，才可以写回 `docs/`。Red Finding 不自动成为
Architecture Gap，Blue Proposal 不自动成为 ADR；先归档“发生了什么”，再由 Main 决定“是否
改变正式架构”。

## 当前状态

```text
LAB_STATE: LIGHTWEIGHT_RECONSTRUCTION
ACTIVE_WORKFLOW: WORKFLOW.md
ACTIVE_ROUND: NONE
FORMAL_ROUND_OWNER: docs/history/red-blue/
ARCHITECTURE_REVISION: NOT_PART_OF_THIS_CLEANUP
PRODUCTION_READINESS: NOT_ESTABLISHED
```

本次轻量化重建不启动新的 Round，不生成题集，不修改 Canonical Architecture、Facts、ADR 或
业务 Runtime。
