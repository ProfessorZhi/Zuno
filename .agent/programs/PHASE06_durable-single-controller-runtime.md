# PHASE06 durable-single-controller-runtime

status: active

## 目标

在 `agent/harness.py` 的节点定义之上，实现 durable checkpoint、resume、interrupt、approval wait、cancel 和 replan，让 Single Controller runtime 成为真实长任务状态机。

## 范围

- 将 task lifecycle 与 runtime state 绑定。
- 实现 checkpoint persistence adapter 和 resume path。
- 让 approval-required interrupt 能暂停并恢复执行。

## 禁止范围

- 不把 harness contract 当作 durable runtime。
- 不把产品 runtime 改成默认多 Agent。
- 不绕开 task/session/event trace。

## 验收闸门

- focused tests 能启动任务、写 checkpoint、模拟中断、恢复并继续输出 event。
- RuntimeTurnLedger、trace id、task id 在 resume 前后保持一致。
- recoverable failure 与 non-recoverable failure 可区分。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_single_controller_runtime_harness.py tests/agent -p no:cacheprovider
```
