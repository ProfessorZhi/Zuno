# PHASE10 Eval Observability LangSmith

status: pending

## 目标

建立 LangSmith-compatible Trace / Eval 平台化能力，同时保留本地 pytest/eval runner 作为 release gate。

本 phase 的目标不是把 LangSmith 当成唯一事实源，而是把 Zuno 内部 trace 先设计成 OTel-compatible span schema，再把 LangSmith 作为第一可视化 sink 和实验台。这样本地 JSONL / database、CI release gate、LangSmith experiment、Prometheus / OpenTelemetry-native backend 都能消费同一套事件结构，避免观测体系被单一 vendor 锁死。

目标链路：

```text
Runtime Event
  -> Zuno Span Builder
  -> OTel/LangSmith-compatible Span Schema
  -> Redaction + Sampling + Routing
  -> Local JSONL / DB Release Evidence
  -> LangSmith Trace / Dataset / Experiment
  -> Metrics Backend for latency, cost, error, security
```

## 步骤

- [ ] 定义 trace/span schema，覆盖 model、tool、retrieval、evidence、citation、approval、sandbox、latency、cost。
- [ ] 定义 primary keys：`trace_id`、`session_id`、`thread_id`、`task_id`、`turn_id`、`run_id`、`parent_run_id`、`run_type`。
- [ ] 建立 offline eval dataset：企业制度问答、合同审查、简历/JD、项目知识问答。
- [ ] 定义 dataset schema，包含 `case_id`、`scenario`、`workspace_fixture`、`input_query`、`expected_evidence_refs`、`expected_behavior`、`forbidden_tools`、`labels`。
- [ ] 建立 retrieval、answer、agent trajectory、security 和 business scenario 指标。
- [ ] 增加 LangSmith export adapter 或兼容 metadata builder。
- [ ] 增加 OTel-compatible span builder，字段覆盖 trace_id、session_id、workspace_id、run_id、parent_run_id、span_kind、inputs、outputs、redacted_payload、latency、cost、error、policy_decision。
- [ ] 增加 redaction / sampling / routing 层，保证 PII、商业机密和 secrets 不进入外部 sink。
- [ ] 建立 release baseline 文件，记录 dataset version、evaluator version、metric result、failure examples 和 commit sha。
- [ ] 将关键 eval 加入 CI regression gate。

## 输入 / 输出文件

输入：

- PHASE03 task/session/event contract。
- PHASE05 runtime spans。
- PHASE08 EvidenceBundle / citation fields。
- PHASE09 policy / sandbox / approval events。
- `tools/evals/zuno/**`
- `docs/evidence/eval-baselines.md`

输出：

- OTel / LangSmith-compatible span schema。
- local JSONL / DB release evidence schema。
- LangSmith export adapter。
- offline eval datasets。
- metric thresholds and CI gate config。

## Metric Threshold 初稿

| 指标 | 初始门槛 | 闭环方式 |
| --- | --- | --- |
| retrieval_recall_at_10 | >= 0.80 | offline retrieval eval。 |
| citation_coverage | >= 0.90 | evidence/citation eval。 |
| faithfulness | >= 0.85 | LLM-as-judge + evidence spot check。 |
| tool_selection_accuracy | >= 0.90 | trajectory eval。 |
| tool_success_rate | >= 0.95 | tool span status。 |
| approval_escape_count | == 0 | security eval hard gate。 |
| cross_workspace_leak_count | == 0 | security eval hard gate。 |
| secret_redaction_miss_count | == 0 | external sink / artifact check。 |
| prompt_injection_attack_pass_rate | >= 0.95 | simulated attack suite。 |

这些阈值是第一版 release gate 建议，不代表当前仓库已达标。若 dataset 太小，PHASE10 需要先标注 `experimental_threshold`，但仍必须记录 baseline。

## 外部 Sink 脱敏规则

- LangSmith export 只能发送 redacted inputs / outputs。
- PII、商业机密、raw document text、secrets、credential、unapproved tool args 不得进入外部 sink。
- 本地 JSONL / DB 是完整 release evidence 的事实源；LangSmith 是可视化和实验 sink。
- Online sampling 必须先通过 policy check，再决定是否外发。

## 验收

- 每次回答能追踪 query method、evidence、citation、tool trajectory 和安全事件。
- eval baseline 可版本化、可回归、可写进 release evidence。
- offline eval 覆盖 correctness、groundedness、retrieval relevance、citation coverage、tool selection、trajectory correctness。
- online monitoring 覆盖 latency、cost、fallback rate、approval rate、policy block rate、user feedback。
- LangSmith 中能看到同一次请求的 model、retrieval、tool、evidence、citation、approval 和 memory commit span。
- LangSmith 是 sink，不是唯一事实源。
- 没有 dataset version、evaluator version 和 metric result 的 release baseline，不能作为 PHASE12 closure 证据。

## 验证

```powershell
pytest -q tests/evals tools/evals/zuno -p no:cacheprovider
```
