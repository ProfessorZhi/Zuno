from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_ENTRYPOINTS = {
    "UserDefinedToolRuntime": REPO_ROOT / "src/backend/zuno/platform/services/user_defined_tool_runtime.py",
    "RuntimeFactory": REPO_ROOT / "src/backend/zuno/agent/runtime/factory.py",
    "CapabilityRuntime": REPO_ROOT / "src/backend/zuno/capability/runtime.py",
}

# The old generic agent entry point is retired. Product execution enters
# through the explicit application owners and the governed tool gateway.
RETIRED_DEFAULT_ENTRYPOINTS = {
    "GeneralAgent": REPO_ROOT / "src/backend/zuno/agent/core/agents/general_agent.py",
}

REQUIRED_PHRASES = {
    "UserDefinedToolRuntime": [
        "ToolInvocationGateway",
        "gateway.invoke_readonly",
        "_is_openapi_readonly",
        "TOOL_EFFECT_POLICY_REQUIRED",
    ],
    "RuntimeFactory": [
        "GovernedMemoryContextRuntime",
        "MemoryUnitOfWork",
    ],
    "CapabilityRuntime": [
        "ToolRuntimeRequest",
        "approval_decision_ref",
        "_record_tool_runtime_facts",
        "email sent",
    ],
}

FORBIDDEN_DEFAULT_PHRASES = {
    "UserDefinedToolRuntime": [
        "coroutine=cli_adapter.execute",
        "return [cli_adapter.tool_schema], {cli_adapter.tool_name: cli_adapter.execute}",
        "return await tool_adapter.execute(_tool_name=tool_name, **kwargs)",
    ],
    "CapabilityRuntime": [
        '"message_id": f"msg_',
    ],
}

ADAPTER_ALLOWED_PHRASES = {
    "src/backend/zuno/capability/tools/cli_tool/adapter.py": "asyncio.create_subprocess_exec",
    "src/backend/zuno/capability/tools/openapi_tool/adapter.py": "httpx.AsyncClient",
}


def verify() -> list[str]:
    errors: list[str] = []
    for name, path in DEFAULT_ENTRYPOINTS.items():
        if not path.exists():
            errors.append(f"missing default tool runtime entrypoint: {path.relative_to(REPO_ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in REQUIRED_PHRASES.get(name, []):
            if phrase not in text:
                errors.append(f"{name} missing gateway/cutover phrase: {phrase}")
        for phrase in FORBIDDEN_DEFAULT_PHRASES.get(name, []):
            if phrase in text:
                errors.append(f"{name} retains direct execution bypass phrase: {phrase}")
    for name, path in RETIRED_DEFAULT_ENTRYPOINTS.items():
        if path.exists():
            errors.append(f"retired default tool runtime entrypoint still exists: {path.relative_to(REPO_ROOT)}")

    for rel_path, phrase in ADAPTER_ALLOWED_PHRASES.items():
        text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        if phrase not in text:
            errors.append(f"adapter allowlist lost expected implementation phrase: {rel_path}: {phrase}")

    gateway = REPO_ROOT / "src/backend/zuno/capability/tool_runtime/invocation_gateway.py"
    if not gateway.exists():
        errors.append("missing ToolInvocationGateway implementation")
    else:
        gateway_text = gateway.read_text(encoding="utf-8")
        for phrase in [
            "class ToolInvocationGateway",
            "readonly: bool",
            "TOOL_EFFECT_POLICY_REQUIRED",
            "ToolAttemptInput",
            "ToolExecutionReceiptInput",
            "record_bypass_guard",
        ]:
            if phrase not in gateway_text:
                errors.append(f"ToolInvocationGateway missing required phrase: {phrase}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Tool execution bypass verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
