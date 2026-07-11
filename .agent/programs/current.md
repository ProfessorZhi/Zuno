# 当前程序

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-unified-agent-runtime-closure-v1

## 当前状态

`.agent/programs/` 当前处于 no-active 等待态。最近完成并归档的 program 是：

- `docs/history/programs/zuno-unified-agent-runtime-closure-v1/`

## 最近完成结论

`zuno-unified-agent-runtime-closure-v1` 已完成 PHASE01-PHASE13 的本地 unified runtime implementation baseline，并以 `implementation_complete_measurement_blocked` 收口。

完成事实：

- Model Gateway、durable store、unified LangGraph service、Plan-and-Execute / ReAct step execution、Tool Control Plane、corrective Agentic GraphRAG / EvidenceLedger、Reflection / Replan / Grounded Synthesis、Memory / Reflexion reuse、Completion / Workspace API cutover 和真实 text PDF SourceSpan vertical slice 已完成本地 focused tests。
- PHASE13 修复 EnterpriseRAG paired benchmark 的 measured 语义：profile 不完整、provider 不可用或 sample-80 缺少 tracked set 时不会写成 `fixed_benchmark`。
- release gate 输出面可区分 `blocked_not_measured`、`prepared_not_measured` 和 `fixed_benchmark`。

质量边界：

```text
implementation available
measurement blocked
quality not yet proven
```

sample-8 已运行但 blocked，原因是本地 embedding profile runner 未配置。sample-80 仍因仓库没有 tracked fixed 80-case set 而 blocked。不得把本轮 implementation closure 写成 Agentic GraphRAG fixed benchmark measured pass。

## 当前前台文件

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/queued-programs/README.md`

## 下一步

只有用户明确打开新 program 后，才能从 PHASE01 建立新的 active program。新 program 应优先处理 EnterpriseRAG profile runner 配置 / sample-80 tracked set / release validation，而不是继续扩大架构层。

## 历史边界

- `zuno-enterprise-agentic-graphrag-production-suite-v1` 是历史 suite 输入，不是当前 active program。
- Program 3 Mega 归档仍在 `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`。
- 历史 Program 3 final alias surface closure 已完成，旧 public import path 只通过 `legacy_aliases.py` 注册兼容。
- `zuno-production-architecture-and-deliverables-completion-v1` 是一次性交付型成熟化 program。
- `zuno-production-document-ingestion-and-thread-foundation-v1` 是历史 ingestion foundation program。
- `zuno-enterprise-ingestion-async-infrastructure-v1` 是 Program 3 Mega 的历史 merged input。
- `zuno-target-architecture-runtime-full-implementation-v1` 归档在 `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`。
