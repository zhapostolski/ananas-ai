"""Promo Simulator Agent — pre-launch promotion impact estimator.

On-demand agent: given a proposed discount % and category, outputs expected
GMV lift, margin impact, and break-even volume. No live API ever needed --
pure Claude reasoning over historical order/margin patterns.

Directly addresses coupon dependency by forcing a margin check before every
promotion is approved.
"""

from __future__ import annotations

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

# Realistic Ananas baseline metrics per category for simulation.
# When live Orders + Margin APIs are available, these are replaced by real data.
CATEGORY_BASELINES = {
    "electronics": {
        "avg_weekly_orders": 1840,
        "avg_order_value": 142.0,
        "avg_margin_pct": 14.2,
        "avg_return_rate_pct": 8.1,
        "price_elasticity": 1.8,
        "coupon_dependency_pct": 38.0,
    },
    "shoes_clothing": {
        "avg_weekly_orders": 4210,
        "avg_order_value": 58.0,
        "avg_margin_pct": 32.1,
        "avg_return_rate_pct": 18.4,
        "price_elasticity": 2.1,
        "coupon_dependency_pct": 52.0,
    },
    "home_garden": {
        "avg_weekly_orders": 2870,
        "avg_order_value": 74.0,
        "avg_margin_pct": 22.8,
        "avg_return_rate_pct": 6.2,
        "price_elasticity": 1.5,
        "coupon_dependency_pct": 29.0,
    },
    "sports_outdoors": {
        "avg_weekly_orders": 1620,
        "avg_order_value": 68.0,
        "avg_margin_pct": 28.4,
        "avg_return_rate_pct": 9.7,
        "price_elasticity": 1.9,
        "coupon_dependency_pct": 34.0,
    },
    "beauty_health": {
        "avg_weekly_orders": 3140,
        "avg_order_value": 41.0,
        "avg_margin_pct": 38.6,
        "avg_return_rate_pct": 4.1,
        "price_elasticity": 2.3,
        "coupon_dependency_pct": 61.0,
    },
    "toys_kids": {
        "avg_weekly_orders": 980,
        "avg_order_value": 52.0,
        "avg_margin_pct": 26.3,
        "avg_return_rate_pct": 5.8,
        "price_elasticity": 1.7,
        "coupon_dependency_pct": 27.0,
    },
    "all_categories": {
        "avg_weekly_orders": 18200,
        "avg_order_value": 71.0,
        "avg_margin_pct": 24.6,
        "avg_return_rate_pct": 9.8,
        "price_elasticity": 1.9,
        "coupon_dependency_pct": 43.0,
    },
}


def simulate(
    category: str,
    discount_pct: float,
    duration_days: int = 7,
    promo_type: str = "sitewide",
) -> dict:
    """Run the promo simulation math.

    Returns a structured dict with GMV lift, margin impact, break-even,
    and a go/no-go signal. Used both internally and by the CLI.
    """
    baseline_key = category.lower().replace(" ", "_").replace("&", "").replace("-", "_")
    if baseline_key not in CATEGORY_BASELINES:
        baseline_key = "all_categories"
    b = CATEGORY_BASELINES[baseline_key]

    weeks = duration_days / 7
    baseline_orders = b["avg_weekly_orders"] * weeks
    baseline_gmv = baseline_orders * b["avg_order_value"]
    baseline_margin = baseline_gmv * (b["avg_margin_pct"] / 100)

    # Estimate incremental orders using price elasticity.
    # Elasticity: 1% price drop -> elasticity% volume increase.
    incremental_order_lift_pct = discount_pct * b["price_elasticity"]
    # Cap at realistic upper bound -- deep discounts have diminishing returns.
    incremental_order_lift_pct = min(incremental_order_lift_pct, discount_pct * 2.5)

    promo_orders = baseline_orders * (1 + incremental_order_lift_pct / 100)
    promo_gmv = promo_orders * b["avg_order_value"] * (1 - discount_pct / 100)
    promo_margin_pct = b["avg_margin_pct"] - discount_pct
    promo_margin = promo_gmv * (max(promo_margin_pct, 0) / 100)

    gmv_lift_pct = round((promo_gmv - baseline_gmv) / baseline_gmv * 100, 1)
    margin_delta = round(promo_margin - baseline_margin, 2)
    margin_delta_pct = round(
        (promo_margin - baseline_margin) / baseline_baseline_margin_safe(baseline_margin) * 100, 1
    )

    # Break-even: how many extra orders needed to offset margin loss from discount.
    margin_gained_per_extra_order = (
        b["avg_order_value"] * (1 - discount_pct / 100) * (max(promo_margin_pct, 0) / 100)
    )
    if margin_gained_per_extra_order > 0:
        break_even_extra_orders = int(abs(min(margin_delta, 0)) / margin_gained_per_extra_order) + 1
    else:
        break_even_extra_orders = 999999

    break_even_lift_pct = round(break_even_extra_orders / baseline_orders * 100, 1)

    # Coupon cannibalization warning: if coupon dependency is high,
    # a significant portion of promo orders would have happened anyway.
    cannibalization_pct = b["coupon_dependency_pct"]
    true_incremental_orders = promo_orders * (1 - cannibalization_pct / 100) - baseline_orders * (
        1 - cannibalization_pct / 100
    )

    # Go / no-go signal
    go_nogo = (
        "GO"
        if margin_delta >= 0
        else ("CAUTION" if margin_delta > -baseline_margin * 0.1 else "NO-GO")
    )

    return {
        "headline": (
            f"{go_nogo}: {discount_pct:.0f}% off {category} for {duration_days}d | "
            f"GMV lift {gmv_lift_pct:+.1f}% | "
            f"Margin delta EUR{margin_delta:+,.0f}"
        ),
        "inputs": {
            "category": category,
            "discount_pct": discount_pct,
            "duration_days": duration_days,
            "promo_type": promo_type,
        },
        "baseline": {
            "orders": round(baseline_orders),
            "gmv_eur": round(baseline_gmv, 2),
            "margin_eur": round(baseline_margin, 2),
            "margin_pct": b["avg_margin_pct"],
            "coupon_dependency_pct": b["coupon_dependency_pct"],
        },
        "projected": {
            "orders": round(promo_orders),
            "gmv_eur": round(promo_gmv, 2),
            "margin_eur": round(promo_margin, 2),
            "margin_pct": round(promo_margin_pct, 1),
            "gmv_lift_pct": gmv_lift_pct,
            "margin_delta_eur": margin_delta,
            "margin_delta_pct": margin_delta_pct,
        },
        "break_even": {
            "extra_orders_needed": break_even_extra_orders,
            "order_lift_pct_needed": break_even_lift_pct,
            "achievable": break_even_lift_pct <= incremental_order_lift_pct,
        },
        "cannibalization_warning": {
            "historical_coupon_dependency_pct": cannibalization_pct,
            "est_true_incremental_orders": round(true_incremental_orders),
            "risk": "HIGH"
            if cannibalization_pct > 50
            else ("MEDIUM" if cannibalization_pct > 30 else "LOW"),
        },
        "signal": go_nogo,
        "sources_live": False,
    }


def baseline_baseline_margin_safe(baseline_margin: float) -> float:
    return baseline_margin if baseline_margin != 0 else 1.0


class PromoSimulatorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="promo-simulator-agent",
            module_name="promo-simulator",
            output_type="on-demand-analysis",
        )

    def sample_summary(self) -> dict:
        return simulate("all_categories", 10.0, 7, "sitewide")

    def run(self, date_from: str, date_to: str) -> dict:
        return self.run_simulation("all_categories", 10.0, 7)

    def run_simulation(
        self,
        category: str,
        discount_pct: float,
        duration_days: int = 7,
        promo_type: str = "sitewide",
    ) -> dict:
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model

        logger.info(
            "promo-simulator-agent: simulating %.0f%% discount on %s for %d days",
            discount_pct,
            category,
            duration_days,
        )

        raw = simulate(category, discount_pct, duration_days, promo_type)

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Promo Simulator. Ananas is North Macedonia's largest "
            "e-commerce marketplace. Your job is to evaluate proposed promotions BEFORE they run, "
            "protecting margin and reducing coupon dependency. "
            "Ananas currently has heavy coupon dependency -- many customers buy only with discounts, "
            "which masks real acquisition efficiency. "
            "Analyse the simulation data and provide: "
            "1. Clear GO / CAUTION / NO-GO verdict with rationale. "
            "2. Margin impact in EUR (not just %). "
            "3. Break-even analysis -- how many extra orders needed. "
            "4. Cannibalization risk -- what % of promo orders would have happened anyway. "
            "5. One alternative recommendation (e.g. targeted discount instead of sitewide). "
            "Be direct. Marketing teams need a clear decision, not a report."
        )
        user = (
            f"Proposed promotion: {discount_pct:.0f}% discount on {category} "
            f"for {duration_days} days ({promo_type})\n\n"
            f"Simulation data:\n{raw}\n\n"
            "Give your assessment and verdict."
        )

        try:
            result = call_model(route.model, system, user)
            raw["analysis"] = result["text"]
            raw["model_used"] = result["model_used"]
            raw["fallback"] = result["fallback"]
            raw["tokens_in"] = result["tokens_in"]
            raw["tokens_out"] = result["tokens_out"]
            raw["estimated_cost"] = result["estimated_cost"]
        except Exception as e:
            logger.error("promo-simulator-agent: model call failed: %s", e)
            raw["analysis"] = f"Promo simulation ({raw['signal']}) -- model unavailable"

        return raw
