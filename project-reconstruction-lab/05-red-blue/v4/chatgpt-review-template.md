# ChatGPT External Architecture Review Template

这不是 Codex 自评表。它是用户把 Round Artifact 交给独立 ChatGPT Architecture Auditor 时使用的
输入模板。

```yaml
round_id: <round-id>
base_sha: <snapshot-base-sha>
final_sha: <blue-final-sha>
verdict: <ACCEPT|ACCEPT_WITH_DEBT|BLUE_REPAIR_REQUIRED|ROUND_REPLAY_REQUIRED|USER_GATE_REQUIRED>
blocking_findings: []
nonblocking_debt: []
required_blue_repairs: []
next_round_focus: []
review_timestamp: <ISO-8601>
```

审查者必须独立读取 `canonical-snapshot.yaml`、Context Packet、Red/Blue Artifact、最终
Canonical Diff 和 Owner 文档。没有用户提供的这份 Verdict，不能把 Round 标为 `CLOSED`。
