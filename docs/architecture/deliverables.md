# Zuno 交付物清单

## 用途

这份清单定义 Zuno 最终成品的验收边界。它是面向人的正式文档，保持少而精；高频变化的执行计划、图清单细节和工作流规则仍放在 `.agent/references/`。

## 八大交付物

| 编号 | 交付物 | 期望状态 | 验收方式 |
| --- | --- | --- | --- |
| 1 | Agent 工作流文档系统 | Agent 进入仓库后能从 `AGENTS.md` 和 `.agent/references/` 明确读取任务路由、边界、验证和收尾规则。 | `AGENTS.md`、`.agent/references/*`、Agent verifier 和 repo tests 一致。 |
| 2 | 元工作流自我维护系统 | 用户提出长期规则后，Agent 能判断是否更新 workflow requirements、change log、templates、programs 和 verifier。 | `.agent/references/workflow-*` 有规则和变更记录；相关 verifier 通过。 |
| 3 | 模板与执行计划系统 | `.agent/templates/` 提供稳定输出骨架；`.agent/programs/` 只保留当前或明确等待状态。 | templates、current program、roadmap 和 closure checklist 不冲突。 |
| 4 | 正式架构文档系统 | `docs/architecture/` 少而精，能清楚区分 Current、Target、Future、History。 | `docs/architecture/README.md`、current、target、roadmap、`docs/architecture/architecture.md` 同步。 |
| 5 | 架构 HTML 展示系统 | `architecture.html` 用正式行文和十类架构视图展示 Zuno，不成为第二套事实源。 | 由 `tools/agent/render_architecture.py` 生成并通过 `--check`。 |
| 6 | 完善的 Zuno 目标架构 | 目标架构讲清 Single Controller Agent、Agentic RAG、GraphRAG、Memory、Tool、Hooks、Evidence、Trace、Eval。 | `target-architecture.md`、`docs/architecture/architecture.md` 和 absorbed reference programs / roadmap reference inputs 一致。 |
| 7 | 清晰干净的代码和目录 | 目录能表达职责，根目录保持干净，无临时截图、缓存、导出物和过时方案混在当前主线。 | repo hygiene verifier、git status、root artifact guard 通过。 |
| 8 | 一致性与验证系统 | 代码、测试、Trace/Eval、README、docs、HTML、`.agent/references` 互相不打架。 | docs verifier、repo structure verifier、Agent verifier、相关 pytest 通过。 |

## 十类架构视图

十类图不是十张装饰图，而是十个不同架构关注面。每类图都必须回答一个具体问题，并在 `docs/architecture/architecture.md` 中维护 Mermaid 源。

| 编号 | 视图 | 对应理论 | 期望表达 |
| --- | --- | --- | --- |
| 1 | Logical View | 4+1 Logical | 展示 Zuno 的核心职责分层：Frontend、API、Agent、Memory、Tool、Knowledge、Evidence、Platform。 |
| 2 | Development View | 4+1 Development | 展示 apps、src/backend/zuno、docs、.agent、tools、tests 的开发组织方式。 |
| 3 | Process View | 4+1 Process | 展示请求、服务、Agent runtime、工具/检索/LLM 调用、事件流和 trace 的运行关系。 |
| 4 | Physical View | 4+1 Physical | 展示本地优先部署、FastAPI、Web/Desktop、数据库、向量/图存储、LLM/MCP 外部依赖。 |
| 5 | Scenarios View | 4+1 Scenarios | 展示一个 query 如何经过 Context Builder、Mode Policy、Agentic RAG、Evidence Check、Citation、Trace。 |
| 6 | V&B Logical View | View & Beyond Logical | 展示 Runtime、Memory、Tool、Retrieval、Evidence 等领域子系统。 |
| 7 | Component-and-Connector View | View & Beyond C&C | 展示 API、Controller Agent、Memory Manager、Tool Registry、Retrieval Router、Evidence、Trace 的运行连接。 |
| 8 | V&B Deployment View | View & Beyond Deployment | 展示 Local Storage、SQL、Vector Store、Graph Store、Model Gateway、Search、MCP 的可替换部署边界。 |
| 9 | Quality View | View & Beyond Quality | 展示性能、可靠性、安全性、可观测性、可修改性、评测和治理闸门如何落地。 |
| 10 | Agent Loop View | Zuno 专题图 | 展示 Single Controller Agent 的 Plan、Act、Observe、Reflect、Replan 循环；它是 Process / C&C 的子系统放大图。 |

## 根目录清洁期望

项目根目录只保留项目入口和稳定配置，例如 `README.md`、`AGENTS.md`、workspace 配置、构建配置和许可证等。临时截图、浏览器截图、PDF 预览、测试产物、缓存和本地报告不得放在根目录。

正式资产应放入明确归属位置：

- 架构正式附件：`docs/architecture/assets/`
- 临时调试产物：`.local/` 或 `tmp/`
- Eval 报告：`reports/` 下的受控路径
- 历史材料：`docs/history/`

根目录出现不明图片、HTML 截图、临时 JSON、导出 PDF 或缓存目录时，应先判断是否是用户资料；确认是本轮生成物后清理，并把规则同步到 workflow / verifier。

## 最小验证

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_repo_hygiene.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
```
