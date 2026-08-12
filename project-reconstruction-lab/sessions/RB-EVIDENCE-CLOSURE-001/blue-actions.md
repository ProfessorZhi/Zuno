# Blue Actions

Blue Team 只提出最小补证据动作，不在本会话直接实现 Target Architecture。

## 优先级

### A — Domain 与并发

1. 为 Q005 建立最小 Domain Owner mutation contract：合法 Owner、非法 Owner、版本、审计、幂等。
2. 为 Q053 建立 PlanVersion/DomainVersion 并发冲突 fixture：旧计划拒绝、重规划、重放安全。
3. 以 Q016/Q097 的现有 focused recovery test 为基础，加入 Domain DB、Runtime checkpoint、EffectReceipt 的 crash matrix。

### B — Tool Effect 与 Security

1. 把 Q061/Q063/Q064/Q070 组合成一条从 authorization 到 receipt 的最小集成路径。
2. 加入 revoked/expired SecurityEpoch、Provider timeout、duplicate request 和 Unknown reconciliation。
3. 在隔离环境可用后执行 Q066 的 escape、egress、secret 和 resource tests。
4. 从不可信 Context 到 Tool 执行加入 Q067 的 injection integration test。

### C — Evidence / Eval

1. 恢复 Court QA 的协议，不先填模糊分数；冻结问题、参考材料、评价人和 rubric。
2. 为 Q039 执行 Citation correctness、Evidence sufficiency、Unsupported Claim Rate 和 A/B/C 对照。
3. 仅在真实输入和固定预算下判断 Legal Domain/Capability/Runtime 是否有增益。

## 不采取的动作

- 不为“让 verifier 通过”修改产品 Runtime；
- 不把 12 个 P0 拆成更多根因；
- 不为了满足微服务目标预先拆服务；
- 不添加 Java、Kafka、Kubernetes、Event Sourcing、2PC 或 Saga；
- 不修改 Schema/Migration、公开 API、依赖或生产 Infra；
- 不同步 `docs/project/`，直到 P0 Closure Gate 和 User Architecture Gate 通过。

## Reversal Criteria

如果 V4/V5 结果表明简单的 Tool/Worker/模块化单体已经达到同等质量、安全和恢复指标，
对应 Domain-aware Runtime、Graph、Memory、Service 或自研组件必须降级、外部化、延后或删除。
