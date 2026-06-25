import asyncio
import importlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_domain_pack_routes_are_not_registered_on_current_router() -> None:
    router = open("src/backend/zuno/api/router.py", encoding="utf-8").read()
    package_exports = open("src/backend/zuno/api/v1/__init__.py", encoding="utf-8").read()

    assert "domain_packs" not in router
    assert "router.include_router(domain_packs.router)" not in router
    assert "domain_packs" not in package_exports


def test_domain_pack_endpoint_module_is_retired_from_current_api_surface() -> None:
    assert not (REPO_ROOT / "src/backend/zuno/api/v1/domain_packs.py").exists()
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.api.v1.domain_packs")


def test_eval_profiles_endpoint_returns_skeleton_payload(monkeypatch):
    from zuno.api.v1.knowledge import list_eval_profiles

    async def fake_list_eval_profiles():
        return [{"eval_profile_id": "contract_review_local", "label": "合同本地评测"}]

    monkeypatch.setattr(
        "zuno.api.v1.knowledge.KnowledgeService.list_eval_profiles",
        fake_list_eval_profiles,
    )

    response = asyncio.run(list_eval_profiles())

    assert response.status_code == 200
    assert response.data[0]["eval_profile_id"] == "contract_review_local"
