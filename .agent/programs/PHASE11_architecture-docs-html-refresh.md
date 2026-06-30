# PHASE11 Architecture Docs HTML Refresh

status: pending

## 目标

把 PHASE02-PHASE10 已完成的事实同步到正式架构 Markdown、Agent 架构镜像、架构 HTML、README 和图集，让展示页和代码事实一致。

## 步骤

- [ ] 更新 `docs/architecture/architecture.md` 的 Current / Target / Future。
- [ ] 更新十类 Mermaid 图，展示文件夹治理、企业场景、Document Ingestion、Runtime、Memory、Tool、GraphRAG、安全、Eval。
- [ ] 更新图前正文，让 Markdown 内容比 HTML 更详细；HTML 只负责图形展示和简短分析。
- [ ] 运行 renderer 同步 `.agent/architecture/architecture.md` 和两个 HTML。
- [ ] 更新 README 当前架构和 active program 状态。
- [ ] 更新 AGENTS.md 工作流和读文档顺序。

## 十类图更新清单

| 图 | 必须展示 | Current / Target 标注规则 |
| --- | --- | --- |
| Logical View | 九平面 + Platform 支撑。 | 已验证 foundation 标 Current；未实现 production plane 标 Target。 |
| Development View | `api/agent/memory/capability/knowledge/platform` 内部 ownership。 | 物理已存在写 Current；目标代码树写 Target。 |
| Process View | task/session/event、runtime、memory、tool、retrieval、trace。 | SSE/WS 未完成前只写 Target。 |
| Physical View | local-first、storage、worker、model gateway、MCP、LangSmith sink。 | 微服务、worker、外部 provider 不写 Current。 |
| Scenarios View | 企业知识库 upload -> parse -> index -> query -> answer -> artifact。 | 场景链路未实现前写 Target。 |
| V&B Logical View | Runtime、Memory、Tool、Knowledge、Ingestion、Workspace、Policy。 | 与正文九平面一致。 |
| Component-and-Connector View | ToolCard、Policy、Sandbox、Retrieval Router、Evidence、Memory commit。 | 未落地 approval/sandbox 前写 Target。 |
| V&B Deployment View | OTel/LangSmith、storage、MCP、CLI/SSH sandbox。 | gVisor/Firecracker 只能写 candidate。 |
| Quality View | security gates、eval metrics、CI gate、release baseline。 | 指标未跑出 baseline 前写 Target。 |
| Agent Loop View | prepare_context、plan、ReAct、observe、reflect、replan、commit。 | 完整 LangGraph runtime 未完成前写 Target。 |

## 架构图补充清单

本 program 不强制突破 renderer 的十张 Mermaid 图数量限制。若需要更多合同级图，优先在十张图内部扩细；若后续要新增图，必须先更新 `tools/agent/render_architecture.py` 的 EXPECTED_DIAGRAMS、verifier 和 tests。候选图包括：

- 系统上下文与信任边界。
- Tool 执行与沙箱流。
- Memory 平面图。
- Knowledge / Ingestion / GraphRAG index 双流程图。
- Eval trace tree。

## 输入 / 输出文件

输入：

- PHASE02-PHASE10 的 closure evidence。
- `docs/architecture/architecture.md`
- `.agent/architecture/architecture.md`
- `tools/agent/render_architecture.py`
- README / AGENTS / diagram inventory。

输出：

- 更新后的正式架构 Markdown。
- `.agent/architecture/architecture.md` byte mirror。
- 两份生成 HTML。
- README / AGENTS 状态说明。

## Current / Target 写入规则

- 每个小节更新前先检查对应 phase evidence。
- 没有 tests/verifier/eval/trace 证据，只能写 Target。
- PDF / 研究报告中的能力不能直接写 Current。
- 如果 HTML 图为了展示目标画了未实现能力，图下分析必须明确“Target，不是 Current”。

## 验收

- Markdown 内容比 HTML 更充实。
- HTML 以图为主，可以展示各模块二级细节。
- docs 和 agent architecture mirrors byte-consistent。
- Mermaid 图比例、全屏查看、线条可读性必须由 HTML renderer 保持；如果视觉不合格，先修 renderer / 图结构，再声称完成。

## 验证

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```
