# Contradictions

## 处理方式

冲突不是自动选择一个更好听的版本。记录两边证据、适用范围和下一步核验。

| ID | Claim A | Claim B | 现状 | 下一步 |
|---|---|---|---|---|
| C-001 | 用户确认历史 OpenViking Memory/Context 接入 | 当前仓库未发现 OpenViking | `OPEN / 可解释`：历史项目与当前仓库可能不是同一快照 | 查旧代码、配置或 Artifact；不否定用户记忆 |
| C-002 | 用户确认有 Pilot Validation | 当前仓库没有客户环境/生产证据 | `OPEN / 范围不同`：Pilot 不等于 Production | 查 Demo、测试反馈和试点记录 |
| C-003 | 用户记得 Docker/Compose 可能使用 | 当前 Compose 有多个基础设施 | `OPEN`：当前表面不能证明历史启动清单 | 用本地启动场景回忆 |

状态可以是 `OPEN`、`RESOLVED_BY_SCOPE`、`RESOLVED_BY_ARTIFACT` 或 `CONTRADICTED`。在裁判前不删除任一证据。
