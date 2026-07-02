# Capability And Skill Layer

本文说明 Zuno 的 Capability / Skill / Tool / MCP 边界。它只承载稳定架构说明，高频执行细节仍在 `.agent/programs/`。

## 定位

Capability Layer 负责把任务方法、知识访问、工具调用、MCP 连接、Artifact 生成和策略审计统一成可路由、可授权、可观测的能力面。Skill 是任务方法包，描述如何做一类任务；Tool 是具体动作；Knowledge 是检索能力；MCP 是外部工具协议入口。

## Current Local Slice

当前已由代码和测试证明：

- `src/backend/zuno/capability/layer.py` 提供 `CapabilityLayerRegistry`、`CapabilityRouter`、`CapabilityPolicy`、`CapabilityRiskProfile` 和 `CapabilityAuditEvent` 的本地 baseline。
- `src/backend/zuno/capability/runtime.py`、`registry.py`、`policy.py`、`execution.py` 和 `control_plane.py` 保留现有 capability / tool control contracts。
- SkillCard fixtures 已覆盖 `contract_review`、`research_report`、`code_review` 或 `bug_diagnosis` 中的本地可测任务方法包。
- Tool / MCP boundary 在未配置真实外部服务时返回 permission / target-blocked evidence，不 fake success。
- Capability policy 已能阻止跨 workspace KnowledgeCapability 和未授权 Tool/MCP capability。

对应 focused tests 包括 `tests/capability/test_capability_skill_layer.py`、`tests/agent/test_capability_layer_surfaces.py`、`tests/agent/test_capability_system.py`、`tests/agent/test_capability_registry.py` 和 `tests/agent_system/test_agent_guardrails.py`。

## Skill 与 Capability 的关系

```text
SkillCard
  -> recommended_retrieval_profile
  -> required_evidence
  -> allowed_tools
  -> required_memory_scopes
  -> output_contract
  -> safety_policy
  -> eval_rubric
  -> trace_requirements

CapabilityRouter
  -> KnowledgeCapability
  -> ToolCapability
  -> MCPCapability
  -> ArtifactCapability
```

Skill 选择不会绕过 capability policy。即使用户 pin 了 skill，router 仍必须检查 workspace scope、tool permission、network policy、credential policy、side effect level 和 audit policy。

## Launchable Prototype Target

- 把 SkillCard、CapabilityPolicy、Knowledge / Tool / MCP / Artifact capability 边界写入正式归档。
- Product API 继续向用户展示“标准检索 / 深度检索”和任务结果，而不是把 Capability 内部细节做成用户手动工具箱。
- PHASE15 closure 中保留 capability risk、permission denial、target-blocked MCP 和 audit event evidence。

## Production Scale Target

以下仍不是 Current：

- 生产级 Skill Registry 和 skill marketplace。
- 真实 MCP connector governance、connector health、tenant-level approval policy。
- 外部 vault / OAuth credential broker。
- rootless / gVisor / Firecracker sandbox。
- 持久 approval DB 和生产网络代理。

## 不变量

- Skill 不是 Tool，不能把 skill list 写成 tool list。
- MCP 未配置时不能伪装成功调用。
- Capability policy 是 runtime guard，不是 README 里的建议。
