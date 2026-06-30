# Program Closure Checklist

归档 program：`zuno-master-architecture-implementation-v1`

state: completed / archived

## Program Closure 自维护审查

- [x] `.agent/programs/current.md`、`.agent/programs/README.md`、`.agent/references/current-program.md`、`README.md` 和 `AGENTS.md` 已切换到 no-active / latest archived program。
- [x] `.agent/programs/` 已回到 no-active 等待态。
- [x] 上一轮 `zuno-architecture-detail-and-execution-plan-v1` 已归档到 `docs/history/programs/`。
- [x] completed program 已归档到 `docs/history/programs/`。
- [x] 八个方面产物都有代码、测试、文档和验证证据。
- [x] `docs/architecture/architecture.md` 只把已证明能力写成 Current。
- [x] `.agent/architecture/architecture.md` 与 `docs/architecture/architecture.md` byte-consistent。
- [x] `docs/architecture/architecture.html` 和 `.agent/architecture/architecture.html` 由 renderer 生成且一致。
- [x] README 反映 no-active 状态、目标架构和最近归档 program。
- [x] `AGENTS.md` 同步 no-active 工作流和读文档顺序。
- [x] verifiers/tests 覆盖新目录布局、no-active state、architecture mirror、compat import 和 release gates。
- [x] verifier / tests 是否覆盖新规则：已覆盖 no-active state、archive required paths、architecture mirror、docs entrypoints 和 backend facade guards。
- [x] 如果用户提醒“以后注意”，不能只留在对话里；本轮没有新的长期提醒需要写回。
- [x] `__pycache__`、`.pytest_cache`、本地输出、临时报告和运行产物没有进入 git。
- [x] 兼容 import 仍通过 legacy/import guard 测试保护。
- [x] 安全、评测、文档解析和工具审批未完成部分仍标记为 Target/Future。

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
