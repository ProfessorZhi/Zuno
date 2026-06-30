# PHASE02 Project Folder And Code Layout Cleanup

status: pending

## 目标

先把项目文件夹、代码 ownership、compat/vendor 边界和本地缓存噪音整理清楚，再进入 runtime feature implementation。

## 关键判断

`src/backend/zuno` 顶层六层已经清楚，真正需要治理的是六层内部：`platform/services` 过胖、`capability/tools` 和 `capability/mcp/servers` 视觉上零碎、`platform/compatibility` 同时承载 alias 和 vendor、旧 import 仍通过 compatibility matrix 保护。

## 步骤

- [ ] 生成 backend ownership matrix，覆盖 `api / agent / memory / capability / knowledge / platform`。
- [ ] 清理未跟踪 `__pycache__`、`.pytest_cache` 和本地临时产物。
- [ ] 盘点 `platform/services` 中每个子目录的 target owner。
- [ ] 盘点 `capability/tools` 与 `capability/mcp/servers` 的 provider / builtin / compat 分类。
- [ ] 设计 `compat import registry` 与 `platform/vendor` 分离方案。
- [ ] 更新 `tools/scripts/verify_repo_structure.py` 和 repo tests，固定新目录规则。

## 验收

- 读者能从 README 和 ownership matrix 判断每个目录做什么。
- 本地缓存不出现在 VS Code 项目树的结构判断中。
- 旧 import path 不被破坏。
- 新 runtime 代码不会继续写入 compatibility。

## 验证

```powershell
git ls-files | rg "__pycache__|\\.pyc$"
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_repo_hygiene.py
pytest -q tests/repo/test_repo_structure_consistency.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider
```
