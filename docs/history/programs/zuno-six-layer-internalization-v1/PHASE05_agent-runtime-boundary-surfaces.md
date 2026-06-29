# PHASE05 Agent Runtime Boundary Surfaces

状态：completed

## 目标

在不重写 `GeneralAgent` 主循环的前提下，把 `src/backend/zuno/agent/` 的目标层入口拆成 runtime、context、post_turn、state、streaming 和 tool_bridge。

## 完成内容

- `runtime.py`：AgentConfig 和 GeneralAgent lazy 入口。
- `context.py`：AgentExecutionContext、ContextOrchestrator、ContextTrace、ModelContextPacket lazy 入口。
- `post_turn.py`：post-turn memory commit 所需的 memory thin surface 入口。
- `state.py`：StreamAgentState 入口。
- `streaming.py`：streaming middleware / state 入口。
- `tool_bridge.py`：agent 到 capability selector / registry 的桥接入口。

## 修复的结构 bug

`agent.context` 不能在导入时 eager load GraphRAG query service、retrieval、DB 或 vector runtime；本 phase 将 context 入口改为 lazy surface，避免 thin surface import 触发重 runtime 链路。

## 边界

本 phase 不改 `GeneralAgent` 执行顺序、LangGraph runtime、streaming 行为、tool execution 行为或旧 `zuno.core.agents` / `zuno.services.application.context` import path。

## 验证

```powershell
pytest -q tests/agent/test_agent_layer_surfaces.py -p no:cacheprovider
```
