# V4 Workflow Bootstrap Review Package

## 基线

```text
BASE_SHA: bdaa029b0ae88a1a75a1b1be3efac22efcd30f3a
FINAL_SHA: RECORDED_IN_FINAL_HANDOFF
workflow: ZUNO-RED-BLUE-WORKFLOW-V4
```

`FINAL_SHA` 在最终提交完成后由交接报告记录；本文件不通过自引用方式伪造未来提交哈希。

## 本轮范围

本轮只改 Workflow、Governance、Lab Protocol、Session Contract、Prompt Template、Context
Packet、Verifier、Routing 和 Docs Tests。没有启动 Round-006，不修改 Business Runtime、Domain
或 Citation Implementation、Schema、Migration、UI、Dependencies、Production Infra、Facts 或 ADR。

## 双轨状态

| Track | 状态 | 说明 |
| --- | --- | --- |
| Architecture Evolution | `READY_FOR_FRESH_RED_THREAD` | Round-006 尚未开始，下一轮必须使用两个 Fresh Session |
| Implementation Evidence | `WAITING_FOR_RED_COUNTER_RETEST` | Wave-001 独立存在，不再阻塞 Architecture Round |

## V4 机制

- Red/Blue 使用不同、全新的 Session ID；双方从同一个 `canonical-snapshot.yaml` 开始。
- Red 只读、冻结 100 Questions，并在 Blue 修改后进入 Judge Phase。
- Blue 是唯一 Canonical Writer；不能修改 Red Questions、Facts、Red Score 或历史 Round。
- 线程之间只通过 Artifact 交接；没有可靠 Thread API 时只生成 Prompt/Manifest/Manual Launch，
  不伪造已启动 Session。
- Round 在外部 ChatGPT Verdict 前为 `WAITING_FOR_CHATGPT_REVIEW`，Codex/verifier 不代签。
- Architecture Review 与 Implementation Verification 并行；两者都不能把 Target 变成 Current。

## Round-006 readiness

```text
READY_FOR_FRESH_RED_THREAD
NOT_STARTED
red_session_id: NOT_CREATED
blue_session_id: NOT_CREATED
```

本 Bootstrap 不属于 Round-006，也没有生成 Round-006 目录、100 Questions 或 Canonical Diff。

## 外部审查要求

ChatGPT Auditor 应独立读取本包、V4 Protocol、Verifier Diff 和最终提交，判断 Workflow 是否
`ACCEPT`、`ACCEPT_WITH_DEBT`、`BLUE_REPAIR_REQUIRED`、`ROUND_REPLAY_REQUIRED` 或
`USER_GATE_REQUIRED`。在用户提供 Verdict 前，`chatgpt-verdict.md` 不得被填写为有效签名。

## 验证边界

完整 CI、真实 Codex Thread API、Round-006、真实 Runtime、法院 QA、Sandbox、HA 和 Production
均未在本轮执行。Production Readiness 保持 `NOT_ESTABLISHED`。
