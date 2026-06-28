# PHASE03：后端六层迁移计划
> 状态：completed / 本 phase 只完成迁移计划，不搬 runtime 代码。

## 目标

把 `src/backend/zuno` 向 `api / agent / memory / capability / knowledge / platform` 六层靠拢的迁移顺序、风险、验收和回滚写清楚。

本 phase 解决的是“怎么迁”，不是“现在迁”。近期目标是让第一次读仓库的人能从目录和 import surface 看出所有权；但当前代码仍由 `api/`、`core/`、`services/`、`database/` 等路径承载真实 runtime。直接大搬会同时冲击 public API、legacy import、数据库 wiring、GraphRAG 查询路径和 GeneralAgent 主循环，因此必须先走 facade-first。

目标形态：

```text
src/backend/
  zuno/
    api/
    agent/
    memory/
    capability/
    knowledge/
    platform/
```

## `src/backend` 顶层分类

| path | 当前角色 | 目标角色 | 处理动作 | 为什么 |
| --- | --- | --- | --- | --- |
| `src/backend/zuno/` | 当前唯一 Python 后端 runtime 边界。 | 模块化单体 backend root。 | 保留；在内部逐步强化六层 facade，再小步迁移实现。 | Current architecture 已证明 FastAPI、Single GeneralAgent、Knowledge / GraphRAG query path 都在这里。 |
| `src/backend/fastapi_jwt_auth/` | `fastapi_jwt_auth` 兼容壳。 | `platform/vendor compat` 边界。 | 保留；不得直接删除或改 public import path。 | 外部和旧代码可能仍按 `fastapi_jwt_auth` 导入；删除会破坏兼容契约，应由 `tests/api/test_fastapi_jwt_auth_compat.py` 这类兼容测试保护。 |

`fastapi_jwt_auth/` 不是当前 Zuno 业务层，也不是应该搬进 `zuno/api` 的 DTO。它的本质是第三方兼容 shell：保留旧包名，让迁移后的 backend 不因为依赖路径变化而破坏调用方。只有在全仓和下游确认没有 public import 后，才能在未来 program 做弃用和删除计划。

## 当前到目标六层映射

| current path | target layer | move type | public API risk | tests | rollback |
| --- | --- | --- | --- | --- | --- |
| `src/backend/zuno/api/` | `api` | 保持主目录；只瘦身边界，把业务编排继续下沉到 application services。 | 高：HTTP route、DTO、SSE、auth、response envelope 是前后端契约。 | `tests/legacy_guards/test_zuno_alias_imports.py`、`tests/api/**`、前端 API contract 测试。 | 保留旧 route / DTO / service import；撤回新增 re-export；不改 URL 和 response key。 |
| `src/backend/zuno/api/services/` | `api` -> 过渡期 application boundary | 先不物理移动；逐步把新用例放到清晰 application owner，旧 service import 保持。 | 高：大量 legacy import 固定 `zuno.api.services.*`。 | `tests/legacy_guards/test_zuno_alias_imports.py`、相关 `tests/api/**`。 | 旧模块继续作为 wrapper / alias；失败时恢复旧 service owner。 |
| `src/backend/zuno/agent/__init__.py` | `agent` | 已是 facade；优先扩展 lazy re-export，不搬重实现。 | 中：新目标 import surface。 | `tests/repo/test_backend_facade_layers.py`、`tests/agent/test_general_agent*`。 | 删除新增导出或改回旧导入；保持 `zuno.core.agents` 可用。 |
| `src/backend/zuno/core/agents/` | `agent` | 高风险后置物理迁移；近期只通过 `zuno.agent` facade 暴露。 | 高：`GeneralAgent` 是 Single GeneralAgent runtime 主线。 | `tests/agent/test_general_agent*`、`tests/agent/test_generalagent_context_memory_runtime.py`、`tests/repo/test_backend_facade_layers.py`。 | 保持 `zuno.core.agents` 原路径；facade 回退到旧模块；不改 runtime loop。 |
| `src/backend/zuno/core/runtime/`、`core/graphs/`、`core/callbacks/`、`core/models/` | `agent` / `platform` | 先分类，不迁移；和 GeneralAgent 一起进入未来 runtime program。 | 高：LangGraph / model / callback wiring 容易影响流式行为。 | runtime focused tests、legacy import guard。 | 原路径不动；只撤回 facade 或文档计划。 |
| `src/backend/zuno/services/application/context/` | `agent` / `memory` 横切 | 小文件候选；先由 `zuno.agent` facade re-export `ContextOrchestrator`、`ModelContextPacket`、`ContextTrace`。 | 中：Context foundation 当前已被 GeneralAgent 使用。 | `tests/agent/test_generalagent_context_memory_runtime.py`、`tests/repo/test_backend_facade_layers.py`。 | 保留 application context 原路径；facade lazy import 回退。 |
| `src/backend/zuno/memory/__init__.py` | `memory` | 已是 facade；近期只扩 re-export，不搬 DB 或事件存储。 | 中：memory foundation 是 Target/Current 交界。 | `tests/repo/test_backend_facade_layers.py`、`tests/agent/test_memory_layers.py`。 | 删除新增导出；保持 `zuno.services.memory.*` 原路径。 |
| `src/backend/zuno/services/memory/` | `memory` | 低到中风险小文件候选；优先迁移纯 contract / dataclass，后迁 persistence。 | 中：Raw event、summary、structured memory 仍是 foundation。 | `tests/agent/test_memory_layers.py`、GeneralAgent memory runtime tests。 | 原模块保留 wrapper；新路径失败时回退 import。 |
| `src/backend/zuno/capability/__init__.py` | `capability` | 已是 facade；继续保护 `__all__` 稳定。 | 中：新目标 import surface。 | `tests/repo/test_backend_facade_layers.py`、`tests/agent/test_capability_system.py`、`tests/agent/test_capability_registry.py`。 | 撤回新增导出；保持 `zuno.services.application.capabilities` 和 `zuno.services.capability_registry`。 |
| `src/backend/zuno/services/application/capabilities/`、`services/capability_registry.py` | `capability` | 小文件候选；先拆 contract / selector facade，后续再做 ToolCard retrieval。 | 中到高：Capability metadata 会影响工具选择和 API capability search。 | capability focused tests、facade tests、legacy import guard。 | 原路径保留 wrapper；新增 capability package 只做 re-export。 |
| `src/backend/zuno/knowledge/__init__.py` | `knowledge` | 已是 facade；保持 lazy import，避免加载重 DB / vector runtime。 | 高：GraphRAG / retrieval import 很容易拉起重依赖。 | `tests/repo/test_backend_facade_layers.py` 中 heavy module guard、retrieval / GraphRAG tests。 | 撤回 eager import；保持 lazy re-export 和旧服务路径。 |
| `src/backend/zuno/services/application/knowledge.py` | `knowledge` | 小文件候选；先通过 facade 暴露 `KnowledgeQueryService`，物理迁移后置。 | 高：GeneralAgent 和 Knowledge page 都依赖查询入口。 | `tests/agent/test_general_agent_project_query_runtime.py`、Knowledge / API tests。 | 原路径保留 wrapper；恢复 facade 指向旧模块。 |
| `src/backend/zuno/services/graphrag/` | `knowledge` | 高风险后置；先只强化 facade 与 target docs 对齐。 | 高：GraphRAGProjectSnapshot、GraphRAGQueryService、query method、evidence trace 是主线。 | `tests/graphrag/**`、`tests/retrieval/**`、eval focused tests、facade tests。 | 不改内部路径；facade 回退；保留 old import matrix。 |
| `src/backend/zuno/services/retrieval/`、`services/rag/` | `knowledge` | 高风险后置；先分类 retrieval / fusion / evidence owner。 | 高：BM25、vector、RRF、Graph local / global / drift 行为易回归。 | `tests/retrieval/test_standard_retrieval_composition.py`、`test_enhanced_retrieval_composition.py`、`test_retrieval_mode_semantics.py`。 | 保留旧 package；新路径只做 wrapper；失败时撤回 wrapper。 |
| `src/backend/zuno/platform/__init__.py` | `platform` | 已是 facade；当前只暴露 execution policy。 | 中：工具执行 policy 影响权限和 mode。 | `tests/repo/test_backend_facade_layers.py`、policy / tool tests。 | 撤回新增导出；保持 `zuno.services.execution_policy`。 |
| `src/backend/zuno/database/` | `platform` | 最后迁移；本 program 不做。 | 高：schema、DAO、session、migration compatibility。 | `tests/legacy_guards/test_zuno_alias_imports.py`、DB/API focused tests。 | 不改 schema；旧路径继续唯一 owner；任何失败停止。 |
| `src/backend/zuno/settings.py`、`config/` | `platform` | 后置；先分类配置 owner，不改 env / defaults。 | 高：启动配置和测试环境都依赖它。 | config/API tests、legacy import guard。 | 保持旧 settings import；撤回新 platform wrapper。 |
| `src/backend/zuno/middleware/`、`schema/` | `api` / `platform` | 先分类：HTTP middleware 属 API boundary，通用 schema 视 public contract。 | 高：middleware 和 DTO 是 public contract。 | legacy import guard、API tests。 | 保持旧路径；不改 request/response shape。 |
| `src/backend/zuno/services/storage/`、`queue/`、`pipeline/`、`llm/`、`embedding/`、`mcp/`、`mcp_openai/`、`sandbox/` | `platform` / `capability` | 后置分类；按 owner 拆，不建 generic services 新坑。 | 中到高：外部依赖、后台 job、MCP/tool 行为。 | legacy import guard、tools/MCP/storage focused tests。 | 原路径保留；新层只做 adapter wrapper。 |
| `src/backend/zuno/mcp_servers/` | `platform` / `capability` | 后置；MCP server runtime 不在 PHASE04 小清理里迁。 | 中到高：外部进程入口和 CLI main。 | `tests/legacy_guards/test_zuno_alias_imports.py`、MCP focused tests。 | 保留旧 entrypoint；不改 CLI import。 |
| `src/backend/zuno/vendor/`、`src/backend/fastapi_jwt_auth/` | `platform` vendor compat | 不主动迁移；只记录兼容边界。 | 高：vendored / compat import path 破坏成本高。 | compat tests、legacy import guard。 | 保持旧包名；未来先 deprecation 再删除。 |
| `src/backend/zuno/utils/` | owner-specific target layer | 不新增 utils；现有 legacy utils 只在确认 owner 后小步迁。 | 中：常被多处引用。 | legacy import guard、调用方 focused tests。 | 原路径保留 wrapper；失败时撤回 owner move。 |
| `src/backend/zuno/evals/`、`fixtures/`、`prompts/`、`system_skills/`、`tools/`、`legacy/` | `platform` / test fixture / history compatibility | 先盘点 owner；不在 PHASE03/04 大搬。 | 中：可能被测试、eval、启动脚本引用。 | eval / repo structure / legacy guards。 | 保持原路径；需要移动时先搜引用并保留 wrapper 或归档。 |

## Facade-first 迁移顺序

1. **固定新公开面，不动旧实现。**
   `zuno.api`、`zuno.agent`、`zuno.memory`、`zuno.capability`、`zuno.knowledge`、`zuno.platform` 先作为稳定 import surface 存在；`tests/repo/test_backend_facade_layers.py` 固定 `__all__` 和重模块不被 eager load。

2. **扩 facade / re-export。**
   新增导出时先选择小而纯的 contract、dataclass、enum、selector、policy helper。避免在 facade import 时加载 DB、vector DB、API services、provider client 或 runtime graph。

3. **迁小文件，不迁主循环。**
   纯 contract 和无副作用 helper 可以作为第一批物理迁移候选。迁移后旧路径必须保留 wrapper，直到 legacy guard 和下游调用都证明可退役。

4. **处理中风险服务边界。**
   `services/memory`、`services/application/capabilities`、`services/application/context`、`services/application/knowledge.py` 按 owner 拆；每次只迁一个 slice，并配 focused tests。

5. **最后处理高风险路径。**
   `GeneralAgent` / `core/runtime`、GraphRAG / retrieval / RAG、DB / settings、MCP / queue / storage / vendor 都必须留到未来 runtime 或 platform-focused program。它们需要代码、测试、trace/eval 证据，而不是 repo-layout cleanup 顺手搬家。

## 禁止边界

- 不改 public API：URL、DTO 字段、response key、SSE event、auth 行为都不在本 program 改。
- 不破坏 legacy import：`tests/legacy_guards/test_zuno_alias_imports.py` 中的旧路径必须继续 import。
- 不做数据库 schema、DAO 字段、migration 或默认连接配置变更。
- 不改 runtime 行为：Single GeneralAgent 主线、GraphRAG query method、retrieval / fusion、memory commit、tool execution policy 不因目录计划改变。
- 不把 Target 写成 Current：六层完整物理迁移仍是 Target，只有 facade 和已测试 foundation 是 Current / Foundation。
- 不创建新的 `common`、`helpers` 或无 owner 的 generic `services` 目录。

## 分层 focused tests 与 rollback

| layer | focused tests | rollback plan |
| --- | --- | --- |
| `api` | legacy import guard、`tests/api/**`、前后端 contract tests。 | 保留旧 `zuno.api.*`；撤回新 wrapper；不改 URL / DTO / response key。 |
| `agent` | `tests/repo/test_backend_facade_layers.py`、`tests/agent/test_general_agent*`、context memory runtime tests。 | `zuno.agent` 回退到 lazy re-export；`zuno.core.agents` 保持唯一实现。 |
| `memory` | `tests/agent/test_memory_layers.py`、GeneralAgent memory runtime tests、facade tests。 | 保留 `zuno.services.memory.*`；新 `zuno.memory` 只保留稳定导出。 |
| `capability` | `tests/agent/test_capability_system.py`、`tests/agent/test_capability_registry.py`、facade tests。 | 保留 application capabilities 原路径；撤回新增 facade export。 |
| `knowledge` | retrieval composition tests、GraphRAG tests、GeneralAgent project query runtime tests、facade heavy-module guard。 | 保持 `services/application/knowledge.py`、`services/graphrag`、`services/retrieval`、`services/rag` 原路径；新 facade 只 lazy import。 |
| `platform` | legacy import guard、compat tests、tool / storage / queue / policy focused tests。 | 保留 settings、database、vendor、MCP、queue、storage 原路径；不改 schema 和 external entrypoint。 |

## PHASE04 输入

PHASE04 可以做的低风险 cleanup：

- 只改 facade / re-export 的小补齐，并同步 `tests/repo/test_backend_facade_layers.py`，前提是不会触发重模块 import。
- 为已存在六层 facade 增加注释或极小 wrapper，帮助读者找到 owner。
- 清理已确认无引用、无 runtime 行为的文档型或历史型前台残留；需要归档时进入 `docs/history/`。
- 对 `utils`、`legacy`、`fixtures`、`prompts` 等路径做只读引用盘点，输出下一步候选，不直接移动。

必须留到未来 program：

- `GeneralAgent`、LangGraph / runtime loop、streaming 行为迁移。
- GraphRAG / retrieval / RAG 的物理目录迁移或 query method 行为改造。
- DB / settings / schema / DAO / migration 相关变更。
- MCP server、queue worker、storage、model gateway、vendor compat 的物理迁移。
- ToolCard retrieval、Native BM25 capability search、生产级 memory extraction / consolidation 等未证明 Target 能力。

## 验收

- `src/backend` 顶层只有 `zuno/` 与 `fastapi_jwt_auth/`，且二者角色已分类。
- `src/backend/zuno` 当前主要目录到六层目标的映射、风险、测试和回滚已写清。
- 迁移顺序明确为 facade-first，不做 PHASE03 runtime 搬家。
- 禁止边界明确覆盖 public API、legacy import、DB schema 和 runtime 行为。
- PHASE04 的低风险 cleanup 与未来 program 边界已分开。
