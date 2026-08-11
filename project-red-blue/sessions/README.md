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
