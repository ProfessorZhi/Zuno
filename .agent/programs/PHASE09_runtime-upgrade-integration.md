# PHASE09 Runtime Upgrade Integration

Program: `zuno-eight-deliverables-full-realization-v1`
status: completed

## 为什么

前面各层如果不进入 GeneralAgent 主路径，只会成为漂亮 facade。最终必须形成清晰的 `prepare_context -> agent_loop -> post_turn_commit` 运行链，同时保持现有 API 和兼容边界。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- GeneralAgent runtime path 的小步集成。
- 六层目录的真实 owner 收口。
- Context、Capability、Knowledge、Trace、Memory 的协作边界。
- 必要时补前端只读 trace 展示，但不默认改产品 UI。

## 执行步骤

1. 先做只读 runtime call-chain 审计，确认最小集成点。
2. 将 mode router、context builder、tool selector、knowledge retrieval、trace hooks 接入同一 runtime contract。
3. 保留旧 import 和 API compatibility。
4. 增加 integration tests、runtime smoke tests、eval baseline comparison。
5. 同步 docs current/target 状态。

## 验收

- Runtime path 能展示完整 context、retrieval/tool、answer、post-turn evidence。
- 六层目录不是空壳，关键 owner 有测试。
- 不把未完成 feature 宣称为 Current。
- full focused test stack 通过。

## 完成证据

- `RuntimeTurnLedger` 已进入 `zuno.agent.post_turn` / `zuno.agent`，能汇总 `prepare_context -> capability_selection -> agent_loop -> knowledge_retrieval_trace -> tool_trace -> post_turn_commit` 的当前轮证据。
- `GeneralAgent.astream()` 每轮重置 knowledge/tool trace buffer，传递 `model_context_packet` / `context_trace` 到单一 ReAct loop，并在 finally 中生成 runtime turn ledger。
- `search_knowledge_base` 的 `KnowledgeQueryService` trace metadata 会写入当前轮 knowledge trace；tool middleware 可记录 pre/post tool trace event；`post_turn_commit()` 的 raw memory event payload 保留 capability / knowledge / tool trace。
- `GeneralAgent` 的 foundation contract imports 已收口到 `zuno.agent`、`zuno.capability`、`zuno.knowledge`、`zuno.memory` 目标层入口；`verify_module_boundaries.py` 和 focused tests 固定该边界。
- Multihop eval diagnostics 已能读取 `runtime_turn_ledger` 的 stage order、layers touched、post-turn memory event count、knowledge trace id 和 tool trace event count。
- 仍不属于 Current：生产级 Memory DB、成熟 memory retrieval / consolidation、完整动态工具编排、完整 model-visible context injection、API/SSE/DB/frontend 行为变化、frontend trace panel、产品级多 Agent runtime。

## PR 边界

必须按小切片推进，不做不可审查的大包重写。共享核心文件由主线程集中审查。
