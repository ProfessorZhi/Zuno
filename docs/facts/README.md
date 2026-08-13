# Zuno 当前事实入口

`docs/facts/` 只回答：**今天理解 Zuno 必须相信什么？**

这里不是历史档案，也不是 Target 设计目录。Facts 可以包含项目曾经的起源，但前提是这段背景今天仍然是理解 Zuno 边界和用途所必需的事实。

## 文件

| 文件 | 回答的问题 |
| --- | --- |
| [`project-context.md`](project-context.md) | Zuno 是什么、为什么存在、服务什么背景？ |
| [`current-state.md`](current-state.md) | 当前代码、测试、证据和 Production Readiness 到了哪里？ |

如果事实需要完整证据，进入 [`../evidence/`](../evidence/README.md)；如果内容是“为什么这样设计”，进入 [`../architecture/`](../architecture/README.md) 或 [`../decisions/`](../decisions/README.md)；如果只是过去如何演进，进入 [`../history/`](../history/README.md)。

## 状态边界

```text
Facts       今天仍可作为 Zuno 当前基线使用的事实
Architecture 当前 Target 设计和跨层契约
Decisions   仍然有效的设计决策
History     已结束、已替换或只用于考古的过去材料
Evidence    支撑 Facts / Current 的可复现 Artifact
```

Target、Future、Hypothesis 和 UNKNOWN 不得因为写进 Facts 就变成 Current。`current-state.md` 中的 UNKNOWN、Measurement Blocked 和 Not Established 必须原样保留。
