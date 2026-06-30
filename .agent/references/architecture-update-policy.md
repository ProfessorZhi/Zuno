# Architecture Update Policy

## When To Use

当改动可能影响 Agent Runtime、RAG、GraphRAG、Memory、Tool、Hooks、Trace、Eval、部署、前后端契约或架构展示时，使用本策略判断同步范围。

## Mental Model

```text
change area
  -> affected human docs
  -> affected generated HTML and diagrams
  -> affected agent operating memory
  -> affected templates / programs / verifiers
```

## Current Truth

任何触碰以下区域的变更都必须触发架构文档检查。

| Change Area | Affected docs | Examples |
| --- | --- | --- |
| Agent Runtime | `docs/architecture/current-architecture.md`, `docs/architecture/target-architecture.md`, `docs/architecture/roadmap.md`, `docs/architecture.md`, `docs/architecture.html`, `README.md`, `.agent/references/current-program.md`, `.agent/references/code-map.md`, `.agent/references/runtime-call-chain.md`, `.agent/references/diagram-inventory.md` | Planner、ReAct loop、Reflection、Replan、Task DAG、Todo、Checkpoint、RuntimeTurnLedger、post-turn evidence |
| RAG / GraphRAG | `docs/architecture/target-architecture.md`, `docs/architecture.md`, `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md` | product mode、query_method、basic / local / global / drift、Evidence Check、Conditional Requery |
| Memory System | `docs/architecture/target-architecture.md`, `docs/architecture.md`, `.agent/architecture/near-term/02-context-memory-architecture.md` | Short-term、Working、Conversation、Project、Long-term、Graph Memory、Context Builder |
| Tool Layer / Hooks / MCP | `docs/architecture/target-architecture.md`, `docs/architecture.md`, `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md` | Tool Registry、Tool Contract、MCP Adapter、before_tool、after_tool、Permission、Budget |
| Evidence / Citation / Trace / Eval | `docs/architecture/current-architecture.md`, `docs/architecture/target-architecture.md`, `docs/architecture/roadmap.md` | Evidence Bundle、Citation Builder、Trace Event、Eval baseline、contract review |
| Frontend / Backend Contract | `docs/architecture/current-architecture.md`, `docs/architecture/target-architecture.md`, `README.md` | API schema、event schema、SSE / WebSocket、request / response DTO |
| Deployment / Infrastructure | `docs/architecture/target-architecture.md`, `docs/architecture/roadmap.md`, `docs/architecture.md` | database、vector store、graph store、worker、Redis、RabbitMQ、deployment topology |
| Quality Attributes | `docs/architecture/target-architecture.md`, `docs/architecture.md`, `docs/architecture.html` | performance、reliability、security、observability、modifiability、evaluation |

## Target Direction

架构变更最终应能回答三件事：

1. 人类在 `docs/architecture` 能看懂。
2. 展示页能讲清楚。
3. Agent 下次能从 `.agent/references` 自动维护同一规则。

## Must Preserve

- `global` 不应被写成和 BM25 chunk ranking 直接混榜；它是 community-level prior / report synthesis，再用 local/basic 回补 supporting evidence。
- `auto` 是 router，不是第五种固定检索实现。
- 多 agent 可以是 Codex 执行模式，不是 Zuno runtime Current。
- GraphRAG 是 BM25 + Dense Vector 的补充，不是替代。

## Before Editing

1. 确认变更区域。
2. 查上表列出受影响 docs。
3. 查 `diagram-inventory.md` 决定是否更新十类架构视图。
4. 需要 HTML 更新时只改 `docs/architecture.md` 或 `tools/agent/render_architecture.py`，再生成。

## Allowed Changes

- 更新受影响架构说明、图源、展示页生成器、verifier 和 tests。
- 为未来 program 更新 queued draft 状态。

## Forbidden Changes

- 不要把远期微服务、事件驱动 worker、产品级多 Agent 写成近期 Current。
- 不要把 fallback、retry 或 try/except 直接包装成已完成 circuit breaker。

## Common Failure Patterns

- 改 query mode 文档但忘记 `Scenarios View` 或 `Component-and-Connector View`。
- 改 Agent loop 文档但忘记 `Agent Loop View`。
- 改 quality 叙事但没有更新 `Quality View`。

## Debug Playbooks

- 不知道是否影响架构：如果会改变用户如何理解模块、流程、依赖、质量属性或部署，就影响。
- 不知道写 Current 还是 Target：没有代码和测试证据就不要写 Current。

## Focused Tests

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Docs Sync

修改本文件时检查：

- `.agent/references/diagram-inventory.md`
- `docs/architecture/README.md`
- `tools/scripts/verify_docs_entrypoints.py`

## Lessons Learned

架构同步不是“补一句说明”，而是让源文档、展示页、Agent 规则和验证脚本同时收口。
