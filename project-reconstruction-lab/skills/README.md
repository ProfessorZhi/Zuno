# 仓库内本地 Skill

这里的三个目录各自包含一个可由仓库 Agent 直接读取的 `SKILL.md`。它们共享同一组边界：证据先于叙事，
`CURRENT / HISTORY / TARGET / HYPOTHESIS / UNKNOWN` 不混用，复杂度必须可以被删除或替换。

## 使用方式

这些 Skill 不是全局安装包。任务匹配时，Agent 按 `.agent/system.yaml` 的本地注册读取对应
`SKILL.md`；也可以在提示中明确给出相对路径。完成一次任务后，Skill 文件仍留在本仓库，
不写入用户的全局 Skill 目录。

| Skill | 作用 |
| --- | --- |
| [`red-team-interviewer/SKILL.md`](red-team-interviewer/SKILL.md) | 只攻击项目真实性、个人贡献和架构取舍 |
| [`architecture-red-blue-loop/SKILL.md`](architecture-red-blue-loop/SKILL.md) | 执行 Red、Blue、Review、Main Gate 和验证闭环 |
| [`jd-enterprise-project/SKILL.md`](jd-enterprise-project/SKILL.md) | 从 JD 推导真实、可实现、不过度设计的项目 |

Skill 之间不复制 Facts、ADR 或架构正文。完整项目重建由调用方组合三个 Specialist；本目录不
保存项目专属事实。
