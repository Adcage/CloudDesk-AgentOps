from app.prompts.versions import CURRENT_VERSIONS, load_prompt


def test_load_prompt_returns_text_and_version():
    text, version = load_prompt("billing")

    assert version == CURRENT_VERSIONS["billing"]
    assert "账单" in text or "退款" in text
