# 运行时调用链

## 目的

概括当前后端调用方向，避免在重构时把依赖方向画反。

## 当前形态

```text
HTTP route
  -> application/service function
  -> core/runtime orchestration
  -> GeneralAgent prepare_context
  -> GeneralAgent ReAct loop
  -> post_turn_commit
  -> RuntimeTurnLedger foundation evidence
  -> retrieval, GraphRAG, context contracts, memory, capabilities, tools, storage
  -> response DTO
```

## 规则

下层不能反向依赖 API 层。

## 能力边界

Capability foundation 代码位于：

- `src/backend/zuno/services/application/capabilities/`

它定义 Knowledge、ActionTool、MCPTool、MCPResource、MCPPrompt 和 Skill capability 的当前 metadata contract，以及一个最小 selector。selector 可以只返回与任务相关的 schema。现有 API capability search service 保留旧 response key，同时暴露统一 metadata 字段。

GeneralAgent 还没有在每轮模型调用中完整注入 selected capabilities；完整产品级 capability orchestration 仍属于后续 product/runtime closure，不属于当前已经完成事实。

## GeneralAgent 上下文运行时

`GeneralAgent.astream()` 当前会准备 `ModelContextPacket`，把 `context_trace` 和 `model_context_packet` 放入单一 ReAct loop state，重置当前轮 knowledge/tool trace buffer，并在启用 memory 时写入 scoped raw event、task summary 和 runtime evidence payload。PHASE09 还会生成 `RuntimeTurnLedger`，汇总 context trace、capability trace、knowledge trace、tool trace events 和 post-turn memory event ids。

这只是已验证 foundation path。完整产品级 model-visible context injection、动态工具编排、生产级 memory retrieval / consolidation、API/SSE/DB/frontend trace 展示仍不是 Current。

详细目标行为见：

- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`

## GraphRAG 与知识路径

GraphRAG 是被选择的 Knowledge Capability，不是第二套聊天 runtime。当前查询路径应经过 `KnowledgeQueryService` 和 `GraphRAGQueryService`，并把 evidence、citation、trace 返回给上层。

Domain Pack 只在迁移 alias、DB compatibility、eval CLI compatibility、retirement/history tests 中保留受限含义，不是 active mainline。
