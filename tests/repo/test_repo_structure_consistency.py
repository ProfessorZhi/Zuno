import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_required_current_paths_exist() -> None:
    required_paths = [
        "AGENTS.md",
        ".agent/README.md",
        ".agent/references/README.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/references/docs-map.md",
        ".agent/programs/current.md",
        ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
        ".agent/architecture/near-term/01-target-runtime-architecture.md",
        ".agent/architecture/near-term/02-context-memory-architecture.md",
        ".agent/architecture/near-term/03-capability-tool-retrieval-architecture.md",
        ".agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md",
        ".agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md",
        ".agent/architecture/blueprint.html",
        "apps/desktop",
        "apps/web",
        "docs/README.md",
        "docs/architecture/current-architecture.md",
        "docs/architecture/target-architecture.md",
        "docs/architecture/roadmap.md",
        "docs/architecture/diagrams.md",
        "docs/architecture/overview.html",
        "docs/evidence/public-demo.md",
        "docs/reference/terminology.md",
        "docs/history/README.md",
        "docs/history/phases/README.md",
        "docs/history/plans/README.md",
        "docs/history/programs/README.md",
        "docs/history/development/README.md",
        "docs/history/reference/migration.md",
        "docs/history/audits",
        "docs/history/specs",
        "docs/history/domain-packs/root-contract-review/contract_review/pack.yaml",
        "src/backend/zuno/main.py",
        "tools/agent/render_architecture.py",
        "tools/evals/zuno",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing required path: {relative_path}"


def test_repo_structure_verifier_pins_current_front_path() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    required_paths = set(verifier.REQUIRED_PATHS)
    for relative_path in [
        "AGENTS.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        "docs/README.md",
        "docs/architecture/current-architecture.md",
        "docs/architecture/target-architecture.md",
        "docs/architecture/roadmap.md",
        "docs/architecture/overview.html",
        "docs/evidence/public-demo.md",
        "docs/reference/terminology.md",
        "docs/history/audits",
        "docs/history/specs",
        "docs/history/development/README.md",
    ]:
        assert relative_path in required_paths


def test_repo_structure_verifier_pins_first_class_directory_responsibilities() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.TOP_LEVEL_RESPONSIBILITY_DIRECTORIES == {
        "tools": "维护脚本、验证器、eval、launcher、migration 和架构渲染工具",
        "tests": "自动化测试源和仓库边界 guardrails",
        "examples": "可运行示例和示例输入，不存放运行输出",
        "infra": "数据库、Docker 和本地基础设施配置，不存放运行态 volume/cache",
    }
    assert verifier.ALLOWED_RESPONSIBILITY_SUBDIRS == {
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


def test_repo_structure_verifier_pins_backend_zuno_directory_classifications() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS == {
        "api": "target-layer",
        "agent": "target-layer",
        "memory": "target-layer",
        "capability": "target-layer",
        "knowledge": "target-layer",
        "platform": "target-layer",
    }


def test_backend_zuno_classified_directories_have_boundary_readmes() -> None:
    classified_directories = [
        "api",
        "agent",
        "memory",
        "capability",
        "knowledge",
        "platform",
    ]

    for directory in classified_directories:
        readme = REPO_ROOT / "src" / "backend" / "zuno" / directory / "README.md"
        assert readme.exists(), f"missing backend zuno boundary README: {directory}"
        content = readme.read_text(encoding="utf-8")
        for phrase in ["当前角色", "Target role", "禁止事项", "Focused tests"]:
            assert phrase in content, f"{readme.relative_to(REPO_ROOT)} missing phrase: {phrase}"


def test_backend_zuno_top_level_directories_match_classification_map() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    actual_directories = sorted(
        path.name
        for path in (REPO_ROOT / "src/backend/zuno").iterdir()
        if path.is_dir() and path.name != "__pycache__"
    )

    assert actual_directories == sorted(verifier.BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS)


def test_repo_structure_verifier_pins_backend_compatibility_alias_modules() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.BACKEND_COMPATIBILITY_ALIAS_MODULES == {
        "src/backend/zuno/compatibility.py": "legacy zuno.compatibility imports route to zuno.platform.compatibility",
        "src/backend/zuno/config.py": "legacy zuno.config imports route to zuno.platform.config",
        "src/backend/zuno/core.py": "legacy zuno.core imports route to zuno.agent.core",
        "src/backend/zuno/database.py": "legacy zuno.database imports route to zuno.platform.database",
        "src/backend/zuno/mcp_servers.py": "legacy zuno.mcp_servers imports route to zuno.capability.mcp.servers",
        "src/backend/zuno/middleware.py": "legacy zuno.middleware imports route to zuno.platform.middleware",
        "src/backend/zuno/evals.py": "legacy zuno.evals imports route to tools/evals/zuno",
        "src/backend/zuno/resources.py": "legacy zuno.resources imports route to zuno.platform.resources",
        "src/backend/zuno/schema.py": "legacy zuno.schema imports route to zuno.api.dto",
        "src/backend/zuno/services.py": "legacy zuno.services imports route to zuno.platform.services",
        "src/backend/zuno/settings.py": "legacy zuno.settings imports route to zuno.platform.settings",
        "src/backend/zuno/tools.py": "legacy zuno.tools imports route to zuno.capability.tools",
        "src/backend/zuno/utils.py": "legacy zuno.utils imports route to zuno.platform.common",
    }


def test_repo_structure_verifier_pins_root_local_artifact_directories() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.ROOT_LOCAL_ARTIFACT_DIRECTORIES == {
        ".agents": "旧 Agent 入口或本地执行残留；当前唯一入口是 AGENTS.md",
        ".local": "本地配置、eval 和运行态产物；可以存在于本机但不能挡住仓库根目录",
        ".test-tmp": "测试 scratch 目录；可再生成且必须保持本地 ignored",
        "__pycache__": "Python bytecode cache；可再生成且不属于仓库结构",
        ".pytest_cache": "pytest 本地缓存；可再生成且不属于仓库结构",
        "node_modules": "依赖安装产物；根目录不提交也不作为项目结构展示",
    }


def test_first_class_directory_subdirs_match_allowed_responsibilities() -> None:
    allowed_subdirs = {
        "tools": {"agent", "cli", "evals", "launchers", "migrations", "scripts"},
        "tests": {
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
        },
        "examples": {"graphrag-projects"},
        "infra": {"db", "docker"},
    }
    allowed_files = {
        "tools": {"__init__.py"},
        "tests": {"README.md", "conftest.py"},
        "examples": set(),
        "infra": set(),
    }

    for directory, expected_subdirs in allowed_subdirs.items():
        actual_subdirs = {
            path.name
            for path in (REPO_ROOT / directory).iterdir()
            if path.is_dir() and not path.name.startswith("__pycache__")
        }
        actual_files = {
            path.name
            for path in (REPO_ROOT / directory).iterdir()
            if path.is_file()
        }
        assert actual_subdirs == expected_subdirs
        assert actual_files == allowed_files[directory]


def test_repo_structure_verifier_runs_first_class_directory_responsibility_check(monkeypatch) -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    sentinel = "first-class responsibility check was called"

    def fake_responsibility_check() -> list[str]:
        return [sentinel]

    monkeypatch.setattr(
        verifier,
        "verify_first_class_directory_responsibilities",
        fake_responsibility_check,
    )

    result = verifier.run_verification()

    assert sentinel in result.errors


def test_repo_structure_verifier_runs_backend_zuno_directory_classification_check(monkeypatch) -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    sentinel = "backend zuno directory classification check was called"

    def fake_backend_classification_check() -> list[str]:
        return [sentinel]

    monkeypatch.setattr(
        verifier,
        "verify_backend_zuno_directory_classifications",
        fake_backend_classification_check,
    )

    result = verifier.run_verification()

    assert sentinel in result.errors


def test_repo_structure_verifier_runs_root_local_artifact_check(monkeypatch) -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    sentinel = "root local artifact check was called"

    def fake_root_local_artifact_check() -> list[str]:
        return [sentinel]

    monkeypatch.setattr(
        verifier,
        "verify_root_local_artifacts_are_absent",
        fake_root_local_artifact_check,
    )

    result = verifier.run_verification()

    assert sentinel in result.errors


def test_repo_structure_verifier_pins_retired_backend_top_level_paths() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.BACKEND_RETIRED_TOP_LEVEL_PATHS == {
        "src/backend/fastapi_jwt_auth": "public FastAPI JWT shell retired; runtime imports use zuno.compatibility.vendor.fastapi_jwt_auth",
        "src/backend/zuno/prompts": "runtime prompts moved to zuno/resources/prompts",
        "src/backend/zuno/fixtures": "runtime fixtures moved to zuno/resources/fixtures",
        "src/backend/zuno/system_skills": "runtime system skills moved to zuno/resources/system_skills",
        "src/backend/zuno/legacy": "legacy aliases moved to zuno/compatibility/legacy",
        "src/backend/zuno/vendor": "vendored dependencies moved to zuno/compatibility/vendor",
        "src/backend/zuno/mcp_servers": "MCP server compatibility shell retired to zuno/mcp_servers.py; implementations live in zuno/capability/mcp/servers",
        "src/backend/zuno/middleware": "HTTP middleware compatibility shell retired to zuno/middleware.py; implementations live in zuno/platform/middleware",
        "src/backend/zuno/evals": "eval compatibility shell retired to zuno/evals.py; implementations live in tools/evals/zuno",
        "src/backend/zuno/compatibility": "compatibility implementation moved to zuno/platform/compatibility; zuno/compatibility.py remains as alias",
        "src/backend/zuno/config": "configuration resources moved to zuno/platform/config; zuno/config.py remains as alias",
        "src/backend/zuno/database": "database implementation moved to zuno/platform/database; zuno/database.py remains as alias",
        "src/backend/zuno/resources": "runtime resources moved to zuno/platform/resources; zuno/resources.py remains as alias",
        "src/backend/zuno/schema": "DTO schema implementation moved to zuno/api/dto; zuno/schema.py remains as alias",
        "src/backend/zuno/tools": "runtime tools moved to zuno/capability/tools; zuno/tools.py remains as alias",
        "src/backend/zuno/services": "legacy service implementation moved to zuno/platform/services; zuno/services.py remains as alias",
        "src/backend/zuno/core": "legacy core implementation moved to zuno/agent/core; zuno/core.py remains as alias",
        "src/backend/zuno/utils": "legacy utils moved to zuno/platform/common; zuno/utils.py remains as alias",
    }


def test_repo_structure_verifier_runs_retired_backend_top_level_path_check(
    monkeypatch,
) -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    sentinel = "retired backend path check was called"

    def fake_retired_backend_path_check() -> list[str]:
        return [sentinel]

    monkeypatch.setattr(
        verifier,
        "verify_backend_retired_top_level_paths_are_absent",
        fake_retired_backend_path_check,
    )

    result = verifier.run_verification()

    assert sentinel in result.errors


def test_retired_front_path_directories_are_not_current_paths() -> None:
    retired_paths = [
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
        ".agent/skills",
        ".agent/workflows",
        ".agent/programs/context-memory-agent-runtime-v1",
        ".agent/programs/official-graphrag-cleanup-v1",
        ".agent/programs/zuno-target-runtime-v2",
        ".agent/programs/implementation-phases",
        "docs/superpowers",
        "src/frontend",
        "domain-packs",
        "tests/compat",
    ]

    for relative_path in retired_paths:
        assert not (REPO_ROOT / relative_path).exists(), f"retired path still current: {relative_path}"


def test_backend_visual_compatibility_shells_are_modules_not_directories() -> None:
    backend_root = REPO_ROOT / "src" / "backend" / "zuno"

    for name in [
        "compatibility",
        "config",
        "core",
        "database",
        "evals",
        "mcp_servers",
        "middleware",
        "resources",
        "schema",
        "services",
        "settings",
        "tools",
        "utils",
    ]:
        assert not (backend_root / name).exists(), f"visual compatibility directory still exists: {name}"
        assert (backend_root / f"{name}.py").exists(), f"missing compatibility module: {name}.py"


def test_backend_zuno_top_level_files_match_completion_allowlist() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    actual_files = sorted(
        path.name
        for path in (REPO_ROOT / "src/backend/zuno").iterdir()
        if path.is_file()
    )

    assert actual_files == sorted(verifier.BACKEND_ZUNO_ALLOWED_TOP_LEVEL_FILES)


def test_front_path_docs_link_current_entrypoints() -> None:
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "current-architecture.md" in architecture_index
    assert "target-architecture.md" in architecture_index
    assert "roadmap.md" in architecture_index
    assert "../evidence/public-demo.md" in architecture_index
    assert "./architecture/roadmap.md" in docs_index
    assert "./docs/architecture/roadmap.md" in readme


def test_phase_completion_truth_is_historical() -> None:
    content = (REPO_ROOT / "docs" / "history" / "phases" / "README.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "Phase 0: Stable Runtime Recovery",
        "Phase 1: LangGraph Runtime Deepening",
        "Phase 2: GraphRAG Mainline Deepening",
        "Phase 3: Domain Pack Formalization",
        "Phase 4: Knowledge Config V2 + Local Eval Strengthening",
        "Phase 5: Docs And Public Explanation Sync",
        "Phase 6: Agent GraphRAG Pluginization / Future Platform Layer",
    ]:
        assert phrase in content


def test_readme_mentions_current_backend_start_and_focused_verification() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in [
        "python tools/scripts/verify_docs_entrypoints.py",
        "python tools/scripts/verify_repo_structure.py",
        "pytest -q tests/repo/test_repo_structure_consistency.py",
        "pytest -q tests/repo/test_publish_boundary.py",
        "uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860",
        "受限历史兼容",
        "docs/history/domain-packs/root-contract-review/",
        "Phase 11A",
        "Phase 11B",
        "Phase 11C",
        "Phase 12",
    ]:
        assert phrase in readme


def test_reference_migration_doc_is_archived_out_of_front_path() -> None:
    assert not (REPO_ROOT / "docs" / "reference" / "migration.md").exists()
    assert (REPO_ROOT / "docs" / "history" / "reference" / "migration.md").exists()


def test_program3_continuation_keeps_one_active_phase_file() -> None:
    active_files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent" / "programs").iterdir()
        if path.is_file()
    )

    assert active_files == sorted(
        [
            "README.md",
            "current.md",
            "implementation-roadmap.md",
            "closure-checklist.md",
        ]
    )
    assert not (REPO_ROOT / ".agent/programs/zuno-target-runtime-v2").exists()
    assert not (REPO_ROOT / ".agent/programs/implementation-phases").exists()
    assert (
        REPO_ROOT
        / "docs/history/programs/zuno-target-runtime-v2/implementation-phases/README.md"
    ).exists()

    roadmap = (
        REPO_ROOT / ".agent/programs/implementation-roadmap.md"
    ).read_text(encoding="utf-8")
    for phrase in [
        "当前没有 active program",
        "每次新 program 都从 `PHASE01` 开始编号",
        "zuno-repo-layout-cleanup-v1",
        "zuno-runtime-architecture-upgrade-v1",
        "zuno-architecture-visuals-v1",
    ]:
        assert phrase in roadmap
    program3 = (
        REPO_ROOT / "docs/history/programs/zuno-repo-layout-cleanup-v1/README.md"
    ).read_text(encoding="utf-8")
    assert "Directory Surface Alignment V1" in program3
    assert "repo hygiene verifier" in program3
    assert "capability/mcp/servers" in program3
    assert "platform/middleware" in program3
    for phase in [
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
    ]:
        assert (
            REPO_ROOT / "docs/history/programs/zuno-repo-layout-cleanup-v1" / phase
        ).exists()
    phase03 = (
        REPO_ROOT / "docs/history/programs/zuno-workflow-doc-system-v1/PHASE03_skill-template-program-system.md"
    ).read_text(encoding="utf-8")
    assert "本地 skill system" in phase03
    program2 = (
        REPO_ROOT / "docs/history/programs/zuno-target-architecture-refresh-v1/README.md"
    ).read_text(encoding="utf-8")
    assert "LLM extraction" in program2


def test_architecture_diagram_generation_paths_are_pinned() -> None:
    content = (REPO_ROOT / "tools/scripts/verify_repo_structure.py").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "docs/architecture/diagrams.md",
        "docs/architecture/overview.html",
        ".agent/architecture/blueprint.html",
        "tools/agent/render_architecture.py",
        "verify_architecture_diagram_outputs",
    ]:
        assert phrase in content


def test_superseded_specs_are_archived_out_of_architecture_front_path() -> None:
    assert not (REPO_ROOT / "docs" / "architecture" / "specs").exists()
    for relative_path in [
        "deep-graphrag-v1-runtime.md",
        "domain-pack-langgraph-graphrag-architecture.md",
        "domain-pack-builder.md",
        "knowledge-product-boundary.md",
    ]:
        assert (REPO_ROOT / "docs" / "history" / "specs" / relative_path).exists()
