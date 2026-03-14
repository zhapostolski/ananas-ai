"""Tests for Phase 2 agents batch 2 — sample_summary + build_payload contracts."""

from __future__ import annotations

import pytest

from ananas_ai.agents.demand_forecasting import DemandForecastingAgent
from ananas_ai.agents.employer_branding import EmployerBrandingAgent
from ananas_ai.agents.influencer_partnership import InfluencerPartnershipAgent
from ananas_ai.agents.knowledge_retrieval import KnowledgeRetrievalAgent
from ananas_ai.agents.listing_content_quality import ListingContentQualityAgent
from ananas_ai.agents.meeting_intelligence import MeetingIntelligenceAgent
from ananas_ai.agents.organic_merchandising import OrganicMerchandisingAgent
from ananas_ai.agents.search_merchandising import SearchMerchandisingAgent
from ananas_ai.agents.supplier_intelligence import SupplierIntelligenceAgent
from ananas_ai.agents.traditional_media_correlation import TraditionalMediaCorrelationAgent
from ananas_ai.validator import validate_agent_output

TODAY = "2026-03-15"

BATCH2_AGENT_CLASSES = [
    DemandForecastingAgent,
    SupplierIntelligenceAgent,
    OrganicMerchandisingAgent,
    SearchMerchandisingAgent,
    ListingContentQualityAgent,
    InfluencerPartnershipAgent,
    TraditionalMediaCorrelationAgent,
    EmployerBrandingAgent,
    MeetingIntelligenceAgent,
    KnowledgeRetrievalAgent,
]


# ── Generic contract tests ────────────────────────────────────────────────────


@pytest.mark.parametrize("cls", BATCH2_AGENT_CLASSES)
def test_sample_summary_returns_dict(cls):
    agent = cls()
    result = agent.sample_summary()
    assert isinstance(result, dict)


@pytest.mark.parametrize("cls", BATCH2_AGENT_CLASSES)
def test_build_payload_passes_validation(cls):
    agent = cls()
    payload = agent.build_payload(agent.sample_summary(), TODAY, TODAY)
    errors = validate_agent_output(payload)
    assert errors == [], f"{cls.__name__} validation errors: {errors}"


@pytest.mark.parametrize("cls", BATCH2_AGENT_CLASSES)
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


@pytest.mark.parametrize("cls", BATCH2_AGENT_CLASSES)
def test_sample_summary_has_headline(cls):
    agent = cls()
    result = agent.sample_summary()
    assert "headline" in result, f"{cls.__name__} sample_summary missing 'headline'"
    assert result["headline"], f"{cls.__name__} headline is empty"


# ── DemandForecastingAgent specific ──────────────────────────────────────────


def test_demand_forecasting_has_signals():
    agent = DemandForecastingAgent()
    data = agent.sample_summary()
    assert isinstance(data["demand_signals"], list)
    assert len(data["demand_signals"]) > 0


def test_demand_forecasting_signal_states_valid():
    agent = DemandForecastingAgent()
    data = agent.sample_summary()
    valid_states = {"ACCELERATING", "RISING", "EARLY_SIGNAL", "DECLINING", "STABLE"}
    for sig in data["demand_signals"]:
        assert sig["signal"] in valid_states, f"Invalid state: {sig['signal']}"


def test_demand_forecasting_has_seasonal_calendar():
    agent = DemandForecastingAgent()
    data = agent.sample_summary()
    assert isinstance(data["seasonal_calendar"], list)
    assert len(data["seasonal_calendar"]) > 0
    for event in data["seasonal_calendar"]:
        assert "event" in event
        assert "starts" in event
        assert "confidence" in event


def test_demand_forecasting_sessions_change_present():
    agent = DemandForecastingAgent()
    data = agent.sample_summary()
    for sig in data["demand_signals"]:
        assert "ga4_sessions_wow_change_pct" in sig


# ── SupplierIntelligenceAgent specific ───────────────────────────────────────


def test_supplier_intelligence_has_suppliers():
    agent = SupplierIntelligenceAgent()
    data = agent.sample_summary()
    assert isinstance(data["suppliers"], list)
    assert len(data["suppliers"]) >= 3


def test_supplier_intelligence_opportunity_scores_valid():
    agent = SupplierIntelligenceAgent()
    data = agent.sample_summary()
    valid_scores = {"HIGH", "MEDIUM", "LOW"}
    for sup in data["suppliers"]:
        assert sup["opportunity"] in valid_scores, f"Invalid score: {sup['opportunity']}"


def test_supplier_intelligence_revenue_positive():
    agent = SupplierIntelligenceAgent()
    data = agent.sample_summary()
    for sup in data["suppliers"]:
        assert sup["weekly_revenue_eur"] >= 0


def test_supplier_intelligence_has_summary():
    agent = SupplierIntelligenceAgent()
    data = agent.sample_summary()
    assert "summary" in data
    assert data["summary"]["total_weekly_revenue_eur"] > 0


# ── OrganicMerchandisingAgent specific ───────────────────────────────────────


def test_organic_merchandising_has_keywords():
    agent = OrganicMerchandisingAgent()
    data = agent.sample_summary()
    assert isinstance(data["keyword_movements"], list)
    assert len(data["keyword_movements"]) > 0


def test_organic_merchandising_keyword_movements_have_direction():
    agent = OrganicMerchandisingAgent()
    data = agent.sample_summary()
    valid_directions = {"UP", "DOWN"}
    for kw in data["keyword_movements"]:
        assert kw["direction"] in valid_directions, f"Invalid direction: {kw['direction']}"


def test_organic_merchandising_has_seo_issues():
    agent = OrganicMerchandisingAgent()
    data = agent.sample_summary()
    assert isinstance(data["seo_issues"], list)
    assert len(data["seo_issues"]) > 0
    for issue in data["seo_issues"]:
        assert "severity" in issue
        assert "affected_pages" in issue


def test_organic_merchandising_indexation_positive():
    agent = OrganicMerchandisingAgent()
    data = agent.sample_summary()
    assert data["total_indexed_pages"] > 0
    assert data["total_catalog_size"] > 0
    assert 0 < data["indexation_pct"] < 100


# ── SearchMerchandisingAgent specific ─────────────────────────────────────────


def test_search_merchandising_zero_result_rate():
    agent = SearchMerchandisingAgent()
    data = agent.sample_summary()
    funnel = data["search_funnel"]
    assert 0 < funnel["zero_result_rate_pct"] < 100
    assert funnel["zero_result_rate_pct"] > funnel["zero_result_target_pct"]


def test_search_merchandising_has_zero_result_queries():
    agent = SearchMerchandisingAgent()
    data = agent.sample_summary()
    assert isinstance(data["zero_result_queries"], list)
    assert len(data["zero_result_queries"]) > 0
    for q in data["zero_result_queries"]:
        assert "query" in q
        assert "search_count" in q


def test_search_merchandising_revenue_at_risk_positive():
    agent = SearchMerchandisingAgent()
    data = agent.sample_summary()
    assert data["revenue_at_risk_eur"] > 0


def test_search_merchandising_has_failed_sessions():
    agent = SearchMerchandisingAgent()
    data = agent.sample_summary()
    assert isinstance(data["failed_sessions"], list)
    assert len(data["failed_sessions"]) > 0


# ── ListingContentQualityAgent specific ───────────────────────────────────────


def test_listing_content_has_issues():
    agent = ListingContentQualityAgent()
    data = agent.sample_summary()
    assert isinstance(data["quality_issues"], list)
    assert len(data["quality_issues"]) > 0


def test_listing_content_gmv_at_risk_positive():
    agent = ListingContentQualityAgent()
    data = agent.sample_summary()
    assert data["total_gmv_at_risk_weekly_eur"] > 0
    for issue in data["quality_issues"]:
        assert issue["gmv_at_risk_eur_weekly"] >= 0


def test_listing_content_has_quick_wins():
    agent = ListingContentQualityAgent()
    data = agent.sample_summary()
    assert isinstance(data["quick_wins"], list)
    assert len(data["quick_wins"]) > 0


def test_listing_content_category_quality_scores():
    agent = ListingContentQualityAgent()
    data = agent.sample_summary()
    assert isinstance(data["category_quality"], list)
    for cat in data["category_quality"]:
        assert 0 <= cat["quality_score"] <= 100


# ── InfluencerPartnershipAgent specific ───────────────────────────────────────


def test_influencer_has_campaigns():
    agent = InfluencerPartnershipAgent()
    data = agent.sample_summary()
    assert isinstance(data["active_campaigns"], list)
    assert len(data["active_campaigns"]) > 0


def test_influencer_roas_positive():
    agent = InfluencerPartnershipAgent()
    data = agent.sample_summary()
    for campaign in data["active_campaigns"]:
        assert campaign["roas"] >= 0


def test_influencer_has_affiliate_summary():
    agent = InfluencerPartnershipAgent()
    data = agent.sample_summary()
    assert "affiliate_summary" in data
    assert "active_affiliates" in data["affiliate_summary"]


def test_influencer_has_opportunities():
    agent = InfluencerPartnershipAgent()
    data = agent.sample_summary()
    assert isinstance(data["opportunities"], list)
    assert len(data["opportunities"]) > 0


# ── TraditionalMediaCorrelationAgent specific ─────────────────────────────────


def test_traditional_media_has_campaigns():
    agent = TraditionalMediaCorrelationAgent()
    data = agent.sample_summary()
    assert isinstance(data["offline_campaigns"], list)
    assert len(data["offline_campaigns"]) > 0


def test_traditional_media_roas_positive():
    agent = TraditionalMediaCorrelationAgent()
    data = agent.sample_summary()
    for campaign in data["offline_campaigns"]:
        assert campaign["implied_offline_roas"] > 0


def test_traditional_media_has_baseline_metrics():
    agent = TraditionalMediaCorrelationAgent()
    data = agent.sample_summary()
    assert "baseline_metrics" in data
    assert "branded_search_lift_pct" in data["baseline_metrics"]


def test_traditional_media_budget_positive():
    agent = TraditionalMediaCorrelationAgent()
    data = agent.sample_summary()
    assert data["total_offline_budget_eur"] > 0


# ── EmployerBrandingAgent specific ────────────────────────────────────────────


def test_employer_branding_has_linkedin_metrics():
    agent = EmployerBrandingAgent()
    data = agent.sample_summary()
    assert "linkedin" in data
    assert data["linkedin"]["followers"] > 0


def test_employer_branding_has_job_postings():
    agent = EmployerBrandingAgent()
    data = agent.sample_summary()
    assert isinstance(data["job_postings"], list)
    assert len(data["job_postings"]) > 0


def test_employer_branding_risk_roles_in_postings():
    agent = EmployerBrandingAgent()
    data = agent.sample_summary()
    risk_roles = [j for j in data["job_postings"] if "RISK" in j["status"]]
    assert len(risk_roles) > 0, "Expected at least one at-risk job posting in sample data"


# ── MeetingIntelligenceAgent specific ─────────────────────────────────────────


def test_meeting_intelligence_has_action_items():
    agent = MeetingIntelligenceAgent()
    data = agent.sample_summary()
    assert isinstance(data["action_items"], list)
    assert len(data["action_items"]) > 0
    for item in data["action_items"]:
        assert "action" in item
        assert "owner" in item
        assert "due" in item


def test_meeting_intelligence_has_key_decisions():
    agent = MeetingIntelligenceAgent()
    data = agent.sample_summary()
    assert isinstance(data["key_decisions"], list)
    assert len(data["key_decisions"]) > 0


def test_meeting_intelligence_has_participants():
    agent = MeetingIntelligenceAgent()
    data = agent.sample_summary()
    assert isinstance(data["participants"], list)
    assert len(data["participants"]) > 0


# ── KnowledgeRetrievalAgent specific ──────────────────────────────────────────


def test_knowledge_retrieval_has_answer():
    agent = KnowledgeRetrievalAgent()
    data = agent.sample_summary()
    assert "answer" in data
    assert data["answer"]


def test_knowledge_retrieval_has_sources():
    agent = KnowledgeRetrievalAgent()
    data = agent.sample_summary()
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0


def test_knowledge_retrieval_confidence_valid():
    agent = KnowledgeRetrievalAgent()
    data = agent.sample_summary()
    assert data["confidence"] in ("high", "medium", "low", "none")
