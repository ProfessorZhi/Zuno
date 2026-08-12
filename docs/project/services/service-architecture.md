# Service Architecture：逻辑能力如何形成服务？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 哪些能力值得独立部署，哪些应该是 library/worker/provider？
owner: Service Architecture / Infrastructure
replaces: old 11-module physical interpretation and `docs/project/modules/11-infrastructure.md` (Superseded)

## Part A — Architecture Narrative

服务边界来自不同 workload 和 failure/security domain，而不是来自旧的 11 个逻辑模块或用户数量。
一次案件分析会同时产生短事务（Matter/Review）、长任务（Agent Run）、CPU/GPU/IO 重活（OCR、索引、
Graph Build）和受保护副作用（Sandbox）。把它们都塞进一个进程会让资源竞争、故障恢复和安全审计
互相干扰；把每个逻辑名词都拆成服务又会带来网络延迟、schema 漂移和分布式故障。
这里要解决的问题是如何用最少的部署边界隔离这些差异，而不是把“微服务”当成默认答案。

因此当前 Target 只保留候选五类 network-facing role，并允许能力以 library、worker 或 Provider
存在。Domain Service 是 Canonical State 的唯一写者，Agent Runtime 只拥有控制状态，Knowledge
只产生候选，Tool/Sandbox 只拥有 EffectReceipt。Service count、Model Gateway、Memory 和 Eval
是否独立，必须由独立扩缩容、失败隔离、安全边界、生命周期或可测收益证明。

典型失败是服务 A 已提交本地事务但队列或服务 B 超时；系统不能用重试风暴或跨服务 JOIN 掩盖未知
结果，而应通过 idempotency、Outbox/Inbox（如必要）和 reconciliation 收口。若一个模块化单体
加独立 worker 已经满足相同的资源和安全边界，就应合并服务。

## Part B — Detailed Architecture Specification

### Service admission contract

服务候选必须声明 API/schema version、state owner、resource profile、failure domain、security boundary、
retry/idempotency、trace correlation 和 replacement path。HTTP 适合 CRUD/query/small command，
durable queue 适合长任务，MCP/API 适合外部互操作；gRPC 只有在 serialization/latency benchmark
通过后才采用。服务不得读取其他服务的私有表或通过网络重建第二套 Domain 状态机。
Transient delivery failure 才允许 bounded retry；命令和 Job 依靠幂等键收敛，unknown outcome
必须进入 reconciliation，不能用重复投递掩盖失败。

## Service set

Target candidate is five network-facing Python service roles; the count is revisable:

| Service | API | state/contract owner | heavy workers |
|---|---|---|---|
| `edge-api` | FastAPI external ingress, auth, SSE, routing | delivery correlation only | none |
| `platform-domain-service` | Matter, Review, Domain command/query, authorization | Canonical Domain State | domain outbox/reconcile worker |
| `agent-runtime-service` | Run submit/status/control, stream | Runtime Control State | agent runner, profile workers |
| `knowledge-service` | upload/ingestion/retrieval/evidence query | Knowledge projections and candidates | parse, embed, index, graph workers |
| `tool-sandbox-service` | prepared action, sandbox, MCP/API adapters | Tool Attempt/Effect Receipt | sandbox/effect/reconcile workers |

Eval/Observability is an independently deployable batch/trace worker, not a V1 synchronous business service. Legal Intelligence、Model Gateway、Memory 和 Agent profiles remain providers/libraries/workers until service evidence appears.

## Why not 11 services

11 is a logical ownership history. A service is allowed only for independent scaling, failure, security/resource isolation, deployment, availability, data ownership or lifecycle. A shared Python image, package or database does not remove a service boundary; conversely a logical capability does not create one.

## Contract rules

- Service API carries versioned commands, queries, proposals, references, snapshots and receipts.
- No service reads another service's private tables or performs cross-service SQL JOIN.
- Domain Service is the only writer of accepted business state.
- Runtime never writes Domain final state directly.
- Knowledge never writes Finding directly.
- Tool never writes Agent Plan or legal fact.
- Security decisions are owned by the security policy authority and enforced by every relevant service.

## Current / Target / Gap

- Current：Compose has one backend application container, one worker application container and one frontend; infrastructure dependencies are not business services.
- Target：candidate network-facing service roles plus independently scaled workers；服务数量不因本表冻结。
- Gap：service images, API contracts, schema ownership, fault injection, tracing, deployment and on-call evidence。
