# 文档与 Agent 工作流

## Source of truth

`AGENTS.md` 是仓库规则入口；`.agent/system.yaml` 是机器路由。

`docs/` 的八个一级目录各自拥有不同信息类型：

```text
Knowledge Plane:
project / research / architecture / modules

Control & Maintenance Plane:
decisions / evidence / governance / maintenance
```

其中 `research/` 只提供上游研究依据，`maintenance/` 只提供运行/协作/历史材料；两者都不能覆盖 Project、Architecture 或 Evidence。

给人看的完整 ChatGPT / Claude Code / GitHub 协作说明见 `docs/maintenance/agent-workflow/README.md`；Red / Blue Interview Harness 的人类流程见 `docs/maintenance/red-blue/README.md`。本文件保持机器路由所需的简洁版本。

## 文档修改

1. 确认目标分支、latest main SHA 和用户已有修改。
2. 读取 `docs/README.md` 及任务对应的 Project、Research、Architecture、ADR、Evidence、Governance 或 Review Record。
3. 先定义 Canonical Owner、边界和删除/迁移清单，再修改。
4. Research 结论进入 canonical docs 前，先区分 `DIRECT_LINEAGE / CAPABILITY_LINEAGE / CONCEPTUAL_LINEAGE / BACKGROUND_ONLY / UNVERIFIED`。
5. 迁移唯一内容到新 Owner，更新引用、验证器和测试，删除不再是 active route 的旧文件。
6. 运行 focused tests、文档验证和 diff review，只提交本任务范围。
7. PR CI 通过后 merge；merge 后重新读取 exact `main` HEAD 再宣布完成。

总体架构文档采用两层阅读模型：Part A 是给人看的设计叙事，Part B 是给实现、测试和审查使用的工程参考。理解系统先读 Part A；涉及 Contract、State、Recovery、Security 或实现时必须继续读 Part B、ADR、Evidence 和相关 Governance。

## Research

研究材料不能直接覆盖 Canonical Truth：

```text
paper / interview / platform / external research
→ verify source and identity
→ record in docs/research/
→ decide Writing Gap vs Architecture Gap vs Evidence Gap
→ update canonical owner separately if accepted
→ Current still requires docs/evidence/
```

平台 baseline 会过期；Build/Buy 判断前重新核验官方资料。

## Red / Blue

Red / Blue 使用专用 `.agent/red-blue/`，不再混在一般 `.agent/programs/` 中。它是 Interview / Architecture Stress-Test Harness：

```text
.agent/red-blue/                         machine protocol + active Round state
docs/maintenance/red-blue/              human workflow
docs/maintenance/history/red-blue/      closed Round archive
```

Red 从精确简历 Claim 出发，可以读取批准的真实面试语料校准 interviewer pressure；Blue 使用同一份简历快照和允许的 Zuno canonical docs，尤其优先从 Project / Architecture / Module Part A 组织回答。面经、八股、用户过去 QA、Red hidden intent 和 Judge 评语不得进入 Blue Closed-book context。

支持 `human-candidate`、`chatgpt-duel` 和 `autonomous-agent`。正式 Agent Round 应隔离 Red / Blue / Judge contexts；Judge 只判 Gap，不给 Blue 补标准答案。原始记录进入 `docs/maintenance/history/red-blue/`，但不成为事实源或架构源。Main Judgment 只有在明确接受且单独完成 Architecture/ADR/Docs/Evidence 修改后才进入 canonical owner；Round 本身不自动触发实现。

## 清理与收尾

已授权的历史压缩只删除当前树副本，Git history 保留考古能力。不要删除用户文件、未提交资产、Migration 或可复现 Evidence。

收尾要求：PR required CI 通过、merge 成功、重新读取 main HEAD、文档入口/链接/边界验证通过。不要根据 PR 摘要或本地旧状态宣布完成。
