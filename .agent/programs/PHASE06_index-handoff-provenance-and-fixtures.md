# PHASE06 Index Handoff、Provenance 与 Fixtures

status: planned
program: zuno-production-document-ingestion-and-thread-foundation-v1

## 目标

证明文档解析结果能稳定进入索引交接层，并保留企业知识库问答必须的 provenance：source file、block id、page、section、parser version、ACL、安全标签和 manifest。

## 范围

- Document IR -> index manifest handoff。
- source provenance、ACL inheritance、parser diagnostics、adapter status。
- retry / replay 关联 parser job 和 index job。
- golden fixtures 覆盖 parse -> IR -> manifest 的完整路径。

## 禁止范围

- 不接入 Elasticsearch / Milvus / Neo4j。
- 不改 GraphRAG query ranking 策略。
- 不把本地 manifest 写成生产 index service。
- 不扩大到 Program 4 eval runner。

## 验收闸门

- 每个 indexed block 都能追溯到 source file 和 parser output。
- manifest 记录 parser name、version、job id、adapter status、ACL 和 diagnostics。
- replay 不重复制造冲突 block id。
- focused tests 能证明 parse -> index handoff 不是只在文档中存在。

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge/test_index_jobs_runtime.py tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
pytest -q tests/agent/test_knowledge_graphrag_runtime_contracts.py -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
```

## 需要先读取

- PHASE03 parser job lifecycle。
- `src/backend/zuno/knowledge/indexing/`
- `src/backend/zuno/knowledge/agentic_graphrag.py`
- `tests/knowledge/test_index_jobs_runtime.py`
- `tests/agent/test_knowledge_graphrag_runtime_contracts.py`

## 需要修改的文件

- `src/backend/zuno/knowledge/indexing/**`
- `src/backend/zuno/knowledge/ingestion/**`
- `tests/knowledge/test_index_jobs_runtime.py`
- `tests/knowledge/test_parse_gateway_runtime.py`
- `tests/agent/test_knowledge_graphrag_runtime_contracts.py`
- `.agent/programs/PHASE06_index-handoff-provenance-and-fixtures.md`

## 执行拆解

1. 写 failing test：Document IR block 进入 index manifest 后保留 source provenance。
2. 写 failing test：ACL 和 sensitivity metadata 从 parser output 传入 manifest。
3. 写 failing test：parser diagnostics 和 adapter status 可被 index job 读取。
4. 写 failing test：replay 不重复产生 block ids。
5. 实现 handoff metadata。
6. 检查 Agentic GraphRAG evidence / citation 不因 metadata 改动退化。
7. 运行 focused tests。

## 多 agent 分工

- 一个 subagent 可只读审计 indexing manifest。
- 一个 subagent 可只读审计 citation / evidence 所需字段。
- 主线程负责 tests、实现和 phase evidence。

## 需要返回的证据

- parse -> IR -> index manifest 示例。
- provenance 字段表。
- replay / idempotency 结果。
- focused test 输出。

## 停止条件

- index manifest 变更需要迁移历史数据。
- GraphRAG evidence contract 与新的 provenance 字段冲突。
- 外部 index service 成为验收前提。
