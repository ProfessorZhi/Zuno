from __future__ import annotations

from dataclasses import dataclass
import importlib
import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


REQUIRED_PATHS = [
    "AGENTS.md",
    ".agent/README.md",
    ".agent/system.yaml",
    ".agent/references/README.md",
    ".agent/references/task-routing.md",
    ".agent/references/workflow.md",
    ".agent/references/docs-map.md",
    ".agent/programs/current.md",
    ".agent/programs/implementation-roadmap.md",
    ".agent/programs/closure-checklist.md",
    ".agent/architecture/future/programs/README.md",
    ".agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md",
    ".agent/architecture/future/programs/zuno-architecture-visuals-v1/implementation-roadmap.md",
    ".agent/architecture/README.md",
    ".agent/architecture/blueprint.html",
    ".agent/architecture/future/README.md",
    ".agent/architecture/decisions/README.md",
    ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
    ".agent/architecture/near-term/01-target-runtime-architecture.md",
    ".agent/architecture/near-term/02-context-memory-architecture.md",
    ".agent/architecture/near-term/03-capability-tool-retrieval-architecture.md",
    ".agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md",
    ".agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md",
    ".agent/scripts/verify_agent_system.py",
    ".agent/scripts/verify_doc_boundaries.py",
    ".agent/scripts/verify_repo_hygiene.py",
    "apps/desktop",
    "apps/web",
    "apps/web/AGENTS.md",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/architecture/current-architecture.md",
    "docs/architecture/target-architecture.md",
    "docs/architecture/roadmap.md",
    "docs/architecture/diagrams.md",
    "docs/architecture/overview.html",
    "docs/architecture/decisions/README.md",
    "docs/evidence/README.md",
    "docs/evidence/public-demo.md",
    "docs/evidence/eval-baselines.md",
    "docs/reference/terminology.md",
    "docs/history/README.md",
    "docs/history/phases/README.md",
    "docs/history/plans/README.md",
    "docs/history/programs/README.md",
    "docs/history/programs/zuno-target-architecture-migration-v1/README.md",
    "docs/history/programs/zuno-target-runtime-v2/README.md",
    "docs/history/programs/official-graphrag-cleanup-v1/README.md",
    "docs/history/programs/zuno-workflow-doc-system-v1/README.md",
    "docs/history/programs/zuno-target-architecture-refresh-v1/README.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/README.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE01_repo-layout-audit.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE02_root-docs-hygiene.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE03_backend-six-layer-migration-plan.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE04_small-boundary-cleanups.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE05_hygiene-verifier-closure.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE06_backend-directory-clarity-audit.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE07_fastapi-jwt-auth-compat-retirement-plan.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE08_backend-physical-cleanup-slices.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE09_target-layout-visual-compat-shell-retirement.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE10_alias-inventory-and-target-contract.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE11_import-smoke-and-compat-registry-design.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE12_low-risk-alias-surface-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE13_medium-risk-alias-surface-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE14_high-risk-core-services-settings-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE15_final-root-surface-guard-and-closure.md",
    "docs/history/development/README.md",
    "docs/history/reference/migration.md",
    "docs/history/specs",
    "docs/history/audits",
    "examples/graphrag-projects/contract_review/settings.yaml",
    "examples/graphrag-projects/contract_review/schema.json",
    "examples/graphrag-projects/contract_review/retrieval_policy.yaml",
    "examples/graphrag-projects/contract_review/eval/eval_dataset.jsonl",
    "docs/history/domain-packs/root-contract-review/contract_review/pack.yaml",
    "docs/history/domain-packs/root-contract-review/contract_review/schema.json",
    "infra/db",
    "infra/docker",
    "src/backend/zuno",
    "src/backend/zuno/main.py",
    "tests",
    "tools",
    "tools/agent/render_architecture.py",
    "tools/evals/zuno",
    "tools/evals/zuno/AGENTS.md",
]


FORBIDDEN_CURRENT_PATHS = [
    ".agent/skills",
    ".agent/workflows",
    "docs/architecture/history",
    "docs/architecture/audits",
    "docs/architecture/specs",
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
    "docs/development",
    "docs/prototypes",
    "docs/ui-review",
    "docs/ui-gallery",
    "docs/reference/api.md",
    "docs/reference/core.md",
    "docs/reference/database.md",
    "docs/reference/service.md",
    "docs/reference/zuno.md",
    ".agent/programs/context-memory-agent-runtime-v1",
    ".agent/programs/official-graphrag-cleanup-v1",
    ".agent/programs/zuno-target-runtime-v2",
    ".agent/programs/implementation-phases",
    ".agent/programs/phase-05-memory-engine.md",
    ".agent/programs/phase-06-capability-tool-retrieval.md",
    ".agent/programs/phase-07-graphrag-llm-entity-extraction.md",
    ".agent/programs/phase-08-langgraph-runtime.md",
    ".agent/programs/phase-09-product-trace-eval-closure.md",
    "docs/superpowers",
    "src/frontend",
    "domain-packs",
    "tests/compat",
]


DOC_REQUIRED_PHRASES: dict[str, list[str]] = {
    "AGENTS.md": [
        "这是仓库唯一的 Agent 入口",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/system.yaml",
        ".agent/programs/",
        ".agent/architecture/",
        "前台文档默认中文",
    ],
    ".agent/README.md": [
        "Zuno Local Agent Skill System",
        "本地 Agent Skill System",
        "新写或重写的 Agent 文档默认使用中文",
    ],
    "docs/README.md": [
        "./architecture/current-architecture.md",
        "./architecture/target-architecture.md",
        "./architecture/roadmap.md",
        "./evidence/public-demo.md",
        "./history/README.md",
        "前台文档默认使用中文",
    ],
    "docs/architecture/README.md": [
        "current-architecture.md",
        "target-architecture.md",
        "roadmap.md",
        "../evidence/public-demo.md",
        "docs/history/programs/official-graphrag-cleanup-v1/",
        "docs/history/programs/zuno-target-architecture-migration-v1/",
        "过时审计、旧规格、旧 phase、旧计划和旧 runbook",
    ],
    "docs/architecture/roadmap.md": [
        "Phase 11A：已完成",
        "Phase 11B：已完成",
        "Phase 11C：active runtime cleanup 已完成",
        "Phase 12：已通过 target migration closure evidence 关闭",
        "受限历史兼容",
        "zuno-workflow-doc-system-v1",
        "zuno-target-architecture-refresh-v1",
        "zuno-repo-layout-cleanup-v1",
        "zuno-architecture-visuals-v1",
    ],
}

TOP_LEVEL_RESPONSIBILITY_DIRECTORIES = {
    "tools": "维护脚本、验证器、eval、launcher、migration 和架构渲染工具",
    "tests": "自动化测试源和仓库边界 guardrails",
    "examples": "可运行示例和示例输入，不存放运行输出",
    "infra": "数据库、Docker 和本地基础设施配置，不存放运行态 volume/cache",
}

ALLOWED_RESPONSIBILITY_SUBDIRS = {
    "tools": ["agent", "cli", "evals", "launchers", "migrations", "scripts"],
    "tests": [
        "agent",
        "agent_system",
        "api",
        "evals",
        "frontend",
        "graphrag",
        "legacy_guards",
        "repo",
        "retrieval",
        "storage",
        "tools",
    ],
    "examples": ["graphrag-projects"],
    "infra": ["db", "docker"],
}

ALLOWED_RESPONSIBILITY_FILES = {
    "tools": ["__init__.py"],
    "tests": ["README.md", "conftest.py"],
    "examples": [],
    "infra": [],
}

BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS = {
    "api": "target-layer",
    "agent": "target-layer",
    "memory": "target-layer",
    "capability": "target-layer",
    "knowledge": "target-layer",
    "platform": "target-layer",
}

BACKEND_LEGACY_IMPORT_ALIASES = {
    "zuno.compatibility": "legacy imports route through zuno.platform.compatibility",
    "zuno.config": "legacy imports route through zuno.platform.config",
    "zuno.core": "legacy imports route through zuno.agent.core",
    "zuno.database": "legacy imports route through zuno.platform.database",
    "zuno.mcp_servers": "legacy imports route through zuno.capability.mcp.servers",
    "zuno.middleware": "legacy imports route through zuno.platform.middleware",
    "zuno.evals": "legacy imports route through tools/evals/zuno",
    "zuno.resources": "legacy imports route through zuno.platform.resources",
    "zuno.schema": "legacy imports route through zuno.api.dto",
    "zuno.services": "legacy imports route through zuno.platform.services",
    "zuno.settings": "legacy imports route through zuno.platform.settings",
    "zuno.tools": "legacy imports route through zuno.capability.tools",
    "zuno.utils": "legacy imports route through zuno.platform.common",
}

BACKEND_ZUNO_ALLOWED_TOP_LEVEL_FILES = {
    "__init__.py": "package marker",
    "main.py": "FastAPI application entrypoint",
}

BACKEND_RETIRED_TOP_LEVEL_PATHS = {
    "src/backend/fastapi_jwt_auth": "public FastAPI JWT shell retired; runtime imports use zuno.compatibility.vendor.fastapi_jwt_auth",
    "src/backend/zuno/prompts": "runtime prompts moved to zuno/resources/prompts",
    "src/backend/zuno/fixtures": "runtime fixtures moved to zuno/resources/fixtures",
    "src/backend/zuno/system_skills": "runtime system skills moved to zuno/resources/system_skills",
    "src/backend/zuno/legacy": "legacy aliases moved to zuno/compatibility/legacy",
    "src/backend/zuno/vendor": "vendored dependencies moved to zuno/compatibility/vendor",
    "src/backend/zuno/mcp_servers": "MCP server compatibility directory retired; implementations live in zuno/capability/mcp/servers",
    "src/backend/zuno/middleware": "HTTP middleware compatibility directory retired; implementations live in zuno/platform/middleware",
    "src/backend/zuno/evals": "eval compatibility directory retired; implementations live in tools/evals/zuno",
    "src/backend/zuno/compatibility": "compatibility implementation moved to zuno/platform/compatibility; root alias file retired",
    "src/backend/zuno/config": "configuration resources moved to zuno/platform/config; root alias file retired",
    "src/backend/zuno/database": "database implementation moved to zuno/platform/database; root alias file retired",
    "src/backend/zuno/resources": "runtime resources moved to zuno/platform/resources; root alias file retired",
    "src/backend/zuno/schema": "DTO schema implementation moved to zuno/api/dto; root alias file retired",
    "src/backend/zuno/tools": "runtime tools moved to zuno/capability/tools; root alias file retired",
    "src/backend/zuno/services": "legacy service implementation moved to zuno/platform/services; root alias file retired",
    "src/backend/zuno/core": "legacy core implementation moved to zuno/agent/core; root alias file retired",
    "src/backend/zuno/utils": "legacy utils moved to zuno/platform/common; root alias file retired",
    "src/backend/zuno/compatibility.py": "legacy zuno.compatibility alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/config.py": "legacy zuno.config alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/core.py": "legacy zuno.core alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/database.py": "legacy zuno.database alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/evals.py": "legacy zuno.evals alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/mcp_servers.py": "legacy zuno.mcp_servers alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/middleware.py": "legacy zuno.middleware alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/resources.py": "legacy zuno.resources alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/schema.py": "legacy zuno.schema alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/services.py": "legacy zuno.services alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/settings.py": "legacy zuno.settings alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/tools.py": "legacy zuno.tools alias now registered by zuno.platform.compatibility.legacy_aliases",
    "src/backend/zuno/utils.py": "legacy zuno.utils alias now registered by zuno.platform.compatibility.legacy_aliases",
}

ROOT_LOCAL_ARTIFACT_DIRECTORIES = {
    ".agents": "旧 Agent 入口或本地执行残留；当前唯一入口是 AGENTS.md",
    ".local": "本地配置、eval 和运行态产物；可以存在于本机但不能挡住仓库根目录",
    ".test-tmp": "测试 scratch 目录；可再生成且必须保持本地 ignored",
    "__pycache__": "Python bytecode cache；可再生成且不属于仓库结构",
    ".pytest_cache": "pytest 本地缓存；可再生成且不属于仓库结构",
    "node_modules": "依赖安装产物；根目录不提交也不作为项目结构展示",
}


@dataclass
class VerificationResult:
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def verify_required_paths() -> list[str]:
    return [
        f"missing required path: {relative_path}"
        for relative_path in REQUIRED_PATHS
        if not (REPO_ROOT / relative_path).exists()
    ]


def verify_forbidden_current_paths() -> list[str]:
    return [
        f"retired current-path still exists: {relative_path}"
        for relative_path in FORBIDDEN_CURRENT_PATHS
        if (REPO_ROOT / relative_path).exists()
    ]


def verify_doc_phrases() -> list[str]:
    errors: list[str] = []
    for relative_path, phrases in DOC_REQUIRED_PHRASES.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing required doc: {relative_path}")
            continue
        content = _read_text(relative_path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{relative_path} missing phrase: {phrase}")
    return errors


def verify_first_class_directory_responsibilities() -> list[str]:
    errors: list[str] = []
    for directory, role in TOP_LEVEL_RESPONSIBILITY_DIRECTORIES.items():
        root = REPO_ROOT / directory
        if not root.exists():
            errors.append(f"missing first-class responsibility directory: {directory}")
            continue
        if not role:
            errors.append(f"first-class responsibility directory missing role: {directory}")
        actual_subdirs = sorted(
            path.name
            for path in root.iterdir()
            if path.is_dir() and not path.name.startswith("__pycache__")
        )
        actual_files = sorted(path.name for path in root.iterdir() if path.is_file())
        expected_subdirs = ALLOWED_RESPONSIBILITY_SUBDIRS[directory]
        expected_files = ALLOWED_RESPONSIBILITY_FILES[directory]
        if actual_subdirs != expected_subdirs:
            errors.append(
                f"{directory}/ subdirectories drifted from responsibility allowlist: "
                f"expected {expected_subdirs}, got {actual_subdirs}"
            )
        if actual_files != expected_files:
            errors.append(
                f"{directory}/ files drifted from responsibility allowlist: "
                f"expected {expected_files}, got {actual_files}"
            )
    return errors


def verify_backend_zuno_directory_classifications() -> list[str]:
    errors: list[str] = []
    backend_root = REPO_ROOT / "src" / "backend" / "zuno"
    actual_directories = sorted(
        path.name
        for path in backend_root.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    )
    expected_directories = sorted(BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS)
    if actual_directories != expected_directories:
        errors.append(
            "backend zuno top-level directories drifted from classification map: "
            f"expected {expected_directories}, got {actual_directories}"
        )
    for directory, classification in BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS.items():
        path = backend_root / directory
        if not path.is_dir():
            errors.append(f"missing backend zuno classified directory: {directory}")
            continue
        readme = path / "README.md"
        if not readme.exists():
            errors.append(f"missing backend zuno boundary README: {directory}")
            continue
        content = readme.read_text(encoding="utf-8")
        for phrase in [
            f"分类：`{classification}`",
            "当前角色",
            "Target role",
            "禁止事项",
            "Focused tests",
        ]:
            if phrase not in content:
                errors.append(
                    f"{readme.relative_to(REPO_ROOT).as_posix()} missing phrase: {phrase}"
                )
    actual_files = sorted(
        path.name
        for path in backend_root.iterdir()
        if path.is_file()
    )
    expected_files = sorted(BACKEND_ZUNO_ALLOWED_TOP_LEVEL_FILES)
    if actual_files != expected_files:
        errors.append(
            "backend zuno top-level files drifted from completion allowlist: "
            f"expected {expected_files}, got {actual_files}"
        )
    return errors


def verify_backend_legacy_import_aliases() -> list[str]:
    errors: list[str] = []
    registry = REPO_ROOT / "src/backend/zuno/platform/compatibility/legacy_aliases.py"
    if not registry.is_file():
        errors.append("missing backend legacy alias registry: src/backend/zuno/platform/compatibility/legacy_aliases.py")
        return errors
    for module_name, reason in BACKEND_LEGACY_IMPORT_ALIASES.items():
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            errors.append(f"legacy backend import alias failed: {module_name} ({reason}): {exc}")
            continue
        if module_name != "zuno.settings" and not hasattr(module, "__path__"):
            errors.append(f"legacy backend import alias is not package-like: {module_name}")
    return errors


def verify_backend_retired_top_level_paths_are_absent() -> list[str]:
    errors: list[str] = []
    for relative_path, reason in BACKEND_RETIRED_TOP_LEVEL_PATHS.items():
        path = REPO_ROOT / relative_path
        if path.exists():
            errors.append(
                f"retired backend top-level path still exists: {relative_path} ({reason})"
            )
    return errors


def verify_root_local_artifacts_are_absent() -> list[str]:
    errors: list[str] = []
    for relative_path, reason in ROOT_LOCAL_ARTIFACT_DIRECTORIES.items():
        path = REPO_ROOT / relative_path
        if path.exists():
            errors.append(
                f"root local artifact must not remain visible: {relative_path} ({reason})"
            )
    return errors


def verify_target_architecture_html() -> list[str]:
    errors: list[str] = []
    html_path = REPO_ROOT / ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html"
    if not html_path.exists():
        return ["missing canonical target architecture HTML"]
    html = html_path.read_text(encoding="utf-8")
    if "<html" not in html.lower() or "</html>" not in html.lower():
        errors.append("canonical target architecture HTML is not valid HTML")
    for phrase in [
        "Target / Proposed",
        "Native BM25",
        "RRF",
        "Summary Compression",
        "Structured Extraction",
        "ToolCard",
        "Phase 05",
        "Query Journey",
        "产品入口层",
        "RAG / GraphRAG 层",
    ]:
        if phrase not in html:
            errors.append(f"canonical target architecture HTML missing phrase: {phrase}")
    html_refs = [
        path
        for path in REPO_ROOT.glob(".agent/**/*.md")
        if "zuno-ideal-architecture-and-repo-layout.html" in path.read_text(encoding="utf-8")
    ]
    if len(html_refs) < 5:
        errors.append("target architecture HTML is under-referenced by Agent docs")
    return errors


def verify_active_architecture_surface_phase_plan() -> list[str]:
    roadmap_path = REPO_ROOT / ".agent/programs/implementation-roadmap.md"
    if not roadmap_path.exists():
        return ["missing .agent/programs implementation roadmap"]
    roadmap = roadmap_path.read_text(encoding="utf-8")
    errors = [
        f"active program roadmap missing phrase: {phrase}"
        for phrase in [
            "zuno-six-layer-internalization-v1",
            "zuno-repo-layout-cleanup-v1",
            "每次新 program 都从 `PHASE01` 开始编号",
            "zuno-runtime-architecture-upgrade-v1",
            "zuno-architecture-visuals-v1",
        ]
        if phrase not in roadmap
    ]
    phase03_path = REPO_ROOT / "docs/history/programs/zuno-workflow-doc-system-v1/PHASE03_skill-template-program-system.md"
    if not phase03_path.exists():
        errors.append("missing archived Program 1 PHASE03 Skill / Template / Program plan")
    else:
        phase03 = phase03_path.read_text(encoding="utf-8")
        for phrase in [
            "本地 skill system",
            "skill / lesson / playbook",
            "queued program",
        ]:
            if phrase not in phase03:
                errors.append(f"archived Program 1 PHASE03 Skill / Template / Program plan missing phrase: {phrase}")
    active_phase_names = sorted(
        path.name for path in (REPO_ROOT / ".agent/programs").glob("PHASE*.md")
    )
    expected_active_phase_names = [
        "PHASE01_six-layer-current-inventory.md",
        "PHASE02_memory-layer-foundation-surfaces.md",
    ]
    if active_phase_names != expected_active_phase_names:
        errors.append(
            ".agent/programs active phase files are not the expected six-layer internalization set: "
            + ", ".join(active_phase_names)
        )
    for phase_name in [
        "PHASE01_directory-closure-master-plan.md",
        "PHASE02_platform-foundation-directory-migration.md",
        "PHASE03_schema-tools-resources-directory-migration.md",
        "PHASE04_services-thinning-directory-migration.md",
        "PHASE05_core-agent-runtime-directory-migration.md",
        "PHASE06_final-six-layer-guard-and-closure.md",
        "PHASE06_backend-directory-clarity-audit.md",
        "PHASE07_fastapi-jwt-auth-compat-retirement-plan.md",
        "PHASE08_backend-physical-cleanup-slices.md",
        "PHASE09_target-layout-visual-compat-shell-retirement.md",
        "PHASE10_alias-inventory-and-target-contract.md",
        "PHASE11_import-smoke-and-compat-registry-design.md",
        "PHASE12_low-risk-alias-surface-cleanup.md",
        "PHASE13_medium-risk-alias-surface-cleanup.md",
        "PHASE14_high-risk-core-services-settings-cleanup.md",
        "PHASE15_final-root-surface-guard-and-closure.md",
    ]:
        if not (REPO_ROOT / "docs/history/programs/zuno-repo-layout-cleanup-v1" / phase_name).exists():
            errors.append(f"missing archived Program 3 continuation phase: {phase_name}")
    archived_program3 = REPO_ROOT / "docs/history/programs/zuno-repo-layout-cleanup-v1/README.md"
    if not archived_program3.exists():
        errors.append("missing archived Program 3 README")
    else:
        archived_text = archived_program3.read_text(encoding="utf-8")
        for phrase in [
            "root/docs hygiene",
            "backend 六层迁移计划",
            "repo hygiene verifier",
            "Directory Surface Alignment V1",
        ]:
            if phrase not in archived_text:
                errors.append(f"archived Program 3 README missing phrase: {phrase}")
    for queued_path in sorted((REPO_ROOT / ".agent/architecture/future/programs").glob("*/*.md")):
        content = queued_path.read_text(encoding="utf-8")
        if "queued draft / not active" not in content:
            errors.append(f"queued program file missing not-active banner: {queued_path.relative_to(REPO_ROOT).as_posix()}")
    system_yaml_path = REPO_ROOT / ".agent/system.yaml"
    if not system_yaml_path.exists():
        errors.append("missing .agent/system.yaml")
    else:
        system_yaml = system_yaml_path.read_text(encoding="utf-8")
        for phrase in [
            "new_program_first_phase: \"PHASE01\"",
            "skill_routes:",
            ".agent/references/workflow.md",
        ]:
            if phrase not in system_yaml:
                errors.append(f".agent/system.yaml missing phrase: {phrase}")
    return errors


def verify_architecture_diagram_outputs() -> list[str]:
    errors: list[str] = []
    diagrams = _read_text("docs/architecture/diagrams.md")
    for phrase in [
        "Mermaid 源只维护在本文",
        "python tools/agent/render_architecture.py --check",
        "#f8f8fb",
        "#f6f3ff",
        "#a99cff",
        "#2c255f",
        "#9b8cff",
    ]:
        if phrase not in diagrams:
            errors.append(f"docs/architecture/diagrams.md missing diagram sync phrase: {phrase}")

    for relative_path in [
        "docs/architecture/overview.html",
        ".agent/architecture/blueprint.html",
    ]:
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing architecture diagram HTML: {relative_path}")
            continue
        content = path.read_text(encoding="utf-8")
        for phrase in [
            "docs/architecture/diagrams.md",
            "tools/agent/render_architecture.py",
            "Current Runtime",
            "Target Runtime",
            "Maintenance Workflow",
            "#f8f8fb",
            "#f6f3ff",
            "#a99cff",
            "#2c255f",
            "#9b8cff",
        ]:
            if phrase not in content:
                errors.append(f"{relative_path} missing diagram HTML phrase: {phrase}")
    script_path = REPO_ROOT / "tools/agent/render_architecture.py"
    if script_path.exists():
        spec = importlib.util.spec_from_file_location("render_architecture", script_path)
        if spec is None or spec.loader is None:
            errors.append("cannot load tools/agent/render_architecture.py")
        else:
            render_architecture = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = render_architecture
            spec.loader.exec_module(render_architecture)
            rendered = render_architecture.build_html()
            for relative_path in [
                "docs/architecture/overview.html",
                ".agent/architecture/blueprint.html",
            ]:
                path = REPO_ROOT / relative_path
                if path.exists() and path.read_text(encoding="utf-8") != rendered:
                    errors.append(f"generated architecture HTML is stale: {relative_path}")
    return errors


def run_verification() -> VerificationResult:
    return VerificationResult(
        errors=[
            *verify_required_paths(),
            *verify_forbidden_current_paths(),
            *verify_doc_phrases(),
            *verify_root_local_artifacts_are_absent(),
            *verify_first_class_directory_responsibilities(),
            *verify_backend_zuno_directory_classifications(),
            *verify_backend_legacy_import_aliases(),
            *verify_backend_retired_top_level_paths_are_absent(),
            *verify_target_architecture_html(),
            *verify_active_architecture_surface_phase_plan(),
            *verify_architecture_diagram_outputs(),
        ]
    )


def main() -> int:
    result = run_verification()
    if result.ok:
        print("Repository structure verification passed.")
        return 0

    for error in result.errors:
        print(f"ERROR: {error}")
    print("Repository structure verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
