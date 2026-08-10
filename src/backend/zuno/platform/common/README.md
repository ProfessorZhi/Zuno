# Platform Common 边界

`platform/common/` 只承载跨模块、无业务 owner 的纯函数和基础类型，例如文件路径、hash、日期、模型输出和观测辅助函数。

新业务逻辑必须进入明确的 Agent、Capability、Knowledge、Memory 或 application owner。保留在 common 的 helper 要有清晰输入输出和针对性测试，不得形成隐式 service facade。
