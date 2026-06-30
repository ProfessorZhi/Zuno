"""Document Ingestion / Parse Gateway contracts."""

from .contracts import (
    CanonicalDocumentIR,
    DocumentBlock,
    DocumentFigure,
    DocumentMetadata,
    DocumentProvenance,
    DocumentTable,
    IndexHandoffPayload,
    ParserAdapterContract,
    ParserCapability,
    ParserFailure,
    SourceSpan,
)
from .router import (
    PARSER_ADAPTER_CONTRACTS,
    PARSER_CAPABILITY_MATRIX,
    build_index_handoff_payload,
    select_parser_for_format,
)

__all__ = [
    "CanonicalDocumentIR",
    "DocumentBlock",
    "DocumentFigure",
    "DocumentMetadata",
    "DocumentProvenance",
    "DocumentTable",
    "IndexHandoffPayload",
    "PARSER_ADAPTER_CONTRACTS",
    "PARSER_CAPABILITY_MATRIX",
    "ParserAdapterContract",
    "ParserCapability",
    "ParserFailure",
    "SourceSpan",
    "build_index_handoff_payload",
    "select_parser_for_format",
]
