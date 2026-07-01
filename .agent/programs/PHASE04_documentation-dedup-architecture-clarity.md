# PHASE04 Documentation Dedup Architecture Clarity

status: pending

## 目标

让文档系统清晰无冗余：`architecture.md` 讲目标架构，`production-readiness.md` 讲成熟度和交付物，program 文件讲执行，History 保存旧证据。

## 范围

- 检查 README、AGENTS、docs/architecture、.agent/architecture、.agent/references、docs/history 的重复和漂移。
- 保持 `docs/architecture/architecture.md` 与 `.agent/architecture/architecture.md` 镜像一致。
- 保持 HTML 由 Markdown 生成，不承载唯一事实。

## 禁止范围

- 不恢复 `current-architecture.md`、`target-architecture.md`、`roadmap.md`、`deliverables.md` 为当前前台。
- 不在 README / AGENTS 重复 phase 目录或 Production Target 细节。

## 验收闸门

- 前台文档入口少而精。
- 架构描述和生产成熟度边界清楚。
- 文档去冗余规则进入 verifier / tests。

## 验证命令

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-docs.ps1
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```
