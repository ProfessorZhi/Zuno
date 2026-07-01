# PHASE06 Product Surface Desktop Recovery Loop

status: completed
completed_at: 2026-07-01
next_phase: PHASE07_production-parse-and-index-platform

## 目标

把产品闭环从 Web 第一版推进到 production Desktop、长任务恢复、下载体验和错误恢复产品化。

## 范围

- Web / Desktop workspace task、file ingest、SSE / event stream、approval、artifact、trace-eval、feedback。
- 长任务 resume / cancel / failure recovery 的用户可见状态。
- artifact 下载、失败提示、可重试路径和 trace 关联。

## 禁止范围

- 不绕过后端 task/session/event runtime。
- 不只做 UI 文案而不接真实 API / runtime surface。

## 验收闸门

- Desktop 与 Web 至少共享同一套 task lifecycle contract。
- 长任务恢复和失败恢复有 focused tests 或 e2e evidence。
- artifact / feedback / trace 可从同一 task 串起。

## 验证命令

```powershell
git diff --check
pytest -q tests/api/test_workspace_task_runtime.py tests/api/test_workspace_product_loop_contract.py tests/frontend/test_frontend_workspace_features.py -p no:cacheprovider
npm --prefix apps/web test -- --run
```

## 需要先读取

- `apps/web/AGENTS.md`
- `apps/web/src/apis/workspace.ts`
- `apps/web/src/**/workspace*`
- `apps/desktop/**`
- `src/backend/zuno/api/**`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `docs/architecture/production-readiness.md`

## 需要修改的文件

- `apps/web/**`
- `apps/desktop/**`
- `src/backend/zuno/api/**`
- `tests/api/test_workspace_task_runtime.py`
- `tests/api/test_workspace_product_loop_contract.py`
- `tests/frontend/test_frontend_workspace_features.py`
- relevant Desktop tests 或 bridge tests

## 执行拆解

1. 对齐 Web / Desktop 使用同一 task lifecycle：file、ingest、task、event、approval、artifact、trace-eval、feedback。
2. 补长任务恢复状态：pending、running、approval_required、recoverable_failed、cancelled、completed。
3. 补 artifact 下载和错误恢复路径，不只显示 UI 文案。
4. 保证 trace_id、session_id、task_id、artifact_id、feedback_id 可串联。
5. 更新 frontend/backend contract tests。

## 多 agent 分工

- Thread A：后端 workspace task / artifact / feedback。
- Thread B：Web task surface 和 event stream。
- Thread C：Desktop bridge 和恢复体验。
- Thread D：frontend/backend tests。
- 主线程：跑端到端 product loop 验证。

## 需要返回的证据

- task lifecycle 状态表。
- Web / Desktop contract 对齐证据。
- SSE / event stream 示例。
- artifact / feedback / trace 关联样例。

## 完成证据

- task lifecycle 状态表：`WORKSPACE_TASK_LIFECYCLE_FLOW = pending / running / approval_required / recoverable_failed / cancelled / completed`；`GET /api/v1/workspace/task-lifecycle` 返回同一状态表、internal status mapping 和 recovery actions。
- Web / Desktop contract 对齐：`apps/web/src/apis/workspace.ts` 暴露 `getWorkspaceTaskLifecycleAPI` / `downloadWorkspaceArtifactAPI`；`apps/desktop/preload.cjs` 暴露 `taskLifecycleEndpoint`、`artifactDownloadEndpointTemplate` 和 `workspaceTaskLifecycleStates`，Electron 继续复用同一 Web bundle 与 backend API。
- SSE / event stream 示例：`stream_task_events()` 对每个事件输出 `lifecycle_state`；`task_failed` 事件带 `recoverable_failed` 和 `recovery_actions`；`artifact_created` 事件带 `download_url`。
- artifact / feedback / trace 关联样例：focused test 创建 `task_phase06_download`，验证 artifact download response、`feedback_ids`、artifact `trace_id` 和 feedback event `trace_id` 同 task 串联。
- Web 体验：workspace artifact panel 增加真实 `downloadWorkspaceArtifactAPI` 下载按钮；recoverable failure 面板消费 runtime `recovery_actions`，不是纯 UI 文案。

## 验证结果

```powershell
pytest -q tests/api/test_workspace_task_runtime.py tests/api/test_workspace_product_loop_contract.py tests/frontend/test_frontend_workspace_features.py -p no:cacheprovider
# 17 passed, 1 warning

pytest -q tests/api/test_workspace_task_runtime.py tests/api/test_workspace_product_loop_contract.py tests/frontend/test_frontend_workspace_features.py tests/frontend/test_workspace_product_loop_types.py -p no:cacheprovider
# 20 passed, 1 warning

python tools/agent/render_architecture.py --check
# passed

git diff --check
# passed

npm --prefix apps/web run lint
# passed

npm --prefix apps/web run build
# passed

npm --prefix apps/web test -- --run
# blocked: apps/web/package.json has no "test" script

python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-docs.ps1
# passed after removing generated local artifacts node_modules/ and apps/web/dist/
```

## Remaining Target

- production Desktop 打包/e2e 闭环仍是 Target；本 phase 证明的是 Desktop 通过同一 Web bundle/API 共享 task lifecycle contract。
- 进程重启后的 durable recovery 仍属于 PHASE08 / 后续 production persistence Target；本 phase 只把 recoverable failure 和 retry/trace/feedback actions 产品化暴露。
- 运维级错误恢复和外部发布 gate 仍留到后续 release closure。

## 停止条件

- Desktop 需要无法本地复现的打包环境。
- UI 需要修改公共 API 字段。
- 长任务恢复需要 durable runtime 先完成 PHASE08。
