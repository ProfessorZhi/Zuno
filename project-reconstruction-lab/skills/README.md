# Skill Design Specs

本目录只保存三个 Skill 的设计规范，不自动安装或生成正式 `SKILL.md`。正式 Skill 生成前必须检查当前 Codex Skill 规范、触发规则、读取机制和可复用资源。

## 组合关系

```text
project-reconstruction
    ├─ follows architecture-red-blue
    └─ invokes big-tech-interviewer-red-team
```

三个 Skill 共享 Evidence State、Fact State、Architecture State、Challenge Record 和 Decision Record；不复制各自的事实或状态机。

| Spec | 角色 |
|---|---|
| `project-reconstruction-skill-spec.md` | Orchestrator，贯穿完整项目恢复和重构 |
| `architecture-red-blue-skill-spec.md` | Specialist，攻击/防守/反击架构 |
| `big-tech-interviewer-red-team-skill-spec.md` | Specialist，模拟大厂深挖 |

V3.1.3 共享契约新增三项：Closure Class Integrity（Severity 与 A/I/E/X 正交）、Distribution Audit（防止默认归类偏差）和 Human Continuity（Canonical Part A 必须整篇重读）。Round 问题必须优先使用具体失败场景，而不是用抽象名词填充题库。
