# Platform Vendor 边界

`platform/vendor/` 是第三方库适配与隔离的唯一目录。这里可以保存第三方 API 的最小 shim、配置转换和 import guard，但不实现业务用例、Product API 或 Agent Runtime。

所有新代码必须直接使用本目录声明的 canonical import。供应商适配器必须保持输入、输出、异常和安全边界可测试；不得把第三方对象泄漏为业务层的隐式契约。

验证入口：`python tools/scripts/verify_repo_structure.py`。
