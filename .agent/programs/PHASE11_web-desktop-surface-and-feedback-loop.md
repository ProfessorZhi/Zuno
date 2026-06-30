# PHASE11 web-desktop-surface-and-feedback-loop

status: active

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

## 验证命令

```powershell
git diff --check
pytest -q tests/frontend tests/api -p no:cacheprovider
npm --prefix apps/web test -- --run
```
