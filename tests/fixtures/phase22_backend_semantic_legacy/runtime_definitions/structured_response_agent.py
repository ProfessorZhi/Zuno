"""StructuredResponseAgent fixture — INTERNAL_STEP_CAPABILITY.

Deterministic structured-output capability. Even though this fixture
uses ``create_agent`` inside the class (which on a top-level runtime
would be a legacy signature), the verifier must classify it as
``INTERNAL_STEP_CAPABILITY`` because the class name itself is the
contract.
"""


def create_agent(*, model, response_format):
    return {"model": model, "response_format": response_format}


class StructuredResponseAgent:
    def __init__(self, response_format):
        self.response_format = response_format
        self.structured_agent = self._create_structured_agent()

    def _create_structured_agent(self):
        return create_agent(
            model=None,
            response_format=self.response_format,
        )

    def get_structured_response(self, messages):
        result = self.structured_agent.invoke(input={"messages": messages})
        return result.get("structured_response")