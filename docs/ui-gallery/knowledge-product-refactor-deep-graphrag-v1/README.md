# Knowledge Product Refactor + Deep GraphRAG V1 UI Snapshot Audit

- Generated at: 2026-06-19T18:29:24.246919+00:00
- Commit SHA: `caf1c394d2035a3acff273b7aa62de4be21b89ba`
- Previous baseline commit: `8b44326`
- Capture method: load root preview page, navigate client-side to target routes, intercept `/api/**` with audit-safe mock data, then export screenshots and HTML snapshots.
- This is the responsive hardening after snapshot for tablet/mobile settings shell layout.

## Pages

- `domain-pack-list`: 领域包列表页
- `domain-pack-create`: 领域包创建页
- `domain-pack-detail`: 领域包详情页
- `knowledge-create-wizard`: 知识库创建向导
- `knowledge-maintenance`: 知识库维护页
- `legacy-knowledge-config-route`: 旧配置路由对比快照（当前会收口到 settings 页面）

## Viewports

- desktop: `1440x1000`
- tablet: `1024x900`
- mobile: `390x844`

## Focus

- 修复 tablet/mobile 下 settings shell 的布局压缩问题
- 让主内容优先可见，避免横向滚动和主内容掉到首屏之外
- 保持产品层文案只暴露“标准检索 / 增强检索”
