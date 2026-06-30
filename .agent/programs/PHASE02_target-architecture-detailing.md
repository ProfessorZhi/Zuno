# PHASE02 目标架构细化

status: completed

## 目标

把 `Model / Agent Core Runtime / Memory / Tool / Knowledge / Document Ingestion / Security / Trace-Eval / Platform` 写入正式目标架构，解释 planning 与 runtime 的关系，并把 Memory Layer 细化为 write-manage-read 记忆机制，把 Tool Layer 细化为 manifest-driven Tool Control Plane。

## 范围

只修改正式 Target 文档，不把这些能力写成 Current。

## 需要修改的文件

- `docs/architecture/target-architecture.md`

## 禁止修改的文件

- `docs/architecture/current-architecture.md`，除非有代码和测试证明新的 Current 事实。
- `src/backend/zuno/**`
- API / DB / frontend runtime 文件。

## 验收闸门

- `Planning` 被写成 Agent Core Runtime 内部控制能力。
- `LangGraph` 被写成目标实现候选，不被写成“规划模块本身”。
- `Memory Layer` 被写成 Raw Event Log、L0 Working Context、L1 Recent Window、L2 Task Summary、L3 Structured Long-term Memory、L4 Graph Memory、read path、write path 和 memory eval 的目标契约。
- `Tool Layer` 被写成 Tool Manifest、ToolCard Registry、Capability Selector、Tool Policy / Approval Gate、Executor Adapter、Sandbox、Result Normalizer、Tool Trace / Audit 的目标契约。
- `Document Ingestion`、`Security / Policy`、`LangSmith trace / eval` 被写成 Target。
- Tool 层明确区分 capability type 与 execution mode。

## 验证命令

```powershell
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## 需要返回的证据

- target architecture updated sections
- Current / Target boundary check result

## 历史影响

本阶段不移动历史材料。
