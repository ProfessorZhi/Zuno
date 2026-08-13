# V4.1 Red Judge Prompt

你仍使用独立的 Red Session，但只读取 `red-judge-context.md`。对每个 Conceptual Question：

1. 第一遍只读取 Final Part A，判断 `PART_A_DEFENSE: CLEAR | PARTIAL | MISSING`；
2. 第二遍读取 Part B，检查概念与精确 Contract 是否一致；
3. 最后核对 Blue Answer、Decision、Canonical Diff 和 Candidate SHA。

对每条 Deep-Dive Attack Chain 评分 `INTERVIEW_DEPTH: 0–5`，只衡量连续追问是否从 Claim 打到
必要性、边界、失败、替代、成本和反转；它不进入 Architecture Defense Score。Part-A first pass
之后再记录 `INTERVIEW_EXPLAINABILITY: CLEAR | DENSE | TERM_DEPENDENT | MISSING`。如果 Fresh
Blue 只能用大量 Zuno-specific English Terms 才能讲清普通概念，记录 `TERM_DEPENDENT` 并要求
Part A Rewrite。

不要读业务代码来替 Part A 补洞。回答写得很长、术语很多或代码当前如此，都不能单独提高分数。
如果核心 P0/P1 概念仍为 `MISSING`，记录 `BLUE_REPAIR_REQUIRED`。输出
`part-a-explainability.md`、`red-counter-review.md` 和 `scorecard.md`；Human Writing 只能
标记 `PASS | WARNING | FAIL` 供人工审查，不能由 verifier 自动签 PASS。
