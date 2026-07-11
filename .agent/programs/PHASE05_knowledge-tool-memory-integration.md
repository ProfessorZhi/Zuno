# PHASE05 Knowledge Tool Memory Integration

```yaml
program: zuno-real-unified-runtime-cutover-v1
phase: PHASE05_knowledge-tool-memory-integration
state: pending
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

- Knowledge 缺失时 blocked，不再 synthetic evidence。
- filesystem.read 有 workspace containment、max bytes 和 trace。
- filesystem.write 有 approval、atomic write、idempotency、allowed extension 和 audit trace。
- Memory pre-turn read、in-turn selected refs、post-turn raw event / summary / pending Reflexion candidate 可观测。
- PDF -> index -> corrective retrieval -> EvidenceLedger -> synthesis -> page citation 最低纵向链路通过。

## 验证命令

```powershell
pytest -q tests/agent/runtime tests/e2e -p no:cacheprovider
python tools/scripts/verify_real_runtime_cutover.py --enforce-knowledge-tool-memory
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
git diff --check
```

