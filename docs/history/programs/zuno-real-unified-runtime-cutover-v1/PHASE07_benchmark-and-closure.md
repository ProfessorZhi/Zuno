# PHASE07 Benchmark And Closure

```yaml
program: zuno-real-unified-runtime-cutover-v1
phase: PHASE07_benchmark-and-closure
state: completed
```

## 目标

运行或诚实阻塞 fixed EnterpriseRAG paired benchmark，输出 implementation_status、measurement_status、quality_gate_status，归档 program 并恢复 no-active。

## 范围

- `tools/evals/zuno/**`
- `tests/evals/**`
- `.agent/programs/**`
- `docs/history/programs/zuno-real-unified-runtime-cutover-v1/**`
- `docs/architecture/**`
- `README.md`

## 禁止范围

- 不写死本机 embedding/model 地址。
- 不人工挑选只对 agentic 有利的问题。
- 不把 implementation tests passed 写成 quality pass。
- 不把 blocked / prepared / partial profile 写成 measured。

## 验收闸门

- [x] sample-8 尝试运行或输出 precise blocked_reason。
- [x] fixed 80-case set 不存在时创建 tracked manifest 或记录 blocked_reason。
- [x] release gate 只在完整 measured profile 时判断 pass / fail。
- [x] 合法结果只能是：

```text
implementation_complete + measurement_pass + quality_pass
implementation_complete + measurement_pass + quality_fail
implementation_complete + measurement_blocked + quality_not_proven
```

## 完成证据

- raw EnterpriseRAG parquet run blocked: `.local/evals/raw/enterprise_rag_bench/hf/data/questions/test.parquet` 不存在，runner 抛出 `FileNotFoundError`。
- tracked sample-8 JSONL run timed out after 184 seconds，partial artifacts 只包含 baseline / local / deep profile，缺 agentic profile 和顶层 `metrics.json` / `report.md`。
- final status: `implementation_complete + measurement_blocked + quality_not_proven`。

## 验证命令

```powershell
pytest -q tests/evals tests/agent/runtime tests/api -p no:cacheprovider
python tools/scripts/verify_real_runtime_cutover.py --enforce-product-cutover
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
git diff --check
```
