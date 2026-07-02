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

这次扩展后的产品范围包括三个闭环：

1. 知识库初始化：创建页要能设置知识库名称、说明、默认检索 profile、基础模型引用和是否需要图谱索引能力。
2. 知识库后续修改：维护页要能修改可变参数，并在保存前展示 impact preview，说明是立即生效、需要 reindex，还是需要 rebuild graph / full rebuild。
3. 文件生命周期：文件新增、删除、失败重试、后续替换 / 更新都要显式进入解析、索引、图谱状态链路，不能把文件变化静默当成索引已完成。

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

AgentChat 从已有知识库发起任务时，前端必须从知识库配置推导每个知识库的 product profile：

| 配置来源 | AgentChat profile | 说明 |
|---|---|---|
| `retrieval_settings.default_mode = rag` | `standard` | 标准检索，不要求图谱索引。 |
| `retrieval_settings.default_mode = rag_graph` | `deep` | 深度检索；GraphRAG 可用时可走图扩展，不可用时降级。 |
| `index_capability = rag_graph` 且 default mode 缺失 | `deep` | 兼容旧数据。 |
| 未知值、空值、损坏值 | `standard` | 保守降级，不暴露内部模式。 |

旧聊天兼容字段可以继续发送：

```json
{
  "knowledge_ids": ["ks_x"],
  "retrieval_mode": "rag_graph"
}
```

但 Workspace 产品路径必须同时发送 `knowledge_space_ids`、`knowledge_space_profiles` 和 `retrieval_profiles`。后端以显式 profile 为准。

## Knowledge Lifecycle Contract

### 初始化配置界面

创建知识库时只暴露少量不会让用户误解底层实现的参数：

| 用户可见项 | 写入字段 | 默认值 | 后续是否可改 | 影响 |
|---|---|---|---|---|
| 名称 / 说明 | `knowledge_name` / `knowledge_desc` | 用户输入 | 可改 | 立即生效。 |
| 默认检索 profile | `standard / deep` product mode | `standard` | 可改 | 查询默认值立即生效；从 `standard` 切到 `deep` 时如果启用图谱能力，需要提示图索引状态。 |
| 索引能力 | `index_capability = rag / rag_graph` | 随 profile 推导 | 可改 | 可能触发 text / graph / full rebuild。 |
| Embedding / VL Embedding / Rerank | `model_refs.*` | 空 | 可改 | Embedding 影响重建索引；Rerank 可立即影响查询。 |
| GraphRAG Project | `graphrag_project_id` | 空 | 可改 | 只在 `deep` 或 `rag_graph` 下有效；改变后需要图谱更新或社区报告更新。 |

创建页不要出现 `basic / local / global / drift`。这些只属于内部 GraphRAG query method。

### 后续修改界面

后续维护页按“直接保存”和“保存后需要动作”区分：

| 参数类别 | 可修改字段 | 保存策略 | 推荐动作 |
|---|---|---|---|
| 元数据 | 名称、说明 | 直接保存 | `save_only` |
| 查询默认值 | `retrieval_settings.default_mode`、`top_k`、`rerank_enabled`、`rerank_top_k`、`score_threshold`、`graph_hop_limit`、`max_paths_per_entity` | 先 preview，保存后下次查询生效 | `save_only` |
| Rerank 模型 | `model_refs.rerank_model_id` | 先 preview，保存后下次查询生效 | `save_only` |
| 分段参数 | `chunk_mode`、`chunk_size`、`overlap`、`separator`、清洗开关 | 必须 preview | `text_index` / `bm25_index` / `full_rebuild` |
| Embedding 模型 | `text_embedding_model_id`、`vl_embedding_model_id` | 必须 preview | `text_index` / `image_index` |
| 向量后端 | `vector_backend` | 必须 preview | `text_index` 或生产环境迁移动作 |
| 图谱抽取 | `entity_extraction_mode`、`relation_schema`、`entity_normalization`、`evidence_backlink`、`use_rag_entry_chunk` | 必须 preview | `graph_index` / `community_detection` / `full_rebuild` |
| 社区报告 | `community_report_prompt_id`、GraphRAG Project prompt/version | 必须 preview | `community_report` |

前端保存配置前应调用 `analyzeKnowledgeConfigImpactAPI` 或使用同等本地预览。保存后如果 preview 给出 rebuild 动作，界面必须明确提示“配置已保存，但已有文件需要重建索引 / 图谱”，不能只显示保存成功。

### 文件增删改

| 文件动作 | 当前接口 / 目标接口 | 状态语义 | 后续动作 |
|---|---|---|---|
| 新增文件 | `createKnowledgeFileAPI` | 创建 ingest task，进入 `parse_status / rag_index_status / graph_index_status` 状态链路 | 成功后轮询文件任务；失败可重试。 |
| 删除文件 | `deleteKnowledgeFileAPI` | 删除源文件记录及对应 RAG 文档索引 | 后续目标应记录 deletion event 和 graph stale。 |
| 失败重试 | `retryKnowledgeTaskAPI` | 复用 task payload，重进 queue / sync pipeline | UI 显示新 task 或继续打开任务详情。 |
| 批量重建 | `reindexKnowledgeFilesAPI` 或 action API | 所有文件重建索引 | 用于配置改动后的 text / image / BM25 rebuild。 |
| 替换 / 更新文件 | 近期目标：删除旧文件 + 新增新文件；Production Target：显式 replace API | 新版本进入重新 parse / index；旧版本 citation lineage 保留或标记 superseded | 需要 Change Impact Preview。 |

本轮不强行新增 replace API；先把契约写清，并确保当前新增、删除、重试、重建动作在 UI / API 类型中可见。

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

初始化页面必须把原来的“增强检索”收口成“深度检索”。“增强”可以作为说明词，但不再作为代码里的 product mode 枚举。

配置维护页面必须保留内部索引能力字段，因为这是构建参数；但聊天页和普通用户任务 payload 不能把 `rag_graph` 当成 product profile。

文件页面必须展示至少三个状态：

- 解析状态。
- RAG / 检索索引状态。
- 图谱索引状态。

如果文件是 PDF / Office / image / scanned 且外部 parser 或 OCR/VLM 未配置，界面必须能展示 blocked / failed / last_error，不允许显示成 indexed success。

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

## Implementation Steps

本轮按 TDD 小闭环推进：

1. 在 `tests/api/test_workspace_agentic_product_contract.py` 增加前端静态契约测试，先证明当前聊天页没有显式发送 `knowledge_space_profiles`，知识库创建页仍使用 `enhanced` product mode。
2. 在 `apps/web/src/utils/knowledge-config.ts` 增加 product profile 映射函数：内部 `rag/rag_graph` -> Workspace `standard/deep`。
3. 在 `apps/web/src/pages/workspace/defaultPage/defaultPage.vue` 让已有知识库选择进入 `knowledge_space_ids`、`knowledge_space_profiles` 和 `retrieval_profiles`。
4. 在 `apps/web/src/pages/knowledge/knowledge-create.vue` 把创建页 product mode 从 `standard/enhanced` 收口到 `standard/deep`，内部仍映射到 `rag/rag_graph`。
5. 运行 focused tests 和前端 typecheck；如果前端依赖缺失，只记录阻塞，不声称通过。

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
