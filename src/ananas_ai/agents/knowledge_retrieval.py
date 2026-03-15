"""Knowledge Retrieval Agent - institutional memory search.

On-demand agent. Searches agent_outputs DB, meeting summaries, and
(Phase 2) Confluence + Jira for answers to team questions.

Phase 1: searches the local agent_outputs database.
Phase 2: adds Confluence and Jira API search.
"""

from __future__ import annotations

from typing import Any

from ananas_ai.agents.base import BaseAgent
from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)

SAMPLE_KNOWLEDGE_RESULT: dict[str, Any] = {
    "query": "sample query",
    "answer": "Knowledge Retrieval is in sample mode. Submit a real query via the portal to search agent outputs, meeting summaries, and (Phase 2) Confluence.",
    "sources": [
        {
            "type": "agent_output",
            "agent": "performance-agent",
            "date": "2026-03-15",
            "relevance": "high",
        },
        {
            "type": "agent_output",
            "agent": "category-growth-agent",
            "date": "2026-03-10",
            "relevance": "medium",
        },
    ],
    "confidence": "low",
    "related": [],
}


class KnowledgeRetrievalAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="knowledge-retrieval-agent",
            module_name="knowledge-retrieval",
            output_type="on-demand-analysis",
        )

    def sample_summary(self) -> dict:
        return {
            **SAMPLE_KNOWLEDGE_RESULT,
            "headline": "Knowledge Retrieval (sample) -- submit a query to search institutional memory",
            "sources_live": False,
        }

    def search(self, query: str) -> dict:
        """Search agent outputs DB + meeting summaries for an answer."""
        from ananas_ai.model_client import call_model
        from ananas_ai.model_router import choose_model
        from ananas_ai.persistence import fetch_latest_outputs

        logger.info("knowledge-retrieval-agent: searching for '%s'", query)

        try:
            recent_outputs = list(fetch_latest_outputs())
        except Exception as e:
            logger.warning("knowledge-retrieval-agent: could not fetch DB outputs: %s", e)
            recent_outputs = []

        route = choose_model(self.name)
        system = (
            "You are the Ananas AI Knowledge Retrieval Agent. "
            "You search institutional memory for the Ananas marketing team. "
            "You have access to recent agent outputs from the system. "
            "Answer the query directly and concisely. "
            "If you find the answer: state it, cite the source (agent name + date). "
            "If not found: say 'Not found in available sources' and suggest where to look. "
            "Never fabricate data. Confidence: high (direct match), medium (partial), low (inferred)."
        )
        user = (
            f"Query: {query}\n\n"
            f"Available agent outputs (most recent):\n{recent_outputs[:10]}\n\n"
            "Answer the query."
        )

        try:
            result = call_model(route.model, system, user)
            return {
                "query": query,
                "answer": result["text"],
                "sources": [{"type": "agent_output_db", "records_searched": len(recent_outputs)}],
                "confidence": "medium",
                "model_used": result["model_used"],
                "tokens_in": result["tokens_in"],
                "tokens_out": result["tokens_out"],
                "estimated_cost": result["estimated_cost"],
                "sources_live": True,
                "headline": f"Query answered: {query[:60]}",
            }
        except Exception as e:
            logger.error("knowledge-retrieval-agent: model call failed: %s", e)
            return {
                "query": query,
                "answer": "Model unavailable -- could not search knowledge base.",
                "confidence": "none",
                "sources_live": False,
                "headline": "Knowledge retrieval -- model unavailable",
            }

    def run(self, date_from: str, date_to: str) -> dict:
        logger.warning("knowledge-retrieval-agent: no query provided, returning sample")
        raw = self.sample_summary()
        raw["model_used"] = "none"
        raw["tokens_in"] = 0
        raw["tokens_out"] = 0
        raw["estimated_cost"] = 0.0
        return raw
