# PHASE05 Context Builder Memory System

Program: `zuno-eight-deliverables-full-realization-v1`
status: completed

## 为什么

Agentic RAG 的关键不是把更多文本塞进 prompt，而是建立可解释的 Context Pack 和记忆生命周期。没有 owner、source ids、压缩和抽取策略，增强模式会退化成不可验证的拼接。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- Context Pack contract。
- 短期状态、工作记忆、语义记忆、情节记忆、程序性记忆。
- Summary Compression、Structured Extraction、approval / review policy。

## 执行步骤

1. 审计 `src/backend/zuno/memory` 和现有 `platform/services/memory` owner。
2. 定义 Context Pack 数据边界、source ids、token budget 和 compression policy。
3. 实现 memory contracts、rendering、retrieval、review 的可测试路径。
4. 将 context builder 接入 Agent runtime 的准备阶段，但避免大规模重写主循环。
5. 增加 focused tests 和 docs/eval proof。

## 验收

- Context Pack 能说明每块上下文来源、类型、预算和使用方式。
- 五类记忆有边界和 owner，不混成单一 prompt 缓存。
- 记忆写入或抽取有 review / approval 规则。
- Current 文档只陈述已实现能力。

## PR 边界

建议拆成 contract PR、memory runtime PR、integration test PR。

## 完成摘要

PHASE05 已完成 Context Pack 和 memory lifecycle 的 foundation slice：

- `ContextPackPolicy`、`ModelContextPacket.context_policy`、`ContextTrace.source_event_ids_by_item` 和缺失 source id 检查已进入 context contract。
- `RecentWindowSelector` 为 system prompt、message 和 tool call/result 生成可复现 source id，并在 trace 中保留 policy 和来源覆盖率。
- Memory foundation 明确短期状态、工作记忆、语义记忆、情节记忆和程序性记忆；structured memory candidate 默认 pending review，approval/rejection decision 保留 reviewer、reason、layer 和 source ids。
- `GeneralAgent.prepare_context()` 只接入已验证的轻量路径：同 scope task summary 与 approved structured memory 可进入本轮 context；`post_turn_commit()` 继续只写 scoped raw event 和 task summary，不迁移 DB-backed memory，也不宣称成熟 memory extraction / retrieval / consolidation。
- `zuno.agent.*` 和 `zuno.memory.*` 薄入口已同步 export，旧 `zuno.services.memory.layers` 兼容路径继续保留。

## 验证证据

最小有效验证：

```powershell
pytest -q tests/agent/test_context_contracts.py tests/agent/test_context_orchestrator.py tests/agent/test_memory_layers.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py -p no:cacheprovider
```

完整 phase 收口还必须通过基础验证栈：

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## 多 agent 工作组结果

- Architecture / Docs Agent：确认 PHASE05 Current 只能写 foundation / thin entry / focused verified slice，生产级 Memory DB、成熟 retrieval / consolidation 和完整 PostTurnPipeline 仍是 Target。
- Runtime / Code Agent：确认最短实现路径是 context policy、source id trace、memory review taxonomy、facade exports 和 `GeneralAgent` 轻量 readback，不触碰 API response shape、DB schema 或 frontend。
- Verification Agent：确认 focused tests 覆盖 context contract、orchestrator、memory taxonomy、facade surfaces、GeneralAgent integration 和 static import guards。
- Integration Reviewer Agent：确认 PR 必须 stacked 到 PHASE04，保留 legacy import compatibility，不把内部 context trace 暴露到 `/completion` SSE。

PHASE05 未禁用多 agent；所有子任务均为只读审计或主线程最终集成，未让多个 agent 同时修改同一批文件。

## 剩余风险

- 这是 foundation slice，不是生产级 memory engine。
- `ContextOrchestrator` 只证明可解释 Context Pack contract，不等于 mature product context selection。
- Memory candidate promotion 仍是 contract / policy 级，完整 extraction、deduplication、conflict resolution 和 durable promotion 留给后续 runtime slice。
