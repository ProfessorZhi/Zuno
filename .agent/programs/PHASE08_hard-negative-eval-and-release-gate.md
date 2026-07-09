# PHASE08 Hard Negative Eval And Release Gate

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE08_hard-negative-eval-and-release-gate
status: pending
owner: Eval / Release

## 目标

补齐 hard negative eval，并用 release gate 判断 Agentic GraphRAG 是否真正稳定超过 standard RAG。

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
