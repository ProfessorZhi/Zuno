# Canonical Audit Before Rewrite

本表记录修改前目标文件的 SHA256 和本轮归一化范围。SHA256 是审计输入，不是 Git Commit SHA。

| Canonical Owner Doc | Before SHA256 | Structural finding | Rewrite mode |
|---|---|---|---|
| docs/project/architecture/architecture.md | 43B50D1D627F487FAEC7990361C891D6BA090EE2A693906A6411FB882D693EAE | Part B 后仍有产品、服务、运行时和状态正文 | FULL_PART_REWRITE |
| docs/project/product/product-architecture.md | 809F9DFEA5B62EBC350297DB868636BF5AF5065E1BC280A95E1680C11702BF0A | Scope/Flow/acceptance 内容悬浮在 Part B 后 | FULL_PART_REWRITE |
| docs/project/domain/legal-domain-model.md | 7E960CB8154B1CB77D757BAEE8F0A03EE697B40460F4BF04F7D05D6E0F9820DD | Definition/Provider/Mutation 内容混排 | FULL_PART_REWRITE |
| docs/project/domain/domain-state-lifecycle.md | BC950AF57556D197EE86F98AD96DC5779C53E2DCFCE2705DDC2425222A5096F4 | Version/Failure 内容继续出现在 Part B 后 | FULL_PART_REWRITE |
| docs/project/agents/agent-platform.md | 48EDA243C94FC84376CCB5A6C33947B74FD175E3B32BA8074D2F82974329C676 | Part-A execution model 位于 Part B 后 | FULL_PART_REWRITE |
| docs/project/agents/multi-agent-runtime.md | 9AFC7AF974876F08B92223DBE6CE9897BDA89CC64EC6D3E6F5DF01DA9C60C2D0 | Narrative 使用未定义 L5 | FULL_PART_REWRITE |
| docs/project/knowledge/knowledge-evidence-architecture.md | D63F345B68040C7E3F6F1DEF3654FC1272EEA6A38986DC04E7D42619BCCDE099 | Ingestion/Graph/Worker 内容混排 | FULL_PART_REWRITE |
| docs/project/services/service-architecture.md | E937F1AD332DD9F5292FAB906DB9CB0AB9C1EF54766F1B731BBA03B21C265872 | Service set/Contract 内容位于旧正文区 | FULL_PART_REWRITE |
| docs/project/data/data-ownership-and-recovery.md | E81219F6FFD060BF36C8CC9995DCD21E5382C08535631052990A19B47B3B6099 | Ownership/Store/Recovery 内容混排 | FULL_PART_REWRITE |
| docs/project/security/security-architecture.md | F01F2524C1EAD1A8C2174D56B0308DF3A435ABF17F7481081955768075BF98 | Threat 与 Effect Contract 需要清晰分割 | FULL_PART_REWRITE |
| docs/project/eval/legal-eval-and-benchmark.md | EEC6B3AA9149040CCABBD906703207FEEA0D6690405BA1F264BD592833C6E3FB | A/B/C、Metrics 和 L5 内容混排 | FULL_PART_REWRITE |
| docs/project/deployment/microservice-deployment.md | 9BCFF637B3F89C4616BEEF4AF0EF92DEE89A3A22ABC4B849BBDFD668FE5B62CD | Profiles/Scaling/Communication 位于旧正文区 | FULL_PART_REWRITE |

说明：上述结构发现来自本轮静态审计；不能推出历史项目曾按这些旧结构实现。
