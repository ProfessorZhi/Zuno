# Program Roadmap

state: completed
program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
active_program: none
current_phase: none
latest_completed_program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`

## Suite 结果

`zuno-enterprise-agentic-graphrag-production-suite-v1` 已完成三个前台 program：

1. Program 1：`zuno-production-document-ingestion-and-thread-foundation-v1`，completed / archived。
2. Program 2：`zuno-enterprise-document-ingestion-platform-v2`，completed / archived。
3. Program 3 Mega：`zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`，completed / archived。

## Program 3 Mega 结果

原 Program 3 / 4 / 5 / 6 已合并并完成：

- `zuno-enterprise-ingestion-async-infrastructure-v1` -> merged into Program 3 Mega。
- `zuno-runtime-subsystems-parallel-v1` -> merged into Program 3 Mega。
- `zuno-agent-planning-integration-v1` -> merged into Program 3 Mega。
- `zuno-enterprise-knowledge-eval-benchmark-v1` -> merged into Program 3 Mega。

核心链路：

```text
企业内部资料
  -> 多格式解析
  -> Document IR
  -> durable ingestion facts
  -> async parse / index workers
  -> index / graph handoff
  -> Memory & Context Engine
  -> Capability Layer
  -> Planning & Control Runtime
  -> Single Controller Agentic GraphRAG
  -> cited answer / artifact / trace / cost / eval
  -> launchable product baseline
```

## 完成的 Phase Gate

1. `PHASE01_truth-source-and-merge-plan.md`：completed。
2. `PHASE02_shared-contract-freeze.md`：completed。
3. `PHASE03_enterprise-ingestion-async-infrastructure.md`：completed。
4. `PHASE04_knowledge-retrieval-and-graphrag-profile.md`：completed。
5. `PHASE05_memory-context-engine.md`：completed。
6. `PHASE06_capability-skill-tool-mcp-layer.md`：completed。
7. `PHASE07_security-governance-envelope.md`：completed。
8. `PHASE08_model-gateway-cost-latency.md`：completed。
9. `PHASE09_planning-contract-and-strategy-selector.md`：completed。
10. `PHASE10_react-reflection-replan-reflexion-runtime.md`：completed。
11. `PHASE11_workspace-product-api-frontend-sync.md`：completed。
12. `PHASE12_end-to-end-product-runtime.md`：completed。
13. `PHASE13_eval-trace-cost-benchmark.md`：completed。
14. `PHASE14_docs-architecture-expansion.md`：completed。
15. `PHASE15_verification-archive-closure.md`：completed。

## 后续路线

当前没有 active program，也没有 queued program。下一轮如果要推进生产级部署，应先打开新 program，并把真实 PostgreSQL / RabbitMQ / Redis / MinIO / external OCR / VLM / external index / external observability 的 dependency probe、focused tests 和 rollback boundary 放在 PHASE01 / PHASE02。
