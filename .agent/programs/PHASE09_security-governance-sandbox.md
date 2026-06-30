# PHASE09 Security Governance Sandbox

status: active

## 目标

把企业私有知识库场景的安全治理前置为系统架构：输入、检索、工具、输出四道闸，配合 policy、workspace、execution、network/credential sandbox。

本 phase 的核心判断：安全不是“最后输出前扫一遍”，而是一个横切控制面。企业知识库 Agent 会读内部文档、调用工具、生成产物、可能访问邮件/数据库/CLI/外部 API，风险来自四类：稳定性风险、越权风险、隐私/商业机密泄露风险、工具副作用风险。提示注入尤其不能只当作 prompt 问题，它可能藏在网页、PDF、邮件、表格、issue、代码注释和检索结果里，必须通过最小权限、隔离、审批和审计来控损。

四层 sandbox 目标：

```text
Policy Sandbox
  ToolCard risk_level, side_effect_level, approval_required, sandbox_required,
  network_policy, credential_policy, audit_required

Workspace Sandbox
  raw knowledge, uploaded files, temp dir, artifact output, read-only source,
  writable workspace, ACL scope and cross-workspace isolation

Execution Sandbox
  local CLI, SSH, code execution, MCP server, heavy parser, artifact renderer,
  timeout, cwd scope, allowlist, resource limit, secret redaction, audit log

Network / Credential Sandbox
  default deny, allowed domains, outbound proxy, credential broker,
  no raw secrets in prompt or sandbox filesystem
```

## 步骤

- [ ] 建立 input gate：auth、rate limit、file validation、PII/business secret scan、prompt injection scan。
- [ ] 建立 retrieval gate：chunk ACL、workspace scope、document trust label、retrieval result sanitization。
- [ ] 建立 tool gate：side effect policy、approval、timeout、cwd/network/credential allowlist。
- [ ] 建立 output gate：DLP、citation coverage、format validation、redaction。
- [ ] 建立 ToolCard security fields：`risk_level`、`side_effect_level`、`approval_required`、`sandbox_required`、`network_policy`、`credential_policy`、`audit_required`。
- [ ] 建立 approval interrupt / resume contract，覆盖 `send_email`、SSH、CLI、删除/覆盖、外部写操作和跨 workspace 读取。
- [ ] 建立 sandbox audit event schema，进入 trace/eval，以便回放 policy decision。
- [ ] 建立 `model_intent` 与 `final_decision` 分离日志，证明模型建议和系统执行决策不是一回事。
- [ ] 增加 verifier 或 tests：secrets 不进入 prompt、trace 明文、artifact、sandbox filesystem。
- [ ] 写 prompt injection、data exfiltration、cross-workspace leakage 和 unauthorized tool call tests。

## 输入 / 输出文件

输入：

- PHASE03 workspace / task / event contract。
- PHASE07 ToolCard risk matrix。
- `src/backend/zuno/platform/security/**`
- `src/backend/zuno/capability/**`
- `tests/security/**`

输出：

- Security gate contracts。
- approval audit schema。
- sandbox profile mapping。
- prompt injection / DLP / cross-workspace regression tests。

## Sandbox Level 到 ToolCard Risk 映射

| Tool risk | 默认 approval | 默认 sandbox | 必测项 |
| --- | --- | --- | --- |
| none | never | none | schema validity。 |
| read | on ACL-sensitive read | workspace_ro | path scope、ACL、audit。 |
| write_local | on overwrite | workspace_rw_artifacts | artifact-only write、no source overwrite。 |
| write_external | always or on_high_risk | network_limited | approval、credential broker、domain allowlist。 |
| destructive | admin_only / disabled | execution_restricted or disabled | 默认不可自动执行。 |

## Approval Audit Schema

```json
{
  "approval_id": "appr_xxx",
  "task_id": "task_xxx",
  "tool_call_id": "tool_xxx",
  "model_intent": "发送候选人评估邮件",
  "risk_reason": ["external_write", "pii_possible"],
  "proposed_args_redacted": {},
  "policy_decision": "require_approval",
  "final_decision": "approved|denied|expired",
  "approver": "user_or_admin",
  "timestamp": "ISO8601",
  "audit_ref": "audit_xxx"
}
```

## Current / Target 防线

- rootless container、gVisor、Firecracker、full credential broker 都是候选或 Target；只有实现和测试后才能写 Current。
- 输出 DLP 不等于安全完成；必须同时有输入、检索、工具、输出四道 gate。
- 本地模型只改善数据驻留，不自动解决 prompt injection、越权工具和 secret 泄露。

## 验收

- 安全不是输出端单点检测，而是贯穿输入、检索、工具和输出。
- 邮件、SSH、CLI、删除/覆盖、外部写操作默认高风险。
- 原始 secrets 不进入 prompt、trace、artifact 或 sandbox 文件系统。
- 任意检索结果、附件和外部网页都被视为不可信输入，不能直接提升为系统指令。
- 每次高风险动作都有 policy decision、approval state、actor、target、result 和 audit id。
- 本地模型只代表数据驻留边界，不替代 sandbox 和 approval。
- approval escape count 必须为 0；否则本 phase 不可关闭。

## 验证

```powershell
pytest -q tests/security tests/tools tests/agent/test_capability_system.py -p no:cacheprovider
```
