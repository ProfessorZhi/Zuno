"""Resources adapter for converting MCP resources to LangChain Blobs."""

import base64

from langchain_core.documents.base import Blob
from mcp import ClientSession
from mcp.types import BlobResourceContents, ResourceContents, TextResourceContents


def convert_mcp_resource_to_langchain_blob(
    resource_uri: str, contents: ResourceContents
) -> Blob:
    if isinstance(contents, TextResourceContents):
        data = contents.text
    elif isinstance(contents, BlobResourceContents):
        data = base64.b64decode(contents.blob)
    else:
        raise TypeError(f"Unsupported content type for URI {resource_uri}")

    return Blob.from_data(
        data=data, mime_type=contents.mimeType, metadata={"uri": resource_uri}
    )


async def get_mcp_resource(session: ClientSession, uri: str) -> list[Blob]:
    contents_result = await session.read_resource(uri)
    if not contents_result.contents:
        return []

    return [
        convert_mcp_resource_to_langchain_blob(uri, content)
        for content in contents_result.contents
    ]


async def load_mcp_resources(
    session: ClientSession,
    *,
    uris: str | list[str] | None = None,
) -> list[Blob]:
    blobs = []

    if uris is None:
        resources_list = await session.list_resources()
        uri_list = [resource.uri for resource in resources_list.resources]
    elif isinstance(uris, str):
        uri_list = [uris]
    else:
        uri_list = uris

    current_uri = None
    try:
        for uri in uri_list:
            current_uri = uri
            blobs.extend(await get_mcp_resource(session, uri))
    except Exception as exc:
        raise RuntimeError(f"Error fetching resource {current_uri}") from exc

    return blobs
