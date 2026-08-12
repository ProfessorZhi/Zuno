# 红蓝会话摘要

本目录保存经过批准的 Red Interview、Blue Answer 和 Red/Blue Optimization Session 记录。记录目的是审查问题质量、回答是否迎合、Gap 是否聚类正确、架构修改是否真的改善以及后续是否回归；不是建立第二套架构事实源。

不得保存隐藏思维链、private chain-of-thought 或 token-level reasoning。可以保存所有用户可见的红队问题、蓝队回答、来源、公开的 Follow-up Decision Summary、评分、Gap、Change Set 和复测结果。

新会话应复制 [TEMPLATE](TEMPLATE/)，并至少包含：

```text
manifest.yaml
transcript.md
scorecard.md
gaps.md
blue-change-set.md
retest.md
```

会话记录必须 Pin 输入版本，区分真实面试与 Architecture Campaign，并把逐题 Gap 聚类后再进入 Blue Change Set。`sessions/` 不覆盖 `docs/` 的正式架构事实；Canonical Sync 只能记录已经通过 User Gate 的结果。

## Session Conformance

每个已完成 Session 必须能由机器复核，而不是只依赖书写协议：

```powershell
python tools/scripts/verify_red_blue_session.py
python tools/scripts/verify_red_blue_session.py project-reconstruction-lab/sessions/<session-id>
```

验证器检查：

- `Q001..QNNN` 连续且不重复，Transcript 的 `Scorecard Ref` / `Gap Candidate Refs` 可解析；
- `actual_question_count`、`question_budget` 和不足预算时的 `stop_reason` 一致；
- Scorecard、Gap Cluster、Change Set 和 Retest 之间没有孤儿引用；
- Campaign / Round Lineage、Attack Area Quality Profile 和 Baseline Delta 已声明；
- `APPLIED` Change 必须有 User Gate、Canonical Paths、Applied Commit 和验证记录；只有 `APPLIED` Change 才能被 Retest 作为正式修复引用。

`TEMPLATE/` 和以下划线开头的 synthetic fixture 不会被默认全目录扫描；它们可以被测试直接传给 verifier。

Gate Realignment 等 specialized session 可以使用独立的 `protocol_version` 和专用 verifier，
但仍必须声明基线、状态、用户 Gate、Canonical Sync、事实/Runtime 边界和不可升级的证据结论。

Scorecard 必须覆盖完整 Project Package。若问题长期只集中在 Agent/RAG，遗漏项目背景、产品价值、Ownership、开发过程、模型部署、竞品替代、上线和生产证据，应标记 `COVERAGE_FAILURE`。

建议命名：`YYYY-MM-DD-<scope>-<short-name>.md`。

最低结构：

```text
# 会话标题
日期：
范围：
输入事实版本：
红队角色：
攻击 Claim：
关键问题与回答摘要：
确认事实：
保持 Unknown：
新增 Gap：
蓝队提案：
用户确认项：
正式同步：
复测结果：
```

推荐执行入口见 [workflows/](../workflows/README.md)。
