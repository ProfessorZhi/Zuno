# Legacy Verifier Map

| 验证器族 | 作用 | 本轮处置 |
|---|---|---|
| `verify_red_blue_session.py` | 通用 Session 记录契约 | 保留，验证历史记录 |
| `verify_red_blue_round_v2.py` | V2 Round-001 格式 | 保留为历史回归 |
| `verify_red_blue_round_v3*.py` | V3/V3.1 Round 格式和评分 | 保留为历史回归 |
| `verify_red_blue_repair_v1.py` | Blue Repair | 保留为历史回归 |
| `verify_red_blue_evidence_closure_v1.py` | Evidence Closure | 保留为历史回归 |
| `verify_red_blue_p0_v4_execution_v1.py` | V4 verification-only evidence | 保留为历史回归 |
| `verify_closure_semantic_audit_v3131.py` | Closure derived audit | 保留为历史回归 |
| `verify_red_blue_workflow_v4*.py` | V4/V4.1/V4.2 Bootstrap/Session contract | 保留为历史回归，不代表 active |
| `verify_red_blue_round006_closure.py` | Round-006 aborted closure | 保留，immutable evidence 回归 |
| `verify_red_blue_reset.py` | 本次 RESET active boundary | 新增，唯一验证当前 reset 入口 |

历史验证器不得自动生成 Session、题集、Candidate 或修改 Canonical。V4.2 的 Batch/Live 规则
继续由归档文档和历史回归测试解释，不进入当前 active Protocol。
