# Zuno Workflow Doc System V1 执行计划

Program ID：`zuno-workflow-doc-system-v1`

## 目标

先把本地文档系统和 Agent 工作流收口成自洽、可验证、可继续维护的项目级工作流。这个 program 不升级 runtime，不做目录物理迁移，也不重做架构 HTML。

## 为什么先做

后续目标架构升版、文件夹整理和 runtime 升级都会修改大量文档与边界。如果工作流本身不清楚，后面的 program 会继续靠临时提示词和人工记忆推进，容易重新漂移。

## 执行 Phase

1. [PHASE01：工作流与文档系统只读审计](PHASE01_workflow-doc-audit.md)
2. [PHASE02：Agent bootloader 与 routing 收口](PHASE02_agent-bootloader-routing.md)
3. [PHASE03：Skill / Template / Program 系统收口](PHASE03_skill-template-program-system.md)
4. [PHASE04：Workflow verifier 与漂移测试](PHASE04_workflow-verifiers-drift-tests.md)
5. [PHASE05：Program closure 与 history 归档](PHASE05_closure-history-archive.md)

## 并行规则

- PHASE01 可以拆成 3 个只读线程：`docs`、`.agent`、`tests/verifiers`。
- PHASE03 可以拆成 2-3 个线程：`references skills`、`templates`、`program layout`。
- PHASE02、PHASE04、PHASE05 建议串行，由主线程或单一写入线程负责。
- 所有子线程必须使用独立 worktree、独立 branch、Codex UI 目标模式和线程内部多 agent。

## 停止条件

- 不改 runtime 行为、API、DB schema、依赖、frontend 产品行为或 eval baseline。
- 不把 queued program 当成 active program。
- 不把 `.agent/references/` 写成普通索引；它只能沉淀 skill / lesson / playbook。
- 不在当前 program 里追加 PHASE06+；需要继续则新开 program。
- 每次新 program 都从 `PHASE01` 开始编号。

## 后续 Program 队列

- Program 2：`.agent/architecture/future/programs/zuno-target-architecture-refresh-v1/`
- Program 3：`.agent/architecture/future/programs/zuno-repo-layout-cleanup-v1/`
- Program 4：`.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- Program 5：`.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

## 验证

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_hygiene.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```

## 参考

- `AGENTS.md`
- `.agent/system.yaml`
- `.agent/references/`
- `.agent/templates/`
- `docs/architecture/roadmap.md`
- `.agent/architecture/future/programs/`
