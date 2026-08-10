# API 层边界

## 当前角色

`src/backend/zuno/api/` 是 HTTP、DTO、认证、response envelope、SSE 和 application owner 的公开边界。

Product API 的提交、action、agent studio 和 projection 入口进入明确的 application service；文件与 ingestion 进入 `ProductIngestionService`，检索观测进入 `ProductObservabilityService`。API 不直接拥有 Agent loop、retrieval、memory 或数据库 schema。

## 规则

- route 只负责输入校验、身份提取、调用 owner 和响应映射。
- DTO 是公开传输契约；前端不得依赖内部 service 或数据库对象。
- 新的业务行为必须先确定 application owner，再增加 route。
- 失败必须保留安全拒绝、持久化失败、幂等冲突和租户隔离语义。

## 验证入口

- `tests/api/`
- `tests/frontend/test_product_runtime_contracts.py`
- `python tools/scripts/verify_docs_entrypoints.py`
