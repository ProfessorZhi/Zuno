# Future Skill Design

这里保存未来 Skill 的设计规格，不是当前可执行的 `SKILL.md`。当前不安装、不生成正式 Skill。至少完成数次真实红蓝会话、观察提问质量和修复闭环后，才决定是否固化为 Skill。

候选规格：

- [mock-interviewer-skill-spec.md](mock-interviewer-skill-spec.md)：只问问题的模拟面试官；
- [red-blue-architect-skill-spec.md](red-blue-architect-skill-spec.md)：Red → Blue → Repair → Retest 架构优化器。

候选模式：

- `BOOTSTRAP_PROJECT`：采集 P0 事实并建立 Claim Inventory；
- `RED_TEAM_ARCHITECTURE`：攻击架构、模块边界和技术取舍；
- `RED_TEAM_RESUME`：攻击简历陈述和个人贡献；
- `OPEN_SOURCE_REVIEW`：评估 Adopt / Extend / Build / Defer；
- `TEAM_OWNERSHIP_REVIEW`：攻击团队、协作和责任边界；
- `LANDING_PRODUCTION_REVIEW`：攻击上线、指标、成本、安全和运维；
- `FULL_PROJECT_SIMULATION`：组合角色完成一次项目模拟面试；
- `RETEST`：针对已关闭 Gap 重新攻击。

Skill 未来仍必须遵守：只读红队、事实标签、用户确认、正式文档唯一事实源和 Current / Target / Unknown 分离。
