# ADR-0009：Python-only 后端 Target

- 状态：`accepted-target`
- 日期：2026-08-13
- 基线：`0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f`
- 关联：`project-reconstruction-lab/sessions/RB-ARCH-REFRAME-V1/`

## Context

Zuno 同时包含 FastAPI API、Agent orchestration、RAG/NLP、模型 Provider、数据库、消息队列、Sandbox 和异步 Worker。Java/Spring 在企业事务、安全、强类型、JVM 并发和人才池上有真实优势；Python 也有 GIL、CPU 任务、依赖体积和长期维护风险。本决策不能用“AI 都用 Python”替代工作负载和边界分析。

## Decision

Zuno 后端 Target 采用 Python-only。FastAPI/Pydantic、SQLAlchemy/SQLModel、LangGraph、PyTorch、Transformers 和 RAG/NLP Provider 共用 Python Contract、类型、测试和观测语义；外部 Java/Spring 系统通过 HTTP、gRPC candidate、MCP/API 或消息 Contract 集成。

Python-only 不是单进程性能承诺：

| Workload | Target 处理方式 |
|---|---|
| HTTP、CRUD、短命令、模型/API/DB 等待 | FastAPI async/application service；保持 request thread 短 |
| Agent long-running、replan、HITL、model calls | Agent worker / queue；独立 timeout、retry、checkpoint 和资源池 |
| OCR、解析、embedding、rerank、graph build、batch eval | CPU/GPU/IO worker；可调用 PyTorch/CUDA/ONNX 或 native-backed engine |
| Sandbox、filesystem/network、secret、tool effect | 独立安全/资源进程或服务；不在 API request 中执行不受控副作用 |

必须用 Python 类型、Schema、lint、静态检查、Contract/Fault/E2E 测试和 workload benchmark 约束动态语言风险。FastAPI 不能承担 CPU-heavy 任务；Python-only 也不能掩盖 native backend 的资源和许可证边界。

## Rejected Alternatives

- Java + Python 双后端：当前没有跨语言收益证据，增加 DTO/RPC/Tracing/Failure/Build/Deployment 复杂度；外部 Java 集成不要求内部第二语言。
- Python 单进程：无法隔离长任务、CPU/GPU、Sandbox 和批处理故障。
- 仅以 QPS/用户数选择语言：不解释 workload 类型和数据/安全边界。

## Consequences

正面：统一 AI/Agent/数据生态、Schema 和调试方式，减少跨语言 Contract 复制；外部企业系统仍可互操作。

负面：需要显式 worker、资源隔离、类型纪律、依赖治理和性能 Benchmark；如果 Python worker 的总运维成本显著高于第二语言，必须重开 ADR。

## Reversal Criteria

只有在固定 workload、数据、SLO、资源和团队条件下，跨语言 Spike 证明 Python-only 的性能、可靠性、安全或维护总成本不可接受，才允许引入第二后端语言。Java/Spring 的一般成熟度本身不是 reversal evidence。

## Current / Target / Gap

- Current：仓库证据为 Python 3.12、FastAPI、Docker Python base、`zuno.main:app`；未发现 Java/Spring repo match。
- Target：Python-only services + independent workers。
- Gap：真实 workload profile、CPU/GPU queue SLO、性能/成本、团队维护和外部部署证据未完成。
