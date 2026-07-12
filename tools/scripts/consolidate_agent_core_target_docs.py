from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN_NAME = "06-agent-core-planning-control.md"
REMOVED_NAMES = [
    "06-agent-core-control-protocols.md",
    "06-agent-core-consistency-lifecycle-protocols.md",
]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def write(relative: str, content: str) -> None:
    (ROOT / relative).write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def shift_headings(content: str) -> str:
    lines: list[str] = []
    for line in content.splitlines():
        match = re.match(r"^(#{1,5})(\s+.*)$", line)
        if match:
            line = "#" + match.group(1) + match.group(2)
        lines.append(line)
    return "\n".join(lines).strip()


def replace_once(content: str, old: str, new: str, label: str) -> str:
    if content.count(old) != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, got {content.count(old)}")
    return content.replace(old, new, 1)


def build_single_target_document() -> str:
    main = read(f"docs/modules/{MAIN_NAME}")
    control = read("docs/modules/06-agent-core-control-protocols.md")
    consistency = read("docs/modules/06-agent-core-consistency-lifecycle-protocols.md")

    main = main.replace("status: normative-target-module-design", "status: normative-target-module-architecture")

    section_zero_start = main.index("## 0. 文档集与规范优先级")
    part_one_start = main.index("# Part I：定位与概念架构")
    section_zero = """## 0. 文档边界与事实源

本文是 Agent Core / Planning & Control 模块唯一的正式 Target 架构文档，统一承载：

```text
问题与目标
概念架构与完整运行流程
架构不变量和状态机
DAG、并发、Interrupt、Signal 与副作用协议
TaskContract、GoalVersion 与一致性协议
Finalization、Artifact、Publication 与 RunOutcome
Failure、Budget、Recovery、Event 与时间语义
目标代码、数据库、Contract、测试和完成证据
```

文档边界：

```text
docs/modules/06-agent-core-planning-control.md
    唯一 Target 架构事实源。

.agent/modules/06-agent-core-planning-control.md
    字节级一致的 Agent 镜像。

.agent/programs/
    Current → Target 的实现、升级、迁移、切流和收口计划。

docs/status/
    Current、Gap、Measurement 和完成证据状态。
```

规范优先级：

```text
全局架构原则
→ 本模块 Target 架构文档
→ 已确认的 Program
→ 代码与 Migration
```

任何 Program 或实现不得自行改变本文已经确认的架构原则。本文不包含 Current Baseline、具体迁移阶段或 Cutover 步骤。

---

"""
    main = main[:section_zero_start] + section_zero + main[part_one_start:]

    validation_marker = "# Part V：验证与完成证据"
    if validation_marker not in main:
        raise RuntimeError("main document missing validation part")
    design, validation = main.split(validation_marker, 1)
    validation = "# Part VIII：验证与完成证据" + validation
    validation = validation.replace(
        "编号 033–060 由控制协议定义；编号 061–080 由一致性协议定义。验证器确保编号 001 至 080 连续、无重复。",
        "编号 033–060 由本文 Part VI 定义；编号 061–080 由本文 Part VII 定义。验证器确保编号 001 至 080 连续、无重复。",
    )

    control_body = control[control.index("# 1. 控制权模型") :]
    consistency_body = consistency[consistency.index("# 1. TaskContract、GoalVersion 与 Objective") :]

    merged = "\n".join(
        [
            design.rstrip(),
            "",
            "# Part VI：规范性控制协议",
            "",
            shift_headings(control_body),
            "",
            "# Part VII：一致性与生命周期协议",
            "",
            shift_headings(consistency_body),
            "",
            validation.strip(),
        ]
    )
    for name in REMOVED_NAMES:
        merged = '\n'.join(line for line in merged.splitlines() if name not in line)
    return merged


def docs_modules_readme() -> str:
    return """# Zuno 逻辑模块设计文档

`docs/modules/` 是 Zuno 十一个逻辑模块的正式 Target 设计目录。

这里回答：

```text
模块解决什么问题
负责与不负责什么
完整运行流程
状态、失败、恢复、幂等和安全
跨模块 Contract 与 Ownership
目标代码、数据库和测试规格
什么证据才能把 Target 变为 Current
```

总架构以 `docs/architecture/architecture.md` 为最高层入口；Current、Gap 和 Blocked 以 `docs/status/production-readiness.md` 为事实源。

## 十一个逻辑模块

| 编号 | 模块 | 正式模块文档 | 状态 |
| --- | --- | --- | --- |
| 01 | Product Surface | `01-product-surface.md` | 待细化 |
| 02 | Input / Document Ingestion | [`02-input-document-ingestion.md`](./02-input-document-ingestion.md) | 已建立 Target 规范 |
| 03 | Knowledge / Agentic GraphRAG | [`03-knowledge-agentic-graphrag.md`](./03-knowledge-agentic-graphrag.md) | 已建立 Target 规范 |
| 04 | Model Gateway | `04-model-gateway.md` | 待细化 |
| 05 | Memory & Context | [`05-memory-context.md`](./05-memory-context.md) | 已建立 Target 规范 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 已建立单一完整 Target 架构文档 |
| 07 | Capability / Skill | [`07-capability-skill.md`](./07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | `09-security.md` | 待细化 |
| 10 | Observability & Eval | [`10-observability-eval.md`](./10-observability-eval.md) | 已建立 Target 规范 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

## Agent Core 文档边界

唯一正式 Target 文档：

```text
docs/modules/06-agent-core-planning-control.md
```

它统一包含概念架构、运行流程、不变量、状态机、DAG 与并发、Interrupt / Signal、副作用、Finalization、一致性、事件、Artifact、恢复、时间、目标代码、数据库和测试规格。

执行和迁移计划不写入模块 Target 文档：

```text
.agent/programs/    Current → Target 的实现、迁移、切流和收口计划
docs/status/       Current、Gap、Measurement 和完成状态
docs/history/      已完成 Program 与历史证据
```

## Agent 镜像

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md
```

正式文件与镜像必须字节级一致。

规则：

- 不得只修改 `.agent/modules/`；
- 不得在 Target 文档中写 Current Baseline 或具体迁移步骤；
- Current 变化只有在代码、Migration、测试、Trace、Eval 和运行证据完成后，才可写入状态文档；
- 模块设计不得放回 `docs/architecture/`；
- Agent Core 变更必须同步单一正式文档、镜像、入口、验证器和测试。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
```
"""


def agent_modules_readme() -> str:
    return """# Zuno 逻辑模块设计文档镜像

`.agent/modules/` 保存 Agent System 高频读取的模块镜像；`docs/modules/` 是正式事实源。

## 十一个逻辑模块

| 编号 | 模块 | 正式模块文档 | 状态 |
| --- | --- | --- | --- |
| 01 | Product Surface | `01-product-surface.md` | 待细化 |
| 02 | Input / Document Ingestion | [`02-input-document-ingestion.md`](../../docs/modules/02-input-document-ingestion.md) | 已建立 Target 规范 |
| 03 | Knowledge / Agentic GraphRAG | [`03-knowledge-agentic-graphrag.md`](../../docs/modules/03-knowledge-agentic-graphrag.md) | 已建立 Target 规范 |
| 04 | Model Gateway | `04-model-gateway.md` | 待细化 |
| 05 | Memory & Context | [`05-memory-context.md`](../../docs/modules/05-memory-context.md) | 已建立 Target 规范 |
| 06 | Agent Core / Planning & Control | [`06-agent-core-planning-control.md`](./06-agent-core-planning-control.md) | 单一完整 Target 架构镜像 |
| 07 | Capability / Skill | [`07-capability-skill.md`](../../docs/modules/07-capability-skill.md) | 已建立 Target 规范 |
| 08 | Tool Runtime | `08-tool-runtime.md` | 待细化 |
| 09 | Security | `09-security.md` | 待细化 |
| 10 | Observability & Eval | [`10-observability-eval.md`](../../docs/modules/10-observability-eval.md) | 已建立 Target 规范 |
| 11 | Infrastructure | `11-infrastructure.md` | 待细化 |

## Agent Core 唯一 Target 镜像

```text
.agent/modules/06-agent-core-planning-control.md
```

对应正式事实源：

```text
docs/modules/06-agent-core-planning-control.md
```

该文档统一包含主设计、控制协议和一致性生命周期协议。Current 与 Gap 读取 `docs/status/production-readiness.md`；实现与迁移计划读取 `.agent/programs/`。

正式文件与镜像必须字节级一致，不得只修改 `.agent/modules/`。

专用验证：

```text
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/repo/test_agent_core_target_protocols.py -p no:cacheprovider
```
"""


def update_agents() -> None:
    path = ROOT / "AGENTS.md"
    content = path.read_text(encoding="utf-8")
    old = """- Agent Core 正式文档集：
  - `docs/modules/06-agent-core-planning-control.md`
  - `docs/modules/06-agent-core-control-protocols.md`
  - `docs/modules/06-agent-core-consistency-lifecycle-protocols.md`
- Agent Core 镜像集：
  - `.agent/modules/06-agent-core-planning-control.md`
  - `.agent/modules/06-agent-core-control-protocols.md`
  - `.agent/modules/06-agent-core-consistency-lifecycle-protocols.md`

Agent Core 规范优先级：全局架构原则 → 规范性协议 → 主设计实施规格 → Program 与代码。

模块文档可以很详细，但必须服从总架构的 Owner 边界，不得把 Target 冒充为 Current。Agent Core 三份文档只描述 Target，不承载 Current Baseline 或具体迁移计划。"""
    new = """- Agent Core 唯一正式 Target 文档：`docs/modules/06-agent-core-planning-control.md`。
- Agent Core 唯一镜像：`.agent/modules/06-agent-core-planning-control.md`。

Agent Core 规范优先级：全局架构原则 → 单一模块 Target 架构文档 → Program → 代码与 Migration。

模块文档可以很详细，但必须服从总架构的 Owner 边界，不得把 Target 冒充为 Current。Agent Core Target 文档不承载 Current Baseline、实现 Phase、Cutover 或具体迁移计划；这些内容必须进入 `.agent/programs/`。"""
    content = replace_once(content, old, new, "AGENTS module document block")
    content = content.replace(
        "Agent Core 任务必须同时读取主设计、控制协议和一致性协议。",
        "Agent Core 任务必须读取唯一正式 Target 文档 `docs/modules/06-agent-core-planning-control.md`。",
    )
    content = content.replace(
        "`src/backend/zuno/agent/**` → Agent Core 三份模块文档、Runtime Call Chain 和 Code Map。",
        "`src/backend/zuno/agent/**` → Agent Core 单一模块 Target 文档、Runtime Call Chain 和 Code Map。",
    )
    path.write_text(content, encoding="utf-8", newline="\n")


def update_system_yaml() -> None:
    path = ROOT / ".agent/system.yaml"
    content = path.read_text(encoding="utf-8")
    old = """    formal:
      - "docs/modules/06-agent-core-planning-control.md"
      - "docs/modules/06-agent-core-control-protocols.md"
      - "docs/modules/06-agent-core-consistency-lifecycle-protocols.md"
    mirror:
      - ".agent/modules/06-agent-core-planning-control.md"
      - ".agent/modules/06-agent-core-control-protocols.md"
      - ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md"
    target_only: true
    normative_order:
      - "global architecture principles"
      - "Agent Core normative protocols"
      - "Agent Core main design implementation specification"
      - "Program and code"""
    new = """    formal:
      - "docs/modules/06-agent-core-planning-control.md"
    mirror:
      - ".agent/modules/06-agent-core-planning-control.md"
    target_only: true
    execution_plan_root: ".agent/programs"
    normative_order:
      - "global architecture principles"
      - "Agent Core unified target architecture document"
      - "Program"
      - "code and migration"""
    content = replace_once(content, old, new, "system.yaml agent_core block")
    for name in REMOVED_NAMES:
        content = "\n".join(line for line in content.splitlines() if name not in line) + "\n"
    path.write_text(content, encoding="utf-8", newline="\n")


def update_architecture_entrypoints() -> None:
    for relative in ["docs/architecture/README.md", ".agent/architecture/README.md"]:
        content = read(relative)
        content = content.replace("Agent Core Target 文档集：", "Agent Core 唯一 Target 文档：")
        content = content.replace("对应 Agent 镜像：", "对应唯一 Agent 镜像：")
        for name in REMOVED_NAMES:
            content = "\n".join(line for line in content.splitlines() if name not in line) + "\n"
        write(relative, content)

    for relative in ["docs/architecture/architecture.md", ".agent/architecture/architecture.md"]:
        content = read(relative)
        content = content.replace(
            "完整 Target 由三份模块规范共同定义：",
            "完整 Target 由一份模块架构文档统一定义：",
        )
        content = content.replace(
            "问题、概念架构、完整运行流程、目标代码和持久化规格。",
            "统一包含概念架构、控制协议、一致性协议、目标代码、数据库和测试规格。",
        )
        for name in REMOVED_NAMES:
            content = "\n".join(line for line in content.splitlines() if name not in line) + "\n"
        write(relative, content)


def verifier_source() -> str:
    return '''from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/06-agent-core-planning-control.md"
MIRROR = REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"
AGENTS = REPO_ROOT / "AGENTS.md"
SYSTEM_YAML = REPO_ROOT / ".agent/system.yaml"

REMOVED_PATHS = [
    REPO_ROOT / "docs/modules/06-agent-core-control-protocols.md",
    REPO_ROOT / "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
    REPO_ROOT / ".agent/modules/06-agent-core-control-protocols.md",
    REPO_ROOT / ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",
]

REQUIRED_PARTS = [
    "# Part I：定位与概念架构",
    "# Part II：智能机制与运行流程",
    "# Part III：状态、恢复与一致性",
    "# Part IV：目标 Contract 与实施规格",
    "# Part VI：规范性控制协议",
    "# Part VII：一致性与生命周期协议",
    "# Part VIII：验证与完成证据",
]

REQUIRED_TERMS = [
    "Single Controller Agent Runtime",
    "AgentRunGraph",
    "StepExecutionGraph",
    "TaskContract",
    "GoalVersion",
    "pending_interrupt_refs",
    "WAITING_CONDITION",
    "CANCELLING",
    "PreparedAction",
    "RecoveryWatermark",
    "ResultValidity",
    "RunOrphanReconciler",
    "prepare_publication",
    "DeliveryReceipt",
    "PostgreSQL",
    "本文是 Agent Core / Planning & Control 模块唯一的正式 Target 架构文档",
    ".agent/programs/",
]

FORBIDDEN_TERMS = [
    "# 35. Current Baseline",
    "# 36. 实现阶段",
    "pending_interrupt_id: str | None",
    "同一 Run 默认只允许一个 PENDING Interrupt",
    "Agent Core Target 由三份正式文档共同构成",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    for path in [FORMAL, MIRROR, DOCS_INDEX, AGENT_INDEX, AGENTS, SYSTEM_YAML]:
        if not path.exists():
            errors.append(f"missing Agent Core target path: {path.relative_to(REPO_ROOT)}")
    for path in REMOVED_PATHS:
        if path.exists():
            errors.append(f"retired split Agent Core document still exists: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal = _read(FORMAL)
    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Agent Core formal document and mirror must be byte-identical")

    if "status: normative-target-module-architecture" not in formal:
        errors.append("Agent Core document must declare normative-target-module-architecture")

    for part in REQUIRED_PARTS:
        if part not in formal:
            errors.append(f"Agent Core document missing part: {part}")
    for term in REQUIRED_TERMS:
        if term not in formal:
            errors.append(f"Agent Core document missing required term: {term}")
    for term in FORBIDDEN_TERMS:
        if term in formal:
            errors.append(f"Agent Core document contains obsolete contract: {term}")

    ids = [int(value) for value in re.findall(r"ARCH-AGENT-(\\d{3})", formal)]
    if sorted(ids) != list(range(1, 81)):
        errors.append("Agent Core document must define ARCH-AGENT-001 through ARCH-AGENT-080 exactly once")

    for index_name, content in {
        "docs/modules/README.md": _read(DOCS_INDEX),
        ".agent/modules/README.md": _read(AGENT_INDEX),
        "AGENTS.md": _read(AGENTS),
        ".agent/system.yaml": _read(SYSTEM_YAML),
    }.items():
        if "06-agent-core-planning-control.md" not in content:
            errors.append(f"{index_name} does not route to the unified Agent Core target document")
        for retired in [
            "06-agent-core-control-protocols.md",
            "06-agent-core-consistency-lifecycle-protocols.md",
        ]:
            if retired in content:
                errors.append(f"{index_name} still references retired split document: {retired}")

    if ".agent/programs" not in formal or ".agent/programs" not in _read(DOCS_INDEX):
        errors.append("Target architecture and execution Program boundary is not explicit")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("unified Agent Core target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def tests_source() -> str:
    return '''from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_agent_core_target_protocols.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_agent_core_target_protocols", VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Agent Core target verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_unified_agent_core_target_contract() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_only_one_agent_core_target_document_exists() -> None:
    assert (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").exists()
    assert (REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md").exists()
    for relative in [
        "docs/modules/06-agent-core-control-protocols.md",
        "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
        ".agent/modules/06-agent-core-control-protocols.md",
        ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",
    ]:
        assert not (REPO_ROOT / relative).exists()


def test_unified_document_covers_all_requirements_once() -> None:
    content = (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").read_text(encoding="utf-8")
    ids = [int(value) for value in re.findall(r"ARCH-AGENT-(\\d{3})", content)]
    assert sorted(ids) == list(range(1, 81))


def test_unified_document_is_target_only_and_program_separated() -> None:
    content = (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").read_text(encoding="utf-8")
    assert "唯一的正式 Target 架构文档" in content
    assert ".agent/programs/" in content
    assert "# 35. Current Baseline" not in content
    assert "# 36. 实现阶段" not in content
    assert "pending_interrupt_id: str | None" not in content


def test_agent_core_mirror_is_byte_identical() -> None:
    formal = (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").read_bytes()
    mirror = (REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md").read_bytes()
    assert mirror == formal


def test_unified_document_keeps_control_and_consistency_protocols() -> None:
    content = (REPO_ROOT / "docs/modules/06-agent-core-planning-control.md").read_text(encoding="utf-8")
    for term in [
        "# Part VI：规范性控制协议",
        "# Part VII：一致性与生命周期协议",
        "WAITING_CONDITION",
        "PreparedAction",
        "RecoveryWatermark",
        "ResultValidity",
        "RunOrphanReconciler",
        "prepare_publication",
    ]:
        assert term in content
'''


def update_agent_system_verifier() -> None:
    path = ROOT / ".agent/scripts/verify_agent_system.py"
    content = path.read_text(encoding="utf-8")
    content = re.sub(
        r"AGENT_CORE_DOCS = \[.*?\]\n",
        'AGENT_CORE_DOCS = ["06-agent-core-planning-control.md"]\n',
        content,
        count=1,
        flags=re.S,
    )
    content = re.sub(
        r'        "docs/modules/06-agent-core-planning-control\.md": \[.*?\n        \],\n        "docs/modules/06-agent-core-control-protocols\.md": \[.*?\n        \],\n        "docs/modules/06-agent-core-consistency-lifecycle-protocols\.md": \[.*?\n        \],',
        '''        "docs/modules/06-agent-core-planning-control.md": [
            "Single Controller Agent Runtime",
            "Plan DAG",
            "TaskContract",
            "pending_interrupt_refs",
            "WAITING_CONDITION",
            "PreparedAction",
            "RecoveryWatermark",
            "ResultValidity",
            "RunOrphanReconciler",
            "prepare_publication",
            "ARCH-AGENT-080",
            "PostgreSQL",
        ],''',
        content,
        count=1,
        flags=re.S,
    )
    path.write_text(content, encoding="utf-8", newline="\n")


def remove_retired_references() -> None:
    candidates = [
        "tools/scripts/verify_docs_entrypoints.py",
        "tests/repo/test_docs_entrypoints.py",
        ".agent/references/docs-map.md",
        ".agent/references/architecture-docs-map.md",
        ".agent/references/verification-map.md",
        ".agent/references/runtime-call-chain.md",
        ".agent/references/code-map.md",
    ]
    for relative in candidates:
        path = ROOT / relative
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for name in REMOVED_NAMES:
            content = "\n".join(line for line in content.splitlines() if name not in line) + "\n"
        content = content.replace("三份 Agent Core Target 文档", "单一 Agent Core Target 文档")
        content = content.replace("Agent Core 三份 Target 文档", "Agent Core 单一 Target 文档")
        path.write_text(content, encoding="utf-8", newline="\n")


def delete_split_docs() -> None:
    for relative in [
        "docs/modules/06-agent-core-control-protocols.md",
        "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
        ".agent/modules/06-agent-core-control-protocols.md",
        ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",
    ]:
        path = ROOT / relative
        if path.exists():
            path.unlink()


def ensure_no_active_references() -> None:
    ignored_roots = {".git", "docs/history"}
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".py", ".yaml", ".yml"}:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if any(relative == root or relative.startswith(root + "/") for root in ignored_roots):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for name in REMOVED_NAMES:
            if name in content:
                failures.append(f"{relative}: {name}")
    if failures:
        raise RuntimeError("retired split document references remain:\n" + "\n".join(failures))


def main() -> None:
    merged = build_single_target_document()
    write(f"docs/modules/{MAIN_NAME}", merged)
    write(f".agent/modules/{MAIN_NAME}", merged)
    write("docs/modules/README.md", docs_modules_readme())
    write(".agent/modules/README.md", agent_modules_readme())
    update_agents()
    update_system_yaml()
    update_architecture_entrypoints()
    write("tools/scripts/verify_agent_core_target_protocols.py", verifier_source())
    write("tests/repo/test_agent_core_target_protocols.py", tests_source())
    update_agent_system_verifier()
    remove_retired_references()
    delete_split_docs()
    print("Agent Core Target documentation consolidated into one canonical module document.")


if __name__ == "__main__":
    main()
