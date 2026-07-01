# PHASE12 Security Trace Eval Release Closure

status: completed
previous_phase: PHASE11_production-graphrag-evidence-citation
completed_at: 2026-07-01

## 目标

完成 Security / Trace / Eval / Release 的生产级收口：外部 trace/eval、online eval、CI release gate、生产运维证据归档、全量验证和 program 归档。

## 范围

- input / retrieval / tool / output gates。
- DLP、prompt injection、cross-workspace leakage、redaction。
- LangSmith / OTel export、online eval、persistent trace store。
- CI release gate operations 和 evidence archive。

## 禁止范围

- 不把本地 release baseline 伪装成在线 eval 平台。
- 不跳过 Program Closure 自维护审查。
- 不在 full verification 失败时归档为 completed。

## 验收闸门

- 四大总交付物和八类 runtime-first 交付物都有 Current 证据或明确 Remaining Target。
- `docs/architecture/production-readiness.md`、`architecture.md`、README、AGENTS、current-program、verifier 和 tests 一致。
- program 已归档到 `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`。
- `.agent/programs/` 回到明确状态。

## 验证命令

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-docs.ps1
pytest -q -p no:cacheprovider
```

## 需要先读取

- `.agent/programs/closure-checklist.md`
- all `.agent/programs/PHASE*.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/architecture.md`
- `.agent/references/current-program.md`
- `tools/scripts/verify_docs_entrypoints.py`
- `tools/scripts/verify_repo_structure.py`
- `.agent/scripts/verify_agent_system.py`
- `.agent/scripts/verify-workflow.ps1`

## 需要修改的文件

- `src/backend/zuno/platform/security/**`
- `src/backend/zuno/platform/observability/**`
- `tools/evals/zuno/**`
- `.github/workflows/**` only if CI release gate is in scope
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `.agent/programs/**`
- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/**`
- verifier / tests touched by final state transition

## 执行拆解

1. 收口 input / retrieval / tool / output 四道 gate，确保 DLP、prompt injection、cross-workspace leakage、redaction 有测试或 Remaining Target。
2. 接通 LangSmith / OTel export adapter、persistent trace store 或明确 blocked evidence。
3. 建立 online eval / CI release gate operations；无法接外部平台时保留 local baseline + adapter contract + Remaining Target。
4. 更新 production-readiness：只把已验证能力升 Current。
5. 归档 active program，写 closure summary，更新 current state。
6. 运行完整验证、提交、推送，证明 main / origin 对齐。

## 多 agent 分工

- Thread A：security gates / DLP / leakage tests。
- Thread B：trace / eval / external sink adapter。
- Thread C：CI release gate / evidence archive。
- Thread D：docs / history / verifier final state。
- 主线程：最终 full verification、diff review、archive、commit、push。

## 需要返回的证据

- 四大总交付物 closure table。
- 八类 runtime-first deliverables closure table。
- Current / Remaining Target / Future 边界。
- release evidence index。
- full verification log。
- archive path、commit hash、push status、main/origin 对齐证明。

## 停止条件

- full verification 失败且无法在当前 phase 修复。
- 生产级能力没有证据却被要求写成 Current。
- 归档会丢失 active program evidence。

## 完成证据

- `docs/architecture/production-readiness.md` 已更新四大总交付物和八类 runtime-first 交付物闭环；未接入外部平台的 LangSmith / OTel sink、online eval、persistent trace store 和 CI release gate operations 保持 Remaining Target。
- `.agent/programs/` 已回到 no-active 等待态，PHASE01-PHASE12 已归档到本目录。
- `AGENTS.md`、README、`.agent/references/current-program.md`、`.agent/references/verification-map.md`、verifier 和 repo tests 已同步 no-active / latest completed archive 规则。
- full verification 结果记录在 `closure-summary.md`。
