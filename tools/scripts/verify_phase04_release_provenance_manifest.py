from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from zuno.platform.contracts import ReleaseManifestV1, canonical_sha256

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO_ROOT / "infra" / "docker" / "docker-compose.yml"
ALEMBIC_VERSIONS = REPO_ROOT / "infra" / "db" / "alembic" / "versions"
CAPABILITY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-infrastructure-capability-profile.md"
)
UPGRADE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-upgrade-compatibility-profiles.md"
)
CONFORMANCE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-adapter-conformance-profiles.md"
)

REQUIRED_INFRA_SERVICES = {
    "postgres": "zuno-postgres",
    "rabbitmq": "zuno-rabbitmq",
    "minio": "zuno-minio",
}


def _run(args: list[str]) -> str:
    result = subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout.strip()


def _compose() -> dict[str, Any]:
    return yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))


def _compose_hash() -> str:
    return canonical_sha256(yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8")))


def _source_commit() -> str:
    return _run(["git", "rev-parse", "HEAD"])


def _running_image_id(container_name: str) -> str:
    image_id = _run(["docker", "inspect", "--format", "{{.Image}}", container_name])
    if not image_id.startswith("sha256:"):
        raise RuntimeError(f"{container_name} image id is not sha256")
    return image_id


def _running_health(container_name: str) -> str:
    return _run(
        [
            "docker",
            "inspect",
            "--format",
            "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}",
            container_name,
        ]
    )


def _network_refs(compose: dict[str, Any]) -> tuple[str, ...]:
    refs: list[str] = []
    services = compose.get("services") or {}
    for service_name, container_name in REQUIRED_INFRA_SERVICES.items():
        service = services.get(service_name) or {}
        for port in service.get("ports") or []:
            refs.append(f"{container_name}:{port}")
        for network in service.get("networks") or []:
            refs.append(f"{container_name}:network:{network}")
    return tuple(sorted(refs))


def _adapter_versions(compose: dict[str, Any]) -> tuple[str, ...]:
    services = compose.get("services") or {}
    versions: list[str] = []
    for service_name, container_name in REQUIRED_INFRA_SERVICES.items():
        image = services[service_name]["image"]
        image_id = _running_image_id(container_name)
        versions.append(f"{service_name}:{image}@{image_id}")
    return tuple(sorted(versions))


def _migration_versions() -> tuple[str, ...]:
    versions = [
        path.stem
        for path in sorted(ALEMBIC_VERSIONS.glob("*.py"))
        if path.name != "__init__.py"
    ]
    if not versions:
        raise RuntimeError("no Alembic migration versions found")
    return tuple(versions)


def _release_manifest() -> ReleaseManifestV1:
    compose = _compose()
    compose_hash = _compose_hash()
    adapter_versions = _adapter_versions(compose)
    source_commit = _source_commit()
    bundle_digest = "sha256:" + canonical_sha256(
        {
            "compose_hash": compose_hash,
            "adapter_versions": adapter_versions,
            "source_commit": source_commit,
        }
    )
    payload = {
        "release_id": f"phase04-infra-{source_commit[:12]}",
        "source_commit": source_commit,
        "application_image_digest": bundle_digest,
        "sbom_ref": f"infra/docker/docker-compose.yml#sha256:{compose_hash}",
        "signature_ref": "sha256:"
        + canonical_sha256(
            {
                "release_id": f"phase04-infra-{source_commit[:12]}",
                "bundle_digest": bundle_digest,
                "provenance": "phase04.infrastructure.release.provenance.v1",
            }
        ),
        "config_versions": (
            f"compose:{compose_hash}",
            "dr-profile:docs/governance/infrastructure-dr-profile.yaml",
            "operations-runbook:docs/governance/infrastructure-operations-runbook.md",
        ),
        "migration_versions": _migration_versions(),
        "adapter_versions": adapter_versions,
        "data_service_compatibility_ref": (
            "docs/evidence/phase04-upgrade-compatibility-profiles.md"
        ),
        "rollback_release_ref": None,
        "network_refs": _network_refs(compose),
        "provenance_refs": (
            "docs/evidence/phase04-infrastructure-capability-profile.md",
            "docs/evidence/phase04-upgrade-compatibility-profiles.md",
            "docs/evidence/phase04-adapter-conformance-profiles.md",
        ),
    }
    return ReleaseManifestV1(**payload, content_hash=canonical_sha256(payload))


def verify_phase04_release_provenance_manifest() -> list[str]:
    errors: list[str] = []
    compose = _compose()
    services = compose.get("services") or {}

    missing_services = sorted(set(REQUIRED_INFRA_SERVICES) - set(services))
    if missing_services:
        errors.append(f"missing compose service(s): {missing_services!r}")

    for service_name, container_name in REQUIRED_INFRA_SERVICES.items():
        service = services.get(service_name) or {}
        if not service.get("image"):
            errors.append(f"{service_name} image is missing")
        if not service.get("ports"):
            errors.append(f"{service_name} ports are missing")
        if "zuno-network" not in (service.get("networks") or []):
            errors.append(f"{service_name} is not attached to zuno-network")
        try:
            if _running_health(container_name) != "healthy":
                errors.append(f"{container_name} is not healthy")
        except RuntimeError as exc:
            errors.append(str(exc))

    for evidence in [CAPABILITY_EVIDENCE, UPGRADE_EVIDENCE, CONFORMANCE_EVIDENCE]:
        if not evidence.exists():
            errors.append(f"missing provenance evidence ref: {evidence}")

    try:
        manifest = _release_manifest()
    except (RuntimeError, ValidationError) as exc:
        errors.append(f"release manifest validation failed: {exc}")
        return errors

    if manifest.content_hash != canonical_sha256(manifest.hash_inputs()):
        errors.append("release manifest content hash is not canonical")
    if manifest.data_service_compatibility_ref != str(
        UPGRADE_EVIDENCE.relative_to(REPO_ROOT).as_posix()
    ):
        errors.append("release manifest is not bound to the compatibility evidence")
    if not any(ref.endswith("5432:5432") for ref in manifest.network_refs):
        errors.append("postgres network ref is missing")
    if not any(ref.endswith("5672:5672") for ref in manifest.network_refs):
        errors.append("rabbitmq network ref is missing")
    if not any(ref.endswith("9000:9000") for ref in manifest.network_refs):
        errors.append("minio network ref is missing")
    if not all("sha256:" in version for version in manifest.adapter_versions):
        errors.append("adapter versions are not bound to running image ids")

    mutated = manifest.hash_inputs()
    mutated["source_commit"] = "0" * 40
    if canonical_sha256(mutated) == manifest.content_hash:
        errors.append("source commit change did not change manifest hash")

    try:
        ReleaseManifestV1(**manifest.hash_inputs(), content_hash="bad")
        errors.append("invalid release manifest content_hash was accepted")
    except ValidationError:
        pass

    try:
        payload = manifest.hash_inputs()
        payload["rollback_release_ref"] = payload["release_id"]
        payload["content_hash"] = canonical_sha256(payload)
        ReleaseManifestV1(**payload)
        errors.append("self rollback release ref was accepted")
    except ValidationError:
        pass

    return errors


def main() -> int:
    errors = verify_phase04_release_provenance_manifest()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 release provenance manifest verification failed.")
        return 1
    print("PHASE04 release provenance manifest verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
