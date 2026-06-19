from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
GALLERY_ROOT = REPO_ROOT / "docs" / "ui-gallery" / "knowledge-product-refactor-deep-graphrag-v1"
BASELINE_COMMIT = "8b44326"

PAGES: list[dict[str, str]] = [
    {
        "page_name": "domain-pack-list",
        "route": "/workspace/settings/knowledge/domain-packs",
        "component_path": "apps/web/src/pages/knowledge/domain-pack-list.vue",
        "html_file": "domain-pack-list.html",
        "notes": "领域包作为独立资源展示；创建入口在列表页。",
    },
    {
        "page_name": "domain-pack-create",
        "route": "/workspace/settings/knowledge/domain-packs/create",
        "component_path": "apps/web/src/pages/knowledge/domain-pack-create.vue",
        "html_file": "domain-pack-create.html",
        "notes": "领域包构建页强调样本文件、schema/prompt 审核、发布步骤。",
    },
    {
        "page_name": "domain-pack-detail",
        "route": "/workspace/settings/knowledge/domain-packs/contract-review-v1",
        "component_path": "apps/web/src/pages/knowledge/domain-pack-detail.vue",
        "html_file": "domain-pack-detail.html",
        "notes": "详情页聚焦领域包本体，不直接承担知识库维护职责。",
    },
    {
        "page_name": "knowledge-create-wizard",
        "route": "/workspace/settings/knowledge/create",
        "component_path": "apps/web/src/pages/knowledge/knowledge-create.vue",
        "html_file": "knowledge-create-wizard.html",
        "notes": "产品层只暴露标准检索与增强检索，不直接暴露内部 runtime 模式。",
    },
    {
        "page_name": "knowledge-maintenance",
        "route": "/workspace/settings/knowledge/kb-contract-review/settings?name=%E5%90%88%E5%90%8C%E5%AE%A1%E6%9F%A5%E7%9F%A5%E8%AF%86%E5%BA%93",
        "component_path": "apps/web/src/pages/knowledge/knowledge-settings.vue",
        "html_file": "knowledge-maintenance.html",
        "notes": "维护页展示模型、索引、图谱、社区与重建动作，用产品词汇表达能力。",
    },
    {
        "page_name": "legacy-knowledge-config-route",
        "route": "/workspace/settings/knowledge/kb-contract-review/config?name=%E5%90%88%E5%90%8C%E5%AE%A1%E6%9F%A5%E7%9F%A5%E8%AF%86%E5%BA%93",
        "component_path": "apps/web/src/pages/knowledge/knowledge-settings.vue",
        "html_file": "legacy-knowledge-config-route.html",
        "notes": "旧 config 路由仍保留，但当前用户路径已收口到 settings 页面。",
    },
]

VIEWPORTS: list[tuple[str, dict[str, int]]] = [
    ("desktop", {"width": 1440, "height": 1000}),
    ("tablet", {"width": 1024, "height": 900}),
    ("mobile", {"width": 390, "height": 844}),
]


def build_mock_payloads() -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    knowledge_config: dict[str, Any] = {
        "index_capability": "rag_graph",
        "domain_pack_id": "contract_review_v1",
        "eval_profile_id": "local_eval_contract",
        "model_refs": {
            "text_embedding_model_id": "embed-text-v4",
            "vl_embedding_model_id": "embed-vl-v4",
            "rerank_model_id": "rerank-gte-v2",
        },
        "index_settings": {
            "chunk_mode": "general",
            "chunk_size": 1024,
            "overlap": 120,
            "separator": "\n\n",
            "replace_consecutive_spaces": True,
            "remove_urls_emails": False,
            "image_indexing_mode": "dual",
            "vector_backend": "milvus",
            "index_version": "idx-2026-06-19",
            "status": "active",
            "health_status": "ready",
        },
        "graph_index_settings": {
            "entity_extraction_mode": "rule_llm",
            "relation_schema": "typed",
            "entity_normalization": True,
            "evidence_backlink": True,
            "use_rag_entry_chunk": True,
            "community_report_prompt_id": "community-contract-v1",
            "index_version": "graph-2026-06-19",
            "health_status": "ready",
            "graph_index_status": "ready",
            "community_detection_status": "stale",
            "community_report_status": "ready",
            "community_version": "community-2026-06-19",
        },
        "retrieval_settings": {
            "default_mode": "rag_graph",
            "profile": "balanced",
            "refill_policy": "smart",
            "top_k": 8,
            "rerank_enabled": True,
            "rerank_top_k": 20,
            "score_threshold": 0.42,
            "graph_hop_limit": 2,
            "max_paths_per_entity": 5,
        },
    }
    knowledge_list = [
        {
            "id": "kb-contract-review",
            "name": "合同审查知识库",
            "description": "用于 UI 审查的模拟知识库",
            "user_id": "audit",
            "create_time": "2026-06-19T00:00:00",
            "update_time": "2026-06-19T00:00:00",
            "count": 12,
            "file_size": "18 MB",
            "processing_count": 0,
            "failed_count": 0,
            "completed_count": 12,
            "knowledge_config": knowledge_config,
        }
    ]
    llm_data = {
        "Embedding": [
            {
                "llm_id": "embed-text-v4",
                "model": "text-embedding-v4",
                "provider": "DashScope",
                "llm_type": "Embedding",
                "base_url": "https://api.example.com",
                "api_key": "",
                "user_id": "audit",
                "create_time": "2026-06-19T00:00:00",
                "update_time": "2026-06-19T00:00:00",
            },
            {
                "llm_id": "embed-vl-v4",
                "model": "vl-embedding-v4",
                "provider": "DashScope",
                "llm_type": "Embedding",
                "base_url": "https://api.example.com",
                "api_key": "",
                "user_id": "audit",
                "create_time": "2026-06-19T00:00:00",
                "update_time": "2026-06-19T00:00:00",
            },
        ],
        "Rerank": [
            {
                "llm_id": "rerank-gte-v2",
                "model": "gte-rerank-v2",
                "provider": "DashScope",
                "llm_type": "Rerank",
                "base_url": "https://api.example.com",
                "api_key": "",
                "user_id": "audit",
                "create_time": "2026-06-19T00:00:00",
                "update_time": "2026-06-19T00:00:00",
            }
        ],
    }
    return knowledge_list, llm_data


def api_body(url: str) -> dict[str, Any]:
    knowledge_list, llm_data = build_mock_payloads()
    domain_packs = [
        {
            "pack_id": "contract-review-v1",
            "name": "合同审查",
            "version": "0.1.0",
            "description": "合同条款问答、风险识别和引用溯源模板。",
            "status": "published",
        }
    ]
    if url.endswith("/api/v1/knowledge/select"):
        return {"status_code": 200, "status_message": "ok", "data": knowledge_list}
    if url.endswith("/api/v1/domain-packs"):
        return {"status_code": 200, "status_message": "ok", "data": domain_packs}
    if url.endswith("/api/v1/domain-packs/draft") or url.endswith("/api/v1/domain-packs/draft/from-knowledge"):
        return {"status_code": 200, "status_message": "ok", "data": {"pack_id": "contract-review-v1", "status": "draft"}}
    if "/api/v1/domain-packs/" in url and url.endswith("/publish"):
        return {"status_code": 200, "status_message": "ok", "data": {**domain_packs[0], "status": "published"}}
    if "/api/v1/domain-packs/" in url:
        return {
            "status_code": 200,
            "status_message": "ok",
            "data": {
                **domain_packs[0],
                "schema_data": {"entities": ["Party", "Clause"], "relations": ["HAS_OBLIGATION"]},
                "retrieval_policy_data": {"graph_hop_limit": 2, "max_paths_per_entity": 5},
                "extraction_prompt_text": "Extract contract entities and evidence.",
            },
        }
    if "/api/v1/knowledge/kb-contract-review/config/impact" in url:
        return {
            "status_code": 200,
            "status_message": "ok",
            "data": {
                "changed_fields": [],
                "immediate_effect_fields": [],
                "text_reindex_required": False,
                "image_reindex_required": False,
                "bm25_reindex_required": False,
                "graph_update_required": False,
                "community_detection_required": False,
                "community_report_required": False,
                "full_rebuild_required": False,
                "recommended_action": "save_only",
            },
        }
    if url.endswith("/api/v1/knowledge/kb-contract-review/config"):
        return {"status_code": 200, "status_message": "ok", "data": knowledge_list[0]["knowledge_config"]}
    if "/api/v1/knowledge/kb-contract-review/reindex/" in url:
        action = url.rsplit("/", 1)[-1]
        return {"status_code": 200, "status_message": "ok", "data": {"knowledge_id": "kb-contract-review", "action": action, "status": "accepted"}}
    if url.endswith("/api/v1/knowledge/create"):
        return {
            "status_code": 200,
            "status_message": "ok",
            "data": {
                "id": "kb-new-product-wiring",
                "name": "新知识库",
                "description": "用于 Product Wiring V1 的知识库说明。",
                "knowledge_config": knowledge_list[0]["knowledge_config"],
            },
        }
    if url.endswith("/api/v1/llm/visible"):
        return {"status_code": 200, "status_message": "ok", "data": llm_data}
    if url.endswith("/api/v1/knowledge/update"):
        return {"status_code": 200, "status_message": "ok", "data": None}
    if url.endswith("/api/v1/knowledge_file/select"):
        return {"status_code": 200, "status_message": "ok", "data": []}
    if url.endswith("/api/v1/knowledge_file/reindex"):
        return {
            "status_code": 200,
            "status_message": "ok",
            "data": {
                "summary": {
                    "knowledge_id": "kb-contract-review",
                    "total_files": 12,
                    "created_tasks": 12,
                    "dispatched_tasks": 12,
                    "failed_tasks": 0,
                },
                "task_ids": [],
                "file_ids": [],
            },
        }
    if "/api/v1/workspace/execution-modes" in url:
        return {"status_code": 200, "status_message": "ok", "data": {"modes": [], "access_scopes": []}}
    if "/api/v1/workspace/session/info" in url:
        return {"status_code": 200, "status_message": "ok", "data": None}
    return {"status_code": 200, "status_message": "ok", "data": []}


def prepare_page(page: Page, base_url: str, target_route: str) -> None:
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
        localStorage.setItem('token', 'audit-token')
        localStorage.setItem('userInfo', JSON.stringify({ id: 'audit', username: 'audit' }))
        localStorage.setItem('zuno.workspace.settingsUiMode', 'traditional')
        """
    )
    page.goto(base_url, wait_until="networkidle", timeout=30000)
    page.evaluate(
        """
        (route) => {
          history.pushState({}, '', route)
          window.dispatchEvent(new PopStateEvent('popstate'))
        }
        """,
        target_route,
    )
    page.wait_for_timeout(3500)


def current_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).decode().strip()


def write_readme(commit_sha: str, generated_at: str) -> None:
    readme = f"""# Knowledge Product Refactor + Deep GraphRAG V1 UI Snapshot Audit

- Generated at: {generated_at}
- Commit SHA: `{commit_sha}`
- Previous baseline commit: `{BASELINE_COMMIT}`
- Capture method: load root preview page, navigate client-side to target routes, intercept `/api/**` with audit-safe mock data, then export screenshots and HTML snapshots.
- This is the responsive hardening after snapshot for tablet/mobile settings shell layout.

## Pages

- `domain-pack-list`: 领域包列表页
- `domain-pack-create`: 领域包创建页
- `domain-pack-detail`: 领域包详情页
- `knowledge-create-wizard`: 知识库创建向导
- `knowledge-maintenance`: 知识库维护页
- `legacy-knowledge-config-route`: 旧配置路由对比快照（当前会收口到 settings 页面）

## Viewports

- desktop: `1440x1000`
- tablet: `1024x900`
- mobile: `390x844`

## Focus

- 修复 tablet/mobile 下 settings shell 的布局压缩问题
- 让主内容优先可见，避免横向滚动和主内容掉到首屏之外
- 保持产品层文案只暴露“标准检索 / 增强检索”
"""
    (GALLERY_ROOT / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:4175/")
    args = parser.parse_args()

    for subdir in ("desktop", "tablet", "mobile"):
        (GALLERY_ROOT / "screenshots" / subdir).mkdir(parents=True, exist_ok=True)
    (GALLERY_ROOT / "html").mkdir(parents=True, exist_ok=True)

    commit_sha = current_commit()
    generated_at = datetime.now(timezone.utc).isoformat()
    manifest: list[dict[str, Any]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for page_def in PAGES:
            html_written = False
            html_rel = f"html/{page_def['html_file']}"
            for viewport_name, viewport in VIEWPORTS:
                page = browser.new_page(
                    viewport=viewport,
                    device_scale_factor=1,
                    is_mobile=viewport_name == "mobile",
                )
                prepare_page(page, args.base_url, page_def["route"])
                shot_name = f"{page_def['page_name']}-{viewport_name}.png"
                shot_rel = f"screenshots/{viewport_name}/{shot_name}"
                page.screenshot(path=str(GALLERY_ROOT / shot_rel), full_page=True)
                if not html_written:
                    (GALLERY_ROOT / html_rel).write_text(page.content(), encoding="utf-8")
                    html_written = True
                manifest.append(
                    {
                        "commit_sha": commit_sha,
                        "generated_at": generated_at,
                        "page_name": page_def["page_name"],
                        "route": page_def["route"],
                        "component_path": page_def["component_path"],
                        "viewport": viewport,
                        "screenshot_path": shot_rel.replace("\\", "/"),
                        "html_path": html_rel.replace("\\", "/"),
                        "notes": page_def["notes"],
                    }
                )
                page.close()
        browser.close()

    (GALLERY_ROOT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(commit_sha, generated_at)


if __name__ == "__main__":
    main()
