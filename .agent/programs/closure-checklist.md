# Program Closure Checklist

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-unified-agent-runtime-closure-v1

## 最近完成 Program

- [x] PHASE01 baseline、truth source、PowerShell 命令和 sample case set 已冻结。
- [x] PHASE02-PHASE12 unified runtime implementation baseline 已完成并逐 phase 提交。
- [x] PHASE13 修复 profile 缺失仍标 measured 的 bug。
- [x] PHASE13 新增 profile case counts / hashes 和 `profile_completeness` diagnostics。
- [x] PHASE13 provider/runtime profile runner 不可用时输出 `blocked_not_measured`，不异常冒充 measured。
- [x] sample-8 runner 已执行并产出 blocked report。
- [x] sample-80 保持 blocked，因为没有 tracked fixed 80-case set。
- [x] production readiness 和 evidence 文档已记录 measurement blocked。
- [x] program 已归档到 `docs/history/programs/zuno-unified-agent-runtime-closure-v1/`。

## 未完成质量门

- [ ] fixed EnterpriseRAG paired benchmark 完整 measured pass。
- [ ] Evidence Text Available@5 >= 0.60。
- [ ] Source Doc Citation Accuracy >= 0.85。
- [ ] Citation Accuracy >= 0.30。
- [ ] Answer Correctness >= standard_rag。
- [ ] Agentic GraphRAG stable superiority over baseline。

## 禁止的虚假关闭

- contract test 通过不等于 runtime complete。
- deterministic fixture 通过不等于真实 provider complete。
- benchmark prepared 不等于 measured。
- partial profile output 不等于 fixed paired benchmark。
- doc-level citation 不等于 source-span strict citation。
- implementation closure 不等于 quality gate pass。
