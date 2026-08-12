# Evidence Rules

## 证据优先级

```text
用户真实确认 / 原始 Artifact
  > 当前或历史仓库可复核证据
  > 官方公开背景
  > 多线索重建候选
  > 单一模型推断
```

优先级不允许跨层偷换。例如官方学校页面可以证明学校背景，但不能证明 Zuno 的合同客户。

## Evidence Record

每条重要证据必须尽量记录：

```yaml
evidence_id: E-YYYY-NNN
source_type: USER_MEMORY | REPO | ARTIFACT | PUBLIC_CONTEXT | SESSION
source: 可定位的文件、URL、提交或用户原话
observed_at: 访问/记录时间
claim_supported: 支持的具体 Claim
scope: 历史 | 当前仓库 | Target | 外围背景
confidence: HIGH | MEDIUM | LOW
contradictions: []
notes: 边界和不能推出的内容
```

## 反向约束

- 当前 GitHub 只能标 `PARTIAL_REPOSITORY_EVIDENCE`，除非存在直接历史 Artifact。
- 目录、类名、依赖、Compose 和 Mock Test 只能证明存在表面。
- “用户参与”必须有用户确认或个人 Artifact；团队代码不能自动归因给用户。
- “已部署/已生产/质量提升”需要环境、运行、客户或指标证据。
- 一条证据支持不了更强的 Claim 时，缩小 Claim，而不是提高证据等级。
