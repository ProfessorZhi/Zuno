import asyncio
from types import SimpleNamespace


def test_domain_pack_routes_are_registered() -> None:
    router = open("src/backend/zuno/api/router.py", encoding="utf-8").read()
    package_exports = open("src/backend/zuno/api/v1/__init__.py", encoding="utf-8").read()

    assert "domain_packs" in router
    assert "router.include_router(domain_packs.router)" in router
    assert "domain_packs" in package_exports


def test_list_domain_packs_endpoint_returns_service_payload(monkeypatch):
    from zuno.api.v1.domain_packs import list_domain_packs

    async def fake_list_domain_packs():
        return [{"pack_id": "contract_review", "name": "合同审查", "status": "published"}]

    monkeypatch.setattr(
        "zuno.api.v1.domain_packs.DomainPackService.list_domain_packs",
        fake_list_domain_packs,
    )

    response = asyncio.run(list_domain_packs())

    assert response.status_code == 200
    assert response.data[0]["pack_id"] == "contract_review"
    assert response.data[0]["status"] == "published"


def test_publish_domain_pack_endpoint_uses_service(monkeypatch):
    from zuno.api.v1.domain_packs import publish_domain_pack

    captured = {}

    async def fake_publish_domain_pack(pack_id: str):
        captured["pack_id"] = pack_id
        return {"pack_id": pack_id, "status": "published", "version": "v1"}

    monkeypatch.setattr(
        "zuno.api.v1.domain_packs.DomainPackService.publish_domain_pack",
        fake_publish_domain_pack,
    )

    response = asyncio.run(publish_domain_pack(pack_id="contract_review"))

    assert response.status_code == 200
    assert captured["pack_id"] == "contract_review"
    assert response.data["status"] == "published"


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

