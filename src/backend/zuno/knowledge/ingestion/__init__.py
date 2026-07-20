"""Document Ingestion / Parse Gateway contracts."""

from .adapters import PARSER_ADAPTER_REGISTRY, ParserAdapter, get_parser_adapter
from .contracts import (
    CanonicalDocumentIR,
    DocumentBlock,
    DocumentFigure,
    DocumentMetadata,
    DocumentProvenance,
    DocumentTable,
    IndexHandoffPayload,
    ParseDocumentRequest,
    ParseDocumentResult,
    ParseJobSnapshot,
    ParserAdapterContract,
    ParserCapability,
    ParserDiagnostic,
    ParserFailure,
    ParserJobMetrics,
    SourceSpan,
    build_source_span_provenance,
)
from .gateway import ParseGateway
from .normalizer import normalize_legacy_chunks_to_ir
from .review import (
    HumanReviewRuntime,
    QualityGateResult,
    QualityMetric,
    ReviewDecisionReceipt,
    ReviewTask,
)
from .router import (
    PARSER_ADAPTER_CONTRACTS,
    PARSER_CAPABILITY_MATRIX,
    adapter_boundary_metadata,
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
    "HumanReviewRuntime",
    "PARSER_ADAPTER_CONTRACTS",
    "PARSER_ADAPTER_REGISTRY",
    "PARSER_CAPABILITY_MATRIX",
    "ParseDocumentRequest",
    "ParseDocumentResult",
    "ParseJobSnapshot",
    "ParseGateway",
    "ParserAdapterContract",
    "ParserAdapter",
    "ParserCapability",
    "ParserDiagnostic",
    "ParserFailure",
    "ParserJobMetrics",
    "QualityGateResult",
    "QualityMetric",
    "ReviewDecisionReceipt",
    "ReviewTask",
    "SourceSpan",
    "adapter_boundary_metadata",
    "build_index_handoff_payload",
    "build_source_span_provenance",
    "get_parser_adapter",
    "normalize_legacy_chunks_to_ir",
    "select_parser_for_format",
]
