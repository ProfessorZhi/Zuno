# 文档与 Agent 工作流

## Source of truth

`AGENTS.md` 是仓库规则入口；`.agent/system.yaml` 是机器路由；`docs/project/`、`docs/architecture/`、`docs/decisions/`、`docs/evidence/` 和 `docs/history/red-blue/` 分别拥有自己的信息类型。

## 文档修改

1. `git status --short --branch`，确认分支、HEAD、origin/main 和用户已有修改。
2. 读取 `docs/README.md` 及任务对应的 Project、Architecture、ADR、Evidence 或 Review Record。
3. 先定义 Canonical Owner、边界和删除清单，再修改。
4. 迁移唯一内容到新 Owner，更新引用、验证器和测试，删除不再是 active route 的旧文件。
5. 运行 focused tests、文档验证、`git diff --check`，只提交本任务范围。

总体架构文档采用两层阅读模型：Part A 是给人看的设计叙事，Part B 是给实现、测试和审查使用的工程参考。理解系统先读 Part A；涉及 Contract、State、Recovery、Security 或实现时必须继续读 Part B、ADR、Evidence 和相关 Governance。不能只根据 Part A 实施工程细节。

## Red / Blue

Red / Blue 是人工协调的 Architecture Review。原始记录进入 `docs/history/red-blue/`，但不成为事实源或架构源。Main Judgment 只有在明确接受且单独完成 Architecture/ADR 修改后才进入 canonical 文档；Round 本身不自动触发实现。

## 清理与收尾

已授权的历史压缩只删除当前树副本，Git history 保留考古能力。不要删除用户文件、未提交资产、Migration 或可复现 Evidence。收尾要求：main 与 origin/main 一致、工作树只保留明确的用户未提交文件、文档入口/链接/边界验证通过。
