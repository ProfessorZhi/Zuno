from pathlib import Path

# One-time PR reconciliation helper; removed after the branch absorbs latest main.
ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs/modules/README.md"
AGENT = ROOT / ".agent/modules/README.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def main() -> None:
    docs = DOCS.read_text(encoding="utf-8")
    docs = docs.replace(
        "| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) | 已建立 Target 规范 |",
        "| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md)；[`RAG Core Five / Agentic GraphRAG / Agent Efficiency 附录`](./10-observability-eval-rag-agent-evaluation.md) | 已建立实施级 Target 规范 |",
    )
    section = '''## Observability & Eval 文档边界

正式 Target 主文档与受控附录：

```text
docs/modules/10-observability-eval.md
.agent/modules/10-observability-eval.md

docs/modules/10-observability-eval-rag-agent-evaluation.md
.agent/modules/10-observability-eval-rag-agent-evaluation.md
```

主文档定义 Trace、Audit、Metric、Eval、Evidence、Release Gate、事件交付、恢复和质量证明边界；受控附录冻结 RAG Core Five、Agentic GraphRAG 全过程 Trace、Graph Failure Bucket 和 Agent Efficiency。旧 Retrieval、Citation、Safety 与 Runtime 指标保留为诊断层，不得冒充 Core Five。

Current 与质量状态仍以代码、运行证据、`docs/status/production-readiness.md` 和 `docs/evidence/` 为准。

专用验证：

```text
python tools/scripts/verify_observability_eval_target_protocols.py
pytest -q tests/repo/test_observability_eval_target_protocols.py -p no:cacheprovider
```

'''
    docs = replace_once(docs, "## Agent Core 文档边界\n", section + "## Agent Core 文档边界\n", "docs observability section")
    DOCS.write_text(docs, encoding="utf-8", newline="\n")

    agent = AGENT.read_text(encoding="utf-8")
    agent = agent.replace(
        "| 10 | Observability & Eval | [`10-observability-eval.md`](../../docs/modules/10-observability-eval.md) | 已建立 Target 规范 |",
        "| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) + [`10-observability-eval-rag-agent-evaluation.md`](./10-observability-eval-rag-agent-evaluation.md) | 主 Target 与 RAG/Agent Eval 受控附录镜像 |",
    )
    agent_section = '''## Observability & Eval Target 镜像

```text
.agent/modules/10-observability-eval.md
.agent/modules/10-observability-eval-rag-agent-evaluation.md
```

对应正式事实源：

```text
docs/modules/10-observability-eval.md
docs/modules/10-observability-eval-rag-agent-evaluation.md
```

两对文件必须分别字节级一致。主文档定义 Trace/Audit/Eval/Evidence 总边界；附录定义 RAG Core Five、Agentic GraphRAG Trace、Failure Bucket 和 Agent Efficiency。

专用验证：

```text
python tools/scripts/verify_observability_eval_target_protocols.py
pytest -q tests/repo/test_observability_eval_target_protocols.py -p no:cacheprovider
```

'''
    agent = replace_once(agent, "## Agent Core 唯一 Target 镜像\n", agent_section + "## Agent Core 唯一 Target 镜像\n", "agent observability section")
    AGENT.write_text(agent, encoding="utf-8", newline="\n")
    print("Observability branch reconciled with latest Wave 1 main")


if __name__ == "__main__":
    main()
