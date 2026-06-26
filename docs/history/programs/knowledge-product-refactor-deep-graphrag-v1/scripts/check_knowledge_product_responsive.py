from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from capture_knowledge_product_ui_gallery import prepare_page


@dataclass
class CheckCase:
    name: str
    route: str
    viewport: dict[str, int]
    page_selector: str
    expectations: list[str]


CASES = [
    CheckCase(
        name="tablet-create-shell",
        route="/workspace/settings/knowledge/create",
        viewport={"width": 1024, "height": 900},
        page_selector=".knowledge-create-page",
        expectations=[
            "tablet sidebar width should be compact",
            "tablet main content should fit viewport without horizontal overflow",
        ],
    ),
    CheckCase(
        name="mobile-create-shell",
        route="/workspace/settings/knowledge/create",
        viewport={"width": 390, "height": 844},
        page_selector=".knowledge-create-page",
        expectations=[
            "mobile page content should be visible in first viewport",
            "mobile should not horizontally overflow",
            "mobile sidebar should not occupy most of the first screen",
        ],
    ),
    CheckCase(
        name="mobile-maintenance-shell",
        route="/workspace/settings/knowledge/kb-contract-review/settings?name=%E5%90%88%E5%90%8C%E5%AE%A1%E6%9F%A5%E7%9F%A5%E8%AF%86%E5%BA%93",
        viewport={"width": 390, "height": 844},
        page_selector=".knowledge-settings-page",
        expectations=[
            "maintenance page content should be visible in first viewport",
            "maintenance page should not horizontally overflow",
        ],
    ),
]


def collect_metrics(page: Page, page_selector: str) -> dict[str, float | bool]:
    return page.evaluate(
        """
        ({ pageSelector }) => {
          const root = document.querySelector(pageSelector)
          const sidebar = document.querySelector('.settings-shell-sidebar')
          const content = document.querySelector('.settings-shell-content')
          if (!root || !sidebar || !content) {
            throw new Error(`Missing required element for ${pageSelector}`)
          }
          const rootRect = root.getBoundingClientRect()
          const sidebarRect = sidebar.getBoundingClientRect()
          const contentRect = content.getBoundingClientRect()
          return {
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight,
            scrollWidth: document.documentElement.scrollWidth,
            rootTop: rootRect.top,
            rootRight: rootRect.right,
            rootWidth: rootRect.width,
            sidebarWidth: sidebarRect.width,
            sidebarHeight: sidebarRect.height,
            contentTop: contentRect.top,
            contentWidth: contentRect.width,
          }
        }
        """,
        {"pageSelector": page_selector},
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:4175/")
    args = parser.parse_args()

    failures: list[dict[str, object]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for case in CASES:
            page = browser.new_page(
                viewport=case.viewport,
                device_scale_factor=1,
                is_mobile=case.viewport["width"] < 768,
            )
            prepare_page(page, args.base_url, case.route)
            metrics = collect_metrics(page, case.page_selector)
            page.close()

            case_failures: list[str] = []
            if case.viewport["width"] == 1024 and float(metrics["sidebarWidth"]) > 220:
                case_failures.append(
                    f"tablet sidebar width is {metrics['sidebarWidth']:.1f}px, expected <= 220px"
                )
            if float(metrics["scrollWidth"]) > float(metrics["viewportWidth"]) + 1:
                case_failures.append(
                    f"horizontal overflow detected: scrollWidth={metrics['scrollWidth']}, viewportWidth={metrics['viewportWidth']}"
                )
            if case.viewport["width"] == 390:
                if float(metrics["rootTop"]) > 260:
                    case_failures.append(
                        f"page root starts too low on mobile: top={metrics['rootTop']:.1f}px"
                    )
                if float(metrics["sidebarHeight"]) > 240:
                    case_failures.append(
                        f"mobile sidebar occupies too much height: {metrics['sidebarHeight']:.1f}px"
                    )
            if case.viewport["width"] == 1024 and float(metrics["rootRight"]) > float(metrics["viewportWidth"]) - 12:
                case_failures.append(
                    f"tablet content nearly clips viewport: rootRight={metrics['rootRight']:.1f}px"
                )

            if case_failures:
                failures.append(
                    {
                        "case": case.name,
                        "route": case.route,
                        "expectations": case.expectations,
                        "metrics": metrics,
                        "failures": case_failures,
                    }
                )
        browser.close()

    if failures:
        print(json.dumps({"status": "failed", "failures": failures}, ensure_ascii=False, indent=2))
        raise SystemExit(1)

    print(json.dumps({"status": "passed", "checked_cases": [case.name for case in CASES]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
