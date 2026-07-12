# Agent 架构工作区

`.agent/architecture/` 只保留正式总架构的四个 Agent 镜像入口：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## 同步规则

- `.agent/architecture/architecture.md` 必须与 `docs/architecture/architecture.md` 一致。
- `.agent/architecture/architecture-views.md` 必须与 `docs/architecture/architecture-views.md` 一致。
- `.agent/architecture/architecture.html` 必须与 `docs/architecture/architecture.html` 一致。
- 模块设计放在 `.agent/modules/`，不得放入 `.agent/architecture/`。
- Current / Gap 状态读取 `docs/status/production-readiness.md`。
- ADR 读取 `docs/decisions/`。
- Repository ownership 与治理文档读取 `docs/governance/`。

修改总架构、图源或 HTML shell 后运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
```

## 文件职责

```text
.agent/architecture/architecture.md        总架构文字镜像
.agent/architecture/architecture-views.md  Mermaid 图源镜像
.agent/architecture/architecture.html      Architecture Atlas 镜像
.agent/architecture/README.md              本目录规则
```

Agent Core V2 模块设计位于：

```text
.agent/modules/06-agent-core-planning-control.md
```

正式文件位于：

```text
docs/modules/06-agent-core-planning-control.md
```

## 禁止

- 不在 `.agent/architecture/` 新增模块专题文档。
- 不把 Production Readiness、ADR、Program、实施计划或 ownership matrix 放进本目录。
- 不单独修改镜像文件；先修改 `docs/architecture/` 正式入口，再同步。
- 不把 Future Optional 写成 Current。
- 不恢复已归档的 split architecture docs。