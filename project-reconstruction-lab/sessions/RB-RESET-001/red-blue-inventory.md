# Red / Blue Inventory

## 盘点基线

```text
base_sha: 8904004c7f236f030b07cef0960aa9b4d8c509ce
source: project-reconstruction-lab/05-red-blue/, project-reconstruction-lab/sessions/,
        docs/governance/, .agent/, tools/scripts/
```

## Active workspace（重置前）

重置前 `05-red-blue/` 混合了：

- `round-protocol-v2/v3/v3.1/v3.1.2/v3.1.3/v4/v4.1/v4.2`；
- V4、V4.1、V4.2 的 Prompt、Review Template 和 Interview Calibration；
- Attack Registry、Blue Repair、Counter Attack、Evidence Closure、Kill Test、Complexity Card；
- 11+1 Coverage Map 和一个包含多代规则的 Active README。

这些内容分别对应历史 Protocol、历史操作指南或历史辅助材料，不再适合作为单一 active
入口。

## Sessions

`project-reconstruction-lab/sessions/` 保留以下已存在的历史/证据会话族：V2 Round-001、
V3 Round-002、V3.1 Round-003、Document Normalization、Round-004、Round-005、Semantic
Audit、Blue Repair、Evidence Closure、P0 V4、Gate Realignment、V4/V4.1/V4.2 Bootstrap、
Round-006 和独立 Implementation Evidence Track。它们是审计材料，不是新 Protocol。

本轮新增的唯一 Session 是 `RB-RESET-001`；没有创建 Round-007。

## Governance / Routing / Verification

- `AGENTS.md`：仓库入口和不可变边界；
- `.agent/system.yaml`：任务路由和验证命令；
- `.agent/references/{workflow,task-routing,verification-map,current-program}.md`：执行路由；
- `tools/scripts/verify_red_blue_*`、`verify_*round*`、`verify_*closure*`：历史格式和已完成
  Session 的兼容验证器，不等于 active Protocol；
- `tests/repo/`：历史 Protocol/Session 回归和本轮 reset/readability 验证。

## 结论

盘点发现的主要风险不是缺少更多流程，而是历史规则仍位于 active 入口。Reset 通过归档、
最小入口、路由同步和专用 reset verifier 消除该歧义。
