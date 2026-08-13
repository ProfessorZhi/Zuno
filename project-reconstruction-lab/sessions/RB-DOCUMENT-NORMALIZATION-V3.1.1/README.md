# RB-DOCUMENT-NORMALIZATION-V3.1.1

本 Session 记录 Canonical Part A / Part B 的结构归一化，不是新的 100Q Round，也不是 Runtime、Facts 或 Production 证据。

## Status

- Protocol: ZUNO-RED-BLUE-WORKFLOW-V3.1.1
- BASE_SHA: 4b361fe51486b4cfbede9ab9725a3e2b5c6fd48a
- FINAL_SHA: recorded in final handoff
- Round-004: READY_NOT_STARTED
- Facts changed: NONE
- Runtime changed: NONE
- Schema/Migration/Dependencies/Production Infra changed: NONE
- ADR changed: NONE
- Full CI: NOT RUN

## Scope

本轮将 12 份 Canonical Owner 文档从 Part A → Part B → Legacy Main Body 的混排形式归一为同文件双层结构。Part A 使用专题自己的叙事逻辑解释 WHY/WHAT/BIG PICTURE；Part B 保留 HOW EXACTLY 的 Contract、状态、失败、恢复、安全、所有权和验证。

Round、Delta、Question、Score 和 Red/Blue 过程痕迹只保留在 Lab Session，不进入 Canonical 正文。

## Outputs

- canonical-audit.md：修改前 SHA、结构问题和改写范围
- review-package.md：V3.1.1 Review Package
- canonical-sync-record.md：SECTION_REWRITE/FULL_PART_REWRITE 记录
- scorecard.md：Part A/Part B 结构化复核分数
- manifest.yaml：本轮边界与验证状态
