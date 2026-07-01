# PHASE06 Product Surface Desktop Recovery Loop

status: pending

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

## 停止条件

- Desktop 需要无法本地复现的打包环境。
- UI 需要修改公共 API 字段。
- 长任务恢复需要 durable runtime 先完成 PHASE08。
