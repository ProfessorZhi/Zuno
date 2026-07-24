# PHASE12 Knowledge Version and Standard RAG

phase_id: PHASE12
status: ready
depends_on: PHASE08, PHASE11
owner: Module 03 Knowledge / Agentic GraphRAG

## Phase 目标

先实现稳定、可发布、可回滚的 Knowledge 基线：KnowledgeVersion、KnowledgeSnapshot、Index Build/Verify/Cutover、BM25/Vector Hybrid Retrieval、Fusion/Rerank、Evidence、CitationLineage、ACL/Temporal/Authority/Conflict 和 Standard RAG。此 Phase 不实现 Agentic 多轮纠正。

## Minimal Read Set

- `docs/modules/03-knowledge-agentic-graphrag.md`
- PHASE11 IndexableDocumentSnapshot/SourceSpan
- PHASE03 Knowledge Contract
- PHASE04 PostgreSQL/Object/Queue
- PHASE05 Security
- PHASE08 Agent Core Knowledge Port
- 当前 knowledge/retrieval/index/evidence/citation 代码

## Current Anchors

```text
src/backend/zuno/knowledge/**
src/backend/zuno/services/rag/** through current aliases
local BM25/vector/graph index code
GraphRAGQueryService / RetrievalPlanner / EvidenceBundle / CitationBuilder
index manifest and chunk code
```

## Allowed Paths

```text
src/backend/zuno/knowledge/domain/**
src/backend/zuno/knowledge/application/**
src/backend/zuno/knowledge/index/**
src/backend/zuno/knowledge/retrieval/**
src/backend/zuno/knowledge/evidence/**
src/backend/zuno/platform/database/knowledge/**
alembic/**
tests/knowledge/**
tests/integration/knowledge/**
tests/fault/knowledge/**
docs/evidence/**
```

## Forbidden Paths

- Knowledge 创建/激活 Agent PlanVersion 或决定最终 Ask User/Replan/Finalize。
- Input 直接拥有 Chunk/Entity/KnowledgeVersion。
- Index 写入完成冒充 Knowledge Publication。
- 在本 Phase 伪装 Agentic GraphRAG 已完成。

## Work Packages

### P12-T01 KnowledgeVersion and Snapshot Domain
- Goal：实现 corpus manifest、document version set、schema/extractor/chunker/embedding/index config refs、status、generation、publication。
- States：DRAFT→BUILDING→VERIFYING→READY→ACTIVE→SUPERSEDED/REVOKED/DELETED。
- Tests：immutability、CAS activation、stale generation、tenant/workspace scope、revocation。
- Acceptance：一次 Query 固定 KnowledgeSnapshot，不读浮动“latest”。

### P12-T02 Chunk and Source Lineage Build
- Goal：从 CanonicalDocumentIR 建 Chunk/TextUnit，保留 SourceSpan、TransformLedger、ACL、temporal/authority metadata。
- Tests：deterministic chunk IDs、rebuild same hash、page/table/OCR citation、delete propagation。
- Acceptance：Chunk 是 Knowledge projection，不反写 Input IR。

### P12-T03 Index Build Job and Write Batches
- Goal：实现 BM25/Vector/Graph projection build job、write batch、lease/fencing、manifest、attempt。
- Tests：duplicate batch、partial failure、worker crash、lease loss、retry exhausted、schema mismatch。
- Acceptance：各 Index 可重建；Job receipt 不等于 publication。

### P12-T04 Visibility Verification and Cutover
- Goal：验证写入可见性、count/hash/sample retrieval、serving watermark，然后原子切换 active version。
- Tests：visibility lag、missing vector、stale alias、cutover race、rollback to prior version。
- Acceptance：只有 Knowledge Owner 提交 Publication/Cutover 事实。

### P12-T05 Standard Hybrid Retrieval
- Goal：实现 Query Normalize（确定性）、BM25/Vector parallel retrieve、filter、fusion、rerank、top-k budget。
- Tests：single-hop、ACL、temporal version、no-result、timeout/partial retriever、deterministic fusion。
- Acceptance：首次检索只产生 RetrievalOutcome，不自行循环。

### P12-T06 Evidence, Authority, Temporal and Conflict Ledger
- Goal：构建 EvidenceItem/EvidenceBundle、authority、valid-time、conflict group、support/contradict、accepted/rejected reason。
- Tests：conflicting policies、expired evidence、low authority、duplicate spans、cross-tenant evidence。
- Acceptance：Evidence 是 Knowledge 事实，Final Answer 仍归 Agent Core。

### P12-T07 CitationLineage and Strict Grounding
- Goal：实现 Claim/Evidence/Citation ref 所需的 document/page/span/text availability 和 graph-to-text base contract。
- Tests：source text missing、span hash mismatch、deleted source、citation authorization、citation precision fixtures。
- Acceptance：无 SourceSpan 的候选不能作为 strict evidence。

### P12-T08 Standard RAG Cutover and Old Query Service Removal Plan
- Goal：让 Agent Core 标准检索真实调用新 Knowledge Port，shadow 对比旧 QueryService，再 canary/default new。
- Tests：same query/snapshot、evidence/citation parity、rollback、no duplicate index reads。
- Acceptance：旧 `services/rag`/alias 仅临时 adapter；PHASE22 删除旧目录/alias，不保留 `legacy_rag`。

## Phase 完成定义

- KnowledgeVersion/Snapshot/Build/Verify/Cutover 可运行并恢复。
- Standard Hybrid RAG 产生真实 Evidence/CitationLineage。
- Delete/Revocation/ACL/Conflict/Temporal 测试通过。
- Agentic 内层循环仍为后续 Target，未提前声明。

## Validation

```bash
git diff --check
pytest -q tests/knowledge tests/integration/knowledge tests/fault/knowledge -p no:cacheprovider
# run retrieval/citation golden fixtures discovered in PHASE01
```
