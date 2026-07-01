# PHASE07 Security Governance Envelope

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE07_security-governance-envelope
status: active

## 目标

建立横切 Security / Governance envelope：Input Gate、Retrieval Gate、Tool Gate、Output Gate，覆盖 ACL、workspace isolation、prompt injection、DLP、tool approval、credential-ref-only 和 audit。

## 范围

- Input Gate：prompt injection、secret / PII signal、file safety metadata。
- Retrieval Gate：workspace ACL、document block ACL、index chunk ACL、sensitivity filter。
- Tool Gate：side effect、permission、approval、credential-ref-only、sandbox profile。
- Output Gate：citation coverage、unsupported claim、DLP / sensitive output safety。
- audit event / trace event contract。

## 目标架构拼接点

本 phase 拼到 Governance / Trace / Eval Envelope。安全不是单点过滤，而是横切所有层：

- Input Gate 保护 user message、file metadata 和 prompt injection。
- Retrieval Gate 必须在召回前按 workspace / ACL / sensitivity 过滤。
- Tool Gate 控制 side effect、approval、credential-ref-only 和 sandbox。
- Output Gate 检查 citation coverage、unsupported claim 和敏感输出。
- Audit / Trace 把每个 gate verdict 交给 Eval / Release Gate。

本 phase 的 verdict 被 PHASE09/PHASE10 Planning Runtime 用来 stop、ask_user、replan、refuse 或 continue。

## 并行开发可行性

本 phase 由 Workstream E 推进，可以与 Capability、Knowledge、Planning 并行，但需要 gate contract 稳定。

可并行：

- Input / Retrieval / Tool / Output Gate tests 可拆开。
- Retrieval Gate 与 Workstream B 联调。
- Tool Gate 与 Workstream D 联调。

不可并行：

- 不得在检索后才做 ACL。
- 不得把 dangerous tool approval 写成 UI TODO。
- 不得让 security blocked 被 Planning 忽略。

## 详细执行卡

- 输入依赖：PHASE02 security policy contract、PHASE04 retrieval candidate fields、PHASE06 ToolCard side effect fields、现有 agent guardrails。
- 主要交付物：InputGate、RetrievalGate、ToolGate、OutputGate，ACL / sensitivity propagation，prompt injection handling，approval decision，citation safety verdict。
- 可并行工作包：input gate、retrieval ACL、tool approval、output citation/DLP 可拆；统一 SecurityDecision contract 只能单 owner 改。
- Coordinator 锁点：workspace isolation、credential-ref-only、dangerous tool approval、unsupported claim/citation failure 的默认行为。
- 下游交接：PHASE09 planner 读 allowed capabilities；PHASE10 replan 处理 security_blocked；PHASE12 E2E 覆盖 blocked path；PHASE13 记录 security_block_count。
- PR / commit 建议：`feat(security): add agent governance gates` 与 `test(security): cover acl prompt injection approval output gate`。

## 禁止范围

- 不在回答生成后才做权限过滤；必须检索前过滤。
- 不把 credential 原文写入业务事实或 trace。
- 不用 fake safety pass 掩盖 citation missing 或 unsupported claim。

## 验收闸门

- prompt injection 标记或隔离测试通过。
- cross-workspace retrieval blocked 测试通过。
- dangerous tool approval 测试通过。
- output citation coverage low 触发 rewrite / refuse / replan 的 contract 测试通过。

## 验证命令

```powershell
git diff --check
pytest -q tests/security -p no:cacheprovider
pytest -q tests/agent_system -p no:cacheprovider
pytest -q tests/agent -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/platform/security/**`
- `src/backend/zuno/capability/**`
- `src/backend/zuno/knowledge/**`
- `tests/security/**`
- `tests/agent_system/**`

## 需要修改的文件

- `src/backend/zuno/platform/security/**`
- `tests/security/**`
- `tests/agent_system/**`
- policy integration tests where gates are consumed

## 执行拆解

1. 写 Input Gate focused test。
2. 写 Retrieval Gate ACL / sensitivity focused test。
3. 写 Tool Gate approval / credential-ref-only focused test。
4. 写 Output Gate citation / unsupported claim focused test。
5. 实现 local deterministic gate baseline。
6. 确认 Planning phase 能看到 blocked reason。

## 多 agent 分工

- Workstream E owner。
- Workstream D 配合 Tool / Capability policy。
- Workstream B 配合 retrieval gate filter。
- Workstream F 消费 gate verdict，不直接绕过 gate。

## 需要返回的证据

- 四道 gate tests。
- policy verdict 示例。
- audit / trace 字段示例。
- blocked reason 示例。

## 停止条件

- retrieval gate 无法在检索前执行。
- tool gate 会泄露 credential 原文。
- output gate 会把低引用覆盖伪装成成功回答。
