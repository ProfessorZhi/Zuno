from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs/decisions/0003-wave1-cross-module-contract-freeze.md"
DECISIONS_INDEX = ROOT / "docs/decisions/README.md"
REGISTRY = ROOT / "docs/governance/wave1-cross-module-contract-registry.md"
MODULES_INDEX = ROOT / "docs/modules/README.md"
AGENT_INDEX = ROOT / ".agent/modules/README.md"
WAVE_VERIFIER = ROOT / "tools/scripts/verify_wave1_contract_freeze.py"
INFRA_VERIFIER = ROOT / "tools/scripts/verify_infrastructure_target_protocols.py"
WAVE_TESTS = ROOT / "tests/repo/test_wave1_contract_freeze.py"

FINAL_MAIN_SHA = "849820d2c52d36abebee8c3d4a974bf035524e0a"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def update_adr() -> None:
    text = ADR.read_text(encoding="utf-8")
    text = re.sub(r"^status: .+$", "status: accepted-target", text, count=1, flags=re.M)
    if "confirmed_wave1_main_sha:" not in text:
        text = text.replace(
            "baseline_main_sha: `729e439e29deadc101c5687fc47125104e62e2c1`\n",
            "baseline_main_sha: `729e439e29deadc101c5687fc47125104e62e2c1`\n"
            f"confirmed_wave1_main_sha: `{FINAL_MAIN_SHA}`\n",
            1,
        )
    text = re.sub(
        r"^reviewed_parallel_prs: .+$",
        "reviewed_and_merged_prs: `#18 Model Gateway`、`#19 Security`、`#17 Infrastructure / shared contracts`、`#21 Observability & Eval`",
        text,
        count=1,
        flags=re.M,
    )
    text = re.sub(
        r"^> 本 ADR 是 Target 设计决议.*$",
        "> 本 ADR 已合并到 `main`，是 Wave 1 的正式共享 Target Contract；它仍不是 Current、实现证据、质量证明或 production readiness 声明。",
        text,
        count=1,
        flags=re.M,
    )
    text = text.replace("accepted-target-pending-merge", "accepted-target")
    text = text.replace("`FIELD_FROZEN_PENDING_MERGE`", "`CONFIRMED_TARGET`")
    ADR.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def update_registry() -> None:
    text = REGISTRY.read_text(encoding="utf-8")
    text = re.sub(r"^status: .+$", "status: confirmed-target", text, count=1, flags=re.M)
    text = re.sub(r"^previous_status: .+$", "previous_status: field-frozen-pending-merge", text, count=1, flags=re.M)
    if "confirmed_wave1_main_sha:" not in text:
        text = text.replace(
            "baseline_main_sha: `729e439e29deadc101c5687fc47125104e62e2c1`\n",
            "baseline_main_sha: `729e439e29deadc101c5687fc47125104e62e2c1`\n"
            f"confirmed_wave1_main_sha: `{FINAL_MAIN_SHA}`\n",
            1,
        )
    text = re.sub(
        r"reviewed_parallel_prs:\n(?:  - .+\n)+canonical_adr:",
        "merged_wave1_prs:\n"
        "  - `#18 Model Gateway → 2ac4f4b5bbf0064cd5a54395755fae13854a33a0`\n"
        "  - `#19 Security → bbd58941c8950cb5e45a9514c524bbecdd9b92ad`\n"
        "  - `#17 Infrastructure / shared contracts → 20964346728d24360a95fb9dcd040d2b58f7d904`\n"
        "  - `#21 Observability & Eval → 849820d2c52d36abebee8c3d4a974bf035524e0a`\n"
        "canonical_adr:",
        text,
        count=1,
    )
    text = re.sub(
        r"^> 本文件是 Wave 1 跨模块共享 Contract 的合并前 Registry.*$",
        "> 本文件已合并到 `main`，是 Wave 1 跨模块共享 Contract 的 `CONFIRMED_TARGET` Registry。它冻结字段、Owner、Failure Namespace 和恢复责任，但仍不代表 Runtime 已实现或成为 Current。",
        text,
        count=1,
        flags=re.M,
    )

    # Promote every active contract row and state marker. Restore the historical
    # lifecycle enum/definition afterwards so the transition history remains documented.
    text = text.replace("`FIELD_FROZEN_PENDING_MERGE`", "`CONFIRMED_TARGET`")
    text = text.replace(
        "PARALLEL_PROPOSAL\nALIGNED_PENDING_FIELDS\nCONFLICT_REQUIRES_DECISION\nCONFIRMED_TARGET\nCONFIRMED_TARGET\nIMPLEMENTATION_AVAILABLE\nCURRENT",
        "PARALLEL_PROPOSAL\nALIGNED_PENDING_FIELDS\nCONFLICT_REQUIRES_DECISION\nFIELD_FROZEN_PENDING_MERGE\nCONFIRMED_TARGET\nIMPLEMENTATION_AVAILABLE\nCURRENT",
        1,
    )
    text = text.replace(
        "CONFIRMED_TARGET\n    已完成字段级设计审计，但仍在未合并 PR。\n\nCONFIRMED_TARGET\n    ADR 0003 与本 Registry 已合并到 main。",
        "FIELD_FROZEN_PENDING_MERGE\n    已完成字段级设计审计，但仍在未合并 PR。\n\nCONFIRMED_TARGET\n    ADR 0003 与本 Registry 已合并到 main。",
        1,
    )
    text = text.replace(
        "本轮决议不会把 Target 写成 Current，也不会把 PR #18、#19、#20 当成已合并事实源。",
        "Wave 1 的 #18、#19、#17、#21 已合并；本轮确认只提升 Target Contract 状态，不把任何模块写成 Current。",
    )
    text = text.replace(
        "PR #17 合并后，本 Registry 状态应更新为 `CONFIRMED_TARGET`。",
        "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`。",
    )

    duplicate = (
        "- `contract_bundle_version`、`producer_module`、`consumer_module` 是强制路由与兼容字段。\n"
        "- `payload` / `payload_ref` 至少一个存在，并同时校验 payload hash 与 schema hash。\n"
        "- Agent 相关消息保留 `run_id` / `step_run_id`；非 Agent 工作流可以为空。\n"
    )
    while text.count(duplicate) > 1:
        first = text.find(duplicate)
        second = text.find(duplicate, first + len(duplicate))
        text = text[:second] + text[second + len(duplicate):]

    REGISTRY.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def update_decisions_index() -> None:
    text = DECISIONS_INDEX.read_text(encoding="utf-8")
    old = """待合并生效的 Target 决议：

- [ADR 0003：Wave 1 跨模块 Contract 与 Infrastructure 物理边界冻结](0003-wave1-cross-module-contract-freeze.md)
  - 当前状态：`accepted-target-pending-merge`；只有合并到 `main` 后才成为正式共享 Target Contract。
  - 冻结范围：`zuno/platform/**` 物理 Ownership、共享 Envelope、Security Epoch、Secret/Credential、Audit、Model Gateway、派生索引、PreparedToolAction、Failure Code 与 Retry/Recovery Owner。
"""
    new = """正式 Target 决议：

- [ADR 0003：Wave 1 跨模块 Contract 与 Infrastructure 物理边界冻结](0003-wave1-cross-module-contract-freeze.md)
  - 当前状态：`accepted-target`；已合并到 `main`，是正式共享 Target Contract，但不是 Current 或实现证据。
  - 冻结范围：服务端权威产品边界、`zuno/platform/**` 物理 Ownership、共享 Envelope、Security Epoch、Secret/Credential、Audit、Model Gateway、派生索引、PreparedToolAction、Failure Code 与 Retry/Recovery Owner。
"""
    text = replace_once(text, old, new, "decisions index ADR 0003 status")
    DECISIONS_INDEX.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def update_module_indexes() -> None:
    text = MODULES_INDEX.read_text(encoding="utf-8")
    marker = "ADR 0003 与 Registry 统一冻结 Security、Infrastructure、Model Gateway、Observability & Eval 之间的 Owner、Envelope、Receipt、Failure Namespace、Security Epoch 和 Recovery 边界。模块文档中的重复说明不得覆盖共享 Contract。"
    addition = marker + "\n\n当前状态：`CONFIRMED_TARGET`。服务端物理实现归 `src/backend/zuno/platform/**`；Agent Core 使用 `ActionProposal / ActionExecutionBinding`，可执行副作用事实归 Tool Runtime `PreparedToolAction`。"
    text = replace_once(text, marker, addition, "formal index Wave 1 confirmed status")
    MODULES_INDEX.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")

    text = AGENT_INDEX.read_text(encoding="utf-8")
    marker = "ADR 0003 与 Registry 是 Wave 1 跨模块 Owner、Envelope、Receipt、Failure Namespace、Security Epoch 和 Recovery 边界的共享事实源。"
    addition = marker + "\n\n当前状态：`CONFIRMED_TARGET`。物理实现归 `src/backend/zuno/platform/**`；Agent Core 只持有 `ActionProposal / ActionExecutionBinding`，可执行副作用事实归 Tool Runtime `PreparedToolAction`。"
    text = replace_once(text, marker, addition, "agent index Wave 1 confirmed status")
    AGENT_INDEX.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def update_wave_verifier() -> None:
    text = WAVE_VERIFIER.read_text(encoding="utf-8")
    text = text.replace('"status: accepted-target-pending-merge"', '"status: accepted-target"')
    text = text.replace('"FIELD_FROZEN_PENDING_MERGE",\n    "src/backend/zuno/platform/"', '"CONFIRMED_TARGET",\n    "src/backend/zuno/platform/"')
    text = text.replace('"status: field-frozen-pending-merge"', '"status: confirmed-target"')

    deferred = '''    # The immediate post-merge integration PR owns shared README routing. This
    # avoids selecting one stale concurrent module index while preserving strict
    # ADR, Registry, Core, Ownership and Requirement validation here.
    if "field-frozen-pending-merge" in registry:
        deferred_routes = "\\n0003-wave1-cross-module-contract-freeze.md\\nwave1-cross-module-contract-registry.md\\nFIELD_FROZEN_PENDING_MERGE\\nsrc/backend/zuno/platform/**\\nPreparedToolAction\\n"
        modules_index += deferred_routes
        agent_index += deferred_routes

'''
    text = text.replace(deferred, "")

    old_index = '''    for content, label in [(modules_index, "docs/modules/README.md"), (agent_index, ".agent/modules/README.md")]:
        for term in [
            "0003-wave1-cross-module-contract-freeze.md",
            "wave1-cross-module-contract-registry.md",
            "FIELD_FROZEN_PENDING_MERGE",
            "src/backend/zuno/platform/**",
            "PreparedToolAction",
        ]:
            if term not in content:
                findings.append(Finding("XMOD_INDEX_ROUTE", f"{label} missing {term}"))
'''
    new_index = '''    for content, label in [(modules_index, "docs/modules/README.md"), (agent_index, ".agent/modules/README.md")]:
        for term in [
            "0003-wave1-cross-module-contract-freeze.md",
            "wave1-cross-module-contract-registry.md",
            "CONFIRMED_TARGET",
            "src/backend/zuno/platform/**",
            "PreparedToolAction",
            "04-model-gateway",
            "09-security",
            "10-observability-eval",
            "11-infrastructure",
        ]:
            if term not in content:
                findings.append(Finding("XMOD_INDEX_ROUTE", f"{label} missing {term}"))
        if "FIELD_FROZEN_PENDING_MERGE" in content:
            findings.append(Finding("XMOD_INDEX_STALE_STATUS", f"{label} still advertises pending-merge status"))

    if modules_index.count("## Model Gateway 文档边界") != 1:
        findings.append(Finding("XMOD_INDEX_DUPLICATE", "docs/modules/README.md must contain exactly one Model Gateway boundary section"))
    if agent_index.count("## Model Gateway Target 镜像") != 1:
        findings.append(Finding("XMOD_AGENT_INDEX_DUPLICATE", ".agent/modules/README.md must contain exactly one Model Gateway mirror section"))
'''
    text = replace_once(text, old_index, new_index, "strict Wave 1 index checks")

    old_status = '''    if registry.count("`FIELD_FROZEN_PENDING_MERGE`") < 25:
        findings.append(Finding("XMOD_STATUS_NOT_FROZEN", "too few shared contracts are field-frozen"))
'''
    new_status = '''    if registry.count("`CONFIRMED_TARGET`") < 25:
        findings.append(Finding("XMOD_STATUS_NOT_CONFIRMED", "too few shared contracts are confirmed target"))
    for stale in ["| `FIELD_FROZEN_PENDING_MERGE` |", "状态：`FIELD_FROZEN_PENDING_MERGE`"]:
        if stale in registry:
            findings.append(Finding("XMOD_ACTIVE_STATUS_STALE", f"active pending-merge marker remains: {stale}"))
'''
    text = replace_once(text, old_status, new_status, "confirmed target count")
    WAVE_VERIFIER.write_text(text, encoding="utf-8", newline="\n")


def update_infra_verifier() -> None:
    text = INFRA_VERIFIER.read_text(encoding="utf-8")
    deferred = '''    # Security and Model Gateway were merged while this PR was open. To avoid a
    # content conflict, shared index routing is finalized by the immediate
    # post-merge Wave 1 integration PR. All module, mirror, Contract and state
    # checks remain strict in this PR.
    if "field-frozen-pending-merge" in registry_content:
        formal_index += "\\n(./11-infrastructure.md)\\n11-infrastructure-data-services.md\\n11-infrastructure-consistency-lifecycle.md\\nwave1-cross-module-contract-registry.md\\n"
        mirror_index += "\\n(./11-infrastructure.md)\\n11-infrastructure-data-services.md\\n11-infrastructure-consistency-lifecycle.md\\n"
'''
    text = text.replace(deferred, "")
    INFRA_VERIFIER.write_text(text, encoding="utf-8", newline="\n")


def update_wave_tests() -> None:
    text = WAVE_TESTS.read_text(encoding="utf-8")
    old = '''def test_registry_is_field_frozen_not_current() -> None:
    content = REGISTRY.read_text(encoding="utf-8")
    assert "status: field-frozen-pending-merge" in content
    assert content.count("`FIELD_FROZEN_PENDING_MERGE`") >= 25
    assert "协调状态：`CONFLICT_REQUIRES_DECISION`" not in content
    assert "本文件当前所有条目最高只能是 `ALIGNED_PENDING_FIELDS`" not in content
    assert "PR #17 合并后，本 Registry 状态应更新为 `CONFIRMED_TARGET`" in content
'''
    new = '''def test_registry_is_confirmed_target_not_current() -> None:
    content = REGISTRY.read_text(encoding="utf-8")
    assert "status: confirmed-target" in content
    assert content.count("`CONFIRMED_TARGET`") >= 25
    assert "| `FIELD_FROZEN_PENDING_MERGE` |" not in content
    assert "状态：`FIELD_FROZEN_PENDING_MERGE`" not in content
    assert "协调状态：`CONFLICT_REQUIRES_DECISION`" not in content
    assert "本文件当前所有条目最高只能是 `ALIGNED_PENDING_FIELDS`" not in content
    assert "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`" in content
    assert "IMPLEMENTATION_AVAILABLE" in content
    assert "CURRENT" in content
'''
    text = replace_once(text, old, new, "Wave 1 confirmed target test")
    WAVE_TESTS.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    update_adr()
    update_registry()
    update_decisions_index()
    update_module_indexes()
    update_wave_verifier()
    update_infra_verifier()
    update_wave_tests()
    print("Wave 1 architecture governance finalized.")


if __name__ == "__main__":
    main()
