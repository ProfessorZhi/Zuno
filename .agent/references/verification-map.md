# 验证地图

## 工作流验证

```powershell
powershell -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## 文档入口验证

```powershell
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py
```

## Agent 系统验证

```powershell
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## 聚焦文档 / Agent 测试

```powershell
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/repo/test_agent_system.py tests/repo/test_repo_hygiene.py -p no:cacheprovider
```

## Git 与 diff 检查

```powershell
git status --short
git diff --stat
git diff --check
```

## 历史兼容 grep 检查

```powershell
git grep -n ".agentmd"
git grep -n ".agent.md"
git grep -n "<legacy lowercase Agent entrypoint filename>"
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/grep-domain-pack.ps1
```

第三条命令里的占位符要替换为已经退休的小写入口文件名。Domain Pack helper 会扫描 `Domain Pack`、`domain_pack`、`DomainQAGraph`、`MultiAgentSupervisorGraph` 和 `domain-packs`，并排除 `docs/history/**`。剩余命中必须分类为 Current compatibility、Target reference、Blocked Legacy 或需要修复的 bug。

## 标准架构 grep

```powershell
git grep -n "zuno-ideal-architecture-and-repo-layout.html"
```

该 HTML 只能是 `.agent/architecture/near-term/` 下的 Target / Proposed 视觉蓝图，不应被写成 Current truth。
