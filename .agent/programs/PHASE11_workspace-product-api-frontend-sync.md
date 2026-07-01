# PHASE11 Workspace Product API Frontend Sync

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE11_workspace-product-api-frontend-sync
status: pending

## 目标

把后端新增的 knowledge retrieval profile、planning summary、trace / eval / cost summary、artifact citation info 和 capability / skill snapshot 同步到 Workspace Product API 与前端 API types 的最小兼容层。

## 范围

- request contract 支持每个 knowledge space 的标准检索 / 深度检索。
- task snapshot 能返回 plan / reflection / replan / trace summary。
- artifact response 能返回 citation info。
- frontend API type 最小同步，避免 schema 漂移。
- 保持现有 `/workspace/file`、`/workspace/ingest` 和 task runtime compatibility。

## Knowledge Space Product Contract

PHASE11 不只同步后端字段，还必须把知识库创建、配置、文件状态和配置变更影响预览纳入产品契约。UI 大改可以后置，但 API / type / plan 必须让后续 UI 有明确落点。

### KnowledgeSpaceConfig

```text
KnowledgeSpaceConfig
  name
  description
  workspace_id
  acl_scope
  default_sensitivity
  index_capabilities
  parser_config
  chunk_config
  embedding_config
  graph_config
  ocr_vlm_config
  retrieval_defaults
  security_policy
```

`index_capabilities` 必须区分：

- 基础索引：必选，包含 BM25 / vector / source span / citation lineage。
- 图谱增强索引：可选，包含 entity / relation / community / graph local/global/drift。
- OCR / 多模态解析：可选，只是 worker target；缺 provider 时显示 dependency probe 和 blocked diagnostics。

`parser_config` / `ocr_vlm_config` 必须能表达 PDF / Office parser provider target、dependency probe、timeout、privacy gate、budget gate、review_required 和 fallback policy。`retrieval_defaults` 只暴露标准检索 / 深度检索，不暴露 basic / local / global / drift 作为主产品模式。

### 创建知识库 UI

创建时使用 Wizard 简化版，减少配置负担：

1. 基础信息：名称、描述、workspace、可见范围、默认安全标签。
2. 上传文件：本地文件、附件、未来同步源占位。
3. 索引能力：基础索引必选，图谱增强索引可选，OCR / 多模态解析可选。
4. 默认检索策略：标准检索 / 深度检索。

### 知识库详情页

后续 Settings 使用完整配置，建议 tabs：

- 概览：文件数、已索引数、失败数、blocked 数、默认检索策略、图谱和 OCR 状态。
- 文件：file_id、filename、mime_type、size_bytes、source_sha256、storage_uri 或 source_ref、parse_status、index_status、parser_id、document_version_id、index_job_id、blocked_reason、dependency_probe、retry_count、last_error、retry / cancel / reparse / reindex / rebuild_graph / view_diagnostics actions。
- 索引配置：基础索引、chunk policy、embedding、reranker、parser config。
- 解析任务：parse job、index job、worker status、retries、dead letter、diagnostics。
- 图谱状态：graph ready、entity count、community count、last rebuild、rebuild action。
- 评测与质量：citation coverage、unsupported claim、avg latency、avg cost、standard vs deep 对比。
- 权限与安全：ACL、sensitivity、retrieval gate stats、DLP stats。
- 高级设置：provider boundary、budget、adapter probe 和 target-blocked evidence。

### Change Impact Preview

保存配置前必须能预览影响：

| 修改类型 | 触发动作 | 说明 |
|---|---|---|
| name / description | metadata-only | 不重建索引。 |
| ACL / sensitivity | ACL refresh | 更新 metadata 和 index chunk ACL，不必重 parse。 |
| 上传 / 删除文件 | incremental parse / tombstone | 新文件进入 parse / index；删除生成 tombstone 或 hide。 |
| parser_config / chunk_config | reparse + reindex | 生成新 document_version，旧引用继续指向旧版本。 |
| enable graph | graph rebuild | 基于已有 Document IR / blocks 构建 graph。 |
| disable graph | deep_without_graph fallback | 禁用 graph retrieval，保留旧 graph artifact 或 tombstone。 |
| enable OCR / VLM | OCR / VLM worker job | 生成 derived blocks，再 reindex affected version。 |
| embedding model | vector rebuild | 不重 parse，只重建 vector index。 |
| reranker | query-time only | 不重建 index，只影响查询时 rerank。 |
| PDF / Office parser provider target | dependency probe / reparse target | provider 未配置时不启动真实解析，只更新 blocked 可见性和 retry action。 |
| ACL / sensitivity | ACL refresh | 更新 source object、document block、index chunk 和 retrieval gate metadata，不重 parse。 |

用户可见文案必须说明预计影响，例如需要 reparse 的文档数、rebuild chunks 数、是否影响旧 artifact 引用和预计耗时。

Change Impact Preview 必须额外覆盖：

- 上传新文件 -> incremental parse / index。
- 删除文件 -> tombstone / hide / index delete。
- parser_config 改动 -> reparse + reindex。
- chunk_config 改动 -> rechunk + reindex。
- embedding model 改动 -> vector rebuild。
- enable graph -> graph rebuild。
- disable graph -> deep_without_graph fallback。
- enable OCR / VLM -> OCR / VLM jobs for image / scanned / PDF pages。
- ACL / sensitivity 改动 -> ACL refresh。

保存前必须展示受影响文件数、受影响 chunks 数、是否影响旧 artifact 引用、预计耗时、是否需要外部 provider、是否会产生 blocked / dependency_probe 状态。

## 目标架构拼接点

本 phase 拼到 Product Surface。用户看见的是 AgentChat、知识库选择、标准检索 / 深度检索、artifact、trace 和 feedback；后端实现细节不能泄露成复杂模式选择：

- Knowledge selection 传递 per-knowledge-space retrieval profile。
- Task snapshot 展示 plan / reflection / replan 摘要，而不是内部全部 trace。
- Artifact response 保留 citation refs。
- Feedback 能回到 eval / memory review。
- Frontend API type 与 backend DTO 保持最小一致。
- 文件级 parse / index 状态和 dependency probe 给用户可见，不暴露外部 worker 技术细节。

本 phase 是目标架构的产品入口闭环，不负责 UI 大改，但必须保证 API 不漂移。

## 并行开发可行性

本 phase 由 Coordinator + Workstream H 处理，因为它触碰共享 API 和前端类型。

可并行：

- 后端 response schema test 与 frontend type sync 可分工。
- Artifact citation response 与 task trace summary 可分工。

不可并行：

- 多个 agent 同时改 workspace public API。
- 不经 Coordinator 改 `workspace_task_runtime.py`。
- 把 standard/deep 变成 basic/local/global/drift 下拉。

## 详细执行卡

- 输入依赖：PHASE02 API DTO contract、PHASE04 retrieval profile、PHASE09 planner summary、PHASE13 trace/eval summary target fields。
- 主要交付物：workspace API schema alignment、KnowledgeSpaceConfig、KnowledgeSpaceSettings UI/API plan、Change Impact Preview、file-level status fields、parser provider dependency probe fields、standard/deep request field、task snapshot plan/eval/trace summary、artifact citation fields、minimal frontend API type sync。
- 可并行工作包：backend schema tests、frontend API type update、compatibility docs 可拆；public response shape 由 Coordinator 统一审查。
- Coordinator 锁点：`src/backend/zuno/schema/workspace.py`、`workspace_task_runtime.py`、`apps/web/src/apis/workspace.ts`。
- 下游交接：PHASE12 使用同一 API path 做 E2E；PHASE14 文档记录产品层只暴露标准/深度检索；PHASE15 verifier 确保 entrypoint 不漂移。
- PR / commit 建议：`feat(api): expose knowledge retrieval profile and trace summaries` 与 `test(api): keep workspace runtime compatibility`。

## 禁止范围

- 不做大型 UI 改版。
- 不破坏现有 public API。
- 不把用户暴露给 basic / local / global / drift 技术模式。

## 验收闸门

- API response schema tests 通过。
- workspace task runtime compatibility tests 通过。
- frontend API type 或 existing frontend tests 通过。
- frontend API types 包含 retrieval profile、knowledge config summary、file status 和 change impact preview。
- 文件列表字段包含 file_id、filename、mime_type、size_bytes、source_sha256、storage_uri/source_ref、parse_status、index_status、parser_id、document_version_id、index_job_id、blocked_reason、dependency_probe、retry_count、last_error 和 retry/cancel/reparse/reindex/rebuild_graph/view_diagnostics actions。
- KnowledgeSpaceConfig 区分创建 Wizard 简化版和 Settings 完整版，但底层 schema 一致。
- 配置变更能明确 metadata-only、ACL refresh、reparse、vector rebuild、graph rebuild、OCR/VLM job。
- 标准检索 / 深度检索字段能进入后端 retrieval plan。
- 普通用户界面不得暴露 basic / local / global / drift 为主选择。

## 验证命令

```powershell
git diff --check
pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/api -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/api/v1/workspace.py`
- `src/backend/zuno/api/dto/**`
- `apps/web/src/apis/workspace.ts`
- `tests/api/**`

## 需要修改的文件

- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/api/v1/workspace.py`
- `src/backend/zuno/api/dto/**`
- `apps/web/src/apis/workspace.ts`
- `tests/api/**`

## 执行拆解

1. 写 API schema compatibility test。
2. 写 requested knowledge profile test。
3. 写 task trace summary response test。
4. 写 artifact citation info response test。
5. 最小同步 frontend API type。
6. 运行 existing API tests。

## 多 agent 分工

- Coordinator owner for shared API files。
- Workstream H executes scoped API/frontend changes under Coordinator review。
- Workstream F/B/G provide contract expectations。

## 需要返回的证据

- API request / response examples。
- compatibility tests。
- frontend type diff。
- no breaking change summary。

## 停止条件

- 需要 breaking public API change 且没有兼容策略。
- frontend sync 变成大规模 UI 改版。
- retrieval profile 被暴露成 basic/local/global/drift 技术选择。
