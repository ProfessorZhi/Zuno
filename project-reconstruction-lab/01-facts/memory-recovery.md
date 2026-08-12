# Memory Recovery Framework

## 目标

通过具体场景帮助用户恢复发生过的操作，而不是让用户从技术名词中猜答案。

## 场景模板

```text
场景：上传一个 PDF / 第一次 Demo / 第一次调数据库
可观察动作：页面、命令、容器、管理后台、错误提示
A：候选场景 1
B：候选场景 2
C：候选场景 3
用户回答：明确记得 / 更接近 / 不记得
升级状态：USER_CONFIRMED / USER_PARTIAL_RECALL / UNKNOWN
新增 Evidence ID：
```

## 恢复规则

1. 先问发生了什么，再问组件名。
2. 先问可见 UI、命令、日志和数据，再问架构术语。
3. 用户确认“见过”只证明接触过，不证明负责实现。
4. 用户说“像是”进入 `USER_PARTIAL_RECALL`，不能变成 `USER_CONFIRMED`。
5. 模型根据仓库推断的内容进入 `RECONSTRUCTED_CANDIDATE`。
6. 每轮恢复必须更新 Evidence Ledger 和 Open Questions。

## 典型提示

```text
上传 PDF 后页面是一直等待，还是立即显示“处理中”？
是否见过 Queue / Ready / Unacked 的管理页面？
是否在 MinIO 看到 bucket/object？
是否在图数据库 Browser 里看到节点和边，或写过 MATCH (...) RETURN ...？
数据库里看到的是 Agent、Session、Run、Memory 还是 Document？
```

## 禁止

- 不给用户列出一个“最可能的技术栈”让其顺着确认。
- 不用当前 Compose 反向暗示历史组件。
- 不为了补齐故事把模糊记忆写成完整调用链。
