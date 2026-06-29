# Zuno 后端 Agent 规则

修改 `src/backend/zuno` 前先读：

1. `.agent/references/code-map.md`
2. `.agent/references/runtime-call-chain.md`
3. `.agent/references/workflow.md`

如果任务涉及后端架构替换、GraphRAG 边界、上下文/记忆或包布局，还要读：

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`

## 规则

- 路由层不拥有业务逻辑或检索策略。
- Application Service 负责用例编排。
- core 和 runtime 代码不能反向依赖 API 层。
- 公共契约变化必须同步 DTO、前端类型和测试。
- 检索、Agent、记忆和 GraphRAG 变更必须对齐对应参考文档和目标架构说明。
