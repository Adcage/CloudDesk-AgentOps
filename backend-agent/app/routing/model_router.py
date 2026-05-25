from __future__ import annotations

from collections import deque
from pathlib import Path

import yaml

from app.core.config import settings


class DynamicModelRouter:
    def __init__(self, config_path: str | None = None):
        base_dir = Path(__file__).resolve().parents[2]
        self.config_path = Path(config_path) if config_path else base_dir / "config" / "model_routing.yaml"
        with self.config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        self.tiers = config.get("tiers", {})
        self.budget = config.get("budget", {})
        self.task_tier_map = config.get("task_tier_map", {})
        self.latency_window: dict[str, deque[int]] = {}
        self.daily_cost = 0.0

    def route(self, task_type: str, complexity: int, risk_level: str, trace_id: str) -> dict:
        del trace_id
        tier = self.task_tier_map.get(task_type, "medium")
        reasoning = [f"task={task_type}", f"base={tier}"]

        if complexity > 7:
            upgraded = self._shift_tier(tier, 1)
            if upgraded != tier:
                reasoning.append(f"complexity={complexity}: {tier}->{upgraded}")
                tier = upgraded

        if (risk_level or "low").lower() == "high" and tier == "fast":
            reasoning.append("risk=high: fast->medium")
            tier = "medium"

        if self._is_latency_unhealthy(tier):
            degraded = self._shift_tier(tier, -1)
            if degraded != tier:
                reasoning.append(f"latency_failover: {tier}->{degraded}")
                tier = degraded

        budget_protection = False
        daily_limit = float(self.budget.get("daily_limit_usd", 5.0))
        if self.daily_cost > daily_limit * 0.8:
            degraded = self._shift_tier(tier, -1)
            if degraded != tier:
                reasoning.append(f"budget_protection: {tier}->{degraded}")
                tier = degraded
                budget_protection = True

        model_info = self.tiers.get(tier, {})
        return {
            "tier": tier,
            "model": model_info.get("model", settings.llm_model_medium),
            "reasoning": " | ".join(reasoning),
            "budget_protection": budget_protection,
        }

    def record_latency(self, model_name: str, latency_ms: int) -> None:
        if model_name not in self.latency_window:
            self.latency_window[model_name] = deque(maxlen=10)
        self.latency_window[model_name].append(latency_ms)

    def record_cost(self, model_name: str, tokens: int) -> None:
        for tier_info in self.tiers.values():
            if tier_info.get("model") == model_name:
                self.daily_cost += (tokens / 1000) * float(tier_info.get("cost_per_1k", 0))
                break

    def _shift_tier(self, tier: str, direction: int) -> str:
        order = ["fast", "medium", "strong"]
        if tier not in order:
            return "medium"
        index = max(0, min(len(order) - 1, order.index(tier) + direction))
        return order[index]

    def _is_latency_unhealthy(self, tier: str) -> bool:
        model_info = self.tiers.get(tier, {})
        model_name = model_info.get("model")
        max_latency_ms = float(model_info.get("max_latency_ms", 0))
        if not model_name or max_latency_ms <= 0:
            return False

        history = self.latency_window.get(model_name)
        if not history:
            return False

        average_latency = sum(history) / len(history)
        return average_latency > max_latency_ms * 1.5


_router: DynamicModelRouter | None = None


def get_router() -> DynamicModelRouter:
    global _router
    if _router is None:
        _router = DynamicModelRouter()
    return _router


def select_model(task_type: str, complexity: int = 5, risk_level: str = "low", trace_id: str = "") -> str:
    return get_router().route(task_type, complexity=complexity, risk_level=risk_level, trace_id=trace_id)["model"]
