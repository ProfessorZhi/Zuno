# PHASE10 Validation Release Closure

Program: `zuno-eight-deliverables-full-realization-v1`
status: active

## 为什么

完整 program 只有在文档、代码、验证、历史归档和提交推送都闭环后才算完成。否则八交付物会再次变成“做过一些”而不是“可证明完成”。

## 范围

覆盖交付物：

- 1-8 全部。

主要目标：

- 全量 verifier/test/eval 证据。
- docs / `.agent` / README 状态同步。
- program 归档到 `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`。
- `.agent/programs/` 回到 no-active 或下一 program 明确等待态。
- commit / push / PR closure。

## 执行步骤

1. 汇总每个 phase 的证据、diff、测试和剩余风险。
2. 运行 full validation stack。
3. 修正 Current / Target / Future / History 漂移。
4. 归档 completed program，清空前台 PHASE 文件。
5. 最后提交、推送，并准备 PR / release summary。

## 验收

- 八个交付物都有文件、代码或验证证据支撑。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/` 保存完整 program。
- `.agent/programs/current.md` 不再误报 active program。
- verifier/tests 固定完成态，防止下一轮漂移。

## 必跑验证

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
```

Runtime phase 完成后还必须运行对应 backend focused tests 和 eval comparison。
