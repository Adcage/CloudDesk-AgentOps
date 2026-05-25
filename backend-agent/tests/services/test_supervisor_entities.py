from app.agents.supervisor import _extract_entities_by_regex


def test_extract_entities_keeps_full_order_id():
    entities = _extract_entities_by_regex("客户 C002 的订单 O1002 被重复扣费了，帮我处理")

    assert entities["customer_id"] == "C002"
    assert entities["order_id"] == "O1002"


def test_extract_entities_reads_amount_from_dollar_amount():
    entities = _extract_entities_by_regex("客户C002要求退款$200，订单号O1003，需要审批吗？")

    assert entities["customer_id"] == "C002"
    assert entities["order_id"] == "O1003"
    assert entities["amount"] == 200.0


def test_extract_entities_reads_amount_without_currency_symbol():
    entities = _extract_entities_by_regex("客户C002要求退款200，订单号O1003，需要审批吗？")

    assert entities["customer_id"] == "C002"
    assert entities["order_id"] == "O1003"
    assert entities["amount"] == 200.0


def test_regex_result_should_be_preferred_over_llm_guess():
    regex_entities = _extract_entities_by_regex("客户C002要求退款200，订单号O1003，需要审批吗？")
    llm_entities = {"customer_id": None, "order_id": "O003", "amount": 2}

    merged = {
        "customer_id": regex_entities.get("customer_id") or llm_entities.get("customer_id"),
        "order_id": regex_entities.get("order_id") or llm_entities.get("order_id"),
        "amount": regex_entities.get("amount") if regex_entities.get("amount") is not None else llm_entities.get("amount"),
    }

    assert merged == {"customer_id": "C002", "order_id": "O1003", "amount": 200.0}
