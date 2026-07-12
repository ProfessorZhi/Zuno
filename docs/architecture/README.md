# 架构文档

`docs/architecture/` 只保留 Zuno 的四个 canonical 架构入口：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## 文件职责

- `architecture.md`：重文字的目标总架构设计，说明项目定位、十一逻辑模块、六个物理运行域、核心 Contract、状态、失败语义和完成标准。
- `architecture-views.md`：4+1、Views & Beyond 与 Zuno Product Core 的 Mermaid 规范图源。
- `architecture.html`：读取 `architecture-views.md` 的可视化 Architecture Atlas。
- `README.md`：本目录入口、边界和验证方式。

职责边界：

```text
architecture.md        讲总设计
architecture-views.md  维护规范图源
architecture.html      看图
README.md               讲目录规则
```

## 其他文档的位置

```text
docs/modules/       十一个逻辑模块的实施级设计
docs/status/        Current、Gap、Blocked、Completed、Future Optional
docs/decisions/     正式 ADR
docs/governance/    Repository ownership、文档与工程治理
docs/evidence/      可验证证据
docs/history/       过时计划、旧规格和历史材料
```

重要入口：

- Agent Core 模块：`docs/modules/06-agent-core-planning-control.md`
- Production Readiness：`docs/status/production-readiness.md`
- Repository Ownership Matrix：`docs/governance/repo-ownership-matrix.md`
- ADR：`docs/decisions/README.md`

禁止在 `docs/architecture/` 新增模块专题、状态报告、ADR、Program 或实施计划。

## 更新与验证

修改 `architecture.md`、`architecture-views.md` 或 HTML shell 后运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
```

生成器负责：

- 验证 `architecture.md` 的十一模块文字设计和核心 Contract；
- 验证 `architecture-views.md` 的 canonical views；
- 验证 HTML 使用 Mermaid v11 并读取独立图源；
- 同步 `.agent/architecture/architecture.md`；
- 同步 `.agent/architecture/architecture-views.md`；
- 同步 `.agent/architecture/architecture.html`。

模块文档镜像位于 `.agent/modules/`，不放入 `.agent/architecture/`。

## HTML 预览

HTML 通过 HTTP 读取 `/docs/architecture/architecture-views.md`。在仓库根目录运行：

```powershell
python -m http.server 8000
```

打开：

```text
http://localhost:8000/docs/architecture/architecture.html
```

## 历史入口

- 公开证据：`docs/evidence/public-demo.md`
- 旧架构清理工作集：`docs/history/architecture-surface-cleanup-2026-06-30/`
- 过时审计、旧规格、旧 phase、旧计划和旧 runbook 只保存在 `docs/history/`。