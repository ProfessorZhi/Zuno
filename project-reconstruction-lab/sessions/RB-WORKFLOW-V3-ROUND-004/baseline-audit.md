# Round-004 Baseline Audit

- Baseline SHA: `166a54d51aba0a822c3b5c539d1c43435f8c203f`
- Source state: Canonical Architecture `ACCEPTED_TARGET`; V3.1.1 normalization complete。
- Scope: Human Writing V3.1.2 and Architecture Consistency / Failure Semantics / Component Survival。
- Historical Round-003: immutable；不重算、不改写。
- Facts / Runtime / UI / Schema / Migration / Dependencies / Production Infra: unchanged。
- Existing Part A scorecard: Product、Multi-Agent、Services、Eval、Deployment 低于 Strong，作为本轮优先阅读输入。

本审计把“读起来像人写的”和“Contract 是否完整”分开。Part A 关注推导、场景和代价；Part B
继续由已有结构 verifier 检查。确定性 warning 不自动升级为人工 PASS。
