# 安全与沙箱目标架构

## 定位

Zuno 的安全目标不是把整个后端都叫做“沙箱”，而是按风险边界分层隔离：主服务负责控制、鉴权、路由和 trace；不可信输入处理和高风险工具执行进入明确的策略、工作区、执行和网络/凭证边界。

核心原则：

```text
本地模型解决数据出域问题；
安全闸门、审批和沙箱解决 Agent 乱动手问题。
```

当前 Zuno 不能声称已经有成熟沙箱系统。成熟沙箱是 Target / Future，而不是 Current。

## 风险分层

| 层级 | 示例 | 默认策略 |
| --- | --- | --- |
| read_only | RAG 检索、GraphRAG 查询、读取知识库、读取允许范围内文件 | 可自动执行，但必须有 scope / ACL / trace。 |
| medium | 写临时报告、生成草稿、更新本地索引、生成 artifact | 策略控制、workspace 限制、trace 必须开启。 |
| high | 发邮件、写文件、执行 CLI、调用本地 MCP、SSH、外部写 API | 必须 approval + sandbox + audit。 |
| critical | 删除数据、修改权限、远程部署、批量外发 | 默认禁止，或需要更高级审批。 |

## 四层沙箱目标

### 1. Policy Sandbox

Policy Sandbox 是工具调用前的治理层，不是 OS 隔离。它先回答“能不能调用、要不要审批、预算多少、结果如何审计”。

```text
Agent tool proposal
  -> ToolCard / Manifest
  -> risk classification
  -> permission check
  -> approval policy
  -> budget / timeout
  -> audit event
```

ToolCard / manifest 至少需要描述：

- risk level。
- side effect level。
- required permissions。
- approval required。
- sandbox required。
- filesystem policy。
- network policy。
- credential policy。
- audit required。

### 2. Workspace Sandbox

Workspace Sandbox 限制文件读写范围：

```text
workspace_root/
  readonly_sources/
  writable_artifacts/
  temp/
  quarantine/
```

目标规则：

- 企业知识库原始文件默认只读。
- 用户上传文件先进入 quarantine。
- Agent 生成结果只能写入 writable artifacts。
- 中间文件只能写入 temp。
- `.env`、密钥、SSH key、系统目录和未授权项目目录默认不可读。
- 代码修改必须走 patch / diff，不允许任意写整个文件系统。

### 3. Execution Sandbox

Execution Sandbox 隔离高风险执行：

- PDF / DOCX / PPTX / 图片 OCR 解析。
- 不可信文件转换。
- 代码执行。
- 本地 CLI。
- MCP local server。
- SSH wrapper。
- 爬虫或浏览器自动化。

目标执行器：

| Executor | 阶段 | 目标能力 |
| --- | --- | --- |
| `ProcessExecutor` | Target | 最小 allowlist 命令、cwd 限制、timeout、stdout/stderr 截断和审计。 |
| `DockerExecutor` | Target+ | 容器隔离、只挂载允许目录、资源限制、默认禁网。 |
| `RootlessDockerProfile` | Future | 非 root daemon / user namespace / seccomp / AppArmor profile。 |
| `MicroVMExecutor` | Future | 用 microVM 作为更强信任边界，适合不可信代码和多租户。 |
| `RemoteSandboxExecutor` | Future | 企业远程隔离执行，适合高安全部署。 |

### 4. Network / Credential Sandbox

网络和凭证沙箱防止企业资料外泄：

- 网络默认 deny。
- 只允许访问 allowlist 域名。
- 禁止访问 localhost、内网 IP、metadata endpoint。
- HTTP/HTTPS 通过受控代理出站。
- 凭证由 host-side credential broker 注入。
- raw secret 不进入 prompt，也不进入 sandbox filesystem。
- stdout、stderr、tool result 和 artifact metadata 必须做 secret redaction。

## 企业知识库场景的沙箱矩阵

| 模块 | 是否必须沙箱 | 治理重点 |
| --- | --- | --- |
| 普通 RAG 检索 | 不一定 OS 沙箱 | 只读、租户/项目 scope、ACL、trace。 |
| GraphRAG 查询 | 不一定 OS 沙箱 | 只读、community report / graph scope、citation policy。 |
| PDF / DOCX / PPTX 解析 | 建议必须 | parser 隔离、资源限制、恶意文件隔离、parse trace。 |
| 图片 OCR / 多模态解析 | 建议必须 | OCR confidence、隐藏指令标记、资源限制。 |
| 代码执行 | 必须 | allowlist、文件/网络/资源隔离、审计。 |
| CLI 工具 | 必须 | 命令白名单、shell injection 防护、cwd/env 限制。 |
| MCP local server | 必须 | server trust profile、启动命令显式确认、文件/网络最小权限。 |
| MCP remote server | 不一定 OS 沙箱 | auth/audience、tool allowlist、SSRF 和 token 风险控制。 |
| SSH | 必须强审批 | host/user allowlist、non-root、timeout、audit trace。 |
| 邮件发送 | 不一定 OS 沙箱 | 默认草稿；外发必须 approval、DLP、recipient check。 |
| 文件写入/删除 | 必须策略隔离 | writable artifact scope、危险动作审批、diff/audit。 |

## 安全控制链路

```text
User Request
  -> Input Guard
  -> Context / Retrieval ACL
  -> Tool Policy / Approval Gate
  -> Sandbox Executor
  -> Result Normalizer
  -> Output DLP / Citation Check
  -> Trace / Audit / Eval
```

输入、检索、工具和输出都必须有安全闸门。输出检查不能替代检索前 ACL，也不能替代工具前审批。

## Current / Target / Future

### Current

当前 Zuno 已有：

- ToolCard / MCP policy foundation。
- Hook / Evidence / Trace foundation。
- Capability selection trace bridge。
- Security / observability platform thin surfaces。
- 文档中对 `Security / Policy`、`Tool Policy Approval`、`Sandbox / Budget / Timeout` 的目标表达。

这些不是成熟 sandbox runtime。

### Target

下一阶段目标：

- Policy Sandbox。
- Tool risk classification。
- Human approval / interrupt / audit trace。
- Workspace sandbox。
- Local `SandboxExecutor`。
- Document parser sandbox。
- PII / 商业秘密脱敏。
- Prompt injection 防护。
- Output DLP 和 citation coverage gate。

### Future

长期方向：

- Rootless Docker / microVM sandbox。
- Network proxy 和 credential broker。
- 多租户隔离。
- 组织级工具策略中心。
- 安全红队样本集和在线安全监控。

## 不允许写成 Current

- 成熟 OS sandbox。
- Docker / microVM 执行沙箱。
- credential broker。
- 生产级 prompt injection 防护。
- 完整 DLP。
- 自动邮件外发安全闭环。
- 多租户隔离。

只有代码、测试、trace、eval 和 verifier 都证明后，才能把对应能力从 Target 移到 Current。
