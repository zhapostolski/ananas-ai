from __future__ import annotations

from abc import ABC, abstractmethod

from ananas_ai.logging_config import get_logger

logger = get_logger(__name__)


class BaseIntegration(ABC):
    """
    Common interface for all MCP / API integrations.

    Agents call fetch() and get either real data or an empty dict.
    They never crash because of a missing integration — they log a warning
    and fall back to sample data.
    """

    name: str  # set by subclasses

    def is_configured(self) -> bool:
        """Return True if all required credentials are present in env."""
        raise NotImplementedError

    @abstractmethod
    def fetch(self, date_from: str, date_to: str) -> dict:
        """Fetch data for the given date range. Returns {} if not configured."""
        ...

    def safe_fetch(self, date_from: str, date_to: str) -> dict:
        """Wrapper: returns empty dict on missing config or any error."""
        if not self.is_configured():
            logger.warning("%s not configured — skipping", self.name)
            return {}
        try:
            return self.fetch(date_from, date_to)
        except Exception as exc:
            logger.error("%s fetch failed: %s", self.name, exc)
            return {}

    def test_connection(self) -> tuple[bool, str]:
        """Quick connectivity check for the doctor command."""
        if not self.is_configured():
            return False, "Not configured (missing credentials)"
        try:
            self.fetch("2026-01-01", "2026-01-01")
            return True, "OK"
        except Exception as exc:
            return False, str(exc)
