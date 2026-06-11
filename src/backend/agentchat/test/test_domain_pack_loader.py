from agentchat.services.domain_pack.loader import DomainPackLoader
from agentchat.services.domain_pack.registry import DomainPackRegistry


def test_contract_review_pack_can_be_loaded():
    pack = DomainPackLoader().load("contract_review")
    assert pack is not None
    assert pack.id == "contract_review"
    assert pack.schema == "schema.json"
    assert pack.retrieval_policy_data["graph_hop_limit"] == 2
    assert "结论" in (pack.answer_template_text or "")
    assert pack.schema_data is not None


def test_registry_lists_contract_review_pack():
    pack_ids = DomainPackRegistry().list_pack_ids()
    assert "contract_review" in pack_ids
