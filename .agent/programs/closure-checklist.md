# Program Closure Checklist

program: `zuno-production-architecture-and-deliverables-completion-v1`
state: active

## Phase 顺序

- [x] PHASE01 production maturity gap audit
- [x] PHASE02 program truth source and execution system
- [x] PHASE03 workflow self maintenance automation
- [x] PHASE04 documentation dedup architecture clarity
- [x] PHASE05 repo ownership and compatibility retirement
- [x] PHASE06 product surface desktop recovery loop
- [x] PHASE07 production parse and index platform
- [x] PHASE08 durable agent runtime persistence
- [x] PHASE09 memory context production governance
- [x] PHASE10 tool sandbox vault network runtime
- [x] PHASE11 production graphrag evidence citation
- [ ] PHASE12 security trace eval release closure

## 四大总交付物

- [ ] 工作流自洽与自我维护：长期规则能被分类、写回、模板化并进入机器检查。
- [ ] 文档系统清晰无冗余：前台文档少而精，architecture / production-readiness / program / history 边界清楚。
- [ ] 文件夹和代码 ownership 清晰：六层 owner 清楚，compatibility / vendor / legacy alias 只承担必要临时桥接。
- [ ] 架构功能完整实现：八类 runtime-first 交付物达到 production target 或保留明确 Remaining Target 证据。

## 八类 runtime-first 交付物

- [ ] 产品闭环。
- [x] 文档解析与索引。
- [x] Agent Runtime。
- [x] Memory 与 Context。
- [x] Tool Control Plane 与 Sandbox。
- [x] Knowledge / GraphRAG / Evidence / Citation。
- [ ] Security / Trace / Eval / Release。
- [ ] 仓库治理与一致性。

## Program Closure 自维护审查

- [ ] `AGENTS.md` 是否需要更新。
- [ ] `.agent/system.yaml` 的 route、docs_sync、verify 是否需要更新。
- [ ] `.agent/references/` 是否有新的 skill、lesson、pitfall 或 debug playbook 要沉淀。
- [ ] `.agent/templates/` 是否需要新增或修正执行骨架。
- [ ] `.agent/programs/` 是否完成归档并回到明确状态。
- [ ] completed program 是否已归档到 `docs/history/programs/`。
- [ ] `docs/architecture/architecture.md` 的 Current / Target / Future / History 是否仍严格区分。
- [ ] `.agent/architecture/architecture.md` 是否与 `docs/architecture/architecture.md` 完全一致。
- [ ] 两个 `architecture.html` 是否由同一个 Markdown 源生成且可通过渲染校验。
- [ ] verifier / tests 是否覆盖新规则，避免下次漂移。

## 必须归档的证据

- [x] PHASE01 maturity gap audit。
- [ ] 四大总交付物 closure table。
- [ ] 八类 runtime-first deliverables closure table。
- [ ] owner map 和 import matrix。
- [ ] external dependency / blocked evidence matrix。
- [ ] trace / eval / release baseline。
- [ ] full verification log。
- [ ] final `git status --short --branch`。
- [ ] final commit hash。
- [ ] push status。

## 不允许关闭的情况

- [ ] 任何 Target / Future 被写成 Current，但没有代码、测试、trace、eval 或 verifier 证据。
- [ ] `.agent/programs/`、`README.md`、`AGENTS.md`、`.agent/references/current-program.md` 对 program 状态不一致。
- [ ] `docs/architecture/architecture.md` 和 `.agent/architecture/architecture.md` 不一致。
- [ ] `architecture.html` 不是由当前 Markdown 生成。
- [ ] compatibility / vendor / legacy alias 被删除但没有 import matrix 和 tests。
- [ ] full pytest 或 required verifier 失败且没有 blocked evidence。

## 最终验证命令

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
