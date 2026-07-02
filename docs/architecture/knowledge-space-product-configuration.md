# Knowledge Space Product Configuration

本文说明企业知识库在产品面如何配置和变更。它关注用户可见的知识库选择、检索 profile、文件状态和变更影响，不展开内部 GraphRAG 算法细节。

## Current Local Slice

当前已证明：

- `src/backend/zuno/api/dto/workspace.py` 提供 `KnowledgeSpaceConfig`、`WorkspaceRetrievalProfile`、`WorkspaceKnowledgeSelection`、`WorkspaceCitationRef` 和 `ChangeImpactPreview`。
- `src/backend/zuno/api/services/workspace_task_runtime.py` 接收 per-knowledge-space `standard` / `deep` retrieval profile，并把 retrieval plan、trace / eval / cost summary、artifact citation refs、file status 和 feedback 暴露给 workspace product API。
- `src/backend/zuno/api/v1/workspace.py` 暴露对应 workspace API。
- `apps/web/src/apis/workspace.ts` 同步 `WorkspaceRetrievalProfile = 'standard' | 'deep'`、retrieval profile map、citation refs 和 cost summary types。
- tests 证明 API schema、requested profile propagation、task summary、artifact citation refs、KnowledgeSpaceConfig serialization、ChangeImpactPreview 和 frontend type contract。

对应测试包括 `tests/api/test_workspace_agentic_product_contract.py`、`tests/api/test_workspace_task_runtime.py`、`tests/api/test_workspace_durable_ingest_runtime.py`、`tests/frontend/test_workspace_product_loop_types.py` 和 PHASE12 / PHASE13 eval tests。

## 产品配置对象

```text
KnowledgeSpaceConfig
  knowledge_space_id
  display_name
  retrieval_defaults
  ingestion_policy
  security_policy
  change_impact_preview

Workspace task request
  selected_knowledge_spaces
  retrieval_profiles: standard / deep
  task objective
```

用户选择标准检索 / 深度检索；Single Controller Agent 决定内部 BM25、vector、GraphRAG fallback、rerank、Skill 和 Tool 使用。

## Change Impact

ChangeImpactPreview 用来解释配置变化会触发什么：

- metadata-only：只改显示名、描述或标签。
- ACL refresh：权限或 sensitivity 变化。
- reparse：parser config、chunk policy、OCR 参数或 redaction policy 变化。
- vector rebuild：embedding policy 或 chunk 内容变化。
- graph rebuild：graph extraction policy 或 community report policy 变化。
- blocked dependency：需要外部 parser / OCR / VLM / index provider，但当前未配置。

## Launchable Prototype Target

- 产品面应能展示知识库文件状态、blocked reason、citation refs、task trace summary、eval/cost summary 和 artifact citation summary。
- PHASE14/15 文档与归档保留“标准检索 / 深度检索”的产品口径。
- 前端不是业务事实源；刷新或后端 service rehydrate 后仍能从后端查询 file / ingest / task / artifact / feedback。

## Production Scale Target

以下仍不是 Current：

- 完整创建 Wizard 和 Settings tabs。
- 多租户 admin / ops。
- production Desktop 打包 / e2e。
- 进程重启后的跨 worker 长任务恢复。
- 企业级知识库权限同步、审计报表和大规模变更预估。

## 不变量

- 不把 internal query mode 暴露成产品下拉。
- 不把 frontend type 写成业务事实源。
- 文件变更必须保留 document_version / index_manifest lineage，不能覆盖旧引用。
