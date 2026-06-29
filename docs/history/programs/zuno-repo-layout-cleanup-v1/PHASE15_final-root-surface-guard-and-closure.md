# PHASE06 Final Root Surface Guard And Closure

> 状态：completed / archived。

## 目标

完成 Program3 最终收口：根目录只保留 `__init__.py`、`main.py` 和六层目录；旧 alias 由内部兼容机制承接；Program3 归档。

## 最终目标树

```text
src/backend/zuno/
├─ __init__.py
├─ main.py
├─ api/
├─ agent/
├─ memory/
├─ capability/
├─ knowledge/
└─ platform/
```

## 需要修改的文件

- `tools/scripts/verify_repo_structure.py`
- `.agent/scripts/verify_agent_system.py`
- `tests/repo/test_repo_structure_consistency.py`
- `tests/repo/test_agent_system.py`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/references/current-program.md`
- `docs/architecture/current-architecture.md`
- `docs/architecture/roadmap.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/README.md`

## 禁止修改的文件

- Program4 queued docs
- runtime feature code
- DB schema
- API/frontend/eval baseline

## 验收闸门

- `src/backend/zuno` 根目录没有零碎 alias `.py` 文件。
- 旧 public import path smoke matrix 通过。
- Program3 completed / archived。
- Program4/5 仍 queued / not active。

## 验证命令

```powershell
pytest -q -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
git diff --check
```
