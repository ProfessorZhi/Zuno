# 仓库内本地 Skill

这里的三个目录各自包含一个仓库内、仅显式调用的 `SKILL.md`。它们共享同一组边界：证据先于叙事，
`CURRENT / HISTORY / TARGET / HYPOTHESIS / UNKNOWN` 不混用，复杂度必须可以被删除或替换。

统一定位：

```text
REPOSITORY LOCAL
EXPLICIT INVOCATION
PORTABLE
NOT CANONICAL
NOT AUTO-EXECUTED
```

## 使用方式

这些 Skill 不是当前 Zuno Manual Workflow 的自动 Runtime，也不是全局安装包。只有用户或上层
Coordinator 明确指定名称或路径时，Agent 才读取对应 `SKILL.md`；完成任务后仍留在本仓库。

| Skill | 作用 |
| --- | --- |
| [`red-team-interviewer/SKILL.md`](red-team-interviewer/SKILL.md) | 只攻击项目真实性、个人贡献和架构取舍 |
| [`architecture-red-blue-loop/SKILL.md`](architecture-red-blue-loop/SKILL.md) | 执行 Red、Blue、Review、Main Gate 和验证闭环 |
| [`jd-enterprise-project/SKILL.md`](jd-enterprise-project/SKILL.md) | 从 JD 推导真实、可实现、不过度设计的项目 |

Skill 之间不复制 Facts、ADR 或架构正文。完整项目重建由调用方组合三个 Specialist；本目录不
保存项目专属事实。
