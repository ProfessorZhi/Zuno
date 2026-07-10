# PHASE02 lean-architecture-markdown

status: completed
program: zuno-lean-complete-product-architecture-v1

## 目标

重写 Markdown 事实源和前台文档，使 Zuno 的近期目标从大规模企业平台收缩到 Lean Complete Agentic GraphRAG Product，同时保留可实施架构细节。

## 必改范围

- `docs/architecture/architecture.md`
- `README.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/document-ingestion-foundation.md`
- `docs/architecture/agent-core-runtime.md`
- `docs/architecture/capability-and-skill-layer.md`
- `docs/architecture/agentic-retrieval-planner.md`
- `docs/architecture/eval-observability-and-cost.md`
- `docs/architecture/input-layer-and-document-processing.md`
- `docs/architecture/knowledge-space-product-configuration.md`
- `.agent/architecture/README.md`
- `.agent/references/docs-map.md`
- `.agent/references/documentation-governance.md`

## architecture.md 必须包含

- 项目定位与边界。
- 用户产品场景。
- 黄金端到端链路。
- 六个运行域按统一模板展开。
- 代码 ownership matrix。
- 配置化和禁止写死契约。
- 核心状态对象和 restart recovery 边界。
- 错误、fallback、trace、metrics、focused tests 和 E2E 验收。
- Runtime 完成与质量完成的区别。
- Agentic GraphRAG fixed benchmark gate 和 measurement blocked 语义。
- Future Optional 简短章节。

## 禁止

- 不把 `architecture.md` 改成宣传页。
- 不复制历史 phase 清单。
- 不把 Production Scale 写成近期 blocker。
- 不修改 runtime。
