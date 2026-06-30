# zuno-eight-deliverables-full-realization-v1

> 状态：completed / archived。此目录是历史证据，不是当前 active program。

## 目标

把 Zuno 最终成品的八个内部交付物完整落到文档、目标架构、代码结构、runtime contracts、验证和收口证据中，而不是只做 architecture markdown / HTML 或最小实现。

## Phase 与 PR

| Phase | 目标 | PR |
| --- | --- | --- |
| PHASE01 | Program boot baseline | https://github.com/ProfessorZhi/Zuno/pull/4 |
| PHASE02 | Workflow self-maintenance system | https://github.com/ProfessorZhi/Zuno/pull/5 |
| PHASE03 | Architecture docs / HTML system | https://github.com/ProfessorZhi/Zuno/pull/6 |
| PHASE04 | Query router / mode policy | https://github.com/ProfessorZhi/Zuno/pull/7 |
| PHASE05 | Context builder / memory system | https://github.com/ProfessorZhi/Zuno/pull/8 |
| PHASE06 | Capability ToolCard / MCP system | https://github.com/ProfessorZhi/Zuno/pull/9 |
| PHASE07 | Hooks / evidence / trace / artifact system | https://github.com/ProfessorZhi/Zuno/pull/10 |
| PHASE08 | GraphRAG knowledge runtime system | https://github.com/ProfessorZhi/Zuno/pull/11 |
| PHASE09 | Runtime upgrade integration | https://github.com/ProfessorZhi/Zuno/pull/12 |
| PHASE10 | Validation release closure | https://github.com/ProfessorZhi/Zuno/pull/13 |

## 八交付物完成证据

| 交付物 | 证据 |
| --- | --- |
| Agent 工作流文档系统 | `AGENTS.md`、`.agent/README.md`、`.agent/references/workflow.md`、`.agent/programs/current.md`。 |
| 元工作流自我维护系统 | `.agent/references/workflow-governance.md`、`.agent/references/workflow-update-policy.md`、`.agent/references/workflow-maintenance-checklist.md`、`verify_agent_system.py`。 |
| 模板与执行计划系统 | `.agent/templates/`、本目录的 `implementation-roadmap.md`、`closure-checklist.md` 和 PHASE01-PHASE10。 |
| 正式架构文档系统 | `docs/architecture.md`、`docs/architecture/README.md`、`docs/architecture/current-architecture.md`、`docs/architecture/target-architecture.md`、`docs/architecture/roadmap.md`。 |
| 架构 HTML 展示系统 | `docs/architecture.html` 由 `tools/agent/render_architecture.py` 从 `docs/architecture.md` 生成并由 `--check` 验证。 |
| 完善的 Zuno 目标架构 | `.agent/architecture/near-term/`、`docs/architecture/target-architecture.md`、PHASE04-PHASE09 foundation slices。 |
| 清晰干净的代码和目录 | `src/backend/zuno/api|agent|memory|capability|knowledge|platform` 六层、legacy alias compatibility guard、module boundary verifier。 |
| 一致性与验证系统 | `.agent/scripts/verify_agent_system.py`、`.agent/scripts/verify_doc_boundaries.py`、`.agent/scripts/verify_repo_hygiene.py`、`tools/scripts/verify_repo_structure.py`、repo tests、focused backend tests 和 eval comparison。 |

## 关键边界

本 program 没有把 Target 或 Future 写成 Current。PHASE04-PHASE09 是 foundation slices，不表示完整产品级 runtime upgrade、生产级 Memory DB、DB schema 迁移、frontend trace panel、完整动态工具编排、Java / 微服务 / event worker 或 Zuno runtime 多 Agent 架构已经完成。

Codex 线程内多 agent 只是执行协作方式，不是 Zuno runtime 当前架构。

## 完成验证

PHASE10 关闭前必须重新运行：

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_module_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
pytest -q tests/agent/test_agent_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py tests/agent/test_general_agent_project_query_runtime.py tests/agent/test_hooks_evidence_trace_artifacts.py tests/evals/test_multihop_eval_real_runtime_runner.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py -p no:cacheprovider
python tools/evals/zuno/contract_review_eval/run_contract_eval.py --profiles dev_offline,dev_local,demo --output-dir .local/evals/zuno/phase10/contract_review
```

最终验证结果以 PHASE10 closure commit / PR 的命令输出为准。

## 后续

当前 `.agent/programs/` 已回到 no-active 等待态。打开下一轮 program 前必须重新确认 worktree、branch、允许范围、禁止范围，并从 `PHASE01` 开始。
