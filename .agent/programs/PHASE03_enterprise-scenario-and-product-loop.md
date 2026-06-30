# PHASE03 Enterprise Scenario And Product Loop

status: completed

## 目标

把 Zuno 的主场景从“普通 RAG 问答”固定为“企业私有知识库与多功能 Agent 助手”，并定义 workspace、task/session、upload、artifact、event stream 和 trace panel 的产品闭环。

## 步骤

- [x] 定义 Workspace、Knowledge Space、Session、Task、Uploaded File、Artifact、Trace Event、Citation 和 Feedback 的 contract。
- [x] 为每个产品对象写字段表：`id`、`workspace_id`、`owner`、`status`、`policy_scope`、`trace_id`、`created_at`、`updated_at`、`retention_policy`。
- [x] 定义 upload -> parse/index -> ask -> event stream -> answer/report -> artifact download -> feedback/eval 的链路。
- [x] 固定第一版事件流协议：优先 SSE；WebSocket 作为 Target 后续增强，除非本 phase 明确实现双向审批。
- [x] 定义 task 状态机：`created -> context_building -> planning -> running -> approval_waiting -> resuming -> finalizing -> completed | failed | cancelled`。
- [x] 定义 runtime request envelope，包含 `workspace_id`、`session_id`、`user_id`、`goal`、`product_mode`、`knowledge_space_ids`、`uploaded_file_ids`、`approval_mode`、`budget` 和 `output_contract`。
- [x] 明确企业知识库、HR 简历库、合同/审查报告三个首批场景。
- [x] 更新 API / frontend contract tests。
- [x] 更新架构文档中的 Scenarios View。

## 完成证据

- 后端 `zuno.schema.workspace` 已提供 Workspace、KnowledgeSpace、Session、Task、UploadedFile、Artifact、TraceEvent、Citation 和 Feedback contract。
- `WorkSpaceSimpleTask` 已包含 PHASE03 runtime request envelope 字段，且保持旧 workspace chat endpoint 行为不变。
- 前端 `apps/web/src/apis/workspace.ts` 已同步 product loop 类型，并保留 task_id / trace_id / artifact_id / citation_ids 的 stream normalizer 透传。
- `docs/architecture/architecture.md` 已更新核心对象模型、request envelope 示例和 Scenarios View。

## 产品对象契约

| 对象 | 必填字段 | 状态 / 行为 |
| --- | --- | --- |
| `Workspace` | workspace_id、owner、members、policy_profile、retention_policy。 | 工作空间是权限、存储、trace 和知识库隔离边界。 |
| `KnowledgeSpace` | knowledge_space_id、workspace_id、graph_project_id、index_version、acl_policy。 | 文档集合、索引版本和 GraphRAG project 的边界。 |
| `Session` | session_id、workspace_id、user_id、thread_id、active_task_id。 | 用户交互上下文，不等同于单个 task。 |
| `Task` | task_id、session_id、workspace_id、goal、product_mode、status、budget、trace_id。 | 长任务状态机和事件流的根对象。 |
| `UploadedFile` | file_id、workspace_id、mime_type、hash、security_label、parse_status。 | 进入 Parse Gateway 前必须完成文件校验和安全标签。 |
| `Artifact` | artifact_id、task_id、kind、uri、hash、download_policy。 | Markdown、PDF、JSON、citation bundle、trace report。 |
| `TraceEvent` | event_id、task_id、trace_id、type、timestamp、payload。 | 前端事件和 trace span 分离，但共享 id。 |
| `Citation` | citation_id、evidence_id、document_id、block_id、source_span。 | 回答中引用必须可回到 Document IR。 |
| `Feedback` | feedback_id、task_id、rating、label、comment、dataset_candidate。 | 线上反馈回流 eval dataset 候选。 |

## 输入 / 输出文件

输入：

- `src/backend/zuno/api/**`
- `src/backend/zuno/platform/services/workspace/**`
- `apps/web/**`
- `docs/architecture/architecture.md`

输出：

- API DTO / contract tests。
- SSE event envelope tests。
- Artifact / citation / feedback contract tests。
- 前端 trace panel 或 product visibility 的最小 UI contract。

## 依赖与阻塞

- 依赖 PHASE02 的 ownership matrix；新增 API / workspace code 必须有 target owner。
- PHASE05 runtime 必须消费本 phase 的 `Task`、`Session`、`TraceEvent` 契约。
- PHASE10 trace/eval 必须复用 `task_id`、`session_id`、`trace_id`，不能另起 id 体系。

## 前端边界

本 phase 的前端范围只包括产品闭环可见性：上传状态、task 状态、事件流、artifact list、citation / trace reference 和 feedback。它不做营销 landing page，不做无关 hero，不做完整企业权限后台。未实现 UI 不能写成 Current。

## 验收

- 主场景可以用一张图和一条事件链讲清楚。
- API 和 frontend 不再只是聊天入口，而能表达知识库、任务、产物和 trace。
- 未实现的 UI 和 backend 行为不写成 Current。
- 只有 API/frontend contract tests 通过后，产品闭环才允许写入 Current；SSE / WebSocket 未实现前只能写 Target。

## 验证

```powershell
pytest -q tests/api tests/frontend -p no:cacheprovider
python tools/agent/render_architecture.py --check
```
