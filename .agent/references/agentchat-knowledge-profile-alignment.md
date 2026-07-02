# AgentChat 知识库 Profile 对齐规格

## When To Use

当任务涉及 AgentChat 知识库选择、知识库创建 / 配置页、`standard / deep` 检索 profile、`rag / rag_graph` 索引能力、GraphRAG 内部 query method、前后端 Workspace 产品契约或可观测性展示时，先读本文件。

## Mental Model

Zuno 前台产品只给用户暴露两种知识库检索选择：

- `standard`：标准检索。面向普通事实问答、单文档定位、低成本回答。
- `deep`：深度检索。面向跨文档分析、多步检索、rerank、requery、GraphRAG 可用时的图扩展。

内部索引和 GraphRAG 运行时可以继续使用更细的技术概念：

- `rag`：标准 RAG 索引能力。
- `rag_graph`：RAG + GraphRAG 索引能力。
- `basic / local / global / drift`：历史或底层 GraphRAG query method，不是 AgentChat 产品级用户模式。

产品层和内部层必须通过显式映射连接，不能混用字段语义。

## Current Truth

- 后端 Workspace DTO 已定义 `WorkspaceRetrievalProfile = Literal["standard", "deep"]`。
- 后端 `WorkSpaceSimpleTask` 已支持 `knowledge_space_profiles` 和 `retrieval_profiles`。
- 前端 `apps/web/src/apis/workspace.ts` 已有同名类型和请求字段。
- 当前聊天页仍主要根据知识库旧配置生成 `retrieval_mode`，没有把所选知识库显式发送为 `knowledge_space_profiles`。
- 当前知识库创建 / 配置工具仍使用 `standard / enhanced`、`rag / rag_graph` 等混合语义；这些可以保留为内部配置，但前台文案和 AgentChat 产品契约必须收口到 `standard / deep`。

## Target Direction

本轮目标是做方案 B：前后端 AgentChat 知识库 profile 对齐，并同步知识库创建 / 配置页的产品语言。

目标不是接入真实外部 GraphRAG、OCR、RabbitMQ、Redis 或生产数据库；这些仍是 Production Scale Target。

## Product Contract

AgentChat 发送任务时必须显式携带：

```json
{
  "knowledge_space_ids": ["ks_x"],
  "knowledge_space_profiles": [
    {
      "knowledge_space_id": "ks_x",
      "retrieval_profile": "standard"
    }
  ]
}
```

多知识库时每个知识库都要有明确 profile。没有用户手动选择时，可以从知识库默认配置推导：

- `rag` -> `standard`
- `rag_graph` -> `deep`
- `standard` -> `standard`
- `deep` -> `deep`
- 未知值 -> `standard`

旧 `retrieval_mode` 可以继续传给兼容路径，但不能作为新产品主语义。

## UI Contract

用户界面只展示：

- 标准检索
- 深度检索
- 深度检索降级

不要在 AgentChat 产品界面展示 `basic / local / global / drift`。这些词只能出现在低层 GraphRAG 调试、内部 trace 或历史兼容上下文中。

知识库创建 / 配置页要区分两层：

- 产品默认检索 profile：`standard / deep`。
- 内部索引能力：`rag / rag_graph`。

当用户选择标准检索：

- 默认 profile 是 `standard`。
- 内部索引能力默认 `rag`。

当用户选择深度检索：

- 默认 profile 是 `deep`。
- 内部索引能力默认 `rag_graph`。

## Observability Contract

Agent run 的前端进度、trace summary 或后续可观测性模块至少要能显示：

- requested profile
- effective profile
- fallback reason
- retrievers used
- evidence count
- citation coverage
- estimated cost
- latency
- security verdict

如果请求是 `deep`，但图索引或外部图服务不可用，必须显示 `deep_without_graph` 或等价降级原因，不能把降级伪装成完整 GraphRAG 成功。

## Allowed Changes

- `apps/web/src/apis/workspace.ts`
- `apps/web/src/apis/knowledge.ts`
- `apps/web/src/utils/knowledge-config.ts`
- `apps/web/src/utils/retrieval.ts`
- `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`
- `apps/web/src/pages/knowledge/*`
- `tests/api/test_workspace_agentic_product_contract.py`
- 必要的前端静态契约测试或 repo tests

## Forbidden Changes

- 不修改后端 `WorkspaceRetrievalProfile` 的用户可见枚举为 `basic / local / global / drift`。
- 不把 `rag_graph` 写成用户必须理解的 AgentChat 模式。
- 不把 GraphRAG target-blocked / fallback 写成 Current success。
- 不为这次 UI / 契约对齐引入真实外部 parser、queue、Redis、MinIO、external index。
- 不重写整个知识库管理页面的信息架构；本轮只收口 profile 语义和 payload。

## Focused Tests

最低验证：

```powershell
pytest -q tests/api/test_workspace_agentic_product_contract.py -p no:cacheprovider
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

如果修改前端代码，优先运行现有前端 lint / typecheck；如果依赖缺失导致不能运行，必须记录阻塞原因，不声称通过。

## Common Failure Patterns

- 只改 `workspace.ts` 类型，不改聊天页 payload，导致测试能过但真实 UI 没对齐。
- 把 `rag_graph` 翻译成“深度检索”后又传给后端 Workspace 产品接口，导致后端 profile 合约失效。
- 在知识库配置页删除旧 `rag / rag_graph` 字段，破坏已有索引配置兼容。
- 在可观测性里只展示“深度检索”，不展示 `effective_profile` 和 fallback reason，掩盖 `deep_without_graph`。

## Docs Sync

如果本轮只改前端和 API 契约测试，通常不需要修改正式 `docs/architecture/architecture.md`。如果新增或重定义产品层 profile 语义，必须检查：

- `docs/architecture/knowledge-space-product-configuration.md`
- `docs/architecture/agentic-retrieval-planner.md`
- `docs/architecture/production-readiness.md`
- `.agent/references/code-map.md`
- `.agent/references/current-program.md`

