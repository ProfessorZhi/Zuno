# 架构文档

`docs/architecture/` 与 `.agent/architecture/` 都只保留四个 canonical 架构入口：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## 文件职责

- `architecture.md`：目标总架构文字事实源。
- `architecture-views.md`：4+1、Views & Beyond 与 Zuno Product Core 的 Mermaid 规范图源。
- `architecture.html`：读取 `architecture-views.md` 的 Architecture Atlas。
- `README.md`：目录边界、镜像和验证规则。

`.agent/architecture/` 是正式总架构的字节级镜像，不是独立事实源。

## 其他正式文档

```text
docs/modules/       十一个逻辑模块的实施级 Target 设计
docs/status/        Current、Gap、Blocked、Completed、Future Optional
docs/decisions/     正式 ADR
docs/governance/    Ownership 与文档治理
docs/evidence/      可复现证据
docs/history/       历史材料与研究附件
```

Agent Core Target 文档集：

```text
docs/modules/06-agent-core-planning-control.md
docs/modules/06-agent-core-control-protocols.md
docs/modules/06-agent-core-consistency-lifecycle-protocols.md
```

对应 Agent 镜像：

```text
.agent/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-control-protocols.md
.agent/modules/06-agent-core-consistency-lifecycle-protocols.md
```

Current / Gap 事实源：`docs/status/production-readiness.md`。

禁止在 architecture 目录新增模块专题、状态报告、ADR、Program、实施计划、附件目录或其他文件。

## 更新与验证

```text
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_agent_core_target_protocols.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

修改总架构、图源或 HTML 后必须同步正式文件和 `.agent` 镜像。模块设计镜像放在 `.agent/modules/`。
