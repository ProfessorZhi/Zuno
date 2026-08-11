# Technology Reality

本文件回答“项目实际使用了什么”，不把 Target Architecture 中的模型、服务或部署图自动当成历史事实。

## 模型与部署必须分开确认

```text
Business Need
  → Model Role / Candidate
  → Hosted API or Self-hosted
  → Prompt / RAG / Few-shot 是否足够
  → Fine-tuning 是否必要
  → Serving / Resource / Cost
  → Failure / Fallback / Eval
```

| Claim | 状态 | 说明 |
|---|---|---|
| 实际使用的模型 Provider / Model Version | `[UNKNOWN]` | 需要配置、调用记录、代码或用户确认 |
| 使用 Hosted API 还是 Self-hosted | `[UNKNOWN]` | “使用 DeepSeek”等名称不能自动推出私有部署 |
| 如果 Self-hosted，权重、推理 Runtime、GPU 和 Endpoint | `[UNKNOWN]` | 需要部署和运维证据 |
| 是否 Fine-tuning | `[UNKNOWN]` | 先证明 Prompt / RAG / Few-shot 不足，再讨论训练 |
| 训练数据、权限、Train/Validation/Test 隔离 | `[UNKNOWN]` | 需要 Dataset、实验和治理证据 |
| API / Model Gateway 当前实现 | `[REPO_EVIDENCE]` 或 `[UNKNOWN]` | 以模块文档、代码和运行证据交叉确认 |
| 目标模型路由、Serving 和回滚 | `[TARGET_ACCEPTED]` 或 `[BLUE_PROPOSAL]` | 不能冒充历史部署 |
| 当前后端语言与 API 入口 | `[REPO_EVIDENCE]` | `pyproject.toml` 为 Python 3.12，Docker 使用 Python 3.12，`zuno.main:app` 为 FastAPI 入口 |
| 当前是否存在 Java / Spring 后端 | `[UNKNOWN]`（仓库内无匹配证据） | 只能说明当前仓库没有 Java/Spring 文件或配置匹配，不能推断外部系统 |
| 当前是否已经是真微服务部署 | `[REPO_EVIDENCE]` + `[UNKNOWN]` | Compose 有 backend、worker、frontend 应用容器和基础设施；没有独立 Domain/Runtime/Knowledge/Tool 服务的生产证据 |

## 本轮事实 Gate 的明确保留项

以下信息仍然是 `[UNKNOWN]`，不能写入 Resume Current Claim，也不能由 Target Architecture 推导：

```text
实际 DeepSeek 使用
Hosted / Self-hosted
GPU 与 Model Serving
Fine-tuning / DPO
训练数据与实验结果
真实模型 Provider、Version、Quota、Cost 和运行 Trace
```

后续如果需要把某个模型或训练方案从 Candidate 推进到 Target，必须经过 Prompt / Structured Output / RAG / Few-shot / Routing 的对照，以及 10 Observability & Eval 的可复现 Release Gate。

Hosted API 主要需要证明 Provider/API Contract、数据出境、Quota、Fallback、版本和成本；Self-hosted 才需要进一步证明 Model Artifact、Inference Runtime、GPU、Health、Scaling、Version 和 Rollback。

## 其他技术事实

RAG、Memory、Agent、Tool、MQ、DB、GPU 和部署的实际使用情况，都必须区分：个人工作、团队工作、框架提供、外部团队工作和目标设计。目标架构进入 [`../architecture/`](../architecture/README.md) 与专题目录；实际证据进入 [`../../evidence/`](../../evidence/README.md)。
