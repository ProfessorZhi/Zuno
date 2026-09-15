# Round Report — rb-2026-09-15-formal-019

status: `COMPLETE`

## 结论先行

本轮 Red/Blue 没有证明 Zuno 需要更复杂的拓扑。Generic Host / Single Agent + Legal Backend、Single Controller、GraphRAG/Memory/Multi-Agent measurement-gated 的总体方向仍成立。

真正值得修的是四个 P0：

1. **Memory / Context Authority 没完全落位**；
2. **Tool / Capability / Config / Credential 的版本依赖链在文档里过于分散**；
3. **Effect Reconciliation Current 状态写得不够锋利，而且实现确实有 blocker**；
4. **Mandatory Audit Target 正确，但 Current send gate 已被负向证据证明没有闭合**。

Red Final 对候选人的盲评是 `PASS`。主要短板是 Evidence，不是实现深度或真实性。

## Red1 发现了什么

Red1 没从九模块名词开始，而是先削复杂度：为什么 Agent、为什么 GraphRAG、为什么 Memory、为什么 direct route、为什么自研 MCP 层。

它很快把三个关键事实打出来：

- Tool/MCP 历史实现可以讲深，但 4 月版本不能外推成后来完整 Effect Control；
- GraphRAG 的回退修复很真实，但 5-query smoke 只能证明 regression fix；
- Memory V2 有 contract 深度，但 scope equality、review、并发、撤权都不能冒充 enterprise closure。

## Blue1 暴露了什么

Blue1 最有价值的行为是主动承认边界：

- shared Agent instance 的 cross-user isolation 没有历史证明；
- MCP config 是 call-time 读取，长任务可能漂移；
- GraphRAG threshold 6/9 是 heuristic；
- tiny smoke 没 holdout / ablation；
- Memory scope 不是 authorization；
- durable Memory concurrency / revocation / quality A/B 没闭环。

这让 Red2 有了真正 answer-driven 的攻击面。

## Red2 怎样继续追

Red2 没重复 Red1，而是追 Blue1 自己说出来的薄弱点：

- instance-bound user identity 如何避免串租户；
- config/schema version 变化时 Retry/Replan 谁负责；
- Tool timeout 没 EffectReceipt 时实际上能否区分 failed/unknown；
- GraphRAG hard threshold/min-rank 是否制造新的 false promotion；
- Memory APPROVED 能否绕过 reviewer；
- ContextPack 构建后撤权是否产生 TOCTOU；
- Generic Host 已经能做普通 Agent 能力时 Zuno 还应该 Own 什么。

## Blue2 是否顶住

顶住了，而且主要靠简化而不是继续堆对象：

- 4 月 Tool path 只认历史边界，不冒充副作用安全；
- direct route 允许删除；
- GraphRAG 建议先只保留 fusion，再用 holdout/ablation 决定 seed/alias/path 是否值得；
- structured long-term Memory 没有 A/B 前可以默认关闭；
- Multi-Agent 继续晚于 Tool/Subgraph/worker；
- Generic Host + PostgreSQL Legal Backend 继续作为首版 baseline。

## Red Final

最终盲评：`PASS`。

高可信个人主线：

1. Tool/MCP concrete binding + config injection / hardening；
2. GraphRAG ranking regression + baseline-preserving fusion；
3. scoped Context/Memory V2 foundation + approved readback / provenance。

未建立：

- direct route 稳定收益；
- GraphRAG 普遍收益；
- long-term Memory 质量收益；
- Multi-Agent 必要性；
- 候选人本人在法院侧测试中的具体 Owner 深度。

没有触发真实性 Kill Switch。

# 真正的架构/文档缺陷

## 1. Memory / Context Owner 没讲到底

九模块 Matrix 明确：04 Runtime **不拥有 long-term Memory truth**；08 拥有 Security / lifecycle policy；跨模块 reference 又说 Memory/Context 是 Optional Provider Boundary。

但 structured memory 如果存在，仍需要回答：

```text
谁保存 record？
谁决定当前可召回？
谁能 review / approve？
谁处理 supersede / conflict / expiry / delete？
```

当前文档没有把这组事实完整落到一个明确边界。

建议不新增第十模块。默认：Provider 保存非权威 memory record；08 决定 recall/lifecycle/scope policy；01/04 只消费当前允许的 snapshot；02 继续拥有真正 Domain truth。如果这仍不值得，先删除 structured long-term Memory Target。

## 2. Tool 版本一致性有对象，但缺一条跨模块运行故事

05 有 CapabilityVersion / ProviderBinding / config version；06 有 ToolVersion；08 有 SecurityEpoch / CredentialVersion；04 有 resolved input-version set。

对象都在，但文档没有用一个非常具体的 failure 把它们连起来：

```text
Plan 按 schema/config v1 生成
→ dispatch 前变成 v2
→ 旧 Step 到底继续还是 Replan？
```

建议不新增对象，只把 04 的 input-version set 明确覆盖这些 refs，并增加 drift failure scenario。

## 3. Effect Reconcile 的 Target 正确，Current 文档低估了已确认缺陷

Current Evidence 已经证明：

- UNKNOWN effect 能耐久记录；
- replay 不会二次 dispatch；
- 但 restart replay 会把未完成 Reconciliation 的状态错误升级成 `completed`；
- Current 没有完整 remote-query / resolved writer / conclusive ReconciliationReceipt 收敛链。

所以 Current 不能只写“unknown → RECONCILE / no blind retry”。应该明确写：**unknown ledger 有了，最终 certainty convergence 还没闭环，而且 replay 已有已知 bug。**

## 4. Mandatory Audit 有 Target contract，但 Current 没有真正挡住 send

证据已经证明：Security 产生了 `MANDATORY_BEFORE_EFFECT` requirement，durable audit receipt 不存在时，provider dispatch 仍发生。

这是明确 Implementation Blocker，不是“以后再测”的 Unknown。06 / 08 的 Current/Gap 段应该直接写出来。

## 5. Context trace 容易被误读成 correctness

source ids / provenance 能证明来源和变换过程，不能证明：

- 来源是真的；
- 调用者有权看；
- compression 没丢关键法律限定。

Architecture 应加一条显式 invariant：`provenance != truth != authorization != semantic preservation`。

# 不是架构缺陷的地方

## GraphRAG

当前 Target 已经 measurement-gated，因此不是架构错误。问题是 Evidence：heuristic 太多、样本太小、缺 holdout/ablation。先实验，没收益就删。

## direct route

是历史工程故事，不值得升成 Target 架构。Current runtime 已经移除旧 direct execution path，不要为面试故事重新造 Router Service。

## Multi-Agent

本轮没有任何证据证明必须升级。继续 Tool → Subgraph → worker → Specialist → Persistent Multi-Agent 的复杂度阶梯。

## Generic Host + Legal Backend

subtraction test 后仍然成立。普通 session/workflow/MCP/RAG 尽量复用，Zuno Own 的应该是法律 Domain/Evidence/Effect/Security 的长期业务 Authority。

# 工作流自身的缺陷

- Red 框架总体有效，Red2 明显比 Red1 更强；后续应减少“历史题预设今天 Target object”的倾向。
- Blue 技术上很强，但回答偏长。下一轮应默认 20–60 秒口语，再让 Red 追深。
- 用户 checkpoint UX 已校准为：当前阶段只给当前 artifact 链接；Resume 可全文；100 Q/A 只摘少量代表内容。

# 建议审批顺序

先批准/拒绝四个 P0：

1. Memory Authority 收口；
2. Tool dependency-version 文档串联；
3. Effect Reconciliation Current 文档纠偏 + 实现计划；
4. Mandatory Audit Current 文档纠偏 + send-gate 实现计划。

GraphRAG 放到 Evidence 计划，不先改架构。Multi-Agent、direct route、九模块总体拓扑都先不动。
