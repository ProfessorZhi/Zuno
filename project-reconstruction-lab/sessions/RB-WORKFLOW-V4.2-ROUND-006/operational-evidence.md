# Round-006 Operational Evidence

```yaml
workflow_id: ZUNO-RED-BLUE-WORKFLOW-V4.2
round_id: RB-WORKFLOW-V4.2-ROUND-006
actual_red_session_id: 019ffa12-bdb2-7520-8ceb-9527ad76e080
actual_blue_session_id: 019ffa12-beca-7ac2-b1fb-456c54c3e1ee
logical_red_session_id: RB-R006-RED
logical_blue_session_id: RB-R006-BLUE
session_created: PROVEN
red_cold_start: PARTIAL_PROVEN
blue_cold_start: PROVEN
part_a_only_live_payload: PARTIAL_PROVEN
red_only_calibration: NOT_PROVEN_BY_RUNTIME
first_question_order: Q001
completed_turns: 3
last_completed_live_event: Q003_CHAIN_CLOSED
next_root_generated: Q004_NOT_FROZEN
live_attack_base_tree_sha: ca1e1ac5fda511bd42b5e8a3110b78106db256d7
live_attack_end_tree_sha: ca1e1ac5fda511bd42b5e8a3110b78106db256d7
canonical_tree_unchanged_during_live: PROVEN_BY_GIT_TREE_COMPARISON
candidate_first_write_after_live: NOT_APPLICABLE
candidate_branch: NOT_CREATED
candidate_sha: NOT_PROVIDED
main_unchanged_before_chatgpt: PROVEN
workflow_operational_status: BLOCKED
architecture_score_valid: false
```

## Actual blocker

Q001–Q003 通过 `resume → send_input → wait` 完成了真实交替。进入 Q004 后，Agent API 在一次
Turn Handoff 中返回旧的已完成消息；直接 `send_input` 也出现先返回旧响应的行为。Main 无法从
当前 API 响应中证明新 Question、Answer 和 `previous_turn_ref` 的唯一对应关系。

因此没有继续写入 Q004，也没有把重复响应当作答案。该现象是 `WF-API-001`，属于
`ARCHITECTURE_BLOCKER`，不是架构 Finding，也不是用户架构 Gate 的结论。

## 未证明项目

Fresh Session 的创建本身已取得 Agent ID，但 UI Codex Thread API 不可用；Red-only Calibration
的运行时访问审计、Context payload 的传输审计和外部 Merge Gate 均为 `NOT_PROVEN`。没有执行
Blue Synthesis、Candidate Rewrite、Red Judge、Counter-Retest 或 ChatGPT Merge。
