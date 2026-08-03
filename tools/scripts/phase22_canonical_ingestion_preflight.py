"""PHASE22 canonical ingestion preflight (read-only, deterministic).

Decides whether a document has every dependency required to enter formal
canonical ingestion by statically inspecting the canonical owner source tree
(``src/backend/zuno/knowledge`` and ``src/backend/zuno/platform``).

The preflight is deliberately read-only:
- It parses Python sources with :mod:`ast`; it never imports production code.
- It never writes to databases, object stores, indexes, queues, or receipts.
- It never opens TCP connections; connectivity is NOT used to decide READY.

Output contract: the final line is exactly one of
``READY_FOR_CANONICAL_INGESTION`` or ``BLOCKED_WITH_EXACT_GAP``.
Exit status is 0 for READY and 1 for BLOCKED_WITH_EXACT_GAP.

Required dependencies checked (PHASE22 canonical ingestion owner entrypoints):
1. formal Ingestion Application Service
2. UoW / Repository Owner
3. Object Store
4. PostgreSQL
5. Elasticsearch Adapter
6. Milvus Adapter
7. Neo4j Adapter
8. Embedding Gateway
9. Snapshot Activation Owner
10. Index Visibility / Read-back Contract
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_EXAMPLE_REL = "src/backend/zuno/platform/config/config.example.yaml"

READY = "READY_FOR_CANONICAL_INGESTION"
BLOCKED = "BLOCKED_WITH_EXACT_GAP"


@dataclass(frozen=True)
class EntrypointRequirement:
    """A single formal entrypoint that must exist at a known module path."""

    module_rel: str
    entrypoint: str
    methods: tuple[str, ...] = ()
    fields: tuple[str, ...] = ()


@dataclass(frozen=True)
class DependencySpec:
    name: str
    requirements: tuple[EntrypointRequirement, ...]
    credential_path: tuple[str, ...] | None = None


DEPENDENCIES: tuple[DependencySpec, ...] = (
    DependencySpec(
        name="formal ingestion application service",
        requirements=(
            EntrypointRequirement(
                "src/backend/zuno/knowledge/ingestion/production_runtime.py",
                "PackageAProductionIngestionRuntime",
                methods=("accept_workspace_upload", "confirm_snapshot_handoff_published"),
            ),
        ),
    ),
    DependencySpec(
        name="unit-of-work / repository owner",
        requirements=(
            EntrypointRequirement(
                "src/backend/zuno/platform/database/session.py",
                "domain_uow",
            ),
            EntrypointRequirement(
                "src/backend/zuno/platform/database/ingestion/persistence.py",
                "IngestionRepository",
            ),
        ),
    ),
    DependencySpec(
        name="object store",
        requirements=(
            EntrypointRequirement(
                "src/backend/zuno/knowledge/ingestion/production_runtime.py",
                "PackageAProductionIngestionRuntime",
                fields=("object_store",),
            ),
            EntrypointRequirement(
                "src/backend/zuno/platform/storage/durable.py",
                "DurableMinioObjectStore",
                methods=("stage", "commit", "reconcile_committed", "read_committed"),
            ),
        ),
    ),
    DependencySpec(
        name="postgresql",
        requirements=(
            EntrypointRequirement(
                "src/backend/zuno/platform/database/foundation.py",
                "create_foundation_engine",
            ),
        ),
    ),
    DependencySpec(
        name="elasticsearch adapter",
        requirements=(
            EntrypointRequirement(
                "src/backend/zuno/knowledge/indexing/adapters.py",
                "ElasticsearchBm25IndexClient",
            ),
        ),
        credential_path=("rag", "elasticsearch", "hosts"),
    ),
    DependencySpec(
        name="milvus adapter",
        requirements=(
            EntrypointRequirement(
                "src/backend/zuno/knowledge/indexing/adapters.py",
                "MilvusVectorIndexClient",
            ),
        ),
        credential_path=("rag", "vector_db"),
    ),
    DependencySpec(
        name="neo4j adapter",
        requirements=(
            EntrypointRequirement(
                "src/backend/zuno/knowledge/indexing/adapters.py",
                "Neo4jGraphIndexClient",
            ),
        ),
        credential_path=("neo4j",),
    ),
    DependencySpec(
        name="embedding gateway",
        requirements=(
            EntrypointRequirement(
                "src/backend/zuno/platform/model_gateway_adapters.py",
                "OpenAIEmbeddingGatewayAdapter",
            ),
        ),
        credential_path=("multi_models", "embedding", "api_key"),
    ),
    DependencySpec(
        name="snapshot activation owner",
        requirements=(
            EntrypointRequirement(
                "src/backend/zuno/knowledge/ingestion/handoff.py",
                "SnapshotHandoffRuntime",
                methods=("create_snapshot", "dispatch_outbox"),
            ),
        ),
    ),
    DependencySpec(
        name="index visibility / read-back contract",
        requirements=(
            EntrypointRequirement(
                "src/backend/zuno/knowledge/indexing/contracts.py",
                "IndexQueryResult",
            ),
            EntrypointRequirement(
                "src/backend/zuno/knowledge/indexing/contracts.py",
                "IndexJobManifest",
                fields=("adapter_visibility_receipts",),
            ),
        ),
    ),
)


@dataclass
class ModuleSurface:
    top_level: set[str] = field(default_factory=set)
    methods: dict[str, set[str]] = field(default_factory=dict)
    fields: dict[str, set[str]] = field(default_factory=dict)
    missing: bool = False


def parse_module_surface(module_path: Path) -> ModuleSurface:
    """Extract top-level names, class methods and class fields via AST."""
    surface = ModuleSurface()
    if not module_path.is_file():
        surface.missing = True
        return surface
    tree = ast.parse(
        module_path.read_text(encoding="utf-8-sig"), filename=str(module_path)
    )
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            surface.top_level.add(node.name)
        if isinstance(node, ast.ClassDef):
            surface.methods[node.name] = set()
            surface.fields[node.name] = set()
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    surface.methods[node.name].add(child.name)
                    for arg in child.args.args + child.args.kwonlyargs:
                        if arg.arg:
                            surface.fields[node.name].add(arg.arg)
                    if child.name == "__init__":
                        for statement in ast.walk(child):
                            if (
                                isinstance(statement, ast.Assign)
                                and statement.targets
                                and isinstance(statement.targets[0], ast.Attribute)
                                and isinstance(statement.targets[0].value, ast.Name)
                                and statement.targets[0].value.id == "self"
                            ):
                                surface.fields[node.name].add(statement.targets[0].attr)
                elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                    surface.fields[node.name].add(child.target.id)
                elif (
                    isinstance(child, ast.Assign)
                    and isinstance(child.targets[0], ast.Name)
                    and isinstance(child.targets[0].ctx, ast.Store)
                ):
                    surface.fields[node.name].add(child.targets[0].id)
    return surface


def yaml_key_path_present(text: str, path: tuple[str, ...]) -> bool:
    """Check a (possibly nested) key path exists in a YAML-ish file by indentation."""
    if not path:
        return False
    lines = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    stack: list[tuple[int, str]] = []
    for line in lines:
        indent = len(line) - len(line.lstrip())
        key = line.lstrip().split(":", 1)[0].strip().strip('"').strip("'")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        stack.append((indent, key))
        if tuple(part for _, part in stack) == path:
            return True
    return False


def credential_declared(config_path: Path, path: tuple[str, ...]) -> bool:
    if not config_path.is_file():
        return False
    return yaml_key_path_present(config_path.read_text(encoding="utf-8"), path)


@dataclass
class Gap:
    dependency: str
    reason: str
    detail: str = ""


@dataclass
class PreflightResult:
    gaps: list[Gap] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        return BLOCKED if self.gaps else READY

    def describe(self) -> str:
        lines = []
        for gap in self.gaps:
            suffix = f": {gap.detail}" if gap.detail else ""
            lines.append(f"- {gap.dependency}: {gap.reason}{suffix}")
        return "\n".join(lines)


def _check_entrypoint(surface: ModuleSurface, requirement: EntrypointRequirement) -> list[str]:
    problems: list[str] = []
    if requirement.entrypoint not in surface.top_level:
        problems.append(f"entrypoint {requirement.entrypoint!r} not defined")
        return problems
    for method in requirement.methods:
        if method not in surface.methods.get(requirement.entrypoint, set()):
            problems.append(
                f"entrypoint {requirement.entrypoint!r} missing method {method!r}"
            )
    for field_name in requirement.fields:
        if field_name not in surface.fields.get(requirement.entrypoint, set()):
            problems.append(
                f"entrypoint {requirement.entrypoint!r} missing field {field_name!r}"
            )
    return problems


def run_preflight(repo_root: Path, dependencies: Iterable[DependencySpec] = DEPENDENCIES) -> PreflightResult:
    result = PreflightResult()
    config_path = repo_root / CONFIG_EXAMPLE_REL
    for spec in dependencies:
        problems: list[str] = []
        for requirement in spec.requirements:
            surface = parse_module_surface(repo_root / requirement.module_rel)
            if surface.missing:
                problems.append(f"module {requirement.module_rel} missing")
            else:
                problems.extend(_check_entrypoint(surface, requirement))
        if spec.name == "object store":
            problems.extend(_check_object_store_binding(repo_root))
        if spec.credential_path is not None and not credential_declared(
            config_path, spec.credential_path
        ):
            problems.append(
                f"credential not declared in {CONFIG_EXAMPLE_REL}: {'.'.join(spec.credential_path)}"
            )
        if problems:
            result.gaps.append(
                Gap(dependency=spec.name, reason=problems[0], detail="; ".join(problems[1:]))
            )
    return result


def _check_object_store_binding(repo_root: Path) -> list[str]:
    """Validate the production object-store binding without class-name guessing.

    Domain ports, local adapters and physical clients may coexist. The preflight
    only fails owner uniqueness when more than one production ingestion runtime
    constructor binds a competing durable object-store adapter as the default
    production dependency.
    """

    runtime_path = repo_root / "src/backend/zuno/knowledge/ingestion/production_runtime.py"
    if not runtime_path.is_file():
        return ["OBJECT_STORE_BINDING_AMBIGUITY: production runtime module missing"]

    tree = ast.parse(runtime_path.read_text(encoding="utf-8-sig"), filename=str(runtime_path))
    bindings: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != "PackageAProductionIngestionRuntime":
            continue
        for child in node.body:
            if not isinstance(child, ast.FunctionDef) or child.name != "__init__":
                continue
            for arg in child.args.kwonlyargs:
                if "object_store" not in arg.arg:
                    continue
                annotation = _annotation_name(arg.annotation)
                if annotation:
                    bindings.append(annotation)

    if not bindings:
        return ["OBJECT_STORE_BINDING_AMBIGUITY: PackageAProductionIngestionRuntime.object_store has no explicit binding"]
    production_bindings = [name for name in bindings if name != "LocalObjectStore"]
    if len(set(production_bindings)) > 1:
        return [
            "OWNER_NON_UNIQUE: multiple production object-store bindings: "
            + ", ".join(sorted(set(production_bindings)))
        ]
    if "LocalObjectStore" in bindings and production_bindings:
        return ["OWNER_NON_UNIQUE: LocalObjectStore is bound together with a production adapter"]
    if bindings == ["LocalObjectStore"]:
        return ["OBJECT_STORE_BINDING_AMBIGUITY: LocalObjectStore is the only explicit binding"]
    if production_bindings != ["DurableMinioObjectStore"]:
        return [
            "OBJECT_STORE_BINDING_AMBIGUITY: unexpected production binding "
            + ", ".join(sorted(set(production_bindings)))
        ]
    return []


def _annotation_name(annotation: ast.expr | None) -> str:
    if annotation is None:
        return ""
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Attribute):
        return annotation.attr
    if isinstance(annotation, ast.Constant):
        return str(annotation.value)
    if isinstance(annotation, ast.Subscript):
        return _annotation_name(annotation.value)
    return ""


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    repo_root = Path(argv[0]).resolve() if argv else REPO_ROOT
    result = run_preflight(repo_root)
    for spec in DEPENDENCIES:
        gap = next((g for g in result.gaps if g.dependency == spec.name), None)
        if gap is None:
            print(f"PASS  {spec.name}")
        else:
            detail = f" ({gap.detail})" if gap.detail else ""
            print(f"GAP   {spec.name}: {gap.reason}{detail}")
    print()
    if result.gaps:
        print("Canonical ingestion preflight gaps:")
        print(result.describe())
    print(result.verdict)
    return 0 if not result.gaps else 1


if __name__ == "__main__":
    raise SystemExit(main())
