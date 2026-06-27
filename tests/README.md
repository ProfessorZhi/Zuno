# 测试目录说明

`tests/` 不再平铺所有测试文件。根目录只保留 `conftest.py` 和本说明，具体测试按领域放入子目录。

## 分类

- `repo/`：仓库结构、文档入口、Agent 工作流、发布边界和 repo hygiene。
- `agent/`：GeneralAgent、Context、Memory、Capability、MCP、Workspace 会话和运行时行为。
- `api/`：后端 API、DTO、用例边界和知识配置接口。
- `frontend/`：Web 前端页面、产品 wiring 和 UI review 导出。
- `graphrag/`：GraphRAG Project、图检索、实体别名、图路径、contract graph 和结构化图抽取。
- `retrieval/`：retrieval planner/orchestrator、query rewrite、rerank、enhanced retrieval 和 fusion。
- `evals/`：RAG eval、multihop eval、stackless eval、Contract Review eval、local model eval 工具。
- `storage/`：数据库、队列、pipeline、文件解析、embedding provider、存储工具。
- `tools/`：CLI tool、OpenAPI tool、系统工具、启动器和工具运行时。
- `legacy_guards/`：旧 phase、旧 runtime、Domain Pack、compat namespace 和退役边界防回归测试。

## 规则

- 新测试按行为归类，不再直接放到 `tests/` 根层。
- 退役守卫测试不要和当前功能测试混在一起；放到 `legacy_guards/`。
- 如果一个测试只证明历史 phase 名称，不再影响当前行为，应优先判断能否移动到 `legacy_guards/` 或归档为历史证据。
- 修改测试路径后，同步 `.agent/references/verification-map.md`、`README.md`、验证器和任何硬编码测试路径。
