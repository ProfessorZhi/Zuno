# Evidence Ledger

本表只记录证据索引，不把证据自动升级为事实。

| Evidence ID | Source Type | Source | Supported Claim | Scope | Confidence | Boundary |
|---|---|---|---|---|---|---|
| E-USER-001 | USER_MEMORY | 用户本轮确认 | 智慧法院项目组、Zuno 产品关系 | Historical | HIGH | 正式机构和合同主体 UNKNOWN |
| E-USER-002 | USER_MEMORY | 用户本轮确认 | 天津体系部分法院、法院侧测试、Pilot、未生产 | Historical | HIGH | 具体法院和部署证据 UNKNOWN |
| E-USER-003 | USER_MEMORY | 用户本轮确认 | 2026-03 加入、7–8 人、学硕学长带入 | Historical | HIGH | 详细团队 title UNKNOWN |
| E-USER-004 | USER_MEMORY | 用户本轮确认 | Agent、Memory、OpenViking、Tool Calling、数据库调试 | Personal | HIGH | 不等于完整 Owner |
| E-REPO-001 | REPO | `src/`、`infra/`、`tests/`、`pyproject.toml` | 当前 Python/Agent/Memory/Knowledge/Tool 与基础设施表面 | Current Repository | MEDIUM | 不代表完整历史 |
| E-REPO-002 | REPO | `infra/docker/docker-compose.yml` | 当前 Compose 服务表面 | Current Repository | MEDIUM | 不代表历史启动清单 |
| E-REPO-003 | REPO | `git log` 与当前文档 | 当前仓库阶段性架构和文档演进 | Current Repository | MEDIUM | 不代表横向项目最初状态 |
| E-PUBLIC-001 | PUBLIC_CONTEXT | 南京大学软件学院 / LIPLAB / 最高人民法院公开页面 | 天津智慧法院外围背景 | Public Context | HIGH | 不证明 Zuno 合同关系 |
| E-PUBLIC-002 | PUBLIC_CONTEXT | LawBench、LJPCheck、JIA、Fact–Article Correspondence、InternLM-Law primary sources；见 `sources/legal-ai-capability-matrix.md` | 法律能力分层、结构化中间任务、功能测试和人工/长文本评测可作为 Zuno Eval 设计输入 | Architecture Context | HIGH | 不证明 Zuno 已集成、质量优于竞品或 Native Runtime 有额外收益 |
| E-ARTIFACT-001 | ARTIFACT_EVIDENCE | 简历与附件候选稿 | 技术名词和个人叙事线索 | Historical Candidate | LOW/MEDIUM | 需逐项回忆或原始材料核验 |

新增证据必须带来源、Scope 和不能推出的内容。没有 Evidence ID 的重要 Claim 不得进入报告结论。
