# Zuno 架构文档

`docs/architecture/` 与 `.agent/architecture/` 只能保留：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## 正式设计事实

Zuno 正式架构设计事实共十三份：

```text
11 × docs/modules/<NN>-<module>.md
 1 × docs/architecture/architecture.md
 1 × docs/architecture/architecture.html
```

职责：

- `architecture.md`：十一模块的跨模块集成架构、全局不变量和端到端流程。
- `architecture.html`：总体架构的 Mermaid 可视化入口。
- `architecture-views.md`：HTML 的 Mermaid 渲染源，不是第二份文字总架构。
- `README.md`：目录、镜像和维护规则，不是架构正文。
- `docs/modules/`：每个领域 Owner 的唯一详细 Target 架构；领域细节冲突时以对应模块文档为准。

`.agent/architecture/` 是字节级镜像，不是独立事实源。

## 状态事实

```text
docs/status/production-readiness.md
docs/evidence/
最新 main 的代码、Migration、测试、Trace、Eval 与运行证据
```

负责 Current、Gap、Measurement 和 Production Readiness。Target 文档存在不能自动提升状态。

## 更新与验证

模块含义变化时先更新对应模块唯一文档，再同步总架构的跨模块关系。图形关系变化时同步 `architecture-views.md` 和 HTML。

```text
python tools/scripts/verify_architecture_document_set.py
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_architecture_document_set.py tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

禁止在 architecture 目录放置模块专题、状态报告、ADR、Program、Migration 计划或附件目录。
