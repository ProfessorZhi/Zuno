# Findings — rb-2026-09-09-resume-claims-002

Round result: `CLOSED_WITH_REMAINING_EVIDENCE_GAP`  
Highest severity: `S2`

本轮是 `rb-2026-09-09-resume-claims-001` 的独立措辞复测。上一轮两个 S0 Resume 风险和 measurement-related Resume risk 已解除；只保留一个仍会改变后续决策的 Finding。

## F1R — Resume 真实性风险已解除，但个人任务级 Evidence 仍不足

Severity: `S2`  
Type: `OWNERSHIP_GAP`, `EVIDENCE_GAP`

### Retest result

事实对齐候选简历已经把 Zuno 个人 Claim 收回到 Canonical Project 能够支持的范围：

- 部分 Agent 开发 / Tool Calling Strategy；
- Memory 第一批重要工作；
- OpenViking 在 Memory / Context 区域的接入；
- PostgreSQL 实际数据查看 / 调试；
- 后续 Architecture / Evidence 边界复盘。

它不再把统一控制器、完整 GraphRAG、整个 Memory、完整 Runtime 或评测系统写成本人已完成设计 / 实现。因此上一轮的 `S0 RESUME_CLAIM_RISK` 已经关闭。

当前缺口出现在下一层：方向级参与还不足以支撑高质量项目深挖。若面试官要求候选人任选一条 Zuno 经历，连续讲清“原需求 → 本人决策 → 代码 / 接口 → 失败或 Bug → 测试 → 结果 → 团队边界”，现有 Project / Provenance 还没有恢复足够细的任务级证据。

### Decision impact

不要继续通过弱化 Resume 文案解决这个问题。候选稿已经足够克制；下一步应恢复 1–2 个个人任务闭环，让当前“参与过”升级成可验证、可展开的工程故事。

优先顺序：

1. OpenViking / Memory / Context 接入；
2. Tool Calling Strategy；
3. 某个具体 Agent 开发任务；
4. 数据库调试 / 故障定位。

哪一条最先恢复出真实 commit / code / test / bug 证据，就先成为主面试故事。

### Source support

- fact-aligned candidate resume snapshot；
- `docs/project/README.md` 的方向级个人参与边界；
- `docs/governance/project-fact-provenance.md` PF-009～PF-012 及待补证来源。

### Evidence needed

每个候选任务尽量恢复：

```text
需求 / 问题
本人负责范围
相关 commit / PR / 文件
关键数据结构 / API / 状态变化
真实 Bug / 失败场景
测试 / 调试方式
结果或可验证产物
团队 / Framework 边界
```

### Retest scenario

恢复一个任务闭环后，Red 不再问“你参与过什么”，而直接选一条 bullet：

> 这个需求是谁提的？你改了哪段代码？为什么这样做？最难的 Bug 是什么？怎么验证？如果不用你的方案，最简单替代是什么？

Blue 必须在不进入 Target Architecture 兜底的情况下，用 History / Current Evidence 完成 3–5 分钟回答。

## Resolved previous findings

- `S0 PROJECT_REALITY_GAP / RESUME_CLAIM_RISK`：候选简历恢复法律智能 / LIPLAB / 天津法院相关项目身份，并保留 Pilot / Production 上限。
- measurement-related `RESUME_CLAIM_RISK`：候选简历不再把固定评测覆盖或 GraphRAG 收益写成已验证结果。
- strong-personal-ownership `RESUME_CLAIM_RISK`：候选简历不再把团队 / Target 能力写成本人完整设计实现。

项目本身的正式 `MEASUREMENT_GAP` 仍然存在，但它不再是 Resume Truthfulness Finding。
