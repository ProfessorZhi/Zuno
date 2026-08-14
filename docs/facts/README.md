# Zuno 项目事实入口

`docs/facts/` 只回答：**哪些项目事实可以作为今天理解 Zuno 的可靠基线？**

这些文件承载已经恢复、仍与产品边界有关的历史事实；它们不是 Target Architecture，
也不替代 `docs/evidence/` 的当前实现证据。每个不确定结论都必须保留状态标签、来源边界和
`UNKNOWN`，不能用当前代码或目标设计补齐历史空白。

## 阅读顺序

1. [项目背景](project-background.md)
2. [历史需求与业务流程](requirements-and-workflows.md)
3. [开发与演进](development-and-evolution.md)
4. [团队与个人 Ownership](team-and-ownership.md)
5. [交付与客户反馈](delivery-and-feedback.md)
6. [技术现实](technology-reality.md)

## 文件职责

| 文件 | Canonical Question |
| --- | --- |
| `project-background.md` | 项目从哪里来、服务什么方向？ |
| `requirements-and-workflows.md` | 历史业务问题和人工流程恢复到什么程度？ |
| `development-and-evolution.md` | 项目如何从已有产品演进到 Demo、测试和 Pilot？ |
| `team-and-ownership.md` | 团队和用户本人分别确认做了什么？ |
| `delivery-and-feedback.md` | 实际验证、交付阶段和质量反馈是什么？ |
| `technology-reality.md` | 历史技术使用、当前仓库证据和 Target-only 内容如何区分？ |

## 相关入口

- 当前代码、测试、运行与评测证据：[`../evidence/README.md`](../evidence/README.md)
- Target Architecture：[`../architecture/architecture.md`](../architecture/architecture.md)
- ADR：[`../decisions/README.md`](../decisions/README.md)
- 过时材料和 Red/Blue 原始档案：[`../history/README.md`](../history/README.md)

## 状态边界

```text
FACTS        今天理解 Zuno 必须相信什么
EVIDENCE     当前仓库和运行结果实际证明了什么
ARCHITECTURE 当前接受的 Target 设计为什么这样工作
HISTORY      已结束、已替换或只用于考古的材料
```

写入 Facts 不会把 `TARGET`、`FUTURE`、`HYPOTHESIS` 或 `UNKNOWN` 升级为 Current。
Production Readiness 仍由证据支持，当前状态为 `NOT_ESTABLISHED`。
