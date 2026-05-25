from app.guardrails.pii_filter import detect_and_filter_pii


def test_email_is_hidden():
    filtered_text, detections = detect_and_filter_pii("请发送邮件到 user@example.com 获取更多信息。")

    assert "user@example.com" not in filtered_text
    assert "[已隐藏]" in filtered_text
    assert detections[0]["type"] == "email"


def test_phone_is_hidden():
    filtered_text, detections = detect_and_filter_pii("请联系客服电话 13812345678 或 010-12345678。")

    assert "13812345678" not in filtered_text
    assert "010-12345678" not in filtered_text
    assert len(detections) >= 2


def test_clean_text_is_unchanged():
    filtered_text, detections = detect_and_filter_pii("您的订单已处理，请查看邮件。")

    assert filtered_text == "您的订单已处理，请查看邮件。"
    assert detections == []
