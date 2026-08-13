# 历史面试验证材料

本目录保存旧一轮面试题、覆盖矩阵和追问链。它们是派生验证材料，不拥有新的事实、架构、Current 或 Production 结论；当前入口统一回到 `docs/facts/`、`docs/architecture/`、`docs/decisions/`、`docs/governance/` 和 `docs/evidence/`。

## 内容

- `project facts`：项目背景、个人贡献、当前实现和生产边界，来源是 [`../../facts/`](../../facts/README.md)；
- `architecture QA`：为什么这样设计、状态如何变化、失败如何恢复，来源是 [`../../architecture/`](../../architecture/README.md)；
- `deep-dive / coverage / gap`：验证材料和追问记录，不能反向修改正式事实。

## 使用边界

```text
facts / architecture / evidence
              ↓
        historical QA material
```

面试答案与正式文档冲突时，以 `docs/facts/`、`docs/architecture/`、`docs/decisions/`、`docs/governance/` 和 `docs/evidence/` 为准。`FULL` 只表示文档覆盖，不表示代码已实现、质量已证明或已经生产就绪。

## 维护

新问题不在本目录建立新的 Canonical 事实；应先更新对应的 Facts、Architecture、Decision 或 Evidence，再把需要练习的派生材料归档到这里。
