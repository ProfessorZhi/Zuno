from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from uuid import uuid4


BASE_URL = os.getenv("ZUNO_FULL_E2E_BASE", "http://127.0.0.1:8090").rstrip("/")
API_URL = os.getenv("ZUNO_FULL_E2E_API", "http://127.0.0.1:7860").rstrip("/")
QA_API_URL = os.getenv("ZUNO_FULL_E2E_QA_API", "http://127.0.0.1:9101").rstrip("/")
AUTH_PATH = Path(os.getenv("ZUNO_FULL_E2E_AUTH", "auth.json"))
PRODUCT_CUTOVER_COMMANDS = {
    "shadow": "SHADOW_SUBMIT_USER_GOAL",
    "canary": "CANARY_SUBMIT_USER_GOAL",
    "new_default": "SUBMIT_USER_GOAL",
}


def _read_json_url(url: str) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise AssertionError(f"Failed to reach {url}: {exc}") from exc


def _storage_token() -> str:
    if not AUTH_PATH.exists():
        raise AssertionError(f"Missing Playwright storage state: {AUTH_PATH}")
    state = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    for origin in state.get("origins", []):
        for item in origin.get("localStorage", []):
            if item.get("name") == "token" and item.get("value"):
                return str(item["value"])
    raise AssertionError("Playwright storage state does not contain localStorage.token")


def _runtime_request_body(mode: str, command_kind: str) -> dict[str, Any]:
    marker = uuid4().hex
    return {
        "tenant_id": "tenant:web",
        "workspace_id": "workspace:agent-studio:web",
        "conversation_id": f"conversation:phase10-cutover-smoke:{mode}:{marker}",
        "client_request_id": f"client:phase10-cutover-smoke:{mode}:{marker}",
        "runtime_request_ref": f"runtime-request:phase10-cutover-smoke:{mode}:{marker}",
        "raw_intent_ref": f"intent:phase10-cutover-smoke:{mode}:{marker}",
        "command_kind": command_kind,
        "active_agent_version_id": "agent-version:web-default",
        "payload": {
            "goal": f"PHASE10 browser cutover smoke {mode}",
            "query": f"PHASE10 browser cutover smoke {mode}",
            "cutover_mode": mode,
            **({"rollback_reason": "product_runtime_cutover_rollback"} if mode == "rollback" else {}),
        },
    }


def _run_browser_smoke() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover - environment diagnostic path
        raise AssertionError("Python Playwright is required for browser full-e2e smoke") from exc

    token = _storage_token()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            context = browser.new_context(storage_state=str(AUTH_PATH))
            page = context.new_page()
            page.goto(f"{BASE_URL}/workspace", wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_selector(".workspace-container", timeout=20_000)
            page.wait_for_function("() => Boolean(window.localStorage.getItem('token'))", timeout=5_000)
            if "auth=login" in page.url or page.url.rstrip("/").endswith("/login"):
                raise AssertionError(f"Workspace redirected to login: {page.url}")

            catalog = page.evaluate(
                """async ({ token }) => {
                  const response = await fetch(
                    '/api/v1/product/agent-catalog?tenant_id=tenant%3Aweb&workspace_id=workspace%3Aagent-studio%3Aweb',
                    { headers: { Authorization: `Bearer ${token}` } }
                  )
                  const body = await response.json()
                  return { status: response.status, body }
                }""",
                {"token": token},
            )
            if catalog["status"] != 200:
                raise AssertionError(f"Product catalog request failed: {catalog}")
            entries = catalog["body"].get("data", {}).get("agent_catalog_entries")
            if not isinstance(entries, list):
                raise AssertionError(f"Product catalog payload missing entries: {catalog}")

            cutover = page.evaluate(
                """async ({ token, requests }) => {
                  const results = []
                  for (const request of requests) {
                    const response = await fetch('/api/v1/product/runtime-requests', {
                      method: 'POST',
                      headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify(request.body),
                    })
                    const body = await response.json()
                    results.push({
                      mode: request.mode,
                      command_kind: request.body.command_kind,
                      http_status: response.status,
                      status_code: body.status_code,
                      status_message: body.status_message || '',
                      receipt_status: body.data?.status || '',
                      command_id: body.data?.command_id || '',
                      projection_event_id: body.data?.projection?.projection_event_id || '',
                    })
                  }
                  return results
                }""",
                {
                    "token": token,
                    "requests": [
                        {
                            "mode": mode,
                            "body": _runtime_request_body(mode, command_kind),
                        }
                        for mode, command_kind in PRODUCT_CUTOVER_COMMANDS.items()
                    ] + [
                        {
                            "mode": "rollback",
                            "body": _runtime_request_body("rollback", "SUBMIT_USER_GOAL"),
                        }
                    ],
                },
            )
            by_mode = {item["mode"]: item for item in cutover}
            for mode, command_kind in PRODUCT_CUTOVER_COMMANDS.items():
                result = by_mode.get(mode)
                if not result:
                    raise AssertionError(f"Missing Product runtime cutover smoke result for {mode}: {cutover}")
                if result["http_status"] != 200 or result["status_code"] != 200:
                    raise AssertionError(f"Product runtime cutover {mode} request failed: {result}")
                if result["command_kind"] != command_kind:
                    raise AssertionError(f"Product runtime cutover {mode} used wrong command kind: {result}")
                if result["receipt_status"] not in {"ACCEPTED", "DUPLICATE"}:
                    raise AssertionError(f"Product runtime cutover {mode} did not return an accepted receipt: {result}")
                if not result["command_id"] or not result["projection_event_id"]:
                    raise AssertionError(f"Product runtime cutover {mode} missing receipt/projection evidence: {result}")

            rollback = by_mode.get("rollback")
            if not rollback:
                raise AssertionError(f"Missing Product runtime rollback smoke result: {cutover}")
            if rollback["http_status"] != 200 or rollback["status_code"] == 200:
                raise AssertionError(f"Product runtime rollback was not rejected fail-closed: {rollback}")
            if "Product runtime rollback mode is active" not in rollback["status_message"]:
                raise AssertionError(f"Product runtime rollback returned wrong failure: {rollback}")
        finally:
            browser.close()


def main() -> int:
    backend_health = _read_json_url(f"{API_URL}/health")
    qa_health = _read_json_url(f"{QA_API_URL}/health")
    if backend_health.get("status") != "OK":
        raise AssertionError(f"Backend health is not OK: {backend_health}")
    if qa_health.get("status") != "OK":
        raise AssertionError(f"QA API health is not OK: {qa_health}")
    _run_browser_smoke()
    print("full-e2e smoke passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"full-e2e smoke failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
