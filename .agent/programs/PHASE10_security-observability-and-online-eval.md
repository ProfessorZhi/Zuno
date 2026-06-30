# PHASE10 security-observability-and-online-eval

status: active

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

## 验证命令

```powershell
git diff --check
pytest -q tests/security tests/evals tools/evals/zuno -p no:cacheprovider
```
