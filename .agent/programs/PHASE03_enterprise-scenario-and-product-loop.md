# PHASE03 Enterprise Scenario And Product Loop

status: pending

## 目标

把 Zuno 的主场景从“普通 RAG 问答”固定为“企业私有知识库与多功能 Agent 助手”，并定义 workspace、task/session、upload、artifact、event stream 和 trace panel 的产品闭环。

## 步骤

- [ ] 定义 Workspace、Knowledge Space、Session、Task、Uploaded File、Artifact、Trace Event、Citation 和 Feedback 的 contract。
- [ ] 定义 upload -> parse/index -> ask -> event stream -> answer/report -> artifact download -> feedback/eval 的链路。
- [ ] 明确企业知识库、HR 简历库、合同/审查报告三个首批场景。
- [ ] 更新 API / frontend contract tests。
- [ ] 更新架构文档中的 Scenarios View。

## 验收

- 主场景可以用一张图和一条事件链讲清楚。
- API 和 frontend 不再只是聊天入口，而能表达知识库、任务、产物和 trace。
- 未实现的 UI 和 backend 行为不写成 Current。

## 验证

```powershell
pytest -q tests/api tests/frontend -p no:cacheprovider
python tools/agent/render_architecture.py --check
```
