# PHASE04：Services Thinning Directory Migration

> 状态：planned。目标 PR：Program3 PR4。

## 目标

让 `services/` 从“旧业务主线目录”变成临时兼容 facade，并把低风险小模块迁入六层目标目录。

## 迁移范围

优先迁移小而清楚的模块：

| 当前来源 | 目标位置 |
| --- | --- |
| `services/memory/` | `memory/` |
| `services/application/capabilities/` | `capability/` |
| `services/retrieval/bm25*` | `knowledge/retrieval/` |
| `services/rag` public facade | `knowledge/` |

高风险 orchestrator / fusion / graph runtime 只在本 phase 做 facade，不做大拆。

## 禁止范围

- 不一次性搬空 `services/`。
- 不改 retrieval 语义、GraphRAG 方法选择或 eval baseline。
- 不碰 `core/agents/general_agent.py`。

## 验收

- 新代码不得继续写入泛 `services/` 主线。
- `services/` 顶层只保留 compatibility facade 和暂缓迁移清单。
- 低风险模块从六层目标目录可直接导入。

## 验证命令

- `pytest -q tests/agent test/retrieval -p no:cacheprovider`
- `pytest -q tests/retrieval tests/graphrag tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
