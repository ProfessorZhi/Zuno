# Round-004 Blue Decisions

The table is the structured decision record. The natural-language answer is in blue-answers.md; document_impact is kept next to the decision so a later Canonical Sync cannot silently change only one half of the contract.

| ID | Red Score | Severity | Red Finding | Blue Decision | Architecture After | Complexity Added | Complexity Removed | Document Impact | Canonical Owner Doc | Delta Ref | Sync Mode | Part A / Part B Required |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| Q001 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q002 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q003 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q004 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q005 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q006 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q007 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q008 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q009 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q010 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q011 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q012 | 3/5 | P1 | 场景暴露了需要显式化的 00 Overall Architecture 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/architecture/architecture.md | D001 | NO_CHANGE | NO / NO |
| Q013 | 3/5 | P1 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / NO |
| Q014 | 3/5 | P1 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / YES |
| Q015 | 3/5 | P1 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / NO |
| Q016 | 4/5 | P2 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / YES |
| Q017 | 4/5 | P2 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / YES |
| Q018 | 4/5 | P2 | 场景暴露了需要显式化的 01 Product Surface 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/product/product-architecture.md | D002 | FULL_PART_REWRITE | YES / YES |
| Q019 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q020 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q021 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q022 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q023 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q024 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q025 | 4/5 | P2 | 场景暴露了需要显式化的 02 Input / Document Ingestion 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/knowledge/knowledge-evidence-architecture.md | D003 | NO_CHANGE | NO / NO |
| Q026 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q027 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q028 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q029 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q030 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q031 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q032 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q033 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q034 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q035 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q036 | 4/5 | P2 | 场景暴露了需要显式化的 03 Knowledge / Agentic GraphRAG 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/knowledge/knowledge-evidence-architecture.md | D004 | NO_CHANGE | NO / NO |
| Q037 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q038 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q039 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q040 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q041 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q042 | 4/5 | P2 | 场景暴露了需要显式化的 04 Model Gateway 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/agents/agent-platform.md | D005 | NO_CHANGE | NO / NO |
| Q043 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q044 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q045 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q046 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q047 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q048 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q049 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q050 | 4/5 | P2 | 场景暴露了需要显式化的 05 Memory & Context 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D006 | NO_CHANGE | NO / NO |
| Q051 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q052 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q053 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | NO / YES |
| Q054 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q055 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q056 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | NO / YES |
| Q057 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q058 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | NO / YES |
| Q059 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q060 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | NO / YES |
| Q061 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q062 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q063 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | NO / YES |
| Q064 | 4/5 | P2 | 场景暴露了需要显式化的 06 Agent Core / Planning & Control 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D007 | FULL_PART_REWRITE | YES / YES |
| Q065 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q066 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q067 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q068 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q069 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q070 | 4/5 | P2 | 场景暴露了需要显式化的 07 Capability / Skill 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/agents/agent-platform.md | D008 | NO_CHANGE | NO / NO |
| Q071 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q072 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q073 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q074 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q075 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q076 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q077 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q078 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q079 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q080 | 4/5 | P2 | 场景暴露了需要显式化的 08 Tool Runtime 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D009 | NO_CHANGE | NO / NO |
| Q081 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q082 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q083 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q084 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q085 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q086 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q087 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q088 | 4/5 | P2 | 场景暴露了需要显式化的 09 Security 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/security/security-architecture.md | D010 | NO_CHANGE | NO / NO |
| Q089 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | YES / YES |
| Q090 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | YES / NO |
| Q091 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_B | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | NO / YES |
| Q092 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | YES / YES |
| Q093 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | DEFER | 保留为条件能力并等待替换/消融证据 | 评测与替换门禁 | 无证据的默认启用 | PART_A | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | YES / NO |
| Q094 | 4/5 | P2 | 场景暴露了需要显式化的 10 Observability & Eval 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/eval/legal-eval-and-benchmark.md | D011 | FULL_PART_REWRITE | YES / YES |
| Q095 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | KEEP | 保持 Owner 边界，补足恢复与观测契约 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / YES |
| Q096 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / YES |
| Q097 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / NO |
| Q098 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / YES |
| Q099 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | BOTH | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / YES |
| Q100 | 4/5 | P2 | 场景暴露了需要显式化的 11 Infrastructure 边界 | REFINE | 显式化版本、失败、恢复和幂等边界 | 版本/回执/对账约束 | 隐式重试、双写或无条件合并 | PART_A | docs/project/deployment/microservice-deployment.md | D012 | FULL_PART_REWRITE | YES / NO |
