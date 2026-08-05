"""Production caller with assignment alias to a NON-delegate class.

``Runtime = WorkSpaceSimpleAgent`` at module level then ``Runtime(...)``
where the candidate class is the no-delegate shape (see
``candidate_constructor_unknown.py``). The verifier must classify the
candidate as ``UNRESOLVED`` because there is no canonical_delegate
evidence and the class is reached by a Production Entry Point.
"""

from tests.fixtures.phase22_backend_semantic_legacy.runtime_definitions.candidate_constructor_unknown import (  # noqa: E402
    WorkSpaceSimpleAgent,
)


Runtime = WorkSpaceSimpleAgent


def build_with_assignment_alias_unknown(model_config, user_id, session_id):
    return Runtime(
        model_config=model_config,
        user_id=user_id,
        session_id=session_id,
    )
