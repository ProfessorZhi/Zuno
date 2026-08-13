# V4 Red Judge Prompt

你现在进入同一 Red Thread 的 Judge Phase，但只能读取新的 `red-judge-context.md`。
该 Packet 包含 Original Snapshot、100 个原始问题、Blue Answers、Blue Decisions、Architecture
Delta、Canonical Diff、Final Owner Docs 和 Escalations。不要使用未进入 Artifact 的旧聊天印象，
不要修改原始问题或 Canonical。

逐题同时检查：

1. 原问题是否被直接回答；
2. Decision 是否与回答一致；
3. 最终 Canonical 是否真实吸收了必要 Contract；
4. 是否仍存在 Owner/State/Failure/Recovery/Security/Tradeoff 空洞；
5. 是否只是 Implementation、Measurement 或 External Gap。

输出 `DEFENSE_SCORE`（0–5）和 `POST_SYNC_STATUS`。回答写了但 Canonical 没写入时，不得给
Closure 级高分。生成 `red-counter-review.md` 和 `scorecard.md` 后，状态只能进入
`WAITING_FOR_CHATGPT_REVIEW`。
