from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_ENTRYPOINTS = {
    "GeneralAgent": REPO_ROOT / "src/backend/zuno/agent/core/agents/general_agent.py",
    "UserDefinedToolRuntime": REPO_ROOT / "src/backend/zuno/platform/services/user_defined_tool_runtime.py",
    "RuntimeFactory": REPO_ROOT / "src/backend/zuno/agent/runtime/factory.py",
    "CapabilityRuntime": REPO_ROOT / "src/backend/zuno/capability/runtime.py",
}

REQUIRED_PHRASES = {
    "GeneralAgent": [
        "ToolInvocationGateway",
        "gateway.invoke_readonly",
        "readonly=self._is_readonly_tool",
    ],
    "UserDefinedToolRuntime": [
        "ToolInvocationGateway",
        "gateway.invoke_readonly",
        "_is_openapi_readonly",
        "PHASE16_REQUIRED",
    ],
    "RuntimeFactory": [
        "GovernedMemoryContextRuntime",
        "MemoryUnitOfWork",
    ],
    "CapabilityRuntime": [
        "readonly_cutover_only=False",
        "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL",
        "_record_tool_runtime_facts",
        "email sent",
    ],
}

FORBIDDEN_DEFAULT_PHRASES = {
    "GeneralAgent": [
        "tool_result = await handler(request)",
        "tool_result, _ = await use_tool.coroutine",
        "await current_tool.ainvoke(tool_args)",
    ],
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
            "PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL",
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
