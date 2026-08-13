# V4.2 Red Judge Prompt

`LIVE_ADAPTIVE` 的 Live Attack 完成后，你可以保留同一 Round 的 Red 对攻上下文；
`BATCH_ADVERSARIAL` 的 Judge 必须使用独立 Fresh Red Judge Session。两种 Profile 的正式 Judge 只能读取
Judge Packet：BASE Part A、完整 Q/A Ledger、Blue Architecture Decisions、Canonical Delta、
Final Part A、Final Part B 和 Candidate SHA。

按三遍执行：

1. 只读 Final Part A，标记 `CLEAR | PARTIAL | MISSING`；
2. 读取 Part B，核对叙事与 Contract；
3. 核对 Delta、Answer 和 Candidate。

每个高风险 Chain 至少提出一个 `Counter-Retest Question`。Retest 必须改变场景、约束或失败
条件，不能只是原问题换标点。Judge 不直接修复 Candidate，只记录 Finding、风险和证据。
