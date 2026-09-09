# Transcript — rb-2026-09-09-resume-claims-001

Mode: `CHATGPT_AUTO`  
Zuno base: `2dd908b7146f21b6be0e970ab4ef31f444920032`  
Resume: `ProfessorZhi/internship-work@382189e19b64ad2d691f67ca7f3906be039a96f5:resume/00_resume_versions/Zuno_v3+CodingAgent+SFTDPO_简历/当前简历文案_三项目版.md`

本记录保留 Red 问题、Blue closed-book 回答摘要、source trace 和 Verifier 结论。Red hidden intent 不进入长期 transcript。

## Turn 1 — Build / Buy + Personal Ownership

### Red

简历声称个人“设计工作区、Agent、知识库、Skill 和 Tool 等领域模型”，并继续写统一控制器、动态 GraphRAG、三层记忆、工具审批、幂等 / 中断恢复和固定评测。既然 Generic Host、LangGraph、RAG / Memory / MCP 平台已经能承担大量基础能力，为什么还需要自己做这些？这些能力具体哪些是本人设计和实现的？

### Blue

不能用“Dify / LangGraph 做不到”作为 Zuno 的理由。Canonical Project 把 Generic Host + 受控 RAG 视为简单任务的合理 baseline；UI、会话、通用工作流、模型调用、RAG 和 Tool Calling 等成熟能力应优先复用。Zuno 只有在长期法律工作出现材料就绪、Candidate → Formal Business Fact、历史成果失效、现实副作用结果未知、专业 Provider 资格与持续安全等问题时，才增加自己的语义边界。

个人 Ownership 也不能按简历当前强动词整体认领。Project History 明确说明项目在本人加入前已经存在；当前能够稳定确认的是部分 Agent 开发、Memory 第一批重要工作、OpenViking 接入、Tool Calling Strategy 以及数据库查看 / 调试等方向级参与。现有 Canonical sources 不足以证明完整 Runtime、GraphRAG、全部 RAG 或整个后端都是本人独立设计实现。

因此，如果面试官逐项追问统一控制器、三层记忆、GraphRAG 动态路由等是否由本人设计实现，Blue 只能对有任务级证据的部分作个人 Claim；其余需要降低到团队 / Target 设计，或继续恢复 PR、代码、Bug、测试与结果闭环。

### Source trace

- Resume snapshot：Zuno 条目中的“设计 / 实现”强 Claim。
- `docs/project/README.md`：Generic Host / RAG baseline、项目历史、团队与个人参与、Current / Target / Unknown。
- `docs/architecture/README.md`：复杂机制的条件性与 reuse-first 边界。
- `docs/evidence/README.md`：Target 不自动成为 Current Evidence。

### Verifier

Verdict: `UNSUPPORTED_CLAIM`  
Severity: `S0`  
Gap: `RESUME_CLAIM_RISK + OWNERSHIP_GAP + EVIDENCE_GAP`  
Next action: `CONTINUE_SAME_CHAIN`

新版 Human docs 能够阻止 Blue 为简历强 Claim 圆谎；问题落在 Resume / Ownership / Evidence，而不是 Narrative。

## Turn 2 — Project Identity / Historical Reality

### Red

简历把项目写成“企业知识库 Agent 平台”，项目简介强调企业内部知识问答、跨文档分析和受控任务执行；Canonical Project 却来自 LIPLAB 智慧司法、天津法院相关场景和法律专业工作。为什么面试官不应该判断这是为了投 AI Agent 岗而把一个法律项目重新包装成泛企业项目？

### Blue

当前资料不能证明“企业知识库 Agent 平台”是 Zuno 历史上正式存在过的另一个产品定位。Canonical Project 能证明的是 LIPLAB 智慧司法研究与工程化、天津法院智慧平台相关场景，以及研究成果进入长期法律工作的工程问题；同时 Canonical Project 明确禁止用今天的 Target Architecture 反写历史。

因此不能临时补充“后来泛化成企业平台”的故事。若历史上确实发生过产品泛化，需要恢复对应需求、产品文档、代码版本或其他历史 Evidence。没有这些证据时，Resume 的项目身份应与 Canonical Project Truth 对齐。

### Source trace

- Resume snapshot：项目名与项目简介使用“企业知识库 Agent 平台”。
- `docs/project/README.md`：智慧司法 / 天津法院相关背景、History / Target 分离、Pilot / Production 边界。
- `docs/governance/project-fact-provenance.md`：项目事实来源与 Claim 强度规则。

### Verifier

Verdict: `UNSUPPORTED_CLAIM`  
Severity: `S0`  
Gap: `RESUME_CLAIM_RISK + PROJECT_REALITY_GAP`  
Next action: `NEXT_ATTACK_ANGLE`

Blue 能正确拒绝编造产品泛化历史，因此 Canonical narrative 本身通过；Resume 项目身份需要独立修复或补历史证据。

## Turn 3 — Measurement / Current vs Target

### Red

简历写“建立 Trace、成本统计和固定评测链路，覆盖证据召回、完整证据链命中与无据拒答”。固定评测集多少条？证据召回和无据拒答指标是多少？GraphRAG 相比 BM25 / Vector 提升多少？如果没有结果数字，凭什么写“建立固定评测链路”？

### Blue

Current Evidence 不能提供这些质量数字。`docs/evidence/current-eval-baseline.md` 明确标记 `MEASUREMENT_BLOCKED`，正式 benchmark 当前没有可用外部实际数据，因此不能宣称质量或 Production Readiness 已通过。

能够证明的是评测执行路径和当前测试入口存在。`docs/evidence/current-test-baseline.md` 记录 canonical runtime / retrieval / evaluator checks，同时明确 `benchmark: BLOCKED_NOT_MEASURED`、`quality: NOT_YET_PROVEN`、`production_readiness: NOT_ESTABLISHED`。

所以“建立固定评测链路”如果只表示 evaluator / tooling / 固定执行入口，可以保留；但“覆盖证据召回、完整证据链命中与无据拒答”目前没有足够 Current Evidence 支撑为已经完成并验证的个人成果。GraphRAG 相比更简单 baseline 的收益也必须保持 Unknown / Blocked，等待正式 baseline / ablation。

### Source trace

- Resume snapshot：评测链路与覆盖范围 Claim。
- `docs/evidence/current-eval-baseline.md`：`MEASUREMENT_BLOCKED`。
- `docs/evidence/current-test-baseline.md`：selected canonical tests；benchmark / quality / production readiness 未建立。
- `docs/decisions/0006-evidence-driven-agentic-graphrag.md`：无据拒答和可测量路径属于 Target / Decision 语义，不能替代 Current measurement。

### Verifier

Verdict: `PARTIAL`  
Severity: `S1/S2`  
Gap: `EVIDENCE_GAP + MEASUREMENT_GAP + RESUME_CLAIM_RISK`  
Next action: `CLOSE_ROUND`

评测执行路径有 Current 支持，但 Resume 把“评测 plumbing 存在”写得接近“这些质量能力已经被覆盖验证”。继续追问只会重复同一 Evidence / Measurement 根因，Round 在此停止。
