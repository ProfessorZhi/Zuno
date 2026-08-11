# 01 Agentic GraphRAG / Evidence Retrieval QA

> Architecture Verification Corpus；不是canonical architecture。答案只从正式架构文档重生成。

### Interview Drill Chain A：Q001–Q012

连续追问从概念进入机制、失败、取舍和证据。

## Q001 什么是 Zuno 的 Agentic GraphRAG？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+技术资料+面试+001/正文.md
- primary_domain: knowledge
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 1. 为什么需要 Agentic GraphRAG
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 2. 普通 GraphRAG 与 Agentic GraphRAG
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-001
- status: Target

### 面试官问题

什么是 Zuno 的 Agentic GraphRAG？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

它围绕 EvidenceRequirement 运行 Retrieval Control Loop，按需选择 SearchAction、评估 EvidenceLedger 并受治理停止；不是固定全开检索。

### 深挖回答

它围绕 EvidenceRequirement 运行 Retrieval Control Loop，按需选择 SearchAction、评估 EvidenceLedger 并受治理停止；不是固定全开检索。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 1. 为什么需要 Agentic GraphRAG
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 2. 普通 GraphRAG 与 Agentic GraphRAG

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q002 普通 RAG、传统 GraphRAG 和 Agentic GraphRAG 的边界是什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 1. 为什么需要 Agentic GraphRAG
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 2. 普通 GraphRAG 与 Agentic GraphRAG
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-002
- status: Target

### 面试官问题

普通 RAG、传统 GraphRAG 和 Agentic GraphRAG 的边界是什么？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

普通 RAG 做一次召回，GraphRAG增加结构，Agentic GraphRAG还会诊断不足、创建新 RetrievalRound并输出控制建议。

### 深挖回答

普通 RAG 做一次召回，GraphRAG增加结构，Agentic GraphRAG还会诊断不足、创建新 RetrievalRound并输出控制建议。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 1. 为什么需要 Agentic GraphRAG
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 2. 普通 GraphRAG 与 Agentic GraphRAG

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q003 为什么不默认 BM25、Vector、Local、Global、DRIFT 五路全开？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+4月+二面+001/正文.md
- primary_domain: knowledge
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 1. 为什么需要 Agentic GraphRAG
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 2. 普通 GraphRAG 与 Agentic GraphRAG
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-003
- status: Target

### 面试官问题

为什么不默认 BM25、Vector、Local、Global、DRIFT 五路全开？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

固定全开会增加成本、延迟和噪音；Admission要求每个额外 Action都有未解决 Requirement、预算和预期收益。

### 深挖回答

固定全开会增加成本、延迟和噪音；Admission要求每个额外 Action都有未解决 Requirement、预算和预期收益。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 1. 为什么需要 Agentic GraphRAG
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 2. 普通 GraphRAG 与 Agentic GraphRAG

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q004 Retrieval Control Plane 和 Data Plane 分别负责什么？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_原始逐字稿.md
- primary_domain: knowledge
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 1. 为什么需要 Agentic GraphRAG
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 2. 普通 GraphRAG 与 Agentic GraphRAG
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Retrieval Control Plane 和 Data Plane 分别负责什么？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Control Plane决定为什么搜、搜什么、是否足够和下一步；Data Plane只在固定 Snapshot、Scope和Budget内执行 Retriever。

### 深挖回答

Control Plane决定为什么搜、搜什么、是否足够和下一步；Data Plane只在固定 Snapshot、Scope和Budget内执行 Retriever。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 1. 为什么需要 Agentic GraphRAG
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 2. 普通 GraphRAG 与 Agentic GraphRAG

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q005 为什么 BM25 仍然需要？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+技术资料+面试+001/正文.md
- primary_domain: knowledge
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 10. STANDARD 完整流程
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么 BM25 仍然需要？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

BM25擅长条款号、专名、版本和精确术语，提供 lexical recall，补足语义检索的盲点。

### 深挖回答

BM25擅长条款号、专名、版本和精确术语，提供 lexical recall，补足语义检索的盲点。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 10. STANDARD 完整流程
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q006 Vector 检索解决什么问题？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 10. STANDARD 完整流程
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Vector 检索解决什么问题？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Vector擅长同义表达和语义改写，提供 semantic recall，但不等于权限、引用或充分性判断。

### 深挖回答

Vector擅长同义表达和语义改写，提供 semantic recall，但不等于权限、引用或充分性判断。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 10. STANDARD 完整流程
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q007 BM25 和 Vector 返回的是什么粒度？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+4月+二面+001/正文.md
- primary_domain: knowledge
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 10. STANDARD 完整流程
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-007
- status: Target

### 面试官问题

BM25 和 Vector 返回的是什么粒度？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

两路返回带版本、CitationChunk、SourceSpan和分数语义的 ranked candidates，不是最终 Claim。

### 深挖回答

两路返回带版本、CitationChunk、SourceSpan和分数语义的 ranked candidates，不是最终 Claim。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 10. STANDARD 完整流程
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q008 为什么 BM25 raw score 和 Vector similarity 不能直接相加？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_原始逐字稿.md
- primary_domain: knowledge
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 10. STANDARD 完整流程
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-008
- status: Target

### 面试官问题

为什么 BM25 raw score 和 Vector similarity 不能直接相加？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

两者分数的量纲和分布不同，先保留 ranked lists，再以 rank-based RRF或版本化Policy融合。

### 深挖回答

两者分数的量纲和分布不同，先保留 ranked lists，再以 rank-based RRF或版本化Policy融合。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 10. STANDARD 完整流程
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q009 RRF 解决什么问题？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+技术资料+面试+001/正文.md
- primary_domain: knowledge
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-009
- status: Target

### 面试官问题

RRF 解决什么问题？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

RRF只融合多个 ranked list的 rank，输出候选排序，不比较raw score，也不判断证据是否充分。

### 深挖回答

RRF只融合多个 ranked list的 rank，输出候选排序，不比较raw score，也不判断证据是否充分。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q010 RRF 之后为什么还需要 Rerank？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-010
- status: Target

### 面试官问题

RRF 之后为什么还需要 Rerank？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

RRF提高融合稳定性，但候选可能缺定义、法域或引用跨度，所以要在有界池上做Unified Evidence Rerank。

### 深挖回答

RRF提高融合稳定性，但候选可能缺定义、法域或引用跨度，所以要在有界池上做Unified Evidence Rerank。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q011 Recall Stage 为什么宁可多找一些？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+4月+二面+001/正文.md
- primary_domain: knowledge
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Recall Stage 为什么宁可多找一些？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

首轮优先Recall，降低关键证据漏召；之后由Rerank、Selection和Evidence Evaluation控制噪音与成本。

### 深挖回答

首轮优先Recall，降低关键证据漏召；之后由Rerank、Selection和Evidence Evaluation控制噪音与成本。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q012 Retriever Top-N、RRF cap、Rerank Top-K 为什么不是同一个数？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_原始逐字稿.md
- primary_domain: knowledge
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Retriever Top-N、RRF cap、Rerank Top-K 为什么不是同一个数？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Retriever N、fusion cap、rerank K和evidence budget处在不同阶段，服务不同的延迟、Token和质量约束。

### 深挖回答

Retriever N、fusion cap、rerank K和evidence budget处在不同阶段，服务不同的延迟、Token和质量约束。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

### Interview Drill Chain B：Q013–Q024

连续追问从概念进入机制、失败、取舍和证据。

## Q013 Rerank 和 Evidence Evaluation 有什么区别？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+技术资料+面试+001/正文.md
- primary_domain: knowledge
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Rerank 和 Evidence Evaluation 有什么区别？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Rerank问候选谁更相关；Evidence Evaluation问候选集合是否足以支撑Claim并检查多维质量。

### 深挖回答

Rerank问候选谁更相关；Evidence Evaluation问候选集合是否足以支撑Claim并检查多维质量。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q014 First-pass Rerank 和 Unified Evidence Rerank 是否是两个架构步骤？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-014
- status: Target

### 面试官问题

First-pass Rerank 和 Unified Evidence Rerank 是否是两个架构步骤？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

架构只保留一个canonical Unified Evidence Rerank；Adapter内的pre-rank是实现优化，不是第二套事实。

### 深挖回答

架构只保留一个canonical Unified Evidence Rerank；Adapter内的pre-rank是实现优化，不是第二套事实。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15. Fusion、Rerank 与 Selection
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.1 Recall、RRF、Rerank 与 Evidence Evaluation 的分工

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q015 CitationChunk 是什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+4月+二面+001/正文.md
- primary_domain: knowledge
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-015
- status: Target

### 面试官问题

CitationChunk 是什么？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

CitationChunk是给检索、排序、Context和Citation消费的文本单元，不等于原文身份。

### 深挖回答

CitationChunk是给检索、排序、Context和Citation消费的文本单元，不等于原文身份。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q016 SourceSpan 是什么？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_原始逐字稿.md
- primary_domain: knowledge
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-016
- status: Target

### 面试官问题

SourceSpan 是什么？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

SourceSpan是DocumentVersion中的精确定位、provenance、content hash和审计来源，是strict Citation的最终事实。

### 深挖回答

SourceSpan是DocumentVersion中的精确定位、provenance、content hash和审计来源，是strict Citation的最终事实。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q017 CitationChunk 和 SourceSpan 是一对一吗？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+技术资料+面试+001/正文.md
- primary_domain: knowledge
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-017
- status: Target

### 面试官问题

CitationChunk 和 SourceSpan 是一对一吗？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

它们不是一对一：一个Chunk可含多个Span，一个Span也可被不同ChunkingPolicy复用。

### 深挖回答

它们不是一对一：一个Chunk可含多个Span，一个Span也可被不同ChunkingPolicy复用。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q018 为什么不能只保存 Chunk 文本？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-018
- status: Target

### 面试官问题

为什么不能只保存 Chunk 文本？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Chunk本身不能证明版本、位置、hash、权限和审计；没有SourceSpan最多只能AUXILIARY_ONLY。

### 深挖回答

Chunk本身不能证明版本、位置、hash、权限和审计；没有SourceSpan最多只能AUXILIARY_ONLY。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q019 EvidenceCandidate 到 SourceObject 的完整 lineage 是什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+4月+二面+001/正文.md
- primary_domain: knowledge
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-019
- status: Target

### 面试官问题

EvidenceCandidate 到 SourceObject 的完整 lineage 是什么？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

完整链是EvidenceCandidate→CitationChunk→one-or-more SourceSpan→DocumentVersion→SourceObject。

### 深挖回答

完整链是EvidenceCandidate→CitationChunk→one-or-more SourceSpan→DocumentVersion→SourceObject。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q020 文档重新上传后 Citation 如何避免漂移？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_原始逐字稿.md
- primary_domain: knowledge
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-020
- status: Target

### 面试官问题

文档重新上传后 Citation 如何避免漂移？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

新上传产生新DocumentVersion和Span lineage；旧Citation不原地改写，无法映射时进入Repair或CITATION_INELIGIBLE。

### 深挖回答

新上传产生新DocumentVersion和Span lineage；旧Citation不原地改写，无法映射时进入Repair或CITATION_INELIGIBLE。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q021 Chunking Policy 改变后旧 Citation 怎么办？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+技术资料+面试+001/正文.md
- primary_domain: knowledge
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-021
- status: Target

### 面试官问题

Chunking Policy 改变后旧 Citation 怎么办？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

新Chunk只能引用新Span和版本；旧Citation保留历史lineage，不能按字符位置盲迁移。

### 深挖回答

新Chunk只能引用新Span和版本；旧Citation保留历史lineage，不能按字符位置盲迁移。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 7.2 三种检索粒度
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 38. EvidenceRecord

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q022 SearchAction 和 EvidenceRequirement 的关系是什么？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 14.1 SearchAction 层级
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 36. RetrieverAction
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

SearchAction 和 EvidenceRequirement 的关系是什么？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Requirement是证据目标，SearchAction是解决目标的检索路线，一个Requirement可选1..N个互补Action。

### 深挖回答

Requirement是证据目标，SearchAction是解决目标的检索路线，一个Requirement可选1..N个互补Action。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 14.1 SearchAction 层级
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 36. RetrieverAction

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q023 一个 EvidenceRequirement 为什么允许多个 SearchAction？

- source_type: REAL
- source_ref: interview-notes/RAG/RAG+4月+二面+001/正文.md
- primary_domain: knowledge
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 14.1 SearchAction 层级
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 36. RetrieverAction
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

一个 EvidenceRequirement 为什么允许多个 SearchAction？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

风险审查常需文本事实和交叉引用，多个Action只有在互补、可解释且预算允许时才通过Admission。

### 深挖回答

风险审查常需文本事实和交叉引用，多个Action只有在互补、可解释且预算允许时才通过Admission。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 14.1 SearchAction 层级
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 36. RetrieverAction

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q024 HYBRID 是一个 Action，还是 BM25/Vector 两个 Action？

- source_type: REAL
- source_ref: internship-work/interview/02_则知科技_Agent开发实习/01_面试_原始逐字稿.md
- primary_domain: knowledge
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 14.1 SearchAction 层级
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 36. RetrieverAction
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-024
- status: Target

### 面试官问题

HYBRID 是一个 Action，还是 BM25/Vector 两个 Action？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

HYBRID是逻辑Action，内部并行BM25和Vector；具体operator attempt由RetrieverAction记录。

### 深挖回答

HYBRID是逻辑Action，内部并行BM25和Vector；具体operator attempt由RetrieverAction记录。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 14.1 SearchAction 层级
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 36. RetrieverAction

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

### Interview Drill Chain C：Q025–Q036

连续追问从概念进入机制、失败、取舍和证据。

## Q025 什么时候 Query Policy 应偏向 lexical？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 14.1 SearchAction 层级
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 36. RetrieverAction
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

什么时候 Query Policy 应偏向 lexical？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

精确条款号、专名和版本可使用lexical-preferred budget，但仍保留统一Evidence Gate。

### 深挖回答

精确条款号、专名和版本可使用lexical-preferred budget，但仍保留统一Evidence Gate。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 14.1 SearchAction 层级
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 36. RetrieverAction

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q026 Graph Local 的 seed Entity 从哪里来？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Graph Local 的 seed Entity 从哪里来？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Local seed优先来自已授权文本命中、高置信实体解析或显式实体，没有可靠seed不能全图游走。

### 深挖回答

Local seed优先来自已授权文本命中、高置信实体解析或显式实体，没有可靠seed不能全图游走。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q027 Entity Linking 错了会怎样？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Entity Linking 错了会怎样？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

错误Entity Linking会污染GraphPath，因此要记录confidence、scope、version和rejected path。

### 深挖回答

错误Entity Linking会污染GraphPath，因此要记录confidence、scope、version和rejected path。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q028 为什么 Graph Local 不能无限 k-hop？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么 Graph Local 不能无限 k-hop？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

无限k-hop会产生hub、循环、延迟和噪音；hop、fanout、path、deadline和budget必须受限。

### 深挖回答

无限k-hop会产生hub、循环、延迟和噪音；hop、fanout、path、deadline和budget必须受限。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q029 Graph Local 如何限制 Relation Type？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Graph Local 如何限制 Relation Type？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Graph constraints按relation type、方向、scope、jurisdiction和时间筛选，而不是只按距离。

### 深挖回答

Graph constraints按relation type、方向、scope、jurisdiction和时间筛选，而不是只按距离。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q030 Graph Local 原生返回的是 Chunk 还是 Relation？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-030
- status: Target

### 面试官问题

Graph Local 原生返回的是 Chunk 还是 Relation？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Graph原生结果可以是Entity、Relation和GraphPath；必须Materialization回链到CitationChunk/SourceSpan。

### 深挖回答

Graph原生结果可以是Entity、Relation和GraphPath；必须Materialization回链到CitationChunk/SourceSpan。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q031 GraphPath 能直接作为最终 Citation 吗？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-031
- status: Target

### 面试官问题

GraphPath 能直接作为最终 Citation 吗？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

GraphPath是provenance、structural relevance和trace，strict Citation仍须绑定基础SourceSpan。

### 深挖回答

GraphPath是provenance、structural relevance和trace，strict Citation仍须绑定基础SourceSpan。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q032 Evidence Materialization 做了什么？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-032
- status: Target

### 面试官问题

Evidence Materialization 做了什么？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Materialization把结构发现转为带SourceSpan、版本、权限和引用资格的Source-backed Candidate。

### 深挖回答

Materialization把结构发现转为带SourceSpan、版本、权限和引用资格的Source-backed Candidate。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 15.2 Candidate Materialization 与 Canonical Dedup

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q033 同一 SourceSpan 被三路检索发现怎么 Dedup？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 1. 为什么需要 Agentic GraphRAG
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 2. 普通 GraphRAG 与 Agentic GraphRAG
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-033
- status: Target

### 面试官问题

同一 SourceSpan 被三路检索发现怎么 Dedup？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

按knowledge_space、document_version、source_span_ref和content_hash去重，保留一个Candidate并合并origins。

### 深挖回答

按knowledge_space、document_version、source_span_ref和content_hash去重，保留一个Candidate并合并origins。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 1. 为什么需要 Agentic GraphRAG
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 2. 普通 GraphRAG 与 Agentic GraphRAG

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q034 Graph Global 为什么不能与 BM25 Chunk 直接做 raw-score fusion？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-034
- status: Target

### 面试官问题

Graph Global 为什么不能与 BM25 Chunk 直接做 raw-score fusion？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Community Report是派生摘要，score量纲不同，必须先转为derived candidate并做SourceSpan backfill。

### 深挖回答

Community Report是派生摘要，score量纲不同，必须先转为derived candidate并做SourceSpan backfill。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q035 Community Report 是什么？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Community Report 是什么？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Community用于corpus-level coverage和导航，不是atomic strict citation。

### 深挖回答

Community用于corpus-level coverage和导航，不是atomic strict citation。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q036 Community Report 能直接证明法律结论吗？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Community Report 能直接证明法律结论吗？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

法律结论必须回到权限、时间和定位均有效的SourceSpan，Community只能辅助发现或引导backfill。

### 深挖回答

法律结论必须回到权限、时间和定位均有效的SourceSpan，Community只能辅助发现或引导backfill。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

### Interview Drill Chain D：Q037–Q048

连续追问从概念进入机制、失败、取舍和证据。

## Q037 什么时候使用 Graph Global？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

什么时候使用 Graph Global？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

跨文档、跨社区主题或总体模式需要Global；单条款事实不应承担Global成本。

### 深挖回答

跨文档、跨社区主题或总体模式需要Global；单条款事实不应承担Global成本。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q038 Global 太贵或社区版本过旧怎么办？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Global 太贵或社区版本过旧怎么办？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

按Snapshot、deadline、budget和Assurance Policy跳过、等待或治理降级，不能把旧Community当当前证据。

### 深挖回答

按Snapshot、deadline、budget和Assurance Policy跳过、等待或治理降级，不能把旧Community当当前证据。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q039 DRIFT 和 Graph Local 有什么区别？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

DRIFT 和 Graph Local 有什么区别？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Local围绕已知实体有界扩展，DRIFT从seed观察frontier并提出有界primer/follow-up。

### 深挖回答

Local围绕已知实体有界扩展，DRIFT从seed观察frontier并提出有界primer/follow-up。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q040 DRIFT 是另一种无限游走 Retriever 吗？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

DRIFT 是另一种无限游走 Retriever 吗？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

DRIFT不是无限游走，每次扩展都绑定Requirement、novelty、hop、token、deadline和budget。

### 深挖回答

DRIFT不是无限游走，每次扩展都绑定Requirement、novelty、hop、token、deadline和budget。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q041 什么条件触发 DRIFT？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

什么条件触发 DRIFT？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

问题宽泛、初始路径不完整且frontier仍有可解释增益时触发DRIFT。

### 深挖回答

问题宽泛、初始路径不完整且frontier仍有可解释增益时触发DRIFT。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q042 如何防止 DRIFT 无限探索？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

如何防止 DRIFT 无限探索？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

记录已探索/拒绝路径、marginal gain、budget和deadline，低增益或无新Requirement即停。

### 深挖回答

记录已探索/拒绝路径、marginal gain、budget和deadline，低增益或无新Requirement即停。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q043 DRIFT 找到的结果如何回到 SourceSpan？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

DRIFT 找到的结果如何回到 SourceSpan？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

DRIFT结果必须Materialization和SourceSpan backfill，缺strict span只能partial/auxiliary。

### 深挖回答

DRIFT结果必须Materialization和SourceSpan backfill，缺strict span只能partial/auxiliary。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 12. Graph 路由
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q044 Claim、EvidenceRequirement、QuerySpec、Requery 如何区分？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 14. Evidence Requirement 与 Evidence Frontier
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 35. QueryStrategyDecision
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Claim、EvidenceRequirement、QuerySpec、Requery 如何区分？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Claim是待输出判断，Requirement是证明它所需证据，QuerySpec是一次查询表达，Requery是下一次查询建议。

### 深挖回答

Claim是待输出判断，Requirement是证明它所需证据，QuerySpec是一次查询表达，Requery是下一次查询建议。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 14. Evidence Requirement 与 Evidence Frontier
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 35. QueryStrategyDecision

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q045 QuerySpec 由谁生成，谁能执行？

- source_type: DERIVED
- source_ref: derived-from: interview-notes/RAG/RAG+题库汇总+面试+002/正文.md
- primary_domain: knowledge
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 14. Evidence Requirement 与 Evidence Frontier
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 35. QueryStrategyDecision
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

QuerySpec 由谁生成，谁能执行？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Planner或模型可提出QuerySpec，确定性Admission检查Scope、Snapshot、Budget、版本和目标后才执行。

### 深挖回答

Planner或模型可提出QuerySpec，确定性Admission检查Scope、Snapshot、Budget、版本和目标后才执行。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 14. Evidence Requirement 与 Evidence Frontier
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 35. QueryStrategyDecision

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q046 Requery 和 Replan 是一回事吗？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 14. Evidence Requirement 与 Evidence Frontier
- primary_domain: knowledge
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 14. Evidence Requirement 与 Evidence Frontier
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 35. QueryStrategyDecision
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Requery 和 Replan 是一回事吗？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Requery只创建新的Knowledge RetrievalRound；Replan改变任务前提，必须回到Agent Core。

### 深挖回答

Requery只创建新的Knowledge RetrievalRound；Replan改变任务前提，必须回到Agent Core。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 14. Evidence Requirement 与 Evidence Frontier
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 35. QueryStrategyDecision

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q047 EvidenceLedger 保存什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- primary_domain: knowledge
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 39. EvidenceVerdict
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

EvidenceLedger 保存什么？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Ledger append-only记录候选、来源、coverage、冲突、引用资格、选择和诊断。

### 深挖回答

Ledger append-only记录候选、来源、coverage、冲突、引用资格、选择和诊断。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 39. EvidenceVerdict

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q048 Evidence Evaluation 至少看哪些维度？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- primary_domain: knowledge
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 39. EvidenceVerdict
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Evidence Evaluation 至少看哪些维度？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Evaluation至少检查coverage、claim support、citation integrity、authority、conflict、freshness、temporal、jurisdiction、security和novelty。

### 深挖回答

Evaluation至少检查coverage、claim support、citation integrity、authority、conflict、freshness、temporal、jurisdiction、security和novelty。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 39. EvidenceVerdict

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

### Interview Drill Chain E：Q049–Q060

连续追问从概念进入机制、失败、取舍和证据。

## Q049 为什么高 relevance 不等于 evidence sufficient？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- primary_domain: knowledge
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 39. EvidenceVerdict
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

为什么高 relevance 不等于 evidence sufficient？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

相似度只说明可能相关，不能证明覆盖完整、authority足够、时间/法域有效和可strict引用。

### 深挖回答

相似度只说明可能相关，不能证明覆盖完整、authority足够、时间/法域有效和可strict引用。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 16. Evidence Quality Gates
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 39. EvidenceVerdict

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q050 Failure Diagnosis 的作用是什么？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- primary_domain: knowledge
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Failure Diagnosis 的作用是什么？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Failure Diagnosis把漏召、错召、定义/引用缺失、法域未知、权限过滤和索引失败映射到可审计路线。

### 深挖回答

Failure Diagnosis把漏召、错召、定义/引用缺失、法域未知、权限过滤和索引失败映射到可审计路线。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q051 CITATION_SPAN_MISSING 怎么处理？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- primary_domain: knowledge
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

CITATION_SPAN_MISSING 怎么处理？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

CITATION_SPAN_MISSING走focused backfill；仍无定位来源就Partial/Abstain，不能伪造。

### 深挖回答

CITATION_SPAN_MISSING走focused backfill；仍无定位来源就Partial/Abstain，不能伪造。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q052 Graph 不可用但 Requirement mandatory 怎么处理？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- primary_domain: knowledge
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Graph 不可用但 Requirement mandatory 怎么处理？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Graph mandatory不可用时按Assurance Policy等待、治理降级或输出control proposal，不能冒充Graph证据。

### 深挖回答

Graph mandatory不可用时按Assurance Policy等待、治理降级或输出control proposal，不能冒充Graph证据。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q053 权限过滤导致证据不足怎么办？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- primary_domain: knowledge
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

权限过滤导致证据不足怎么办？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

权限过滤保持原Scope，输出partial、ask或abstain，不能扩大权限。

### 深挖回答

权限过滤保持原Scope，输出partial、ask或abstain，不能扩大权限。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q054 Retriever timeout 能不能直接重试？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- primary_domain: knowledge
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Retriever timeout 能不能直接重试？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

只有明确transient且保留Snapshot、Scope、Budget和幂等约束时才bounded retry。

### 深挖回答

只有明确transient且保留Snapshot、Scope、Budget和幂等约束时才bounded retry。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q055 Retry、Corrective Retrieval、Retrieval Replan 有什么区别？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- primary_domain: knowledge
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix
- initial_coverage_status: PARTIAL
- coverage_status: FULL
- gap_id: CLOSED-GAP-03-055
- status: Target

### 面试官问题

Retry、Corrective Retrieval、Retrieval Replan 有什么区别？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Retry重做同一动作，Corrective改变获取方法，Retrieval Replan重排Knowledge内部Round，任务前提变化才Agent Replan。

### 深挖回答

Retry重做同一动作，Corrective改变获取方法，Retrieval Replan重排Knowledge内部Round，任务前提变化才Agent Replan。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 44. Failure Taxonomy
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 45. Failure Decision Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q056 新交叉引用为什么可能触发 Retrieval Replan？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 18. Retry、Corrective Retrieval 与 Replan
- primary_domain: knowledge
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 18. Retry、Corrective Retrieval 与 Replan
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 42. KnowledgeControlProposal
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

新交叉引用为什么可能触发 Retrieval Replan？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

新交叉引用先扩展Frontier和新Round；只有计划前提失效才形成KnowledgeControlProposal。

### 深挖回答

新交叉引用先扩展Frontier和新Round；只有计划前提失效才形成KnowledgeControlProposal。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 18. Retry、Corrective Retrieval 与 Replan
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 42. KnowledgeControlProposal

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q057 什么情况下必须交给 Agent Core Replan？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 18. Retry、Corrective Retrieval 与 Replan
- primary_domain: knowledge
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 18. Retry、Corrective Retrieval 与 Replan
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 42. KnowledgeControlProposal
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

什么情况下必须交给 Agent Core Replan？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

目标、依赖、能力或强制前提改变时才由Agent Core经Replan Barrier创建新PlanVersion。

### 深挖回答

目标、依赖、能力或强制前提改变时才由Agent Core经Replan Barrier创建新PlanVersion。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 18. Retry、Corrective Retrieval 与 Replan
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 42. KnowledgeControlProposal

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q058 检索最多几轮？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 26. Budget
- primary_domain: knowledge
- difficulty: L2
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 26. Budget
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 55. Test Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

检索最多几轮？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

没有固定臆造数字；hard max、deadline和budget由Profile配置并由Eval校准。

### 深挖回答

没有固定臆造数字；hard max、deadline和budget由Profile配置并由Eval校准。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 26. Budget
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 55. Test Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q059 Marginal Evidence Gain 如何帮助停止？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- primary_domain: knowledge
- difficulty: L3
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 40. SelectedEvidenceBundle
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

Marginal Evidence Gain 如何帮助停止？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

Marginal Evidence Gain比较新增候选对未解决Requirement、Claim Support、Citation和Novelty的增益。

### 深挖回答

Marginal Evidence Gain比较新增候选对未解决Requirement、Claim Support、Citation和Novelty的增益。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 40. SelectedEvidenceBundle

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q060 什么条件下 Stop Controller 可以结束检索？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- primary_domain: knowledge
- difficulty: L4
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 40. SelectedEvidenceBundle
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

什么条件下 Stop Controller 可以结束检索？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

所有强制Requirement满足，或进入受治理的partial/ask/abstain/failed路径，Stop才可结束。

### 深挖回答

所有强制Requirement满足，或进入受治理的partial/ask/abstain/failed路径，Stop才可结束。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 40. SelectedEvidenceBundle

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

### Interview Drill Chain F：Q061–Q065

连续追问从概念进入机制、失败、取舍和证据。

## Q061 没有证据为什么不能强答？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- primary_domain: knowledge
- difficulty: L5
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 40. SelectedEvidenceBundle
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

没有证据为什么不能强答？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

没有合格Evidence/Citation就不能完成Final Gate，必须显式表达不确定性。

### 深挖回答

没有合格Evidence/Citation就不能完成Final Gate，必须显式表达不确定性。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 19. 停止与控制输出
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 40. SelectedEvidenceBundle

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q062 BM25、Vector、Graph 版本如何保持一致？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 20. 领域状态与 Checkpointer 边界
- primary_domain: knowledge
- difficulty: L6
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 20. 领域状态与 Checkpointer 边界
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 28. Recovery 与 Reconciliation
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

BM25、Vector、Graph 版本如何保持一致？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

一次Run pin KnowledgeSnapshot，所有RetrieverAction引用同一Snapshot、Scope和generation。

### 深挖回答

一次Run pin KnowledgeSnapshot，所有RetrieverAction引用同一Snapshot、Scope和generation。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 20. 领域状态与 Checkpointer 边界
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 28. Recovery 与 Reconciliation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q063 同一次 RetrievalRun 中索引正在更新怎么办？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 20. 领域状态与 Checkpointer 边界
- primary_domain: knowledge
- difficulty: L7
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 20. 领域状态与 Checkpointer 边界
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 28. Recovery 与 Reconciliation
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

同一次 RetrievalRun 中索引正在更新怎么办？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

索引更新不改变运行中的Snapshot；新版本用新Snapshot和新Run提供。

### 深挖回答

索引更新不改变运行中的Snapshot；新版本用新Snapshot和新Run提供。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 20. 领域状态与 Checkpointer 边界
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 28. Recovery 与 Reconciliation

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q064 如何证明 Agentic GraphRAG 比固定 Hybrid+Graph 更好？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 34. Agentic GraphRAG Eval
- primary_domain: knowledge
- difficulty: L8
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 34. Agentic GraphRAG Eval
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 55. Test Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

如何证明 Agentic GraphRAG 比固定 Hybrid+Graph 更好？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

用固定Dataset、Snapshot、Budget和ablation比较质量、Citation、Route/Stop Accuracy、Latency和Cost。

### 深挖回答

用固定Dataset、Snapshot、Budget和ablation比较质量、Citation、Route/Stop Accuracy、Latency和Cost。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 34. Agentic GraphRAG Eval
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 55. Test Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。

## Q065 如何评测 Route Accuracy？

- source_type: ARCHITECTURE_STRESS
- source_ref: zuno-target: docs/project/modules/03-knowledge-agentic-graphrag.md — § 34. Agentic GraphRAG Eval
- primary_domain: knowledge
- difficulty: L1
- interview_probability: HIGH
- resume_trigger: Agentic GraphRAG、Evidence Retrieval
- architecture_refs:
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 34. Agentic GraphRAG Eval
  - docs/project/modules/03-knowledge-agentic-graphrag.md — § 55. Test Matrix
- initial_coverage_status: FULL
- coverage_status: FULL
- gap_id: None
- status: Target

### 面试官问题

如何评测 Route Accuracy？

### 他真正想考什么

检验是否能把 Recall、Precision、Evidence、Failure 和 Eval 串成机制，而不是只背诵名词。

### 30 秒回答

该问题由对应 canonical 章节定义，回答必须保留Target边界并由确定性Gate验证。

### 深挖回答

该问题由对应 canonical 章节定义，回答必须保留Target边界并由确定性Gate验证。 模型只能提出策略或Candidate，确定性Runtime负责Snapshot、Scope、状态、版本、幂等和审计；本文只表达Target，不声称Current实现或生产指标。

### 可能继续追问

1. 输入事实、触发条件和边界是什么？
2. 谁提出Proposal，哪个确定性Gate裁决？
3. 状态、版本、Scope或持久化事实怎样变化？
4. 失败时为什么选Retry、Repair、Replan或Reconciliation？
5. 怎样用Test、Trace或Eval证明？

### Architecture Evidence

- docs/project/modules/03-knowledge-agentic-graphrag.md — § 34. Agentic GraphRAG Eval
- docs/project/modules/03-knowledge-agentic-graphrag.md — § 55. Test Matrix

### 当前文档是否足够回答

FULL

### 如果不够，缺什么

None。第一轮记录的缺口已写回canonical architecture；本QA不新增架构事实。
