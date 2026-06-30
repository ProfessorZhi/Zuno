# PHASE06 Capability ToolCard MCP System

Program: `zuno-eight-deliverables-full-realization-v1`
status: completed

## 为什么

工具层如果只是一堆函数注册，Agent 无法解释为什么选择某个工具、是否允许调用、成本如何、失败如何回退。ToolCard 和检索式 capability selection 是 Agentic RAG 的动作边界。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- ToolCard registry。
- Native BM25 capability/tool search。
- MCP adapters 和 tool policy。
- 权限、成本、health、fallback trace。

## 执行步骤

1. 审计 `src/backend/zuno/capability` 和 MCP server 目录。
2. 固定 ToolCard schema：name、description、input contract、owner、permissions、cost、health、evidence。
3. 实现 capability retrieval / selector / policy 的 focused path。
4. 将 tool selection result 写入 trace。
5. 增加 tests，证明工具选择可解释、权限可拦截、旧入口兼容。

## 验收

- ToolCard 不只是文档，有代码 contract 和测试。
- Native BM25 search 能返回可解释候选。
- MCP / local tools 共享 policy 和 trace 边界。
- 旧 public import path 继续通过 compatibility 保护。

## PR 边界

建议拆成 ToolCard contract PR、selector/search PR、MCP policy/trace PR。

## 完成摘要

PHASE06 已完成 Capability ToolCard / MCP foundation slice：

- `ToolCard`、`ToolCardRegistry`、`NativeBM25Retriever`、`NativeBM25SearchResult` 和 `CapabilityPolicyDecision` 已进入 capability physical owner，并通过 `zuno.capability.*` 薄入口暴露。
- `ToolCard` 将 full schema 降为可检索 compact metadata：name、aliases、type、schema summary、permissions、side effects、cost/latency hint、health、owner、source、tags、examples。
- `NativeBM25Retriever` 对 ToolCard searchable text 做本地 BM25 排序，并返回 matched terms 和 explainable score。
- `DynamicCapabilitySelector` 现在基于 ToolCard BM25 候选执行 type、health、permission、side effect、cost 和 relevance filter，并在 `CapabilitySelectionTrace` 中记录 candidate ToolCard ids、retrieval scores、filters、selected/rejected ids 和 injected schema ids。
- `CapabilityRegistryService.list_tool_cards()` 能从现有 tool / skill / MCP public dict 构造内部 ToolCard；现有 `/capability/search` response shape 不泄露 `tool_card` 字段。
- `GeneralAgent.prepare_context()` 将 capability selection trace 写入内部 capability context item metadata，不改变 SSE/API response shape，也不改变 runtime tool wiring。

## 验证证据

最小有效验证：

```powershell
pytest -q tests/agent/test_capability_system.py tests/agent/test_capability_registry.py tests/agent/test_capability_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py -p no:cacheprovider
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

- Architecture / Docs Agent：确认 PHASE06 可写为 Capability foundation slice；production-grade dynamic orchestration、optional vector capability search 和完整 ToolCard retrieval system 仍不得写成 Current。
- Runtime / Code Agent：确认实现边界应集中在 capability physical owner、registry service、facades 和 GeneralAgent 内部 trace metadata，不改变 API response shape、DB schema、frontend 或 MCP config。
- Verification Agent：确认 focused tests 应覆盖 ToolCard/BM25/policy trace、registry-to-ToolCard conversion、facade/static guards 和 GeneralAgent internal trace bridge；行为检查不放入 Agent system verifier。
- Integration Reviewer Agent：确认 PHASE06 PR 必须 stacked 到 PHASE05，保留 `zuno.services.application.capabilities`、`zuno.services.capability_registry`、`zuno.tools.*` 和 `zuno.mcp_servers.*` 兼容路径。

PHASE06 未禁用多 agent；所有子任务均为只读审计或主线程最终集成，未让多个 agent 同时修改同一批文件。

## 剩余风险

- 这是 foundation slice，不是生产级动态工具编排系统。
- Runtime 仍保持既有 LangChain tool wiring；PHASE06 只证明 selection trace 和 compact schema/card boundary，不宣称执行层已按 ToolCard policy 过滤所有实际工具。
- optional vector capability search、生产级 permission / health / cost filter、完整 fallback execution policy 和 product-facing trace UI 仍是 Target。
