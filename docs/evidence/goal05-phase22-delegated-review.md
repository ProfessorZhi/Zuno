# PHASE22 公共 Benchmark 候选集委托审核证据

status: REVIEW_PARTIAL
phase: PHASE22
date: 2026-08-10

## 审核结论

用户已明确委托当前 Agent 执行候选集人工审核。审核范围覆盖全部 80 个 candidate case：

- `52` 个批准为 `reviewer_status=approved`、`benchmark_eligible=true`；
- `28` 个拒绝为 `reviewer_status=rejected`、`benchmark_eligible=false`；
- 没有把缺失 gold evidence 的 case 改写为通过。

审核标准是：问题、答案、gold document/evidence 引用必须与本地缓存的官方上游记录一致，且候选包完整性状态为 `VERIFIED`。52 个批准 case 中，HotpotQA 32 个、MultiHop-RAG 20 个均完成逐条上游记录比对；完整性结果为 `52 VERIFIED / 28 INCOMPLETE / 0 INVALID / 0 UNVERIFIABLE`。

## 根因修复

HotpotQA 官方数据的 `supporting_facts` 使用平行的 `title` / `sent_id` 数组，而候选生成器此前只解析二维列表，错误地把 32 个有 gold evidence 的 case 标成 incomplete。同时，官方记录字段是 `id`，生成器此前只读取 `_id`，导致来源标识退化为合成 ID。

已在 `tools/evals/zuno/rag_eval/datasets/generate_candidate_pack.py` 修复两种问题，并增加回归测试。

## 可复现产物

- 原始候选包：`docs/evidence/goal05-phase22-public-benchmark-review-pack/candidate_cases.jsonl`
- 审核摘要：`docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/review_summary.json`
- 审核后的 Case Set：`docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/reviewed_cases.jsonl`
- 逐条决议：`docs/evidence/goal05-phase22-public-benchmark-review-pack/reviewed/review_decisions.jsonl`
- 审核脚本：`tools/scripts/review_phase22_candidate_pack.py`

当前审核 Case Set SHA-256：`24e0ab28b00852a5fff6c13e59c452bd47012f9c10f2c3d14783d431341f9bbd`。

## 边界

本证据只完成候选集审核，不声明 fixed benchmark measured、quality proven 或 production ready。固定 Benchmark 仍缺 28 个 eligible case，并且正式四 profile runtime、formal credentials、runtime/product/approval attestations、full final verification 和 Program archive 仍未完成。
