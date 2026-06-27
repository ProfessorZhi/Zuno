# Zuno Local Skills

`.agent/references/` 是 Zuno Local Agent Skill System 的本地项目 skill library。它不是普通索引目录，而是沉淀“在 Zuno 里怎么正确做事”的 skills、lessons、playbooks、失败模式、测试选择和文档同步规则。

## Mental Model

```text
AGENTS.md
  -> bootloader：入口、边界、阅读顺序、停止条件
.agent/system.yaml
  -> router：路径 -> skills -> templates -> docs_sync -> verify
.agent/references/
  -> local skills：可复用操作知识、失败模式、debug playbook、测试选择
.agent/templates/
  -> execution skeletons：只保存输出骨架，不保存项目知识
docs/
  -> formal truth：已实现、已验证、面向人的正式结论
docs/history/
  -> archive：完成、过时、被替换的证据和旧程序
```

## Current Truth

当前可用 skill 文件保持克制：

```text
.agent/references/
  README.md
  current-program.md
  docs-map.md
  task-routing.md
  workflow.md
  code-map.md
  runtime-call-chain.md
  verification-map.md
  command-catalog.md
  known-pitfalls.md
```

这些文件共同回答四件事：

- 任务该走哪条路。
- 修改前必须保护哪些边界。
- 出问题时先查哪一层。
- 收尾时跑哪些最小有效验证并同步哪些文档。

## Skill 文件标准

新增或重写的 `.agent/references/*.md` 如果承载本地 skill，应尽量使用以下结构。不是每个文件都必须机械填满所有段落，但缺少任一关键段落时，要能解释为什么。

```text
When To Use
Mental Model
Current Truth
Target Direction
Must Preserve
Before Editing
Allowed Changes
Forbidden Changes
Common Failure Patterns
Debug Playbooks
Focused Tests
Docs Sync
Lessons Learned
```

## Must Preserve

- `.agent/references/` 保存可复用项目知识，不保存一次性调查流水账。
- `.agent/templates/` 只保存执行骨架，不复制项目事实、目标架构正文或历史结论。
- `.agent/programs/` 保存当前 active phase 计划；完成或被替换的程序进入 `docs/history/programs/`。
- `.agent/architecture/near-term/` 保存目标架构细节；正式当前事实只能进入 `docs/`。

## Before Editing

1. 先读 `AGENTS.md` 和 `.agent/system.yaml`。
2. 按 `.agent/references/task-routing.md` 选择本地 skills。
3. 如果触碰 docs、`.agent` 或 history，读 `.agent/references/workflow.md`、`docs-map.md`、`verification-map.md`。
4. 如果触碰 runtime、API、eval 或前端，读对应模块 `AGENTS.md` 和 `.agent/references/code-map.md`。
5. 修改前确认任务允许范围；不允许的路径需要停止并返回证据。

## Common Failure Patterns

- 把 references 写成“目录有什么”的索引，导致下次 Agent 不知道怎么决策。
- 把一次性 run log 写进 references，导致 active skill 被噪音污染。
- 把 Target 架构写成 Current truth，绕过代码、测试和 trace 证据。
- 模板里塞项目知识，导致模板和 skills 同步漂移。
- 修改 docs / `.agent` 后没有同步 verifier 和 tests。

## Debug Playbooks

- 路由不清：先查 `.agent/system.yaml`，再查 `task-routing.md`，最后查 `docs-map.md` 或 `code-map.md`。
- 验证失败：先读失败输出，定位是路径缺失、词条漂移、历史归档、还是 Current / Target 边界错误。
- 文件该放哪不清：按 `docs/` formal truth、`.agent/references/` reusable skill、`.agent/templates/` skeleton、`docs/history/` archive 四类分类。

## Focused Tests

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

## Docs Sync

修改 references 时至少检查：

- `.agent/README.md`
- `.agent/system.yaml`
- `.agent/templates/README.md`
- `.agent/references/docs-map.md`
- `.agent/references/verification-map.md`
- `tests/repo/test_agent_system.py`

只有已实现并验证的正式结论才同步到 `docs/`。

## Lessons Learned

- 本地 skill 的价值不是文件多，而是让下一次执行少猜一步。
- 旧程序和历史证据应归档，不应静默删除。
- 每个 skill 都应能回答“为什么先读它、它保护什么、失败时怎么查”。
