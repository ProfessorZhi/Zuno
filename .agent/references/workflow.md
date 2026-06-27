# 工作流

本文件替代旧 workflow 目录。Zuno 的本地工作流由 `AGENTS.md` 总入口和 `.agent/references/` 参考文件共同组成。

## 通用执行流程

1. 读 `AGENTS.md`，确认任务边界。
2. 按 `.agent/references/task-routing.md` 判断任务类型。
3. 读 `docs/architecture/current-architecture.md`、`target-architecture.md`、`roadmap.md`。
4. 读 `.agent/references/docs-map.md`、`code-map.md`、`verification-map.md`。
5. 如果涉及目标架构，读 `.agent/architecture/near-term/` 和 `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`。
6. 执行最小必要修改。
7. 过时材料移动到 `docs/history/`，不留在前台路径。
8. 同步验证器和测试。
9. 运行最小有效验证。
10. 修改任务完成后 commit 并 push，除非验证或 push 被阻塞。

## 文档维护流程

- 前台文档默认使用中文。
- `docs/` 只放正式人类真相。
- `.agent/` 只放 Agent 工作流、参考、目标设计、当前 program、脚本和模板。
- `docs/history/` 统一存放旧 audit、旧 spec、旧 runbook、旧 UI 原型、旧 phase、旧 program 和被替换设计。
- 不把 transient screenshot、browser snapshot、cache 或 local report 提交到仓库。

## 仓库卫生流程

1. `git status --short`
2. 确认移动/删除目标在仓库内。
3. 搜索所有引用。
4. 移动到目标归档位置。
5. 更新 docs、`.agent`、verifier、test。
6. 运行 `git diff --check` 和相关 verifier/test。

## 架构重构流程

1. 先读 Current / Target / Roadmap。
2. 读 canonical HTML 和 near-term 设计。
3. 明确 Current / Foundation / Target / Future / History。
4. 目标设计放 `.agent/architecture/near-term/`。
5. 正式结论放 `docs/architecture/`。
6. 执行计划放 `.agent/programs/` 根层，当前状态、总目录、phase 文件和收口清单平铺，不再按 program 子目录嵌套。
7. 旧计划和旧设计放 `docs/history/`；如果执行计划被替换，旧计划从 `.agent/programs/` 当前前台移除。

## 具体执行步骤、停止条件、验证和收尾规则

- 如果修改范围触碰 forbidden path，停止并返回证据。
- 如果 Target 与 Current 边界不清，先修正文档边界。
- 如果当前验证器仍引用旧路径，先同步验证器和测试。
- 如果验证失败，先追根因再修。
- 修改任务收尾必须给出修改文件、验证结果、commit hash、push 结果和最终 `git status --short`。

## 验证基线

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/repo/test_agent_system.py tests/repo/test_repo_hygiene.py -p no:cacheprovider
```
