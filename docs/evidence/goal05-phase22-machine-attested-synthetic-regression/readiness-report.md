# PHASE22 Machine-attested Synthetic Regression Readiness

status: BLOCKED_WITH_EXACT_GAPS
track: machine_attested_synthetic_regression
date: 2026-08-03

## 当前结论

本报告建立 Synthetic Regression Track 的当前事实边界和人工分工入口，不声明 track ready。

当前可证明事实：

- `origin/main`：`c9d099d64a1af28102231751ce55df8217173e89`
- PR #106：Open，head `95e17fc522591e7ee543b40b5b568d71963b6aa0`，GitHub checks passed
- Stacked branch：`codex/phase22-real-synthetic-benchmark-readiness`
- PHASE22：`in_progress`
- Program：`active`
- Production Readiness：not established
- Public Benchmark：`reviewer_approved_count=0`，`benchmark_eligible_count=0`

Synthetic Track 当前仍为 `BLOCKED_WITH_EXACT_GAPS`，原因是完整 80 case 独立推导、完整 Corpus 真实 Canonical Ingestion、三索引 Visibility Receipt、Snapshot Activation、同 Snapshot 四 Profile Runtime、Gold 隔离、非零阈值 Release Decision、Fault/Security/Resume/Idempotency 矩阵均未执行完成。

## 历史 PR 分类

本轮历史审查范围：PR #100、PR #104、PR #105。

| PR | 分类 | 结论 |
| --- | --- | --- |
| #100 | ACCEPT_AFTER_REWORK / DROP mixed | Corpus 和 80 case 资产可选择性参考；`ingest_and_run.py`、profile result、release decision、runtime ingestion 产物必须 DROP，因为使用 in-memory substring / expected answer 注入 / TCP probe 冒充 runtime。 |
| #104 | ACCEPT_AFTER_REWORK / SUPERSEDED_BY_MAIN mixed | Truth boundary、execution candidate gate、task prompt 思路可参考；已关闭未合并，不是 Current。PR #106 已正式吸收 synthetic invalidation guard 的核心边界。 |
| #105 | ACCEPT_AFTER_REWORK | `CanonicalIngestionSliceRuntime`、状态机测试、Package A upload helper 可逐文件审查后迁移；不得整体合并，且必须适配最新 main owner boundary。Alembic env import fix需重新验证是否仍必要。 |

## 当前 Blocker

- Dataset：没有当前分支内的 80/80 derivation validator 通过证据。
- Ingestion：没有完整 Corpus 走 Source Upload 到 Snapshot Activation 的真实 ID 链。
- Index：没有 ES/Milvus/Neo4j 三索引全量 visibility receipt。
- Embedding：没有 formal Embedding Gateway provider/model/dimension/config hash。
- Graph：缺最小 Neo4j Path Visibility Receipt Contract 的实现与 owner runtime 产出。
- Profiles：四 Profile 仍没有同 Snapshot、不同正式路径的 run ids。
- Evaluation：没有 Gold 与 Runtime 隔离证明，没有非零阈值下的 synthetic release decision。
- Fault：Fault/Security/Resume/Idempotency matrix 未执行。

## 人工分工入口

四张人工 Claude Code 任务卡已写入：

- `.agent/programs/thread-prompts/CC-A-phase22-dataset-corpus-derivation-validator.md`
- `.agent/programs/thread-prompts/CC-B-phase22-canonical-ingestion-three-indexes.md`
- `.agent/programs/thread-prompts/CC-C-phase22-four-profile-runtime-benchmark.md`
- `.agent/programs/thread-prompts/CC-D-phase22-integration-fault-security-evidence.md`

这些任务卡只是人工分派材料，不启动 Worker，不改变 Codex 当前工作流。

## 验证入口

```powershell
python tools/scripts/verify_phase22_synthetic_regression_track.py
```

该 verifier 只证明当前 blocked truth boundary 和任务卡完整性，不证明 Synthetic Track Ready。
