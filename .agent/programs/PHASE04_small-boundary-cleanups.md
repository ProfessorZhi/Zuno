# PHASE04：小步边界清理
> 状态：in progress / 第二波线程 A 已完成六层 README 边界说明；本 phase 不做 runtime 大搬家。

## 目标

只做低风险边界清理：import facade、历史命名、生成物忽略、过时 docs 前台移除。

可执行范围只来自 PHASE01/03 的审计结果。允许做小步、低风险、可回滚的清理，例如：

- 为目标六层补充 facade / re-export。
- 移除或归档已经确认无引用的前台历史材料。
- 把本地产物和生成物加入 `.gitignore` 或移动到正确位置。
- 给低风险目录增加 README / AGENTS 边界说明。

禁止在本 phase 做跨层大搬家、runtime 行为变更、public API 变更或数据库 schema 变更。

## 本轮完成：六层 README 边界说明

第二波线程 A 只补充目标六层目录的 README，用来帮助第一次进入 `src/backend/zuno` 的读者区分 Current / Target / Future：

| path | 本轮动作 | 边界 |
| --- | --- | --- |
| `src/backend/zuno/api/README.md` | 新增 API 层当前角色、target role、允许新增内容、禁止事项和 focused tests。 | API 是 HTTP / DTO / auth / response envelope 边界，不承载 Agent、GraphRAG、memory 或 DB runtime。 |
| `src/backend/zuno/agent/README.md` | 新增 Agent 层边界说明。 | 当前是 lazy facade；`GeneralAgent` 主循环仍在旧 runtime 路径，不能直接搬动。 |
| `src/backend/zuno/memory/README.md` | 新增 Memory 层边界说明。 | 当前是 memory foundation facade；成熟 memory extraction / consolidation 仍是 Target。 |
| `src/backend/zuno/capability/README.md` | 新增 Capability 层边界说明。 | 当前是 capability metadata / selector foundation facade；产品级 ToolCard retrieval 仍是 Target。 |
| `src/backend/zuno/knowledge/README.md` | 新增 Knowledge 层边界说明。 | 当前是 Knowledge / GraphRAG / retrieval facade；GraphRAG 与 retrieval 物理迁移后置。 |
| `src/backend/zuno/platform/README.md` | 新增 Platform 层边界说明。 | 当前只暴露 execution policy facade；DB、settings、MCP、vendor compat 等底座不在本轮迁移。 |

本轮没有修改 Python runtime 代码、`__init__.py`、public API、DB schema、GraphRAG runtime、GeneralAgent runtime、`.gitignore`、verifier/test 或 `docs/architecture`。

## 验收

旧 import 不破坏，runtime 行为不变，repo hygiene tests 通过。
