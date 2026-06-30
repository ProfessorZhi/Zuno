# Program Closure Checklist

当前 active program：`zuno-master-architecture-implementation-v1`

state: active

## Program Closure 自维护审查

- [ ] `.agent/programs/current.md`、`.agent/programs/README.md`、`.agent/references/current-program.md`、`README.md` 和 `AGENTS.md` 是否写同一个 active program。
- [ ] `.agent/programs/` 是否只保留本 program 的 PHASE01-PHASE12。
- [ ] 上一轮 `zuno-architecture-detail-and-execution-plan-v1` 是否已归档到 `docs/history/programs/`。
- [ ] completed program 是否已归档到 `docs/history/programs/`。
- [ ] 八个方面产物是否都有代码、测试、文档和验证证据。
- [ ] `docs/architecture/architecture.md` 是否只把已证明能力写成 Current。
- [ ] `.agent/architecture/architecture.md` 是否与 `docs/architecture/architecture.md` byte-consistent。
- [ ] `docs/architecture/architecture.html` 和 `.agent/architecture/architecture.html` 是否由 renderer 生成且一致。
- [ ] README 是否反映当前 program 状态、目标架构和下一阶段。
- [ ] `AGENTS.md` 是否同步新的工作流规则和读文档顺序。
- [ ] verifiers/tests 是否覆盖新目录布局、active program、architecture mirror、compat import 和 release gates。
- [ ] verifier / tests 是否覆盖新规则。
- [ ] 如果用户提醒“以后注意”，不能只留在对话里，必须判断是否写回 AGENTS、`.agent/references/`、templates、verifier 或 tests。
- [ ] `__pycache__`、`.pytest_cache`、本地输出、临时报告和运行产物是否没有进入 git。
- [ ] 兼容 import 仍通过 `tests/legacy_guards/test_zuno_alias_imports.py` 或后继等价测试保护。
- [ ] 安全、评测、文档解析和工具审批未完成部分是否仍标记为 Target/Future。

## 最小验证命令

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q -p no:cacheprovider
```

## 归档要求

完成后归档到：

```text
docs/history/programs/zuno-master-architecture-implementation-v1/
```

归档必须包含：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `closure-summary.md`
- `PHASE01` 到 `PHASE12`
