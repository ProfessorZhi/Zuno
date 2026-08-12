# Verification Fixtures

本目录不保存产品数据。Q005/Q053/Q097 的 model spike 和 Q063/Q064 的 loopback provider
emulator 定义在 `tests/architecture/test_p0_v4_execution.py`，只用于本轮可复现验证。

边界说明：

- Q063/Q064 的 HTTP provider 是 `127.0.0.1` 进程内 emulator，不是真实第三方 Provider；
- Q005/Q053/Q097 的模型不是 Current Domain/Plan/Recovery implementation；
- Q039 fixture 只验证当前 synthesis contract，不代表法院数据集；
- 没有将任何 fixture 写入生产数据库、Migration 或 Runtime。
