# Semantic Classification Method

## Scope

本审计不重新打分、不重新回答、不修改 Round-005。每道题从零读取：Question、Blue Answer、Red Score、Blue Decision 和同步后的 Canonical Owner 文档。Round-005 的原始 Class 只用于比较，不能作为 Derived Class 的输入。

## Ordered test

1. 场景是否显示 Target Contract 仍无法给出唯一 Owner、State、Retry/Replan、Security 或 Recovery Authority？是则 attack-time `A`。
2. 若 Contract 已能说明，主要缺代码、Migration、接线、测试或真实 execution？是则 `I`。
3. 若设计和实现路径都清楚，主要缺质量、效率、成本或因果收益测量？是则 `E`。
4. 若设计可说明，但必须依赖真实 Sandbox、Provider、HA、Production、External Credential 或资格环境？是则 `X`。

`secondary_gaps` 可以并存，但不改变第一阻塞 Gate。`post_round_class` 描述 Canonical Sync 后仍阻塞成熟度的类别；架构问题已修复但实现仍未完成时，attack-time 可以是 A，post-round 可以是 I。`finding_state` 记录“本轮发现过”与“当前仍开放”的区别。

## Semantic independence

分类依据是场景中出现的具体对象、冲突和成熟度 Gate，例如 Domain/Checkpoint authority、Parser publication、Graph/Hybrid measurement、Provider qualification 或 Sandbox evidence。题号、预设数量和 Lens 只用于索引和统计，不参与分类。

## Boundary

这些是 Derived Audit 结论，不提升 Runtime、Facts、ADR、Current、Measured 或 Production 状态。
