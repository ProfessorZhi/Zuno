# PHASE04 从架构图反推执行计划

status: active

## 目标

根据细化架构图和 2026-06-30 架构深度评估，生成后续产品化执行顺序。PHASE04 不再继续扩展总览图，而是把 Zuno 主场景收束为“企业私有知识库与多功能 Agent 助手”，并把下一轮实现拆成四条可执行主线：文档摄取、Runtime + Memory + Tool Plane、Eval / Observability、安全与企业场景。同时新增总架构文档治理：文字总架构文档放在 `docs/architecture/overall-architecture.md`，Agent 侧维护镜像放在 `.agent/architecture/overall-architecture.md`。

## 范围

只写计划，不实施功能。

## 需要修改的文件

- `.agent/programs/implementation-roadmap.md`
- `docs/architecture/overall-architecture.md`
- `.agent/architecture/overall-architecture.md`
- `docs/architecture/product-scenario-enterprise-kb.md`
- `docs/architecture/security-and-sandbox.md`
- `docs/architecture/README.md`
- `docs/architecture/target-architecture.md`
- `docs/architecture/roadmap.md`
- `README.md`
- `.agent/references/docs-map.md`
- `.agent/references/architecture-docs-map.md`
- `.agent/references/documentation-governance.md`
- `.agent/references/architecture-update-policy.md`
- `.agent/references/workflow.md`
- `.agent/system.yaml`

## 禁止修改的文件

- `src/backend/zuno/**`
- `apps/web/**`
- DB schema 或依赖版本。

## 验收闸门

- 执行顺序明确写成 `architecture detail -> Document Ingestion / Parse Gateway -> Runtime + Memory + Tool Plane -> Eval / Observability -> Security + Enterprise Scenarios -> frontend trace/artifact product loop`。
- `Document Ingestion` 必须包括多格式解析、Canonical Document IR、chunk/provenance、BM25/vector/graph indexing 和 parser contract tests。
- `Runtime + Memory + Tool Plane` 必须包括 Context Pack、summary compression、structured extraction、ToolCard manifest、executor registry 和 approval flow。
- `Eval / Observability` 必须包括 LangSmith trace mapping、dataset versioning、RAGAS / DeepEval 指标、citation coverage、faithfulness、context recall 和 CI regression gate。
- `Security + Enterprise Scenarios` 必须包括 PII / 商业秘密脱敏、prompt injection 防护、ACL、输出 DLP、Policy / Workspace / Execution / Network-Credential Sandbox、高风险工具人工审批，以及企业知识库 / HR 简历库场景。
- README 只给精简入口，不堆完整执行细节。
- roadmap 明确当前 program active，且不把后续实现写成 Current。
- 总架构文档必须说明当前事实、目标分层、主链路、文档解析、安全评测和实施落点。
- `docs/architecture/overall-architecture.md` 与 `.agent/architecture/overall-architecture.md` 必须登记为同步维护面；`docs/architecture/architecture.html` 仍由 `docs/architecture/architecture.md` 生成，不复制到 `.agent/architecture/`。

## 后续 Program 切分建议

1. `zuno-document-ingestion-v1`
   - 目标：统一多格式文档解析与知识构建输入。
   - 边界：新增 parser gateway、Canonical Document IR、chunk/provenance 和 indexing contract；不先做前端产品闭环。
2. `zuno-runtime-memory-tool-plane-v1`
   - 目标：把 Context Builder、memory write-manage-read 和 Tool Control Plane 从 Target contract 推进到可运行 runtime。
   - 边界：只做单控制器 runtime 的可恢复循环和工具审批，不改成产品级多 Agent。
3. `zuno-eval-observability-v1`
   - 目标：把本地 trace/eval foundation 映射到 LangSmith / dataset / evaluator / regression gate。
   - 边界：保留本地 pytest/eval runner 作为 release gate，不把第三方平台作为唯一真相。
4. `zuno-security-enterprise-scenarios-v1`
   - 目标：围绕企业知识库和 HR 简历库建立输入、检索、工具、输出四道安全闸门。
   - 边界：邮件发送、SSH、外部写操作默认 human approval；成熟 OS sandbox、credential broker、完整 DLP 和多租户隔离仍是 Target / Future，不能写成 Current。

## 验证命令

```powershell
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_docs_entrypoints.py
```

## 需要返回的证据

- program roadmap summary
- formal roadmap active state

## 历史影响

本阶段不移动历史材料。
