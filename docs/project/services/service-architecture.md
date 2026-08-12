# Service Architecture：逻辑能力如何形成服务？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 哪些能力值得独立部署，哪些应该是 library/worker/provider？
owner: Service Architecture / Infrastructure
replaces: old 11-module physical interpretation and `docs/project/modules/11-infrastructure.md` (Superseded)

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

## Round-002 Target refinements（D005、D009、D011）

Model Gateway、Memory、Legal Intelligence 和 Eval 默认是 library/provider/worker，而不是因为
逻辑名称就独立成 network-facing service。它们只有在独立资源池、失败域、部署生命周期、配额/安全
边界或可测吞吐收益成立时，才获得独立服务候选资格。

Tool/Sandbox 则按安全和副作用边界保留独立候选：`PreparedAction` 在执行时重新授权，EffectReceipt
记录 provider operation ID 和 unknown outcome，Tool 服务不能写 Domain final state。队列和服务调用
必须可重试、可取消、可对账；Round-002 不冻结具体 MQ、gRPC、容器编排或服务数量。
