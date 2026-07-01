# PHASE11 Production GraphRAG Evidence Citation

status: pending

## 目标

把 Knowledge / GraphRAG / Evidence / Citation 推进到生产 GraphRAG extraction、community report、RRF / rerank、外部图索引、unsupported claim guard 和 evidence eval。

## 范围

- basic / local / global / drift 内部方法。
- normal / enhanced / auto 用户模式。
- Agentic retrieval router、fusion、rerank、evidence bundle、citation builder。
- graph extraction、community report、index manifest。

## 禁止范围

- 不生成无 evidence 的 citation。
- 不让 enhanced / auto 模式绕过 unsupported claim check。
- 不把外部图服务 adapter 未接通状态写成 Current。

## 验收闸门

- cited answer 可从 evidence block 追到 source document。
- graph extraction 和 rerank 有 focused tests 或 blocked evidence。
- retrieval / citation / unsupported claim metrics 进入 trace / eval。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_knowledge_graphrag_runtime_contracts.py tests/graphrag tests/retrieval tests/evals/test_multihop_eval_real_runtime_runner.py -p no:cacheprovider
```
