from __future__ import annotations

import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import boto3

from ananas_ai.agents.category_growth import CategoryGrowthAgent
from ananas_ai.agents.competitor_intelligence import CompetitorIntelligenceAgent
from ananas_ai.agents.crm_lifecycle import CRMLifecycleAgent
from ananas_ai.agents.cross_channel_brief import CrossChannelBriefAgent
from ananas_ai.agents.customer_segmentation import CustomerSegmentationAgent
from ananas_ai.agents.demand_forecasting import DemandForecastingAgent
from ananas_ai.agents.employer_branding import EmployerBrandingAgent
from ananas_ai.agents.influencer_partnership import InfluencerPartnershipAgent
from ananas_ai.agents.knowledge_retrieval import KnowledgeRetrievalAgent
from ananas_ai.agents.listing_content_quality import ListingContentQualityAgent
from ananas_ai.agents.marketing_ops import MarketingOpsAgent
from ananas_ai.agents.meeting_intelligence import MeetingIntelligenceAgent
from ananas_ai.agents.organic_merchandising import OrganicMerchandisingAgent
from ananas_ai.agents.performance import PerformanceAgent
from ananas_ai.agents.product_feed import ProductFeedAgent
from ananas_ai.agents.promo_simulator import PromoSimulatorAgent
from ananas_ai.agents.reputation import ReputationAgent
from ananas_ai.agents.search_merchandising import SearchMerchandisingAgent
from ananas_ai.agents.supplier_intelligence import SupplierIntelligenceAgent
from ananas_ai.agents.traditional_media_correlation import TraditionalMediaCorrelationAgent
from ananas_ai.config import load_agent_channels, load_settings
from ananas_ai.email_delivery import send_brief
from ananas_ai.logging_config import get_logger
from ananas_ai.persistence import (
    bootstrap,
    fetch_daily_tokens,
    fetch_latest_outputs,
    insert_agent_output,
    log_agent_run,
    upsert_health,
)
from ananas_ai.teams import post_message
from ananas_ai.validator import validate_agent_output

logger = get_logger(__name__)

_CW_NAMESPACE = "AnanasAI"
_CW_METRIC = "BriefHeartbeat"
_CW_REGION = os.environ.get("AWS_REGION", "eu-central-1")


def _publish_heartbeat() -> None:
    """Put a CloudWatch metric so the dead-man alarm knows the brief ran."""
    try:
        cw = boto3.client("cloudwatch", region_name=_CW_REGION)
        cw.put_metric_data(
            Namespace=_CW_NAMESPACE,
            MetricData=[
                {
                    "MetricName": _CW_METRIC,
                    "Value": 1,
                    "Unit": "Count",
                }
            ],
        )
        logger.info("Heartbeat published to CloudWatch (%s/%s)", _CW_NAMESPACE, _CW_METRIC)
    except Exception as e:
        logger.warning("Heartbeat publish failed (non-fatal): %s", e)


AGENT_MAP = {
    # Phase 1
    "performance-agent": PerformanceAgent,
    "crm-lifecycle-agent": CRMLifecycleAgent,
    "reputation-agent": ReputationAgent,
    "marketing-ops-agent": MarketingOpsAgent,
    "cross-channel-brief-agent": CrossChannelBriefAgent,
    # Phase 2
    "product-feed-agent": ProductFeedAgent,
    "promo-simulator-agent": PromoSimulatorAgent,
    "customer-segmentation-agent": CustomerSegmentationAgent,
    "category-growth-agent": CategoryGrowthAgent,
    "competitor-intelligence-agent": CompetitorIntelligenceAgent,
    "demand-forecasting-agent": DemandForecastingAgent,
    "supplier-intelligence-agent": SupplierIntelligenceAgent,
    "organic-merchandising-agent": OrganicMerchandisingAgent,
    "search-merchandising-agent": SearchMerchandisingAgent,
    "listing-content-quality-agent": ListingContentQualityAgent,
    "influencer-partnership-agent": InfluencerPartnershipAgent,
    "traditional-media-correlation-agent": TraditionalMediaCorrelationAgent,
    "employer-branding-agent": EmployerBrandingAgent,
    "meeting-intelligence-agent": MeetingIntelligenceAgent,
    "knowledge-retrieval-agent": KnowledgeRetrievalAgent,
}


def _agent_channels() -> dict[str, tuple[str, str]]:
    """Load agent → (channel, title) mapping from config/output-channels.json."""
    try:
        return load_agent_channels()
    except Exception:
        # Fallback so CLI never hard-breaks if config is temporarily unavailable
        return {
            "performance-agent": ("#marketing-performance", "Performance Summary"),
            "crm-lifecycle-agent": ("#marketing-crm", "CRM & Lifecycle Summary"),
            "reputation-agent": ("#marketing-reputation", "Reputation Summary"),
            "marketing-ops-agent": ("#marketing-ops", "Marketing Ops Summary"),
            "product-feed-agent": ("#ai-marketing", "Product Feed Health"),
            "promo-simulator-agent": ("#ai-marketing", "Promo Simulation"),
            "customer-segmentation-agent": ("#ai-marketing", "Customer Segmentation"),
            "category-growth-agent": ("#ai-marketing", "Category Growth"),
            "competitor-intelligence-agent": ("#ai-marketing", "Competitor Intelligence"),
            "demand-forecasting-agent": ("#ai-marketing", "Demand Forecast"),
            "supplier-intelligence-agent": ("#ai-marketing", "Supplier Intelligence"),
            "organic-merchandising-agent": ("#ai-marketing", "Organic & Merchandising"),
            "search-merchandising-agent": ("#ai-marketing", "Search Merchandising"),
            "listing-content-quality-agent": ("#ai-marketing", "Listing Content Quality"),
            "influencer-partnership-agent": ("#ai-marketing", "Influencer & Partnerships"),
            "traditional-media-correlation-agent": ("#ai-marketing", "Traditional Media"),
            "employer-branding-agent": ("#ai-marketing", "Employer Branding"),
            "meeting-intelligence-agent": ("#ai-marketing", "Meeting Intelligence"),
            "knowledge-retrieval-agent": ("#ai-marketing", "Knowledge Retrieval"),
        }


def _daily_cap() -> int:
    try:
        return int(load_settings().model_routing["controls"]["per_day_token_cap_per_agent"])
    except Exception:
        return 200_000


def _check_daily_cap(agent_name: str) -> bool:
    """Return True if agent is within daily token cap, False if exceeded."""
    cap = _daily_cap()
    used = fetch_daily_tokens(agent_name)
    if used >= cap:
        logger.warning(
            "%s: daily token cap reached (%d/%d tokens) — skipping run",
            agent_name,
            used,
            cap,
        )
        upsert_health(agent_name, "warning", f"Daily token cap reached ({used:,}/{cap:,} tokens)")
        return False
    return True


def doctor() -> int:
    settings = load_settings()
    logger.info("Project:       %s", settings.project_overview["project_name"])
    logger.info("Domain:        %s", settings.project_overview["domain"])
    logger.info("Phase 1 agents: %d", len(settings.agents["phase_1_agents"]))
    logger.info(
        "Model policy:  %s default / %s escalation",
        settings.model_routing["models"]["default"]["model"],
        settings.model_routing["models"]["escalation"]["model"],
    )
    return 0


def run_agent(agent_name: str) -> int:
    if agent_name not in AGENT_MAP:
        raise SystemExit(f"Unknown agent: {agent_name}")
    agent_channels = _agent_channels()
    if agent_name not in agent_channels:
        raise SystemExit("Use run-brief for the cross-channel brief.")

    bootstrap()

    if not _check_daily_cap(agent_name):
        return 0

    agent = AGENT_MAP[agent_name]()
    today = str(date.today())
    channel, title = agent_channels[agent_name]

    logger.info("Running %s", agent_name)
    data = agent.run(today, today)
    run_type = "live" if data.get("sources_active") or data.get("sources_live") else "sample"

    payload = agent.build_payload(data, today, today)
    errors = validate_agent_output(payload)

    tokens_in = data.get("tokens_in", 0)
    tokens_out = data.get("tokens_out", 0)
    cost = data.get("estimated_cost", 0.0)
    actual_model = data.get("model_used", payload.get("model_used", "unknown"))

    if errors:
        log_agent_run(
            agent_name,
            run_type,
            actual_model,
            "error",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost=cost,
            error_message="; ".join(errors),
        )
        upsert_health(agent_name, "error", "; ".join(errors))
        raise SystemExit("Validation failed: " + "; ".join(errors))

    insert_agent_output(payload)
    log_agent_run(
        agent_name,
        run_type,
        actual_model,
        "ok",
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        estimated_cost=cost,
    )
    upsert_health(
        agent_name,
        "ok",
        f"{run_type.capitalize()} run — {tokens_in + tokens_out:,} tokens / ${cost:.4f}",
    )
    logger.info("Completed %s (%d tokens, $%.4f)", agent_name, tokens_in + tokens_out, cost)
    return 0


def _run_one_specialist(agent_name: str, agent: object, today: str) -> dict:
    """Run a single specialist agent, persist results, and return its payload.

    Designed to be called from a thread -- uses per-call DB connections.
    Never raises: returns a sample payload on any failure so the brief
    can still synthesize from the other agents.
    """
    from ananas_ai.agents.base import BaseAgent  # noqa: PLC0415

    assert isinstance(agent, BaseAgent)

    if not _check_daily_cap(agent_name):
        return agent.build_payload(agent.sample_summary(), today, today)

    logger.info("  Running %s", agent_name)
    try:
        data = agent.run(today, today)
    except Exception as e:
        logger.error("  %s failed: %s", agent_name, e)
        upsert_health(agent_name, "error", str(e))
        return agent.build_payload(agent.sample_summary(), today, today)

    pl = agent.build_payload(data, today, today)
    errors = validate_agent_output(pl)
    run_type = "live" if data.get("sources_active") or data.get("sources_live") else "sample"
    tokens_in = data.get("tokens_in", 0)
    tokens_out = data.get("tokens_out", 0)
    cost = data.get("estimated_cost", 0.0)
    actual_model = data.get("model_used", pl.get("model_used", "unknown"))

    if errors:
        log_agent_run(
            agent_name,
            run_type,
            actual_model,
            "error",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost=cost,
            error_message="; ".join(errors),
        )
        upsert_health(agent_name, "error", "; ".join(errors))
        logger.warning("  %s validation errors: %s", agent_name, errors)
    else:
        insert_agent_output(pl)
        log_agent_run(
            agent_name,
            run_type,
            actual_model,
            "ok",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost=cost,
        )
        upsert_health(
            agent_name,
            "ok",
            f"{run_type.capitalize()} run -- {tokens_in + tokens_out:,} tokens / ${cost:.4f}",
        )

    return pl


def run_brief() -> int:
    bootstrap()
    perf = PerformanceAgent()
    crm = CRMLifecycleAgent()
    rep = ReputationAgent()
    ops = MarketingOpsAgent()
    brief = CrossChannelBriefAgent()
    today = str(date.today())

    logger.info("Running all specialist agents in parallel")
    specialists = [
        ("performance-agent", perf),
        ("crm-lifecycle-agent", crm),
        ("reputation-agent", rep),
        ("marketing-ops-agent", ops),
    ]

    # Run all 4 specialists concurrently -- each makes independent API calls
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_name = {
            executor.submit(_run_one_specialist, name, agent, today): name
            for name, agent in specialists
        }
        results: dict[str, dict] = {}
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            results[name] = future.result()

    # Preserve original order for the brief synthesis
    specialist_payloads = [results[name] for name, _ in specialists]

    logger.info("Running cross-channel-brief-agent")
    if not _check_daily_cap("cross-channel-brief-agent"):
        return 0

    data = brief.build_from_specialists(specialist_payloads)
    payload = brief.build_payload(data, today, today, complexity="high")
    errors = validate_agent_output(payload)

    tokens_in = data.get("tokens_in", 0)
    tokens_out = data.get("tokens_out", 0)
    cost = data.get("estimated_cost", 0.0)
    actual_model = data.get("model_used", payload.get("model_used", "unknown"))

    if errors:
        log_agent_run(
            "cross-channel-brief-agent",
            "live",
            actual_model,
            "error",
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            estimated_cost=cost,
            error_message="; ".join(errors),
        )
        upsert_health("cross-channel-brief-agent", "error", "; ".join(errors))
        raise SystemExit("Validation failed: " + "; ".join(errors))

    insert_agent_output(payload)
    log_agent_run(
        "cross-channel-brief-agent",
        "live",
        actual_model,
        "ok",
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        estimated_cost=cost,
    )
    upsert_health(
        "cross-channel-brief-agent",
        "ok",
        f"Live run — {tokens_in + tokens_out:,} tokens / ${cost:.4f}",
    )
    analysis = data.get("analysis", data.get("headline", "Brief ready."))
    post_message("#ai-marketing", "Daily Marketing Brief", analysis)
    send_brief("Daily Marketing Brief", analysis)
    logger.info(
        "Completed cross-channel-brief-agent (%d tokens, $%.4f)",
        tokens_in + tokens_out,
        cost,
    )
    _publish_heartbeat()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ananas AI CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("bootstrap-db")
    ra = sub.add_parser("run-agent")
    ra.add_argument("agent_name")
    sub.add_parser("run-brief")
    sub.add_parser("list-latest")
    args = parser.parse_args()

    if args.command == "doctor":
        return doctor()
    if args.command == "bootstrap-db":
        bootstrap()
        logger.info("Database bootstrapped")
        return 0
    if args.command == "run-agent":
        return run_agent(args.agent_name)
    if args.command == "run-brief":
        return run_brief()
    if args.command == "list-latest":
        for row in fetch_latest_outputs():
            logger.info("%s", row)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
