# V4.1 ChatGPT External Architecture Review Template

ChatGPT 应独立读取 BASE Snapshot、Candidate SHA、Red Questions、Blue Answers/Decisions、Final
Part A、Final Part B、Part-A Explainability、Red Counter Review 和 Canonical Diff。

重点审查：Red 是否形成连续 Deep-Dive Chain 而不是随机百问、是否使用了采访校准但没有把答案
注入 Red、Blue 是否依赖代码当理由、Part A 是否可冷启动解释、术语是否压过概念、Part B 是否
支持 Part A、Candidate 是否没有越权进入 main、Main 是否等待 Verdict。`INTERVIEW_DEPTH`
和 `INTERVIEW_EXPLAINABILITY` 是问题质量/可解释性辅助信号，不得替代架构证据。

```yaml
round_id: <round-id>
reviewed_candidate_sha: <candidate-sha>
verdict: <ACCEPT|ACCEPT_WITH_DEBT|BLUE_REPAIR_REQUIRED|ROUND_REPLAY_REQUIRED|USER_GATE_REQUIRED>
blocking_findings: []
nonblocking_debt: []
required_blue_repairs: []
next_round_focus: []
review_timestamp: <ISO-8601>
```
