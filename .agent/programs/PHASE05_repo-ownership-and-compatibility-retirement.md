# PHASE05 Repo Ownership and Compatibility Retirement

status: active

## 目标

让文件夹结构和代码 ownership 真正清晰，减少零碎和凑合的兼容层，把真实 runtime owner 收回六层目录。

## 范围

- 盘点 `src/backend/zuno/api`、`agent`、`memory`、`capability`、`knowledge`、`platform`。
- 盘点 `platform/services`、`platform/compatibility`、`platform/vendor`、provider tree、legacy alias。
- 设计 import matrix、迁移顺序、兼容桥保留条件和退休条件。

## 禁止范围

- 不无测试删除 public import path。
- 不把 compatibility 当成新功能 owner。
- 不进行无关大重构。

## 验收闸门

- owner map 与 repo-ownership matrix 更新。
- legacy / compatibility / vendor guard 有测试。
- 至少完成一批低风险物理迁移或明确 blocked evidence。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider
```

## 需要先读取

- `docs/architecture/repo-ownership-matrix.md`
- `.agent/references/code-map.md`
- `.agent/references/runtime-call-chain.md`
- `.agent/references/zuno-repo-hygiene.md`
- `src/backend/zuno/*/README.md`
- `src/backend/zuno/platform/compatibility/legacy_aliases.py`

## 需要修改的文件

- `docs/architecture/repo-ownership-matrix.md`
- `src/backend/zuno/api/**`
- `src/backend/zuno/agent/**`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/capability/**`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/platform/**`
- `tools/scripts/verify_repo_structure.py`
- `.agent/scripts/verify_repo_hygiene.py`
- `tests/repo/test_backend_facade_layers.py`
- `tests/repo/test_static_target_layer_imports.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`

## 执行拆解

1. 建立 import matrix：旧 public path、当前 owner、目标 owner、compat bridge、test coverage。
2. 先迁移低风险 alias / facade / README owner，不碰数据库 schema 和 public API field rename。
3. 将 `platform/services` 中真实 runtime owner 分类为保留、迁移、thin facade、blocked。
4. 对 compatibility / vendor / provider tree 写明退休条件和禁止承载新功能规则。
5. 更新 repo structure verifier，让零碎路径不能重新扩散。

## 多 agent 分工

- Thread A：api / agent / memory owner map。
- Thread B：capability / knowledge owner map。
- Thread C：platform/services / compatibility / vendor / provider tree。
- Thread D：verifier/test guard。
- 主线程：审查 import matrix，合并低风险迁移。

## 需要返回的证据

- import matrix。
- compatibility retirement table。
- owner migration diff。
- import smoke test 和 static target layer test 结果。

## 停止条件

- 删除或改名 public import path 会破坏 legacy guards。
- 需要 database schema 或 API field rename。
- 同一 runtime owner 被两个目录同时承载且无法安全拆分。
