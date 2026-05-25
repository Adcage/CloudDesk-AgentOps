from app.agents.approval import _normalize_action, _extract_approval_id


def test_normalize_action_maps_refund_request_to_refund():
    assert _normalize_action("refund_request") == "refund"
    assert _normalize_action("refund") == "refund"


def test_extract_approval_id_reads_wrapped_java_response():
    wrapped = {
        "code": 0,
        "message": "ok",
        "data": {
            "approvalId": "A100",
        },
    }

    assert _extract_approval_id(wrapped) == "A100"
