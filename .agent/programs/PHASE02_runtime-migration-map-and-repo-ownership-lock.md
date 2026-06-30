# PHASE02 runtime-migration-map-and-repo-ownership-lock

status: pending

## 目标

把 `platform/services/*`、`zuno.schema/*`、`zuno.database/*` 与六层 target tree 的真实 runtime owner 关系钉死，避免后续迁移靠视觉直觉推进。

## 范围

- 盘点旧 runtime 实现、当前 facade、目标 owner 和兼容路径。
- 更新 ownership matrix，使每个迁移项都有 current path、target owner、compat path、risk、tests 和 verifier。
- 明确哪些旧实现继续复用、哪些迁移、哪些冻结为 compatibility。

## 禁止范围

- 不为了目录清爽删除兼容路径。
- 不移动高风险 runtime 文件，除非 focused tests 已经覆盖。
- 不把 `platform/services` 写成已退休。

## 验收闸门

- migration map 覆盖 parser、retrieval、GraphRAG、memory、tool、database、workspace、storage、queue 和 sandbox。
- verifiers 固定 owner map，防止目标层和旧服务路径再次漂移。
- 后续 runtime phase 能按 map 判断允许路径和禁止路径。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_backend_facade_layers.py -p no:cacheprovider
```

