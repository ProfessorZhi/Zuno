# PHASE04：后端六层 facade 分层

## 目标

先建立新分层 facade，不大搬旧代码，不改 runtime 行为。

## 目标结构

```text
src/backend/zuno/
  api/
  agent/
  memory/
  capability/
  knowledge/
  platform/
```

## 策略

第一步只做 re-export facade：

```python
from zuno.services.retrieval.fusion import RetrievalFusion

__all__ = ["RetrievalFusion"]
```

这样让目录封面先和目标架构对齐，同时避免一次性物理迁移造成行为回归。

## 不做

- 不删除旧路径。
- 不改 public API。
- 不改数据库 schema。
- 不重写 GeneralAgent。
- 不重做 GraphRAG retrieval 逻辑。

## 验收

- 新 facade 可以 import。
- 旧 import 仍可用。
- 聚焦 import tests 和现有 runtime tests 通过。
- docs 明确 facade 是迁移过渡，不是永久 shim。
