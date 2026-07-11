# Input Layer and Document Processing

所属运行域：Product & API、Input & Knowledge。

## 定位

Input layer 管理用户输入、文件输入和状态反馈。它把 UI 的上传、选择知识库和提问动作转成后端可恢复的 SourceObject、ParseJob、IndexManifest、AgentChat Request 和 TaskEvent。

## Contract

```text
UI Input
-> FastAPI DTO
-> Workspace / Knowledge scope
-> SourceObject or AgentChat Request
-> TaskEvent / SSE
-> durable status
```

前端只展示状态，不是状态事实源。file lifecycle、task lifecycle、parse/index status、approval status 和 trace summary 必须能从后端恢复。

## Document Processing Boundary

- 文本类文档是当前真实闭环基线。
- PDF text parser 是当前最小真实扩展：本地 PyMuPDF 可输出 page / bbox / char offset SourceSpan；不要求同时支持所有 parser。
- parser blocked 时必须显示 blocked reason，不得 fake indexed。
- chunk、source span、citation lineage 必须在 index 和 retrieval trace 中保留。

## 当前与短期目标

Current：

- upload / knowledge DTO、local storage、parser/indexing surface 和 SSE/API surfaces 已存在。
- text PDF source span citation 已通过本地 vertical tests；扫描 PDF/OCR 不 fake 解析。

Short-term：

- P1 task/parse/index status durable。
- P2 前端 E2E 覆盖 upload -> ask -> citation -> trace。

Future Optional：

- OCR/VLM 和扫描 PDF 解析。
- 大量 enterprise parser。
- 分布式 file processing worker。
