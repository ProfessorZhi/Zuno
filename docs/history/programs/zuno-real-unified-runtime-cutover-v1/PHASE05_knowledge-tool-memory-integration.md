# PHASE05 Knowledge Tool Memory Integration

```yaml
program: zuno-real-unified-runtime-cutover-v1
phase: PHASE05_knowledge-tool-memory-integration
state: completed
```

## 目标

让 Knowledge、Tool 和 Memory 真实进入 unified runtime：Corrective retrieval 输出 EvidenceLedger，filesystem.read/write 成为真实本地工具，Memory 完成 pre/in/post-turn 和 Reflexion reuse。

## 范围

- `src/backend/zuno/agent/runtime/execution/knowledge_step.py`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/capability/**`
- `src/backend/zuno/memory/**`
- `tests/agent/runtime/**`
- `tests/e2e/**`

## 禁止范围

- 不伪造 evidence / citation。
- 不写入 workspace root 外路径。
- 不跳过 side-effect approval。
- 不把 Memory candidate 直接写入 approved long-term memory。

## 验收闸门

- [x] Knowledge 缺失时 blocked，不再 synthetic evidence。
- [x] filesystem.read 有 workspace containment、max bytes 和 trace。
- [x] filesystem.write 有 approval、atomic write、idempotency、allowed extension 和 audit trace。
- [x] Memory pre-turn read、in-turn selected refs、post-turn raw event / summary / pending Reflexion candidate 可观测。
- [x] PDF -> index -> corrective retrieval -> EvidenceLedger -> synthesis -> page citation 最低纵向链路通过。

## 完成证据

- `RuntimeStartRequest.knowledge_space_ids` 进入 ContextPack task_state，`KnowledgeStepExecutor` 能通过 unified runtime 读取 caller 选择的 knowledge space。
- PDF fixture 经 ParseGateway / KnowledgeIndexRuntime / CorrectiveAgenticRetrievalRuntime / EvidenceLedger / GroundedSynthesisEngine 形成 page citation vertical slice。
- filesystem.read / filesystem.write 由 Tool Control Plane 注册，write 仍需审批与 idempotency。
- Memory pre-turn read、post-turn raw event / summary / pending Reflexion candidate 和 approved Reflexion reuse 已由 focused runtime tests 覆盖。
- `pytest -q tests/agent/runtime tests/e2e -p no:cacheprovider` 通过。
- `python tools/scripts/verify_real_runtime_cutover.py --enforce-knowledge-tool-memory` 通过。

## 验证命令

```powershell
pytest -q tests/agent/runtime tests/e2e -p no:cacheprovider
python tools/scripts/verify_real_runtime_cutover.py --enforce-knowledge-tool-memory
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
git diff --check
```
