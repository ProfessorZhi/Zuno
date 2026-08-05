"""ReActStepRunner fixture — INTERNAL_STEP_CAPABILITY.

Step-internal capability used inside the StepExecutionGraph. The verifier
must classify it as ``INTERNAL_STEP_CAPABILITY`` and never report it as
a top-level runtime finding, even though its methods look like they
drive a model call. The class name itself is the contract.
"""


class ReActStepRunner:
    def run(self, *, state, step, deps):
        if deps.model_gateway is None:
            return {"status": "blocked", "reason": "missing_model_gateway"}
        request = {
            "run_id": state.run_id,
            "step_id": step.step_id,
            "prompt": "Run exactly one ReAct step",
        }
        result = deps.model_gateway.invoke(request)
        return {"status": result.status, "observation": result.output}


__all__ = ["ReActStepRunner"]