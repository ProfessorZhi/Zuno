# Zuno Web Agent 规则

修改 `apps/web` 前先读：

1. `.agent/references/code-map.md`
2. `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`
3. `.agent/references/workflow.md`

如果任务涉及前后端契约迁移、页面边界或仓库布局，还要读：

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`

## 规则

- API 字段变化必须同步后端 DTO、前端类型和契约测试。
- 视觉、交互和页面布局变化要先做隔离预览，预览产物放到 `.agent/local/previews/<task-id>/`。
- 需要给用户确认的 UI 变更必须提供桌面截图，必要时补移动端截图。
- 用户确认前，不要把视觉原型直接落到生产页面。
- 修改后运行 lint、build 和受影响测试。
- 用户界面不要暴露内部路由、旧 GraphRAG 名称或只用于迁移兼容的字段。
