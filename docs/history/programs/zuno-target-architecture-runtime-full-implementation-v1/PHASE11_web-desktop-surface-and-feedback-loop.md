# PHASE11 web-desktop-surface-and-feedback-loop

status: completed

## 目标

完成用户可感知的产品层：上传、task 状态、SSE 流、审批交互、artifact 下载、citation 展示、trace panel、feedback UI 和失败恢复提示。

## 范围

- Web 优先，Desktop 跟随复用 API。
- 让 `apps/web/src/apis/workspace.ts` 的类型对应真实后端行为。
- 将 feedback 与 task、artifact、trace、eval diagnostic 关联。

## 禁止范围

- 不做 landing page 式展示替代产品界面。
- 不把 mock trace 当成真实 runtime trace。
- 不让 UI 隐藏失败状态或审批等待状态。

## 验收闸门

- 前端测试或可复现手动脚本覆盖上传、事件流、审批、answer/citation、artifact、feedback。
- UI 中能定位 task id、trace id、artifact id。
- failure / blocked / approval_required 状态可见。

## 完成证据

- `apps/web/src/pages/workspace/defaultPage/defaultPage.vue` 在 Agent 模式中改走 workspace task runtime：注册文件、触发 ingest、创建 task、订阅 SSE、审批后刷新 snapshot / artifact，并提交 feedback。
- `apps/web/src/pages/workspace/defaultPage/defaultPage.vue` 的 trace 面板现在显示 runtime failure、artifact id、citation id、trace / eval snapshot、source refs 和 feedback 状态；普通聊天仍保留 `workspaceSimpleChatStreamAPI`。
- `apps/web/src/apis/workspace.ts` 的 PHASE03-PHASE10 类型和 API 已被 Web 产品面实际消费，Desktop 当前仍是 API / bridge 复用，不写成生产级桌面闭环。
- `tests/frontend/test_frontend_workspace_features.py` 增加 PHASE11 静态验收，固定 upload / ingest / task / SSE / artifact / trace / eval / feedback UI 触点。

## 已运行验证

```powershell
pytest -q tests\frontend\test_frontend_workspace_features.py tests\frontend\test_workspace_product_loop_types.py -p no:cacheprovider
pytest -q tests\frontend\test_frontend_workspace_features.py tests\frontend\test_workspace_product_loop_types.py tests\api\test_workspace_task_runtime.py tests\api\test_workspace_security_observability_runtime.py -p no:cacheprovider
git diff --check
python .agent\scripts\verify_agent_system.py
```

`npm run lint` 和 `npm run build` 在 `apps/web` 入口未进入编译：当前 checkout 没有 root `node_modules`，脚本无法加载 `vue-tsc` 和 `vite`。该阻塞不是代码失败，但 PHASE12 需要在 release evidence 中记录。

## 验证命令

```powershell
git diff --check
pytest -q tests/frontend tests/api -p no:cacheprovider
npm --prefix apps/web test -- --run
```
