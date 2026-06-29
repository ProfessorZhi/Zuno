# 验证选择 Skill

## When To Use

当任务需要选择最小有效验证、解释失败、同步 verifier/test，或准备 commit/push 收尾时使用本 skill。

## Mental Model

```text
changed surface
  -> smallest proof that can fail for the right reason
  -> verifier for structure
  -> focused pytest for regressions
  -> broader gate only when blast radius grows
```

## Current Truth

`.agent/scripts/` 是过渡期验证器位置。当前本地 Agent Skill System 的最小验证基线是：

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

## Target Direction

长期目标是把稳定自动化放进 `tools/agent` / `tools/verify`，并把工作流防回归测试集中到 `tests/agent_system`。当前阶段只同步现有过渡期脚本和 `tests/repo/test_agent_system.py`。

## Must Preserve

- 验证失败先追根因，不绕过检查。
- 修改 docs / `.agent` 后必须至少跑结构 verifier 和 focused pytest。
- Runtime、frontend、eval 任务要追加模块级验证；文档任务不主动扩大到 runtime。
- 六层薄入口变更要追加对应 `tests/agent/test_*_layer_surfaces.py` 和 `tests/repo/test_static_target_layer_imports.py`。

## Before Editing

1. 先按 `.agent/system.yaml` 看路径推荐 verify。
2. 再按 `task-routing.md` 判断 task type。
3. 如果修改 verifier/test，先读失败输出和现有断言。
4. 如果验证要求改禁止路径，停止并返回证据。

## Allowed Changes

- 更新验证命令地图。
- 同步 `.agent/scripts/verify_agent_system.py`、`.agent/scripts/verify-workflow.ps1`、`tests/repo/test_agent_system.py` 的 expected phrases。
- 同步 `tools/scripts/verify_repo_structure.py`、`.agent/scripts/verify_doc_boundaries.py` 和 `tests/repo/test_repo_structure_consistency.py` 的 archive / no-active 断言。
- 为新 skill 文件结构增加轻量断言。

## Forbidden Changes

- 不删除失败断言来让验证变绿。
- 不把目标行为写成 Current 来通过文档验证。
- 不在文档任务中修改 runtime 代码以满足无关测试。

## Common Failure Patterns

- `.agent/references/` 文件改名后 verifier 仍检查旧 canonical set。
- `system.yaml` 新增 docs_sync 或 templates 后 test 没覆盖。
- PowerShell verifier 只检查路径，不检查 skill 结构，导致 references 退化成索引。
- `git diff --check` 最后才跑，发现尾随空格后又需要重新验证。

## Debug Playbooks

### Agent system verifier 失败

1. 看失败是 missing path、unexpected path、missing phrase 还是 canonical set。
2. 对照 `AGENTS.md` 和 `.agent/system.yaml` 判断哪边是新真相。
3. 修正文档、verifier 和 tests，避免只改断言。

### Workflow verifier 失败

1. 先确认路径是否存在。
2. 再确认 `.gitignore` 和 retired paths。
3. 最后跑 `python .agent/scripts/verify_agent_system.py` 看结构检查。

### Pytest 失败

1. 读断言的文件和 phrase。
2. 判断 phrase 是否仍是当前 contract。
3. 如果 contract 变了，同步文档和 verifier；如果文档漏了，补文档。

## Focused Tests

文档 / Agent system：

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

六层薄入口：

```powershell
pytest -q tests/agent/test_agent_layer_surfaces.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_capability_layer_surfaces.py tests/agent/test_knowledge_layer_surfaces.py tests/agent/test_platform_layer_surfaces.py -p no:cacheprovider
pytest -q tests/repo/test_static_target_layer_imports.py -p no:cacheprovider
```

PHASE05 Context / Memory foundation：

```powershell
pytest -q tests/agent/test_context_contracts.py tests/agent/test_context_orchestrator.py tests/agent/test_memory_layers.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py -p no:cacheprovider
```

PHASE06 Capability / ToolCard / MCP foundation：

```powershell
pytest -q tests/agent/test_capability_system.py tests/agent/test_capability_registry.py tests/agent/test_capability_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py -p no:cacheprovider
```

PHASE07 Hooks / Evidence / Trace / Artifact foundation：

```powershell
pytest -q tests/agent/test_hooks_evidence_trace_artifacts.py tests/agent/test_general_agent_project_query_runtime.py tests/agent/test_knowledge_layer_surfaces.py tests/api/test_knowledge_api_contract.py tests/evals/test_multihop_eval_real_runtime_runner.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py -p no:cacheprovider
```

PHASE08 GraphRAG 知识运行时基础验证：

```powershell
pytest -q tests/agent/test_knowledge_graphrag_runtime_contracts.py tests/agent/test_general_agent_project_query_runtime.py tests/agent/test_knowledge_layer_surfaces.py tests/api/test_knowledge_api_contract.py tests/graphrag/test_graphrag_project_contracts.py tests/graphrag/test_graphrag_project_loader.py tests/graphrag/test_structured_graph_extractor_contract.py tests/retrieval/test_enhanced_retrieval_composition.py tests/evals/test_multihop_eval_real_runtime_runner.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py -p no:cacheprovider
python tools/evals/zuno/contract_review_eval/run_contract_eval.py --profiles dev_offline,dev_local,demo --output-dir .local/evals/zuno/phase08/contract_review
```

PHASE09 Runtime Upgrade Integration foundation 验证：

```powershell
pytest -q tests/agent/test_agent_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py tests/agent/test_general_agent_project_query_runtime.py tests/agent/test_hooks_evidence_trace_artifacts.py tests/evals/test_multihop_eval_real_runtime_runner.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py -p no:cacheprovider
python .agent/scripts/verify_module_boundaries.py
```

文档入口扩大验证：

```powershell
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

仓库卫生扩大验证：

```powershell
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_repo_hygiene.py -p no:cacheprovider
```

历史兼容 grep：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/grep-domain-pack.ps1
git grep -n "00-architecture-index.md"
```

## Docs Sync

修改验证规则时同步：

- `.agent/system.yaml`
- `.agent/references/workflow.md`
- `.agent/references/task-routing.md`
- `.agent/references/docs-map.md`
- `.agent/scripts/verify_agent_system.py`
- `.agent/scripts/verify-workflow.ps1`
- `.agent/scripts/verify_doc_boundaries.py`
- `tools/scripts/verify_repo_structure.py`
- `tests/repo/test_agent_system.py`
- `tests/repo/test_repo_structure_consistency.py`

## Lessons Learned

好验证不是命令越多越好，而是失败时能指向正确层级：路径、边界、词条、历史归档或 runtime 行为。
