# Platform Middleware 边界

`platform/middleware/` 承载 FastAPI startup 使用的 HTTP middleware。它处理 trace id、白名单状态和请求链横切行为，不拥有 route、DTO 或业务用例。

Middleware 变更必须保持 trace header、错误响应和 whitelist matching 的契约；业务拒绝应由对应 security/application owner 决定。
