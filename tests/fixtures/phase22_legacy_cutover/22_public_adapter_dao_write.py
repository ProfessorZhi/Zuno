"""Contract fixture 22: public API adapter writes directly into a DAO.

This mirrors the pattern the public-adapter ownership check is designed
to detect: a public adapter imports a domain DAO module and calls
``session.add`` / ``session.commit`` directly.
"""

from __future__ import annotations

from zuno.platform.database.dao import SomeDao  # type: ignore[import-not-found]


def write_artifact_directly(session, artifact_id: str) -> None:
    dao = SomeDao(session)
    dao.session.add({"artifact_id": artifact_id})
    dao.session.commit()