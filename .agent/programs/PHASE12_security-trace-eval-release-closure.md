# PHASE12 Security Trace Eval Release Closure

status: pending

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
