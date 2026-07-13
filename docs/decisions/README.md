# 架构决策记录

这里只保留仍然影响当前主线的正式 ADR。

当前有效决策：

- [ADR 0002：退休 compat namespace](0002-retire-compat-namespace.md)

正式 Target 决议：

- [ADR 0003：Wave 1 跨模块 Contract 与 Infrastructure 物理边界冻结](0003-wave1-cross-module-contract-freeze.md)
  - 当前状态：`accepted-target`；已合并到 `main`，是正式共享 Target Contract，但不是 Current 或实现证据。
  - 冻结范围：服务端权威产品边界、`zuno/platform/**` 物理 Ownership、共享 Envelope、Security Epoch、Secret/Credential、Audit、Model Gateway、派生索引、PreparedToolAction、Failure Code 与 Retry/Recovery Owner。

已被替换的决策归档在：

- `docs/history/decisions/`

新增 ADR 时优先记录：

- 会长期影响 runtime 边界的决策。
- 会长期影响 retrieval / evidence contract 的决策。
- 会影响目录结构、服务边界或公开 API 的决策。
