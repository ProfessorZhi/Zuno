# PHASE09 Security Governance Sandbox

status: pending

## 目标

把企业私有知识库场景的安全治理前置为系统架构：输入、检索、工具、输出四道闸，配合 policy、workspace、execution、network/credential sandbox。

## 步骤

- [ ] 建立 input gate：auth、rate limit、file validation、PII/business secret scan、prompt injection scan。
- [ ] 建立 retrieval gate：chunk ACL、workspace scope、document trust label、retrieval result sanitization。
- [ ] 建立 tool gate：side effect policy、approval、timeout、cwd/network/credential allowlist。
- [ ] 建立 output gate：DLP、citation coverage、format validation、redaction。
- [ ] 写 prompt injection、data exfiltration、cross-workspace leakage 和 unauthorized tool call tests。

## 验收

- 安全不是输出端单点检测，而是贯穿输入、检索、工具和输出。
- 邮件、SSH、CLI、删除/覆盖、外部写操作默认高风险。
- 本地模型只代表数据驻留边界，不替代 sandbox 和 approval。

## 验证

```powershell
pytest -q tests/security tests/tools tests/agent/test_capability_system.py -p no:cacheprovider
```
