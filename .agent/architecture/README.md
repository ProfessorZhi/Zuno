# Agent 架构工作区

`.agent/architecture/` 是 Agent 侧架构镜像，不是独立事实源。

## 同步规则

- `.agent/architecture/architecture.md` 必须与 `docs/architecture/architecture.md` 完全一致。
- `.agent/architecture/architecture-views.md` 必须与 `docs/architecture/architecture-views.md` 完全一致。
- `.agent/architecture/architecture.html` 必须与 `docs/architecture/architecture.html` 完全一致。
- 修改文字架构、图源或 HTML shell 后运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
```

## 当前定位

Zuno 当前前台架构定位是 Lean Complete Agentic GraphRAG Product：轻量实现、成熟设计。

文件职责：

```text
docs/architecture/architecture.md        重文字目标设计
docs/architecture/architecture-views.md  十类 Mermaid 图源
docs/architecture/architecture.html      可视化 Atlas
docs/architecture/production-readiness   Current 与差距
```

Agent 镜像目录对应为：

```text
.agent/architecture/architecture.md        重文字目标设计镜像
.agent/architecture/architecture-views.md  Mermaid 图源镜像
.agent/architecture/architecture.html      可视化 Atlas 镜像
```

`architecture.md` 重点说明十一模块、Agent 闭环、Memory、Planning、Tool/MCP/Skill、Agentic GraphRAG、Security、Observability、Infrastructure 和完成标准；HTML 重点展示模块关系和局部连线。

HTML 通过 HTTP 读取 `/docs/architecture/architecture-views.md`，预览方式见 `docs/architecture/README.md`。不得恢复旧的简化 offline SVG renderer。

状态事实源见 `docs/architecture/production-readiness.md`。

## 禁止

- 不在 `.agent/architecture/` 写入独立结论。
- 不单独修改镜像文件；先修改 `docs/architecture/` 正式入口，再运行同步命令。
- 不把 30 张详细图重新堆回 `architecture.md`。
- 不恢复已归档 split architecture docs。
- 不把 Future Optional 写成 Current。
