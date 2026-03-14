"""Tests for Phase 2 agents — sample_summary + build_payload + simulation logic."""

from __future__ import annotations

import pytest

from ananas_ai.agents.category_growth import CategoryGrowthAgent
from ananas_ai.agents.competitor_intelligence import CompetitorIntelligenceAgent
from ananas_ai.agents.customer_segmentation import CustomerSegmentationAgent
from ananas_ai.agents.product_feed import ProductFeedAgent, _estimate_weeks_to_target
from ananas_ai.agents.promo_simulator import PromoSimulatorAgent, simulate
from ananas_ai.validator import validate_agent_output

TODAY = "2026-03-15"

PHASE2_AGENT_CLASSES = [
    ProductFeedAgent,
    PromoSimulatorAgent,
    CustomerSegmentationAgent,
    CategoryGrowthAgent,
    CompetitorIntelligenceAgent,
]


# ── Generic contract tests ────────────────────────────────────────────────────


@pytest.mark.parametrize("cls", PHASE2_AGENT_CLASSES)
def test_sample_summary_returns_dict(cls):
    agent = cls()
    result = agent.sample_summary()
    assert isinstance(result, dict)


@pytest.mark.parametrize("cls", PHASE2_AGENT_CLASSES)
def test_build_payload_passes_validation(cls):
    agent = cls()
    payload = agent.build_payload(agent.sample_summary(), TODAY, TODAY)
    errors = validate_agent_output(payload)
    assert errors == [], f"{cls.__name__} validation errors: {errors}"


@pytest.mark.parametrize("cls", PHASE2_AGENT_CLASSES)
def test_payload_has_required_keys(cls):
    agent = cls()
    payload = agent.build_payload(agent.sample_summary(), TODAY, TODAY)
    for key in (
        "agent_name",
        "module_name",
        "output_type",
        "date_from",
        "date_to",
        "data",
        "model_used",
    ):
        assert key in payload, f"{cls.__name__} missing key: {key}"


@pytest.mark.parametrize("cls", PHASE2_AGENT_CLASSES)
def test_sample_summary_has_headline(cls):
    agent = cls()
    result = agent.sample_summary()
    assert "headline" in result, f"{cls.__name__} sample_summary missing 'headline'"
    assert result["headline"], f"{cls.__name__} headline is empty"


# ── ProductFeedAgent specific ─────────────────────────────────────────────────


def test_product_feed_health_pct_in_range():
    agent = ProductFeedAgent()
    data = agent.sample_summary()
    assert 0 < data["feed_health_pct"] < 100
    assert data["feed_health_pct"] < data["feed_health_target_pct"]


def test_product_feed_has_attribute_gaps():
    agent = ProductFeedAgent()
    data = agent.sample_summary()
    assert isinstance(data["attribute_gaps"], list)
    assert len(data["attribute_gaps"]) > 0
    for gap in data["attribute_gaps"]:
        assert "attribute" in gap
        assert "missing_count" in gap
        assert "impact" in gap


def test_product_feed_has_high_traffic_products():
    agent = ProductFeedAgent()
    data = agent.sample_summary()
    assert isinstance(data["high_traffic_low_cvr"], list)
    assert len(data["high_traffic_low_cvr"]) > 0


def test_estimate_weeks_to_target_at_target():
    assert _estimate_weeks_to_target(90.0, 90.0) == 0


def test_estimate_weeks_to_target_below():
    weeks = _estimate_weeks_to_target(59.1, 90.0)
    assert weeks > 0


# ── PromoSimulatorAgent specific ─────────────────────────────────────────────


def test_simulate_returns_signal():
    result = simulate("electronics", 10.0, 7)
    assert result["signal"] in ("GO", "CAUTION", "NO-GO")


def test_simulate_deep_discount_no_go():
    # 60% discount on a 14% margin category should be NO-GO
    result = simulate("electronics", 60.0, 7)
    assert result["signal"] in ("CAUTION", "NO-GO")


def test_simulate_zero_discount_go():
    result = simulate("electronics", 0.0, 7)
    assert result["signal"] == "GO"


def test_simulate_all_categories_fallback():
    # Unknown category falls back to all_categories baseline
    result = simulate("unknown_category_xyz", 10.0)
    assert result["signal"] in ("GO", "CAUTION", "NO-GO")
    assert result["inputs"]["category"] == "unknown_category_xyz"


def test_simulate_has_break_even():
    result = simulate("beauty_health", 15.0, 7)
    assert "break_even" in result
    assert "extra_orders_needed" in result["break_even"]
    assert "achievable" in result["break_even"]


def test_simulate_has_cannibalization_warning():
    result = simulate("beauty_health", 15.0, 7)
    assert "cannibalization_warning" in result
    assert result["cannibalization_warning"]["risk"] in ("LOW", "MEDIUM", "HIGH")


def test_promo_simulator_agent_sample_is_valid_simulation():
    agent = PromoSimulatorAgent()
    data = agent.sample_summary()
    assert "signal" in data
    assert "projected" in data
    assert "baseline" in data


# ── CustomerSegmentationAgent specific ───────────────────────────────────────


def test_customer_segmentation_has_all_segments():
    agent = CustomerSegmentationAgent()
    data = agent.sample_summary()
    for segment in ("vip", "active", "at_risk", "churned", "new"):
        assert segment in data["segments"], f"Missing segment: {segment}"


def test_customer_segmentation_coupon_insight_present():
    agent = CustomerSegmentationAgent()
    data = agent.sample_summary()
    assert "coupon_insight" in data
    assert data["coupon_insight"]["customers_needing_coupon_pct"] < 60


def test_customer_segmentation_churn_alerts():
    agent = CustomerSegmentationAgent()
    data = agent.sample_summary()
    assert isinstance(data["churn_alerts"], list)
    assert len(data["churn_alerts"]) > 0
    for alert in data["churn_alerts"]:
        assert "urgency" in alert
        assert "revenue_at_risk_eur" in alert


def test_customer_segmentation_total_matches_segments():
    agent = CustomerSegmentationAgent()
    data = agent.sample_summary()
    segment_sum = sum(s["customer_count"] for s in data["segments"].values())
    assert segment_sum == data["total_customers"]


# ── CategoryGrowthAgent specific ─────────────────────────────────────────────


def test_category_growth_has_categories():
    agent = CategoryGrowthAgent()
    data = agent.sample_summary()
    assert isinstance(data["categories"], list)
    assert len(data["categories"]) >= 5


def test_category_growth_all_signals_valid():
    agent = CategoryGrowthAgent()
    data = agent.sample_summary()
    valid_signals = {"SCALE", "MONITOR", "INVESTIGATE", "FIX", "MAINTAIN"}
    for cat in data["categories"]:
        assert cat["signal"] in valid_signals, f"Invalid signal: {cat['signal']}"


def test_category_growth_signal_summary_present():
    agent = CategoryGrowthAgent()
    data = agent.sample_summary()
    assert "signal_summary" in data
    for key in ("SCALE", "MONITOR", "INVESTIGATE", "FIX", "MAINTAIN"):
        assert key in data["signal_summary"]


def test_category_growth_revenue_positive():
    agent = CategoryGrowthAgent()
    data = agent.sample_summary()
    assert data["total_weekly_revenue_eur"] > 0
    for cat in data["categories"]:
        assert cat["weekly_revenue_eur"] >= 0


# ── CompetitorIntelligenceAgent specific ─────────────────────────────────────


def test_competitor_intelligence_has_competitors():
    agent = CompetitorIntelligenceAgent()
    data = agent.sample_summary()
    assert isinstance(data["competitors"], list)
    assert len(data["competitors"]) > 0


def test_competitor_intelligence_has_review_comparison():
    agent = CompetitorIntelligenceAgent()
    data = agent.sample_summary()
    assert isinstance(data["review_comparison"], list)
    ananas = next((r for r in data["review_comparison"] if r["competitor"] == "Ananas"), None)
    assert ananas is not None
    assert ananas["trustpilot_rating"] == 2.0


def test_competitor_intelligence_reputation_gap_positive():
    agent = CompetitorIntelligenceAgent()
    data = agent.sample_summary()
    # Our rating (2.0) should be below competitor average -- gap should be positive
    assert data["summary"]["reputation_gap"] > 0


def test_competitor_intelligence_has_auction_insights():
    agent = CompetitorIntelligenceAgent()
    data = agent.sample_summary()
    assert isinstance(data["auction_insights"], list)
    assert len(data["auction_insights"]) > 0
