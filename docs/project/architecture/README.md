# Zuno 架构文档

`docs/project/architecture/` 是唯一正式总体架构目录，只能保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## 职责

- `architecture.md`：Product、Domain、Logical Capability、Physical Service/Deployment 的跨层关系、全局边界、读取顺序和 Current/Target/History。
- `architecture-views.md` + `architecture.html`：不可拆分的 Mermaid 展示配对，不拥有独立事实。
- `README.md`：维护规则和入口，不承载专题 Contract。

专题设计必须放在 `docs/project/<topic>/`，不能重新塞回 architecture 目录。当前 Canonical Taxonomy 和服务边界由 `docs/decisions/` 下的 [`ADR-0011`](../../decisions/0011-architecture-document-taxonomy.md)、[`ADR-0010`](../../decisions/0010-microservice-target-and-service-boundaries.md) 维护。

## Priority

```text
Accepted ADR / Shared Contract
→ Domain / Owner专题文档
→ architecture.md 跨域组合
→ architecture-views.md + architecture.html 展示
```

Current 状态必须回到 `docs/status/`、`docs/evidence/` 和最新代码；Target 文档不能证明部署或生产就绪。

## Maintenance

含义变化时先修改对应专题 Owner 文档，再同步总架构和图源；图形关系变化时运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
```

禁止创建第五个文件、`.agent/architecture/` 镜像或第二套 Service/Domain/State 清单。
