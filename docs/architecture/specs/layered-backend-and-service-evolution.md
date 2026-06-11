# Layered Backend And Service Evolution

## 目标

这份文档定义 Zuno 当前应该采用什么样的分层后端结构，以及这套结构如何为未来演进留空间。

它关注的不是：

- 立刻拆微服务
- 追求形式化分层

而是下面这个更重要的问题：

```text
在当前仍然以单仓、本地优先为主的前提下，
Zuno 如何把前后端和后端内部边界整理清楚，
让后面继续扩展、多 Agent、云原生、异语言后端接入时不至于推倒重来。
```

## 总体方向

Zuno 当前应该保持：

- 单仓开发
- 前后端清晰分离
- 后端内部明确分层
- 基础设施适配逻辑与业务语义分开

也就是说，现在最正确的方向不是“先拆服务”，而是：

```text
Monorepo now, service-ready later
```

这句话在当前项目上还有一个更具体的含义：

```text
先治理结构，再决定是否做全仓重命名式迁移
```

当前不应该把“项目结构规范化”和“全量改成 apps/packages 外观”混为一谈。

## 推荐分层

后端至少要有四层视角：

1. 控制层
2. 服务层
3. DAO 层
4. 基础设施层

这四层的意义不是教条，而是为了让代码：

- 看得懂
- 改得动
- 后续能拆

## 当前项目结构判断

当前仓库的核心结构是：

```text
Zuno/
  src/
    backend/
    frontend/
  apps/
    desktop/
  docs/
  infra/
  tools/
  tests/
```

这说明当前项目处在传统 `src` 风格和现代 monorepo 风格之间的混合态。

这个状态不是错，但必须明确：

1. 当前主应用入口还没有完全统一语义
2. 桌面端已经按应用视角放在 `apps/`
3. Web 前端和 Python 后端仍按传统源码视角放在 `src/`
4. 当前真正要统一的不是名字，而是职责

因此面试前更合理的目标是：

```text
保留当前可运行结构，
把目录职责、主线边界、演进路线整理清楚。
```

## 面试前的目录结构目标

面试前，项目结构至少要达到下面这个解释粒度：

```text
Zuno/
  src/
    backend/
      zuno/
        api/
        core/
        database/
        services/
      agentchat/
      evals/
    frontend/
  apps/
    desktop/
  docs/
    architecture/
    development/
  infra/
  tools/
  tests/
```

这里的重点不是每一层命名完美，而是每个目录的职责能讲清楚。

### 当前阶段的推荐语义

- `src/backend/`
  后端主源码与运行时主线
- `src/frontend/`
  Web 前端源码
- `apps/desktop/`
  桌面应用壳与桌面端入口
- `docs/`
  架构、开发、公开展示文档
- `infra/`
  Docker、部署与环境编排
- `tools/`
  脚本、迁移、辅助工具
- `tests/`
  跨包、跨层、发布边界与 contract 测试

### 后端内部的推荐语义

- `api/`
  控制层入口
- `core/`
  运行时状态、Graph、核心 contract
- `database/`
  模型、DAO、持久化访问
- `services/`
  业务编排、检索、GraphRAG、Domain Pack、基础设施适配

### 面试前不建议做的结构动作

- 不为了统一外观马上把 `src/backend` 改名成 `apps/api`
- 不在 `Phase 7` 未完成时做大规模路径迁移
- 不为了“像标准 monorepo”而制造更多桥接层

## 面试后的理想演进形态

如果后续继续推进到更完整 monorepo 结构，更合理的方向是：

```text
Zuno/
  apps/
    api/
    web/
    desktop/
  packages/
    agent-runtime/
    retrieval/
    graphrag/
    domain-pack-contract-review/
    shared/
  docs/
  infra/
  tools/
  tests/
```

但这属于面试后继续优化的方向，不是当前必须马上落地的动作。

## 各层职责

### 前端

前端负责：

- 用户交互
- 页面状态
- API 调用
- 展示运行状态、检索状态、评测状态

前端不应该负责：

- 持久化业务逻辑
- 检索策略决策
- 把 GraphRAG / fallback / citation 规则写死在 UI

### 控制层

典型位置：

- `src/backend/zuno/api/v1/*`

职责：

- 处理 HTTP 请求和响应
- 参数校验
- 鉴权
- DTO 到 service 调用的映射

原则：

- 控制层保持薄
- 不直接写复杂业务逻辑
- 不直接承担基础设施编排责任

### 服务层

典型位置：

- `src/backend/zuno/api/services/*`
- `src/backend/zuno/services/*`
- `src/backend/zuno/core/*`

职责：

- 业务编排
- retrieval orchestration
- domain-pack runtime
- LangGraph runtime 组合
- 多 Agent 协调

原则：

- 服务层拥有业务语义
- 服务层可以调多个 DAO 和基础设施适配器
- 服务层是未来服务拆分的首选边界

### DAO 层

典型位置：

- `src/backend/zuno/database/dao/*`

职责：

- 数据持久化访问
- 事务相关查询
- 数据库存储模型映射

原则：

- DAO 不做 workflow 编排
- DAO 不直接承担 HTTP、队列、对象存储等外围流程
- DAO 接口要尽量稳定，方便后续抽服务

### 基础设施层

典型位置：

- `src/backend/zuno/services/redis.py`
- `src/backend/zuno/services/queue/*`
- `src/backend/zuno/services/storage/*`
- `src/backend/zuno/services/rag/vector_db/*`
- `src/backend/zuno/services/graphrag/*`

职责：

- Redis
- 队列与消息
- 对象存储
- 向量库
- 图数据库
- trace / observability 适配

原则：

- provider 相关逻辑留在这一层
- 基础设施层不拥有业务决策
- 上层可以替换 provider，而不重写业务主线

## 当前为什么必须这样分层

这套分层当前最直接的价值有四个：

1. 避免控制层变成“大杂烩”
2. 避免 DAO 层掺进 workflow 和 runtime 逻辑
3. 避免基础设施 provider 把业务语义反向绑死
4. 为后续微服务 / 云原生 / 异语言接入保留清晰边界

## 面向未来的演进空间

### 微服务 / 云原生

当前不应该过早拆微服务，但现在的代码边界要为以后保留空间。

未来更可能拆出的服务域包括：

1. agent runtime 与 workspace
2. knowledge ingestion 与 retrieval
3. evaluation 与 review pipeline

所以今天的模块边界应该尽量减少跨层缠绕。

### 异语言后端接入

未来如果要接入 Java 等其他语言的业务后端，当前应坚持：

- contract 明确
- service 边界清晰
- retrieval 与 domain-pack 语义可 API 化
- 不假设所有能力永远只能通过 Python import 直接互调

### 多 Agent 演进

多 Agent 的进一步发展也依赖这套分层：

- runtime 逻辑留在 core / service 层
- 权限、知识范围、工具范围作为 service 语义管理
- 基础设施层只提供队列、存储、trace 等能力

## 当前不该做错的事

当前应避免：

- 控制层堆积编排逻辑
- DAO 层变成 workflow 管理器
- 基础设施层反向拥有业务决策
- 为了“显得先进”过早拆微服务
- 为了未来 Java 接入而把今天的 Python 内部结构搞复杂

## 近阶段目标

面试前，这份分层文档至少要落到这些结果上：

- 前后端边界讲得清楚
- 后端四层职责讲得清楚
- 项目目录与架构文档一致
- 项目结构可以明确解释“当前为什么这样放、下一步怎么收口、后面怎么演进”
- 未来扩展方向讲清楚，但不把当前实现过度复杂化

## 一句话总结

Zuno 当前的正确工程方向不是：

```text
先把系统拆大
```

而是：

```text
先把边界理顺、分层讲清、主线做实，
再为未来拆服务、多 Agent、异语言后端接入保留稳定接口。
```
