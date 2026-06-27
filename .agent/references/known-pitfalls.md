# 已知坑 Skill

## When To Use

当任务涉及归档、旧路径、Domain Pack 兼容、目标架构边界、BM25 / GraphRAG 术语、或验证失败根因判断时使用本 skill。

## Mental Model

已知坑不是禁止列表集合，而是防止把已经关闭的问题重新打开。每条都要对应一个保护边界：Current truth、Target direction、History archive、或 Migration compatibility。

## Current Truth

- Phase 0-6 架构收口是历史完成事实。
- Phase 11C active runtime cleanup 已完成。
- Domain Pack 只保留在 migration alias、旧数据库兼容、eval CLI 兼容、retirement/history tests 等受限语境。
- `.agent` 当前是 Zuno Local Agent Skill System。

## Target Direction

近期目标继续保持 modular monolith、Single GeneralAgent、Context / Memory foundation、Capability / Tool Retrieval、Knowledge / GraphRAG Retrieval、Evidence / Trace / Eval。Java、microservices、event workers 和 product-level multi-agent mode 是未来方向，不是当前实现路线。

## Must Preserve

- Retired Domain Pack surfaces must not be restored into the target layout.
- 不恢复 root `domain-packs/`、`DomainQAGraph`、retired Domain Pack runtime sources、former `tests/compat/` holding area。
- 不恢复 `docs/architecture/phases/`、`docs/architecture/plans/`、`docs/architecture/programs/` 当前前台目录。
- 不提交 `data/`、`reports/`、`.local/`、`.codex/`、`node_modules/` 或 `.agent/local/*`。
- 不把 `.agent/references/` 扩回长架构正文；详细目标设计属于 `.agent/architecture/near-term/`。
- 不把 Elasticsearch 称为 BM25 算法本体；Native BM25 是目标本地算法，Elasticsearch 是 optional adapter。

## Before Editing

1. 搜索涉及术语的当前命中。
2. 分类为 Current、Target、History、Compatibility。
3. 确认用户允许范围。
4. 如果需要动禁止路径，停止并返回证据。

## Allowed Changes

- 将新发现的可复用失败模式补入本文。
- 将旧材料归档到 `docs/history/` 并同步入口。
- 为防回归增加 verifier/test 词条。

## Forbidden Changes

- 不为了“清理干净”删除历史证据。
- 不把 compatibility 命中误判为 active product surface。
- 不用泛化目录如 `common`、`helpers`、catch-all `utils` 承接新设计。
- 不把 archived near-term 01-19 fragments 当作 active target source。

## Common Failure Patterns

- grep 看到 `domain_pack_id` 就全删，破坏 migration compatibility。
- 看到旧 program 仍在 history 就误以为 active program 未关闭。
- 为了让文档更短，把 Current / Target / History 边界删掉。
- 把 `.agent/templates/` 当成知识库，复制项目规则。

## Debug Playbooks

- Domain Pack 命中：跑 `.agent/scripts/grep-domain-pack.ps1`，分类为 compatibility、history、target reference 或 bug。
- 旧路径命中：先判断是否在 `docs/history/`，历史命中一般保留。
- 术语冲突：以 `docs/architecture/current-architecture.md` 和代码/测试证据判断 Current，以 `.agent/architecture/near-term/` 判断 Target。

## Focused Tests

```powershell
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_hygiene.py -p no:cacheprovider
```

## Docs Sync

新增坑位时检查：

- `.agent/references/workflow.md`
- `.agent/references/verification-map.md`
- `.agent/references/docs-map.md`
- `.agent/system.yaml`
- relevant verifier/test

## Lessons Learned

最危险的回归通常不是代码坏了，而是 Agent 读到旧前台材料后恢复了已退休方向。
