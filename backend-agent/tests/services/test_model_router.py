from collections import deque

import yaml

from app.routing.model_router import DynamicModelRouter


def _write_router_config(path):
    path.write_text(
        yaml.safe_dump(
            {
                "tiers": {
                    "fast": {"model": "fast-model", "cost_per_1k": 0.001, "max_latency_ms": 500},
                    "medium": {"model": "medium-model", "cost_per_1k": 0.003, "max_latency_ms": 1500},
                    "strong": {"model": "strong-model", "cost_per_1k": 0.01, "max_latency_ms": 3000},
                },
                "budget": {"daily_limit_usd": 5.0},
                "task_tier_map": {
                    "intent_classification": "fast",
                    "policy_qa": "medium",
                    "compliance_check": "strong",
                },
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def test_route_uses_task_tier_map(tmp_path):
    config_path = tmp_path / "model_routing.yaml"
    _write_router_config(config_path)
    router = DynamicModelRouter(str(config_path))

    result = router.route("intent_classification", complexity=3, risk_level="low", trace_id="TR_1")

    assert result["tier"] == "fast"
    assert result["model"] == "fast-model"


def test_route_upgrades_when_complexity_high(tmp_path):
    config_path = tmp_path / "model_routing.yaml"
    _write_router_config(config_path)
    router = DynamicModelRouter(str(config_path))

    result = router.route("intent_classification", complexity=8, risk_level="low", trace_id="TR_2")

    assert result["tier"] == "medium"


def test_route_enforces_minimum_medium_for_high_risk(tmp_path):
    config_path = tmp_path / "model_routing.yaml"
    _write_router_config(config_path)
    router = DynamicModelRouter(str(config_path))

    result = router.route("intent_classification", complexity=3, risk_level="high", trace_id="TR_3")

    assert result["tier"] == "medium"


def test_route_downgrades_on_budget_pressure(tmp_path):
    config_path = tmp_path / "model_routing.yaml"
    _write_router_config(config_path)
    router = DynamicModelRouter(str(config_path))
    router.daily_cost = 4.2

    result = router.route("compliance_check", complexity=5, risk_level="low", trace_id="TR_4")

    assert result["tier"] == "medium"
    assert result["budget_protection"] is True


def test_route_failover_uses_lower_tier_when_latency_too_high(tmp_path):
    config_path = tmp_path / "model_routing.yaml"
    _write_router_config(config_path)
    router = DynamicModelRouter(str(config_path))
    router.latency_window["medium-model"] = deque([2600, 2500, 2700], maxlen=10)

    result = router.route("policy_qa", complexity=5, risk_level="low", trace_id="TR_5")

    assert result["tier"] == "fast"
