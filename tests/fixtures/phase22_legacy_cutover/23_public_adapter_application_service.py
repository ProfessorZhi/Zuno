"""Contract fixture 23: public adapter that calls an application service.

This is the canonical, correct pattern: a public adapter delegates to
the application service instead of writing into the DAO directly.
"""

from __future__ import annotations

from zuno.application.artifact_service import ArtifactApplicationService  # type: ignore[import-not-found]


def write_artifact_via_application_service(artifact_id: str) -> None:
    service = ArtifactApplicationService.from_default()
    service.write(artifact_id)