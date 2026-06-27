# PHASE05：大文件轻拆

## 目标

降低几个封面文件的维护成本，只拆结构，不改行为。

## 候选文件

- `src/backend/zuno/core/agents/general_agent.py`
- `src/backend/zuno/services/application/capabilities/__init__.py`
- `src/backend/zuno/services/retrieval/orchestrator.py`
- `src/backend/zuno/services/retrieval/fusion.py`

## 拆分方向

```text
general_agent.py -> runtime.py / context.py / post_turn.py / tool_bridge.py
capabilities/__init__.py -> contracts.py / registry.py / selector.py / policy.py / trace.py
orchestrator.py -> pipeline.py / adapters.py / result_shapes.py
fusion.py -> rrf.py / selection.py / graph_promotions.py
```

## 不做

- 不改行为语义。
- 不改 eval baseline。
- 不同时大搬多个模块。
- 不删除旧 public import，除非同一 phase 有迁移测试证明。

## 验收

- 每次只拆一个文件。
- 每次保留 public API。
- 每次跑对应 focused tests。
- full pytest 是否需要运行由变更范围决定；如果跳过，必须记录原因。

## 当前只读审计结论

本次只读审计只判断拆分边界，不执行 runtime 拆分。四个候选文件都不是“按行数平均切开”的问题；真正风险来自 public import surface、测试覆盖入口和 retrieval 语义耦合。PHASE05 后续如果继续执行，必须每次只拆一个文件，先保留旧 import 路径，再用 focused tests 证明行为未变。

本次线程内部使用的只读审计 agent：

- `GeneralAgent Audit Agent`：审计 `src/backend/zuno/core/agents/general_agent.py`。
- `Capability Audit Agent`：审计 `src/backend/zuno/services/application/capabilities/__init__.py`。
- `Retrieval Orchestrator Audit Agent`：审计 `src/backend/zuno/services/retrieval/orchestrator.py`。
- `Fusion Audit Agent`：审计 `src/backend/zuno/services/retrieval/fusion.py`。
- `Integration Review Agent`：汇总四份审计，确认最终排序、public API 风险、focused tests 和暂缓边界。

推荐顺序：

1. `src/backend/zuno/services/application/capabilities/__init__.py`
   - 理由：职责清楚，主要是 dataclass / enum contract、registry 和 selector；调用方少，已有 `__all__`，最适合先用 re-export 方式证明拆分手法。
2. `src/backend/zuno/core/agents/general_agent.py`
   - 理由：文件中已有较自然的 `context`、`post_turn_commit`、capability record、tool setup、MCP setup、knowledge tool、stream loop 边界；但它承载 Single GeneralAgent 主线，必须小步推进。
3. `src/backend/zuno/services/retrieval/orchestrator.py`
   - 理由：入口公开面主要是 `RetrievalOrchestrator` / adapters，但内部同时负责 query expansion、route planning、retriever fan-out、fusion、metadata、fallback / requery；可以拆 helper，但不能先动 `run()` 主流程。
4. `src/backend/zuno/services/retrieval/fusion.py`
   - 理由：虽然 public surface 只有 `RetrievalFusion`，但内部 guardrail、ranking 和 metadata mutation 高度耦合，且 2Wiki / GraphRAG precision 测试覆盖密集；本 program 内建议只做进一步审计或常量 / 纯 helper 提取，不优先执行完整拆分。

暂缓完整拆分：

- `fusion.py`：暂缓完整拆分。原因是 private helpers 之间共享 class constants、metadata key、ranking order 和 guardrail 顺序；拆错会改变 graph / baseline / requery promotion 语义。
- `orchestrator.py`：暂缓拆 `run()` / `_run_single_pass()` 主流程。可以先提取 `QueryExpanderAdapter`、result shape 或 trace helper，但不要把 route retry、standard floor、requery / graph contribution 判断拆成多个互相改状态的模块。

PHASE05 后续非可选接受线：

- `capabilities/__init__.py` 第一刀只提取 contracts，不同时移动 registry / selector。
- `general_agent.py` 第一刀只提取 `AgentConfig` / `StreamAgentState`，不拆 `astream()`、`prepare_context()` 语义、tool 顺序、middleware wiring 或 post-turn commit flow。
- `orchestrator.py` 第一刀只提取 adapter / pure helper，不拆 pipeline flow。
- `fusion.py` 完整拆分默认延期；如果本 program 内必须触碰，只允许 pure normalize / seed helper extraction，并保留 `RetrievalFusion` class wrapper 和 `merge()` 入口。

## 候选文件审计

### `src/backend/zuno/services/application/capabilities/__init__.py`

当前职责：

- 定义 capability foundation contract：`CapabilityType`、`CapabilityHealth`、permissions、cost、record、selection request / result / trace。
- 提供最小内存 registry：`CapabilityRegistry`。
- 提供当前 selector：`DynamicCapabilitySelector`，按任务 token、类型、health、permission 和数量限制选择 capability。

主要 import / export surface：

- import：`re`、`dataclasses`、`StrEnum`、`typing.Any` / `Iterable`。
- export：文件末尾 `__all__` 暴露 `CapabilityCost`、`CapabilityHealth`、`CapabilityPermissions`、`CapabilityRecord`、`CapabilityRegistry`、`CapabilitySelectionRequest`、`CapabilitySelectionResult`、`CapabilitySelectionTrace`、`CapabilityType`、`DynamicCapabilitySelector`。

调用方依赖：

- `src/backend/zuno/core/agents/general_agent.py` 导入 contract、registry、selector，并在 `prepare_context()` / `_available_capability_records()` / `_tool_capability_record()` 中使用。
- `src/backend/zuno/services/capability_registry.py` 导入 capability contract。
- `tests/agent/test_capability_system.py` 直接从 `zuno.services.application.capabilities` 导入 public symbols。

可拆边界：

- `contracts.py`：enum、permissions、cost、record、selection request / result / trace。
- `registry.py`：`CapabilityRegistry`。
- `selector.py`：`DynamicCapabilitySelector` 与 token / score helper。
- `__init__.py` 保留全部 re-export 和原 `__all__`。

不可拆或高风险边界：

- 不改 `CapabilityType` 的值字符串；它们进入 context metadata 和工具 schema 选择。
- 不改 `CapabilitySelectionResult.tool_schemas()` 的过滤类型集合。
- 不改 selector 排序和 `max(1, request.max_capabilities)` 行为。
- 拆到子模块会改变 dataclass / enum 的 `__module__`；当前未发现依赖，但这是 public surface 风险，后续实现时要用 focused tests 和 import smoke test 证明不影响调用方。

最小安全第一步：

- 新建 `contracts.py` 后只移动 dataclass / enum；`__init__.py` 从 `contracts.py` re-export，运行 capability focused tests。下一步再移动 registry / selector。

focused tests：

```powershell
pytest -q tests/agent/test_capability_system.py tests/agent/test_capability_registry.py -p no:cacheprovider
pytest -q tests/agent/test_generalagent_context_memory_runtime.py -p no:cacheprovider
```

是否建议本 program 内继续执行：

- 建议继续。它是 PHASE05 的最佳第一刀。

### `src/backend/zuno/core/agents/general_agent.py`

当前职责：

- 定义 LangChain / LangGraph streaming state：`StreamAgentState`。
- 定义 agent 配置 contract：`AgentConfig`。
- 定义 stream event middleware：`EmitEventAgentMiddleware`。
- 承载 Single GeneralAgent：初始化模型 / 工具 / skill / MCP / knowledge tool，准备 `ModelContextPacket`，执行 ReAct streaming loop，并在 memory enabled 时写回 raw event 和 task summary。

主要 import / export surface：

- import：LangChain / LangGraph runtime、LLM / MCP / Tool / Skill services、capability contracts、context contracts、knowledge query service、memory layer、MCP manager、user-defined tool runtime、model output helpers。
- direct public classes：`StreamAgentState`、`AgentConfig`、`EmitEventAgentMiddleware`、`GeneralAgent`。
- package public surface：`src/backend/zuno/core/agents/__init__.py` 和 `src/backend/zuno/core/__init__.py` 通过 lazy export 暴露上述类。

调用方依赖：

- `src/backend/zuno/api/services/completion.py` 直接导入 `AgentConfig` / `GeneralAgent`。
- `src/backend/zuno/api/v1/completion.py` 通过 lazy proxy 指向 `zuno.core.agents.general_agent` 的 `AgentConfig` / `GeneralAgent`。
- 多个 legacy / agent tests 直接导入或动态导入 `zuno.core.agents.general_agent`。
- 只读发现：`src/backend/zuno/services/autobuild/client.py` 仍导入 `ChatService`，但当前候选文件未定义该 symbol；PHASE05 不应借拆分顺手修这个 runtime 边界，主线程合并时可另行判断是否是历史残留。

可拆边界：

- `state.py`：`StreamAgentState`、`AgentConfig`。
- `middleware.py`：`EmitEventAgentMiddleware`。
- `context_runtime.py`：`prepare_context()`、`_available_capability_records()`、`_tool_capability_record()`、`_estimate_tokens()`。
- `post_turn.py`：`post_turn_commit()`、`_memory_scope()`。
- `knowledge_tool.py`：`setup_knowledge_tool()`、`_format_knowledge_query_result()`。
- `tool_setup.py` / `mcp_setup.py` / `skill_setup.py`：普通工具、MCP、skill tool wiring。
- `general_agent.py` 保留 `GeneralAgent` public class 和原 import path。

不可拆或高风险边界：

- `astream()` 与 `post_turn_commit()` 的 finally 关系不能拆散成可能跳过 memory commit 的路径。
- `prepare_context()` 产出的 `model_context_packet` / `context_trace` state key 是已证明 current foundation，不能改名。
- `setup_react_agent()` 的 tool 列表顺序、middleware、state schema 和 system prompt 直接影响 streaming 行为。
- public import path `zuno.core.agents.general_agent.AgentConfig` / `GeneralAgent` 必须继续有效。

最小安全第一步：

- 先只提取 `AgentConfig` / `StreamAgentState` 到 `state.py`，`general_agent.py` re-import，`core/agents/__init__.py` 和 `core/__init__.py` 不改 public names。确认直接 import 和 lazy export 都不变后，再考虑 middleware。

focused tests：

```powershell
pytest -q tests/agent/test_general_agent_project_query_runtime.py tests/agent/test_generalagent_context_memory_runtime.py tests/agent/test_completion_agent_config_compatibility.py -p no:cacheprovider
pytest -q tests/legacy_guards/test_phase11b_single_generalagent_cutover.py tests/legacy_guards/test_phase5_general_agent_real_runtime_flow.py tests/legacy_guards/test_phase5_domain_runtime_paths.py tests/legacy_guards/test_phase6_agent_graphrag_pluginization.py -p no:cacheprovider
```

是否建议本 program 内继续执行：

- 建议继续，但排在 capabilities 后，只做一到两个低风险 extract，不重写 runtime 主循环。

### `src/backend/zuno/services/retrieval/orchestrator.py`

当前职责：

- 定义 query rewrite adapter：`QueryExpanderAdapter`。
- 定义 `RetrievalOrchestrator`，串联 query processor、planner、vector / bm25 / graph / community retriever、fusion、fallback retry、proactive requery、standard floor、trace metadata 和 final response shape。
- 在 `run()` 中把 `_run_single_pass()` 的结果补成对上层稳定的 `metadata` / evidence / pipeline trace。

主要 import / export surface：

- import：GraphRetriever、retrieval mode normalize、stale index detector、CommunityGraphService、RetrievalFusion、retrieval models、RetrievalPlanner、retriever adapters、active trace id。
- public class：`QueryExpanderAdapter`、`RetrievalOrchestrator`。
- package public surface：`src/backend/zuno/services/retrieval/__init__.py` re-export `RetrievalOrchestrator`；`src/backend/zuno/services/graphrag/orchestrator.py` 兼容 re-export `QueryExpanderAdapter`、`RagRetrieverAdapter`、`RetrievalOrchestrator`。

调用方依赖：

- runtime：`src/backend/zuno/services/rag/handler.py`、`src/backend/zuno/services/graphrag/query_service.py`、`src/backend/zuno/services/graphrag/orchestrator.py`。
- tests：`tests/retrieval/test_*orchestrator*`、`tests/retrieval/test_standard_retrieval_composition.py`、`tests/retrieval/test_enhanced_*`、`tests/graphrag/test_2wiki_missed_opportunity_activation.py`、`tests/graphrag/test_graphrag_genealogy_path_precision.py`、多个 legacy / eval tests。

可拆边界：

- `query_expansion.py`：`QueryExpanderAdapter`。
- `result_shapes.py`：`_dict_to_document()`、`_serialize_documents()`、`_merge_document_content()`、`_evidence_bundle()`。
- `trace.py`：`_source_names_from_runs()`、`_pipeline_trace()` 和 metadata assembly 的纯 helper。
- `activation.py`：proactive requery / graph / enhanced / missed opportunity / floor preserved reason helpers。

不可拆或高风险边界：

- `run()` 与 `_run_single_pass()` 共享大量临时状态；不要先把二者拆成跨模块互相写 dict 的流程。
- `standard_floor_documents`、`enhanced_fallback_to_floor`、`graph_contributed`、`requery_contributed` 会影响 regression gates，不能改判断顺序。
- `domain_pack_id` 兼容字段仍在结果里保留受限历史语义，不能顺手删除。
- `src/backend/zuno/services/graphrag/orchestrator.py` 的兼容 re-export 必须保持。

最小安全第一步：

- 只提取 `QueryExpanderAdapter` 或纯 serialization helpers；`RetrievalOrchestrator` 保留在原文件并从新模块导入 helper。不要先动 `run()` / `_run_single_pass()` 主流程。

focused tests：

```powershell
pytest -q tests/retrieval/test_retrieval_orchestrator.py tests/retrieval/test_standard_retrieval_composition.py tests/retrieval/test_enhanced_retrieval_composition.py tests/retrieval/test_enhanced_standard_floor_invariance.py tests/retrieval/test_enhanced_requery_activation.py -p no:cacheprovider
pytest -q tests/graphrag/test_2wiki_missed_opportunity_activation.py tests/graphrag/test_graphrag_genealogy_path_precision.py tests/legacy_guards/test_project_query_compatibility_boundaries.py -p no:cacheprovider
```

是否建议本 program 内继续执行：

- 谨慎建议。只做 adapter / pure helper extraction；主流程拆分应等 capabilities 和 GeneralAgent 小拆通过后再判断。

### `src/backend/zuno/services/retrieval/fusion.py`

当前职责：

- 定义 `RetrievalFusion`，把 vector / bm25 / graph / requery documents dedupe、合并和排序。
- 维护 baseline-preserving strategy、graph promotion、comparison guardrail、bridge guardrail、genealogy guardrail、requery confidence / noise metadata。
- 输出 `FusionResult`，其 `fusion_metadata` 被 orchestrator 和 tests 用来解释 activation / fallback。

主要 import / export surface：

- import：`re`、`FusionResult`、`RetrievedDocument`。
- public class：`RetrievalFusion`。
- 隐式 public behavior：大量 private classmethod / staticmethod 修改 `RetrievedDocument.metadata`，虽然不是 public symbol，却是 tests 和 orchestrator metadata 的实际契约。

调用方依赖：

- runtime：`src/backend/zuno/services/retrieval/orchestrator.py`。
- tests：`tests/retrieval/test_retrieval_fusion.py`、`tests/retrieval/test_enhanced_requery_precision_gate.py`、`tests/graphrag/test_graphrag_baseline_preserving_fusion.py`、`test_graphrag_bridge_guardrail.py`、`test_graphrag_comparison_guardrail.py`、`test_graphrag_chain_aware_fusion.py`、`test_graphrag_genealogy_guardrail.py`、`test_graphrag_genealogy_path_precision.py` 等。

可拆边界：

- `fusion_constants.py`：阈值、cue 列表、stopwords、regex pattern；但要保持 `RetrievalFusion.<CONSTANT>` 可访问，避免破坏 private tests 或调试习惯。
- `fusion_entity.py`：`_normalize_entity()` 和 seed extraction helpers。
- `fusion_metadata.py`：comparison / bridge / genealogy / requery annotation helpers。
- `fusion_guardrails.py`：apply guardrail helpers。
- `fusion.py` 保留 `RetrievalFusion.merge()` 作为唯一 public entry。

不可拆或高风险边界：

- `_rank_key()`、metadata annotation、guardrail application 和 final `top_k` 截断顺序是行为核心，不应先拆。
- `RagHandler._local_priority_score()` 的 lazy import 避免顶层依赖；不能改成顶层 import。
- metadata key 是事实契约，例如 `genealogy_promotion_blocked_reason`、`bridge_promotion_blocked_reason`、`requery_confidence_score`、`final_top5_floor_preserved`。
- constants 如果迁移后不保留 class attribute，会破坏调试和潜在外部依赖。

最小安全第一步：

- 本 program 内不建议先拆完整 fusion。若必须做，只提取纯 seed / normalize helper，并保留 `RetrievalFusion` classmethod wrapper，让行为入口、constants 和 metadata order 不变。

focused tests：

```powershell
pytest -q tests/retrieval/test_retrieval_fusion.py tests/retrieval/test_enhanced_requery_precision_gate.py -p no:cacheprovider
pytest -q tests/graphrag/test_graphrag_baseline_preserving_fusion.py tests/graphrag/test_graphrag_bridge_guardrail.py tests/graphrag/test_graphrag_comparison_guardrail.py tests/graphrag/test_graphrag_chain_aware_fusion.py tests/graphrag/test_graphrag_genealogy_guardrail.py tests/graphrag/test_graphrag_genealogy_path_precision.py -p no:cacheprovider
```

是否建议本 program 内继续执行：

- 不建议作为前两步执行；建议暂缓完整拆分。等 capabilities、GeneralAgent 和 orchestrator 的低风险小拆通过后，再决定是否只提取 helper。
