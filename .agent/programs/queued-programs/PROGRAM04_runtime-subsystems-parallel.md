# PROGRAM04 Runtime Subsystems Parallel

state: queued
program: zuno-runtime-subsystems-parallel-v1
depends_on: zuno-enterprise-ingestion-async-infrastructure-v1

## 目标

在 Program 1 固定 Document IR、Program 2 完成 durable ingestion Product V1，且 Program 3 完成 enterprise ingestion async infrastructure baseline 之后，使用多线程模式并行推进四个低耦合子系统：Memory & Context Engine、Capability / Skill / Tool / MCP / Sandbox、Security / Governance、GraphRAG / Index。Program 4 的目标是产出可被 Program 5 合并的模块能力、tests 和 evidence，不直接重写 `GeneralAgent` 主循环，也不回退到 in-memory 产品事实源。

产品口径必须固定：用户不选择 Basic RAG / GraphRAG，也不选择全局 Agent 快速 / 深度模式。用户在勾选具体知识库时选择本次检索策略：标准检索或深度检索。建库时决定知识库是否具备基础索引、图谱增强索引、OCR / 多模态解析能力；查询时只决定本次用多深。Program 4 只准备这些能力和 contract，Program 5 再由 Agentic Retrieval Planner 消费它们。

## 为什么可以并行

这四块写入范围可以相对隔离：

- Memory & Context Engine 主要在 `src/backend/zuno/memory/`、`src/backend/zuno/agent/context.py` 和 memory tests。
- Capability / Skill / Tool / MCP / Sandbox 主要在 `src/backend/zuno/capability/`、`src/backend/zuno/platform/security/` 和 capability / tool tests。
- Security / Governance 主要在 `src/backend/zuno/platform/security/`、trace / redaction tests 和 security tests。
- GraphRAG / Index 主要在 `src/backend/zuno/knowledge/`、retrieval / graph tests 和 eval hooks。Program 4 不再补 Program 3 已负责的 queue、worker、outbox、dead letter 或 reconciler。

共享文件如 `AGENTS.md`、README、`.agent/system.yaml`、`.agent/programs/*`、核心 verifier、架构文档由主线程 coordinator 收口。

## 线程 A：Memory & Context Engine

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
3. 明确 Reflexion Memory 边界：Reflection 发现失败，Reflexion 生成 lesson，Memory 负责保存、scope、expiry 和下次召回。
4. 强化 semantic fallback、privacy delete、sensitive exclusion 和 memory eval baseline。

验收：

- Context Pack 能显示 include / exclude / compressed / dropped reasons。
- 压缩结果可追溯到 raw event 或 memory item。
- sensitive source 不进入模型上下文。
- focused memory tests 通过。

## 线程 B：Capability / Skill / Tool / MCP / Sandbox

建议分支：`codex/zuno-p4-capability-skill-tool`

允许范围：

- `src/backend/zuno/capability/**`
- `src/backend/zuno/platform/security/**`
- `tests/agent/test_capability_system.py`
- `tests/agent/test_capability_registry.py`
- `tests/security/**`
- `tests/tools/**`

目标：

1. 把线程 B 升级为 Capability Layer foundation：Skill Capability、Knowledge Capability、Tool Capability、MCP Capability、External API / File / Code / Browser / Artifact Capability 的 registry / routing 边界。
2. 定义 SkillCard / Skill Registry / Skill policy / runtime hints / required evidence / allowed tools / required memory scopes / output contract / safety policy / eval rubric / trace requirements。
3. 强化 Tool Control Plane：tool registry、policy、approval、execution、result normalization。
4. 强化 MCP connector governance：MCP 是 connector / protocol，不是默认可信工具库；MCP 暴露的工具仍进入 Tool Gate。
5. 强化 approval ledger：redaction、decision id、tool request id、result id。
6. 强化 credential-ref-only broker 和 network policy。
7. 明确 sandbox adapter：当前 `real_isolation=False`，真实 rootless / gVisor / Firecracker 仍是 Target。

验收：

- 高副作用工具必须 approval。
- Skill 不能写成 Tool，不能直接绕过 Knowledge / Tool / Memory / Security；Skill 只能提供任务方法、约束和评测 rubric。
- Capability Router 能区分 Skill、Knowledge、Tool、MCP 和 Memory capability。
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
3. 定义 knowledge retrieval profile contract：`standard` = 标准检索，`deep` = 深度检索。
4. 定义 index capability contract：基础索引必选，图谱增强索引与 OCR / 多模态解析可选。
5. 提供 `deep_without_graph` 降级语义：深度检索请求遇到 graph index 未就绪时，不报错，改用基础索引、多轮重查、强 rerank 和 citation coverage check。
6. 提供 Static GraphRAG baseline runner，为 Program 6 对照组准备。
7. 继续把外部 Elasticsearch / Milvus / Neo4j 写成 adapter boundary 和 Target，不伪装 Current。

验收：

- 同一 query 能产生 retrieval trace、evidence bundle 和 citation source tracing。
- trace 能记录 `requested_profile`、`effective_profile` 和 `fallback_reason`。
- GraphRAG baseline runner 可被 Program 6 eval 调用。
- unsupported claim metrics 可读。

## 主线程 Coordinator 规则

1. Program 1 PHASE07 已按旧 Program 2 语境生成四个 thread prompts；启动本 program 时必须先刷新为当前 Program 4 语境，并引用 Program 3 async ingestion infrastructure closure evidence。
2. 用户在 Codex UI 中创建或确认四个真实目标模式线程。
3. 每个线程必须确认 worktree、branch、status、allowed paths、forbidden paths。
4. 每个线程完成前必须验证、commit、push。
5. 主线程读取 diff 和验证结果，不只信总结。
6. 合并顺序建议：GraphRAG / Index -> Memory & Context Engine -> Capability / Skill / Tool / MCP / Sandbox -> Security / Governance -> docs / verifier 收口。

## Program 4 验证基线

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
