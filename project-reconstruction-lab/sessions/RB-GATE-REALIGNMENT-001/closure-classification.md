# Closure Class Classification

## 定义

Closure Class 与 `P0/P1/P2/P3` 正交，只表示一个问题当前阻塞哪一个 Gate：

| Class | 名称 | 阻塞 |
|---|---|---|
| `A` | `ARCHITECTURE_BLOCKING` | User Architecture Gate |
| `I` | `IMPLEMENTATION_BLOCKING` | Implementation Complete / I-P0 Closure |
| `E` | `EVIDENCE_MEASUREMENT_BLOCKING` | `MEASURED` / Quality Proven |
| `X` | `EXTERNAL_QUALIFICATION_BLOCKING` | Security Qualification / Production / External Validation |

## 12 个原始 P0 的分类

Q039 按既有 Scope Split 展开为两个派生 Closure Record；原始 Q039 不删除。

| Original / Derived | Severity | Closure Class | Design Decision Complete? | Target Contract Complete? | Current Implementation Available? | V4 Evidence Available? | V5 Evidence Required? | External Environment Required? | Blocks User Architecture Gate? | Blocks Implementation Completion? | Blocks Measurement? | Blocks Production? | 依据 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q005 | P0 | P0-I | YES | YES | NO | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | V4 spike 明确不是 Current Domain persistence |
| Q016 | P0 | P0-I | YES | YES | PARTIAL | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | 只有 Runtime restart，缺 Domain/Effect 对账 |
| Q033 | P0 | P0-I | YES | YES | PARTIAL | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | 当前只证明无 Approval 的 gate |
| Q039-C | P0 | P0-I | YES | YES | PARTIAL | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | wrong-span XFAIL 暴露 Citation provenance 实现缺口 |
| Q039-B | P0 | P0-E | YES | YES（Benchmark Contract） | NO | N/A | YES | NO | NO | NOT_BLOCKED | BLOCKED | BLOCKED | Court QA / A-B-C / 指标尚未执行 |
| Q053 | P0 | P0-I | YES | YES | NO | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | V4 model spike 不是 Plan/Domain 联合写回 |
| Q061 | P0 | P0-I | YES | YES | PARTIAL | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | execute-time revoke integration 未执行 |
| Q063 | P0 | P0-I | YES | YES | NO | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | loopback emulator 未接入当前 Gateway/Provider receipt |
| Q064 | P0 | P0-I | YES | YES | NO | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | loopback reconcile 未接入当前 Gateway/Provider |
| Q066 | P0 | P0-X | YES | YES | NO | NO | NO | YES | NO | NOT_BLOCKED | NOT_BLOCKED | BLOCKED | Docker/Deno 不可用，真实 Sandbox 资格测试未执行 |
| Q067 | P0 | P0-I | YES | YES | PARTIAL | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | 只有 untrusted flow 窄路径，缺 Agent→Tool 集成 |
| Q070 | P0 | P0-I | YES | YES | PARTIAL | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | 只有 read-only correlation，缺 EffectReceipt 全链路 |
| Q097 | P0 | P0-I | YES | YES | NO | NO | NO | NO | NO | BLOCKED | NOT_BLOCKED | BLOCKED | recovery model 不是四方 Current state store |

## 计数

```text
Original P0: 12
Derived closure records: 13
A-P0: 0
I-P0: 11
E-P0: 1
X-P0: 1
Original P0 closed: 0 / 12
```

## 判断边界

- `P0-I` 不是“已经实现”，而是“设计已可描述，当前实现不足以取得 V4 closure-grade evidence”。
- `P0-E` 不是“效果差”，而是“效果尚未有合格 Benchmark 证明”。
- `P0-X` 不是“Sandbox 设计错误”，而是“当前外部执行资格不足”。
- 本表不产生 `ACCEPTED_TARGET`；它只为 User Gate 提供可审计输入。
