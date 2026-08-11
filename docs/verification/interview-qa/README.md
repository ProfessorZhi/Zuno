# Zuno Architecture Red Team QA

本目录是 Zuno 的**架构红队模拟面试 QA**唯一维护入口。它不是面试 FAQ、背题题库，也不是第二套架构；它模拟面试官沿着一条机制不断深挖，检查读者能否只依赖正式架构文档回答：

```text
为什么这样设计
→ 输入和判断依据是什么
→ 正常流程怎样执行
→ 状态、版本和权限怎样变化
→ 失败、重试、恢复和对账怎样处理
→ 如何用 Test / Trace / Eval 证明
```

QA 是架构消费者。正式事实仍由 `docs/architecture/`、`docs/modules/`、`docs/decisions/` 和 `docs/governance/` 负责；QA 只能验证、压缩和引用这些事实，不能为了让答案完整而新增 Runtime 语义。

## 目录结构

```text
docs/verification/interview-qa/
├─ README.md                         # 本入口：范围、阅读顺序和维护规则
├─ question-taxonomy.md              # 深挖层级和主题地图
├─ source-audit.md                   # 面经来源、审计边界和来源分层
├─ architecture-coverage-matrix.md   # 每题到正式架构章节的覆盖矩阵
├─ architecture-gap-report.md        # 红队盲审发现的 Gap 与关闭状态
├─ zuno-agentic-graphrag-qa.md       # 03 Knowledge / Evidence
├─ zuno-tool-mcp-security-qa.md      # 07/08/09 Tool Governance
├─ zuno-memory-context-qa.md         # 05 Memory / Context
├─ zuno-memory-information-extraction-qa.md
├─ zuno-agent-core-qa.md              # 06 Planning / Control
└─ zuno-cross-module-system-design-qa.md
```

文件按主题分组，题目用稳定的 `Q001–Q267` 编号关联覆盖矩阵。不要再创建同一主题的 `*-final.md`、`*-deep-dive.md` 或聊天记录镜像；新增深挖应进入对应主题文件，并同步矩阵和验证器需要的元数据。

## Canonical Truth

正式事实源：`docs/architecture/`、`docs/modules/`、`docs/decisions/`、`docs/governance/`。

QA 与正式架构冲突时，正式架构优先。QA 中的 Expected Answer 只允许复述或压缩 canonical docs，不得创造新的 Runtime、Current、Benchmark 或 Production 事实。

本次双层文档重构只改变同一份 Markdown 的阅读入口，不改变架构语义、QA 题目或 Canonical Reference。人类问题优先由 Part A 回答，实现和审查问题继续落到 Part B；QA 仍然是消费者，不是第三套架构事实。

本轮架构文档写作重组保留了既有 canonical section anchors，以避免无语义变化的标题改名破坏外部引用；因此本轮 `section_ref` 更新数量为 `0`。若未来语义迁移导致 anchor 消失，必须先修复 canonical 文档，再更新覆盖矩阵和 QA metadata。

## 题库范围

当前冻结 Q001–Q267，分布为：

| Domain | 题数 |
| --- | ---: |
| Agentic GraphRAG / Evidence | 65 |
| Tool / MCP / Permission / Effect Safety | 58 |
| Memory & Context | 44 |
| Memory & Information Extraction | 35 |
| Agent Core / Planning & Control | 45 |
| Cross-module / System Design | 20 |
| 合计 | 267 |

每题标记 `source_type`：`REAL`（真实问题）、`DERIVED`（从真实问题合理延伸）、`ARCHITECTURE_STRESS`（根据 Zuno Target 设计构造）。红队题不能伪装成真实面经，Target 也不能伪装成 Current。

## 建议阅读顺序

### 第一层：先理解产品和主线

1. `docs/architecture/architecture.md` Part A；
2. `zuno-cross-module-system-design-qa.md`；
3. `question-taxonomy.md`，理解 L1–L8 的追问层级。

### 第二层：按四个面试主战场深挖

1. `zuno-agentic-graphrag-qa.md`：检索、证据、图关系、充分性和停止；
2. `zuno-tool-mcp-security-qa.md`：能力、工具、授权、审批、幂等和副作用；
3. `zuno-memory-context-qa.md` 与 `zuno-memory-information-extraction-qa.md`：记忆写入、冲突、召回和上下文治理；
4. `zuno-agent-core-qa.md`：任务理解、Plan、ReadySet、ReAct、Replan、恢复和 Final Gate。

每道题都应沿着 `30 秒回答 → 深挖回答 → 继续追问` 使用；如果回答只能停在名词或类名，说明应回到对应模块的 Part A，而不是继续增加题目数量。

## 红队维护协议

### 发现架构缺口时

```text
红队问题暴露语义缺口
        ↓
记录 Gap ID 和证据
        ↓
先修改正式架构 / 模块 Contract
        ↓
重新运行架构验证
        ↓
更新 QA 答案、引用和覆盖矩阵
```

QA 不得自行补齐 `Owner`、状态、Failure、Current、Benchmark 或 Production 事实。若正式架构尚未决定，答案必须明确标记 `ARCHITECTURE_SEMANTIC_GAP` 或保持 `Target / Future` 边界。

### 新增或修改题目

- 优先补充现有 Drill Chain，不为一个追问新建文件；
- 保留稳定 QID，除非题目语义已经被正式替代；
- 必须填写来源、主题、难度、正式架构引用、初始覆盖状态和 Gap ID；
- `REAL`、`DERIVED`、`ARCHITECTURE_STRESS` 必须如实区分；
- 题目答案只允许解释正式文档，不能把 Mock、类名、目录或目标文档写成 Current 证据；
- 修改 Part B 的 Contract 后，必须重新检查相关 QA，而不是只改 Expected Answer。

### 质量闸门

```powershell
python tools/scripts/verify_architecture_interview_qa.py
pytest -q tests/repo/test_architecture_interview_qa.py -p no:cacheprovider
python tools/scripts/verify_markdown_internal_links.py
```

Coverage `FULL` 只表示正式文档能够回答该题，不表示 Runtime 已实现、质量已经证明或系统已经达到生产就绪。Current 状态必须回到 `docs/status/production-readiness.md` 和 `docs/evidence/`。

## 三种使用模式

### 模式 A：候选人复习

随机打开一个 QID，先不看答案，只根据 canonical architecture 回答，再对照 30 秒回答、深挖回答和 Follow-up。

### 模式 B：Architecture Audit

只打开 docs/architecture/、对应 docs/modules/、docs/decisions/ 和 docs/governance/，检查能否独立回答；coverage_status=FULL 只代表文档覆盖，不代表 Runtime 已实现。

### 模式 C：未来代码审查

实现完成后，把每道题继续映射到 code、Migration、test、Trace 和 Eval，回答“设计在哪里被代码证明”。这不是本轮的完成条件。

## 覆盖闸门

Architecture Interview Coverage = PASS 仅表示：267/267 有 canonical references，267/267 final coverage=FULL，且没有 conflicting canonical definition 和 QA-only architecture fact。

本轮复核基线与结果：

| 阶段 | FULL | PARTIAL | MISSING | 说明 |
| --- | ---: | ---: | ---: | --- |
| 双层重构前 | 267 | 0 | 0 | 既有 QA metadata 的最终覆盖状态 |
| 双层重构后 | 267 | 0 | 0 | 保留稳定章节锚点后重新运行结构与引用校验 |

这不是 Runtime 质量证明；如果未来 Part A 暴露真正的架构 Gap，应记录到 Gap / ADR，而不是为了让 QA 变成 FULL 虚构实现证据。

它不表示 implementation available、quality proven 或 production ready。Current / Target / Future 状态仍以 docs/status/production-readiness.md 为准。

验证命令：

    python tools/scripts/verify_architecture_interview_qa.py
    pytest -q tests/repo/test_architecture_interview_qa.py -p no:cacheprovider
