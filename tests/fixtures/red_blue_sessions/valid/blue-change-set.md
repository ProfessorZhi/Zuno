# Blue Change Set

## CHANGE-001

```text
Change ID：CHANGE-001
Source Cluster IDs：CLUSTER-001
Target：project
Problem：项目知识入口需要明确三层边界。
Current Design：入口说明分散。
Proposed Design：以 docs/project/README.md 作为统一入口。
Decision：KEEP
Why：降低事实、架构和模块混淆。
Alternatives：维持平铺 docs 入口。
Affected Modules：Project Knowledge
Contract Changes：none
Migration / Implementation Implication：更新入口链接。
Evidence Needed：文档入口验证。
User Gate：APPROVED
Sync Status：APPLIED
Canonical Paths：docs/project/README.md
Applied Commit SHA：7c4b740ac5760b6a3ed42286d4231fe70fbbf18a
Validation Run：python tools/scripts/verify_docs_entrypoints.py
Validation Not Run：none
Retest IDs：RETEST-001
```
