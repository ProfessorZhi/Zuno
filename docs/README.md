# Zuno 文档入口

`docs/` 按读者问题分配事实、证据、设计、决策、历史和治理。判断标准是“谁拥有这类
语义、谁能更新它”，不是文件原来放在哪里。

## 目录

```text
docs/
├─ facts/        已恢复且今天仍然有效的项目事实
├─ architecture/整体 Target Architecture 与跨层契约
├─ modules/     稳定后各责任域的详细设计，目前尚未冻结
├─ decisions/   仍然有效的架构决策（ADR）
├─ history/     已替代、已结束或只用于考古的材料（当前只保留 Red/Blue 历史入口）
├─ evidence/    支撑 Current 判断的可复现证据
└─ governance/  Owner、文档规则和工程治理
```

另外，[`terminology.md`](terminology.md) 是轻量术语表，不再单独设置 `reference/`；图片等附件放在所属文档目录下，不再设置独立 `assets/` 根目录。

## 首读路径

- [项目事实](facts/README.md)：按 [项目背景](facts/project-background.md) → [历史需求与流程](facts/requirements-and-workflows.md) → [开发演进](facts/development-and-evolution.md) → [团队 Ownership](facts/team-and-ownership.md) 阅读
- [总体架构](architecture/architecture.md)：回答系统为什么这样设计、跨层如何闭环
- [模块入口](modules/README.md)：回答模块文档何时建立以及如何服从总架构
- [有效决策](decisions/README.md)
- [可复现证据](evidence/README.md)
- [Red/Blue 历史归档](history/README.md)
- [治理规则](governance/repo-ownership-matrix.md)

## 四条边界

```text
FACTS        今天理解 Zuno 必须相信什么
ARCHITECTURE 当前接受的 Target 设计为什么这样工作
MODULES      各责任域怎样工作（边界稳定后再展开）
HISTORY      以前发生过什么，但不再决定今天怎么设计
```

`evidence/` 和 `governance/` 是支撑层，不与项目知识争夺同一事实入口：前者证明 Current，
后者约束文档和工程协作。Target、目录、类名、Mock 或面试材料都不能反向证明 Current 或
Production。当前 `PRODUCTION_READINESS` 为 `NOT_ESTABLISHED`。

## 状态边界

```text
CURRENT     代码、Migration、Test、Trace、Eval 或真实运行证据已证明
TARGET      已接受的目标设计，不代表实现
HYPOTHESIS  等待 Benchmark、Spike、Security Evidence 或 User Validation
UNKNOWN     证据不足，必须保留未知
HISTORY     已结束、已替换或只用于回顾的材料
```
