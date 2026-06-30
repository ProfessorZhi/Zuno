# 企业私有知识库与多功能 Agent 助手

## 定位

Zuno 的主场景不是普通 RAG 问答，而是**本地优先的企业私有知识库与多功能 Agent 助手**。

一句话定义：

```text
Zuno 是一个本地优先的企业内部知识库与多功能 Agent 助手，用于让企业私有文档从“可搜索”升级为“可理解、可追溯、可执行”。
```

这个主叙事比“泛 Agent 平台”更稳。它把 Zuno 已经形成的本地优先、RAG / GraphRAG、Evidence / Citation / Trace / Eval、Memory、Tool Governance 和安全治理放进一个清晰业务场景，而不是停留在框架名词堆叠。

## 核心数据

企业私有知识资料包括：

- 公司制度、流程、SOP 和培训材料。
- 合同、报价、客户资料和合规材料。
- 项目文档、技术方案、PRD、会议纪要和复盘。
- 技术文档、代码说明、API 文档和故障记录。
- HR 文档、简历、候选人资料、JD、面试记录和评价表。
- 个人项目证据、简历知识库和面试准备材料，作为企业私有知识库的轻量验证样例。

简历和候选人资料在企业招聘场景中属于 HR 敏感资料；在个人展示场景中属于个人职业资料知识库。它们可以复用同一套解析、检索、Evidence、Citation、Trace 和 Eval 架构，但对外表达时必须区分“企业内部数据”和“个人验证样例”。

## 三层场景

### 第一层：企业内部文档知识库

这一层负责把私有资料变成可追溯知识空间：

```text
upload / sync
  -> Document Ingestion / Parse Gateway
  -> Canonical Document IR
  -> chunk / provenance / ACL
  -> BM25 / vector / graph index
  -> Basic RAG / GraphRAG local-global-drift
  -> evidence / citation / trace
```

它验证的是：文档能否被可靠解析、切分、索引、检索和引用。

### 第二层：多功能文档助手

这一层不只回答问题，而是围绕文档完成业务任务：

- 合同条款审查和风险提取。
- 制度问答和政策差异比对。
- 项目文档总结、技术方案解释和决策依据整理。
- 候选人简历分析、岗位匹配和面试提纲生成。
- 会议纪要整理、报告生成和证据包输出。

典型流程：

```text
用户目标
  -> Context Builder
  -> Single Controller Agent
  -> basic / local / global / drift 检索
  -> Evidence / Citation Check
  -> answer / report / artifact
  -> Trace / Eval / Memory Candidate
```

### 第三层：受控工具型 Agent

这一层让 Agent 在安全边界内调用工具，而不是无约束自动执行：

- 生成邮件草稿。
- 生成 Markdown / PDF 报告。
- 读取项目文件或企业知识库。
- 调用内部 API / SDK / MCP。
- 查询数据库或创建任务单。
- 运行受控 CLI、代码片段或 SSH wrapper。

高副作用工具必须走：

```text
tool proposal
  -> ToolCard / Manifest
  -> Policy Check
  -> Approval Gate
  -> Sandbox Executor
  -> Result Normalizer
  -> Audit / Trace
```

## Current / Target / Future

### Current

当前 Zuno 已经具备企业私有知识 Agent Workspace 的架构底座：

- Single `GeneralAgent` 主线。
- Knowledge / GraphRAG 查询边界。
- `normal / enhanced / auto` 产品模式和 `basic / local / global / drift` 内部 query method contract。
- Evidence / Citation / Trace / Eval foundation。
- Context / Memory、Capability / Tool、Hooks / Evidence / Trace、GraphRAG Knowledge Runtime 和 RuntimeTurnLedger 的 foundation slices。
- 架构文档、HTML 展示、program 生命周期、verifier 和 repo tests 的治理闭环。

这些是 foundation，不等于完整企业产品闭环。

### Target

下一阶段目标是把主叙事落成四条实现 program：

1. `zuno-document-ingestion-v1`：多格式解析、Canonical Document IR、chunk/provenance、ACL、BM25/vector/graph indexing。
2. `zuno-runtime-memory-tool-plane-v1`：Context Pack、summary compression、structured extraction、ToolCard manifest、executor registry、approval flow。
3. `zuno-eval-observability-v1`：LangSmith trace mapping、dataset versioning、RAGAS / DeepEval 指标、citation coverage 和 CI regression gate。
4. `zuno-security-enterprise-scenarios-v1`：PII / 商业秘密脱敏、prompt injection 防护、ACL、输出 DLP、高风险工具人工审批，以及企业知识库 / HR 简历库场景。

### Future

长期方向包括企业级多租户隔离、远程安全执行、微虚拟机沙箱、组织级策略中心、前端 trace 面板、artifact 下载闭环和更完整的 enterprise workflow。

这些不能写成 Current。

## 非目标

Zuno 暂时不主打：

- 通用 ChatGPT 替代品。
- 只做向量检索的普通 RAG demo。
- 开放互联网搜索 Agent。
- 无审批自动发邮件、删文件或远程部署的全自动办公机器人。
- 生产级多租户 SaaS。
- 完整 Coding Agent。

## 简历表达

当前真实表达：

```text
构建本地优先企业私有知识库 Agent Workspace，面向企业内部文档、合同、项目资料、技术文档和简历/HR 资料场景，设计 Basic RAG + GraphRAG Local/Global/DRIFT 的增强检索架构，并通过 Evidence、Citation、Trace、Eval、Memory 和 Tool Governance 提升回答可追溯性与工具调用可控性。
```

后续实现文档解析、安全沙箱和评测闭环后，才能升级为：

```text
实现企业私有文档 Agent 平台的数据处理与评测闭环，支持多格式文档解析、BM25/向量/GraphRAG 多路召回、Evidence/Citation/Trace 全链路追踪，并构建 Recall@K、Citation Coverage、Faithfulness 等自动化评测指标用于检索和回答质量回归。
```
