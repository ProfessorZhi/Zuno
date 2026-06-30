# PHASE10 security-observability-and-online-eval

status: completed

## 目标

把四道 security gate、ZunoSpan、LangSmith-compatible export、dataset 和 release baseline 接到真实 runtime。

## 范围

- 输入、检索、工具、输出各自产生 policy decision 和 trace span。
- trace/eval 可落本地持久存储，并可选择性导出外部 sink。
- 建立 retrieval、answer、agent、security 四类离线 baseline 和最小在线采样。

## 禁止范围

- 不把 export adapter 当作外部 sink runtime。
- 不把在线 eval 采样设计写成 Current。
- 不把 PII 明文送入外部 sink。

## 验收闸门

- tests 覆盖 blocked prompt injection、cross-workspace retrieval、tool approval、low citation output 和 redacted export。
- release baseline 能阻断失败指标。
- trace 可从 task 回放到 source document block。

## 完成证据

- Workspace task runtime 已接入 InputSecurityGate、RetrievalSecurityGate、ToolSecurityGate 产生的 audit、OutputSecurityGate，并在 task event stream 中记录 `security_gate`、`eval_diagnostic` 和 blocked/failure 状态。
- Task snapshot 已暴露 `observability.spans`、`observability.trace_replay.source_refs` 和 `observability.release_eval`；ZunoSpan 覆盖 security audit、retrieval 和 eval。
- ReleaseEvalBaseline 已在 task runtime 中按 citation coverage、approval escape、secret redaction miss 和 security block 指标生成 release evidence；失败指标会阻断当前 task。
- PHASE10 仍严格把外部 sink runtime、在线 eval 采样平台、生产级 trace store 和 UI trace panel 写作 Target。
- 验证：`pytest -q tests\security tests\evals tests\api\test_workspace_task_runtime.py tests\api\test_workspace_security_observability_runtime.py tests\frontend\test_workspace_product_loop_types.py -p no:cacheprovider` 通过，167 passed；`python .agent\scripts\verify_agent_system.py`、`python tools\scripts\verify_repo_structure.py`、`powershell -NoProfile -ExecutionPolicy Bypass -File .agent\scripts\verify-workflow.ps1`、`python tools\agent\render_architecture.py --check` 均通过。

## 验证命令

```powershell
git diff --check
pytest -q tests/security tests/evals tools/evals/zuno -p no:cacheprovider
```
