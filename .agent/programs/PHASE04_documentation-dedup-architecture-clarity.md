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

## 需要先读取

- `docs/architecture/README.md`
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `.agent/architecture/README.md`
- `.agent/architecture/architecture.md`
- `.agent/references/docs-map.md`
- `.agent/references/architecture-docs-map.md`
- `.agent/references/documentation-governance.md`
- `tools/scripts/verify_docs_entrypoints.py`

## 需要修改的文件

- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/README.md`
- `.agent/architecture/README.md`
- generated: `docs/architecture/architecture.html`、`.agent/architecture/architecture.md`、`.agent/architecture/architecture.html`
- `tools/scripts/verify_docs_entrypoints.py`
- `tests/repo/test_docs_entrypoints.py`

## 执行拆解

1. 建立前台文档职责表：README 只导航，architecture 讲架构，production-readiness 讲成熟度，program 讲执行，history 留证据。
2. 搜索重复 Current / Target / phase / deliverables 展开，压缩到唯一事实源。
3. 更新 architecture.md 中当前 active program 和实施落点，但不把 Production Target 写成 Current。
4. 运行 render_architecture 同步 HTML 和 `.agent/architecture` 镜像。
5. 更新 docs verifier/test，阻止旧拆分文档回到前台。

## 多 agent 分工

- Thread A：审计 README / docs/architecture。
- Thread B：审计 `.agent/architecture` 和 references。
- Thread C：更新 verifier/test。
- 主线程：修改 architecture.md、运行 renderer、审查镜像 diff。

## 需要返回的证据

- 文档职责表。
- 重复内容删除或保留理由。
- architecture Markdown / HTML sync 结果。
- docs entrypoint verifier 结果。

## 停止条件

- 需要恢复已归档拆分文档作为当前入口。
- Markdown 和 HTML 生成结果不一致。
- Current / Target 边界因文档压缩变模糊。
