from uuid import uuid4

from agentchat.api.services.tool import ToolService
from agentchat.database import ToolTable
from agentchat.schema.tool import SimpleApiConfig
from agentchat.services.simple_api_tool import build_openapi_schema_from_simple_config
from agentchat.services.user_defined_tool_runtime import build_stored_tool_auth_config
from agentchat.tools.cli_tool.adapter import CLIToolAdapter
from agentchat.tools.openapi_tool.adapter import OpenAPIToolAdapter


class ToolCreationService:
    @staticmethod
    def validate_and_resolve(
        *,
        runtime_type: str,
        auth_config: dict | None = None,
        cli_config: dict | None = None,
        openapi_schema: dict | None = None,
        simple_api_config: SimpleApiConfig | dict | None = None,
        source_metadata: dict | None = None,
    ) -> tuple[str, dict | None, dict]:
        runtime_type = runtime_type or "remote_api"
        if runtime_type not in {"remote_api", "cli"}:
            raise ValueError("Unsupported runtime_type")

        if runtime_type == "cli":
            CLIToolAdapter.validate_cli_config(cli_config)
            stored_auth = build_stored_tool_auth_config(runtime_type, auth_config, cli_config, None, source_metadata)
            return runtime_type, None, stored_auth

        simple_config_model = None
        if simple_api_config:
            simple_config_model = (
                simple_api_config
                if isinstance(simple_api_config, SimpleApiConfig)
                else SimpleApiConfig(**simple_api_config)
            )
            openapi_schema = build_openapi_schema_from_simple_config(simple_config_model)

        if not openapi_schema:
            raise ValueError("OpenAPI tools require openapi_schema or simple_api_config")
        OpenAPIToolAdapter.validate_openapi_schema(openapi_schema)
        stored_auth = build_stored_tool_auth_config(
            runtime_type,
            auth_config,
            cli_config,
            simple_config_model.model_dump(by_alias=True) if simple_config_model else None,
            source_metadata,
        )
        return runtime_type, openapi_schema, stored_auth

    @classmethod
    async def create_user_defined_tool(
        cls,
        *,
        display_name: str,
        description: str,
        logo_url: str,
        runtime_type: str,
        user_id: str,
        auth_config: dict | None = None,
        cli_config: dict | None = None,
        openapi_schema: dict | None = None,
        simple_api_config: SimpleApiConfig | dict | None = None,
        source_metadata: dict | None = None,
    ) -> dict:
        runtime_type, resolved_schema, stored_auth = cls.validate_and_resolve(
            runtime_type=runtime_type,
            auth_config=auth_config,
            cli_config=cli_config,
            openapi_schema=openapi_schema,
            simple_api_config=simple_api_config,
            source_metadata=source_metadata,
        )
        tool = ToolTable(
            name=f"user_tool_{uuid4().hex[:8]}",
            display_name=display_name,
            description=description,
            logo_url=logo_url,
            openapi_schema=resolved_schema if runtime_type == "remote_api" else None,
            auth_config=stored_auth,
            user_id=user_id,
            is_user_defined=True,
        )
        return await ToolService.create_user_defined_tool(tool)
