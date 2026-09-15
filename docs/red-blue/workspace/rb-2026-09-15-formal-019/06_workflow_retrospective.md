# Controller Workflow Retrospective — rb-2026-09-15-formal-019

status: `COMPLETE`

## Resume Builder Reflection

这版模拟简历比之前更适合作为真实面试入口：六条都能被追到具体代码、失败或 Evidence，不再用九模块架构词替代个人贡献。

问题有两个：

1. `Workspace direct route` 独立成 bullet 后，Red 很容易把大量时间花在一个价值证据最弱的优化点上；它更适合并回 Tool/MCP 主线。
2. 项目简介里的“法院侧测试与 Pilot Validation”虽然事实边界正确，但仍可能让面试官把团队项目阶段误读成个人现场 Ownership。下一版应把句法改得更明确。

Resume Builder 总体通过，不需要重建整个简历框架。

## Red Thinking Framework Reflection

### 做得好的地方

Red1 没有平均扫六条 bullet，而是围绕 Tool/MCP、GraphRAG、Memory 三条高价值 Claim 建了深度，并且使用了：

- Subtraction Test；
- Ownership Interrupt；
- Evidence Escalation；
- Project → Fundamental Bridge。

Red2 也真正听了 Blue1。它没有重复问“GraphRAG 怎么做”“Memory scope 是什么”，而是抓住 Blue1 自己暴露的 handle：instance-bound user_id、call-time config drift、threshold 6、no holdout、scope equality、APPROVED bypass、TOCTOU、no A/B 等继续追。

Blind Evaluation 基本公平，没有把 canonical Zuno object name 当成隐藏标准答案。

### 可以改进的地方

1. Red1 有少量问题仍然带着“今天成熟架构应该有某对象”的倾向，例如直接把 idempotency/effect语义压进 4 月 Tool 历史。Blue能正确纠偏，但 Red Skill 可以更早区分：**历史能力边界问题** 与 **今天如果重做的问题**。
2. 100 题 Batch 本质是 Pressure Suite，不是真实 45 分钟面试。后续 Round Report 必须继续说明“通过这套题”不等于真实面试一定会覆盖所有 Thread。
3. Red2 的 100 题质量明显高于 Red1，说明 answer-driven generation 是正确方向。未来可考虑让 Red1 更少预先暗含成熟系统答案，把更多深度留给 Red2。

Red Skill 不需要大改，只建议强化“历史事实追问禁止预设 Target object”。

## Blue Candidate Framework Reflection

### 做得好的地方

`HISTORICAL_OWNERSHIP / CURRENT_SYSTEM / TARGET_DESIGN / OPEN_DESIGN / FUNDAMENTAL` 五分法在这轮非常有效。

Blue最成功的不是把问题都答成“有”，而是：

- 4 月没有 Effect closure，就直接说没有；
- GraphRAG 没有 holdout/ablation，就不包装；
- Memory 没有 durable concurrency，就把历史 foundation 与今天设计分开；
- Multi-Agent 没证据，就不升级。

这让 Red Final 最终没有触发真实性 Kill Switch。

### 可以改进的地方

Blue回答有时过于完整，像“提前把下一层追问也答了”。真实面试中这样可能显得背稿或抢话。

下一轮 Candidate Mode 可以加入一个简洁规则：

```text
默认 20–60 秒口头回答；
先回答一层；
只有 Red 已经追到 failure / transaction / version 时才展开第三层。
```

另外，Blue在开放设计题中较频繁使用今天 Target 的成熟术语。虽然事实边界没错，但真实口语可以先讲“谁拥有事实、怎么防重复、什么时候重算”，再报对象名。

## Blue Architecture Framework Reflection

架构诊断总体有效，原因是它没有把每个面试压力都升级成 Architecture Gap。

这轮正确地把：

- GraphRAG → `EVIDENCE_GAP`；
- direct route → `NO_ZUNO_CHANGE / EVIDENCE_GAP`；
- Multi-Agent → `NO_ZUNO_CHANGE`；
- Effect current failure → `IMPLEMENTATION_GAP`；
- Memory Authority owner 缺失 → 条件性的 `ARCHITECTURE_GAP`。

这符合“Owner / Authority / State / Recovery / Security / Build-Buy 因果不成立才升级架构”的高门槛。

需要加强的一点：当一个概念被定义成 `Optional Provider Boundary` 时，Reviewer 仍要追问“provider state 的 durable owner 是谁、谁决定 current/eligible、删除和冲突由谁裁决”。否则“非 Canonical”很容易被误解成“无需 Owner”。

## Harness Reflection

### Invariants

- Red1 = 100 questions：通过。
- Blue1 = 100 answers：通过。
- Red2 = blind Blue1 evaluation + exactly 100 new questions：通过。
- Blue2 = 100 answers：通过。
- Red2 未读取 Blue1 architecture notes：逻辑 allowlist 遵守。
- Red Final 未使用 Blue architecture notes：逻辑 allowlist 遵守。
- Blue2 Candidate 没有用 Blue1 sealed notes coaching：按阶段输入规则执行。
- Round base / skills pinned：通过。

`CHATGPT_AUTO` 仍然只能声称 `LOGICAL_GITHUB_MEDIATED`，不能声称物理上下文隔离；这一点必须继续保留。

### 用户交互

本轮暴露并修复了一个 UX 问题：之前 checkpoint 只说文件名或一次给太多链接。用户明确要求：

- 当前阶段只给当前 artifact 链接；
- Resume 可以全文展示；
- 100 题 / 100 答只摘少量代表内容；
- 不要每次把所有未来 artifact 链接铺满。

稳定 artifact URL contract 已在本轮外部 workflow fix 中建立，后续 Round 应按这个简洁交互执行。

### 本轮连续执行覆盖

原协议默认每个 batch checkpoint 暂停。本轮用户后来明确要求“自己跑完整个过程”，因此 Controller 可以在同一次用户授权下继续 Red2 → Blue2 → Final → Reflection → Report。这个 override 应记录为**用户显式连续执行授权**，不能变成以后默认跳过 checkpoint。

## Retrospective conclusion

本轮工作流整体有效。下一轮不需要再次大改 Harness。

真正需要进入改进清单的是：

1. Resume 合并 direct-route bullet；
2. Red Skill 进一步避免历史题预设 Target object；
3. Blue Candidate 默认更短、更口语；
4. Architecture docs 收口 Memory Authority、Tool dependency-version story、Current Effect/Audit negative evidence；
5. GraphRAG 先做实验，不先改架构。
