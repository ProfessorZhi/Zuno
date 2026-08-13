# Human Writing Audit

## Deterministic signal boundary

`tools/scripts/verify_human_writing_v312.py` 只产生 warning。它不输出 Human Writing PASS；人工结论
由 Blue self-review、Red documentation review 和 ChatGPT review 共同完成。

| Canonical Doc | Template Phrase Density | Heading Density | English Density | Scenario | Failure Story | Tradeoff | Narrative Result | Rewrite |
|---|---|---|---|---|---|---|---|---|
| architecture.md | low | moderate | high | strong | strong | strong | CLEAR / DENSE | SECTION |
| product-architecture.md | low | moderate | moderate | strong | strong | strong | CLEAR | FULL_PART |
| legal-domain-model.md | low | moderate | high | strong | strong | strong | CLEAR / DENSE | NO |
| domain-state-lifecycle.md | low | moderate | high | strong | strong | strong | CLEAR / DENSE | NO |
| agent-platform.md | low | moderate | high | strong | strong | strong | CLEAR / DENSE | NO |
| multi-agent-runtime.md | low after rewrite | moderate | high | strong | strong | strong | CLEAR | FULL_PART |
| knowledge-evidence-architecture.md | moderate | moderate | high | strong | strong | strong | DENSE | NO |
| service-architecture.md | low after rewrite | moderate | moderate | strong | strong | strong | CLEAR | FULL_PART |
| data-ownership-and-recovery.md | low | moderate | moderate | strong | strong | strong | CLEAR / DENSE | NO |
| security-architecture.md | low | moderate | moderate | strong | strong | strong | CLEAR | NO |
| legal-eval-and-benchmark.md | low after rewrite | moderate | high | strong | strong | strong | CLEAR | FULL_PART |
| microservice-deployment.md | low after rewrite | moderate | high | strong | strong | strong | CLEAR | FULL_PART |

## Human review result

- Overall: `WARNING`
- Most natural: Product、Multi-Agent、Service、Deployment、Eval after rewrite。
- Most template-like before rewrite: Product、Multi-Agent、Service、Deployment、Eval。
- English-density concern: Architecture、Domain、Knowledge、Agent、Eval、Deployment remain dense；Part B precision justifies technical terms, but Part A should be reread by a human reviewer。
- Weak scenario risk: no structural failure remains；real-world user validation is still absent。
- Weak failure-story risk: all Part A sections contain a failure path, but no claim that the scenario happened historically。
- Part A regressions: none detected by structural verifier。
- Part B regressions: none detected by existing normalization and deep-dive verifiers。
- Human Writing Gate: `WARNING`, not automatic PASS。
