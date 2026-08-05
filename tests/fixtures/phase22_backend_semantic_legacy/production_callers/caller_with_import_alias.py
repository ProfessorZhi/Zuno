"""Production caller with import alias.

``from module import WorkSpaceSimpleAgent as Agent`` then ``Agent(...)``.
The verifier must resolve ``Agent`` back to ``WorkSpaceSimpleAgent`` and
classify the candidate as ``PRODUCT_ADAPTER`` (canonical-delegate
shape) or ``UNRESOLVED`` (no-delegate shape) depending on the candidate
fixture's evidence.
"""

from tests.fixtures.phase22_backend_semantic_legacy.runtime_definitions.candidate_constructor import (  # noqa: E402
    WorkSpaceSimpleAgent as Agent,
)


def build_with_import_alias(unified_runtime, model_config, user_id, session_id):
    return Agent(
        unified_runtime=unified_runtime,
        model_config=model_config,
        user_id=user_id,
        session_id=session_id,
    )
