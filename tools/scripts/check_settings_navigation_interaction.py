from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from capture_knowledge_product_ui_gallery import api_body


FORBIDDEN_TERMS = [
    "rag_graph_deep",
    "community_global",
    "drift_like",
]


@dataclass
class ViewportCase:
    name: str
    viewport: dict[str, int]


CASES = [
    ViewportCase("desktop", {"width": 1440, "height": 1000}),
    ViewportCase("tablet", {"width": 1024, "height": 900}),
    ViewportCase("mobile", {"width": 390, "height": 844}),
]


def install_mock_api(page: Page) -> None:
    page.route(
        "**/api/**",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(api_body(route.request.url), ensure_ascii=False),
        ),
    )
    page.add_init_script(
        """
        localStorage.setItem('token', 'interaction-audit-token')
        localStorage.setItem('userInfo', JSON.stringify({ id: 'interaction-audit', username: 'interaction-audit' }))
        localStorage.setItem('zuno.workspace.settingsUiMode', 'traditional')
        localStorage.setItem('zuno.workspace.sidebarCollapsed', 'false')
        """
    )


def goto_workspace(page: Page, base_url: str) -> None:
    workspace_url = urljoin(base_url.rstrip("/") + "/", "workspace")
    page.goto(workspace_url, wait_until="networkidle", timeout=30000)
    page.wait_for_selector(".workspace-container", timeout=15000)


def click_settings_entry(page: Page, is_mobile: bool) -> None:
    if is_mobile:
        toggle = page.locator(".mobile-rail-toggle")
        if toggle.is_visible(timeout=3000):
            toggle.click()
            page.wait_for_timeout(250)

    settings_entry = page.locator(".settings-entry").first
    settings_entry.wait_for(state="visible", timeout=10000)
    settings_entry.click()
    page.wait_for_selector(".settings-shell-page", timeout=10000)


def click_shell_nav(page: Page, label: str) -> None:
    nav = page.locator(".settings-shell-sidebar .settings-shell-nav", has_text=label).first
    nav.wait_for(state="visible", timeout=10000)
    nav.click()


def click_detail_back(page: Page) -> None:
    back = page.locator(".settings-shell-detail-back").first
    back.wait_for(state="visible", timeout=10000)
    back.click()


def wait_for_page(page: Page, selector: str) -> None:
    page.locator(selector).first.wait_for(state="visible", timeout=10000)


def assert_visible_text(page: Page, text: str) -> None:
    page.get_by_text(text, exact=False).first.wait_for(state="visible", timeout=10000)


def metrics(page: Page, selector: str) -> dict[str, object]:
    return page.evaluate(
        """
        ({ selector, forbiddenTerms }) => {
          const root = document.querySelector(selector)
          const shell = document.querySelector('.settings-shell-page')
          const content = document.querySelector('.settings-shell-content')
          const activeNav = Array.from(document.querySelectorAll('.settings-shell-nav.active'))
            .map((item) => item.textContent.trim())
          if (!root || !shell || !content) {
            throw new Error(`Missing shell content for ${selector}`)
          }
          const rootRect = root.getBoundingClientRect()
          const shellRect = shell.getBoundingClientRect()
          const contentRect = content.getBoundingClientRect()
          const bodyText = document.body.innerText
          return {
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight,
            scrollWidth: document.documentElement.scrollWidth,
            shellWidth: shellRect.width,
            contentWidth: contentRect.width,
            rootTop: rootRect.top,
            rootBottom: rootRect.bottom,
            activeNav,
            forbiddenTerms: forbiddenTerms.filter((term) => bodyText.includes(term)),
          }
        }
        """,
        {"selector": selector, "forbiddenTerms": FORBIDDEN_TERMS},
    )


def validate_layout(page: Page, selector: str, case: ViewportCase) -> list[str]:
    current = metrics(page, selector)
    failures: list[str] = []
    if float(current["scrollWidth"]) > float(current["viewportWidth"]) + 1:
        failures.append(
            f"horizontal overflow: scrollWidth={current['scrollWidth']}, viewportWidth={current['viewportWidth']}"
        )
    if case.name == "mobile" and float(current["rootTop"]) > 260:
        failures.append(f"mobile main content starts too low: rootTop={float(current['rootTop']):.1f}")
    if "知识库" not in "".join(current["activeNav"]):
        failures.append(f"knowledge nav is not active: activeNav={current['activeNav']}")
    if current["forbiddenTerms"]:
        failures.append(f"forbidden runtime terms are visible: {current['forbiddenTerms']}")
    return failures


def run_case(page: Page, base_url: str, case: ViewportCase) -> dict[str, object]:
    failures: list[str] = []
    is_mobile = case.viewport["width"] < 768
    install_mock_api(page)
    goto_workspace(page, base_url)

    try:
        click_settings_entry(page, is_mobile)
        click_shell_nav(page, "知识库")
        wait_for_page(page, ".knowledge-page")
        failures.extend(validate_layout(page, ".knowledge-page", case))

        create_button = page.locator(".knowledge-page [title='新建知识库']").first
        create_button.wait_for(state="visible", timeout=10000)
        create_button.click()
        wait_for_page(page, ".knowledge-create-page")
        assert_visible_text(page, "标准检索")
        assert_visible_text(page, "增强检索")
        failures.extend(validate_layout(page, ".knowledge-create-page", case))

        click_detail_back(page)
        wait_for_page(page, ".knowledge-page")

        config_button = page.locator(".knowledge-page [aria-label='参数配置']").first
        config_button.wait_for(state="visible", timeout=10000)
        config_button.click()
        wait_for_page(page, ".knowledge-settings-page")
        failures.extend(validate_layout(page, ".knowledge-settings-page", case))

        click_detail_back(page)
        wait_for_page(page, ".knowledge-page")

        domain_pack_button = page.locator(".knowledge-page [title='领域包']").first
        domain_pack_button.wait_for(state="visible", timeout=10000)
        domain_pack_button.click()
        wait_for_page(page, ".domain-pack-page")
        failures.extend(validate_layout(page, ".domain-pack-page", case))

        page.get_by_role("button", name="创建新的领域包").click()
        wait_for_page(page, ".domain-pack-create-page")
        failures.extend(validate_layout(page, ".domain-pack-create-page", case))

        click_detail_back(page)
        wait_for_page(page, ".knowledge-page")
        page.locator(".knowledge-page [title='领域包']").first.click()
        wait_for_page(page, ".domain-pack-page")
        page.locator(".pack-card").first.click()
        wait_for_page(page, ".domain-pack-detail-page")
        failures.extend(validate_layout(page, ".domain-pack-detail-page", case))
    except PlaywrightTimeoutError as exc:
        failures.append(f"interaction timed out: {exc}")

    return {
        "case": case.name,
        "viewport": case.viewport,
        "status": "failed" if failures else "passed",
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:4177/")
    args = parser.parse_args()

    results: list[dict[str, object]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for case in CASES:
            page = browser.new_page(
                viewport=case.viewport,
                device_scale_factor=1,
                is_mobile=case.viewport["width"] < 768,
            )
            results.append(run_case(page, args.base_url, case))
            page.close()
        browser.close()

    failed = [result for result in results if result["status"] != "passed"]
    print(json.dumps({"status": "failed" if failed else "passed", "results": results}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
