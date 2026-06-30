# PHASE11 Architecture Docs HTML Refresh

status: pending

## 目标

把 PHASE02-PHASE10 已完成的事实同步到正式架构 Markdown、Agent 架构镜像、架构 HTML、README 和图集，让展示页和代码事实一致。

## 步骤

- [ ] 更新 `docs/architecture/architecture.md` 的 Current / Target / Future。
- [ ] 更新十类 Mermaid 图，展示文件夹治理、企业场景、Document Ingestion、Runtime、Memory、Tool、GraphRAG、安全、Eval。
- [ ] 运行 renderer 同步 `.agent/architecture/architecture.md` 和两个 HTML。
- [ ] 更新 README 当前架构和 active program 状态。
- [ ] 更新 AGENTS.md 工作流和读文档顺序。

## 验收

- Markdown 内容比 HTML 更充实。
- HTML 以图为主，可以展示各模块二级细节。
- docs 和 agent architecture mirrors byte-consistent。

## 验证

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```
