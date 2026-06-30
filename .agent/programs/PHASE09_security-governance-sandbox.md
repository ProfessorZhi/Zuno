# PHASE09 Security Governance Sandbox

status: pending

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
- [ ] 写 prompt injection、data exfiltration、cross-workspace leakage 和 unauthorized tool call tests。

## 验收

- 安全不是输出端单点检测，而是贯穿输入、检索、工具和输出。
- 邮件、SSH、CLI、删除/覆盖、外部写操作默认高风险。
- 原始 secrets 不进入 prompt、trace、artifact 或 sandbox 文件系统。
- 任意检索结果、附件和外部网页都被视为不可信输入，不能直接提升为系统指令。
- 每次高风险动作都有 policy decision、approval state、actor、target、result 和 audit id。
- 本地模型只代表数据驻留边界，不替代 sandbox 和 approval。

## 验证

```powershell
pytest -q tests/security tests/tools tests/agent/test_capability_system.py -p no:cacheprovider
```
