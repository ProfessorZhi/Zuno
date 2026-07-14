# PHASE07 Model Gateway Runtime

phase_id: PHASE07
status: planned
depends_on: PHASE05, PHASE06
owner: Module 04 Model Gateway

## Phase 目标

让所有真实 Chat、Embedding、Rerank 和 Judge 调用统一经过 Model Gateway，支持角色路由、Capability、Attempt、Streaming、Structured Output、Usage、Quota、Timeout、Cancel、Retry/Fallback、Circuit 和 Trace。业务代码中直接 Provider SDK 调用最终归零。

## Minimal Read Set

- `docs/modules/04-model-gateway.md`
- PHASE03 Model Contract
- PHASE05 Security/SecretLease
- PHASE06 Trace/Audit
- PHASE01 provider bypass inventory

## Current Anchors

```text
src/backend/zuno/platform/model_gateway/**
langchain-openai / anthropic / dashscope imports
embedding and rerank provider calls
agent/model executors
knowledge extractor/query rewriter
observability judge/eval calls
```

## Allowed Paths

```text
src/backend/zuno/platform/model_gateway/**
module adapters calling gateway ports
tests/model_gateway/**
tests/integration/model_gateway/**
tools/scripts/*model*bypass*.py
docs/evidence/**
```

## Forbidden Paths

- Agent/Knowledge/Memory/Tool/Observability 直接 Import Provider SDK。
- Gateway 决定 Agent Plan、Knowledge Evidence 或 Eval Gate。
- 隐藏 Provider Retry 或 Usage。

## Work Packages

### P07-T01 Model Definition, Role and Capability Registry
- Goal：实现 provider/model/version/capability/context/structured/streaming/region/cost/risk registry。
- Tests：unsupported role/capability、inactive model、config hash、version immutability。
- Acceptance：Planner 只请求 RoleRequirement，不写 provider name。

### P07-T02 Routing Policy and Snapshot
- Goal：实现 Role→candidate→policy→resolved route，固定 routing snapshot/hash。
- Tests：tenant policy、data residency、model unavailable、cost ceiling、deterministic tie-break。
- Acceptance：一次 Attempt 绑定不可变 resolved route。

### P07-T03 Provider Adapter SPI
- Goal：OpenAI-compatible、Anthropic、DashScope、Embedding/Rerank Adapter 统一 request/response/error/cancel。
- Tests：schema mapping、timeout、provider error、stream chunk、cancel、secret audience。
- Acceptance：Provider SDK 只存在 adapter 目录。

### P07-T04 ModelAttempt Lifecycle and Structured Output
- Goal：实现 attempt_no、request hash、status、raw/normalized refs、validation/repair/failure。
- Tests：invalid JSON、schema mismatch、partial stream、retry exhausted、late response。
- Acceptance：模型输出是 Proposal，验证后才交给调用 Owner。

### P07-T05 Usage, Quota and Settlement
- Goal：记录 estimated/settled token、cost、provider receipt、reservation/release、quota。
- Tests：settlement delay、duplicate receipt、hidden retry、quota reject、cancel settlement。
- Acceptance：Estimated 不冒充 Settled；Budget Owner 可对账。

### P07-T06 Retry, Fallback, Circuit and Cancellation
- Goal：定义 transient retry、parameter repair、stronger model escalation、provider fallback、circuit、deadline/cancel。
- Tests：429/5xx/timeout、invalid output、circuit open/half-open、cancel race、fallback trace。
- Acceptance：Retry 仍属同一任务执行，不触发 Agent Replan。

### P07-T07 Bypass Cutover and Guard
- Goal：迁移全部真实调用到 Gateway，先 shadow/compare，再默认新路径，最终移除直接 SDK。
- Tests：静态 Bypass Guard 归零；Agent/Knowledge/Eval vertical tests 只产生 Gateway Attempt。
- Acceptance：生产代码无 `legacy_model` 目录、无直接 provider client；旧 adapter/flag 有 PHASE22 删除。

## Phase 完成定义

- 所有真实模型/Embedding/Rerank/Judge 调用经过 Gateway。
- Attempt、Usage、Retry/Fallback、Cancel、Trace 完整。
- 直接 Provider SDK Import Guard 归零。
- 新目录清晰，无 Legacy Model Gateway 包。

## Validation

```bash
git diff --check
python tools/scripts/verify_model_gateway_target_protocols.py
pytest -q tests/model_gateway tests/integration/model_gateway -p no:cacheprovider
python tools/scripts/verify_model_gateway_bypass.py
```
