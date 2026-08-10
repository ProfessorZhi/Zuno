from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_workspace_page_submits_to_product_projection_loop() -> None:
    page = (REPO_ROOT / "apps/web/src/pages/workspace/defaultPage/defaultPage.vue").read_text(
        encoding="utf-8"
    )

    for phrase in (
        "submitWorkspacePayloadToProductRuntime",
        "connectProductRuntimeProjectionStream",
        "consumeProductStoreAction",
        "submitProductFeedback",
        "downloadProductArtifact",
    ):
        assert phrase in page


def test_frontend_runtime_builder_has_no_switchable_runtime_mode() -> None:
    runtime = (REPO_ROOT / "apps/web/src/product/runtime.ts").read_text(encoding="utf-8")

    assert "submitProductRuntimeRequest(command)" in runtime
    assert "command_kind" not in runtime
    assert "ProductRuntimeCutoverMode" not in runtime
    assert "zuno.productRuntimeCutoverMode" not in runtime
