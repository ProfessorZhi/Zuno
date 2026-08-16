# Zuno Project 文档入口

`docs/project/` 只保留一个人类主文档和一个入口。

- [`project.md`](./project.md)：项目是什么、为什么立项、为什么不只使用通用平台、项目如何发展、团队与个人参与、当前能够确认到什么程度，以及高级技术评审常见追问应该进入哪一层。

建议第一次阅读直接打开 `project.md`。它按连续叙事组织，不要求读者在背景、产品定位、开发过程、个人贡献和 Reviewer 问题表之间来回跳转。

项目事实的严格来源、允许表述和 Unknown 仍由 [`docs/governance/project-fact-provenance.md`](../governance/project-fact-provenance.md) 维护；它是事实账本，不属于人类主叙事。

继续深入时按下面的顺序阅读：

```text
project.md
→ ../architecture/architecture.md Part A
→ ../modules/README.md
→ 对应模块 Part A
→ 需要工程细节时再读 Part B / Part C、ADR、Evidence
```

文档职责保持不变：

- Project：为什么有项目、为什么值得做、项目经历与参与事实；
- Architecture：为什么系统这样设计；
- Modules：九个责任域怎样工作、失败和恢复；
- Evidence：今天的代码、测试和运行到底证明了什么。

不要用 Target Architecture 反写历史，也不要用 Pilot、Mock Test 或“架构设计完整”推导 Production Ready。
