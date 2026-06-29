# PHASE01 Alias Inventory And Target Contract

> 状态：completed / archived。

## 目标

重新定义 Program 3 的最终完成标准：`src/backend/zuno` 根目录不再保留零碎 compatibility alias `.py` 文件，只保留 `__init__.py`、`main.py` 和六层目录。

## 范围

- 只做审计、文档、目标契约和 verifier/test 的预备规则。
- 生成旧 import path inventory。
- 明确哪些 alias 属于低/中/高风险。

## 需要修改的文件

- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/references/current-program.md`
- `.agent/references/zuno-repo-hygiene.md`
- `.agent/references/code-map.md`
- `docs/architecture/roadmap.md`
- `docs/architecture/target-architecture.md`
- `tests/repo/test_repo_structure_consistency.py`
- `tools/scripts/verify_repo_structure.py`

## 禁止修改的文件

- `src/backend/zuno/**` runtime implementation
- `apps/**`
- `infra/**`
- DB schema / migration files
- eval baselines

## 执行步骤

1. 用 `rg` 统计旧 import path 使用面：`zuno.services`、`zuno.core`、`zuno.database`、`zuno.schema`、`zuno.tools`、`zuno.utils`、`zuno.config`、`zuno.resources`、`zuno.compatibility`、`zuno.settings`、`zuno.mcp_servers`、`zuno.middleware`、`zuno.evals`。
2. 把根级 alias 文件分成低风险、中风险、高风险三组。
3. 在正式架构文档中写明最终根目录目标树。
4. 更新 Program3 状态，确认 Program4 仍 queued / not active。

## 验收闸门

- 文档明确写出最终根目录只允许 `__init__.py`、`main.py` 和六层目录。
- 没有 runtime 行为修改。
- Program4 未被打开。

## 验证命令

```powershell
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
git diff --check
```
