# PHASE08 Model Gateway Cost Latency

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE08_model-gateway-cost-latency
status: pending

## 目标

定义 Model Gateway baseline，统一 chat、embedding、reranker、VLM、eval judge 的 provider boundary、fallback、retry、timeout、token / latency / cost tracking 和 trace fields。

## 范围

- ModelGateway contract。
- Model category：chat、embedding、reranker、VLM、eval judge。
- Local / mock implementation 用于 tests。
- token count、latency_ms、cost_estimate、retry_count、timeout_count。
- cost guard 与 budget verdict。

## 目标架构拼接点

本 phase 拼到 Agent Core 的 Model Gateway 和 Governance / Trace / Eval Envelope：

- Chat model 被 Planning / Answer generation 调用。
- Embedding model 被 Index / Retrieval 调用。
- Reranker 被 deep retrieval 调用。
- VLM / OCR provider boundary 被 async ingestion 和 multimodal parsing 调用。
- Eval judge 被 benchmark layer 调用。
- 所有 model call 统一输出 token、latency、cost、retry、timeout 和 fallback reason。

本 phase 的 budget verdict 必须能被 Strategy Selector 和 Dynamic Replan 消费，避免深度检索或多轮 requery 无限制增长。

## 并行开发可行性

本 phase 可由 Workstream G 推进，并与 Planning、Retrieval、Eval 并行协作。

可并行：

- mock provider 与 metric collector 可并行。
- cost guard 与 trace output 可并行。
- eval judge category 可先 mock。

不可并行：

- 不得引入必须真实外部 provider 的 tests。
- 不得让 model traces 泄露未脱敏私有原文。
- 不得让 cost guard 与 Planning budget contract 分叉。

## 详细执行卡

- 输入依赖：PHASE02 model call metric contract、现有 model/provider adapter、observability trace schema。
- 主要交付物：Model Gateway contract、mock/local provider、chat/embedding/reranker/VLM/eval judge categories、token/cost/latency/timeout/retry/fallback fields。
- 可并行工作包：contract/mock provider、cost estimator、latency trace、budget guard tests 可拆；真实 provider 接入不在本 phase。
- Coordinator 锁点：成本字段命名、budget exceeded 行为、model fallback reason 是否进入 user-visible trace summary。
- 下游交接：PHASE09 planner 读 budget；PHASE10 replan 处理 budget_low；PHASE13 汇总 cost/latency/token metrics；PHASE12 E2E 展示 run cost summary。
- PR / commit 建议：`feat(model): add model gateway metrics baseline` 与 `test(model): cover cost guard and fallback trace`。

## 禁止范围

- 不要求真实接入多个外部 provider。
- 不让 model gateway 绕过 security / budget envelope。
- 不把 mock provider 写成 production provider。

## 验收闸门

- mock model call 记录 token / latency / cost。
- cost guard 超限能返回 blocked verdict。
- fallback reason 进入 trace。
- eval judge category 可被 eval layer 引用。

## 验证命令

```powershell
git diff --check
pytest -q tests/evals -p no:cacheprovider
pytest -q tests/agent -p no:cacheprovider
pytest -q tests/api -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/platform/model_gateway.py`
- `src/backend/zuno/platform/observability/**`
- `src/backend/zuno/agent/**`
- `tests/evals/**`
- `tests/agent/**`

## 需要修改的文件

- `src/backend/zuno/platform/model_gateway.py`
- `src/backend/zuno/platform/observability/**`
- `tests/evals/**`
- `tests/agent/**`

## 执行拆解

1. 写 model call metric focused test。
2. 写 cost guard focused test。
3. 写 fallback trace focused test。
4. 实现 local / mock baseline。
5. 接入 eval / planning trace contract。

## 多 agent 分工

- Workstream G owner for metrics。
- Workstream F 消费 budget / model verdict。
- Coordinator 审查 public config / API 字段。

## 需要返回的证据

- ModelGateway contract。
- cost / latency metric 示例。
- cost guard test。
- fallback trace 示例。

## 停止条件

- 需要真实外部 provider 才能测试。
- cost guard 与 planning budget contract 冲突。
- trace 字段包含敏感 prompt 原文且无 redaction 策略。
