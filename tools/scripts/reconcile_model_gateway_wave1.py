from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs/modules/README.md"
AGENT = ROOT / ".agent/modules/README.md"
SYSTEM = ROOT / ".agent/system.yaml"


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
        "| 04 | Model Gateway | `04-model-gateway.md` | 待细化 |",
        "| 04 | Model Gateway | [`04-model-gateway.md`](./04-model-gateway.md) + [`04-model-gateway-contract-freeze.md`](./04-model-gateway-contract-freeze.md) + [`04-model-gateway-operations-conformance.md`](./04-model-gateway-operations-conformance.md) | 已建立主 Target、Contract Freeze 与 Operations/Conformance 规范 |",
    )
    model_docs = '''## Model Gateway 文档边界

正式 Target 文档、附录与 Agent 镜像：

```text
docs/modules/04-model-gateway.md
.agent/modules/04-model-gateway.md

docs/modules/04-model-gateway-contract-freeze.md
.agent/modules/04-model-gateway-contract-freeze.md

docs/modules/04-model-gateway-operations-conformance.md
.agent/modules/04-model-gateway-operations-conformance.md
```

每一对正式文件与 Agent 镜像都必须字节级一致。

- 主文档定义完整 Model Gateway Target：Role、Provider、Model、Capability、Routing、Attempt、Streaming、Structured Output、Usage、Quota、Health、Circuit、Security 和 Storage。
- Contract Freeze 附录冻结跨模块 Ownership、ModelOperationKind、ModelCall 聚合、Budget / Usage / Quota 崩溃语义、事件目录、三层 Streaming、Routing Replay、Capability 生命周期和 ResultValidity。
- Operations / Conformance 附录定义 Adapter 一致性、配置激活、Provider/Model 生命周期、多租户公平、过载背压、缓存、运维命令、保留删除、SLO、Readiness、兼容升级和 Eval/Judge 治理。

Current 调用清单及旁路状态仍由代码、测试和 `docs/status/production-readiness.md` 证明。

专用验证：

```text
python tools/scripts/verify_model_gateway_target_protocols.py
python tools/scripts/verify_model_gateway_contract_freeze.py
python tools/scripts/verify_model_gateway_operations_conformance.py
pytest -q tests/repo/test_model_gateway_target_protocols.py tests/repo/test_model_gateway_contract_freeze.py tests/repo/test_model_gateway_operations_conformance.py -p no:cacheprovider
```

'''
    docs = replace_once(docs, "## Agent Core 文档边界\n", model_docs + "## Agent Core 文档边界\n", "docs model section")
    DOCS.write_text(docs, encoding="utf-8", newline="\n")

    agent = AGENT.read_text(encoding="utf-8")
    agent = agent.replace(
        "| 04 | Model Gateway | `04-model-gateway.md` | 待细化 |",
        "| 04 | Model Gateway | [`04-model-gateway.md`](./04-model-gateway.md) + [`04-model-gateway-contract-freeze.md`](./04-model-gateway-contract-freeze.md) + [`04-model-gateway-operations-conformance.md`](./04-model-gateway-operations-conformance.md) | 主 Target、Contract Freeze 与 Operations/Conformance 镜像 |",
    )
    model_agent = '''## Model Gateway Target 镜像

```text
.agent/modules/04-model-gateway.md
.agent/modules/04-model-gateway-contract-freeze.md
.agent/modules/04-model-gateway-operations-conformance.md
```

对应正式事实源：

```text
docs/modules/04-model-gateway.md
docs/modules/04-model-gateway-contract-freeze.md
docs/modules/04-model-gateway-operations-conformance.md
```

每一对正式文件与镜像都必须字节级一致。

- 主文档定义 Model Gateway 完整调用协议与领域边界。
- Contract Freeze 附录补充跨模块 Ownership、ModelOperationKind、ModelCall、Budget / Usage / Quota、Event、Streaming、Routing Replay、Capability 和 ResultValidity。
- Operations / Conformance 附录补充 Adapter 一致性、Config / Model 生命周期、租户公平、过载背压、缓存、运维、Retention / Deletion、SLO / Readiness、兼容升级和 Eval / Judge 治理。

专用验证：

```text
python tools/scripts/verify_model_gateway_target_protocols.py
python tools/scripts/verify_model_gateway_contract_freeze.py
python tools/scripts/verify_model_gateway_operations_conformance.py
pytest -q tests/repo/test_model_gateway_target_protocols.py tests/repo/test_model_gateway_contract_freeze.py tests/repo/test_model_gateway_operations_conformance.py -p no:cacheprovider
```

'''
    agent = replace_once(agent, "## Agent Core 唯一 Target 镜像\n", model_agent + "## Agent Core 唯一 Target 镜像\n", "agent model section")
    AGENT.write_text(agent, encoding="utf-8", newline="\n")

    system = SYSTEM.read_text(encoding="utf-8")
    contract = '''  model_gateway:
    formal:
      - "docs/modules/04-model-gateway.md"
      - "docs/modules/04-model-gateway-contract-freeze.md"
      - "docs/modules/04-model-gateway-operations-conformance.md"
    mirror:
      - ".agent/modules/04-model-gateway.md"
      - ".agent/modules/04-model-gateway-contract-freeze.md"
      - ".agent/modules/04-model-gateway-operations-conformance.md"
    target_only: true
    normative_order:
      - "docs/modules/04-model-gateway.md"
      - "docs/modules/04-model-gateway-contract-freeze.md"
      - "docs/modules/04-model-gateway-operations-conformance.md"
    verifiers:
      - "python tools/scripts/verify_model_gateway_target_protocols.py"
      - "python tools/scripts/verify_model_gateway_contract_freeze.py"
      - "python tools/scripts/verify_model_gateway_operations_conformance.py"
    tests:
      - "pytest -q tests/repo/test_model_gateway_target_protocols.py -p no:cacheprovider"
      - "pytest -q tests/repo/test_model_gateway_contract_freeze.py -p no:cacheprovider"
      - "pytest -q tests/repo/test_model_gateway_operations_conformance.py -p no:cacheprovider"
'''
    system = replace_once(system, '  status_truth: "docs/status/production-readiness.md"\n', '  status_truth: "docs/status/production-readiness.md"\n' + contract, "system model contract")
    for anchor, additions in [
        ('      - "docs/modules/03-knowledge-agentic-graphrag.md"\n', '      - "docs/modules/04-model-gateway.md"\n      - "docs/modules/04-model-gateway-contract-freeze.md"\n      - "docs/modules/04-model-gateway-operations-conformance.md"\n'),
        ('      - ".agent/modules/README.md"\n', '      - ".agent/modules/04-model-gateway.md"\n      - ".agent/modules/04-model-gateway-contract-freeze.md"\n      - ".agent/modules/04-model-gateway-operations-conformance.md"\n'),
        ('      - "python tools/scripts/verify_repo_structure.py"\n', '      - "python tools/scripts/verify_model_gateway_target_protocols.py"\n      - "python tools/scripts/verify_model_gateway_contract_freeze.py"\n      - "python tools/scripts/verify_model_gateway_operations_conformance.py"\n'),
    ]:
        system = replace_once(system, anchor, anchor + additions, f"system insertion {anchor.strip()}")
    test_anchor = '      - "pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider"\n'
    model_test = '      - "pytest -q tests/repo/test_model_gateway_target_protocols.py tests/repo/test_model_gateway_contract_freeze.py tests/repo/test_model_gateway_operations_conformance.py -p no:cacheprovider"\n'
    system = replace_once(system, test_anchor, model_test + test_anchor, "system model tests")
    SYSTEM.write_text(system, encoding="utf-8", newline="\n")

    print("Model Gateway branch reconciled with latest Wave 1 main")


if __name__ == "__main__":
    main()
