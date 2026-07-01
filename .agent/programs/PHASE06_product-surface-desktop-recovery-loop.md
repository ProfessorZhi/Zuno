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
