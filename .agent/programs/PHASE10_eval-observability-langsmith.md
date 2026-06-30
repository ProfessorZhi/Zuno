# PHASE10 Eval Observability LangSmith

status: pending

## 目标

建立 LangSmith-compatible Trace / Eval 平台化能力，同时保留本地 pytest/eval runner 作为 release gate。

## 步骤

- [ ] 定义 trace/span schema，覆盖 model、tool、retrieval、evidence、citation、approval、sandbox、latency、cost。
- [ ] 建立 offline eval dataset：企业制度问答、合同审查、简历/JD、项目知识问答。
- [ ] 建立 retrieval、answer、agent trajectory、security 和 business scenario 指标。
- [ ] 增加 LangSmith export adapter 或兼容 metadata builder。
- [ ] 将关键 eval 加入 CI regression gate。

## 验收

- 每次回答能追踪 query method、evidence、citation、tool trajectory 和安全事件。
- eval baseline 可版本化、可回归、可写进 release evidence。
- LangSmith 是 sink，不是唯一事实源。

## 验证

```powershell
pytest -q tests/evals tools/evals/zuno -p no:cacheprovider
```
