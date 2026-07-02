# 当前程序

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1

## 当前状态

`.agent/programs/` 当前没有 active program。

最近完成并归档的 program 是 Program 3 Mega：

- Program：`zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
- 中文名：Zuno 可上线企业知识库 Agentic GraphRAG 全链路闭环 Program
- 状态：completed / archived
- 归档：`docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`
- Suite：`zuno-enterprise-agentic-graphrag-production-suite-v1`

Program 3 Mega 已完成 PHASE01-PHASE15，把输入层、Knowledge / Retrieval / GraphRAG、Memory & Context Engine、Capability / Skill / Tool / MCP、Security / Governance、Model Gateway / Cost、Planning & Control Runtime、Eval / Trace / Benchmark、Product API / Frontend、E2E、文档和归档统一收口为本地可验证的 launchable product baseline。

成熟度和 runtime-first 交付物边界以 `docs/architecture/production-readiness.md` 为准。

最终结论：

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

## 当前 Front Path 文件

no-active 状态下，`.agent/programs/` 根目录只保留：

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/queued-programs/README.md`

completed program 的 PHASE 文件、closure evidence 和 merged queued inputs 已归档到：

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`

## 历史入口

- `zuno-production-document-ingestion-and-thread-foundation-v1`：Program 1，归档于 `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`。
- `zuno-enterprise-document-ingestion-platform-v2`：Program 2 / Product V1 local durable ingestion baseline，归档于 `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`。
- `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`：Program 3 Mega，已吸收原 `zuno-enterprise-ingestion-async-infrastructure-v1`、`zuno-runtime-subsystems-parallel-v1`、`zuno-agent-planning-integration-v1` 和 `zuno-enterprise-knowledge-eval-benchmark-v1`。
- `zuno-production-architecture-and-deliverables-completion-v1`：一次性交付型成熟化 program，归档于 `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`。
- `zuno-target-architecture-runtime-full-implementation-v1`：runtime-first / vertical-slice-first 闭环，归档于 `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`。
- `zuno-master-architecture-implementation-v1`：目标架构实现归档，归档于 `docs/history/programs/zuno-master-architecture-implementation-v1/`。

## 当前执行规则

- 新 program 必须先更新 `AGENTS.md`、`.agent/system.yaml`、`.agent/references/current-program.md`、verifier 和 repo tests，再从 `PHASE01` 开始。
- 不要从历史 archive 直接恢复旧 active phase 文件；历史只能作为证据和输入。
- Runtime 行为修改仍必须由 focused tests、E2E、trace/eval 或 verifier 证明后才能写成 Current。
- PostgreSQL、RabbitMQ、Redis、MinIO / S3、external OCR / VLM、external index、external observability sink 和 CI release gate operations 仍是 Production Scale Target，除非未来 program 接入真实 provider 并通过验证。
- Codex 多线程是工程执行方式，不是 Zuno 产品 runtime 多 Agent 架构；Zuno 近期 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
