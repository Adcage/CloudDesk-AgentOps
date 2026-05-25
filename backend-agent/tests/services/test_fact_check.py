from unittest.mock import patch

from app.guardrails.fact_check import check_factual_claims


def test_valid_document_citation_passes():
    with patch("app.guardrails.fact_check._document_exists", return_value=True):
        passed, violations = check_factual_claims("根据 refund_policy.md，重复扣费属于可退款场景。")

    assert passed is True
    assert violations == []


def test_fake_document_citation_fails():
    with patch("app.guardrails.fact_check._document_exists", return_value=False):
        passed, violations = check_factual_claims("根据 fake_policy_doc_v99.md，用户可以无限退款。")

    assert passed is False
    assert violations == ["fake_policy_doc_v99.md"]


def test_no_citation_passes():
    passed, violations = check_factual_claims("您好，请问有什么可以帮助您的？")

    assert passed is True
    assert violations == []
