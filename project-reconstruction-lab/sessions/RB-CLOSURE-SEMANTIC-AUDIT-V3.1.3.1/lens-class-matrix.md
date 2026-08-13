# Lens / Closure Class Matrix

Lens 与 Closure Class 正交；统计不用于分配类别。

| Lens | A | I | E | X |
|---|---:|---:|---:|---:|
| 00 Overall Architecture | 3 | 7 | 1 | 1 |
| 01 Product Surface | 1 | 5 | 0 | 0 |
| 02 Input / Document Ingestion | 1 | 6 | 0 | 0 |
| 03 Knowledge / Agentic GraphRAG | 1 | 7 | 2 | 0 |
| 04 Model Gateway | 0 | 3 | 1 | 1 |
| 05 Memory & Context | 0 | 6 | 1 | 1 |
| 06 Agent Core / Planning & Control | 0 | 13 | 2 | 0 |
| 07 Capability / Skill | 0 | 5 | 1 | 0 |
| 08 Tool Runtime | 0 | 8 | 0 | 2 |
| 09 Security | 0 | 6 | 0 | 2 |
| 10 Observability & Eval | 0 | 2 | 3 | 1 |
| 11 Infrastructure | 0 | 3 | 1 | 3 |

## Manual interpretation

Overall 同时出现 A/I/E/X；Memory 也同时出现四类，说明类别不是按 Lens 默认映射。Product、Ingestion、Capability 等类别较少，仍保留多类结果；没有任何 Lens 被验证器自动指定单一 Class。
