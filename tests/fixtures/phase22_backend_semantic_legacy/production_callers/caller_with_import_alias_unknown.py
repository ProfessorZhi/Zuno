"""Production caller with import alias to a NON-delegate class.

``from module import WorkSpaceSimpleAgent as Agent`` then ``Agent(...)``
where the candidate class is the no-delegate shape (see
``candidate_constructor_unknown.py``). The verifier must classify the
candidate as ``UNRESOLVED`` because there is no canonical_delegate
evidence and the class is reached by a Production Entry Point.
"""

from tests.fixtures.phase22_backend_semantic_legacy.runtime_definitions.candidate_constructor_unknown import (  # noqa: E402
    WorkSpaceSimpleAgent as Agent,
)


def build_with_import_alias_unknown(model_config, user_id, session_id):
    return Agent(
        model_config=model_config,
        user_id=user_id,
        session_id=session_id,
    )
