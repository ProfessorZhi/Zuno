# PHASE08 Hard Negative Eval And Release Gate

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE08_hard-negative-eval-and-release-gate
status: completed
owner: Eval / Release

## 目标

补齐 hard negative eval，并用 release gate 判断 Agentic GraphRAG 是否真正稳定超过 standard RAG。

## Current 完成事实

PHASE08 已完成 EnterpriseRAG paired runner 的 release gate 输出面：`metrics.json` 和 `report.md` 会输出 `hard_negative_coverage` 与 `release_gate`，其中 release gate 检查 `Evidence Text Available@5 >= 0.60`、`Source Doc Citation >= 0.85`、`Citation Accuracy >= 0.30`、`Answer Correctness >= standard_rag` 和 hard negative taxonomy 覆盖。

本轮真实本地 paired eval 尝试过两次：

- `sample_size=80` 输出目录：`.local/evals/zuno/rag_eval/runs/enterprise-rag-phase08-release-gate`
- `sample_size=8` 输出目录：`.local/evals/zuno/rag_eval/runs/enterprise-rag-phase08-release-gate-smoke`

两次运行都完成了部分 profile 产物，但 agentic profile 未在本轮运行窗口内完成，因此本轮不能写成 fixed benchmark measured pass。当前 release gate 结论是 `blocked_not_measured_due_to_agentic_profile_incomplete`；quality gate 保持未达成，后续需要修复或拆分 agentic profile runner 后再跑完整 fixed benchmark。

## 范围

hard negatives 至少覆盖：

- 同文档相邻错误 chunk。
- 同主题不同文档。
- 表格 vs 正文。
- 页眉页脚干扰。
- OCR 噪声。
- 多文档冲突。
- graph summary 中有答案但 citation 必须回原文。

## 禁止范围

- 不用小样本偶然 wins 宣布生产完成。
- 不把 external dependencies 写成 Current。
- 不绕过 failure cases。

## 验收闸门

- Program release report 明确 standard / deep / agentic 的收益、成本、失败边界。
- 质量闸门全部达成或明确说明未达成原因。
- completed program 归档到 `docs/history/programs/`。
- `.agent/programs/` 回到 no-active closure state。

## 验证命令

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
pytest -q tests/evals/test_enterprise_rag_paired_benchmark.py tests/evals/test_rag_eval_metrics.py -p no:cacheprovider
```

## 需要先读取

- `.agent/programs/closure-checklist.md`
- `tools/evals/zuno/AGENTS.md`
- `tools/evals/zuno/rag_eval/**`
- `docs/architecture/production-readiness.md`

## 需要修改的文件

预计修改范围：

- `tools/evals/zuno/rag_eval/**`
- `tests/evals/**`
- `.agent/programs/**`
- `docs/history/programs/**`
- `docs/architecture/**`，仅当 Current / Target 结论发生变化时

## 执行拆解

1. 扩展 hard negative fixtures。
2. 运行 paired benchmark。
3. 生成 release report、metrics、failure cases。
4. 做 self-maintenance review。
5. 归档 program 并恢复 no-active。

## 多 agent 分工

可拆 eval fixture、release report、docs self-review；主线程负责最终 verifier 和归档。

## 需要返回的证据

- final metrics。
- failure summary。
- cost / latency tradeoff。
- archive path。
- verification output。

## 停止条件

Program 未归档、verifier 未过或质量闸门未解释清楚时不得关闭。
