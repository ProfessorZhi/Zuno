# Session Scorecard

## 逐题记录

| Question ID | Attack Area | Answer Defensibility (0-5) | Architecture / Project Fitness (0-5) | Severity | Gap Type | Evidence Missing | Stop Status |
|---|---|---:|---:|---|---|---|---|
| Q001 | <!-- Claim / Risk / Attack --> |  |  | P0/P1/P2 |  |  | PASS/KNOWN_GAP/EVIDENCE_REQUIRED/OUT_OF_SCOPE |

`Attack Area` 应从以下 Project Package 维度选择或组合：

```text
PROJECT_BACKGROUND
PRODUCT_VALUE
COMPETITOR
OWNERSHIP
DEVELOPMENT_PROCESS
ARCHITECTURE
MODEL
FINE_TUNING
DEPLOYMENT
RAG
MEMORY
AGENT
TOOL
INFRA
SECURITY
EVAL
PRODUCTION
RESUME
```

## 汇总

- P0：
- P1：
- P2：
- 平均分仅作辅助，不替代最危险 Claim 判断：
- 最危险 Claims：
- 最稳定 Claims：
- 回答防守与架构适配是否分离：`YES / NO`
- 覆盖不足的 Project Package 维度：
- Coverage Status：`SUFFICIENT / COVERAGE_FAILURE`

如果一轮 Question Budget 几乎全部集中在 Agent/RAG，而没有触及背景、价值、Ownership、开发过程、模型部署、开源替代或上线证据，Session 必须标记 `COVERAGE_FAILURE`，不能因为平均分高而通过。

## Campaign Quality Profile

按 Attack Area 聚合，不使用一个掩盖 P0 或 Unsupported 的总分：

| Attack Area | question_count | avg_answer_defensibility | avg_architecture_project_fitness | P0_count | P1_count | unsupported_count | unsupported_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| PROJECT_BACKGROUND |  |  |  |  |  |  |  |

## Campaign Summary

- coverage_status: `SUFFICIENT | COVERAGE_FAILURE`
- P0_total:
- P1_total:
- unsupported_rate:
- reopened_gap_count:

## Baseline Delta

baseline_session_id:

| Attack Area | Baseline | Current | Delta |
|---|---:|---:|---:|
| PROJECT_BACKGROUND |  |  |  |
