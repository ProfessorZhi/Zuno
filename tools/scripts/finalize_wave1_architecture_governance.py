from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "docs/governance/wave1-cross-module-contract-registry.md"

FINAL_TAIL = """## 14. Wave 1 合并审计清单

```text
[x] Wave 1 基线 main SHA 已确认为 849820d2c52d36abebee8c3d4a974bf035524e0a
[x] PR #19 Security 已合并
[x] PR #18 Model Gateway 已合并
[x] PR #17 Infrastructure / shared contracts 已合并
[x] PR #21 Observability & Eval 已合并
[x] Contract 名称、字段、Enum、Hash 和版本由 ADR 0003 与本 Registry 冻结
[x] Security Epoch / Secret / Credential Ownership 对齐
[x] AuditEvent / TelemetryEnvelope / Mandatory Audit 对齐
[x] UsageReceipt / QuotaReservation / CancellationReceipt 对齐
[x] Index Batch / Receipt / Manifest / Cutover / Watermark 对齐
[x] ActionProposal / ActionExecutionBinding / PreparedToolAction / EffectReceipt Owner 已去重
[x] Failure Code Prefix 和共享 Code 去重
[x] Retry / Replan / Fallback / Reconcile / Recovery Owner 去重
[x] Infrastructure 物理目录冻结到 src/backend/zuno/platform/**
[x] 正式文档、模块入口、Agent 镜像和 focused validation 已同步
[x] 未把 Target 写成 Current、implementation available 或 production ready
[ ] Tool Runtime 正式模块采用 PreparedToolAction Contract
[ ] Runtime 实现、Migration 和工程证据完成
[ ] Integration / Fault / E2E / Trace / Eval 和运行证据完成
```

## 15. 当前结论

```text
design available
status = CONFIRMED_TARGET
implementation not established
measurement blocked
quality not yet proven
production ready not established
```

本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`。它是后续模块设计和 Codex 实现的正式 Target 事实源，但仍不是 Runtime Current、实现证据或生产可用声明。
"""


def main() -> None:
    text = REGISTRY.read_text(encoding="utf-8")
    updated, count = re.subn(r"## 14\..*\Z", FINAL_TAIL, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"expected one Wave 1 audit tail, got {count}")
    REGISTRY.write_text(updated.rstrip() + "\n", encoding="utf-8", newline="\n")
    print("Wave 1 Registry final audit state normalized.")


if __name__ == "__main__":
    main()
