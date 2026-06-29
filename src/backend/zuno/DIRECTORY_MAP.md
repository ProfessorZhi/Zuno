# Zuno Backend Directory Map

> 状态：Program 3 PHASE10 active input。本文描述当前 `src/backend/zuno` 一等目录的处理策略，不把 Target 写成 Current。

## 目标

`src/backend/zuno` 的目标表达是六个主层：

```text
api / agent / memory / capability / knowledge / platform
```

Program 3 的下一步不是把所有旧目录一次性搬空，而是让新代码进入六层目录、让旧目录逐步变薄，并用 verifier 防止新的旧式顶层目录继续扩散。

## 当前目录地图

| 目录 | 状态 | 目标归属 | 当前策略 |
| --- | --- | --- | --- |
| `api/` | keep | API 层 | 当前对外入口和 API facade。新 API、DTO、依赖注入优先进入这里。 |
| `agent/` | keep | Agent 层 | 目标 Agent runtime 入口。先补 facade 和 contracts，再迁移高风险 agent loop。 |
| `memory/` | keep | Memory 层 | 目标 memory 入口。优先吸收 `services/memory/` 中小而清楚的 contract/store/retrieval 模块。 |
| `capability/` | keep | Capability 层 | 目标工具、Skill、MCP、权限和执行入口。MCP server implementations 已迁入 `capability/mcp/servers/`。 |
| `knowledge/` | keep | Knowledge 层 | 目标 RAG / GraphRAG / Evidence / Citation 入口。先补 retrieval/fusion facade，再迁移小模块。 |
| `platform/` | keep | Platform 层 | 目标配置、数据库、模型网关、安全、观测、存储入口。HTTP middleware implementations 已迁入 `platform/middleware/`。 |
| `resources/` | facade | Platform / packaged resources | 当前收纳 prompts、fixtures、system skills。保持受控，后续评估是否并入 `platform/resources/`。 |
| `compatibility/` | facade | Platform compatibility | 当前承接 legacy/vendor 兼容。只允许兼容材料，不允许新业务逻辑。 |
| `config/` | migrate | Platform config | 当前仍是基础设施来源。后续迁入 `platform/config/` 或 `platform/config.py`。 |
| `database/` | migrate | Platform database | 当前仍是持久化实现来源。后续迁入 `platform/database/`，先保护 public import。 |
| `core/` | migrate | Agent / Platform model gateway | 当前仍承载旧 runtime 主线。先通过 `agent/` facade 变薄，再拆高风险文件。 |
| `services/` | migrate | Memory / Capability / Knowledge / Platform | 最大迁移源。禁止继续新增泛 `services/*` 主线，新代码按六层进入目标目录。 |
| `schema/` | migrate | API DTO / domain contracts | 当前 schema 过泛。后续按使用方迁入 `api/dto/`、`agent/contracts.py`、`knowledge/contracts.py`。 |
| `tools/` | migrate | Capability tools / root tools | Runtime 可调用工具迁入 `capability/tools/`；维护脚本迁出到仓库根 `tools/`。 |
| `utils/` | migrate | Layer-local helpers / Platform common | 禁止继续当垃圾桶。后续按调用方内聚，少量公共 helper 进入 `platform/common.py`。 |

## 已退休顶层兼容壳

这些不再是目录，只保留 alias module：

| 旧目录 | 当前入口 | 实现归属 |
| --- | --- | --- |
| `mcp_servers/` | `mcp_servers.py` | `capability/mcp/servers/` |
| `middleware/` | `middleware.py` | `platform/middleware/` |
| `evals/` | `evals.py` | `tools/evals/zuno/` |

## 新增目录规则

新增 `src/backend/zuno` 一等目录必须满足至少一个条件：

1. 属于六层目标目录：`api / agent / memory / capability / knowledge / platform`。
2. 是已登记的迁移源、兼容 facade 或 app resource，并在本文和 verifier 中同步。
3. 是短期 alias module，不以目录形式占用顶层。

否则应放入现有层内部，或放到仓库根 `tools/`、`examples/`、`docs/` 等更合适的位置。

## 下一步迁移顺序

1. 补齐六层 facade，让新目录成为正式入口。
2. 迁移低风险小模块，例如 memory contracts、capability contracts、retrieval BM25 等。
3. 最后处理 `core/agents/general_agent.py`、retrieval orchestrator、fusion 等高风险大文件。
