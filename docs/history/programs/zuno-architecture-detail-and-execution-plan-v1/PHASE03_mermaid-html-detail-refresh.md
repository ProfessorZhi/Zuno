# PHASE03 Mermaid 与 HTML 展示升级

status: completed

## 目标

保留十类 canonical 架构图，但把每张图从粗粒度模块图升级为二级组件图，并重新生成 `docs/architecture/architecture.html`。

## 范围

修改 Mermaid 图源、图清单和 renderer 展示宽度。

## 需要修改的文件

- `docs/architecture/architecture.md`
- `docs/architecture/architecture.html`
- `.agent/references/diagram-inventory.md`
- `tools/agent/render_architecture.py`
- `tools/scripts/verify_docs_entrypoints.py`
- `tests/repo/test_docs_entrypoints.py`

## 禁止修改的文件

- 不新增第 11 张 Mermaid 图，除非同步更新 `EXPECTED_DIAGRAMS`、deliverables、inventory 和 tests。
- 不手写 `docs/architecture/architecture.html`。

## 验收闸门

- `docs/architecture/architecture.md` 仍只有十个 Mermaid block。
- `docs/architecture/architecture.html` 由 renderer 生成。
- 十类图展示 Agent Core、Memory read/write、Tool Control Plane、Document Ingestion、Security、Trace / Eval、Tool adapter 和 GraphRAG 的二级组件。

## 验证命令

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## 需要返回的证据

- render command result
- architecture HTML sync result
- diagram contract test result

## 历史影响

本阶段不移动历史材料。
