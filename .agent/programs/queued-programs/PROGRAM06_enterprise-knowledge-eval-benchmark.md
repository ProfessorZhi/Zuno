# PROGRAM06 Enterprise Knowledge Eval Benchmark

state: queued
program: zuno-enterprise-knowledge-eval-benchmark-v1
depends_on: zuno-agent-planning-integration-v1

## 目标

建设企业内部知识库问答系统的自动化评测体系，评估 Zuno 的 Agentic GraphRAG 是否相比 Basic RAG 和 Static GraphRAG baseline 在召回、答案质量、引用质量、低幻觉、安全和可观测性上有实质提升。

## 场景边界

场景是企业内部知识库问答，不是简历评测、聊天 demo 或孤立 RAG 脚本。

资料类型：

- HR / 员工政策。
- IT / 安全规范。
- 采购 / 报销 / 流程制度。
- 产品 / 技术文档。
- 合同 / 法务样例。
- 表格型制度或 FAQ。

用户提供的私有资料默认只留本地；如接 LangSmith，只上传 redacted trace、document ref、hash、指标和结构化 span，不上传原文。

## PHASE01 Eval Design 与 Corpus Policy

目标：

- 定义 corpus 来源、隐私边界、redaction policy、dataset split。
- 决定先用公开/合成企业资料跑通，再接用户本地私有资料。

验收：

- `.local/evals/zuno/enterprise_kb/corpus/` 作为本地私有 corpus 默认路径。
- 公开 demo corpus 与私有 corpus 路径分开。
- LangSmith export 不包含私有文档原文。

## PHASE02 Dataset Schema

目标：

- 定义 `EvalDocument`、`EvalQuestion`、`ExpectedAnswer`、`RelevantBlock`、`Rubric`、`Difficulty`、`QuestionType`。

Question types：

- lookup
- multi-hop
- compare
- policy-exception
- temporal-or-versioned
- table-lookup
- negative-unanswerable
- safety-sensitive

验收：

- dataset JSONL 可校验。
- 每个 question 可关联 expected relevant block ids。

## PHASE03 Ground Truth Builder

目标：

- 用 Program 1 parser 解析资料。
- 选择 relevant blocks。
- 写 expected answer 和 rubric。
- 支持人工标注和 LLM-assisted draft，但最终可人工复核。

验收：

- ground truth builder 不依赖模型即可读取和校验 dataset。
- LLM-assisted 标注必须带 review status。

## PHASE04 Runners

目标：

- Basic RAG baseline runner。
- Static GraphRAG baseline runner。
- Agentic GraphRAG target runner。
- Optional ablation：no-memory、no-replan、no-rerank。

验收：

- 三个 runner 使用同一 corpus、同一 question set、同一 metric interface。
- runner 输出 run id、trace id、retrieved block ids、answer、citations、latency。

## PHASE05 Retrieval Metrics

指标：

- `recall@k`
- `precision@k`
- MRR
- NDCG
- hit rate
- context precision
- context recall

验收：

- retrieval metrics 能按 question type 聚合。
- multi-hop 和 compare 问题单独报告。

## PHASE06 Answer Metrics

指标：

- correctness
- faithfulness
- answer relevance
- citation coverage
- source-span accuracy
- unsupported claim rate
- refusal correctness

验收：

- 不可回答问题必须评估 refusal correctness。
- 有引用答案必须检查 citation 是否指向 relevant block。

## PHASE07 LangSmith / OTel Trace Bridge

目标：

- 将 parse、retrieve、graph_expand、plan、tool、reflect、replan、answer 写成 span。
- 本地 trace 是事实源，LangSmith 是 sink / experiment viewer。

验收：

- redacted span builder 不包含私有原文。
- LangSmith export adapter 能在无 token 时生成 target-blocked evidence。

## PHASE08 Report 与 Release Gate

目标：

- 输出 JSON + Markdown report。
- 给出 Agentic GraphRAG 相比 baseline 的 win / loss / regression。

建议门槛：

- lookup 问题不得明显退化。
- multi-hop / compare 的 recall@5 或 NDCG 应明显高于 Basic RAG。
- citation coverage 达到 release threshold。
- unsupported claim rate 低于 baseline。
- trace completeness 达到 release threshold。

## 候选路径

- `tools/evals/zuno/enterprise_kb/`
- `tools/evals/zuno/run_enterprise_kb_eval.py`
- `tests/evals/test_enterprise_kb_eval_dataset.py`
- `tests/evals/test_enterprise_kb_eval_metrics.py`
- `docs/evidence/eval-baselines.md`

## 验证基线

```powershell
git diff --check
pytest -q tests/evals tools/evals/zuno -p no:cacheprovider
python tools/evals/zuno/run_enterprise_kb_eval.py --suite smoke --compare all --output-dir .local/evals/zuno/enterprise_kb/runs/smoke
python .agent/scripts/verify_agent_system.py
```

## 停止条件

- 用户要求使用私有企业资料，但没有给本地资料路径或脱敏规则。
- LangSmith token、外部 trace sink 或付费模型成为必需条件。
- Agentic GraphRAG 评测不优于 baseline，且需要回到 Program 1-3 修系统能力。
- dataset ground truth 只能由模型生成且无法人工复核。
