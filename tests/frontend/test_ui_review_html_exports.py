from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_ui_review_html_exports_exist_with_expected_fields():
    dashboard = (
        REPO_ROOT / "docs" / "history" / "ui-review" / "settings-shell-dashboard.html"
    ).read_text(encoding="utf-8")
    knowledge = (
        REPO_ROOT / "docs" / "history" / "ui-review" / "settings-shell-knowledge-config.html"
    ).read_text(encoding="utf-8")
    index = (
        REPO_ROOT / "docs" / "history" / "ui-review" / "settings-shell-pages-index.html"
    ).read_text(encoding="utf-8")

    assert "数据看板" in dashboard
    assert "deepseek-v4-flash" in dashboard
    assert "全部模型" in dashboard

    assert "知识库配置" in knowledge
    assert "mixed_tuning_v2_graph_tuned11" in knowledge
    assert "text-embedding-v4" in knowledge
    assert "保存并重建索引" in knowledge

    assert "Zuno 设置区 HTML 导出" in index
    assert "settings-shell-dashboard.html" in index
    assert "settings-shell-knowledge-config.html" in index
