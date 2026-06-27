def test_agent_create_request_uses_graphrag_project_id_as_public_field():
    from zuno.schema.agent import AgentCreateReq

    request = AgentCreateReq(
        name="contract-agent",
        description="Review contract risks",
        system_prompt="review contracts",
        logo_url="/logo.png",
        graphrag_project_id="contract_review",
    )

    payload = request.model_dump()

    assert payload["graphrag_project_id"] == "contract_review"
    assert "domain_pack_id" not in payload


def test_agent_create_request_accepts_legacy_domain_pack_id_as_migration_input():
    from zuno.schema.agent import AgentCreateReq

    request = AgentCreateReq.model_validate(
        {
            "name": "contract-agent",
            "description": "Review contract risks",
            "system_prompt": "review contracts",
            "logo_url": "/logo.png",
            "domain_pack_id": "legacy_contract_review",
        }
    )

    assert request.graphrag_project_id == "legacy_contract_review"
    assert "domain_pack_id" not in request.model_dump()


def test_agent_service_maps_project_field_to_existing_database_column():
    from zuno.api.services.agent import AgentService
    from zuno.schema.agent import AgentCreateReq

    request = AgentCreateReq(
        name="contract-agent",
        description="Review contract risks",
        system_prompt="review contracts",
        logo_url="/logo.png",
        graphrag_project_id="contract_review",
    )

    values = AgentService._agent_request_to_db_values(request)

    assert values["domain_pack_id"] == "contract_review"
    assert "graphrag_project_id" not in values


def test_agent_update_request_prefers_graphrag_project_id_over_legacy_input():
    from zuno.schema.agent import AgentUpdateReq

    request = AgentUpdateReq.model_validate(
        {
            "agent_id": "agent_1",
            "graphrag_project_id": "contract_review_project",
            "domain_pack_id": "legacy_contract_review",
        }
    )

    payload = request.model_dump(exclude={"agent_id"}, exclude_none=True)

    assert payload["graphrag_project_id"] == "contract_review_project"
    assert "domain_pack_id" not in payload


def test_agent_service_maps_update_project_field_to_existing_database_column():
    from zuno.api.services.agent import AgentService

    values = AgentService._agent_update_to_db_values(
        {
            "name": "contract-agent",
            "graphrag_project_id": "contract_review_project",
        }
    )

    assert values["domain_pack_id"] == "contract_review_project"
    assert "graphrag_project_id" not in values
