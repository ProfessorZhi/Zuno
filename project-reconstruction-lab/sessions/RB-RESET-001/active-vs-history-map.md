# Active vs History Map

| 内容 | 当前归属 | 当前是否可执行 | 说明 |
|---|---|---:|---|
| `05-red-blue/README.md` | Active | 否 | 只说明 RESET/PAUSED 和入口 |
| `05-red-blue/principles.md` | Active | 否 | 只保留稳定原则 |
| `05-red-blue/workflow-status.md` | Active | 否 | 当前状态与可读性门 |
| `05-red-blue/history/` | History | 否 | 旧 Protocol、Prompt、指南 |
| `sessions/RB-WORKFLOW-*` | Immutable History | 否 | 原始执行证据，不改写 |
| `sessions/RB-RESET-001` | Audit Record | 否 | 本次重置记录 |
| `docs/project/architecture/` | Canonical Target | 不由本目录触发 | 本轮只做可读性基线收口 |
| `tools/scripts/verify_red_blue_*` | Compatibility Verification | 否 | 验证历史 Artifact 或旧格式 |
| 下一代 Protocol | 未设计 | 否 | 必须等可读性门通过并由用户激活 |

必要的旧路径指针只负责让不可变 Session 的历史链接继续可达；它们不包含旧 Protocol 内容，
也不应出现在新的工作流路由中。
