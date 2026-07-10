from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_llm_api_exposes_activate_endpoint():
    content = (REPO_ROOT / "apps" / "web" / "src" / "apis" / "llm.ts").read_text(encoding="utf-8")

    assert "export interface ActivateLLMRequest" in content
    assert "export function activateLLMAPI" in content
    assert "/api/v1/llm/activate" in content


def test_model_page_exposes_conversation_model_activation_and_close_action():
    content = (REPO_ROOT / "apps" / "web" / "src" / "pages" / "model" / "model.vue").read_text(encoding="utf-8")

    assert "activateLLMAPI" in content
    assert "聊天模型" in content
    assert "工具调用模型" in content
    assert "推理模型" in content
    assert "文本 Embedding" in content
    assert "Rerank" in content
    assert "设为${slot.label}" in content
    assert "deepseek-v4-flash" in content
    assert "closeInlineForm" in content
    assert "title=\"关闭\"" in content
