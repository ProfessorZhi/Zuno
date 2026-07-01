# PROGRAM03 Runtime Subsystems Parallel

state: queued
program: zuno-runtime-subsystems-parallel-v1
depends_on: zuno-enterprise-document-ingestion-platform-v2

## 目标

在 Program 1 固定 Document IR、parser worker 和 index handoff，且 Program 2 完成 enterprise document ingestion persistence platform 之后，使用多线程模式并行推进四个低耦合子系统：Memory / Context、Tool / Sandbox、Security / Governance、GraphRAG / Index。Program 3 的目标是产出可被 Program 4 合并的模块能力、tests 和 evidence，不直接重写 `GeneralAgent` 主循环，也不回退到 in-memory 产品事实源。

## 为什么可以并行

这四块写入范围可以相对隔离：

- Memory / Context 主要在 `src/backend/zuno/memory/`、`src/backend/zuno/agent/context.py` 和 memory tests。
- Tool / Sandbox 主要在 `src/backend/zuno/capability/`、`src/backend/zuno/platform/security/` 和 tool tests。
- Security / Governance 主要在 `src/backend/zuno/platform/security/`、trace / redaction tests 和 security tests。
- GraphRAG / Index 主要在 `src/backend/zuno/knowledge/`、retrieval / graph tests 和 eval hooks。

共享文件如 `AGENTS.md`、README、`.agent/system.yaml`、`.agent/programs/*`、核心 verifier、架构文档由主线程 coordinator 收口。

## 线程 A：Memory / Context

建议分支：`codex/zuno-p2-memory-context`

允许范围：

- `src/backend/zuno/memory/**`
- `src/backend/zuno/agent/context.py`
- `src/backend/zuno/agent/post_turn.py`
- `tests/agent/test_context_contracts.py`
- `tests/agent/test_context_orchestrator.py`
- `tests/agent/test_memory_layers.py`
- `tests/agent/test_memory_layer_surfaces.py`
- `tests/agent/test_generalagent_context_memory_runtime.py`

目标：

1. 明确 working memory、episodic memory、semantic memory、procedural memory、preference / governance memory 的边界。
2. 实现上下文压缩策略：最近窗口、任务摘要、结构化记忆、被丢弃内容原因、可恢复引用。
3. 强化 semantic fallback、privacy delete、sensitive exclusion 和 memory eval baseline。

验收：

- Context Pack 能显示 include / exclude / compressed / dropped reasons。
- 压缩结果可追溯到 raw event 或 memory item。
- sensitive source 不进入模型上下文。
- focused memory tests 通过。

## 线程 B：Tool / Sandbox

建议分支：`codex/zuno-p2-tool-sandbox`

允许范围：

- `src/backend/zuno/capability/**`
- `src/backend/zuno/platform/security/**`
- `tests/agent/test_capability_system.py`
- `tests/agent/test_capability_registry.py`
- `tests/security/**`
- `tests/tools/**`

目标：

1. 强化 Tool Control Plane：tool registry、policy、approval、execution、result normalization。
2. 强化 approval ledger：redaction、decision id、tool request id、result id。
3. 强化 credential-ref-only broker 和 network policy。
4. 明确 sandbox adapter：当前 `real_isolation=False`，真实 rootless / gVisor / Firecracker 仍是 Target。

验收：

- 高副作用工具必须 approval。
- 凭据原文不进入日志、trace 或 approval ledger。
- network deny / deny_by_default 可测试。
- sandbox audit context 可进入 trace。

## 线程 C：Security / Governance

建议分支：`codex/zuno-p2-security-governance`

允许范围：

- `src/backend/zuno/platform/security/**`
- `src/backend/zuno/platform/observability/**`
- `tests/security/**`
- `tests/evals/**`
- `tools/evals/zuno/**` 中与安全指标相关的轻量配置

目标：

1. 输入、检索、工具、输出四道 gate 的测试样例化。
2. prompt injection、cross-workspace leakage、secret / PII redaction、unsupported claim policy 形成可跑 tests。
3. trace 记录 policy decision、redaction、blocked reason。

验收：

- 安全样例集可运行。
- 检索前 ACL 与输出后 DLP 不是互相替代。
- policy blocked / allowed / redacted 都有 trace。

## 线程 D：GraphRAG / Index

建议分支：`codex/zuno-p2-graphrag-index`

允许范围：

- `src/backend/zuno/knowledge/**`
- `tests/agent/test_knowledge_graphrag_runtime_contracts.py`
- `tests/graphrag/**`
- `tests/retrieval/**`
- `tests/evals/test_multihop_eval_real_runtime_runner.py`

目标：

1. 固定 enterprise knowledge schema 和 EvidenceBundle 字段。
2. 增强 local RRF / rerank trace。
3. 提供 Static GraphRAG baseline runner，为 Program 5 对照组准备。
4. 继续把外部 Elasticsearch / Milvus / Neo4j 写成 adapter boundary 和 Target，不伪装 Current。

验收：

- 同一 query 能产生 retrieval trace、evidence bundle 和 citation source tracing。
- GraphRAG baseline runner 可被 Program 5 eval 调用。
- unsupported claim metrics 可读。

## 主线程 Coordinator 规则

1. Program 1 PHASE07 已按旧 Program 2 语境生成四个 thread prompts；启动本 program 时必须先刷新为当前 Program 3 语境。
2. 用户在 Codex UI 中创建或确认四个真实目标模式线程。
3. 每个线程必须确认 worktree、branch、status、allowed paths、forbidden paths。
4. 每个线程完成前必须验证、commit、push。
5. 主线程读取 diff 和验证结果，不只信总结。
6. 合并顺序建议：GraphRAG / Index -> Memory / Context -> Tool / Sandbox -> Security / Governance -> docs / verifier 收口。

## Program 3 验证基线

```powershell
git diff --check
pytest -q tests/agent/test_context_contracts.py tests/agent/test_context_orchestrator.py tests/agent/test_memory_layers.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py -p no:cacheprovider
pytest -q tests/agent/test_capability_system.py tests/agent/test_capability_registry.py tests/security tests/tools -p no:cacheprovider
pytest -q tests/agent/test_knowledge_graphrag_runtime_contracts.py tests/graphrag tests/retrieval -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
```

## 停止条件

- 四线程写入范围无法保持互斥。
- 子线程无法在真实 Codex UI 目标模式执行。
- 子线程需要修改 public API、DB schema 或核心 Agent 主循环。
- 任一线程需要真实外部服务、凭据或生产 sandbox 才能继续。
