from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


BASE_URL = os.getenv("ZUNO_FULL_E2E_BASE", "http://127.0.0.1:8090").rstrip("/")
API_URL = os.getenv("ZUNO_FULL_E2E_API", "http://127.0.0.1:7860").rstrip("/")
QA_API_URL = os.getenv("ZUNO_FULL_E2E_QA_API", "http://127.0.0.1:9101").rstrip("/")
AUTH_PATH = Path(os.getenv("ZUNO_FULL_E2E_AUTH", "auth.json"))


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
