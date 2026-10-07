# GraphRAG 检索 Ablation 协议（冻结）

```text
status: FROZEN_PROTOCOL
measurement_status: BLOCKED_PENDING_DATA
owner: 03 Knowledge & Evidence + 09 Observability & Evaluation
source: red-blue rb-2026-09-15-formal-019 / IMP-019-05
frozen_at: 2026-10-07
frozen_against_main: 5844fe59
```

本文件只冻结**怎样测**，不声明任何质量结论。它是 [`docs/evidence/current-eval-baseline.md`](../evidence/current-eval-baseline.md)（当前状态 `MEASUREMENT_BLOCKED`）的配套验证协议：在数据与运行时可用之前，任何 GraphRAG 收益主张都保持 Unknown。

## 1. 为什么需要这份协议

Zuno 的检索融合层累积了若干启发式（fusion ranking、bridge / genealogy / comparison guardrail、proactive requery、seed expansion、entity alias、path-aware ranking）。这些启发式大多来自针对具体失败案例的修补，**缺少独立 holdout 上的增量收益证明**。已记录的 `normal vs enhanced` 对比只证明"增强路径不劣于基线"，不是逐项 heuristic 的 leave-one-out ablation。

本协议的目标不是"再证明一次 enhanced 好用"，而是回答一个更窄、更可证伪的问题：

> 每一条启发式，在冻结的独立 holdout 上，是否带来**稳定的**增量收益？没有稳定收益的，应当删除，而不是保留为未验证复杂度。

## 2. 结论判据（先定，后测）

对每条被检验的启发式 `H`：

- **保留**：在 holdout 上，`full` 相对 `full minus H` 在首要指标（见 §4）上的提升，方向一致且跨切分稳定（见 §5）。
- **删除**：`full minus H` 与 `full` 无显著差异，或方向不稳定。删除后 `full minus H` 即为新的 `full`，重跑剩余项。
- **不许**用训练/调参样本上的提升作为保留理由；启发式当初就是在这些样本上被调出来的。

一项都保留不下来是可接受结论。删除是合法终点，不是失败。

## 3. 被检验的启发式与开关位置

所有位置以 `main` 为准（冻结于 `5844fe59`）。每条启发式需要一个**可关闭开关**（环境变量、profile 字段或代码分支），否则先补开关再测。

| # | Heuristic | 位置 | 关闭方式 |
| --- | --- | --- | --- |
| H1 | Graph promotion threshold / baseline-preserving ranking | `src/backend/zuno/platform/services/retrieval/fusion.py:9,179-205,1065` | 令 `GRAPH_PROMOTION_THRESHOLD` 失效或短路 `_graph_rank_adjustment` |
| H2 | Comparison guardrail | `fusion.py:_apply_comparison_guardrail,_extract_comparison_seeds` | 跳过 `_apply_comparison_guardrail` |
| H3 | Bridge relation guardrail | `fusion.py:_apply_bridge_guardrail,_extract_bridge_seeds` | 跳过 `_apply_bridge_guardrail` |
| H4 | Genealogy guardrail | `fusion.py:_annotate_genealogy_metadata,_extract_genealogy_seeds` | 跳过 genealogy 标注/晋升 |
| H5 | Proactive requery | `fusion.py:_extract_requery_seed_entities,_annotate_requery_metadata` | 关闭 requery 激活 |
| H6 | Chain protection | `fusion.py:_combined_seed_coverage,_mark_chain_protection` | 跳过 `_mark_chain_protection` |
| H7 | Seed expansion (candidate-aware) | `src/backend/zuno/platform/services/graphrag/retriever.py:_build_seed_entities_with_source,_extract_query_seeds` | 只用原始 query seeds |
| H8 | Entity alias normalization | `src/backend/zuno/platform/services/graphrag/entity_alias.py:resolve_alias` | 关闭 alias 解析（严格字面匹配） |
| H9 | Path-aware ranking | `src/backend/zuno/platform/services/graphrag/retriever.py:_score_path,_path_metadata` | 用固定路径分替换 |

## 4. 指标

沿用 `tools/evals/zuno/multihop_eval` 的 retrieval-only 口径，避免把 Answer EM/F1 当首要闭环指标（见该目录 README）：

- 质量：`Recall@2/5/10`、`Precision@5/10`、`MRR@10`、`ChainRecall@5/10`、`FullChainHit@5/10`
- 引用：`CitationLineage` 命中率（gold support 覆盖率）
- 成本 / 时延：每 query 的 token / 调用次数、p50 / p95 时延
- 退化可见性：`fallback_count`、`failure_count`、`enhanced_hurts` 案例数

首要指标固定为 **`FullChainHit@5` 与 `Recall@5`**；其余为约束（不得显著回退）。

## 5. 数据集与切分

- 数据集：HotpotQA（distractor）、2WikiMultiHopQA、MuSiQue，经 `tools/evals/zuno/multihop_eval` 的 adapter 归一化。
- **冻结切分**：在跑任何 ablation 之前先固定 `dev` 子集 id 列表并写入报告；调参样本与 holdout 严格分离。当前历次 `limit=10/20/50` 结果**不算 holdout**，只能作为回归轨道，不能作为保留判据。
- 样本量：每个数据集至少一个足以给出置信区间的 holdout 规模；首轮建议每个数据集 ≥ 300 题，并报告每题级差值分布而非只看均值。
- 冻结记录：dataset、split id 列表、样本数、`commit SHA`、profile 名、模型名（见 `eval_profiles.example.json`）必须写进报告。

## 6. 执行流程（leave-one-out）

```text
1. 冻结 main SHA + 数据集 + split id + profile
2. 基线跑：normal / enhanced / auto 三条产品路径，记录全部 §4 指标
3. 对 H1..H9 逐个：只关闭 H，其余不变，重跑同一 split
4. 汇总矩阵：rows = {full, full-minus-H1, ..., full-minus-H9}，cols = 指标
5. 按 §2 判据决定保留 / 删除，删除后回到步骤 3 重跑
6. 产出 audit summary（进 Git）+ 完整报告（不入 Git，按 README 规则）
```

执行模式必须标 `real_runtime`。mocked / stackless 结果**不得混入**本协议的任何结论。

## 7. 报告要求

- 进 Git 的只允许审计摘要：`docs/evidence/` 下的摘要，含 dataset、sample count、metric、commit SHA、blocked reason（若有）。
- 完整逐题报告留在 gitignored `reports/evals/multihop/real_runtime/`。
- 报告必须显式列出 `requested_mode` / `normalized_mode` / `product_mode` / `is_ablation_mode`，并列出被关闭的 heuristic。
- 任何一条结论都要能追到：哪次 run、哪个 SHA、哪份 split。

## 8. Blocking（当前真实状态）

截至冻结时（2026-10-07），本协议**无法执行**：

- 本机无法访问 HotpotQA 官方数据源（TCP 连接超时），`data/evals/multihop/` 不存在；
- 本机没有模型 API 凭证与运行时索引；
- 仓库自身 `docs/evidence/current-eval-baseline.md` 状态为 `MEASUREMENT_BLOCKED`。

因此本协议的当前状态是 `BLOCKED_PENDING_DATA`。在数据、运行时与模型凭证就绪前：

- 不得给出任何 GraphRAG 收益或"启发式有效"的结论；
- 不得用调参样本上的旧结果（`limit=10/20/50`）替代 holdout；
- 不得为了让某项通过而调整切分或指标定义。

解锁条件：具备可访问的数据集、可运行的 Knowledge 索引与 §5 的冻结切分。解锁后按 §6 执行，按 §2 判决。
