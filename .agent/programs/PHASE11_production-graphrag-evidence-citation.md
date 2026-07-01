# PHASE11 Production GraphRAG Evidence Citation

status: active
previous_phase: PHASE10_tool-sandbox-vault-network-runtime

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

## 需要先读取

- `src/backend/zuno/knowledge/agentic_graphrag.py`
- `src/backend/zuno/knowledge/query_service.py`
- `src/backend/zuno/knowledge/citation.py`
- `src/backend/zuno/knowledge/evidence.py`
- `src/backend/zuno/knowledge/retrieval/**`
- `src/backend/zuno/knowledge/graphrag/**`
- `tests/graphrag/**`
- `tests/retrieval/**`

## 需要修改的文件

- `src/backend/zuno/knowledge/**`
- GraphRAG extraction / community report / rerank modules
- evidence / citation / unsupported claim guard modules
- `tests/graphrag/**`
- `tests/retrieval/**`
- `tests/evals/**`

## 执行拆解

1. 保持 user-facing mode：normal、enhanced、auto；保持 internal method：basic、local、global、drift。
2. 接入 graph extraction、community report、RRF / rerank 的本地 Current 或 external Target adapter。
3. 确保 EvidenceBundle 能追溯到 source document、block、provenance、ACL。
4. CitationBuilder 不允许生成无 evidence citation。
5. 将 unsupported claim metrics 写入 trace/eval/release baseline。

## 多 agent 分工

- Thread A：retrieval router / fusion / rerank。
- Thread B：graph extraction / community report。
- Thread C：evidence / citation / unsupported claim guard。
- Thread D：eval tests。
- 主线程：验证 cited answer 从 claim 到 evidence 的追踪链。

## 需要返回的证据

- retrieval mode matrix。
- graph extraction / community report 当前边界。
- evidence bundle 示例。
- citation coverage 和 unsupported claim metrics。
- eval baseline 结果。

## 停止条件

- 外部图索引服务不可用且无 local fallback。
- citation 无法追溯 source evidence。
- enhanced / auto 模式绕过 evidence guard。
