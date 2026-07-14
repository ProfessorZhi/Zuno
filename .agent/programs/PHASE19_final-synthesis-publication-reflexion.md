# PHASE19 Final Synthesis, Publication and Reflexion

phase_id: PHASE19
status: planned
depends_on: PHASE10, PHASE13, PHASE16, PHASE18
owner: Module 06 Agent Core with 01/03/05 contracts

## Phase 目标

实现从已接受 Step/Join 结果到最终答案的完整闭环：Claim Extraction、Evidence/Citation Binding、Unsupported Claim、FinalCandidate、Deterministic Final Gate、条件式 Final Reflection、Publication、RunOutcome、BudgetSettlement、Product Delivery 和 ReflexionCandidate。不得由模型直接发布、写 Memory 或绕过证据/安全门。

## Minimal Read Set

- 模块 01、03、05、06、10 文档
- PHASE13 Context/Memory
- PHASE16 Tool Effect
- PHASE18 EvidenceLedger/Proposal
- PHASE10 Product Projection/Delivery
- 当前 synthesis/finalization/post_turn/publication code

## Current Anchors

```text
src/backend/zuno/agent/runtime/**final*|synthesis*|reflection*
src/backend/zuno/agent/post_turn/**
src/backend/zuno/knowledge/evidence/**
src/backend/zuno/memory/**reflexion*
src/backend/zuno/api/services/product/**
current final_answer/claims/citation binding surfaces
```

## Allowed Paths

```text
src/backend/zuno/agent/domain/finalization/**
src/backend/zuno/agent/application/finalization/**
src/backend/zuno/agent/runtime/**
src/backend/zuno/knowledge/evidence/** only owner APIs
src/backend/zuno/memory/** only candidate APIs
src/backend/zuno/api/services/product/delivery_service.py
src/backend/zuno/platform/database/agent/**
alembic/**
tests/agent/finalization/**
tests/integration/finalization/**
tests/fault/finalization/**
docs/evidence/**
```

## Forbidden Paths

- 模型直接创建 Publication/RunOutcome/ACTIVE Memory。
- Final answer 使用未绑定、已撤销或无权限 Evidence。
- Delivery success 反向修改 Publication。
- Reflection 无限循环或自动降低 AnswerPolicy。

## Work Packages

### P19-T01 Claim Extraction and Normalization
- Goal：从 synthesis proposal 提取 atomic claim、claim type、confidence、required evidence、safety classification。
- Tests：compound claim split、empty/format invalid、sensitive claim、duplicate claim、non-factual content。
- Acceptance：Claim 由 deterministic schema validator 接受，不保留隐藏 reasoning。

### P19-T02 Evidence and Citation Binding
- Goal：将 Claim 绑定 EvidenceItem/SourceSpan/CitationLineage，验证 authority、temporal、conflict、authorization、text availability。
- Tests：missing source、span hash mismatch、revoked document、conflicting evidence、citation inaccessible。
- Acceptance：Unsupported Claim 明确记录，不能伪造 citation。

### P19-T03 FinalCandidate Aggregate
- Goal：实现 answer content ref/hash、claims、citations、unsupported claims、policy refs、context/plan/evidence/model versions。
- Tests：immutability、duplicate candidate、stale PlanVersion、wrong snapshot、redaction。
- Acceptance：Candidate 不是 Publication，也不是 RunOutcome。

### P19-T04 Deterministic Final Gate
- Goal：检查 TaskContract、AnswerPolicy、Step Acceptance、Evidence Coverage、Citation、Security、Budget、Deadline、Tool UNKNOWN、Unresolved Conflict。
- Outcomes：PASS/REVISE/WAIT/ABSTAIN/FAIL/BLOCKED。
- Tests：simple task、strict grounded、unknown effect、citation missing、budget exceeded、security revoked。
- Acceptance：简单任务默认无需模型 Reflection，但必须经过 Gate。

### P19-T05 Conditional Final Reflection and Repair
- Goal：复杂/strict/high-risk 时使用 FINAL_CRITIC，输出 revise/retrieve/replan/abstain proposal，受轮次/预算限制。
- Tests：critic timeout/invalid、correct answer degraded、repeated no-change、replan required、fallback deterministic。
- Acceptance：Critic 不能直接发布或改 PlanVersion。

### P19-T06 Publication, RunOutcome and Budget Settlement
- Goal：原子提交 Publication ref、terminal RunOutcome、budget settled/estimated refs、trace/audit/outbox。
- Tests：publication commit crash、duplicate finalize、late usage settlement、delivery unavailable、cancel race。
- Acceptance：Publication 与 Delivery 分离；RunOutcome 只有 Agent Core 写。

### P19-T07 Product Delivery and Client Projection
- Goal：将 Publication 投影为 authorized message/claim/citation/artifact，创建 channel delivery/attempt/receipt。
- Tests：SSE disconnect、duplicate delivery、client render failure、revocation after publish、artifact authorization。
- Acceptance：Provisional Content 不成为正式 Assistant Message。

### P19-T08 ReflexionCandidate and Old Synthesis Cutover
- Goal：从 RunOutcome/Failure/Eval 生成长期经验 Candidate，进入 Memory Governance；迁移旧 post_turn/final answer path。
- Tests：sensitive/prompt-injected candidate、negative transfer、duplicate、rollback、no direct active memory。
- Acceptance：旧 synthesis/post_turn 主路径删除计划固定；最终无 `legacy_synthesis`/旧 publication 目录。

## Phase 完成定义

- Claim→Citation→FinalCandidate→Gate→Publication→RunOutcome→Delivery 可运行。
- Strict/Unsupported/Conflict/UNKNOWN/Revocation Fault Test 通过。
- Reflexion 只生成 Candidate，并经过 Memory Governance。
- 旧 Finalization 路径进入 PHASE21/22 删除清单。

## Validation

```bash
git diff --check
pytest -q tests/agent/finalization tests/integration/finalization tests/fault/finalization -p no:cacheprovider
python tools/scripts/verify_architecture_semantic_alignment.py
```
