# State Model

## Fact State

事实状态只描述历史、当前仓库或背景证据：

```text
USER_CONFIRMED
USER_PARTIAL_RECALL
ARTIFACT_EVIDENCE
PARTIAL_REPOSITORY_EVIDENCE
PUBLIC_CONTEXT
RECONSTRUCTED_CANDIDATE
CONTRADICTED
UNKNOWN
TARGET_ONLY
FUTURE
```

## Evidence Strength

Evidence Strength 与 Fact State 分开维护：

```text
E0  memory / inference only
E1  explicit user confirmation
E2  artifact corroboration
E3  repository / trace corroboration
E4  independent public corroboration
E5  reproducible engineering evidence
```

Strength 必须结合 Scope 解读。E4 只能证明公开来源范围，E5 只能证明可复现的 Current 或
Target 行为；它们都不能自动证明完整历史项目。每个重要 Claim 应关联 Evidence ID，不能
只写一个抽象等级。

## Architecture State

架构状态只描述设计审查生命周期，不能替代历史事实：

```text
PROPOSED
UNDER_ATTACK
SURVIVED
REJECTED
DEFERRED
ACCEPTED_TARGET
IMPLEMENTED
MEASURED
PRODUCTION_PROVEN
```

例如：

```text
Microservices = ACCEPTED_TARGET
Historical Project = UNKNOWN / NOT PROVEN
```

## Interview / Gap State

```text
OPEN
RESEARCHING
USER_CONFIRMATION_REQUIRED
BLUE_PROPOSED
ACCEPTED_FOR_FIX
FIX_IN_PROGRESS
RETEST_PENDING
CLOSED
DEFERRED
REJECTED
```

## State Transition Rules

1. 用户说“记得大概”只能进入 `USER_PARTIAL_RECALL`。
2. 模型推断只能进入 `RECONSTRUCTED_CANDIDATE`。
3. Blue 回答不会自动使 Architecture 进入 `SURVIVED`。
4. `SURVIVED` 必须经过 Counter Attack 和明确证据/决策。
5. `PRODUCTION_PROVEN` 必须有运行、客户或生产证据，不能由测试通过替代。
