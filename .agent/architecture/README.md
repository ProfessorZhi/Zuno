# Agent 架构工作区

`.agent/architecture/` 是 Agent 侧架构镜像，不是独立事实源。

## 同步规则

- `.agent/architecture/architecture.md` 必须与 `docs/architecture/architecture.md` 完全一致。
- `.agent/architecture/architecture.html` 必须与 `docs/architecture/architecture.html` 完全一致。
- 修改架构正文、Mermaid 图或 HTML Atlas shell 后运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
```

## 当前定位

Zuno 当前前台架构是 Lean Complete Agentic GraphRAG Product。

`architecture.md` 是详细实施蓝图与 Mermaid 图源；`architecture.html` 是十类 canonical views 的原生 Mermaid 图谱。收缩的是近期目标规模，不是文档精度。

HTML 通过 HTTP 读取 Markdown，预览方式见 `docs/architecture/README.md`。不得恢复旧的简化 offline SVG renderer。

状态事实源见 `docs/architecture/production-readiness.md`。

## 禁止

- 不在 `.agent/architecture/` 写入独立结论。
- 不单独修改镜像文件；先修改 `docs/architecture/` 正式入口，再运行同步命令。
- 不恢复已归档 split architecture docs。
- 不把 Future Optional 写成 Current。
