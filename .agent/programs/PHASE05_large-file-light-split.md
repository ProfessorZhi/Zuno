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
